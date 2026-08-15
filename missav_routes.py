# ============================================================
# missav_routes.py - 通过 ScraperAPI 代理抓取（最终稳定版）
# ============================================================

import os
import re
import time
from urllib.parse import quote, urlparse
from fastapi import APIRouter, HTTPException, Query
import httpx
from bs4 import BeautifulSoup

router = APIRouter(prefix="/missav", tags=["MissAV"])

SCRAPERAPI_KEY = os.environ.get("SCRAPERAPI_KEY")
if not SCRAPERAPI_KEY:
    print("⚠️ 警告：SCRAPERAPI_KEY 未设置，MissAV 功能将不可用")

class MissAVFetcher:
    def __init__(self):
        self.base_domains = ["missav.ws", "missav.ai"]
        self.timeout = 60
        self.max_retries = 3

    def _fetch_via_scraperapi(self, url):
        """通过 ScraperAPI 获取页面内容（自动绕过 Cloudflare）"""
        if not SCRAPERAPI_KEY:
            raise Exception("SCRAPERAPI_KEY 未配置，请在 Render 环境变量中设置")
        
        # ScraperAPI 请求格式：添加 render=true 启用 JS 渲染，提高成功率
        encoded_url = quote(url, safe='')
        proxy_url = f"http://api.scraperapi.com?api_key={SCRAPERAPI_KEY}&url={encoded_url}&render=true"
        
        with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
            for attempt in range(self.max_retries):
                try:
                    print(f"[MissAV] 请求代理: {url}")
                    resp = client.get(proxy_url)
                    
                    if resp.status_code == 200:
                        # 检查是否包含验证页关键词
                        lower_text = resp.text[:500].lower()
                        if "just a moment" in lower_text or "cloudflare" in lower_text:
                            print(f"[MissAV] 代理返回验证页，重试 {attempt+1}/{self.max_retries}")
                            time.sleep(2 ** attempt)
                            continue
                        return resp.text
                    else:
                        print(f"[MissAV] 代理返回状态码 {resp.status_code}，重试 {attempt+1}")
                        time.sleep(1 * (attempt + 1))
                except httpx.TimeoutException:
                    print(f"[MissAV] 代理请求超时，重试 {attempt+1}")
                    time.sleep(2 ** attempt)
                except Exception as e:
                    print(f"[MissAV] 代理请求异常: {e}，重试 {attempt+1}")
                    time.sleep(1 * (attempt + 1))
            
            raise Exception("所有代理请求均失败，请检查 SCRAPERAPI_KEY 是否有效")

    def search(self, keyword):
        if len(keyword) < 2:
            raise ValueError("至少输入2个字符")

        for domain in self.base_domains:
            base = "https://" + domain
            # 尝试两种搜索路径格式
            for path in [f"/search/{quote(keyword)}", f"/search?q={quote(keyword)}"]:
                url = base + path
                try:
                    print(f"[MissAV] 尝试搜索: {url}")
                    html = self._fetch_via_scraperapi(url)
                    if len(html) < 500:
                        print(f"[MissAV] HTML 长度不足 {len(html)}，跳过")
                        continue
                    
                    soup = BeautifulSoup(html, 'lxml')
                    # 检查是否找到了视频链接
                    links = soup.select('a[href*="/watch/"], a[href*="/dm1/"], a[href*="/v/"]')
                    if not links:
                        # 尝试更通用的正则查找
                        links = soup.find_all('a', href=re.compile(r'/(watch|dm1|v)/[^/]+'))
                    
                    if not links:
                        print(f"[MissAV] 未找到视频链接，可能网站结构变化")
                        continue
                    
                    return self._parse_search(html, base)
                except Exception as e:
                    print(f"[MissAV] 搜索尝试失败 {url}: {e}")
                    continue
        
        raise Exception("所有域名和搜索路径均失败，可能网站屏蔽了代理 IP")

    def _parse_search(self, html, base):
        soup = BeautifulSoup(html, 'lxml')
        results = []
        seen = set()
        
        links = soup.select('a[href*="/watch/"], a[href*="/dm1/"], a[href*="/v/"]')
        if not links:
            links = soup.find_all('a', href=re.compile(r'/(watch|dm1|v)/[^/]+'))

        for a in links:
            href = a.get('href')
            if not href or href in seen:
                continue
            
            # 补全 URL
            full_url = base + href if href.startswith('/') else href
            video_id = href.split('/')[-1] if href.split('/') else ""

            # 提取封面图
            img = a.find('img')
            src = ""
            if img:
                src = img.get('src') or img.get('data-src') or img.get('data-original') or ""
                if src.startswith('//'):
                    src = "https:" + src
                elif src.startswith('/'):
                    src = base + src
            
            # 如果 img 没找到，尝试从 style 背景中提取
            if not src:
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

            # 番号（从标题或 URL 中提取）
            code = ""
            code_match = re.search(r'([A-Z]{2,6}-\d{3,5})', title)
            if code_match:
                code = code_match.group(1)
            else:
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
        """获取详情页"""
        # 如果传入的是完整 URL
        if video_id_or_url.startswith('http'):
            parsed = urlparse(video_id_or_url)
            base = f"{parsed.scheme}://{parsed.netloc}"
            html = self._fetch_via_scraperapi(video_id_or_url)
            return self._parse_detail(html, base, video_id_or_url, video_id_or_url)

        # 否则按 ID 尝试多种路径
        for domain in self.base_domains:
            base = "https://" + domain
            for path in [f"/watch/{video_id_or_url}", f"/dm1/{video_id_or_url}", f"/v/{video_id_or_url}"]:
                url = base + path
                try:
                    html = self._fetch_via_scraperapi(url)
                    if len(html) < 500:
                        continue
                    return self._parse_detail(html, base, video_id_or_url, url)
                except Exception as e:
                    print(f"[MissAV] 详情尝试失败 {url}: {e}")
                    continue
        
        raise Exception("所有详情尝试均失败")

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

        # 视频源 m3u8（核心）
        video_url = ""
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                content = script.string
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
        raise HTTPException(status_code=502, detail=f"搜索失败: {str(e)}")

@router.get("/info")
async def missav_info(video_id: str = Query(...)):
    try:
        data = fetcher.get_detail(video_id)
        return {"ok": True, "item": data}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"获取详情失败: {str(e)}")
