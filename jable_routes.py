# ============================================================
# jable_routes.py - Jable 模块
# 数据源：https://jable.tv
# 复用 shared.missav_db
# ============================================================

import re
from urllib.parse import quote
from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import BaseModel
import httpx
from bs4 import BeautifulSoup

from shared import missav_db

router = APIRouter(prefix="/api/jable", tags=["Jable"])

# ============================================================
# 模型
# ============================================================

class CollectItem(BaseModel):
    video_id: str
    title: str
    actress: str | None = None
    description: str | None = None
    publish_date: str | None = None
    cover_url: str | None = None
    m3u8_url: str
    source_url: str | None = None

# ============================================================
# 工具函数
# ============================================================

def is_developer(request: Request):
    return bool(request.cookies.get("session"))

# ============================================================
# Jable 抓取器
# ============================================================

class JableFetcher:
    def __init__(self):
        self.base_url = "https://jable.tv"
        self.timeout = 30
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        self.client = httpx.Client(timeout=self.timeout, follow_redirects=True, headers=self.headers)

    def _fetch(self, url: str) -> str:
        resp = self.client.get(url)
        if resp.status_code != 200:
            raise Exception(f"HTTP {resp.status_code}")
        return resp.text

    def search(self, keyword: str) -> list[dict]:
        """搜索关键词，返回视频列表"""
        search_url = f"{self.base_url}/search/{quote(keyword)}/"
        html = self._fetch(search_url)
        soup = BeautifulSoup(html, 'lxml')
        results = []
        seen = set()

        for a in soup.select('a[href*="/videos/"]'):
            href = a.get('href')
            if not href or href in seen:
                continue
            if href.startswith('/'):
                href = self.base_url + href

            img = a.find('img')
            title = a.get('title') or (img.get('alt') if img else '')
            cover = img.get('src') or img.get('data-src') if img else ''
            if cover.startswith('//'):
                cover = 'https:' + cover

            video_id = href.split('/')[-2] if href.endswith('/') else href.split('/')[-1]

            results.append({
                "id": video_id,
                "url": href,
                "title": title.strip(),
                "cover": cover,
            })
            seen.add(href)
            if len(results) >= 30:
                break

        return results

    def detail(self, video_id: str) -> dict:
        """获取视频详情"""
        detail_url = f"{self.base_url}/videos/{video_id}/"
        html = self._fetch(detail_url)
        soup = BeautifulSoup(html, 'lxml')

        # 标题
        title_tag = soup.find('h1')
        title = title_tag.text.strip() if title_tag else "未知"

        # 女优
        actress = ""
        actress_link = soup.select_one('a[href*="/actress/"]')
        if actress_link:
            actress = actress_link.text.strip()
        elif '※' in title:
            parts = title.split('※')
            if len(parts) > 1:
                actress = parts[-1].strip()

        # 封面
        cover = ""
        meta_og = soup.find('meta', property='og:image')
        if meta_og:
            cover = meta_og.get('content')
        if cover and cover.startswith('//'):
            cover = 'https:' + cover

        # 简介
        desc = ""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            desc = meta_desc.get('content', '')

        # 发布日期
        publish_date = ""
        date_pattern = re.compile(r'(\d{4}-\d{2}-\d{2})')
        date_match = date_pattern.search(html)
        if date_match:
            publish_date = date_match.group(1)

        # m3u8 地址
        video_url = ""
        video_tag = soup.find('video')
        if video_tag and video_tag.get('src'):
            video_url = video_tag.get('src')
        if not video_url:
            for script in soup.find_all('script'):
                if script.string:
                    matches = re.search(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', script.string)
                    if matches:
                        video_url = matches.group(1)
                        break
        if not video_url:
            iframe = soup.find('iframe')
            if iframe and iframe.get('src'):
                video_url = iframe.get('src')

        return {
            "id": video_id,
            "title": title,
            "actress": actress,
            "cover": cover,
            "description": desc,
            "publish_date": publish_date,
            "video_url": video_url,
            "url": detail_url,
        }

fetcher = JableFetcher()

# ============================================================
# API
# ============================================================

@router.get("/search")
async def search_jable(q: str = Query(..., min_length=1)):
    try:
        items = fetcher.search(q)
        return {"ok": True, "count": len(items), "items": items}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"搜索失败: {str(e)}")

@router.get("/info")
async def info_jable(video_id: str):
    try:
        data = fetcher.detail(video_id)
        return {"ok": True, "item": data}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"获取详情失败: {str(e)}")

@router.post("/collect")
async def collect_jable_item(request: Request, item: CollectItem):
    if not is_developer(request):
        return {"ok": True, "stored": False, "message": "guest mode"}
    if missav_db is None:
        raise HTTPException(status_code=500, detail="MissAV 数据库未配置")
    try:
        await missav_db.execute("""
            CREATE TABLE IF NOT EXISTS public.missav_items (
                id SERIAL PRIMARY KEY,
                video_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                actress TEXT,
                description TEXT,
                publish_date DATE,
                cover_url TEXT,
                m3u8_url TEXT,
                source_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        existing = await missav_db.fetch_one(
            "SELECT id FROM public.missav_items WHERE video_id = :video_id",
            {"video_id": item.video_id}
        )
        params = item.dict()
        if existing:
            await missav_db.execute("""
                UPDATE public.missav_items SET
                    title = :title,
                    actress = :actress,
                    description = :description,
                    publish_date = :publish_date,
                    cover_url = :cover_url,
                    m3u8_url = :m3u8_url,
                    source_url = :source_url,
                    created_at = CURRENT_TIMESTAMP
                WHERE video_id = :video_id
            """, params)
        else:
            await missav_db.execute("""
                INSERT INTO public.missav_items (
                    video_id, title, actress, description,
                    publish_date, cover_url, m3u8_url, source_url
                )
                VALUES (
                    :video_id, :title, :actress, :description,
                    :publish_date, :cover_url, :m3u8_url, :source_url
                )
            """, params)
        return {"ok": True, "stored": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/my-items")
async def get_my_items(request: Request):
    if not is_developer(request):
        return {"ok": True, "items": [], "mode": "guest"}
    if missav_db is None:
        return {"ok": True, "items": [], "mode": "developer", "message": "database not configured"}
    try:
        rows = await missav_db.fetch_all("SELECT * FROM public.missav_items ORDER BY created_at DESC")
        return {"ok": True, "items": [dict(row) for row in rows], "mode": "developer"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/db-search")
async def search_db_items(q: str = ""):
    try:
        rows = await missav_db.fetch_all("""
            SELECT * FROM public.missav_items
            WHERE LOWER(video_id) LIKE LOWER(:q) OR LOWER(title) LIKE LOWER(:q)
            ORDER BY created_at DESC
        """, {"q": f"%{q}%"})
        return {"ok": True, "items": [dict(row) for row in rows]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/actress/{name}")
async def actress_items(name: str):
    try:
        rows = await missav_db.fetch_all("""
            SELECT * FROM public.missav_items
            WHERE LOWER(actress) LIKE LOWER(:name)
            ORDER BY created_at DESC
        """, {"name": f"%{name}%"})
        return {"ok": True, "items": [dict(row) for row in rows]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def stats():
    try:
        total = await missav_db.fetch_val("SELECT COUNT(*) FROM public.missav_items")
        actresses = await missav_db.fetch_val("SELECT COUNT(DISTINCT actress) FROM public.missav_items")
        return {"ok": True, "total": total, "actresses": actresses}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/clear")
async def clear_items(request: Request):
    if not is_developer(request):
        raise HTTPException(status_code=403, detail="permission denied")
    try:
        await missav_db.execute("DELETE FROM public.missav_items")
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/debug-db")
async def debug_db():
    if missav_db is None:
        return {"ok": False, "message": "database not configured"}
    try:
        identity = await missav_db.fetch_one("""
            SELECT
                current_database() AS database_name,
                current_user AS user_name,
                current_schema() AS schema_name,
                inet_server_addr() AS server_address,
                inet_server_port() AS server_port,
                current_setting('search_path') AS search_path
        """)
        table_info = await missav_db.fetch_one("""
            SELECT table_catalog, table_schema, table_name
            FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'missav_items'
        """)
        table_count = None
        if table_info:
            table_count = await missav_db.fetch_val("SELECT COUNT(*) FROM public.missav_items")
        return {
            "ok": True,
            "connection": {
                "database": identity["database_name"] if identity else None,
                "user": identity["user_name"] if identity else None,
                "schema": identity["schema_name"] if identity else None,
                "server_address": str(identity["server_address"]) if identity and identity["server_address"] else None,
                "server_port": identity["server_port"] if identity else None,
                "search_path": identity["search_path"] if identity else None,
            },
            "missav_items": {
                "exists": bool(table_info),
                "catalog": table_info["table_catalog"] if table_info else None,
                "schema": table_info["table_schema"] if table_info else None,
                "table": table_info["table_name"] if table_info else None,
                "count": table_count,
            }
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}
