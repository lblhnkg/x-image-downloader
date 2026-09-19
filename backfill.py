# -*- coding: utf-8 -*-
"""
backfill.py - 自动回填模块
检测缺昵称(author_name)/头像(author_avatar)的博主，调 fxtwitter 抓取后写回 media 表。
触发点：
  1) /api/import-media 上传新数据后（只处理本次涉及的新博主）
  2) 服务启动时兜底（全库检查缺失）
并发保护：同一时间只允许一个回填任务；失败静默，不影响调用方。
"""
import asyncio
import httpx

import shared
from shared import database, load_all_media, save_media_item, load_all_favorites, save_favorite

PROXY = "http://127.0.0.1:10808"
UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1"

_running = False


async def _fetch_author_info(client: httpx.AsyncClient, username: str):
    """调 fxtwitter 用户接口，返回 (name, avatar)"""
    for url in (
        f"https://api.fxtwitter.com/{username}",
        f"https://api.fxtwitter.com/2/profile/{username}",
    ):
        try:
            r = await client.get(url, timeout=30)
            if r.status_code != 200:
                continue
            data = r.json()
            user = data.get("user") or (data.get("data") or {}).get("user") or {}
            name = (user.get("name") or "").strip()
            avatar = (user.get("avatar_url") or user.get("profile_image_url") or "").strip()
            if not name and not avatar:
                continue
            if avatar and "_normal." in avatar:
                avatar = avatar.replace("_normal.", "_200x200.")
            return name, avatar
        except Exception:
            continue
    return "", ""


async def backfill_missing_authors(authors_hint=None, force: bool = False, library_ref=None):
    """回填缺昵称/头像的博主。
    authors_hint: 可选集合（博主名），只处理这些博主；None 表示全库检查。
    force: True 时全量刷新（包括已有昵称头像的博主）。
    library_ref: 可选目标内存字典（如路由层的 media_library），写库成功后同步。
    """
    global _running
    if _running:
        return {"status": "skipped", "reason": "already_running"}
    _running = True
    try:
        if not database.is_connected:
            await database.connect()
        library = await load_all_media()
        favorites = await load_all_favorites()
        fav_by_user = {f["username"].lower(): f for f in favorites}
        hint_lower = {a.lower() for a in authors_hint} if authors_hint is not None else None

        # 收集待回填博主（去重）
        authors = {}
        for item in library.values():
            author = (item.get("author") or "").strip()
            if not author:
                continue
            if hint_lower is not None and author.lower() not in hint_lower:
                continue
            has_name = bool((item.get("author_name") or "").strip())
            has_avatar = bool((item.get("author_avatar") or "").strip())
            if force or not (has_name and has_avatar):
                authors.setdefault(author.lower(), author)

        if not authors:
            return {"status": "ok", "checked": 0, "ok": 0, "failed": []}

        ok_count = 0
        fail_list = []
        async with httpx.AsyncClient(
            proxy=PROXY, timeout=30, follow_redirects=True,
            headers={"User-Agent": UA, "Accept": "application/json"},
        ) as client:
            for author in authors.values():
                name, avatar = await _fetch_author_info(client, author)
                if not name and not avatar:
                    fail_list.append(author)
                    print(f"[BACKFILL] @{author}: 未获取到（自动重试会跳过）")
                    continue

                updated = 0
                for media_id, item in library.items():
                    if (item.get("author") or "").strip().lower() != author.lower():
                        continue
                    changed = False
                    if name and item.get("author_name") != name:
                        item["author_name"] = name
                        changed = True
                    if avatar and item.get("author_avatar") != avatar:
                        item["author_avatar"] = avatar
                        changed = True
                    if changed:
                        ok, err = await save_media_item(media_id, item)
                        if ok:
                            updated += 1
                            # 同步目标内存缓存（路由层 media_library）
                            if library_ref is not None:
                                library_ref[media_id] = item
                            elif shared.media_library:
                                shared.media_library[media_id] = item

                if author.lower() in fav_by_user:
                    await save_favorite(fav_by_user[author.lower()]["username"], name or author)

                ok_count += 1
                print(f"[BACKFILL] @{author}: 昵称={name or '(无)'} 头像={'有' if avatar else '无'} 更新{updated}条")

        if fail_list:
            print(f"[BACKFILL] 未获取到的博主（多为注销账号）: {', '.join('@' + a for a in fail_list)}")
        return {"status": "ok", "checked": len(authors), "ok": ok_count, "failed": fail_list}
    except Exception as e:
        print(f"[BACKFILL] 回填异常: {str(e)[:200]}")
        return {"status": "error", "error": str(e)[:200]}
    finally:
        _running = False
