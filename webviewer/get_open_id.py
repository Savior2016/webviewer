#!/usr/bin/env python3
"""
获取飞书应用对应用户的 Open ID
使用方法：在飞书中给机器人发消息，查看日志中的 open_id
"""

import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

class FeishuEventHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        data = json.loads(body)
        
        print("=" * 60)
        print("收到飞书事件:")
        print(json.dumps(data, ensure_ascii=False, indent=2))
        print("=" * 60)
        
        # 提取 sender_id
        if 'event' in data and 'sender' in data['event']:
            sender = data['event']['sender']
            sender_id = sender.get('sender_id', {})
            open_id = sender_id.get('open_id', '')
            user_id = sender_id.get('user_id', '')
            union_id = sender_id.get('union_id', '')
            
            print(f"\n✅ 用户 ID 信息:")
            print(f"   open_id:  {open_id}")
            print(f"   user_id:  {user_id}")
            print(f"   union_id: {union_id}")
            print(f"\n请将 open_id 设置到环境变量:")
            print(f"   export FEISHU_USER_OPEN_ID=\"{open_id}\"")
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'code': 0}).encode())
    
    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    port = 8899
    print(f"📬 事件监听服务器已启动 (端口：{port})")
    print(f"📱 请在飞书中给机器人发送任意消息")
    print(f"📋 按 Ctrl+C 停止")
    HTTPServer(('0.0.0.0', port), FeishuEventHandler).serve_forever()
