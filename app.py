# ============================================================
# X Media Proxy
# 用于网页端显示 Likes / Bookmarks 中的 X 图片和视频
# ============================================================

from urllib.parse import urlparse
from fastapi import Query, HTTPException
from fastapi.responses import Response
import httpx


MEDIA_PROXY_ALLOWED_HOSTS = {
    "pbs.twimg.com",
    "pbs.twimg.com.",
    "video.twimg.com",
    "video.twimg.com.",
}


def _validate_x_media_url(url: str) -> str:

    if not url:
        raise HTTPException(
            status_code=400,
            detail="媒体地址不能为空"
        )

    try:
        parsed = urlparse(url)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="媒体地址格式错误"
        )

    if parsed.scheme.lower() != "https":
        raise HTTPException(
            status_code=400,
            detail="媒体地址必须使用 HTTPS"
        )

    hostname = (
        parsed.hostname or ""
    ).lower()

    if hostname not in MEDIA_PROXY_ALLOWED_HOSTS:
        raise HTTPException(
            status_code=403,
            detail="不允许代理此媒体地址"
        )

    return url


@app.get("/api/media-proxy")
async def media_proxy(
    url: str = Query(...)
):

    target_url = _validate_x_media_url(
        url
    )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(iPhone; CPU iPhone OS 18_0 like Mac OS X) "
            "AppleWebKit/605.1.15 "
            "(KHTML, like Gecko) "
            "Version/18.0 Mobile/15E148 "
            "Safari/604.1"
        ),

        "Referer": "https://x.com/",

        "Accept": (
            "image/avif,image/webp,image/apng,"
            "image/svg+xml,image/*,*/*;q=0.8"
        ),
    }

    try:

        async with httpx.AsyncClient(
            timeout=60.0,
            follow_redirects=True,
            headers=headers,
        ) as client:

            response = await client.get(
                target_url
            )

    except httpx.TimeoutException:

        raise HTTPException(
            status_code=504,
            detail="X 媒体服务器请求超时"
        )

    except httpx.RequestError as e:

        raise HTTPException(
            status_code=502,
            detail=(
                "无法连接 X 媒体服务器："
                + str(e)
            )
        )

    except Exception as e:

        raise HTTPException(
            status_code=502,
            detail=(
                "媒体代理发生错误："
                + str(e)
            )
        )

    if response.status_code >= 400:

        raise HTTPException(
            status_code=response.status_code,
            detail=(
                "X 媒体服务器返回 HTTP "
                + str(response.status_code)
            )
        )

    content_type = (
        response.headers.get(
            "content-type"
        )
        or "application/octet-stream"
    )

    # 防止把错误页面当成图片返回
    if (
        not content_type.startswith("image/")
        and
        not content_type.startswith("video/")
        and
        content_type != "application/octet-stream"
    ):

        raise HTTPException(
            status_code=502,
            detail=(
                "X 返回的不是有效媒体文件："
                + content_type
            )
        )

    output_headers = {
        "Cache-Control":
            "public, max-age=3600",

        "Access-Control-Allow-Origin":
            "*",

        "Content-Disposition":
            "inline",
    }

    content_length = response.headers.get(
        "content-length"
    )

    if content_length:
        output_headers[
            "Content-Length"
        ] = content_length

    return Response(
        content=response.content,
        media_type=content_type,
        headers=output_headers,
    )

import re
import os
import json
import asyncio
import subprocess
import tempfile
import uuid

from datetime import datetime, timezone
from urllib.parse import urlparse, unquote

import httpx

from fastapi import (
    FastAPI,
    HTTPException,
    Query,
    Body,
)

from fastapi.responses import (
    FileResponse,
    StreamingResponse,
)

from fastapi.middleware.cors import CORSMiddleware

from starlette.background import BackgroundTask


# =========================================================
# X Media Finder V3.2
# =========================================================

app = FastAPI(
    title="X Media Finder"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


FX_API = "https://api.fxtwitter.com"


# =========================================================
# 媒体库
# =========================================================

MEDIA_LIBRARY_FILE = "media_library.json"


def load_media_library():

    if not os.path.exists(
        MEDIA_LIBRARY_FILE
    ):
        return {}

    try:

        with open(
            MEDIA_LIBRARY_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        if isinstance(
            data,
            dict
        ):

            return data

    except Exception as e:

        print(
            "[MEDIA] load error:",
            e
        )

    return {}


def save_media_library(
    library
):

    temp_file = (
        MEDIA_LIBRARY_FILE +
        ".tmp"
    )

    try:

        with open(
            temp_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                library,
                f,
                ensure_ascii=False,
                indent=2
            )

        os.replace(
            temp_file,
            MEDIA_LIBRARY_FILE
        )

        return True

    except Exception as e:

        print(
            "[MEDIA] save error:",
            e
        )

        try:

            if os.path.exists(
                temp_file
            ):
                os.remove(
                    temp_file
                )

        except Exception:
            pass

        return False


media_library = load_media_library()


# =========================================================
# 基础工具
# =========================================================

def get_username(
    profile: str
) -> str:

    profile = profile.strip()

    if not profile:

        raise ValueError(
            "请输入 X 博主主页链接"
        )

    if not profile.startswith(
        (
            "http://",
            "https://"
        )
    ):

        profile = (
            "https://" +
            profile
        )

    parsed = urlparse(
        profile
    )

    host = parsed.netloc.lower()

    if host not in {
        "x.com",
        "www.x.com",
        "twitter.com",
        "www.twitter.com",
    }:

        raise ValueError(
            "请输入类似 https://x.com/username 的 X 主页链接"
        )

    parts = [
        x
        for x in parsed.path.split("/")
        if x
    ]

    if not parts:

        raise ValueError(
            "无法识别 X 用户名"
        )

    username = parts[0]

    if username.lower() in {
        "home",
        "explore",
        "search",
        "i",
        "notifications",
        "messages",
        "settings",
    }:

        raise ValueError(
            "这不是有效的 X 博主主页"
        )

    username = re.sub(
        r"[^A-Za-z0-9_]",
        "",
        username
    )

    if not username:

        raise ValueError(
            "用户名无效"
        )

    return username


def parse_x_date(
    value
):

    if not value:
        return None

    try:

        return datetime.strptime(
            value,
            "%a %b %d %H:%M:%S %z %Y"
        ).astimezone(
            timezone.utc
        )

    except Exception:

        return None


def date_from_string(
    value,
    end_of_day=False
):

    if not value:
        return None

    try:

        dt = datetime.strptime(
            value,
            "%Y-%m-%d"
        ).replace(
            tzinfo=timezone.utc
        )

        if end_of_day:

            dt = dt.replace(
                hour=23,
                minute=59,
                second=59,
                microsecond=999999
            )

        return dt

    except Exception:

        raise ValueError(
            f"日期格式错误：{value}"
        )


# =========================================================
# 获取 X 数据
# =========================================================

async def fetch_media_page(
    username,
    cursor=None,
    count=100
):

    params = {
        "count": min(
            count,
            100
        )
    }

    if cursor:

        params["cursor"] = cursor

    url = (
        f"{FX_API}/2/profile/"
        f"{username}/media"
    )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(iPhone; CPU iPhone OS 18_0 like Mac OS X) "
            "AppleWebKit/605.1.15 "
            "Version/18.0 Mobile/15E148 "
            "Safari/604.1"
        )
    }

    try:

        async with httpx.AsyncClient(
            timeout=30,
            follow_redirects=True,
            headers=headers,
        ) as client:

            response = await client.get(
                url,
                params=params
            )

    except Exception as e:

        raise HTTPException(
            status_code=502,
            detail=(
                "无法连接图片数据源："
                + str(e)
            )
        )

    if response.status_code != 200:

        raise HTTPException(
            status_code=502,
            detail=(
                "图片数据源返回 HTTP "
                + str(response.status_code)
            )
        )

    try:

        data = response.json()

    except Exception:

        raise HTTPException(
            status_code=502,
            detail="图片数据源返回的不是有效 JSON"
        )

    if data.get("code") != 200:

        raise HTTPException(
            status_code=502,
            detail=(
                "图片数据源返回错误："
                + str(data)
            )
        )

    return (
        data.get(
            "results",
            []
        ),
        data.get(
            "cursor",
            {}
        )
    )


# =========================================================
# 判断帖子来源
# =========================================================

def get_post_source(
    tweet
):

    if tweet.get(
        "reposted_by"
    ):

        return "repost"

    quote_fields = [
        "quote",
        "quoted_tweet",
        "quote_status",
        "quoted_status",
    ]

    for field in quote_fields:

        if tweet.get(
            field
        ):

            return "quote"

    return "original"


# =========================================================
# 提取照片
# =========================================================

def extract_photos(
    tweet
):

    media = (
        tweet.get(
            "media"
        )
        or {}
    )

    photos = (
        media.get(
            "photos"
        )
        or []
    )

    result = []

    total = len(
        photos
    )

    for index, photo in enumerate(
        photos
    ):

        if not isinstance(
            photo,
            dict
        ):

            continue

        url = photo.get(
            "url"
        )

        if not url:
            continue

        result.append({

            "id": str(
                photo.get(
                    "id"
                )
                or
                f"{tweet.get('id')}-{index}"
            ),

            "url": url,

            "width":
                photo.get(
                    "width"
                ),

            "height":
                photo.get(
                    "height"
                ),

            "alt":
                photo.get(
                    "altText"
                )
                or "",

            "index":
                index + 1,

            "total":
                total,

        })

    return result


# =========================================================
# 提取视频
# =========================================================

def extract_videos(
    tweet
):

    media = (
        tweet.get(
            "media"
        )
        or {}
    )

    videos = (
        media.get(
            "videos"
        )
        or []
    )

    result = []

    for index, video in enumerate(
        videos
    ):

        if not isinstance(
            video,
            dict
        ):

            continue

        video_url = video.get(
            "url"
        )

        formats = (
            video.get(
                "formats"
            )
            or []
        )

        mp4_formats = []

        for fmt in formats:

            if not isinstance(
                fmt,
                dict
            ):

                continue

            fmt_url = fmt.get(
                "url"
            )

            container = (
                fmt.get(
                    "container"
                )
                or ""
            ).lower()

            if (
                fmt_url
                and
                container == "mp4"
            ):

                mp4_formats.append(
                    fmt
                )

        if mp4_formats:

            best = max(
                mp4_formats,
                key=lambda x:
                    x.get(
                        "bitrate"
                    )
                    or 0
            )

            video_url = best.get(
                "url"
            )

        if not video_url:
            continue

        thumbnail = (
            video.get(
                "thumbnail_url"
            )
            or ""
        )

        result.append({

            "id": str(
                video.get(
                    "id"
                )
                or
                (
                    f"{tweet.get('id')}"
                    f"-video-{index}"
                )
            ),

            "url":
                video_url,

            "thumbnail":
                thumbnail,

            "width":
                video.get(
                    "width"
                ),

            "height":
                video.get(
                    "height"
                ),

            "duration":
                video.get(
                    "duration"
                ),

            "index":
                index + 1,

            "total":
                len(videos),

        })

    return result


# =========================================================
# 搜索接口
# =========================================================

@app.get(
    "/api/search"
)
async def search(

    profile: str = Query(...),

    start_date: str | None = None,

    end_date: str | None = None,

    media_type: str = Query(
        "photo"
    ),

    source_type: str = Query(
        "all"
    ),

    max_pages: int = Query(
        100,
        ge=1,
        le=100
    ),

):

    try:

        username = get_username(
            profile
        )

        start_dt = date_from_string(
            start_date
        )

        end_dt = date_from_string(
            end_date,
            end_of_day=True
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    if (
        start_dt
        and end_dt
        and start_dt > end_dt
    ):

        raise HTTPException(
            status_code=400,
            detail="开始日期不能晚于结束日期"
        )

    if media_type not in {
        "photo",
        "video",
        "all"
    }:

        raise HTTPException(
            status_code=400,
            detail="媒体类型无效"
        )

    if source_type not in {
        "all",
        "original",
        "repost"
    }:

        raise HTTPException(
            status_code=400,
            detail="帖子来源类型无效"
        )

    items = []

    cursor = None

    pages = 0

    seen_cursors = set()

    while pages < max_pages:

        pages += 1

        tweets, cursor_data = (
            await fetch_media_page(
                username,
                cursor=cursor,
                count=100
            )
        )

        if not tweets:
            break

        reached_start = False

        for tweet in tweets:

            created_at_text = (
                tweet.get(
                    "created_at"
                )
                or ""
            )

            created_at = parse_x_date(
                created_at_text
            )

            if not created_at:
                continue

            if (
                start_dt
                and
                created_at < start_dt
            ):

                reached_start = True

                continue

            if (
                end_dt
                and
                created_at > end_dt
            ):

                continue

            post_source = (
                get_post_source(
                    tweet
                )
            )

            if (
                source_type == "original"
                and
                post_source != "original"
            ):

                continue

            if (
                source_type == "repost"
                and
                post_source == "original"
            ):

                continue

            tweet_url = (
                tweet.get(
                    "url"
                )
                or
                (
                    f"https://x.com/"
                    f"{username}/status/"
                    f"{tweet.get('id')}"
                )
            )

            base = {

                "tweet_id": str(
                    tweet.get(
                        "id"
                    )
                    or ""
                ),

                "tweet_url":
                    tweet_url,

                "created_at":
                    created_at_text,

                "timestamp":
                    int(
                        created_at.timestamp()
                    ),

                "text":
                    tweet.get(
                        "text"
                    )
                    or "",

                "source":
                    post_source,

            }

            if media_type in {
                "photo",
                "all"
            }:

                photos = extract_photos(
                    tweet
                )

                for photo in photos:

                    items.append({

                        **base,

                        "media_type":
                            "photo",

                        "media_id":
                            photo["id"],

                        "media_url":
                            photo["url"],

                        "image":
                            photo["url"],

                        "thumbnail":
                            photo["url"],

                        "width":
                            photo["width"],

                        "height":
                            photo["height"],

                        "alt":
                            photo["alt"],

                        "media_index":
                            photo["index"],

                        "media_total":
                            photo["total"],

                    })

            if media_type in {
                "video",
                "all"
            }:

                videos = extract_videos(
                    tweet
                )

                for video in videos:

                    items.append({

                        **base,

                        "media_type":
                            "video",

                        "media_id":
                            video["id"],

                        "media_url":
                            video["url"],

                        "image":
                            video["thumbnail"],

                        "thumbnail":
                            video["thumbnail"],

                        "video_url":
                            video["url"],

                        "width":
                            video["width"],

                        "height":
                            video["height"],

                        "duration":
                            video["duration"],

                        "media_index":
                            video["index"],

                        "media_total":
                            video["total"],

                    })

        if (
            start_dt
            and
            reached_start
        ):

            break

        next_cursor = None

        if isinstance(
            cursor_data,
            dict
        ):

            next_cursor = (
                cursor_data.get(
                    "bottom"
                )
            )

        if not next_cursor:
            break

        if (
            next_cursor
            in seen_cursors
        ):

            break

        seen_cursors.add(
            next_cursor
        )

        cursor = next_cursor

    items.sort(
        key=lambda x:
            x["timestamp"],
        reverse=True
    )

    return {

        "ok": True,

        "username":
            username,

        "count":
            len(items),

        "pages":
            pages,

        "items":
            items,

    }


# =========================================================
# 媒体库工具
# =========================================================

def make_media_id(
    item
):

    media_url = (
        item.get(
            "url"
        )
        or
        item.get(
            "media_url"
        )
        or ""
    )

    if media_url:

        return (
            "url:"
            +
            media_url
        )

    tweet_id = str(
        item.get(
            "tweet_id"
        )
        or
        ""
    )

    media_type = (
        item.get(
            "type"
        )
        or
        item.get(
            "media_type"
        )
        or
        "unknown"
    )

    return (
        "tweet:"
        +
        tweet_id
        +
        ":"
        +
        media_type
    )


def normalize_import_item(
    item
):

    if not isinstance(
        item,
        dict
    ):

        return None

    tweet_id = str(
        item.get(
            "tweetId"
        )
        or
        item.get(
            "tweet_id"
        )
        or
        item.get(
            "id"
        )
        or
        ""
    )

    tweet_url = (
        item.get(
            "tweetUrl"
        )
        or
        item.get(
            "tweet_url"
        )
        or
        item.get(
            "url"
        )
        or ""
    )

    author = (
        item.get(
            "author"
        )
        or ""
    )

    source = (
        item.get(
            "source"
        )
        or "likes"
    )

    if source not in {
        "likes",
        "bookmarks"
    }:

        source = "likes"

    raw_media = (
        item.get(
            "media"
        )
        or []
    )

    if not isinstance(
        raw_media,
        list
    ):

        raw_media = []

    result = []

    for media in raw_media:

        if not isinstance(
            media,
            dict
        ):

            continue

        media_type = (
            media.get(
                "type"
            )
            or ""
        )

        if media_type not in {
            "image",
            "video"
        }:

            continue

        media_url = (
            media.get(
                "url"
            )
            or ""
        )

        thumbnail = (
            media.get(
                "thumbnail"
            )
            or ""
        )

        original_url = (
            media.get(
                "originalUrl"
            )
            or
            media.get(
                "original_url"
            )
            or
            media_url
        )

        result.append({

            "type":
                media_type,

            "url":
                media_url,

            "originalUrl":
                original_url,

            "thumbnail":
                thumbnail,

            "streamType":
                media.get(
                    "streamType"
                )
                or "",

            "width":
                media.get(
                    "width"
                )
                or 0,

            "height":
                media.get(
                    "height"
                )
                or 0,

            "bitrate":
                media.get(
                    "bitrate"
                )
                or 0,

        })

    if not result:

        return None

    return {

        "tweet_id":
            tweet_id,

        "tweet_url":
            tweet_url,

        "author":
            author,

        "source":
            source,

        "media":
            result,

    }


# =========================================================
# 导入媒体
# =========================================================

@app.post(
    "/api/import-media"
)
async def import_media(
    payload: dict = Body(...)
):

    if not isinstance(
        payload,
        dict
    ):

        raise HTTPException(
            status_code=400,
            detail="上传数据格式错误"
        )

    items = (
        payload.get(
            "items"
        )
        or
        payload.get(
            "records"
        )
        or []
    )

    if not isinstance(
        items,
        list
    ):

        raise HTTPException(
            status_code=400,
            detail="items 必须是数组"
        )

    imported = 0

    added = 0

    updated = 0

    duplicates = 0

    for raw_item in items:

        item = normalize_import_item(
            raw_item
        )

        if not item:
            continue

        for media in item["media"]:

            record = {

                "id":
                    "",

                "tweet_id":
                    item["tweet_id"],

                "tweet_url":
                    item["tweet_url"],

                "author":
                    item["author"],

                "source":
                    item["source"],

                "type":
                    media["type"],

                "url":
                    media["url"],

                "originalUrl":
                    media["originalUrl"],

                "thumbnail":
                    media["thumbnail"],

                "streamType":
                    media["streamType"],

                "width":
                    media["width"],

                "height":
                    media["height"],

                "bitrate":
                    media["bitrate"],

                "downloaded":
                    False,

                "createdAt":
                    datetime.now(
                        timezone.utc
                    ).isoformat(),

            }

            media_id = make_media_id(
                record
            )

            record["id"] = media_id

            imported += 1

            old = media_library.get(
                media_id
            )

            if old:

                duplicates += 1

                changed = False

                for key in [
                    "tweet_id",
                    "tweet_url",
                    "author",
                    "source",
                    "thumbnail",
                    "originalUrl",
                    "streamType",
                    "width",
                    "height",
                    "bitrate",
                ]:

                    if (
                        record.get(key)
                        and
                        not old.get(key)
                    ):

                        old[key] = record[key]

                        changed = True

                if changed:

                    updated += 1

                continue

            media_library[
                media_id
            ] = record

            added += 1

    if not save_media_library(
        media_library
    ):

        raise HTTPException(
            status_code=500,
            detail="媒体库保存失败"
        )

    return {

        "ok": True,

        "imported":
            imported,

        "added":
            added,

        "updated":
            updated,

        "duplicates":
            duplicates,

        "total":
            len(media_library),

    }


# =========================================================
# 媒体库
# =========================================================

@app.get(
    "/api/media"
)
async def get_media(

    source: str = Query(
        "all"
    ),

    media_type: str = Query(
        "all"
    ),

    downloaded: str = Query(
        "all"
    ),

):

    items = list(
        media_library.values()
    )

    if source in {
        "likes",
        "bookmarks"
    }:

        items = [
            item
            for item in items
            if item.get(
                "source"
            ) == source
        ]

    if media_type in {
        "image",
        "video"
    }:

        items = [
            item
            for item in items
            if item.get(
                "type"
            ) == media_type
        ]

    if downloaded == "yes":

        items = [
            item
            for item in items
            if item.get(
                "downloaded"
            ) is True
        ]

    elif downloaded == "no":

        items = [
            item
            for item in items
            if item.get(
                "downloaded"
            ) is not True
        ]

    items.sort(
        key=lambda x:
            x.get(
                "createdAt",
                ""
            ),
        reverse=True
    )

    return {

        "ok": True,

        "count":
            len(items),

        "items":
            items,

    }


# =========================================================
# 标记下载状态
# =========================================================

@app.post(
    "/api/media/{media_id}/downloaded"
)
async def mark_downloaded(

    media_id: str,

    payload: dict = Body(
        default={}
    )

):

    if media_id not in media_library:

        raise HTTPException(
            status_code=404,
            detail="媒体不存在"
        )

    downloaded = True

    if isinstance(
        payload,
        dict
    ):

        if (
            "downloaded"
            in payload
        ):

            downloaded = bool(
                payload[
                    "downloaded"
                ]
            )

    media_library[
        media_id
    ][
        "downloaded"
    ] = downloaded

    media_library[
        media_id
    ][
        "downloadedAt"
    ] = (
        datetime.now(
            timezone.utc
        ).isoformat()
        if downloaded
        else None
    )

    if not save_media_library(
        media_library
    ):

        raise HTTPException(
            status_code=500,
            detail="媒体库保存失败"
        )

    return {

        "ok": True,

        "id":
            media_id,

        "downloaded":
            downloaded,

    }


# =========================================================
# 清空媒体库
# =========================================================

@app.delete(
    "/api/media"
)
async def clear_media():

    media_library.clear()

    if not save_media_library(
        media_library
    ):

        raise HTTPException(
            status_code=500,
            detail="媒体库保存失败"
        )

    return {

        "ok": True,

        "count": 0

    }


# =========================================================
# 下载文件
# =========================================================

def safe_filename(
    value
):

    value = unquote(
        str(
            value
            or ""
        )
    )

    value = re.sub(
        r'[\\/:*?"<>|]+',
        "_",
        value
    )

    return value[:150]


@app.get(
    "/api/download"
)
async def download(

    url: str = Query(...),

    filename: str = Query(
        "x-media"
    ),

):

    parsed = urlparse(
        url
    )

    allowed_hosts = {

        "pbs.twimg.com",
        "pbs.twimg.com.",

        "video.twimg.com",
        "video.twimg.com.",

    }

    if (
        parsed.scheme != "https"
        or
        parsed.netloc.lower()
        not in allowed_hosts
    ):

        raise HTTPException(
            status_code=400,
            detail="不是有效的 X 媒体地址"
        )

    headers = {

        "User-Agent": (
            "Mozilla/5.0 "
            "(iPhone; CPU iPhone OS 18_0 like Mac OS X) "
            "AppleWebKit/605.1.15 "
            "Version/18.0 Mobile/15E148 "
            "Safari/604.1"
        )

    }

    try:

        async with httpx.AsyncClient(
            timeout=90,
            follow_redirects=True,
            headers=headers,
        ) as client:

            response = await client.get(
                url
            )

    except Exception as e:

        raise HTTPException(
            status_code=502,
            detail=(
                "下载失败："
                +
                str(e)
            )
        )

    if response.status_code >= 400:

        raise HTTPException(
            status_code=response.status_code,
            detail=(
                "X 媒体服务器拒绝下载，"
                "请尝试打开原帖。"
            )
        )

    content_type = (
        response.headers.get(
            "content-type",
            ""
        ).lower()
    )

    if "mp4" in content_type:

        extension = ".mp4"

    elif "webm" in content_type:

        extension = ".webm"

    elif "png" in content_type:

        extension = ".png"

    elif "webp" in content_type:

        extension = ".webp"

    else:

        extension = ".jpg"

    filename = safe_filename(
        filename
    )

    if not filename:

        filename = "x-media"

    if not filename.lower().endswith(
        extension
    ):

        filename += extension

    return StreamingResponse(

        iter([
            response.content
        ]),

        media_type=(
            content_type
            or
            "application/octet-stream"
        ),

        headers={

            "Content-Disposition":
                (
                    f'attachment; '
                    f'filename="{filename}"'
                )

        },

    )


# =========================================================
# HLS / M3U8
# =========================================================

HLS_ALLOWED_HOSTS = {

    "video.twimg.com",
    "video.twimg.com.",

}


def validate_hls_url(
    url: str
):

    try:

        parsed = urlparse(
            url
        )

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="视频地址格式错误"
        )

    if parsed.scheme != "https":

        raise HTTPException(
            status_code=400,
            detail="视频地址必须使用 HTTPS"
        )

    hostname = (
        parsed.hostname
        or ""
    ).lower()

    if hostname not in HLS_ALLOWED_HOSTS:

        raise HTTPException(
            status_code=400,
            detail="不是有效的 X 视频地址"
        )

    return url


def cleanup_video_directory(
    directory
):

    try:

        if not os.path.isdir(
            directory
        ):

            return

        for filename in os.listdir(
            directory
        ):

            path = os.path.join(
                directory,
                filename
            )

            try:

                if os.path.isfile(
                    path
                ):

                    os.remove(
                        path
                    )

            except Exception:
                pass

        try:

            os.rmdir(
                directory
            )

        except Exception:
            pass

    except Exception:
        pass


@app.get(
    "/api/video-download"
)
async def video_download(

    url: str = Query(...),

    filename: str = Query(
        "x-video.mp4"
    ),

):

    validate_hls_url(
        url
    )

    filename = safe_filename(
        filename
    )

    if not filename:

        filename = "x-video.mp4"

    if not filename.lower().endswith(
        ".mp4"
    ):

        filename += ".mp4"

    temp_dir = tempfile.mkdtemp(
        prefix="x-video-"
    )

    output_path = os.path.join(
        temp_dir,
        f"{uuid.uuid4()}.mp4"
    )

    user_agent = (
        "Mozilla/5.0 "
        "(iPhone; CPU iPhone OS 18_0 like Mac OS X) "
        "AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) "
        "Version/18.0 Mobile/15E148 "
        "Safari/604.1"
    )

    headers = (
        "User-Agent: "
        +
        user_agent
        +
        "\r\n"
        +
        "Referer: https://x.com/\r\n"
    )

    command = [

        "ffmpeg",

        "-hide_banner",

        "-loglevel",
        "error",

        "-headers",
        headers,

        "-protocol_whitelist",
        "file,http,https,tcp,tls,crypto",

        "-allowed_extensions",
        "ALL",

        "-i",
        url,

        "-map",
        "0:v:0?",

        "-map",
        "0:a:0?",

        "-c",
        "copy",

        "-movflags",
        "+faststart",

        "-y",
        output_path,

    ]

    try:

        process = await asyncio.to_thread(

            subprocess.run,

            command,

            stdout=subprocess.PIPE,

            stderr=subprocess.PIPE,

            timeout=180,

        )

    except subprocess.TimeoutExpired:

        cleanup_video_directory(
            temp_dir
        )

        raise HTTPException(
            status_code=504,
            detail="视频转换超时"
        )

    except Exception as e:

        cleanup_video_directory(
            temp_dir
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "FFmpeg 启动失败："
                +
                str(e)
            )
        )

    if process.returncode != 0:

        error_message = (
            process.stderr
            .decode(
                "utf-8",
                errors="ignore"
            )
            .strip()
        )

        cleanup_video_directory(
            temp_dir
        )

        raise HTTPException(

            status_code=500,

            detail=(
                "FFmpeg 转换失败："
                +
                (
                    error_message[-3000:]
                    if error_message
                    else "未知错误"
                )
            )

        )

    if not os.path.exists(
        output_path
    ):

        cleanup_video_directory(
            temp_dir
        )

        raise HTTPException(
            status_code=500,
            detail="FFmpeg 没有生成 MP4"
        )

    file_size = os.path.getsize(
        output_path
    )

    if file_size < 1024:

        cleanup_video_directory(
            temp_dir
        )

        raise HTTPException(
            status_code=500,
            detail="生成的 MP4 文件异常"
        )

    return FileResponse(

        path=output_path,

        media_type="video/mp4",

        filename=filename,

        background=BackgroundTask(

            cleanup_video_directory,

            temp_dir

        ),

    )


# =========================================================
# 首页
# =========================================================

@app.get("/")
async def index():

    return FileResponse(
        "static/index.html"
    )


# =========================================================
# 健康检查
# =========================================================

@app.get(
    "/api/health"
)
async def health():

    return {

        "ok": True,

        "service":
            "X Media Finder V3",

        "media_library":
            True,

        "media_count":
            len(
                media_library
            ),

    }
