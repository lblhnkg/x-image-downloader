# ============================================================
# jable_routes.py - Jable / HohoJ 双数据源模块
# 包含：完整 JableFetcher、HohoJFetcher（女优名取最后一段）
#       收藏增加 code 字段、删除接口、日期修复
# ============================================================

import re
import time
import random
from datetime import datetime
from urllib.parse import quote
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel
from curl_cffi import requests
from bs4 import BeautifulSoup
from shared import missav_db

router = APIRouter(prefix="/api/jable", tags=["Jable"])

# ============================================================
# 模型（增加 code 字段）
# ============================================================

class CollectItem(BaseModel):
    video_id: str
    title: str
    code: str | None = None
    actress: str | None = None
    description: str | None = None
    publish_date: str | None = None
    cover_url: str | None = None
    m3u8_url: str | None = None
    source_url: str | None = None
    source: str | None = "jable"

# ============================================================
# 工具函数
# ============================================================

def is_developer(request: Request):
    return bool(request.cookies.get("session"))

# ============================================================
# Jable 抓取器（完整实现）
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
        self.proxies = {
            "http": "http://127.0.0.1:1081",
            "https": "http://127.0.0.1:1081"
        }
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

        title_tag = soup.find('h1')
        title = title_tag.text.strip() if title_tag else ""
        if not title:
            meta_title = soup.find('meta', property='og:title')
            if meta_title:
                title = meta_title.get('content', '')

        code = ""
        code_match = re.match(r'^([A-Z]{2,6}-\d{3,5})', title)
        if code_match:
            code = code_match.group(1)

        actress = ""
        models = soup.select('a[href*="/models/"]')
        if models:
            actress_names = []
            for m in models:
                span = m.find('span')
                name = ""
                if span:
                    name = span.get('data-original-title') or span.get('title', '')
                if not name:
                    name = m.get('title', '') or m.text.strip()
                if name:
                    name = re.sub(r'^按女優\s*', '', name).strip()
                    name = re.sub(r'[^\u4e00-\u9fff\u3040-\u30ffa-zA-Z0-9\s]', '', name)
                    if name:
                        actress_names.append(name)
            actress = ' '.join(actress_names)
            actress = re.sub(r'^按女優\s*', '', actress).strip()

        if not actress and title:
            title_without_code = re.sub(r'^[A-Z]{2,6}-\d{3,5}\s*', '', title)
            parts = title_without_code.split(' ')
            for i in range(min(3, len(parts)), 0, -1):
                candidate = ' '.join(parts[-i:])
                if re.search(r'[\u4e00-\u9fff]', candidate):
                    actress = candidate
                    break

        cover = ""
        meta_og = soup.find('meta', property='og:image')
        if meta_og:
            cover = meta_og.get('content', '')
        if cover and cover.startswith('//'):
            cover = 'https:' + cover

        desc = ""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            desc = meta_desc.get('content', '')
            if "免費高清AV在線看" in desc:
                desc = ""

        publish_date = ""
        date_pattern = re.compile(r'(\d{4}-\d{2}-\d{2})')
        date_match = date_pattern.search(html)
        if date_match:
            publish_date = date_match.group(1)

        duration_str = ""
        duration_seconds = None
        for script in soup.find_all('script'):
            if script.get('data-ts-session-duration'):
                try:
                    duration_seconds = int(script.get('data-ts-session-duration'))
                    break
                except:
                    pass
        if not duration_seconds:
            video_tag = soup.find('video')
            if video_tag and video_tag.get('duration'):
                try:
                    duration_seconds = int(float(video_tag.get('duration')))
                except:
                    pass
        if not duration_seconds:
            duration_elem = soup.select_one('.label, .duration, .time')
            if duration_elem:
                time_str = duration_elem.text.strip()
                match = re.match(r'(\d{1,2}):(\d{2})(?::(\d{2}))?', time_str)
                if match:
                    h = int(match.group(1)) if match.group(1) else 0
                    m = int(match.group(2))
                    s = int(match.group(3)) if match.group(3) else 0
                    duration_seconds = h*3600 + m*60 + s
        if duration_seconds:
            hours = duration_seconds // 3600
            minutes = (duration_seconds % 3600) // 60
            seconds = duration_seconds % 60
            if hours > 0:
                duration_str = f"{hours}:{minutes:02d}:{seconds:02d}"
            else:
                duration_str = f"{minutes:02d}:{seconds:02d}"

        video_url = ""
        for script in soup.find_all('script'):
            if script.string:
                content = script.string
                match = re.search(r"var\s+hlsUrl\s*=\s*'([^']+\.m3u8[^']*)'", content)
                if match:
                    video_url = match.group(1)
                    break
        if not video_url:
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
            "duration": duration_str,
            "video_url": video_url,
            "url": detail_url,
        }

# ============================================================
# HohoJ 抓取器（修复女优名提取）
# ============================================================

class HohoJFetcher:
    def __init__(self):
        self.base_url = "https://hohoj.tv"
        self.timeout = 30
        self.headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }
        self.proxies = {
            "http": "http://127.0.0.1:1081",
            "https": "http://127.0.0.1:1081"
        }
        self.session = requests.Session(
            impersonate="safari15_5",
            proxies=self.proxies,
            timeout=self.timeout
        )
        self.session.headers.update(self.headers)

    def _fetch(self, url: str, retry: bool = False) -> str:
        if not retry:
            delay = random.uniform(1, 3)
            print(f"[HohoJ] 等待 {delay:.1f} 秒后请求...")
            time.sleep(delay)
        else:
            delay = random.uniform(10, 20)
            print(f"[HohoJ] 重试前等待 {delay:.1f} 秒...")
            time.sleep(delay)

        print(f"[HohoJ] 请求 {url}")
        try:
            resp = self.session.get(url, proxies=self.proxies, timeout=self.timeout)
            print(f"[HohoJ] 状态码 {resp.status_code}")
            if resp.status_code != 200:
                if resp.status_code == 403 and not retry:
                    print(f"[HohoJ] 收到 403，将重试一次...")
                    return self._fetch(url, retry=True)
                raise Exception(f"HTTP {resp.status_code}")
            return resp.text
        except Exception as e:
            if not retry:
                print(f"[HohoJ] 请求异常，将重试一次...")
                return self._fetch(url, retry=True)
            print(f"[HohoJ] 请求失败: {e}")
            raise

    def search(self, keyword: str) -> list[dict]:
        search_url = f"{self.base_url}/search?text={quote(keyword)}"
        html = self._fetch(search_url)
        soup = BeautifulSoup(html, 'lxml')
        results = []
        seen = set()

        for item in soup.select('.video-item'):
            a_tag = item.find('a')
            if not a_tag:
                continue
            href = a_tag.get('href')
            if not href:
                continue
            if href.startswith('/'):
                href = self.base_url + href

            video_id = None
            if '?id=' in href:
                video_id = href.split('?id=')[-1].split('&')[0]
            if not video_id:
                continue
            if video_id in seen:
                continue
            seen.add(video_id)

            img = item.find('img')
            cover = ''
            if img:
                cover = img.get('src') or img.get('data-src') or ''
                if cover.startswith('//'):
                    cover = 'https:' + cover
                if '/small_' in cover:
                    cover = cover.replace('/small_', '/large_')

            title_div = item.select_one('.video-item-title')
            title = title_div.text.strip() if title_div else ''

            code = ''
            title_clean = re.sub(r'^\[?無碼\]?\s*', '', title)
            match = re.match(r'^([A-Z]{2,6}-\d{3,5})', title_clean)
            if match:
                code = match.group(1)

            results.append({
                "id": video_id,
                "url": href,
                "title": title,
                "cover": cover,
                "code": code,
            })

        seen_ids = set()
        unique = []
        for r in results:
            if r['id'] not in seen_ids:
                seen_ids.add(r['id'])
                unique.append(r)
        return unique

    def detail(self, video_id: str) -> dict:
        detail_url = f"{self.base_url}/video?id={video_id}"
        html = self._fetch(detail_url)
        soup = BeautifulSoup(html, 'lxml')

        # 标题
        title_tag = soup.find('h5', class_='mt-3')
        title = title_tag.text.strip() if title_tag else ''

        # 番号
        code = ''
        if title:
            title_clean = re.sub(r'^\[?無碼\]?\s*', '', title)
            match = re.match(r'^([A-Z]{2,6}-\d{3,5})', title_clean)
            if match:
                code = match.group(1)

        # 女优名：只取末尾最后一段（日文名）
        actress = ''
        if title:
            cleaned = re.sub(r'^\[?無碼\]?\s*', '', title)
            cleaned = re.sub(r'^[A-Z]{2,6}-\d{3,5}\s*', '', cleaned)
            match = re.search(r'([\u4e00-\u9fff\u3040-\u30ff]+(?:\s*[\u4e00-\u9fff\u3040-\u30ff]+)*)$', cleaned)
            if match:
                full = match.group(1).strip()
                parts = re.split(r'\s+', full)
                actress = parts[-1] if parts else full

        # 封面
        cover = ''
        img_tag = soup.find('img', src=re.compile(r'large_'))
        if img_tag:
            cover = img_tag.get('src')
            if cover.startswith('//'):
                cover = 'https:' + cover

        # 视频地址
        video_url = ''
        embed_url = f"{self.base_url}/embed?id={video_id}"
        try:
            embed_html = self._fetch(embed_url)
            match = re.search(r'var\s+videoSrc\s*=\s*"([^"]+\.m3u8)"', embed_html)
            if match:
                video_url = match.group(1)
        except Exception as e:
            print(f"[HohoJ] 获取 embed 失败: {e}")

        # 发布日期
        publish_date = None
        date_div = soup.find('div', class_='ms-auto')
        if date_div:
            span = date_div.find('span')
            if span:
                date_text = span.text.strip()
                try:
                    publish_date = datetime.strptime(date_text, '%Y-%m-%d').date()
                except:
                    pass

        return {
            "id": video_id,
            "code": code,
            "title": title,
            "actress": actress,
            "cover": cover,
            "description": "",
            "publish_date": publish_date,
            "duration": "",
            "video_url": video_url,
            "url": detail_url,
        }

# ============================================================
# 创建抓取器实例
# ============================================================

fetcher = JableFetcher()
hohoj_fetcher = HohoJFetcher()

# ============================================================
# API 路由
# ============================================================

@router.get("/search")
async def search_jable(
    q: str = Query(..., min_length=1),
    source: str = Query("jable", regex="^(jable|hohoj)$")
):
    try:
        print(f"[搜索] 来源: {source}, 关键词: {q}")
        if source == "hohoj":
            items = hohoj_fetcher.search(q)
        else:
            items = fetcher.search(q)
        return {"ok": True, "count": len(items), "items": items}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=502, detail=f"搜索失败: {str(e)}")

@router.get("/info")
async def info_jable(
    video_id: str = Query(...),
    source: str = Query("jable", regex="^(jable|hohoj)$")
):
    try:
        if source == "hohoj":
            data = hohoj_fetcher.detail(video_id)
        else:
            data = fetcher.detail(video_id)
        return {"ok": True, "item": data}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=502, detail=f"获取详情失败: {str(e)}")

@router.post("/collect")
async def collect_jable_item(request: Request, item: CollectItem):
    if not is_developer(request):
        return {"ok": True, "stored": False, "message": "guest mode"}
    if missav_db is None:
        raise HTTPException(status_code=500, detail="数据库未配置")

    try:
        # 建表（包含 code 列）
        await missav_db.execute("""
            CREATE TABLE IF NOT EXISTS public.missav_items (
                id SERIAL PRIMARY KEY,
                video_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                code TEXT,
                actress TEXT,
                description TEXT,
                publish_date DATE,
                cover_url TEXT,
                m3u8_url TEXT,
                source_url TEXT,
                source TEXT DEFAULT 'jable',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # 添加 code 列（兼容旧表）
        try:
            await missav_db.execute("ALTER TABLE public.missav_items ADD COLUMN IF NOT EXISTS code TEXT")
        except Exception:
            pass
        try:
            await missav_db.execute("ALTER TABLE public.missav_items ADD COLUMN IF NOT EXISTS source TEXT DEFAULT 'jable'")
        except Exception:
            pass

        existing = await missav_db.fetch_one(
            "SELECT id, source FROM public.missav_items WHERE video_id = :video_id",
            {"video_id": item.video_id}
        )

        params = item.dict()
        # 日期转换
        if params.get("publish_date") and params["publish_date"] is not None:
            try:
                if isinstance(params["publish_date"], str):
                    params["publish_date"] = datetime.strptime(params["publish_date"], "%Y-%m-%d").date()
            except:
                params["publish_date"] = None
        else:
            params["publish_date"] = None

        if not params.get("m3u8_url"):
            params["m3u8_url"] = None
        if not params.get("source"):
            params["source"] = "jable"

        if existing:
            old_source = existing.get("source") or "jable"
            if not params.get("source"):
                params["source"] = old_source
            await missav_db.execute("""
                UPDATE public.missav_items
                SET title=:title, code=:code, actress=:actress, description=:description,
                    publish_date=:publish_date, cover_url=:cover_url,
                    m3u8_url=:m3u8_url, source_url=:source_url,
                    source=:source,
                    created_at=CURRENT_TIMESTAMP
                WHERE video_id=:video_id
            """, params)
        else:
            await missav_db.execute("""
                INSERT INTO public.missav_items (
                    video_id, title, code, actress, description,
                    publish_date, cover_url, m3u8_url, source_url, source
                )
                VALUES (
                    :video_id, :title, :code, :actress, :description,
                    :publish_date, :cover_url, :m3u8_url, :source_url, :source
                )
            """, params)
        return {"ok": True, "stored": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/collect/{video_id}")
async def delete_collect_item(request: Request, video_id: str):
    if not is_developer(request):
        raise HTTPException(status_code=403, detail="permission denied")
    if missav_db is None:
        raise HTTPException(status_code=500, detail="数据库未配置")

    try:
        result = await missav_db.execute(
            "DELETE FROM public.missav_items WHERE video_id = :video_id",
            {"video_id": video_id}
        )
        if result == 0:
            raise HTTPException(status_code=404, detail="未找到该收藏")
        return {"ok": True, "deleted": True}
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
