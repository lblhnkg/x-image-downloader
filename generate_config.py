# generate_config.py - 将你的 VLESS 节点自动转换为 sing-box 配置
import re
import json
from urllib.parse import urlparse, parse_qs, unquote

# 读取你提供的节点文件
with open("decoded_links_5CD26D8E-F0E1-4488-8C90-1C2CA7138B4A.txt", "r", encoding="utf-8") as f:
    NODES_TEXT = f.read()

def parse_vless_link(link):
    """解析单个 vless 链接，返回 (tag, config_dict)"""
    if not link.startswith("vless://"):
        return None
    
    # 移除协议
    no_proto = link[8:]
    
    # 分离用户信息 @ 和其余部分
    at_pos = no_proto.find('@')
    if at_pos == -1:
        return None
    user_uuid = no_proto[:at_pos]
    rest = no_proto[at_pos+1:]
    
    # 分离 fragment（节点名称）
    fragment = ""
    if '#' in rest:
        rest, fragment = rest.split('#', 1)
        fragment = unquote(fragment)  # 解码中文名
    
    # 分离主机端口和查询参数
    if '?' in rest:
        host_part, query_part = rest.split('?', 1)
        query = parse_qs(query_part)
    else:
        host_part = rest
        query = {}
    
    # 解析主机和端口
    if ':' in host_part:
        server, server_port = host_part.split(':')
        server_port = int(server_port)
    else:
        server = host_part
        server_port = 443
    
    # 构建基础配置
    params = {
        "uuid": user_uuid,
        "server": server,
        "server_port": server_port,
    }
    
    # 处理加密方式
    if 'encryption' in query:
        params["encryption"] = query['encryption'][0]
    
    # 处理 TLS
    security = query.get('security', [''])[0]
    if security:
        params["tls"] = {"enabled": True, "insecure": False}
        # 处理 fingerprint
        if 'fp' in query:
            params["tls"]["utls"] = {"enabled": True, "fingerprint": query['fp'][0]}
        # 处理 sni 或 host
        sni = query.get('sni', [''])[0] or query.get('host', [''])[0]
        if sni:
            params["tls"]["server_name"] = sni
        # 处理 insecure
        if query.get('insecure', [''])[0] == '1':
            params["tls"]["insecure"] = True
    else:
        params["security"] = "none"
    
    # 处理传输方式
    transport_type = query.get('type', ['ws'])[0]
    if transport_type == 'ws':
        params["transport"] = {"type": "ws"}
        if 'path' in query:
            params["transport"]["path"] = query['path'][0]
        if 'host' in query:
            params["transport"]["headers"] = {"Host": query['host'][0]}
    elif transport_type == 'tcp':
        params["transport"] = {"type": "tcp"}
    
    # 处理 flow
    if 'flow' in query and query['flow'][0]:
        params["flow"] = query['flow'][0]
    
    # 生成标签
    tag = fragment if fragment else f"{server}:{server_port}"
    # 清理标签中的非法字符
    tag = re.sub(r'[^a-zA-Z0-9_\u4e00-\u9fa5\-]', '_', tag)
    
    return tag, params

def generate_config():
    print("🔄 开始解析节点...")
    lines = NODES_TEXT.strip().splitlines()
    outbounds = []
    tags = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # 只处理 vless 开头的行
        if not line.startswith("vless://"):
            continue
        parsed = parse_vless_link(line)
        if parsed:
            tag, params = parsed
            outbound = {"type": "vless", "tag": tag, **params}
            outbounds.append(outbound)
            tags.append(tag)
            print(f"  ✅ 已解析: {tag}")
        else:
            print(f"  ⚠️ 跳过无法解析的行: {line[:50]}...")
    
    if not outbounds:
        print("❌ 没有解析到任何有效节点，请检查文件格式！")
        return
    
    # 构建完整配置
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
                "type": "selector",
                "tag": "proxy-selector",
                "outbounds": tags,
                "default": tags[0] if tags else "hk1"
            }
        ],
        "route": {
            "rules": [
                {"outbound": "proxy-selector", "network": "tcp"}
            ]
        }
    }
    
    # 写入 config.json
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ config.json 已生成，共包含 {len(tags)} 个节点。")
    print(f"默认节点: {tags[0] if tags else '无'}")

if __name__ == "__main__":
    generate_config()
