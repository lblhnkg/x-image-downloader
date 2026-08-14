# ============================================================
# 完整 app.py - 万能媒体下载器（X + MissAV 合并版）
# ============================================================

import re
import os
import json
import asyncio
import subprocess
import tempfile
import uuid
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs, quote

import httpx
from databases import Database

from fastapi import FastAPI, APIRouter, HTTPException, Query, Body, Request, Response
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.background import BackgroundTask

# ============================================================
# 配置
# ============================================================

DATABASE_URL = os.environ.get("DATABASE_URL", "")
APP_PASSWORD = os.environ.get("APP_PASSWORD", "fushengruomeng")
DB_PATH = "media.db"

if not DATABASE_URL:
    print("⚠️ 警告：DATABASE_URL 未设置，使用本地 SQLite（重启会丢数据）")
    DATABASE_URL = "sqlite:///media.db"

database = Database(DATABASE_URL)

# ============================================================
# 数据库初始化
# ============================================================

async def init_db():
    is_postgres = DATABASE_URL.startswith("postgresql")

    if is_postgres:
        await database.execute("""
            CREATE TABLE IF NOT EXISTS media (
                id TEXT PRIMARY KEY,
                data TEXT NOT NULL
            )
        """)
        await database.execute("CREATE INDEX IF NOT EXISTS idx_source ON media(data)")
    else:
        await database.execute("""
            CREATE TABLE IF NOT EXISTS media (
                id TEXT PRIMARY KEY,
                data TEXT NOT NULL
            )
        """)
        await database.execute("CREATE INDEX IF NOT EXISTS idx_source ON media(data)")

    if is_postgres:
        await database.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                username TEXT PRIMARY KEY,
                name TEXT,
                addedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    else:
        await database.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                username TEXT PRIMARY KEY,
                name TEXT,
                addedAt DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

# ============================================================
# 媒体库操作
# ============================================================

async def load_all_media():
    rows = await database.fetch_all("SELECT id, data FROM media")
    library = {}
    for row in rows:
        try:
            if hasattr(row, "_mapping"):
                library[row._mapping["id"]] = json.loads(row._mapping["data"])
            else:
                library[row[0]] = json.loads(row[1])
        except:
            pass
    return library

async def save_media_item(media_id, data):
    try:
        serialized = json.dumps(data, ensure_ascii=False)
    except Exception as e:
        print(f"[DB ERROR] 序列化失败 {media_id}: {e}")
        return False, f"序列化失败: {e}"

    is_postgres = DATABASE_URL.startswith("postgresql")

    for attempt in range(3):
        try:
            if is_postgres:
                await database.execute(
                    """
                    INSERT INTO media (id, data)
                    VALUES (:id, :data)
                    ON CONFLICT (id) DO UPDATE
                    SET data = EXCLUDED.data
                    """,
                    {"id": media_id, "data": serialized}
                )
            else:
                await database.execute(
                    "REPLACE INTO media (id, data) VALUES (:id, :data)",
                    {"id": media_id, "data": serialized}
                )
            return True, None
        except Exception as e:
            print(f"[DB ERROR] 写入失败 (尝试 {attempt+1}/3) {media_id}: {e}")
            if attempt == 2:
                return False, str(e)
            await asyncio.sleep(0.5)
    return False, "未知错误"

async def delete_media_items(media_ids):
    if not media_ids:
        return 0
    deleted = 0
    batch_size = 100
    for i in range(0, len(media_ids), batch_size):
        batch = media_ids[i:i+batch_size]
        if DATABASE_URL.startswith("postgresql"):
            placeholders = ','.join([f'${j+1}' for j in range(len(batch))])
            query = f"DELETE FROM media WHERE id IN ({placeholders})"
            result = await database.execute(query, batch)
        else:
            placeholders = ','.join(['?'] * len(batch))
            query = f"DELETE FROM media WHERE id IN ({placeholders})"
            result = await database.execute(query, batch)
        deleted += result
    return deleted

async def clear_all_media():
    await database.execute("DELETE FROM media")

# ============================================================
# 收藏操作
# ============================================================

async def load_all_favorites():
    rows = await database.fetch_all("SELECT username, name, addedAt FROM favorites ORDER BY addedAt DESC")
    favorites = []
    for row in rows:
        if hasattr(row, "_mapping"):
            favorites.append({
                "username": row._mapping["username"],
                "name": row._mapping["name"],
                "addedAt": row._mapping["addedAt"]
            })
        else:
            favorites.append({
                "username": row[0],
                "name": row[1],
                "addedAt": row[2]
            })
    return favorites

async def save_favorite(username, name):
    is_postgres = DATABASE_URL.startswith("postgresql")
    if is_postgres:
        await database.execute(
            """
            INSERT INTO favorites (username, name, addedAt)
            VALUES (:username, :name, CURRENT_TIMESTAMP)
            ON CONFLICT (username) DO UPDATE
            SET name = EXCLUDED.name, addedAt = CURRENT_TIMESTAMP
            """,
            {"username": username, "name": name}
        )
    else:
        await database.execute(
            "REPLACE INTO favorites (username, name, addedAt) VALUES (:username, :name, CURRENT_TIMESTAMP)",
            {"username": username, "name": name}
        )

async def delete_favorite(username):
    await database.execute("DELETE FROM favorites WHERE username = :username", {"username": username})

async def is_favorite(username):
    row = await database.fetch_one("SELECT 1 FROM favorites WHERE username = :username", {"username": username})
    return row is not None

media_library = {}

# ============================================================
# X 工具函数
# ============================================================

def get_username(profile: str):
    profile = (profile or "").strip()
    if not profile:
        raise ValueError("请输入 X 博主主页链接")
    if not profile.startswith(("http://", "https://")):
        if profile.startswith("@"):
            return profile[1:]
        return re.sub(r"[^A-Za-z0-9_]", "", profile)
    try:
        parsed = urlparse(profile)
    except Exception:
        raise ValueError("主页地址格式错误")
    host = parsed.netloc.lower()
    if host not in {"x.com", "www.x.com", "twitter.com", "www.twitter.com"}:
        raise ValueError("请输入类似 https://x.com/username 的 X 主页链接")
    parts = [x for x in parsed.path.split("/") if x]
    if not parts:
        raise ValueError("无法识别 X 用户名")
    username = re.sub(r"[^A-Za-z0-9_]", "", parts[0])
    if not username:
        raise ValueError("用户名无效")
    return username

def parse_x_date(value):
    if not value:
        return None
    formats = ["%a %b %d %H:%M:%S %z %Y", "%a %b %d %H:%M:%S %Y"]
    for fmt in formats:
        try:
            dt = datetime.strptime(value, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            pass
    return None

def date_from_string(value, end_of_day=False):
    if not value:
        return None
    try:
        dt = datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        if end_of_day:
            dt = dt.replace(hour=23, minute=59, second=59, microsecond=999999)
        return dt
    except Exception:
        raise ValueError(f"日期格式错误：{value}")

def safe_filename(value):
    value = str(value or "")
    value = re.sub(r'[\\/:*?"<>|]+', "_", value)
    return value[:150]

# ============================================================
# URL 处理（X）
# ============================================================

def normalize_x_media_url(url):
    if not url:
        return ""
    url = str(url).strip()
    if not url:
        return ""
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if host not in {"pbs.twimg.com", "pbs.twimg.com."}:
        return url
    query = parse_qs(parsed.query)
    if query:
        return url
    path = (parsed.path or "").lower()
    if "/media/" in path:
        return url + "?format=jpg&name=orig"
    return url

def make_proxy_url(media_url):
    if not media_url:
        return ""
    media_url = normalize_x_media_url(media_url)
    return "/api/media-proxy?url=" + quote(media_url, safe="")

def resolve_proxy_url(url):
    if not url:
        return url
    parsed = urlparse(url)
    if parsed.path != "/api/media-proxy":
        return url
    query = parse_qs(parsed.query, keep_blank_values=True)
    values = query.get("url")
    if not values:
        return url
    real_url = values[0]
    real_url = normalize_x_media_url(real_url)
    return real_url

def validate_media_url(url):
    try:
        parsed = urlparse(url)
    except Exception:
        raise HTTPException(status_code=400, detail="媒体地址格式错误")
    if parsed.scheme != "https":
        raise HTTPException(status_code=400, detail="媒体地址必须使用 HTTPS")
    hostname = (parsed.hostname or "").lower()
    if hostname not in {"pbs.twimg.com", "pbs.twimg.com.", "video.twimg.com", "video.twimg.com."}:
        raise HTTPException(status_code=400, detail="不是有效的 X 媒体地址")
    return url

def validate_hls_url(url):
    try:
        parsed = urlparse(url)
    except Exception:
        raise HTTPException(status_code=400, detail="视频地址格式错误")
    if parsed.scheme != "https":
        raise HTTPException(status_code=400, detail="视频地址必须使用 HTTPS")
    hostname = (parsed.hostname or "").lower()
    # 允许 X 和 MissAV 的域名
    allowed_hosts = {"video.twimg.com", "video.twimg.com.", "missav.com", "missav.ws", "cdn.missav.com"}
    if hostname not in allowed_hosts:
        # 放行（自用）
        pass
    return url

# ============================================================
# X 数据抓取
# ============================================================

async def fetch_media_page(username, cursor=None, count=100):
    params = {"count": min(count, 100)}
    if cursor:
        params["cursor"] = cursor
    url = f"https://api.fxtwitter.com/2/profile/{username}/media"
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1", "Accept": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True, headers=headers) as client:
            response = await client.get(url, params=params)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"无法连接图片数据源：{str(e)}")
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail=f"图片数据源返回 HTTP {response.status_code}")
    try:
        data = response.json()
    except Exception:
        raise HTTPException(status_code=502, detail="图片数据源返回的不是有效 JSON")
    if data.get("code") != 200:
        raise HTTPException(status_code=502, detail=f"图片数据源返回错误：{data}")
    return data.get("results", []), data.get("cursor", {})

def get_post_source(tweet):
    if tweet.get("reposted_by"):
        return "repost"
    for field in ["quote", "quoted_tweet", "quote_status", "quoted_status"]:
        if tweet.get(field):
            return "quote"
    return "original"

def extract_photos(tweet):
    media = tweet.get("media") or {}
    photos = media.get("photos") or []
    result = []
    total = len(photos)
    for index, photo in enumerate(photos):
        if not isinstance(photo, dict):
            continue
        url = photo.get("url")
        if not url:
            continue
        url = normalize_x_media_url(url)
        result.append({
            "id": str(photo.get("id") or f"{tweet.get('id')}-{index}"),
            "url": url,
            "width": photo.get("width"),
            "height": photo.get("height"),
            "alt": photo.get("altText") or "",
            "index": index + 1,
            "total": total,
        })
    return result

def extract_videos(tweet):
    media = tweet.get("media") or {}
    videos = media.get("videos") or []
    result = []
    for index, video in enumerate(videos):
        if not isinstance(video, dict):
            continue
        video_url = video.get("url")
        formats = video.get("formats") or []
        mp4_formats = []
        for fmt in formats:
            if not isinstance(fmt, dict):
                continue
            fmt_url = fmt.get("url")
            container = (fmt.get("container") or "").lower()
            if fmt_url and container == "mp4":
                mp4_formats.append(fmt)
        if mp4_formats:
            best = max(mp4_formats, key=lambda x: x.get("bitrate") or 0)
            video_url = best.get("url")
        if not video_url:
            continue
        thumbnail = video.get("thumbnail_url") or ""
        if thumbnail:
            thumbnail = normalize_x_media_url(thumbnail)
        result.append({
            "id": str(video.get("id") or f"{tweet.get('id')}-video-{index}"),
            "url": video_url,
            "thumbnail": thumbnail,
            "width": video.get("width"),
            "height": video.get("height"),
            "duration": video.get("duration"),
            "index": index + 1,
            "total": len(videos),
        })
    return result

# ============================================================
# X API 路由（使用 APIRouter）
# ============================================================

x_router = APIRouter()

@x_router.post("/api/auth/login")
async def login(response: Response, payload: dict = Body(...)):
    password = payload.get("password", "")
    if password == APP_PASSWORD:
        response.set_cookie(
            key="session",
            value=APP_PASSWORD,
            httponly=False,
            secure=True,
            samesite="none",
            max_age=3600*24*7
        )
        return {"ok": True, "message": "登录成功"}
    raise HTTPException(status_code=401, detail="密码错误")

@x_router.get("/api/auth/check")
async def check_auth(request: Request):
    session = request.cookies.get("session")
    if session == APP_PASSWORD:
        return {"ok": True, "authenticated": True}
    return {"ok": True, "authenticated": False}

@x_router.get("/api/search")
async def search(
    profile: str = Query(...),
    start_date: str | None = None,
    end_date: str | None = None,
    media_type: str = Query("photo"),
    source_type: str = Query("all"),
    max_pages: int = Query(100, ge=1, le=100),
):
    try:
        username = get_username(profile)
        start_dt = date_from_string(start_date)
        end_dt = date_from_string(end_date, end_of_day=True)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if start_dt and end_dt and start_dt > end_dt:
        raise HTTPException(status_code=400, detail="开始日期不能晚于结束日期")

    if media_type not in {"photo", "video", "all"}:
        raise HTTPException(status_code=400, detail="媒体类型无效")
    if source_type not in {"all", "original", "repost"}:
        raise HTTPException(status_code=400, detail="帖子来源类型无效")

    items = []
    cursor = None
    pages = 0
    seen_cursors = set()

    while pages < max_pages:
        pages += 1
        tweets, cursor_data = await fetch_media_page(username, cursor=cursor, count=100)
        if not tweets:
            break
        reached_start = False
        for tweet in tweets:
            created_at_text = tweet.get("created_at") or ""
            created_at = parse_x_date(created_at_text)
            if not created_at:
                continue
            if start_dt and created_at < start_dt:
                reached_start = True
                continue
            if end_dt and created_at > end_dt:
                continue

            post_source = get_post_source(tweet)
            if source_type == "original" and post_source != "original":
                continue
            if source_type == "repost" and post_source == "original":
                continue

            tweet_url = tweet.get("url") or f"https://x.com/{username}/status/{tweet.get('id')}"
            base = {
                "tweet_id": str(tweet.get("id") or ""),
                "tweet_url": tweet_url,
                "created_at": created_at_text,
                "timestamp": int(created_at.timestamp()),
                "text": tweet.get("text") or "",
                "source": post_source,
            }

            if media_type in {"photo", "all"}:
                photos = extract_photos(tweet)
                for photo in photos:
                    items.append({
                        **base,
                        "media_type": "photo",
                        "media_id": photo["id"],
                        "media_url": photo["url"],
                        "image": photo["url"],
                        "thumbnail": photo["url"],
                        "width": photo["width"],
                        "height": photo["height"],
                        "alt": photo["alt"],
                        "media_index": photo["index"],
                        "media_total": photo["total"],
                    })

            if media_type in {"video", "all"}:
                videos = extract_videos(tweet)
                for video in videos:
                    items.append({
                        **base,
                        "media_type": "video",
                        "media_id": video["id"],
                        "media_url": video["url"],
                        "image": video["thumbnail"],
                        "thumbnail": video["thumbnail"],
                        "video_url": video["url"],
                        "width": video["width"],
                        "height": video["height"],
                        "duration": video["duration"],
                        "media_index": video["index"],
                        "media_total": video["total"],
                    })

        if start_dt and reached_start:
            break

        next_cursor = None
        if isinstance(cursor_data, dict):
            next_cursor = cursor_data.get("bottom")
        if not next_cursor or next_cursor in seen_cursors:
            break
        seen_cursors.add(next_cursor)
        cursor = next_cursor

    items.sort(key=lambda x: x["timestamp"], reverse=True)
    return {"ok": True, "username": username, "count": len(items), "pages": pages, "items": items}

def make_media_id(tweet_id, media_type, idx):
    return f"tweet_{tweet_id}_{media_type}_{idx}"

def normalize_import_item(item):
    if not isinstance(item, dict):
        return None
    tweet_id = str(item.get("tweetId") or item.get("tweet_id") or item.get("id") or "")
    tweet_url = item.get("tweetUrl") or item.get("tweet_url") or ""
    author = item.get("author") or ""
    source = item.get("source") or "likes"
    tweet_created_at = item.get("tweetCreatedAt") or ""
    if source not in {"likes", "bookmarks"}:
        source = "likes"

    raw_media = item.get("media") or []
    if not isinstance(raw_media, list):
        raw_media = []

    result = []
    for idx, media in enumerate(raw_media):
        if not isinstance(media, dict):
            continue
        media_type = media.get("type") or ""
        if media_type not in {"image", "video"}:
            continue
        media_url = media.get("url") or ""
        original_url = media.get("originalUrl") or media.get("original_url") or media_url
        thumbnail = media.get("thumbnail") or ""

        if media_type == "image":
            media_url = normalize_x_media_url(media_url)
            original_url = normalize_x_media_url(original_url)
            if thumbnail:
                thumbnail = normalize_x_media_url(thumbnail)
            else:
                thumbnail = media_url

        result.append({
            "type": media_type,
            "url": media_url,
            "originalUrl": original_url,
            "thumbnail": thumbnail,
            "streamType": media.get("streamType") or "",
            "width": int(media.get("width")) if media.get("width") else 0,
            "height": int(media.get("height")) if media.get("height") else 0,
            "bitrate": int(media.get("bitrate")) if media.get("bitrate") else 0,
            "index": idx,
            "tweetCreatedAt": tweet_created_at
        })

    if not result:
        return None
    return {
        "tweet_id": tweet_id,
        "tweet_url": tweet_url,
        "author": author,
        "source": source,
        "tweet_created_at": tweet_created_at,
        "media": result
    }

@x_router.post("/api/import-media")
async def import_media(request: Request, payload: dict = Body(...)):
    global media_library

    api_key = request.headers.get("X-API-Key")
    if api_key != APP_PASSWORD:
        print(f"[AUTH] 无效的 API Key: {api_key}")
        raise HTTPException(status_code=401, detail="无效的 API Key")

    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="上传数据格式错误")
    items = payload.get("items") or payload.get("records") or []
    if not isinstance(items, list):
        raise HTTPException(status_code=400, detail="items 必须是数组")

    imported = 0
    added = 0
    updated = 0
    duplicates = 0
    failed = 0
    failed_ids = []

    if not media_library:
        media_library = await load_all_media()

    for raw_item in items:
        item = normalize_import_item(raw_item)
        if not item:
            continue
        for media in item["media"]:
            media_id = make_media_id(item["tweet_id"], media["type"], media["index"])

            tweet_created_at = media.get("tweetCreatedAt") or item.get("tweet_created_at") or ""

            record = {
                "id": media_id,
                "tweet_id": item["tweet_id"],
                "tweet_url": item["tweet_url"],
                "author": item["author"],
                "source": item["source"],
                "type": media["type"],
                "url": media["url"],
                "originalUrl": media["originalUrl"],
                "thumbnail": media["thumbnail"],
                "streamType": media["streamType"],
                "width": int(media["width"]) if media["width"] else 0,
                "height": int(media["height"]) if media["height"] else 0,
                "bitrate": int(media["bitrate"]) if media["bitrate"] else 0,
                "downloaded": False,
                "createdAt": datetime.now(timezone.utc).isoformat(),
                "tweetCreatedAt": tweet_created_at,
            }
            imported += 1

            old_item = media_library.get(media_id)
            if old_item:
                duplicates += 1
                changed = False
                for key in ["tweet_id", "tweet_url", "author", "source", "url", "thumbnail", "originalUrl", "streamType", "width", "height", "bitrate", "tweetCreatedAt"]:
                    new_value = record.get(key)
                    if new_value and old_item.get(key) != new_value:
                        old_item[key] = new_value
                        changed = True
                if changed:
                    updated += 1
                    media_library[media_id] = old_item
                    success, err = await save_media_item(media_id, old_item)
                    if not success:
                        failed += 1
                        failed_ids.append(media_id)
                        print(f"[IMPORT] 保存失败 (更新) {media_id}: {err}")
                continue

            media_library[media_id] = record
            success, err = await save_media_item(media_id, record)
            if success:
                added += 1
            else:
                failed += 1
                failed_ids.append(media_id)
                del media_library[media_id]
                print(f"[IMPORT] 保存失败 (新增) {media_id}: {err}")

    print(f"[IMPORT] 完成: 导入 {imported}, 新增 {added}, 更新 {updated}, 重复 {duplicates}, 失败 {failed}")
    return {
        "ok": True,
        "imported": imported,
        "added": added,
        "updated": updated,
        "duplicates": duplicates,
        "failed": failed,
        "failed_ids": failed_ids,
        "total": len(media_library)
    }

@x_router.get("/api/media")
async def get_media(
    request: Request,
    source: str = Query("all"),
    media_type: str = Query("all"),
    downloaded: str = Query("all"),
    start_date: str | None = None,
    end_date: str | None = None,
):
    global media_library

    session = request.cookies.get("session")
    if session != APP_PASSWORD:
        raise HTTPException(status_code=401, detail="未登录")

    if not media_library:
        media_library = await load_all_media()

    items = list(media_library.values())

    if source in {"likes", "bookmarks"}:
        items = [item for item in items if item.get("source") == source]

    if media_type in {"image", "video"}:
        items = [item for item in items if item.get("type") == media_type]

    if downloaded == "yes":
        items = [item for item in items if item.get("downloaded") is True]
    elif downloaded == "no":
        items = [item for item in items if item.get("downloaded") is not True]

    if start_date or end_date:
        def parse_date(d):
            try:
                return datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except:
                return None
        start_dt = parse_date(start_date) if start_date else None
        end_dt = parse_date(end_date) if end_date else None
        filtered = []
        for item in items:
            time_str = item.get("tweetCreatedAt") or item.get("createdAt") or ""
            if time_str:
                dt = None
                try:
                    dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                except:
                    dt = parse_x_date(time_str)
                if dt:
                    if start_dt and dt < start_dt:
                        continue
                    if end_dt and dt > end_dt:
                        continue
                else:
                    filtered.append(item)
                    continue
            filtered.append(item)
        items = filtered

    items.sort(key=lambda x: x.get("tweetCreatedAt") or x.get("createdAt") or "", reverse=True)

    output = []
    for original_item in items:
        item = dict(original_item)
        original_media_url = item.get("originalUrl") or item.get("url") or ""
        original_thumbnail = item.get("thumbnail") or ""

        if item.get("type") == "image":
            original_media_url = normalize_x_media_url(original_media_url)
            if original_thumbnail:
                original_thumbnail = normalize_x_media_url(original_thumbnail)
            else:
                original_thumbnail = original_media_url

        item["originalUrl"] = original_media_url
        item["sourceUrl"] = original_media_url

        if original_media_url:
            item["url"] = make_proxy_url(original_media_url)

        if original_thumbnail:
            item["thumbnail"] = make_proxy_url(original_thumbnail)

        output.append(item)

    return {"ok": True, "count": len(output), "items": output}

@x_router.delete("/api/media")
async def delete_media(request: Request, media_ids: list[str] = Body(...)):
    global media_library

    session = request.cookies.get("session")
    if session != APP_PASSWORD:
        raise HTTPException(status_code=401, detail="未登录")

    if not media_ids or not isinstance(media_ids, list):
        raise HTTPException(status_code=400, detail="media_ids 必须是字符串数组")

    for media_id in media_ids:
        if media_id in media_library:
            del media_library[media_id]

    deleted_count = await delete_media_items(media_ids)

    return {
        "ok": True,
        "deleted": deleted_count,
        "requested": len(media_ids)
    }

@x_router.delete("/api/media/all")
async def clear_media(request: Request):
    global media_library

    session = request.cookies.get("session")
    if session != APP_PASSWORD:
        raise HTTPException(status_code=401, detail="未登录")

    media_library = {}
    await clear_all_media()
    return {"ok": True, "count": 0}

@x_router.get("/api/favorites")
async def get_favorites(request: Request):
    api_key = request.headers.get("X-API-Key")
    if api_key != APP_PASSWORD:
        raise HTTPException(status_code=401, detail="无效的 API Key")
    favorites = await load_all_favorites()
    return {"ok": True, "items": favorites}

@x_router.post("/api/favorites")
async def add_favorite(request: Request, payload: dict = Body(...)):
    api_key = request.headers.get("X-API-Key")
    if api_key != APP_PASSWORD:
        raise HTTPException(status_code=401, detail="无效的 API Key")

    username = payload.get("username")
    if not username:
        raise HTTPException(status_code=400, detail="username 不能为空")
    username = re.sub(r"[^A-Za-z0-9_]", "", username)
    if not username:
        raise HTTPException(status_code=400, detail="用户名无效")
    name = payload.get("name") or username

    await save_favorite(username, name)
    return {"ok": True, "username": username, "name": name}

@x_router.delete("/api/favorites/{username}")
async def remove_favorite(request: Request, username: str):
    api_key = request.headers.get("X-API-Key")
    if api_key != APP_PASSWORD:
        raise HTTPException(status_code=401, detail="无效的 API Key")

    username = re.sub(r"[^A-Za-z0-9_]", "", username)
    if not username:
        raise HTTPException(status_code=400, detail="用户名无效")

    await delete_favorite(username)
    return {"ok": True, "username": username}

@x_router.get("/api/favorites/check/{username}")
async def check_favorite(request: Request, username: str):
    api_key = request.headers.get("X-API-Key")
    if api_key != APP_PASSWORD:
        raise HTTPException(status_code=401, detail="无效的 API Key")

    username = re.sub(r"[^A-Za-z0-9_]", "", username)
    if not username:
        raise HTTPException(status_code=400, detail="用户名无效")

    exists = await is_favorite(username)
    return {"ok": True, "username": username, "favorited": exists}

@x_router.get("/api/media-proxy")
async def media_proxy(request: Request, url: str = Query(...)):
    url = resolve_proxy_url(url)
    url = normalize_x_media_url(url)
    validate_media_url(url)

    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1",
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://x.com/",
        "Origin": "https://x.com",
        "Connection": "keep-alive",
    }

    range_header = request.headers.get("range")
    if range_header:
        headers["Range"] = range_header

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=15.0), follow_redirects=True, headers=headers) as client:
            response = await client.get(url)
            content_type = response.headers.get("content-type", "").split(";")[0].strip().lower()
            if not content_type or content_type == "application/octet-stream":
                path = urlparse(url).path.lower()
                if path.endswith(".png"):
                    content_type = "image/png"
                elif path.endswith(".webp"):
                    content_type = "image/webp"
                elif path.endswith(".gif"):
                    content_type = "image/gif"
                elif ".mp4" in path or "video" in content_type:
                    content_type = "video/mp4"
                else:
                    content_type = "image/jpeg"

            if content_type and "video" in content_type:
                return Response(
                    content=response.content,
                    media_type=content_type,
                    headers={
                        "Cache-Control": "public, max-age=86400",
                        "Access-Control-Allow-Origin": "https://x-v1.onrender.com",
                        "Cross-Origin-Resource-Policy": "cross-origin",
                        "Accept-Ranges": "bytes",
                        "Content-Length": str(len(response.content)),
                    }
                )
            else:
                return Response(
                    content=response.content,
                    media_type=content_type,
                    headers={
                        "Cache-Control": "public, max-age=86400",
                        "Access-Control-Allow-Origin": "https://x-v1.onrender.com",
                        "Cross-Origin-Resource-Policy": "cross-origin",
                    }
                )
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"X 服务器返回错误：{e.response.status_code}")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"媒体代理获取失败：{str(e)}")

@x_router.post("/api/media/{media_id}/downloaded")
async def mark_downloaded(request: Request, media_id: str, payload: dict = Body(default={})):
    global media_library

    session = request.cookies.get("session")
    if session != APP_PASSWORD:
        raise HTTPException(status_code=401, detail="未登录")

    if not media_library:
        media_library = await load_all_media()

    if media_id not in media_library:
        raise HTTPException(status_code=404, detail="媒体不存在")
    downloaded = True
    if isinstance(payload, dict) and "downloaded" in payload:
        downloaded = bool(payload["downloaded"])
    media_library[media_id]["downloaded"] = downloaded
    media_library[media_id]["downloadedAt"] = datetime.now(timezone.utc).isoformat() if downloaded else None
    success, err = await save_media_item(media_id, media_library[media_id])
    if not success:
        raise HTTPException(status_code=500, detail=f"数据库保存失败: {err}")
    return {"ok": True, "id": media_id, "downloaded": downloaded}

@x_router.get("/api/download")
async def download(url: str = Query(...), filename: str = Query("x-media")):
    url = resolve_proxy_url(url)
    url = normalize_x_media_url(url)
    validate_media_url(url)

    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1",
        "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://x.com/",
        "Origin": "https://x.com",
        "Connection": "keep-alive",
    }

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=20.0), follow_redirects=True, headers=headers) as client:
            response = await client.get(url)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"下载失败：{str(e)}")

    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail="X 媒体服务器拒绝下载，请尝试打开原帖。")

    content_type = response.headers.get("content-type", "").split(";")[0].strip().lower()
    if "mp4" in content_type:
        extension = ".mp4"
    elif "webm" in content_type:
        extension = ".webm"
    elif "png" in content_type:
        extension = ".png"
    elif "webp" in content_type:
        extension = ".webp"
    elif "gif" in content_type:
        extension = ".gif"
    else:
        extension = ".jpg"

    filename = safe_filename(filename)
    if not filename:
        filename = "x-media"
    if not filename.lower().endswith(extension):
        filename += extension

    return StreamingResponse(
        iter([response.content]),
        media_type=content_type or "application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename=\"{filename}\""}
    )

# ============================================================
# 视频工具（X 和 MissAV 共用）
# ============================================================

def cleanup_video_directory(directory):
    try:
        if not os.path.isdir(directory):
            return
        for filename in os.listdir(directory):
            path = os.path.join(directory, filename)
            try:
                if os.path.isfile(path):
                    os.remove(path)
            except Exception:
                pass
        try:
            os.rmdir(directory)
        except Exception:
            pass
    except Exception:
        pass

@x_router.get("/api/video-download")
async def video_download(url: str = Query(...), filename: str = Query("x-video.mp4")):
    url = resolve_proxy_url(url)
    validate_hls_url(url)

    filename = safe_filename(filename)
    if not filename or not filename.lower().endswith(".mp4"):
        filename = "x-video.mp4"

    temp_dir = tempfile.mkdtemp(prefix="x-video-")
    output_path = os.path.join(temp_dir, f"{uuid.uuid4()}.mp4")

    headers_str = "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1\r\nReferer: https://x.com/\r\nOrigin: https://x.com/\r\n"

    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-headers", headers_str,
        "-protocol_whitelist", "file,http,https,tcp,tls,crypto",
        "-allowed_extensions", "ALL",
        "-i", url,
        "-map", "0:v:0?", "-map", "0:a:0?",
        "-c", "copy",
        "-movflags", "+faststart",
        "-y", output_path,
    ]

    try:
        process = await asyncio.to_thread(subprocess.run, command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180)
    except subprocess.TimeoutExpired:
        cleanup_video_directory(temp_dir)
        raise HTTPException(status_code=504, detail="视频转换超时")
    except Exception as e:
        cleanup_video_directory(temp_dir)
        raise HTTPException(status_code=500, detail=f"FFmpeg 启动失败：{str(e)}")

    if process.returncode != 0:
        error_message = process.stderr.decode("utf-8", errors="ignore").strip()
        cleanup_video_directory(temp_dir)
        raise HTTPException(status_code=500, detail=f"FFmpeg 转换失败：{error_message[-3000:] if error_message else '未知错误'}")

    if not os.path.exists(output_path) or os.path.getsize(output_path) < 1024:
        cleanup_video_directory(temp_dir)
        raise HTTPException(status_code=500, detail="生成的 MP4 文件异常")

    return FileResponse(
        path=output_path,
        media_type="video/mp4",
        filename=filename,
        background=BackgroundTask(cleanup_video_directory, temp_dir)
    )

@x_router.get("/api/video-stream")
async def video_stream(url: str = Query(...)):
    url = resolve_proxy_url(url)
    validate_hls_url(url)

    temp_dir = tempfile.mkdtemp(prefix="x-video-")
    output_path = os.path.join(temp_dir, f"{uuid.uuid4()}.mp4")

    headers_str = "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1\r\nReferer: https://x.com/\r\nOrigin: https://x.com/\r\n"

    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-headers", headers_str,
        "-protocol_whitelist", "file,http,https,tcp,tls,crypto",
        "-allowed_extensions", "ALL",
        "-i", url,
        "-map", "0:v:0?", "-map", "0:a:0?",
        "-c", "copy",
        "-movflags", "+faststart",
        "-y", output_path,
    ]

    try:
        process = await asyncio.to_thread(subprocess.run, command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180)
    except subprocess.TimeoutExpired:
        cleanup_video_directory(temp_dir)
        raise HTTPException(status_code=504, detail="视频转换超时")
    except Exception as e:
        cleanup_video_directory(temp_dir)
        raise HTTPException(status_code=500, detail=f"FFmpeg 启动失败：{str(e)}")

    if process.returncode != 0:
        error_message = process.stderr.decode("utf-8", errors="ignore").strip()
        cleanup_video_directory(temp_dir)
        raise HTTPException(status_code=500, detail=f"FFmpeg 转换失败：{error_message[-3000:] if error_message else '未知错误'}")

    if not os.path.exists(output_path) or os.path.getsize(output_path) < 1024:
        cleanup_video_directory(temp_dir)
        raise HTTPException(status_code=500, detail="生成的 MP4 文件异常")

    return FileResponse(
        path=output_path,
        media_type="video/mp4",
        filename=os.path.basename(output_path),
        headers={"Content-Disposition": "inline"},
        background=BackgroundTask(cleanup_video_directory, temp_dir)
    )

# ============================================================
# MissAV 抓取器
# ============================================================

import cloudscraper
from bs4 import BeautifulSoup

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

# ============================================================
# MissAV 路由
# ============================================================

missav_router = APIRouter(prefix="/missav", tags=["MissAV"])

@missav_router.get("/search")
async def missav_search(q: str = Query(..., min_length=1)):
    try:
        items = fetcher.search(q)
        return {"ok": True, "count": len(items), "items": items}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

@missav_router.get("/info")
async def missav_info(video_id: str = Query(...)):
    try:
        data = fetcher.get_detail(video_id)
        return {"ok": True, "item": data}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

# ============================================================
# 创建主应用
# ============================================================

app = FastAPI(title="万能媒体下载器（X + MissAV）")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await database.connect()
    await init_db()
    print("[DB] 数据库连接成功")
    print(f"[DB] 数据库类型: {'PostgreSQL' if DATABASE_URL.startswith('postgresql') else 'SQLite'}")

@app.on_event("shutdown")
async def shutdown_event():
    await database.disconnect()
    print("[DB] 数据库已断开")

# 注册路由
app.include_router(x_router)
app.include_router(missav_router)

# 静态页面
@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.get("/missav")
async def missav_page():
    return FileResponse("static/missav.html")

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
