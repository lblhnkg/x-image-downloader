# ============================================================
# missav_routes.py - 自动使用你的订阅节点作为代理
# ============================================================

import os
import re
import time
import base64
import requests as req  # 用于请求订阅地址
from urllib.parse import quote, urlparse
from fastapi import APIRouter, HTTPException, Query
import httpx
from bs4 import BeautifulSoup

# 导入 singbox 代理库
try:
    from singbox2proxy import SingBoxProxy
except ImportError:
    print("⚠️ 请先安装 singbox2proxy: pip install singbox2proxy")
    SingBoxProxy = None

router = APIRouter(prefix="/missav", tags=["MissAV"])

# ------------------------------------------------------------
# 配置区（你只需要改这里！）
# ------------------------------------------------------------

# 你的订阅地址（就是你发我的那个链接）
SUBSCRIBE_URL = "https://liangxin.xyz/api/v1/liangxin?OwO=0ff6856dd2351830c0c70dcb55041dfc"

# ------------------------------------------------------------

class MissAVFetcher:
    def __init__(self):
        self.base_domains = ["missav.ws", "missav.ai"]
        self.timeout = 60
        self.proxy_client = None
        self._init_proxy()

    def _init_proxy(self):
        """初始化代理：从订阅地址提取节点并启动 sing-box"""
        if SingBoxProxy is None:
            print("[MissAV] singbox2proxy 未安装，无法使用代理")
            return

        try:
            print("[MissAV] 正在获取订阅节点...")
            # 1. 获取订阅内容
            resp = req.get(SUBSCRIBE_URL, timeout=30)
            if resp.status_code != 200:
                print(f"[MissAV] 订阅获取失败: {resp.status_code}")
                return

            raw_text = resp.text.strip()
            
            # 2. 尝试解码 Base64（订阅通常都是 Base64 编码的）
            decoded = ""
            try:
                # 补全 Base64 填充
                missing_padding = len(raw_text) % 4
                if missing_padding:
                    raw_text += '=' * (4 - missing_padding)
                decoded = base64.b64decode(raw_text).decode('utf-8')
                print(f"[MissAV] 订阅解码成功")
            except Exception:
                # 如果不是 Base64，就直接用原文
                decoded = raw_text
                print("[MissAV] 订阅不是 Base64 格式，直接使用原文")

            # 3. 从解码内容中提取 vless:// 或 vmess:// 链接
            # 匹配标准代理链接格式
            match = re.search(r'(vless|vmess)://[^\s\n]+', decoded)
            if not match:
                # 尝试找包含 @ 和端口的通用格式
                match = re.search(r'[a-zA-Z0-9]+://[^\s\n]+', decoded)
            
            if not match:
                print("[MissAV] 错误：未能从订阅中提取出有效的代理链接")
                return

            proxy_link = match.group(0)
            print(f"[MissAV] 成功提取代理节点: {proxy_link[:50]}...")

            # 4. 初始化 sing-box 代理客户端
            # 注意：首次运行会下载 sing-box 内核（约 20MB），可能需要几十秒
            self.proxy_client = SingBoxProxy(proxy_link)
            print("[MissAV] Sing-box 代理客户端初始化成功")

        except Exception as e:
            print(f"[MissAV] 代理初始化失败: {e}")
            self.proxy_client = None

    def _fetch_via_proxy(self, url):
        """通过 sing-box 代理请求目标网页"""
        if not self.proxy_client:
            raise Exception("代理客户端未初始化，请检查订阅链接是否有效")

        for attempt in range(3):
            try:
                print(f"[MissAV] 通过代理请求 (尝试 {attempt+1}): {url}")
                # 使用代理发起 GET 请求
                # singbox2proxy 的 request 方法返回响应对象
                response = self.proxy_client.request("GET", url)
                
                if response.status_code == 200:
                    # 检查是否返回了验证页
                    if "Just a moment" in response.text or "Cloudflare" in response.text[:500]:
                        print(f"[MissAV] 代理返回了验证页，重试中...")
                        time.sleep(2 ** attempt)
                        continue
                    return response.text
                else:
                    print(f"[MissAV] 代理返回状态码: {response.status_code}")
                    time.sleep(1 * (attempt + 1))
            except Exception as e:
                print(f"[MissAV] 代理请求异常 {attempt+1}: {e}")
                time.sleep(1 * (attempt + 1))
        
        raise Exception("所有代理请求均失败，可能节点已失效")

    # ---------- 搜索与解析逻辑（和之前一样，只是换成了代理请求）----------
    def search(self, keyword):
        if len(keyword) < 2:
            raise ValueError("至少输入2个字符")
        for domain in self.base_domains:
            base = "https://" + domain
            for path in [f"/search/{quote(keyword)}", f"/search?q={quote(keyword)}"]:
                url = base + path
                try:
                    html = self._fetch_via_proxy(url)
                    if len(html) < 500:
                        continue
                    soup = BeautifulSoup(html, 'lxml')
                    links = soup.select('a[href*="/watch/"], a[href*="/dm1/"], a[href*="/v/"]')
                    if not links:
                        links = soup.find_all('a', href=re.compile(r'/(watch|dm1|v)/[^/]+'))
                    if links:
                        return self._parse_search(html, base)
                except Exception as e:
                    print(f"[MissAV] 搜索尝试失败 {url}: {e}")
                    continue
        raise Exception("所有搜索尝试均失败")

    def _parse_search(self, html, base):
        soup = BeautifulSoup(html, 'lxml')
        results = []
        seen = set()
        links = soup.select('a[href*="/watch/"], a[href*="/dm1/"], a[href*="/v/"]')
        if not links:
            links = soup.find_all('a', href=re.compile(r'/(watch|dm1|v)/[^/]+'))
        for a in links:
            href = a.get('href')
            if not href or href in seen:
                continue
            full_url = base + href if href.startswith('/') else href
            video_id = href.split('/')[-1] if href.split('/') else ""
            img = a.find('img')
            src = ""
            if img:
                src = img.get('src') or img.get('data-src') or img.get('data-original') or ""
                if src.startswith('//'):
                    src = "https:" + src
                elif src.startswith('/'):
                    src = base + src
            title = a.get('title', '') or (img.get('alt', '') if img else '')
            title = title.strip() or "未知标题"
            code_match = re.search(r'([A-Z]{2,6}-\d{3,5})', title)
            code = code_match.group(1) if code_match else ""
            results.append({
                "id": video_id,
                "url": full_url,
                "title": title,
                "code": code,
                "cover": src,
            })
            seen.add(href)
            if len(results) >= 30:
                break
        return results

    def get_detail(self, video_id_or_url):
        if video_id_or_url.startswith('http'):
            parsed = urlparse(video_id_or_url)
            base = f"{parsed.scheme}://{parsed.netloc}"
            html = self._fetch_via_proxy(video_id_or_url)
            return self._parse_detail(html, base, video_id_or_url, video_id_or_url)
        for domain in self.base_domains:
            base = "https://" + domain
            for path in [f"/watch/{video_id_or_url}", f"/dm1/{video_id_or_url}", f"/v/{video_id_or_url}"]:
                url = base + path
                try:
                    html = self._fetch_via_proxy(url)
                    if len(html) < 500:
                        continue
                    return self._parse_detail(html, base, video_id_or_url, url)
                except Exception as e:
                    print(f"[MissAV] 详情尝试失败 {url}: {e}")
                    continue
        raise Exception("所有详情尝试均失败")

    def _parse_detail(self, html, base, video_id, url):
        soup = BeautifulSoup(html, 'lxml')
        title = soup.find('h1').text.strip() if soup.find('h1') else "未知"
        code_match = re.search(r'([A-Z]{2,6}-\d{3,5})', title)
        code = code_match.group(1) if code_match else ""
        cover = ""
        meta_og = soup.find('meta', property='og:image')
        if meta_og:
            cover = meta_og.get('content', '')
        if not cover:
            img = soup.select_one('img[alt*="cover"], img[src*="cover"]')
            if img:
                cover = img.get('src') or img.get('data-src') or ""
        if cover and cover.startswith('//'):
            cover = "https:" + cover
        elif cover and cover.startswith('/'):
            cover = base + cover
        actors = [a.text.strip() for a in soup.select('a[href*="/actor/"]') if a.text.strip()]
        actors = list(dict.fromkeys(actors))
        desc = ""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            desc = meta_desc.get('content', '')
        video_url = ""
        for script in soup.find_all('script'):
            if script.string:
                for pat in [r'video_url\s*[:=]\s*["\'](https?://[^"\']+\.m3u8[^"\']*)["\']',
                            r'videoUrl\s*[:=]\s*["\'](https?://[^"\']+\.m3u8[^"\']*)["\']',
                            r'(https?://[^\s"\']+\.m3u8[^\s"\']*)']:
                    matches = re.findall(pat, script.string, re.I)
                    if matches:
                        video_url = matches[0]
                        break
                if video_url:
                    break
        if not video_url:
            video_tag = soup.find('video')
            if video_tag and video_tag.get('src'):
                video_url = video_tag.get('src')
        if not video_url:
            raise Exception("未找到视频源 m3u8")
        if video_url.startswith('//'):
            video_url = "https:" + video_url
        return {
            "id": video_id,
            "code": code,
            "title": title,
            "cover": cover,
            "actors": actors,
            "description": desc[:500],
            "video_url": video_url,
            "url": url,
        }

fetcher = MissAVFetcher()

@router.get("/search")
async def missav_search(q: str = Query(..., min_length=1)):
    try:
        items = fetcher.search(q)
        return {"ok": True, "count": len(items), "items": items}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"搜索失败: {str(e)}")

@router.get("/info")
async def missav_info(video_id: str = Query(...)):
    try:
        data = fetcher.get_detail(video_id)
        return {"ok": True, "item": data}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"获取详情失败: {str(e)}")
