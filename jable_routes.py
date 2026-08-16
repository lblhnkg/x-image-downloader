# ============================================================
# jable_routes.py - Jable 模块（curl_cffi + Safari 指纹）
# 数据源：https://jable.tv
# 增加时长提取
# ============================================================

import re
import time
import random
from urllib.parse import quote
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel
from curl_cffi import requests
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
# Jable 抓取器（curl_cffi + HTTP 代理 + Safari 指纹）
# ============================================================

class JableFetcher:
    def __init__(self):
        self.base_url = "https://jable.tv"
        self.timeout = 30
        self.headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }
        # HTTP 代理（sing-box 监听 127.0.0.1:1081）
        self.proxies = {
            "http": "http://127.0.0.1:1081",
            "https": "http://127.0.0.1:1081"
        }
        # 使用 curl_cffi 的 Session，模拟 Safari 指纹
        self.session = requests.Session(
            impersonate="safari15_5",
            proxies=self.proxies,
            timeout=self.timeout
        )
        self.session.headers.update(self.headers)

    def _fetch(self, url: str, is_retry: bool = False) -> str:
        if not is_retry:
            delay = random.uniform(1, 3)
            print(f"[Jable] 等待 {delay:.1f} 秒后请求...")
            time.sleep(delay)
        else:
            delay = random.uniform(10, 20)
            print(f"[Jable] 重试前等待 {delay:.1f} 秒...")
            time.sleep(delay)

        print(f"[Jable] 请求 {url}")
        try:
            resp = self.session.get(url)
            print(f"[Jable] 状态码 {resp.status_code}")
            if resp.status_code != 200:
                if resp.status_code == 403 and not is_retry:
                    print(f"[Jable] 收到 403，将重试一次（等待 10-20 秒）...")
                    return self._fetch(url, is_retry=True)
                raise Exception(f"HTTP {resp.status_code}")
            return resp.text
        except Exception as e:
            if not is_retry and ("SSLError" in str(e) or "Connection" in str(e) or "Max retries" in str(e)):
                print(f"[Jable] 请求异常，将重试一次（等待 10-20 秒）...")
                return self._fetch(url, is_retry=True)
            print(f"[Jable] 请求失败: {e}")
            raise

    def search(self, keyword: str) -> list[dict]:
        search_url = f"{self.base_url}/search/{quote(keyword)}/"
        html = self._fetch(search_url)
        soup = BeautifulSoup(html, 'lxml')
        results = []
        seen = set()
        norm_keyword = keyword.strip().lower()

        for a in soup.select('a[href*="/videos/"]'):
            href = a.get('href')
            if not href or href in seen:
                continue
            if href.startswith('/'):
                href = self.base_url + href

            video_id = href.split('/')[-2] if href.endswith('/') else href.split('/')[-1]

            img = a.find('img')
            cover = ""
            if img:
                cover = img.get('src') or img.get('data-src') or ""
                if cover.startswith('//'):
                    cover = 'https:' + cover
                if 'placeholder' in cover and img.get('data-src'):
                    cover = img.get('data-src')
                    if cover.startswith('//'):
                        cover = 'https:' + cover

            title = ""
            detail_div = a.find_parent('div', class_='video-img-box')
            if detail_div:
                title_tag = detail_div.select_one('h6.title a')
                if title_tag:
                    title = title_tag.text.strip()
            if not title:
                title = a.get('title') or ''

            results.append({
                "id": video_id,
                "url": href,
                "title": title,
                "cover": cover,
            })
            seen.add(href)
            if len(results) >= 30:
                break

        results.sort(key=lambda x: x["id"].lower() != norm_keyword)
        return results

    def detail(self, video_id: str) -> dict:
        detail_url = f"{self.base_url}/videos/{video_id}/"
        html = self._fetch(detail_url)
        soup = BeautifulSoup(html, 'lxml')

        # 标题
        title_tag = soup.find('h1')
        title = title_tag.text.strip() if title_tag else ""
        if not title:
            meta_title = soup.find('meta', property='og:title')
            if meta_title:
                title = meta_title.get('content', '')

        # 番号
        code = ""
        code_match = re.match(r'^([A-Z]{2,6}-\d{3,5})', title)
        if code_match:
            code = code_match.group(1)

        # 女优
        actress = ""
        models = soup.select('a[href*="/models/"]')
        if models:
            actress_names = []
            for m in models:
                name = m.text.strip()
                if name:
                    actress_names.append(name)
            actress = ' '.join(actress_names)

        if not actress and title:
            title_without_code = re.sub(r'^[A-Z]{2,6}-\d{3,5}\s*', '', title)
            words = title_without_code.split(' ')
            if len(words) >= 2:
                possible = words[-2:]
                if any('\u4e00' <= c <= '\u9fff' for word in possible for c in word):
                    actress = ' '.join(possible)

        # 封面
        cover = ""
        meta_og = soup.find('meta', property='og:image')
        if meta_og:
            cover = meta_og.get('content', '')
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

        # ===== 新增：时长 =====
        duration_str = ""
        duration_seconds = None
        # 尝试从 og:video:duration 获取
        duration_meta = soup.find('meta', property='og:video:duration')
        if duration_meta:
            try:
                duration_seconds = int(duration_meta.get('content', 0))
            except:
                pass
        # 如果没有，尝试从 video 标签的 duration 属性获取
        if not duration_seconds:
            video_tag = soup.find('video')
            if video_tag and video_tag.get('duration'):
                try:
                    duration_seconds = int(float(video_tag.get('duration')))
                except:
                    pass
        # 格式化为 HH:MM:SS 或 MM:SS
        if duration_seconds:
            hours = duration_seconds // 3600
            minutes = (duration_seconds % 3600) // 60
            seconds = duration_seconds % 60
            if hours > 0:
                duration_str = f"{hours}:{minutes:02d}:{seconds:02d}"
            else:
                duration_str = f"{minutes:02d}:{seconds:02d}"

        # ===== 视频地址 m3u8 =====
        video_url = ""
        video_tag = soup.find('video')
        if video_tag and video_tag.get('src'):
            video_url = video_tag.get('src')
            if '&amp;' in video_url:
                video_url = video_url.replace('&amp;', '&')
            if video_url.startswith('/'):
                video_url = self.base_url + video_url

        return {
            "id": video_id,
            "code": code,
            "title": title,
            "actress": actress,
            "cover": cover,
            "description": desc,
            "publish_date": publish_date,
            "duration": duration_str,   # 新增
            "video_url": video_url,
            "url": detail_url,
        }

fetcher = JableFetcher()

# ============================================================
# API 路由
# ============================================================

@router.get("/search")
async def search_jable(q: str = Query(..., min_length=1)):
    try:
        print(f"[Jable] 搜索: {q}")
        items = fetcher.search(q)
        print(f"[Jable] 找到 {len(items)} 个结果")
        return {"ok": True, "count": len(items), "items": items}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=502, detail=f"搜索失败: {str(e)}")

@router.get("/info")
async def info_jable(video_id: str = Query(...)):
    try:
        data = fetcher.detail(video_id)
        return {"ok": True, "item": data}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=502, detail=f"获取详情失败: {str(e)}")

# ============================================================
# 采集、收藏等接口（保持不变）
# ============================================================

@router.post("/collect")
async def collect_jable_item(request: Request, item: CollectItem):
    if not is_developer(request):
        return {"ok": True, "stored": False, "message": "guest mode"}
    if missav_db is None:
        raise HTTPException(status_code=500, detail="数据库未配置")

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
                UPDATE public.missav_items
                SET title=:title, actress=:actress, description=:description,
                    publish_date=:publish_date, cover_url=:cover_url,
                    m3u8_url=:m3u8_url, source_url=:source_url,
                    created_at=CURRENT_TIMESTAMP
                WHERE video_id=:video_id
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
