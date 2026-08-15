# ============================================================
# missav_routes.py - MissAV 下载器（curl_cffi + BeautifulSoup）
# 完全自主控制代理和指纹，不依赖第三方库
# ============================================================

import os
import re
import asyncio
from urllib.parse import urlparse, quote
from fastapi import APIRouter, HTTPException, Query
from curl_cffi import requests
from bs4 import BeautifulSoup

router = APIRouter(prefix="/missav", tags=["MissAV"])

# ============================================================
# 配置（从环境变量读取）
# ============================================================
PROXY = os.environ.get("MISSAV_PROXY")  # 例如 http://user:pass@host:port
IMPERSONATE = os.environ.get("MISSAV_IMPERSONATE", "chrome124")

# 全局会话（复用）
_session = None

def get_session():
    global _session
    if _session is None:
        _session = requests.Session(impersonate=IMPERSONATE)
        if PROXY:
            _session.proxies = {"http": PROXY, "https": PROXY}
        print(f"[MissAV] 会话初始化（指纹: {IMPERSONATE}, 代理: {PROXY if PROXY else '无'}）")
    return _session

# ============================================================
# 工具函数
# ============================================================
async def fetch_html(url):
    """使用 curl_cffi 获取 HTML"""
    session = get_session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://missav.ws/",
    }
    try:
        response = await asyncio.to_thread(session.get, url, headers=headers, timeout=30)
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}")
        return response.text
    except Exception as e:
        raise Exception(f"请求失败: {str(e)}")

def parse_search(html, base_url):
    """解析搜索页"""
    soup = BeautifulSoup(html, 'lxml')
    results = []
    seen = set()
    # 查找视频链接（支持 /watch/、/dm1/、/v/）
    links = soup.select('a[href*="/watch/"], a[href*="/dm1/"], a[href*="/v/"]')
    if not links:
        links = soup.find_all('a', href=re.compile(r'/(watch|dm1|v)/[^/]+'))
    for a in links:
        href = a.get('href')
        if not href or href in seen:
            continue
        full_url = base_url + href if href.startswith('/') else href
        video_id = href.split('/')[-1]
        img = a.find('img')
        cover = ""
        if img:
            cover = img.get('src') or img.get('data-src') or ""
            if cover.startswith('//'):
                cover = "https:" + cover
        title = a.get('title') or (img.get('alt') if img else "") or "未知"
        code_match = re.search(r'([A-Z]{2,6}-\d{3,5})', title)
        code = code_match.group(1) if code_match else ""
        results.append({
            "id": video_id,
            "url": full_url,
            "title": title.strip(),
            "code": code,
            "cover": cover,
        })
        seen.add(href)
        if len(results) >= 30:
            break
    return results

def parse_detail(html, base_url):
    """解析详情页"""
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
    if cover.startswith('//'):
        cover = "https:" + cover
    actors = [a.text.strip() for a in soup.select('a[href*="/actor/"]') if a.text.strip()]
    desc = ""
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc:
        desc = meta_desc.get('content', '')
    # 提取 m3u8
    video_url = ""
    for script in soup.find_all('script'):
        if script.string:
            content = script.string
            for pat in [r'video_url\s*[:=]\s*["\'](https?://[^"\']+\.m3u8[^"\']*)["\']',
                        r'videoUrl\s*[:=]\s*["\'](https?://[^"\']+\.m3u8[^"\']*)["\']',
                        r'(https?://[^\s"\']+\.m3u8[^\s"\']*)']:
                matches = re.findall(pat, content, re.I)
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
    return {
        "id": video_url.split('/')[-1].split('.')[0],
        "code": code,
        "title": title,
        "cover": cover,
        "actors": actors,
        "description": desc[:500],
        "video_url": video_url,
        "url": "",  # 可补充
    }

# ============================================================
# API 接口
# ============================================================
@router.get("/search")
async def missav_search(q: str = Query(..., min_length=1)):
    try:
        base_url = "https://missav.ws"
        for path in [f"/search/{quote(q)}", f"/search?q={quote(q)}"]:
            url = base_url + path
            try:
                html = await fetch_html(url)
                if len(html) < 500:
                    continue
                items = parse_search(html, base_url)
                if items:
                    return {"ok": True, "count": len(items), "items": items}
            except Exception as e:
                print(f"[MissAV] 搜索路径 {path} 失败: {e}")
                continue
        # 尝试备用域名
        for domain in ["missav.ai"]:
            base_url = "https://" + domain
            for path in [f"/search/{quote(q)}", f"/search?q={quote(q)}"]:
                url = base_url + path
                try:
                    html = await fetch_html(url)
                    if len(html) < 500:
                        continue
                    items = parse_search(html, base_url)
                    if items:
                        return {"ok": True, "count": len(items), "items": items}
                except:
                    continue
        raise Exception("所有搜索尝试均失败")
    except Exception as e:
        print(f"[MissAV] 搜索失败: {e}")
        raise HTTPException(status_code=502, detail=f"搜索失败: {str(e)}")

@router.get("/info")
async def missav_info(video_id: str = Query(...)):
    try:
        base_url = "https://missav.ws"
        for path in [f"/watch/{video_id}", f"/dm1/{video_id}", f"/v/{video_id}"]:
            url = base_url + path
            try:
                html = await fetch_html(url)
                if len(html) < 500:
                    continue
                detail = parse_detail(html, base_url)
                detail["id"] = video_id
                return {"ok": True, "item": detail}
            except:
                continue
        raise Exception("所有详情路径均失败")
    except Exception as e:
        print(f"[MissAV] 详情获取失败: {e}")
        raise HTTPException(status_code=502, detail=f"获取详情失败: {str(e)}")
