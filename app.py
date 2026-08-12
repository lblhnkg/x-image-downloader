import os
import re
from urllib.parse import urlparse
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx

from xtf import Router

NITTER = os.getenv(
    "XTF_NITTER",
    "https://xcancel.com,https://nitter.poast.org,https://nitter.privacyredirect.com,https://nitter.tiekoetter.com"
)

app = FastAPI(title="X Image Finder")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

def username_from_url(value: str) -> str:
    value = value.strip()
    if not value.startswith(("http://", "https://")):
        value = "https://" + value
    p = urlparse(value)
    host = p.netloc.lower()
    if host not in {"x.com", "www.x.com", "twitter.com", "www.twitter.com"}:
        raise ValueError("请输入 x.com 或 twitter.com 的主页链接")
    parts = [x for x in p.path.split("/") if x]
    if not parts:
        raise ValueError("没有识别到用户名")
    if parts[0].lower() in {"home", "explore", "search", "i"}:
        raise ValueError("请输入博主主页链接，例如 https://x.com/username")
    return re.sub(r"[^A-Za-z0-9_]", "", parts[0])

def media_from_tweet(tw):
    if hasattr(tw, "to_dict"):
        tw = tw.to_dict()
    if not isinstance(tw, dict):
        return []
    media = tw.get("media") or tw.get("attachments") or []
    if isinstance(media, dict):
        # Common normalized shapes.
        candidates = media.get("photos") or media.get("all") or media.get("images") or []
    else:
        candidates = media
    out = []
    if isinstance(candidates, dict):
        candidates = [candidates]
    for m in candidates or []:
        if not isinstance(m, dict):
            continue
        typ = str(m.get("type", "image")).lower()
        if typ not in {"image", "photo", "photos"}:
            continue
        url = m.get("url") or m.get("media_url") or m.get("media_url_https")
        thumb = m.get("thumbnail_url") or url
        if url:
            out.append({
                "url": url,
                "thumb": thumb,
                "width": m.get("width") or (m.get("size") or {}).get("width"),
                "height": m.get("height") or (m.get("size") or {}).get("height"),
            })
    # Fallback for normalized media_urls / mediaURLs.
    if not out:
        urls = tw.get("media_urls") or tw.get("mediaURLs") or []
        for u in urls:
            if isinstance(u, str) and re.search(r"\.(?:jpg|jpeg|png|webp)(?:\?|$)", u, re.I):
                out.append({"url": u, "thumb": u, "width": None, "height": None})
    return out

@app.get("/")
def index():
    return FileResponse("static/index.html")

@app.get("/api/health")
def health():
    return {"ok": True, "nitter": NITTER.split(",")}

@app.get("/api/timeline")
def timeline(
    profile: str = Query(..., description="X profile URL or @username"),
    limit: int = Query(200, ge=5, le=200),
):
    try:
        username = username_from_url(profile) if ("/" in profile or profile.startswith("http")) else profile.lstrip("@")
        username = re.sub(r"[^A-Za-z0-9_]", "", username)
        if not username:
            raise ValueError("用户名为空")
        os.environ["XTF_NITTER"] = NITTER
        router = Router(backend="nitter")
        tweets = router.fetch_timeline(username, limit=limit)
    except Exception as e:
        raise HTTPException(502, f"读取 X 时间线失败：{e}")

    result = []
    for tw in tweets:
        d = tw.to_dict() if hasattr(tw, "to_dict") else tw
        photos = media_from_tweet(d)
        if not photos:
            continue
        tweet_id = d.get("tweet_id") or d.get("id") or ""
        tweet_url = d.get("url") or (f"https://x.com/{username}/status/{tweet_id}" if tweet_id else f"https://x.com/{username}")
        created = d.get("created_at") or d.get("time_ago") or ""
        for idx, photo in enumerate(photos):
            result.append({
                "id": f"{tweet_id}-{idx}",
                "tweet_id": tweet_id,
                "tweet_url": tweet_url,
                "created_at": created,
                "text": d.get("text") or d.get("full_text") or "",
                "image": photo["url"],
                "thumb": photo["thumb"],
                "width": photo["width"],
                "height": photo["height"],
            })
    return {"username": username, "count": len(result), "items": result}

@app.get("/api/download")
async def download(url: str = Query(...)):
    # Only proxy X media hosts to reduce abuse risk.
    p = urlparse(url)
    if p.scheme != "https" or p.netloc.lower() not in {"pbs.twimg.com", "video.twimg.com"}:
        raise HTTPException(400, "只允许下载 X 的媒体地址")
    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=30,
        headers={"User-Agent": "Mozilla/5.0 X-Image-Finder/1.0"}
    ) as client:
        r = await client.get(url)
    if r.status_code >= 400:
        raise HTTPException(r.status_code, "X 原图读取失败，请打开原帖下载")
    media_type = r.headers.get("content-type", "image/jpeg")
    suffix = ".jpg"
    if "png" in media_type: suffix = ".png"
    elif "webp" in media_type: suffix = ".webp"
    filename = "x-original" + suffix
    return StreamingResponse(
        iter([r.content]),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
