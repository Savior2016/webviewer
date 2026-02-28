#!/usr/bin/env python3
"""
web_server.py - momhand Web 展示服务
提供物品管理的 Web 界面和 API
"""

import http.server
import socketserver
import json
import os
import sys
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, "/root/.openclaw/workspace/momhand/skills")
from item_manager import manager

PORT = 8080
WEB_DIR = "/root/.openclaw/workspace/momhand/web"

class MomhandHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)
    
    def do_GET(self):
        parsed = urlparse(self.path)
        
        # API 路由
        if parsed.path.startswith("/api/"):
            self.handle_api(parsed)
        else:
            super().do_GET()
    
    def handle_api(self, parsed):
        """处理 API 请求"""
        path = parsed.path
        query = parse_qs(parsed.query)
        
        response = {"success": False, "data": None}
        
        try:
            if path == "/api/items":
                response["data"] = manager.get_all_items()
                response["success"] = True
            
            elif path == "/api/search":
                keyword = query.get("q", [""])[0]
                response["data"] = manager.search_items(keyword)
                response["success"] = True
            
            elif path == "/api/stats":
                response["data"] = manager.get_statistics()
                response["success"] = True
            
            elif path == "/api/expiring":
                days = int(query.get("days", [7])[0])
                response["data"] = manager.get_expiring_items(days)
                response["success"] = True
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode("utf-8"))
        
        except Exception as e:
            response["error"] = str(e)
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode("utf-8"))
    
    def log_message(self, format, *args):
        print(f"[momhand-web] {self.address_string()} - {format%args}")

class ReuseAddrServer(socketserver.TCPServer):
    allow_reuse_address = True

if __name__ == "__main__":
    httpd = ReuseAddrServer(("", PORT), MomhandHandler)
    print(f"🌐 momhand Web 服务已启动：http://localhost:{PORT}")
    print(f"📂 网站目录：{WEB_DIR}")
    print(f"🔗 API 地址：http://localhost:{PORT}/api/items")
    httpd.serve_forever()
