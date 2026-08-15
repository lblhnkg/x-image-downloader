# missav_routes.py
import httpx
from fastapi import APIRouter, Request, Response
from fastapi.responses import StreamingResponse
import re
from lxml import html

router = APIRouter()

BASE_URL = "https://missav.ai"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Referer": BASE_URL + "/",
}

# 全局 httpx 客户端（复用连接，带浏览器头）
client = httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=30)


# ---------- 1. 搜索 ----------
@router.get("/missav/search")
async def search(q: str):
    """输入番号或关键词，返回视频列表"""
    try:
        resp = await client.get(f"{BASE_URL}/search", params={"q": q})
        resp.raise_for_status()
        tree = html.fromstring(resp.text)
        items = []

        # MissAV 搜索结果卡片
        cards = tree.cssselect(".video-item") or tree.cssselect(".grid > div")
        for card in cards[:20]:
            try:
                a_tag = card.cssselect("a")[0]
                href = a_tag.get("href", "")
                video_id = href.strip("/").split("/")[-1].split("?")[0]
                if not video_id or len(video_id) < 3:
                    continue
                title_el = card.cssselect(".title, h3, h4, .text-sm")
                title = title_el[0].text_content().strip() if title_el else video_id
                img_el = card.cssselect("img")
                img = img_el[0].get("src", "") if img_el else ""
                items.append({
                    "id": video_id,
                    "title": title,
                    "cover_url": img,
                    "page_url": BASE_URL + href if href.startswith("/") else href,
                })
            except Exception:
                continue

        return {"results": items, "count": len(items)}
    except Exception as e:
        return {"error": str(e), "results": []}


# ---------- 2. 详情 + 提取 m3u8 ----------
@router.get("/missav/info")
async def get_info(video_id: str):
    """获取视频标题、封面、m3u8 直链"""
    try:
        url = f"{BASE_URL}/{video_id}"
        resp = await client.get(url)
        resp.raise_for_status()

        # 从页面 JS 里抠 m3u8 地址
        m3u8_match = re.search(r'(https?://[^"\'\s]+\.m3u8)', resp.text)
        m3u8_url = m3u8_match.group(1) if m3u8_match else ""

        # 标题
        title_match = re.search(r'<title>([^<]+)</title>', resp.text)
        title = title_match.group(1).replace(" - MissAV", "").strip() if title_match else video_id

        # 封面
        thumb_match = re.search(r'poster="([^"]+)"', resp.text)
        thumbnail = thumb_match.group(1) if thumb_match else ""

        return {
            "video_id": video_id,
            "title": title,
            "m3u8_url": m3u8_url,
            "thumbnail": thumbnail,
            "page_url": url,
        }
    except Exception as e:
        return {"error": str(e), "video_id": video_id}


# ---------- 3. 播放代理（绕过 CORS + Referer 校验）----------
@router.get("/missav/stream")
async def proxy_stream(video_id: str):
    """返回 m3u8 内容，前端 hls.js 直接播"""
    try:
        info = await get_info(video_id)
        m3u8_url = info.get("m3u8_url")
        if not m3u8_url:
            return Response("m3u8 not found", status_code=404)

        stream_headers = {
            "User-Agent": HEADERS["User-Agent"],
            "Referer": f"{BASE_URL}/{video_id}",
            "Origin": BASE_URL,
        }
        resp = await client.get(m3u8_url, headers=stream_headers)
        resp.raise_for_status()

        return Response(
            content=resp.text,
            media_type="application/vnd.apple.mpegurl",
            headers={
                "Cache-Control": "no-cache",
                "Access-Control-Allow-Origin": "*",
            },
        )
    except Exception as e:
        return Response(f"Error: {str(e)}", status_code=500)


# ---------- 4. 下载（ts 合并流式返回）----------
@router.get("/missav/download")
async def download_video(video_id: str):
    """把 HLS 流合并成 MP4 下载"""
    try:
        info = await get_info(video_id)
        m3u8_url = info.get("m3u8_url")
        if not m3u8_url:
            return {"error": "m3u8 not found"}

        stream_headers = {
            "User-Agent": HEADERS["User-Agent"],
            "Referer": f"{BASE_URL}/{video_id}",
            "Origin": BASE_URL,
        }

        # 获取 m3u8 播放列表
        resp = await client.get(m3u8_url, headers=stream_headers)
        resp.raise_for_status()

        # 解析所有 .ts 片段地址
        ts_urls = []
        for line in resp.text.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                if line.startswith("http"):
                    ts_urls.append(line)
                else:
                    base = m3u8_url.rsplit("/", 1)[0]
                    ts_urls.append(f"{base}/{line}")

        if not ts_urls:
            return {"error": "No segments found"}

        # 流式拼接返回（限制前 500 段，约 1-2 小时内容）
        async def generate():
            for ts_url in ts_urls[:500]:
                try:
                    ts_resp = await client.get(ts_url, headers=stream_headers)
                    if ts_resp.status_code == 200:
                        yield ts_resp.content
                except Exception:
                    continue

        return StreamingResponse(
            generate(),
            media_type="video/mp4",
            headers={
                "Content-Disposition": f"attachment; filename={video_id}.mp4",
            },
        )
    except Exception as e:
        return {"error": str(e)}


# ---------- 兼容你旧前端写死的路径 ----------
@router.get("/api/video-stream")
async def old_stream(url: str):
    try:
        stream_headers = {"User-Agent": HEADERS["User-Agent"], "Referer": BASE_URL + "/", "Origin": BASE_URL}
        resp = await client.get(url, headers=stream_headers)
        return Response(content=resp.text, media_type="application/vnd.apple.mpegurl", headers={"Access-Control-Allow-Origin": "*"})
    except Exception as e:
        return Response(str(e), status_code=500)


@router.get("/api/video-download")
async def old_download(url: str, filename: str = "video.mp4"):
    try:
        stream_headers = {"User-Agent": HEADERS["User-Agent"], "Referer": BASE_URL + "/", "Origin": BASE_URL}
        resp = await client.get(url, headers=stream_headers)
        ts_urls = []
        for line in resp.text.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                ts_urls.append(line if line.startswith("http") else f"{url.rsplit('/',1)[0]}/{line}")

        async def generate():
            for ts_url in ts_urls[:500]:
                try:
                    r = await client.get(ts_url, headers=stream_headers)
                    if r.status_code == 200:
                        yield r.content
                except: pass

        return StreamingResponse(generate(), media_type="video/mp4", headers={"Content-Disposition": f"attachment; filename={filename}"})
    except Exception as e:
        return {"error": str(e)}
