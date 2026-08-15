# ============================================================
# missav_routes.py - 使用节点池自动切换（最终版）
# ============================================================

import os
import re
import time
import random
from urllib.parse import quote, urlparse
from fastapi import APIRouter, HTTPException, Query
from bs4 import BeautifulSoup

# 导入 singbox 代理库
try:
    from singbox2proxy import SingBoxProxy
except ImportError:
    print("⚠️ 请先安装 singbox2proxy: pip install singbox2proxy")
    SingBoxProxy = None

router = APIRouter(prefix="/missav", tags=["MissAV"])

# ------------------------------------------------------------
# 节点池（从你的订阅中提取的所有 vless 节点，去重后整理）
# ------------------------------------------------------------
NODES = [
    # 日本节点（不同 host）
    "vless://39225b24-bf38-47c7-863b-3341d45f853b@cfyes.7770006.xyz:443?type=ws&encryption=none&host=jp1-lx.7770006.xyz&path=%2Fliangxin%2Fdata%2Fjp&headerType=none&quicSecurity=none&serviceName=&security=tls&fp=safari&insecure=0&sni=jp1-lx.7770006.xyz#🇯🇵日本高速01",
    "vless://39225b24-bf38-47c7-863b-3341d45f853b@cfyes.7770006.xyz:443?type=ws&encryption=none&host=jp2-lx.7770006.xyz&path=%2Fliangxin%2Fdata&headerType=none&quicSecurity=none&serviceName=&security=tls&fp=safari&insecure=0&sni=jp2-lx.7770006.xyz#🇯🇵日本高速02",
    "vless://39225b24-bf38-47c7-863b-3341d45f853b@cfyes.7770006.xyz:443?type=ws&encryption=none&host=jp3-lx.7770006.xyz&path=%2Fliangxin%2Fdash%2Fjp&headerType=none&quicSecurity=none&serviceName=&security=tls&fp=chrome&insecure=0&sni=jp3-lx.7770006.xyz#🇯🇵日本高速06",
    "vless://39225b24-bf38-47c7-863b-3341d45f853b@cfyes.7770006.xyz:443?type=ws&encryption=none&host=jp4-lx.7770006.xyz&path=%2Fliangxin%2Fdownload%2Fjp&headerType=none&quicSecurity=none&serviceName=&security=tls&fp=chrome&insecure=0&sni=jp4-lx.7770006.xyz#🇯🇵日本高速08",

    # 香港节点（不同 host）
    "vless://39225b24-bf38-47c7-863b-3341d45f853b@aws-link1.lxyun.xyz:36458?type=tcp&encryption=none&host=&path=&headerType=none&quicSecurity=none&serviceName=&security=tls&flow=xtls-rprx-vision&fp=safari&insecure=1&sni=iosapps.itunes.apple.com&pcs=d5c39647e414c144b719bc49cb41c4b8f46f09f4cf26c863cae15c01d4a7b96a#🇭🇰香港高速01",
    "vless://39225b24-bf38-47c7-863b-3341d45f853b@aws-link2.lxyun.xyz:28346?type=tcp&encryption=none&host=&path=&headerType=none&quicSecurity=none&serviceName=&security=tls&flow=xtls-rprx-vision&fp=safari&insecure=1&sni=www.lamer.com.hk&pcs=af0f11574724e7ddd96f64eb77a450f71ce2de61ee5afd6f2e27ed7604a6a9b1#🇭🇰香港高速02",
    "vless://39225b24-bf38-47c7-863b-3341d45f853b@aws-link3.lxyun.xyz:27786?type=tcp&encryption=none&host=&path=&headerType=none&quicSecurity=none&serviceName=&security=reality&flow=xtls-rprx-vision&fp=ios&insecure=0&sni=www.lamer.com.hk&pbk=EYa4ic3GAxqznV61U-OOww-WKsu5wuQQptyS3fw7czM&sid=c50db39f#🇭🇰香港高速03",
    "vless://39225b24-bf38-47c7-863b-3341d45f853b@aws-link4.lxyun.xyz:23564?type=tcp&encryption=none&host=&path=&headerType=none&quicSecurity=none&serviceName=&security=reality&flow=xtls-rprx-vision&fp=ios&insecure=0&sni=www.lamer.com.hk&pbk=3FPGTaxkfOM3nEUWUyCiqkH5oJGsOx-WxPJfADi1QWY&sid=7f369e14#🇭🇰香港高速04",
    "vless://39225b24-bf38-47c7-863b-3341d45f853b@aws-link5.lxyun.xyz:35332?type=tcp&encryption=none&host=&path=&headerType=none&quicSecurity=none&serviceName=&security=reality&flow=xtls-rprx-vision&fp=ios&insecure=0&sni=www.lamer.com.hk&pbk=a11gdDetacKBsiBBfhsPvanTGMtVyZEIvax7gU5Wplg&sid=9bf38508#🇭🇰香港高速05",
    "vless://39225b24-bf38-47c7-863b-3341d45f853b@cfyes.777078.xyz:443?type=ws&encryption=none&host=lx-hk1.7770008.xyz&path=%2Fliangxin%2Fdata%2Fhk1&headerType=none&quicSecurity=none&serviceName=&security=tls&fp=safari&insecure=0&sni=lx-hk1.7770008.xyz#🇭🇰香港01住宅IP",
    "vless://39225b24-bf38-47c7-863b-3341d45f853b@cfyes.777078.xyz:443?type=ws&encryption=none&host=lx-hk2.7770008.xyz&path=%2Fliangxin%2Fdata%2Fhk2&headerType=none&quicSecurity=none&serviceName=&security=tls&fp=safari&insecure=0&sni=lx-hk2.7770008.xyz#🇭🇰香港02住宅IP",
    "vless://39225b24-bf38-47c7-863b-3341d45f853b@cfyes.777078.xyz:443?type=ws&encryption=none&host=lx-hk3.7770008.xyz&path=%2Fliangxin%2Fdata%2Fhk3&headerType=none&quicSecurity=none&serviceName=&security=tls&fp=safari&insecure=0&sni=lx-hk3.7770008.xyz#🇭🇰香港03住宅IP",
    "vless://39225b24-bf38-47c7-863b-3341d45f853b@cfyes.777078.xyz:443?type=ws&encryption=none&host=lx-hk4.7770008.xyz&path=%2Fliangxin%2Fdata%2Fhk4&headerType=none&quicSecurity=none&serviceName=&security=tls&fp=safari&insecure=0&sni=lx-hk4.7770008.xyz#🇭🇰香港04住宅IP",
    "vless://39225b24-bf38-47c7-863b-3341d45f853b@cfyes.777078.xyz:443?type=ws&encryption=none&host=lx-hk5.7770008.xyz&path=%2Fliangxin%2Fdata%2Fhk5&headerType=none&quicSecurity=none&serviceName=&security=tls&fp=safari&insecure=0&sni=lx-hk5.7770008.xyz#🇭🇰香港05住宅IP",

    # 新加坡节点（部分）
    "vless://39225b24-bf38-47c7-863b-3341d45f853b@aws-link7.lxyun.xyz:48574?type=tcp&encryption=none&host=&path=&headerType=none&quicSecurity=none&serviceName=&security=reality&flow=xtls-rprx-vision&fp=ios&insecure=0&sni=www.lamer.com.sg&pbk=lmxSayN8tUg2Dag2MPXrdqZ2SQK9K3OjlaKk8wVCRnc&sid=f8f18902#🇸🇬新加坡高速01",
    "vless://39225b24-bf38-47c7-863b-3341d45f853b@aws-link8.lxyun.xyz:39645?type=tcp&encryption=none&host=&path=&headerType=none&quicSecurity=none&serviceName=&security=reality&flow=xtls-rprx-vision&fp=ios&insecure=0&sni=iosapps.itunes.apple.com&pbk=x7VqpFP7_PrY4ebNw8hi8Ec5Tm5Upmt5JOdrN1M9VnQ&sid=2b3b0b93#🇸🇬新加坡高速02",
    "vless://39225b24-bf38-47c7-863b-3341d45f853b@aws-link9.lxyun.xyz:23587?type=tcp&encryption=none&host=&path=&headerType=none&quicSecurity=none&serviceName=&security=reality&flow=xtls-rprx-vision&fp=ios&insecure=0&sni=iosapps.itunes.apple.com&pbk=H66PLLf6HkZwHk4oFqisfTawIvw2cxkEwk8Ue8sHZgA&sid=19b580ae#🇸🇬新加坡高速03",
    "vless://39225b24-bf38-47c7-863b-3341d45f853b@aws-link30.lxyun.xyz:23568?type=tcp&encryption=none&host=&path=&headerType=none&quicSecurity=none&serviceName=&security=reality&flow=xtls-rprx-vision&fp=safari&insecure=0&sni=www.lamer.com.hk&pbk=EjcM-ENrpWY8iIL82qJtQrZgRs4KlVqhdisqLAXonUY&sid=55d046dc#🇸🇬新加坡高速04",
    "vless://39225b24-bf38-47c7-863b-3341d45f853b@aws-link31.lxyun.xyz:443?type=tcp&encryption=none&host=&path=&headerType=none&quicSecurity=none&serviceName=&security=reality&flow=xtls-rprx-vision&fp=safari&insecure=0&sni=download-porter.hoyoverse.com&pbk=wXayfckurSM2zWeis7OAL_QVGm9wBLr0WYp2zFtJFAE&sid=c7487aeb#🇸🇬新加坡高速05",
    "vless://39225b24-bf38-47c7-863b-3341d45f853b@cfyes.7770008.xyz:443?type=ws&encryption=none&host=lx-1sg.lxy1015.top&path=%2Fliangxin%2Fsg1&headerType=none&quicSecurity=none&serviceName=&security=tls&fp=chrome&insecure=0&sni=lx-1sg.lxy1015.top#🇸🇬新加坡高速06",

    # 美国节点（部分）
    "vless://39225b24-bf38-47c7-863b-3341d45f853b@cfyes.777078.xyz:443?type=ws&encryption=none&host=lx-us1.777078.xyz&path=%2Fliangxin%2Fus&headerType=none&quicSecurity=none&serviceName=&security=tls&fp=chrome&insecure=0&sni=lx-us1.777078.xyz#🇺🇸美国高速01",
    "vless://39225b24-bf38-47c7-863b-3341d45f853b@cfyes.777078.xyz:443?type=ws&encryption=none&host=lx-us2.777078.xyz&path=%2Fliangxin%2Fus&headerType=none&quicSecurity=none&serviceName=&security=tls&fp=chrome&insecure=0&sni=lx-us2.777078.xyz#🇺🇸美国高速02",
    "vless://39225b24-bf38-47c7-863b-3341d45f853b@lxyus1.777078.xyz:443?type=tcp&encryption=none&host=&path=&headerType=none&quicSecurity=none&serviceName=&security=reality&flow=xtls-rprx-vision&fp=safari&insecure=0&sni=iosapps.itunes.apple.com&pbk=ulU6wfyain_FQnYt23NGunTAfBQNLhIBY49mvekiQB0&sid=ca032f81#🇺🇸美国洛杉矶01",
]

# ------------------------------------------------------------
# 节点管理器
# ------------------------------------------------------------
class NodeManager:
    def __init__(self, nodes):
        self.nodes = nodes
        self.current_index = 0
        self.proxy_client = None

    def get_next_node(self):
        """轮询获取下一个节点"""
        if not self.nodes:
            raise Exception("节点列表为空")
        node = self.nodes[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.nodes)
        return node

    def get_proxy_client(self):
        """尝试创建代理客户端，如果失败则自动换节点"""
        if self.proxy_client is not None:
            # 如果已有客户端，先清理（可选）
            pass

        # 尝试最多 len(nodes) 次
        for _ in range(len(self.nodes)):
            node = self.get_next_node()
            try:
                print(f"[MissAV] 尝试使用节点: {node.split('#')[-1] if '#' in node else 'unnamed'}")
                client = SingBoxProxy(node)
                # 简单测试连接：请求一个健康检查页面（或者直接返回客户端）
                # 由于无法在初始化时测试，我们返回客户端，在请求时捕获异常
                self.proxy_client = client
                return client
            except Exception as e:
                print(f"[MissAV] 节点初始化失败: {e}，切换到下一个")
                self.proxy_client = None
                continue
        raise Exception("所有节点初始化均失败")

    def reset(self):
        """重置节点索引（可选）"""
        self.current_index = 0
        self.proxy_client = None

# ------------------------------------------------------------
# MissAV 抓取器
# ------------------------------------------------------------
class MissAVFetcher:
    def __init__(self):
        self.base_domains = ["missav.ws", "missav.ai"]
        self.timeout = 60
        self.node_manager = NodeManager(NODES)
        self.current_proxy = None

    def _fetch_via_proxy(self, url):
        """通过节点池代理请求，自动切换"""
        if not NODES:
            raise Exception("节点列表为空，请检查配置")

        # 尝试所有节点（最多轮询一遍）
        for attempt in range(len(NODES)):
            try:
                # 获取一个可用节点
                client = self.node_manager.get_proxy_client()
                print(f"[MissAV] 通过代理请求 (尝试 {attempt+1}): {url}")
                response = client.request("GET", url, timeout=self.timeout)
                if response.status_code == 200:
                    # 检查是否返回验证页
                    if "Just a moment" in response.text or "Cloudflare" in response.text[:500]:
                        print(f"[MissAV] 节点返回验证页，切换节点")
                        self.node_manager.proxy_client = None  # 强制换节点
                        continue
                    return response.text
                else:
                    print(f"[MissAV] 节点返回状态码 {response.status_code}，切换节点")
                    self.node_manager.proxy_client = None
                    continue
            except Exception as e:
                print(f"[MissAV] 节点请求异常: {e}，切换节点")
                self.node_manager.proxy_client = None
                continue

        raise Exception("所有节点均请求失败，请检查节点是否有效")

    # ----- 以下 search, get_detail, _parse_search, _parse_detail 与之前完全一致 -----
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

# ------------------------------------------------------------
# FastAPI 路由
# ------------------------------------------------------------
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
