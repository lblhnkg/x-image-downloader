# ============================================================
# missav_routes.py - Cookie 会话方案（支持开发者和访客）
# ============================================================

import re
import time
from urllib.parse import quote, urlparse
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel
import httpx
from bs4 import BeautifulSoup

router = APIRouter(prefix="/missav", tags=["MissAV"])

# 全局存储开发者 Cookie（仅存一个，新覆盖旧）
developer_cookie = None

class CookieSet(BaseModel):
    cookie_string: str

@router.post("/set-cookie")
async def set_cookie(data: CookieSet):
    """开发者模式：保存 Cookie 到服务器（替换）"""
    global developer_cookie
    developer_cookie = data.cookie_string.strip()
    return {"ok": True, "message": "Cookie 已保存（开发者模式）"}

@router.get("/cookie-status")
async def cookie_status():
    """检查开发者 Cookie 是否存在"""
    return {"ok": True, "has_cookie": bool(developer_cookie)}

class MissAVFetcher:
    def __init__(self):
        self.base_domains = ["missav.ws", "missav.ai"]
        self.timeout = 30
        self.client = httpx.Client(timeout=self.timeout, follow_redirects=True)

    def _fetch_with_cookies(self, url, cookie_str):
        """使用传入的 Cookie 请求"""
        if not cookie_str:
            raise Exception("未提供 Cookie，请先设置")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://missav.ws/",
            "Cookie": cookie_str,
        }

        for attempt in range(3):
            try:
                resp = self.client.get(url, headers=headers)
                if resp.status_code == 200:
                    if "Just a moment" in resp.text or "Cloudflare" in resp.text[:500]:
                        raise Exception("Cookie 已过期，请重新获取")
                    return resp.text
                time.sleep(1 * (attempt + 1))
            except Exception as e:
                if attempt == 2:
                    raise
                time.sleep(1 * (attempt + 1))
        raise Exception("请求失败")

    def search(self, keyword, cookie_str):
        if len(keyword) < 2:
            raise ValueError("至少输入2个字符")
        for domain in self.base_domains:
            base = "https://" + domain
            for path in [f"/search/{quote(keyword)}", f"/search?q={quote(keyword)}"]:
                url = base + path
                try:
                    html = self._fetch_with_cookies(url, cookie_str)
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

    def get_detail(self, video_id_or_url, cookie_str):
        if video_id_or_url.startswith('http'):
            parsed = urlparse(video_id_or_url)
            base = f"{parsed.scheme}://{parsed.netloc}"
            html = self._fetch_with_cookies(video_id_or_url, cookie_str)
            return self._parse_detail(html, base, video_id_or_url, video_id_or_url)
        for domain in self.base_domains:
            base = "https://" + domain
            for path in [f"/watch/{video_id_or_url}", f"/dm1/{video_id_or_url}", f"/v/{video_id_or_url}"]:
                url = base + path
                try:
                    html = self._fetch_with_cookies(url, cookie_str)
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
async def missav_search(request: Request, q: str = Query(..., min_length=1)):
    try:
        # 优先从请求头获取访客 Cookie，否则使用开发者 Cookie
        cookie = request.headers.get("X-User-Cookie")
        if not cookie:
            cookie = developer_cookie
        if not cookie:
            raise HTTPException(status_code=400, detail="未设置 Cookie，请先获取")
        items = fetcher.search(q, cookie)
        return {"ok": True, "count": len(items), "items": items}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"搜索失败: {str(e)}")

@router.get("/info")
async def missav_info(request: Request, video_id: str = Query(...)):
    try:
        cookie = request.headers.get("X-User-Cookie")
        if not cookie:
            cookie = developer_cookie
        if not cookie:
            raise HTTPException(status_code=400, detail="未设置 Cookie，请先获取")
        data = fetcher.get_detail(video_id, cookie)
        return {"ok": True, "item": data}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"获取详情失败: {str(e)}")
