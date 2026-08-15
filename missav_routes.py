# ============================================================
# missav_routes.py - MissAV 完整功能（适配 missav.ws/dm1/）
# 支持多域名、自动预热、多种路径探测
# ============================================================

import re
import random
import time
from urllib.parse import quote, urlparse
from fastapi import APIRouter, HTTPException, Query
import cloudscraper
from bs4 import BeautifulSoup

router = APIRouter(prefix="/missav", tags=["MissAV"])

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
]

class MissAVFetcher:
    def __init__(self):
        self.base_domains = ["missav.ws", "missav.ai"]  # 主域名 + 备用
        self.timeout = 30
        self.max_retries = 3
        self.session = None  # 用于持久化 cookies

    def _get_session(self):
        if self.session is None:
            self.session = cloudscraper.create_scraper(
                browser={
                    'browser': random.choice(['chrome', 'firefox', 'safari']),
                    'platform': random.choice(['windows', 'macos', 'linux']),
                    'mobile': False
                }
            )
        return self.session

    def _fetch(self, url, retries=None):
        """带重试的请求，自动处理 Cloudflare 盾"""
        if retries is None:
            retries = self.max_retries
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://" + self.base_domains[0] + "/",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        session = self._get_session()
        for attempt in range(retries):
            try:
                resp = session.get(url, headers=headers, timeout=self.timeout)
                if resp.status_code == 200:
                    return resp.text
                if resp.status_code in (403, 503):
                    # 被盾 → 重置会话
                    self.session = None
                    session = self._get_session()
                    time.sleep(2 ** attempt)
                    continue
                raise Exception(f"HTTP {resp.status_code}")
            except Exception as e:
                print(f"[MissAV] 请求失败 (尝试 {attempt+1}/{retries}): {e}")
                if attempt == retries - 1:
                    raise Exception(f"抓取失败: {e}")
                time.sleep(1 * (attempt + 1))
        raise Exception("抓取失败，已达最大重试次数")

    def _warm_up(self, base_url):
        """访问首页获取 Cloudflare cookies"""
        try:
            self._fetch(base_url + "/")
        except:
            pass  # 即使失败也可能拿到部分 cookies

    def _try_search(self, keyword):
        """遍历域名和搜索路径"""
        for domain in self.base_domains:
            base = "https://" + domain
            self._warm_up(base)
            # 尝试两种搜索格式
            for path in [f"/search/{quote(keyword)}", f"/search?q={quote(keyword)}"]:
                url = base + path
                try:
                    html = self._fetch(url)
                    return html, base
                except Exception as e:
                    print(f"[MissAV] 搜索尝试失败 {url}: {e}")
                    continue
        raise Exception("所有域名和搜索路径均失败")

    def search(self, keyword):
        if len(keyword) < 2:
            raise ValueError("至少输入2个字符")

        html, base = self._try_search(keyword)
        soup = BeautifulSoup(html, 'lxml')
        results = []
        seen = set()

        # 查找所有可能的视频链接（/watch/, /dm1/, /v/）
        links = soup.select('a[href*="/watch/"], a[href*="/dm1/"], a[href*="/v/"]')
        if not links:
            links = soup.find_all('a', href=re.compile(r'/(watch|dm1|v)/[^/]+'))

        for a in links:
            href = a.get('href')
            if not href or href in seen:
                continue
            full_url = base + href if href.startswith('/') else href

            # 提取视频ID（URL最后一段）
            video_id = href.split('/')[-1] if href.split('/') else ""

            # 封面图
            img = a.find('img')
            src = ""
            if img:
                src = img.get('src') or img.get('data-src') or img.get('data-original') or ""
                if src.startswith('//'):
                    src = "https:" + src
                elif src.startswith('/'):
                    src = base + src
            if not src:  # 尝试从 style 背景提取
                style = a.get('style', '')
                bg_match = re.search(r'url\(["\']?(.*?)["\']?\)', style)
                if bg_match:
                    src = bg_match.group(1)
                    if src.startswith('//'):
                        src = "https:" + src
                    elif src.startswith('/'):
                        src = base + src

            # 标题
            title = a.get('title', '')
            if not title and img:
                title = img.get('alt', '')
            title = title.strip() or "未知标题"

            # 番号（从标题或URL提取）
            code = ""
            code_match = re.search(r'([A-Z]{2,6}-\d{3,5})', title)
            if code_match:
                code = code_match.group(1)
            else:
                # 尝试从URL提取（如 fc2-ppv-4861514）
                code_match_url = re.search(r'/(watch|dm1|v)/([^/]+)', href)
                if code_match_url:
                    code = code_match_url.group(2)

            results.append({
                "id": video_id,
                "url": full_url,
                "title": title,
                "code": code,
                "cover": src,
            })
            seen.add(href)
            if len(results) >= 30:
                break
        return results

    def get_detail(self, video_id_or_url):
        """
        支持传入视频ID或完整详情页URL
        自动尝试多种路径格式
        """
        # 如果是完整URL，直接抓取
        if video_id_or_url.startswith('http'):
            parsed = urlparse(video_id_or_url)
            base = f"{parsed.scheme}://{parsed.netloc}"
            self._warm_up(base)
            html = self._fetch(video_id_or_url)
            return self._parse_detail(html, base, video_id_or_url, video_id_or_url)

        # 否则按ID尝试多种路径
        for domain in self.base_domains:
            base = "https://" + domain
            self._warm_up(base)
            for path in [f"/watch/{video_id_or_url}", f"/dm1/{video_id_or_url}", f"/v/{video_id_or_url}"]:
                url = base + path
                try:
                    html = self._fetch(url)
                    return self._parse_detail(html, base, video_id_or_url, url)
                except Exception as e:
                    print(f"[MissAV] 详情尝试失败 {url}: {e}")
                    continue
        raise Exception("所有域名和路径均无法获取详情")

    def _parse_detail(self, html, base, video_id, url):
        soup = BeautifulSoup(html, 'lxml')

        # 标题
        title = "未知标题"
        h1 = soup.find('h1')
        if h1:
            title = h1.text.strip()
        else:
            meta_title = soup.find('meta', property='og:title')
            if meta_title:
                title = meta_title.get('content', '').strip()

        # 番号
        code_match = re.search(r'([A-Z]{2,6}-\d{3,5})', title)
        code = code_match.group(1) if code_match else ""

        # 封面
        cover = ""
        meta_og = soup.find('meta', property='og:image')
        if meta_og:
            cover = meta_og.get('content', '')
        else:
            img = soup.select_one('img[alt*="cover"], img[src*="cover"]')
            if img:
                cover = img.get('src') or img.get('data-src') or ""
        if cover and cover.startswith('//'):
            cover = "https:" + cover
        elif cover and cover.startswith('/'):
            cover = base + cover

        # 演员
        actors = []
        for a in soup.select('a[href*="/actor/"]'):
            name = a.text.strip()
            if name:
                actors.append(name)
        actors = list(dict.fromkeys(actors))

        # 简介
        desc = ""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            desc = meta_desc.get('content', '')
        if not desc:
            meta_og_desc = soup.find('meta', property='og:description')
            if meta_og_desc:
                desc = meta_og_desc.get('content', '')

        # 视频源 m3u8
        video_url = ""
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                content = script.string
                # 多种 pattern
                patterns = [
                    r'video_url\s*[:=]\s*["\'](https?://[^"\']+\.m3u8[^"\']*)["\']',
                    r'videoUrl\s*[:=]\s*["\'](https?://[^"\']+\.m3u8[^"\']*)["\']',
                    r'(https?://[^\s"\']+\.m3u8[^\s"\']*)'
                ]
                for pat in patterns:
                    matches = re.findall(pat, content, re.I)
                    if matches:
                        video_url = matches[0]
                        break
                if video_url:
                    break
        if not video_url:
            video_tag = soup.find('video')
            if video_tag:
                src = video_tag.get('src')
                if src and '.m3u8' in src:
                    video_url = src

        if not video_url:
            raise Exception("未找到视频源 m3u8，页面可能改版")

        # 规范化 URL
        if video_url.startswith('//'):
            video_url = "https:" + video_url
        elif video_url.startswith('/'):
            video_url = base + video_url

        return {
            "id": video_id,
            "code": code,
            "title": title,
            "cover": cover,
            "actors": actors,
            "description": desc[:500],
            "video_url": video_url,
            "url": url,
        }

fetcher = MissAVFetcher()

@router.get("/search")
async def missav_search(q: str = Query(..., min_length=1)):
    try:
        items = fetcher.search(q)
        return {"ok": True, "count": len(items), "items": items}
    except Exception as e:
        # 返回具体错误信息供前端显示
        raise HTTPException(status_code=502, detail=f"搜索失败: {str(e)}")

@router.get("/info")
async def missav_info(video_id: str = Query(...)):
    try:
        data = fetcher.get_detail(video_id)
        return {"ok": True, "item": data}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"获取详情失败: {str(e)}")
