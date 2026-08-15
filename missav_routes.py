import os
import re
import time
from urllib.parse import quote, urlparse
from fastapi import APIRouter, HTTPException, Query
import httpx
from bs4 import BeautifulSoup

router = APIRouter(prefix="/missav", tags=["MissAV"])

SCRAPINGBEE_KEY = os.environ.get("SCRAPINGBEE_KEY")
if not SCRAPINGBEE_KEY:
    print("⚠️ 警告：SCRAPINGBEE_KEY 未设置")

class MissAVFetcher:
    def __init__(self):
        self.base_domains = ["missav.ws", "missav.ai"]
        self.timeout = 60
        self.max_retries = 3

    def _fetch_via_scrapingbee(self, url):
        """通过 ScrapingBee 代理抓取"""
        if not SCRAPINGBEE_KEY:
            raise Exception("SCRAPINGBEE_KEY 未配置")
        
        # ScrapingBee API 参数：启用 JS 渲染，模拟移动端
        params = {
            "api_key": SCRAPINGBEE_KEY,
            "url": url,
            "render_js": "true",
            "premium_proxy": "false",  # 免费版使用普通代理
            "country_code": "us",
            "wait": "3000",  # 等待 JS 加载
        }
        # 构建请求 URL
        base_url = "https://app.scrapingbee.com/api/v1/"
        resp = httpx.get(base_url, params=params, timeout=self.timeout)
        if resp.status_code == 200:
            return resp.text
        else:
            raise Exception(f"ScrapingBee 返回 {resp.status_code}: {resp.text[:200]}")

    def search(self, keyword):
        if len(keyword) < 2:
            raise ValueError("至少输入2个字符")
        for domain in self.base_domains:
            base = "https://" + domain
            for path in [f"/search/{quote(keyword)}", f"/search?q={quote(keyword)}"]:
                url = base + path
                try:
                    html = self._fetch_via_scrapingbee(url)
                    if len(html) < 500:
                        continue
                    soup = BeautifulSoup(html, 'lxml')
                    links = soup.select('a[href*="/watch/"], a[href*="/dm1/"], a[href*="/v/"]')
                    if not links:
                        links = soup.find_all('a', href=re.compile(r'/(watch|dm1|v)/[^/]+'))
                    if links:
                        return self._parse_search(html, base)
                except Exception as e:
                    print(f"[MissAV] 搜索尝试失败 {url}: {e}")
                    continue
        raise Exception("所有搜索尝试均失败")

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
            full_url = base + href if href.startswith('/') else href
            video_id = href.split('/')[-1] if href.split('/') else ""
            img = a.find('img')
            src = ""
            if img:
                src = img.get('src') or img.get('data-src') or img.get('data-original') or ""
                if src.startswith('//'):
                    src = "https:" + src
                elif src.startswith('/'):
                    src = base + src
            title = a.get('title', '') or (img.get('alt', '') if img else '')
            title = title.strip() or "未知标题"
            code_match = re.search(r'([A-Z]{2,6}-\d{3,5})', title)
            code = code_match.group(1) if code_match else ""
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
        if video_id_or_url.startswith('http'):
            parsed = urlparse(video_id_or_url)
            base = f"{parsed.scheme}://{parsed.netloc}"
            html = self._fetch_via_scrapingbee(video_id_or_url)
            return self._parse_detail(html, base, video_id_or_url, video_id_or_url)
        for domain in self.base_domains:
            base = "https://" + domain
            for path in [f"/watch/{video_id_or_url}", f"/dm1/{video_id_or_url}", f"/v/{video_id_or_url}"]:
                url = base + path
                try:
                    html = self._fetch_via_scrapingbee(url)
                    if len(html) < 500:
                        continue
                    return self._parse_detail(html, base, video_id_or_url, url)
                except Exception as e:
                    print(f"[MissAV] 详情尝试失败 {url}: {e}")
                    continue
        raise Exception("所有详情尝试均失败")

    def _parse_detail(self, html, base, video_id, url):
        soup = BeautifulSoup(html, 'lxml')
        title = soup.find('h1').text.strip() if soup.find('h1') else "未知"
        code_match = re.search(r'([A-Z]{2,6}-\d{3,5})', title)
        code = code_match.group(1) if code_match else ""
        cover = ""
        meta_og = soup.find('meta', property='og:image')
        if meta_og:
            cover = meta_og.get('content', '')
        if not cover:
            img = soup.select_one('img[alt*="cover"], img[src*="cover"]')
            if img:
                cover = img.get('src') or img.get('data-src') or ""
        if cover and cover.startswith('//'):
            cover = "https:" + cover
        elif cover and cover.startswith('/'):
            cover = base + cover
        actors = [a.text.strip() for a in soup.select('a[href*="/actor/"]') if a.text.strip()]
        actors = list(dict.fromkeys(actors))
        desc = ""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            desc = meta_desc.get('content', '')
        video_url = ""
        for script in soup.find_all('script'):
            if script.string:
                for pat in [r'video_url\s*[:=]\s*["\'](https?://[^"\']+\.m3u8[^"\']*)["\']',
                            r'videoUrl\s*[:=]\s*["\'](https?://[^"\']+\.m3u8[^"\']*)["\']',
                            r'(https?://[^\s"\']+\.m3u8[^\s"\']*)']:
                    matches = re.findall(pat, script.string, re.I)
                    if matches:
                        video_url = matches[0]
                        break
                if video_url:
                    break
        if not video_url:
            video_tag = soup.find('video')
            if video_tag and video_tag.get('src'):
                video_url = video_tag.get('src')
        if not video_url:
            raise Exception("未找到视频源 m3u8")
        if video_url.startswith('//'):
            video_url = "https:" + video_url
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
