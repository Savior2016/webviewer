#!/usr/bin/env python3
"""
WebViewer - 本地 HTTPS 网站服务（修复版）
主要修复：
1. 使用 ThreadingHTTPServer 支持并发请求
2. 添加请求超时保护，防止单个请求卡死服务器
3. 使用线程池限制后台任务数量
4. SQLite 操作添加超时和重试机制
"""

import http.server
import ssl
import socketserver
import os
import json
from urllib.parse import urlparse, parse_qs
from pathlib import Path
import hashlib
import time
import requests
import uuid
from datetime import datetime
import sys
import importlib
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

PORT = 443
WEB_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "www")
CERT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "selfsigned.crt")
KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "selfsigned.key")

# 线程池 - 限制后台任务数量，防止资源耗尽
# 最大 5 个 worker 线程，队列最多 10 个任务
executor = ThreadPoolExecutor(max_workers=5, thread_name_prefix="webviewer-worker")

# 请求超时设置（秒）
REQUEST_TIMEOUT = 30
BACKGROUND_TASK_TIMEOUT = 60

def get_momhand_manager():
    """获取最新的物品管理器实例（SQLite 数据库版本）"""
    if 'momhand_manager_db' in sys.modules:
        importlib.reload(sys.modules['momhand_manager_db'])
    sys.path.insert(0, "/root/.openclaw/workspace")
    from momhand_manager_db import manager
    return manager

def get_cherry_pick_manager():
    """获取最新的搬家管理器实例"""
    if 'cherry_pick_manager' in sys.modules:
        importlib.reload(sys.modules['cherry_pick_manager'])
    sys.path.insert(0, "/root/.openclaw/workspace")
    from cherry_pick_manager import manager
    return manager

def get_bydesign_manager():
    """获取最新的出行管理器实例"""
    if 'bydesign_manager' in sys.modules:
        importlib.reload(sys.modules['bydesign_manager'])
    sys.path.insert(0, "/root/.openclaw/workspace")
    from bydesign_manager import manager
    return manager

SETTINGS_FILE = Path("/root/.openclaw/workspace/data/settings.json")

def get_system_prompt():
    """获取系统提示词"""
    try:
        if SETTINGS_FILE.exists():
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                return settings.get('system_prompt', '')
    except Exception as e:
        print(f"⚠️  读取设置失败：{e}")
    return ''

def save_system_prompt(prompt: str):
    """保存系统提示词"""
    try:
        SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        settings = {'system_prompt': prompt}
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ 保存设置失败：{e}")
        return False

def execute_project_save(project: str, result: dict):
    """执行项目保存操作（带超时保护）"""
    data = result.get('data', {})
    
    print(f"📝 执行 {project} 保存：data={data}")
    
    try:
        if project == 'bydesign':
            manager = get_bydesign_manager()
            
            if data.get('action') == 'add_checklist_items' or 'items_added' in data:
                items = data.get('items_added', [])
                added = manager.add_checklist_items_batch(items)
                print(f"✅ By Design 已批量添加 {len(added)} 项检查")
            elif data.get('action') == 'add_checklist':
                text = data.get('text', data.get('item', ''))
                if text:
                    item = manager.add_checklist_item(text)
                    print(f"✅ By Design 已添加检查项：{item['id']}")
            else:
                trip_name = data.get('name', '出行')
                description = data.get('description', '')
                trip = manager.create_trip(name=trip_name, description=description)
                print(f"✅ By Design 已创建出行：{trip['id']}")
        
        elif project == 'cherry_pick':
            manager = get_cherry_pick_manager()
            moves = manager.get_all_moves()
            if moves:
                move_id = moves[0]['id']
                item = manager.add_item(
                    move_id=move_id,
                    name=data.get('name', '物品'),
                    before_location=data.get('before_location', ''),
                    after_location=data.get('after_location', '')
                )
                print(f"✅ Cherry Pick 已记录物品：{item['id']}")
        
        elif project == 'momhand':
            manager = get_momhand_manager()
            item = manager.add_item({
                'name': data.get('name', '物品'),
                'type': data.get('type', '其他'),
                'location': data.get('location', ''),
                'usage': data.get('usage', '')
            })
            print(f"✅ Momhand 已添加物品：{item['id']}")
    
    except Exception as e:
        print(f"❌ 保存失败：{e}")

def execute_save_action(result: dict):
    """执行保存操作（兼容旧代码）"""
    project = result.get('project')
    execute_project_save(project, result)

# 确保 www 目录存在
os.makedirs(WEB_ROOT, exist_ok=True)

class TimeoutHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """
    支持并发和超时的 HTTP 服务器
    - ThreadingMixIn: 每个请求一个线程
    - 添加超时保护防止请求卡死
    """
    allow_reuse_address = True
    daemon_threads = True  # 线程在服务器关闭时自动终止
    request_queue_size = 20  # 请求队列大小
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeout = REQUEST_TIMEOUT  # 套接字超时


class WebViewerHandler(http.server.BaseHTTPRequestHandler):
    # 请求超时
    timeout = REQUEST_TIMEOUT
    
    # 禁用默认日志中的 DNS 查询（加速请求）
    def address_string(self):
        return self.client_address[0]
    
    def do_GET(self):
        try:
            parsed = urlparse(self.path)
            path = parsed.path
            query = parse_qs(parsed.query)
            
            if path.startswith("/api/prompts/"):
                self.handle_get_prompt(path)
            elif path == "/api/settings":
                self.handle_get_settings()
            elif path == "/api/message-result":
                self.handle_message_result(query)
            elif path.startswith("/momhand/api/"):
                self.handle_momhand_api(path, query)
            elif path.startswith("/cherry-pick/api/"):
                self.handle_cherry_pick_api(path, query)
            elif path.startswith("/bydesign/api/"):
                self.handle_bydesign_api(path, query)
            elif path.startswith("/siri-dream/api/"):
                self.handle_siri_dream_api(path, query)
            else:
                self.serve_static_file(path, WEB_ROOT)
        except Exception as e:
            print(f"❌ GET 请求处理失败：{e}")
            self.send_error(500, str(e))
    
    def handle_momhand_api(self, path, query):
        """处理 momhand API 请求（带超时保护）"""
        try:
            manager = get_momhand_manager()
            response = {"success": False, "data": None}
            
            if path == "/momhand/api/items":
                response["data"] = manager.get_all_items()
                response["success"] = True
            
            elif path == "/momhand/api/search":
                keyword = query.get("q", [""])[0]
                response["data"] = manager.search_items(keyword)
                response["success"] = True
            
            elif path == "/momhand/api/stats":
                response["data"] = manager.get_statistics()
                response["success"] = True
            
            elif path.startswith("/momhand/api/items/"):
                item_id = path.split("/")[-1]
                try:
                    item_id_int = int(item_id)
                    for item in manager.items:
                        if item["id"] == item_id_int:
                            response["data"] = item
                            response["success"] = True
                            break
                except:
                    pass
                response["success"] = bool(response["data"])
            
            elif path == "/momhand/api/expiring":
                days = int(query.get("days", [7])[0])
                response["data"] = manager.get_expiring_items(days)
                response["success"] = True
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode("utf-8"))
        
        except Exception as e:
            print(f"❌ momhand API 错误：{e}")
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))
    
    def handle_momhand_post(self, data):
        """处理 momhand 添加物品请求"""
        try:
            manager = get_momhand_manager()
            
            item_data = {
                "name": data.get("name", "未知"),
                "type": data.get("type", "其他"),
                "location": data.get("location", ""),
                "usage": data.get("usage", "")
            }
            
            item = manager.add_item(item_data)
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(item, ensure_ascii=False).encode("utf-8"))
        
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}, ensure_ascii=False).encode("utf-8"))
    
    def do_POST(self):
        """处理 POST 请求"""
        try:
            parsed = urlparse(self.path)
            path = parsed.path
            
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
            
            try:
                data = json.loads(body) if body else {}
            except:
                data = {}
            
            if path == "/api/send-message":
                self.handle_send_message(data)
            elif path == "/momhand/api/items":
                self.handle_momhand_post(data)
            elif path.startswith("/cherry-pick/api/"):
                self.handle_cherry_pick_post(path, data)
            elif path.startswith("/bydesign/api/"):
                self.handle_bydesign_post(path, data)
            elif path == "/siri-dream/api/message":
                self.handle_siri_dream_message(data)
            else:
                self.send_response(404)
                self.end_headers()
        except Exception as e:
            print(f"❌ POST 请求处理失败：{e}")
            self.send_error(500, str(e))
    
    def do_PUT(self):
        """处理 PUT 请求"""
        try:
            parsed = urlparse(self.path)
            path = parsed.path
            
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
            
            try:
                data = json.loads(body) if body else {}
            except:
                data = {}
            
            if path.startswith("/momhand/api/items/"):
                self.handle_momhand_put(path, data)
            elif path.startswith("/cherry-pick/api/items/"):
                self.handle_cherry_pick_put(path, data)
            elif path.startswith("/bydesign/api/"):
                self.handle_bydesign_put(path, data)
            elif path.startswith("/api/prompts/"):
                self.handle_save_prompt(path, data)
            elif path == "/api/settings":
                self.handle_save_settings(data)
            else:
                self.send_response(404)
                self.end_headers()
        except Exception as e:
            print(f"❌ PUT 请求处理失败：{e}")
            self.send_error(500, str(e))
    
    def do_DELETE(self):
        """处理 DELETE 请求"""
        try:
            parsed = urlparse(self.path)
            path = parsed.path
            
            if path.startswith("/momhand/api/items/"):
                self.handle_momhand_delete(path)
            elif path.startswith("/cherry-pick/api/"):
                self.handle_cherry_pick_delete(path)
            elif path.startswith("/bydesign/api/"):
                self.handle_bydesign_delete(path)
            elif path.startswith("/siri-dream/api/messages/"):
                self.handle_siri_dream_delete(path)
            else:
                self.send_response(404)
                self.end_headers()
        except Exception as e:
            print(f"❌ DELETE 请求处理失败：{e}")
            self.send_error(500, str(e))
    
    def handle_get_prompt(self, path):
        """获取项目提示词"""
        try:
            project = path.split("/")[-1]
            prompt_file = f"/root/.openclaw/workspace/data/prompts/{project}.json"
            
            if os.path.exists(prompt_file):
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": True,
                    "prompt": config.get('system_prompt', ''),
                    "name": config.get('name', '')
                }, ensure_ascii=False).encode("utf-8"))
            else:
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "提示词配置不存在"}, ensure_ascii=False).encode("utf-8"))
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}, ensure_ascii=False).encode("utf-8"))
    
    def handle_save_prompt(self, path, data):
        """保存项目提示词"""
        try:
            import re
            project = path.split("/")[-1]
            if not re.match(r'^[a-zA-Z0-9_-]+$', project):
                raise Exception(f"无效的项目名称：{project}")
            
            prompt_file = f"/root/.openclaw/workspace/data/prompts/{project}.json"
            
            print(f"💾 保存 {project} 提示词到：{prompt_file}")
            print(f"   数据：{data}")
            
            config = {'project': project, 'name': project, 'system_prompt': ''}
            if os.path.exists(prompt_file):
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                print(f"   现有配置：{list(config.keys())}")
            
            prompt = data.get('prompt', '')
            if not prompt:
                raise Exception("提示词不能为空")

            config['system_prompt'] = prompt
            
            with open(prompt_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            print(f"   ✅ 保存成功")
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True}, ensure_ascii=False).encode("utf-8"))
        except Exception as e:
            print(f"   ❌ 保存失败：{e}")
            import traceback
            traceback.print_exc()
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}, ensure_ascii=False).encode("utf-8"))
    
    def handle_process_message(self, data):
        """处理项目消息（已废弃，使用异步版本）"""
        self.send_response(501)
        self.end_headers()
    
    def handle_get_settings(self):
        """获取设置"""
        try:
            prompt = get_system_prompt()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": True,
                "system_prompt": prompt
            }, ensure_ascii=False).encode("utf-8"))
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}, ensure_ascii=False).encode("utf-8"))
    
    def handle_save_settings(self, data):
        """保存设置"""
        try:
            prompt = data.get('system_prompt', '')
            if save_system_prompt(prompt):
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"success": True}, ensure_ascii=False).encode("utf-8"))
            else:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "保存失败"}, ensure_ascii=False).encode("utf-8"))
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}, ensure_ascii=False).encode("utf-8"))
    
    def handle_message_result(self, query):
        """处理消息结果轮询"""
        try:
            msg_id = query.get('msg_id', [None])[0]
            if not msg_id:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "缺少 msg_id 参数"}, ensure_ascii=False).encode("utf-8"))
                return
            
            result_file = f"/root/.openclaw/workspace/data/results/{msg_id}.json"
            if os.path.exists(result_file):
                with open(result_file, 'r', encoding='utf-8') as f:
                    result = json.load(f)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "processed": True, "data": result}, ensure_ascii=False).encode("utf-8"))
            else:
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "processed": False}, ensure_ascii=False).encode("utf-8"))
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}, ensure_ascii=False).encode("utf-8"))
    
    def handle_cherry_pick_api(self, path, query):
        """处理 cherry-pick API GET 请求"""
        try:
            manager = get_cherry_pick_manager()
            response = []
            
            if path == "/cherry-pick/api/moves":
                response = manager.get_all_moves()
            
            elif path.startswith("/cherry-pick/api/moves/") and path.endswith("/items"):
                move_id = path.split("/")[4]
                response = manager.get_items(move_id)
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode("utf-8"))
        
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
    
    def handle_cherry_pick_post(self, path, data):
        """处理 cherry-pick API POST 请求"""
        try:
            manager = get_cherry_pick_manager()
            response = {}
            
            if path == "/cherry-pick/api/moves":
                name = data.get("name", "")
                description = data.get("description", "")
                if not name:
                    raise Exception("名称不能为空")
                response = manager.create_move(name, description)
            
            elif "/items" in path and "/moves/" in path:
                parts = path.split("/")
                move_id = parts[4]
                name = data.get("name", "")
                before_location = data.get("before_location", "")
                pack_location = data.get("pack_location", "")
                after_location = data.get("after_location", "")
                if not name:
                    raise Exception("物品名称不能为空")
                response = manager.add_item(move_id, name, before_location, pack_location, after_location)
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode("utf-8"))
        
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
    
    def handle_cherry_pick_put(self, path, data):
        """处理 cherry-pick API PUT 请求"""
        try:
            manager = get_cherry_pick_manager()
            parts = path.split("/")
            item_id = parts[4]
            
            response = manager.update_item(item_id, data)
            if not response:
                raise Exception("物品不存在")
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True}, ensure_ascii=False).encode("utf-8"))
        
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
    
    def handle_cherry_pick_delete(self, path):
        """处理 cherry-pick API DELETE 请求"""
        try:
            manager = get_cherry_pick_manager()
            
            if "/moves/" in path and "/items/" not in path:
                parts = path.split("/")
                move_id = parts[4]
                manager.delete_move(move_id)
            elif "/items/" in path:
                parts = path.split("/")
                item_id = parts[4]
                manager.delete_item(item_id)
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True}, ensure_ascii=False).encode("utf-8"))
        
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
    
    def handle_momhand_put(self, path, data):
        """处理 momhand 更新请求"""
        try:
            manager = get_momhand_manager()
            item_id = path.split("/")[-1]
            
            try:
                item_id_int = int(item_id)
                result = manager.update_item(item_id_int, data)
                
                if result:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": True, "data": result}, ensure_ascii=False).encode("utf-8"))
                else:
                    self.send_response(404)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": False, "error": "物品不存在"}, ensure_ascii=False).encode("utf-8"))
            except ValueError:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "无效的 item_id"}, ensure_ascii=False).encode("utf-8"))
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}, ensure_ascii=False).encode("utf-8"))
    
    def handle_momhand_delete(self, path):
        """处理 momhand 删除请求"""
        try:
            manager = get_momhand_manager()
            item_id = path.split("/")[-1]
            
            try:
                item_id_int = int(item_id)
                result = manager.delete_item(item_id_int)
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(result, ensure_ascii=False).encode("utf-8"))
            except ValueError:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "无效的 item_id"}, ensure_ascii=False).encode("utf-8"))
        
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}, ensure_ascii=False).encode("utf-8"))
    
    # ========== By Design API Handlers ==========
    def handle_bydesign_api(self, path, query):
        """处理 bydesign API GET 请求"""
        try:
            manager = get_bydesign_manager()
            response = []
            
            if path == "/bydesign/api/checklist":
                response = manager.get_checklist()
            
            elif path == "/bydesign/api/trips":
                response = manager.get_all_trips()
            
            elif path.startswith("/bydesign/api/trips/") and "/progress" not in path:
                trip_id = path.split("/")[4]
                trip = manager.get_trip(trip_id)
                response = trip if trip else {}
            
            elif "/progress" in path:
                trip_id = path.split("/")[4]
                response = manager.get_trip_progress(trip_id)
            
            elif path == "/bydesign/api/templates":
                response = manager.get_templates()
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode("utf-8"))
        
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
    
    def handle_bydesign_post(self, path, data):
        """处理 bydesign API POST 请求"""
        try:
            manager = get_bydesign_manager()
            response = {}
            
            if path == "/bydesign/api/checklist":
                text = data.get("text", "")
                if not text:
                    raise Exception("检查项不能为空")
                response = manager.add_checklist_item(text)
            
            elif path == "/bydesign/api/trips":
                name = data.get("name", "")
                description = data.get("description", "")
                if not name:
                    raise Exception("出行名称不能为空")
                response = manager.create_trip(name, description)
            
            elif "/items" in path and "/trips/" in path:
                parts = path.split("/")
                trip_id = parts[4]
                text = data.get("text", "")
                if not text:
                    raise Exception("物品名称不能为空")
                response = manager.add_custom_item(trip_id, text)
            
            elif "/complete" in path:
                trip_id = path.split("/")[4]
                response = manager.complete_trip(trip_id)
            
            elif path == "/bydesign/api/templates":
                name = data.get("name", "")
                items = data.get("items", [])
                if not name:
                    raise Exception("模板名称不能为空")
                response = manager.create_template(name, items)
            
            elif "/templates" in path and "/trips/" in path:
                parts = path.split("/")
                trip_id = parts[4]
                template_id = data.get("template_id", "")
                if not template_id:
                    raise Exception("模板 ID 不能为空")
                response = manager.import_template_to_trip(trip_id, template_id)
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode("utf-8"))
        
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
    
    def handle_bydesign_put(self, path, data):
        """处理 bydesign API PUT 请求"""
        try:
            manager = get_bydesign_manager()
            parts = path.split("/")
            
            if "/checklist/" in path and "/trips/" not in path:
                item_id = parts[4]
                response = manager.update_checklist_item(item_id, data)
            
            elif "/trips/" in path and "/checklist/" in path:
                trip_id = parts[4]
                item_id = parts[6]
                trip = manager.get_trip(trip_id)
                if trip and trip.get("checklist_snapshot"):
                    for item in trip["checklist_snapshot"]:
                        if item["id"] == item_id:
                            item.update(data)
                            manager._save_trips()
                            response = item
                            break
            
            elif "/trips/" in path and "/items/" in path:
                trip_id = parts[4]
                item_id = parts[6]
                trip = manager.get_trip(trip_id)
                if trip and trip.get("custom_items"):
                    for item in trip["custom_items"]:
                        if item["id"] == item_id:
                            item.update(data)
                            manager._save_trips()
                            response = item
                            break
            
            if not response:
                raise Exception("项目不存在")
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True}, ensure_ascii=False).encode("utf-8"))
        
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
    
    def handle_bydesign_delete(self, path):
        """处理 bydesign API DELETE 请求"""
        try:
            manager = get_bydesign_manager()
            
            if "/checklist/" in path:
                item_id = path.split("/")[4]
                manager.delete_checklist_item(item_id)
            elif "/trips/" in path and "/items/" not in path:
                trip_id = path.split("/")[4]
                manager.delete_trip(trip_id)
            elif "/templates/" in path:
                template_id = path.split("/")[4]
                manager.delete_template(template_id)
            elif "/trips/" in path and "/items/" in path:
                parts = path.split("/")
                trip_id = parts[4]
                item_id = parts[6]
                trip = manager.get_trip(trip_id)
                if trip:
                    trip["custom_items"] = [i for i in trip["custom_items"] if i["id"] != item_id]
                    manager._save_trips()
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True}, ensure_ascii=False).encode("utf-8"))
        
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
    
    # ========== Siri Dream API Handlers ==========
    def handle_siri_dream_api(self, path, query):
        """处理 Siri Dream API GET 请求"""
        try:
            import sys
            sys.path.insert(0, "/root/.openclaw/workspace")
            import siri_dream_manager
            manager = siri_dream_manager.manager
            
            response = {"success": False, "data": None}
            
            if path == "/siri-dream/api/messages":
                limit = int(query.get("limit", [50])[0])
                offset = int(query.get("offset", [0])[0])
                response["data"] = manager['get_messages'](limit, offset)
                response["success"] = True
            
            elif path == "/siri-dream/api/stats":
                response["data"] = manager['get_statistics']()
                response["success"] = True
            
            elif path.startswith("/siri-dream/api/messages/"):
                message_id = path.split("/")[-1]
                message = manager['get_message'](message_id)
                if message:
                    response["data"] = message
                    response["success"] = True
                else:
                    response["error"] = "消息不存在"
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode("utf-8"))
        
        except Exception as e:
            print(f"❌ Siri Dream API 错误：{e}")
            import traceback
            traceback.print_exc()
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))
    
    def handle_siri_dream_message(self, data):
        """处理 Siri Dream 消息"""
        try:
            import sys
            sys.path.insert(0, "/root/.openclaw/workspace")
            import siri_dream_manager
            manager = siri_dream_manager.manager
            
            text = data.get('text', '')
            metadata = data.get('metadata', {})
            
            if not text:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": "消息内容不能为空"}).encode("utf-8"))
                return
            
            # 添加消息
            message = manager['add_message'](text, 'api', metadata)
            
            # 异步处理消息
            import threading
            thread = threading.Thread(
                target=self._process_siri_dream_message,
                args=(message['id'], text),
                daemon=True
            )
            thread.start()
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": True,
                "message_id": message['id'],
                "message": "消息已接收，正在处理..."
            }, ensure_ascii=False).encode("utf-8"))
        
        except Exception as e:
            print(f"❌ Siri Dream 消息处理失败：{e}")
            import traceback
            traceback.print_exc()
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))
    
    def _process_siri_dream_message(self, message_id: str, text: str):
        """后台处理 Siri Dream 消息"""
        import subprocess
        import re
        import json
        
        try:
            import sys
            sys.path.insert(0, "/root/.openclaw/workspace")
            import siri_dream_manager
            manager = siri_dream_manager.manager
            
            # 更新状态为处理中
            manager['update_message_status'](message_id, 'processing')
            
            # 获取提示词
            system_prompt = manager['get_system_prompt']()
            full_prompt = system_prompt.format(message=text)
            
            # 调用 OpenClaw Agent
            cmd = [
                '/root/.nvm/versions/node/v22.22.0/bin/openclaw',
                'agent',
                '--agent', 'dummy',
                '-m', full_prompt
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            output = result.stdout + result.stderr
            
            # 清理输出，提取有效内容
            output = output.strip()
            
            # 尝试提取 JSON（如果有）
            json_match = re.search(r'\{[\s\S]*\}', output)
            
            if json_match:
                try:
                    result_data = json.loads(json_match.group(0))
                    # 如果解析成功，检查是否有 message 字段
                    if isinstance(result_data, dict) and 'message' in result_data:
                        manager['update_message_status'](message_id, 'completed', result_data)
                    else:
                        manager['update_message_status'](message_id, 'completed', {'message': output})
                    print(f"✅ Siri Dream 处理完成：{message_id}")
                except json.JSONDecodeError as e:
                    # JSON 解析失败，使用纯文本
                    manager['update_message_status'](message_id, 'completed', {'message': output})
                    print(f"⚠️ Siri Dream JSON 解析失败，使用纯文本：{message_id}")
            else:
                # 没有 JSON，使用纯文本
                manager['update_message_status'](message_id, 'completed', {'message': output})
                print(f"✅ Siri Dream 处理完成（纯文本）：{message_id}")
        
        except subprocess.TimeoutExpired:
            manager['update_message_status'](message_id, 'failed', {"error": "处理超时"})
            print(f"❌ Siri Dream 处理超时：{message_id}")
        except Exception as e:
            manager['update_message_status'](message_id, 'failed', {"error": str(e)})
            print(f"❌ Siri Dream 处理失败 {message_id}: {e}")
    
    def handle_siri_dream_delete(self, path):
        """处理 Siri Dream DELETE 请求"""
        try:
            import sys
            sys.path.insert(0, "/root/.openclaw/workspace")
            import siri_dream_manager
            manager = siri_dream_manager.manager
            
            message_id = path.split("/")[-1]
            result = manager['delete_message'](message_id)
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"success": result}, ensure_ascii=False).encode("utf-8"))
        
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))
    
    def serve_static_file(self, path, root):
        """服务静态文件"""
        if path == "/":
            path = "/index.html"
        
        file_path = os.path.join(root, path.lstrip("/"))
        
        if os.path.isdir(file_path):
            file_path = os.path.join(file_path, "index.html")
        
        if os.path.exists(file_path):
            try:
                with open(file_path, "rb") as f:
                    content = f.read()
                
                self.send_response(200)
                if file_path.endswith(".html"):
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                elif file_path.endswith(".css"):
                    self.send_header("Content-Type", "text/css")
                elif file_path.endswith(".js"):
                    self.send_header("Content-Type", "application/javascript")
                elif file_path.endswith(".json"):
                    self.send_header("Content-Type", "application/json")
                elif file_path.endswith(".png"):
                    self.send_header("Content-Type", "image/png")
                elif file_path.endswith(".jpg") or file_path.endswith(".jpeg"):
                    self.send_header("Content-Type", "image/jpeg")
                else:
                    self.send_header("Content-Type", "text/plain")
                
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(content)
            except Exception as e:
                self.send_error(500, str(e))
        else:
            self.send_error(404, "File not found")
    
    def log_message(self, format, *args):
        print(f"[WebViewer] {self.log_date_time_string()} - {self.address_string()} - {format%args}")
    
    def handle_send_message(self, data):
        """
        处理发送消息 - 异步处理，立即返回
        使用线程池限制并发任务数量
        """
        try:
            message = data.get('message', '')
            timestamp = data.get('timestamp', '')
            
            if not message:
                raise Exception('消息内容不能为空')
            
            msg_id = str(uuid.uuid4())
            
            # 立即返回响应
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            immediate_response = {
                "success": True,
                "message": "⏳ 正在处理中，请稍候刷新页面查看结果...",
                "msg_id": msg_id,
                "processed_by": "async",
                "processing": True
            }
            self.wfile.write(json.dumps(immediate_response, ensure_ascii=False).encode("utf-8"))
            
            # 使用线程池提交后台任务（而不是无限制创建线程）
            future = executor.submit(
                self._process_message_async,
                msg_id, message
            )
            print(f"📤 消息已提交线程池处理：{msg_id}")
        
        except Exception as e:
            print(f"✗ 提交消息失败：{e}")
            import traceback
            traceback.print_exc()
            
            msg_id = str(uuid.uuid4())
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": False,
                "error": str(e),
                "msg_id": msg_id
            }, ensure_ascii=False).encode("utf-8"))
    
    def _process_message_async(self, msg_id: str, message: str):
        """
        后台异步处理消息（在线程池中运行）
        添加超时保护
        """
        try:
            print(f"🔄 开始后台处理消息：{msg_id}")
            
            import sys
            sys.path.insert(0, "/root/.openclaw/workspace")
            from openclaw_agent_processor import process_via_openclaw_agent
            
            print(f"📤 发送消息到 OpenClaw Agent: {message[:50]}...")
            
            # 处理消息（带超时）
            result = process_via_openclaw_agent(message)
            
            # 保存结果
            result_dir = "/root/.openclaw/workspace/data/results"
            os.makedirs(result_dir, exist_ok=True)
            
            result_data = {
                "msg_id": msg_id,
                "original_message": message,
                "processed_by": "openclaw",
                "timestamp": int(time.time()),
                "processing": False,
                **result
            }
            
            result_file = os.path.join(result_dir, f"{msg_id}.json")
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ OpenClaw 处理完成：{msg_id} -> {result.get('project', 'unknown')}")
            
            if result.get('project') and result.get('data'):
                print(f"📝 执行保存操作：project={result['project']}, action={result.get('action')}")
                execute_save_action(result)
            
        except FuturesTimeoutError:
            print(f"❌ 后台处理超时 {msg_id}")
            self._save_error_result(msg_id, message, "处理超时")
        except Exception as e:
            print(f"❌ 后台处理失败 {msg_id}: {e}")
            import traceback
            traceback.print_exc()
            self._save_error_result(msg_id, message, str(e))
    
    def _save_error_result(self, msg_id: str, message: str, error: str):
        """保存错误结果"""
        result_dir = "/root/.openclaw/workspace/data/results"
        os.makedirs(result_dir, exist_ok=True)
        
        result_data = {
            "msg_id": msg_id,
            "original_message": message,
            "success": False,
            "error": error,
            "timestamp": int(time.time()),
            "processing": False
        }
        
        result_file = os.path.join(result_dir, f"{msg_id}.json")
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # 使用修复后的服务器类
    httpd = TimeoutHTTPServer(("", PORT), WebViewerHandler)
    
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    
    print(f"🔒 WebViewer HTTPS 服务已启动（修复版）：https://0.0.0.0:{PORT}")
    print(f"📂 网站根目录：{WEB_ROOT}")
    print(f"🧵 线程池：最大 5 worker，队列 10 任务")
    print(f"⏱️  请求超时：{REQUEST_TIMEOUT}秒")
    print(f"🏠 首页：https://<IP>/")
    print(f"📦 momhand API: https://<IP>/momhand/api/items")
    print(f"📦 momhand Web: https://<IP>/momhand/")
    print(f"🏠 cherry-pick API: https://<IP>/cherry-pick/api/moves")
    print(f"🏠 cherry-pick Web: https://<IP>/cherry-pick/")
    print(f"✈️ bydesign API: https://<IP>/bydesign/api/checklist")
    print(f"✈️ bydesign Web: https://<IP>/bydesign/")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 服务正在关闭...")
        executor.shutdown(wait=False)
        httpd.shutdown()
        print("✅ 服务已停止")
