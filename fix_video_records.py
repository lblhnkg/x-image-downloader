# -*- coding: utf-8 -*-
"""
fix_video_records.py - 修复被误当图片入库的视频封面图记录
问题：采集脚本漏排除 amplify_video_thumb，导致视频封面图以 type=image 入库
方案：对受影响 tweet 调 fxtwitter status API 反查真实视频，删除错误 image 记录，
      写入正确 video 记录（url=真实视频地址, thumbnail=封面图）。
幂等：已修复过的记录不会重复处理。
"""
import asyncio, sys, os
sys.path.insert(0, r'D:\local-deploy\x-image-downloader')

os.environ.setdefault("DATABASE_URL", "postgresql://neondb_owner:npg_qDV2wW3NbTcu@ep-steep-cherry-azvhbrk0.c-3.ap-southeast-1.aws.neon.tech/neondb?sslmode=require")

import httpx
from shared import database, load_all_media, save_media_item, delete_media_items

PROXY = "http://127.0.0.1:10808"
UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1"

# 视频封面图特征
THUMB_MARKERS = ("ext_tw_video_thumb", "amplify_video_thumb")


def is_bad_image_record(item):
    """type=image 但 URL 是视频封面图 → 误入库"""
    if item.get("type") != "image":
        return False
    url = item.get("url") or ""
    return any(m in url for m in THUMB_MARKERS)


async def fetch_tweet_videos(client, tweet_id):
    """调 fxtwitter status API 拿真实视频列表，返回 [{url, thumbnail, streamType}]"""
    try:
        r = await client.get(f"https://api.fxtwitter.com/status/{tweet_id}", timeout=30)
        if r.status_code != 200:
            return None
        data = r.json()
        media = (data.get("tweet") or {}).get("media") or {}
        videos = media.get("videos") or []
        result = []
        for v in videos:
            url = (v.get("url") or "").strip()
            if not url:
                continue
            thumb = (v.get("thumbnailUrl") or "").strip()
            stream = "hls" if (".m3u8" in url) else "mp4"
            result.append({"url": url, "thumbnail": thumb, "streamType": stream})
        return result or []
    except Exception as e:
        print(f"    [fetch] {tweet_id} 异常: {str(e)[:100]}")
        return None


async def main():
    await database.connect()
    lib = await load_all_media()

    # 1. 找出所有误入库记录
    bad = [it for it in lib.values() if is_bad_image_record(it)]
    print(f"误入库的封面图记录: {len(bad)} 条")

    if not bad:
        print("无需修复")
        await database.disconnect()
        return

    # 2. 按 tweet_id 分组（保留每条记录的 media_id）
    by_tweet = {}
    for it in bad:
        tid = it.get("tweet_id") or ""
        if not tid:
            continue
        by_tweet.setdefault(tid, []).append(it)

    print(f"涉及 tweet 数: {len(by_tweet)}")

    # 3. 对每个 tweet 抓真实视频
    fixed = 0
    skipped_tweets = 0
    still_bad = 0
    failed_tweets = []

    async with httpx.AsyncClient(proxy=PROXY, timeout=30, follow_redirects=True,
                                 headers={"User-Agent": UA, "Accept": "application/json"}) as client:
        for i, (tid, records) in enumerate(by_tweet.items(), 1):
            # 该 tweet 是否已有正确 video 记录（去重基准）
            existing_videos = [v for v in lib.values()
                               if v.get("tweet_id") == tid and v.get("type") == "video" and (v.get("url") or "").strip()]
            existing_urls = {v.get("url") for v in existing_videos}

            videos = await fetch_tweet_videos(client, tid)
            if videos is None:
                failed_tweets.append(tid)
                print(f"[{i}/{len(by_tweet)}] @{records[0].get('author')} tweet={tid}: API 请求失败，保留原记录")
                continue
            if not videos:
                # API 正常但无视频（可能已删/仅剩图）：删掉误入库封面记录，避免展示假图片
                del_ids = [r.get("id") for r in records]
                deleted = await delete_media_items(del_ids)
                if deleted > 0:
                    for r in records:
                        lib.pop(r.get("id"), None)
                    fixed += 1
                else:
                    still_bad += len(records)
                    print(f"    [del] {tid} 删除失败")
                print(f"[{i}/{len(by_tweet)}] @{records[0].get('author')} tweet={tid}: 已无视频，删除 {deleted} 条封面图记录")
                continue

            # 删除误入库封面图记录
            del_ids = [r.get("id") for r in records]
            deleted = await delete_media_items(del_ids)
            if deleted <= 0:
                print(f"    [del] {tid} 删除失败")
                still_bad += len(records)
                continue
            for r in records:
                lib.pop(r.get("id"), None)

            # 写入缺失的视频记录
            added = 0
            max_idx = max([v.get("index") or 0 for v in existing_videos] or [-1])
            for v in videos:
                if v["url"] in existing_urls:
                    continue
                max_idx += 1
                new_id = f"tweet_{tid}_video_{max_idx}"
                if new_id in lib:
                    continue
                record = {
                    "id": new_id,
                    "tweet_id": tid,
                    "tweet_url": records[0].get("tweet_url") or "",
                    "author": records[0].get("author") or "",
                    "source": records[0].get("source") or "likes",
                    "type": "video",
                    "url": v["url"],
                    "originalUrl": v["url"],
                    "thumbnail": v["thumbnail"] or (records[0].get("thumbnail") or ""),
                    "streamType": v["streamType"],
                    "width": 0,
                    "height": 0,
                    "bitrate": 0,
                    "downloaded": False,
                    "createdAt": records[0].get("createdAt") or __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
                    "tweetCreatedAt": records[0].get("tweetCreatedAt") or "",
                }
                ok2, err2 = await save_media_item(new_id, record)
                if ok2:
                    lib[new_id] = record
                    added += 1
                    existing_urls.add(v["url"])
                else:
                    print(f"    [save] {new_id} 保存失败: {err2}")
            fixed += 1
            print(f"[{i}/{len(by_tweet)}] @{records[0].get('author')} tweet={tid}: 删 {len(records)} 条封面图，补 {added} 条视频")

    print(f"\n完成: 处理 tweet {len(by_tweet)}, 成功修复 {fixed}, 保留 {still_bad} 条, API 失败 {len(failed_tweets)}")
    if failed_tweets:
        print("API 失败 tweet:", ", ".join(failed_tweets[:20]), "（可稍后重跑）")

    await database.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
