# -*- coding: utf-8 -*-
"""
backfill_authors.py - 博主昵称/头像回填工具
按博主（去重）调 fxtwitter 用户接口抓昵称+头像，写回 media 表全部旧记录。
幂等：默认只处理缺少昵称或头像的博主；--force 全量刷新。
用法：
  set DATABASE_URL=... && venv\\Scripts\\python.exe backfill_authors.py [--force]
"""
import os
import sys
import asyncio

os.environ.setdefault("DATABASE_URL", "postgresql://neondb_owner:npg_qDV2wW3NbTcu@ep-steep-cherry-azvhbrk0.c-3.ap-southeast-1.aws.neon.tech/neondb?sslmode=require")

import httpx

from shared import database, init_db, load_all_media, save_media_item, load_all_favorites, save_favorite

PROXY = "http://127.0.0.1:10808"
UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1"


async def fetch_author_info(client: httpx.AsyncClient, username: str):
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
        except Exception as e:
            print(f"    [warn] {username} 请求失败: {str(e)[:120]}")
    return "", ""


async def main():
    force = "--force" in sys.argv

    await database.connect()
    await init_db()

    library = await load_all_media()
    favorites = await load_all_favorites()
    fav_by_user = {f["username"].lower(): f for f in favorites}

    # 去重作者列表（只处理有 author 的）
    authors = {}
    for item in library.values():
        author = (item.get("author") or "").strip()
        if not author:
            continue
        authors.setdefault(author.lower(), author)

    # 增量：已有昵称且已有头像的跳过（除非 --force）
    todo = []
    for lower, original in authors.items():
        sample = next((it for it in library.values() if (it.get("author") or "").lower() == lower), {})
        has_name = bool((sample.get("author_name") or "").strip())
        has_avatar = bool((sample.get("author_avatar") or "").strip())
        if force or not (has_name and has_avatar):
            todo.append(original)
        else:
            print(f"  [skip] @{original} 已有昵称/头像")

    print(f"媒体总数: {len(library)}, 去重博主: {len(authors)}, 待回填: {len(todo)}")

    if not todo:
        print("无需回填")
        await database.disconnect()
        return

    async with httpx.AsyncClient(proxy=PROXY, timeout=30, follow_redirects=True,
                                 headers={"User-Agent": UA, "Accept": "application/json"}) as client:
        ok_count = 0
        fail_list = []
        for i, author in enumerate(todo, 1):
            name, avatar = await fetch_author_info(client, author)
            if not name and not avatar:
                fail_list.append(author)
                print(f"[{i}/{len(todo)}] @{author}: 未获取到")
                continue

            # 更新该博主名下所有媒体记录
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
                    if not ok:
                        print(f"    [db] {media_id} 保存失败: {err}")
                    else:
                        updated += 1

            # 顺带更新收藏里的博主名
            if author.lower() in fav_by_user:
                await save_favorite(fav_by_user[author.lower()]["username"], name or author)

            ok_count += 1
            print(f"[{i}/{len(todo)}] @{author}: 昵称={name or '(无)'}, 头像={'有' if avatar else '无'}, 更新 {updated} 条")

    print(f"\n完成: 成功 {ok_count}, 失败 {len(fail_list)}")
    if fail_list:
        print("失败博主:", ", ".join("@" + x for x in fail_list), "（可稍后重跑本脚本补齐）")

    await database.disconnect()
# ============================================================
# 手动入口（一般不需要：服务上传/启动时已自动回填）
# 用法：venv\\Scripts\\python.exe backfill_authors.py [--force]
#   --force 全量刷新所有博主的昵称/头像
# ============================================================
import asyncio
import sys

from backfill import backfill_missing_authors


async def main():
    force = "--force" in sys.argv
    result = await backfill_missing_authors(force=force)
    print("[BACKFILL]", result)


if __name__ == "__main__":
    asyncio.run(main())
