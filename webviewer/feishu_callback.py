#!/usr/bin/env python3
"""
飞书审批回调处理器
处理飞书卡片按钮点击事件
"""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import sys

# 导入主服务器的数据管理器
sys.path.insert(0, str(Path(__file__).parent))
from server_with_approval import data_manager, Config

class FeishuCallbackHandler(BaseHTTPRequestHandler):
    """处理飞书回调"""
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        data = json.loads(body)
        
        # 解析回调数据
        challenge = data.get('challenge')
        if challenge:
            # URL 验证回调
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(str(challenge).encode())
            return
        
        # 处理卡片按钮点击
        header = data.get('header', {})
        event = data.get('event', {})
        action = event.get('action', {})
        value = json.loads(action.get('value', '{}'))
        
        action_type = value.get('type')
        approval_id = value.get('approval_id')
        
        if approval_id and action_type:
            if action_type == 'approve':
                success, result = data_manager.approve_access(approval_id)
                print(f"✅ 审批通过：{approval_id}")
            elif action_type == 'reject':
                success, result = data_manager.reject_access(approval_id)
                print(f"❌ 审批拒绝：{approval_id}")
        
        # 返回响应
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'code': 0}).encode())
    
    def log_message(self, format, *args):
        print(f"[Feishu Callback] {args[0]}")

def run_callback_server():
    port = 8889
    server = HTTPServer(('0.0.0.0', port), FeishuCallbackHandler)
    print(f"📬 飞书回调服务器已启动 (端口：{port})")
    server.serve_forever()

if __name__ == '__main__':
    run_callback_server()
