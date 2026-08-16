# generate_config.py - 将 VLESS 节点转换为 sing-box 配置（自动切换）
import re
import json
from urllib.parse import parse_qs, unquote

def parse_vless_link(link):
    """解析单个 vless 链接，返回 (tag, config_dict)"""
    if not link.startswith("vless://"):
        return None

    no_proto = link[8:]

    at_pos = no_proto.find('@')
    if at_pos == -1:
        return None
    user_uuid = no_proto[:at_pos]
    rest = no_proto[at_pos+1:]

    fragment = ""
    if '#' in rest:
        rest, fragment = rest.split('#', 1)
        fragment = unquote(fragment)

    if '?' in rest:
        host_part, query_part = rest.split('?', 1)
        query = parse_qs(query_part)
    else:
        host_part = rest
        query = {}

    if ':' in host_part:
        server, server_port = host_part.split(':')
        server_port = int(server_port)
    else:
        server = host_part
        server_port = 443

    params = {
        "uuid": user_uuid,
        "server": server,
        "server_port": server_port,
    }

    if 'encryption' in query:
        params["encryption"] = query['encryption'][0]

    security = query.get('security', [''])[0]
    if security:
        params["tls"] = {"enabled": True, "insecure": False}
        if 'fp' in query:
            params["tls"]["utls"] = {"enabled": True, "fingerprint": query['fp'][0]}
        sni = query.get('sni', [''])[0] or query.get('host', [''])[0]
        if sni:
            params["tls"]["server_name"] = sni
        if query.get('insecure', [''])[0] == '1':
            params["tls"]["insecure"] = True
    else:
        params["security"] = "none"

    transport_type = query.get('type', ['ws'])[0]
    if transport_type == 'ws':
        params["transport"] = {"type": "ws"}
        if 'path' in query:
            params["transport"]["path"] = query['path'][0]
        if 'host' in query:
            params["transport"]["headers"] = {"Host": query['host'][0]}
    elif transport_type == 'tcp':
        params["transport"] = {"type": "tcp"}

    if 'flow' in query and query['flow'][0]:
        params["flow"] = query['flow'][0]

    tag = fragment if fragment else f"{server}:{server_port}"
    # 清理非法字符，只保留字母数字、中文、下划线、连字符
    tag = re.sub(r'[^a-zA-Z0-9_\u4e00-\u9fa5\-]', '_', tag)

    return tag, params

def generate_config():
    print("🔄 开始解析节点...")
    try:
        with open("decoded_links_5CD26D8E-F0E1-4488-8C90-1C2CA7138B4A.txt", "r", encoding="utf-8") as f:
            NODES_TEXT = f.read()
    except FileNotFoundError:
        print("❌ 未找到节点文件 decoded_links_5CD26D8E-F0E1-4488-8C90-1C2CA7138B4A.txt")
        return

    lines = NODES_TEXT.strip().splitlines()
    outbounds = []
    tags = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if not line.startswith("vless://"):
            continue
        parsed = parse_vless_link(line)
        if parsed:
            tag, params = parsed
            # 避免重复标签
            original_tag = tag
            counter = 1
            while tag in tags:
                tag = f"{original_tag}_{counter}"
                counter += 1
            outbound = {"type": "vless", "tag": tag, **params}
            outbounds.append(outbound)
            tags.append(tag)
            print(f"  ✅ 已解析: {tag}")
        else:
            print(f"  ⚠️ 跳过无法解析的行: {line[:50]}...")

    if not outbounds:
        print("❌ 没有解析到任何有效节点，请检查文件格式！")
        return

    # 构建完整配置，使用 urltest 自动切换
    config = {
        "log": {"level": "info"},
        "inbounds": [
            {
                "type": "socks",
                "tag": "socks-in",
                "listen": "127.0.0.1",
                "listen_port": 1080
            }
        ],
        "outbounds": outbounds + [
            {
                "type": "urltest",
                "tag": "proxy-selector",
                "outbounds": tags,
                "url": "https://www.google.com",
                "interval": "5m",
                "tolerance": 50
            }
        ],
        "route": {
            "rules": [
                {"outbound": "proxy-selector", "network": "tcp"}
            ]
        }
    }

    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"\n✅ config.json 已生成，共包含 {len(tags)} 个节点。")
    print(f"自动切换已启用（urltest），每5分钟测试一次，默认选择延迟最低的节点。")

if __name__ == "__main__":
    generate_config()
