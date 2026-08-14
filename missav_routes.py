# ============================================================
# missav_routes.py - MissAV 全部功能（独立模块）
# ============================================================

import re
from urllib.parse import quote
from fastapi import APIRouter, HTTPException, Query
import cloudscraper
from bs4 import BeautifulSoup

router = APIRouter(prefix="/missav", tags=["MissAV"])

class MissAVFetcher:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
        )
        self.base_url = "https://missav.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Referer": "https://missav.com/",
        }

    def _fetch(self, url):
        resp = self.scraper.get(url, headers=self.headers, timeout=30)
        if resp.status_code != 200:
            raise Exception(f"抓取失败 HTTP {resp.status_code}")
        return resp.text

    def search(self, keyword):
        if len(keyword) < 2:
            raise ValueError("至少输入2个字符")
        html = self._fetch(f"{self.base_url}/search/{quote(keyword)}")
        soup = BeautifulSoup(html, 'lxml')
        results = []
        seen = set()
        for a in soup.select('a[href*="/watch/"]'):
            href = a.get('href')
            if not href or href in seen:
                continue
            img = a.find('img')
            src = img.get('src') or img.get('data-src') or "" if img else ""
            if src and src.startswith('//'):
                src = "https:" + src
            title = a.get('title') or img.get('alt') if img else "未知"
            code_match = re.search(r'([A-Z]{2,6}-\d{3,5})', title)
            code = code_match.group(1) if code_match else "未知"
            results.append({
                "id": href.split('/')[-1],
                "url": self.base_url + href if href.startswith('/') else href,
                "title": title.strip(),
                "code": code,
                "cover": src,
            })
            seen.add(href)
            if len(results) >= 30:
                break
        return results

    def get_detail(self, video_id):
        html = self._fetch(f"{self.base_url}/watch/{video_id}")
        soup = BeautifulSoup(html, 'lxml')
        title = soup.find('h1').text.strip() if soup.find('h1') else "未知"
        code_match = re.search(r'([A-Z]{2,6}-\d{3,5})', title)
        code = code_match.group(1) if code_match else "未知"
        cover = ""
        img = soup.select_one('img[alt*="cover"], img[src*="cover"]')
        if img:
            cover = img.get('src') or img.get('data-src') or ""
            if cover.startswith('//'):
                cover = "https:" + cover
        actors = [a.text.strip() for a in soup.select('a[href*="/actor/"]') if a.text.strip()]
        desc = soup.find('meta', attrs={'name': 'description'})
        desc = desc.get('content', "") if desc else ""
        video_url = ""
        for script in soup.find_all('script'):
            if script.string:
                matches = re.findall(r'video_url\s*[:=]\s*["\'](https?://[^"\']+\.m3u8[^"\']*)["\']', script.string)
                if matches:
                    video_url = matches[0]
                    break
        if not video_url:
            video_tag = soup.find('video')
            if video_tag and video_tag.get('src'):
                video_url = video_tag.get('src')
        if not video_url:
            raise Exception("未找到视频源 m3u8，页面可能改版")
        return {
            "id": video_id,
            "code": code,
            "title": title,
            "cover": cover,
            "actors": actors,
            "description": desc[:300],
            "video_url": video_url,
            "url": f"{self.base_url}/watch/{video_id}",
        }

fetcher = MissAVFetcher()

@router.get("/search")
async def missav_search(q: str = Query(..., min_length=1)):
    try:
        items = fetcher.search(q)
        return {"ok": True, "count": len(items), "items": items}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

@router.get("/info")
async def missav_info(video_id: str = Query(...)):
    try:
        data = fetcher.get_detail(video_id)
        return {"ok": True, "item": data}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
