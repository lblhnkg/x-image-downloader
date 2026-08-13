import re
import os
import asyncio
import subprocess
import tempfile
import uuid
import json
from datetime import datetime, timezone
from urllib.parse import urlparse, unquote

import httpx
from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.background import BackgroundTask

app = FastAPI(title="X Media Finder")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])
FX_API = "https://api.fxtwitter.com"
MEDIA_DB_FILE = os.path.join(os.path.dirname(__file__), "media_library.json")

# =========================
# 基础工具
# =========================
def get_username(profile: str) -> str:
    profile = profile.strip()
    if not profile:
        raise ValueError("请输入 X 博主主页链接")
    if not profile.startswith(("http://", "https://")):
        profile = "https://" + profile
    parsed = urlparse(profile)
    if parsed.netloc.lower() not in {"x.com", "www.x.com", "twitter.com", "www.twitter.com"}:
        raise ValueError("请输入类似 https://x.com/username 的 X 主页链接")
    parts = [x for x in parsed.path.split("/") if x]
    if not parts:
        raise ValueError("无法识别 X 用户名")
    username = parts[0]
    if username.lower() in {"home", "explore", "search", "i", "notifications", "messages", "settings"}:
        raise ValueError("这不是有效的 X 博主主页")
    username = re.sub(r"[^A-Za-z0-9_]", "", username)
    if not username:
        raise ValueError("用户名无效")
    return username

def parse_x_date(value):
    if not value: return None
    try: return datetime.strptime(value, "%a %b %d %H:%M:%S %z %Y").astimezone(timezone.utc)
    except Exception: return None

def date_from_string(value, end_of_day=False):
    if not value: return None
    try:
        dt = datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        if end_of_day: dt = dt.replace(hour=23, minute=59, second=59, microsecond=999999)
        return dt
    except Exception: raise ValueError(f"日期格式错误：{value}")

# =========================
# 搜索数据源
# =========================
async def fetch_media_page(username, cursor=None, count=100):
    params = {"count": min(count, 100)}
    if cursor: params["cursor"] = cursor
    url = f"{FX_API}/2/profile/{username}/media"
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1"}
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True, headers=headers) as client:
            response = await client.get(url, params=params)
    except Exception as e:
        raise HTTPException(502, f"无法连接图片数据源：{e}")
    if response.status_code != 200: raise HTTPException(502, f"图片数据源返回 HTTP {response.status_code}")
    try: data = response.json()
    except Exception: raise HTTPException(502, "图片数据源返回的不是有效 JSON")
    if data.get("code") != 200: raise HTTPException(502, "图片数据源返回错误：" + str(data))
    return data.get("results", []), data.get("cursor", {})

def get_post_source(tweet):
    if tweet.get("reposted_by"): return "repost"
    for field in ["quote", "quoted_tweet", "quote_status", "quoted_status"]:
        if tweet.get(field): return "quote"
    return "original"

def extract_photos(tweet):
    photos = (tweet.get("media") or {}).get("photos") or []
    result=[]
    for i,p in enumerate(photos):
        if not isinstance(p,dict) or not p.get("url"): continue
        result.append({"id":str(p.get("id") or f"{tweet.get('id')}-{i}"),"url":p["url"],"width":p.get("width"),"height":p.get("height"),"alt":p.get("altText") or "","index":i+1,"total":len(photos)})
    return result

def extract_videos(tweet):
    videos=(tweet.get("media") or {}).get("videos") or []
    result=[]
    for i,v in enumerate(videos):
        if not isinstance(v,dict): continue
        video_url=v.get("url")
        formats=v.get("formats") or []
        mp4=[f for f in formats if isinstance(f,dict) and f.get("url") and (f.get("container") or "").lower()=="mp4"]
        if mp4: video_url=max(mp4,key=lambda x:x.get("bitrate") or 0).get("url")
        if not video_url: continue
        result.append({"id":str(v.get("id") or f"{tweet.get('id')}-video-{i}"),"url":video_url,"thumbnail":v.get("thumbnail_url") or "","width":v.get("width"),"height":v.get("height"),"duration":v.get("duration"),"index":i+1,"total":len(videos)})
    return result

@app.get("/api/search")
async def search(profile: str=Query(...), start_date: str|None=None, end_date: str|None=None, media_type: str=Query("photo"), source_type: str=Query("all"), max_pages: int=Query(100,ge=1,le=100)):
    try:
        username=get_username(profile); start_dt=date_from_string(start_date); end_dt=date_from_string(end_date,True)
    except ValueError as e: raise HTTPException(400,str(e))
    if start_dt and end_dt and start_dt>end_dt: raise HTTPException(400,"开始日期不能晚于结束日期")
    if media_type not in {"photo","video","all"}: raise HTTPException(400,"媒体类型无效")
    if source_type not in {"all","original","repost"}: raise HTTPException(400,"帖子来源类型无效")
    items=[]; cursor=None; pages=0; seen=set()
    while pages<max_pages:
        pages+=1; tweets,cursor_data=await fetch_media_page(username,cursor,100)
        if not tweets: break
        reached=False
        for tweet in tweets:
            created_text=tweet.get("created_at") or ""; created=parse_x_date(created_text)
            if not created: continue
            if start_dt and created<start_dt: reached=True; continue
            if end_dt and created>end_dt: continue
            source=get_post_source(tweet)
            if source_type=="original" and source!="original": continue
            if source_type=="repost" and source=="original": continue
            base={"tweet_id":str(tweet.get("id") or ""),"tweet_url":tweet.get("url") or f"https://x.com/{username}/status/{tweet.get('id')}","created_at":created_text,"timestamp":int(created.timestamp()),"text":tweet.get("text") or "","source":source}
            if media_type in {"photo","all"}:
                for p in extract_photos(tweet):
                    items.append({**base,"media_type":"photo","media_id":p["id"],"media_url":p["url"],"image":p["url"],"thumbnail":p["url"],"width":p["width"],"height":p["height"],"alt":p["alt"],"media_index":p["index"],"media_total":p["total"]})
            if media_type in {"video","all"}:
                for v in extract_videos(tweet):
                    items.append({**base,"media_type":"video","media_id":v["id"],"media_url":v["url"],"image":v["thumbnail"],"thumbnail":v["thumbnail"],"video_url":v["url"],"width":v["width"],"height":v["height"],"duration":v["duration"],"media_index":v["index"],"media_total":v["total"]})
        if start_dt and reached: break
        nxt=cursor_data.get("bottom") if isinstance(cursor_data,dict) else None
        if not nxt or nxt in seen: break
        seen.add(nxt); cursor=nxt
    items.sort(key=lambda x:x["timestamp"],reverse=True)
    return {"ok":True,"username":username,"count":len(items),"pages":pages,"items":items}

# =========================
# 媒体库导入（V0.8 -> V3.2）
# =========================
def load_library():
    try:
        if not os.path.exists(MEDIA_DB_FILE): return {}
        with open(MEDIA_DB_FILE,"r",encoding="utf-8") as f: data=json.load(f)
        return data if isinstance(data,dict) else {}
    except Exception: return {}

def save_library(data):
    temp=MEDIA_DB_FILE+".tmp"
    with open(temp,"w",encoding="utf-8") as f: json.dump(data,f,ensure_ascii=False)
    os.replace(temp,MEDIA_DB_FILE)

def media_key(tweet_id, item):
    url=(item.get("url") or "").strip()
    if url: return "url:"+url
    return "tweet:"+str(tweet_id)+":type:"+str(item.get("type") or "unknown")

@app.post("/api/import-media")
async def import_media(payload: dict = Body(...)):
    records=payload.get("records", payload)
    if not isinstance(records,dict): raise HTTPException(400,"records 必须是对象")
    library=load_library(); added=0; updated=0; duplicates=0; tweets=0; images=0; videos=0
    for rid,tweet in records.items():
        if not isinstance(tweet,dict): continue
        tweet_id=str(tweet.get("id") or rid)
        media=tweet.get("media") if isinstance(tweet.get("media"),list) else []
        if not media: continue
        tweets+=1
        source=tweet.get("source") or "unknown"
        for item in media:
            if not isinstance(item,dict): continue
            typ=item.get("type") or "image"
            if typ=="image": images+=1
            elif typ=="video": videos+=1
            key=media_key(tweet_id,item)
            old=library.get(key)
            if old:
                old_sources=set(old.get("sources") or [])
                if source: old_sources.add(source)
                old["sources"]=sorted(old_sources)
                old["source"]="both" if len(old_sources)>1 else (next(iter(old_sources)) if old_sources else source)
                if not old.get("url") and item.get("url"): old["url"]=item.get("url"); updated+=1
                elif not old.get("thumbnail") and item.get("thumbnail"): old["thumbnail"]=item.get("thumbnail"); updated+=1
                else: duplicates+=1
                continue
            library[key]={"id":uuid.uuid4().hex,"tweet_id":tweet_id,"tweet_url":tweet.get("url") or "","author":tweet.get("author") or "","source":"both" if False else source,"sources":[source],"type":typ,"url":item.get("url") or "","originalUrl":item.get("originalUrl") or "","thumbnail":item.get("thumbnail") or "","streamType":item.get("streamType") or "","width":item.get("width") or 0,"height":item.get("height") or 0,"downloaded":False,"created_at":tweet.get("updatedAt") or int(datetime.now(timezone.utc).timestamp()*1000)}
            added+=1
    save_library(library)
    return {"ok":True,"added":added,"updated":updated,"duplicates":duplicates,"tweets":tweets,"images":images,"videos":videos,"total":len(library)}

@app.get("/api/media")
async def get_media():
    library=load_library()
    return {"ok":True,"count":len(library),"items":list(library.values())}

@app.post("/api/media/{media_id}/downloaded")
async def mark_downloaded(media_id: str, payload: dict=Body(default={} )):
    library=load_library()
    for item in library.values():
        if item.get("id")==media_id:
            item["downloaded"]=bool(payload.get("downloaded",True))
            save_library(library)
            return {"ok":True,"id":media_id,"downloaded":item["downloaded"]}
    raise HTTPException(404,"媒体不存在")

# =========================
# 下载
# =========================
def safe_filename(value):
    value=unquote(str(value or "")); value=re.sub(r'[\\/:*?"<>|]+',"_",value); return value[:150]

@app.get("/api/download")
async def download(url: str=Query(...), filename: str=Query("x-media")):
    parsed=urlparse(url); allowed={"pbs.twimg.com","pbs.twimg.com.","video.twimg.com","video.twimg.com."}
    if parsed.scheme!="https" or parsed.netloc.lower() not in allowed: raise HTTPException(400,"不是有效的 X 媒体地址")
    headers={"User-Agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1"}
    try:
        async with httpx.AsyncClient(timeout=90,follow_redirects=True,headers=headers) as client: response=await client.get(url)
    except Exception as e: raise HTTPException(502,f"下载失败：{e}")
    if response.status_code>=400: raise HTTPException(response.status_code,"X 媒体服务器拒绝下载，请尝试打开原帖。")
    ct=response.headers.get("content-type","").lower(); ext=".mp4" if "mp4" in ct else ".webm" if "webm" in ct else ".png" if "png" in ct else ".webp" if "webp" in ct else ".jpg"
    filename=safe_filename(filename) or "x-media"
    if not filename.lower().endswith(ext): filename+=ext
    return StreamingResponse(iter([response.content]),media_type=ct or "application/octet-stream",headers={"Content-Disposition":f'attachment; filename="{filename}"'})

HLS_ALLOWED_HOSTS={"video.twimg.com","video.twimg.com."}
def validate_hls_url(url):
    parsed=urlparse(url)
    if parsed.scheme!="https" or (parsed.hostname or "").lower() not in HLS_ALLOWED_HOSTS: raise HTTPException(400,"不是有效的 X 视频地址")
    return url

def cleanup_video_directory(directory):
    try:
        if not os.path.isdir(directory): return
        for name in os.listdir(directory):
            path=os.path.join(directory,name)
            try:
                if os.path.isfile(path): os.remove(path)
            except Exception: pass
        try: os.rmdir(directory)
        except Exception: pass
    except Exception: pass

@app.get("/api/video-download")
async def video_download(url: str=Query(...), filename: str=Query("x-video.mp4")):
    validate_hls_url(url); filename=safe_filename(filename) or "x-video.mp4"
    if not filename.lower().endswith(".mp4"): filename+=".mp4"
    temp_dir=tempfile.mkdtemp(prefix="x-video-"); output_path=os.path.join(temp_dir,f"{uuid.uuid4()}.mp4")
    ua="Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1"
    headers="User-Agent: "+ua+"\r\nReferer: https://x.com/\r\n"
    command=["ffmpeg","-hide_banner","-loglevel","error","-headers",headers,"-protocol_whitelist","file,http,https,tcp,tls,crypto","-allowed_extensions","ALL","-i",url,"-map","0:v:0?","-map","0:a:0?","-c","copy","-movflags","+faststart","-y",output_path]
    try:
        process=await asyncio.to_thread(subprocess.run,command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=180)
    except subprocess.TimeoutExpired:
        cleanup_video_directory(temp_dir); raise HTTPException(504,"视频转换超时")
    except Exception as e:
        cleanup_video_directory(temp_dir); raise HTTPException(500,"FFmpeg 启动失败："+str(e))
    if process.returncode!=0:
        err=process.stderr.decode("utf-8",errors="ignore").strip(); cleanup_video_directory(temp_dir); raise HTTPException(500,"FFmpeg 转换失败："+(err[-3000:] if err else "未知错误"))
    if not os.path.exists(output_path) or os.path.getsize(output_path)<1024:
        cleanup_video_directory(temp_dir); raise HTTPException(500,"生成的 MP4 文件异常")
    return FileResponse(output_path,media_type="video/mp4",filename=filename,background=BackgroundTask(cleanup_video_directory,temp_dir))

@app.get("/")
async def index(): return FileResponse("static/index.html")

@app.get("/api/health")
async def health(): return {"ok":True,"service":"X Media Finder V3"}
