#!/usr/bin/env python3
"""监听飞书事件，获取用户 Open ID"""
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        data = json.loads(self.rfile.read(length))
        print("\n" + "="*60)
        print(json.dumps(data, ensure_ascii=False, indent=2))
        print("="*60 + "\n")
        
        # 提取用户 ID
        event = data.get('event', {})
        sender = event.get('sender', {})
        ids = sender.get('sender_id', {})
        
        if ids:
            print("✅ 找到用户 ID:")
            print(f"   open_id:  {ids.get('open_id', '')}")
            print(f"   user_id:  {ids.get('user_id', '')}")
            print(f"   union_id: {ids.get('union_id', '')}")
            print("\n📋 请复制 open_id 并运行:")
            print(f'   export FEISHU_USER_OPEN_ID="{ids.get("open_id", "")}"')
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"code":0}')
    
    def log_message(self, format, *args): pass

print("📬 监听服务器已启动 (端口：8899)")
print("📱 请在飞书中给机器人发送任意消息")
print("📋 按 Ctrl+C 停止\n")
HTTPServer(('0.0.0.0', 8899), Handler).serve_forever()
