#!/usr/bin/env python3
"""
WebViewer 增强版服务器
功能：
- 账号密码登录认证
- 访问审批系统
- 增强访问审计（记录详细信息）
- 实时飞书通知
- 审计日志查看页面
"""

import json
import os
import time
import uuid
import hashlib
import socket
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse, urlencode
import threading
import requests
import ssl

# ==================== 配置 ====================

class Config:
    # 服务器配置
    HOST = '0.0.0.0'
    HTTPS_PORT = 443
    
    # 飞书配置（从环境变量读取）
    FEISHU_APP_ID = os.getenv('FEISHU_APP_ID', '')
    FEISHU_APP_SECRET = os.getenv('FEISHU_APP_SECRET', '')
    FEISHU_USER_OPEN_ID = os.getenv('FEISHU_USER_OPEN_ID', '')
    
    # 会话配置
    SESSION_TIMEOUT_HOURS = 24
    PENDING_TIMEOUT_MINUTES = 30
    ADMIN_SESSION_TIMEOUT_HOURS = 12  # 管理员登录会话有效期
    
    # 数据目录
    DATA_DIR = Path('/root/.openclaw/workspace/webviewer/data')
    WWW_DIR = Path('/root/.openclaw/workspace/www')
    
    # 日志文件
    ACCESS_LOG_FILE = DATA_DIR / 'access_log.jsonl'
    AUDIT_LOG_FILE = DATA_DIR / 'audit_log.jsonl'
    PENDING_APPROVALS_FILE = DATA_DIR / 'pending_approvals.json'
    APPROVED_SESSIONS_FILE = DATA_DIR / 'approved_sessions.json'
    ADMIN_SESSIONS_FILE = DATA_DIR / 'admin_sessions.json'
    
    # 配置文件
    CONFIG_FILE = Path('/root/.openclaw/workspace/webviewer/config.json')
    
    # 白名单 IP（启动时加载）
    WHITELIST_IPS = ['127.0.0.1', '::1']  # 默认包含本地地址
    
    @staticmethod
    def load_whitelist():
        """从 config.json 加载白名单"""
        try:
            if Config.CONFIG_FILE.exists():
                with open(Config.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    whitelist = config.get('whitelist_ips', [])
                    # 添加本地地址
                    whitelist.extend(['127.0.0.1', '::1'])
                    return whitelist
        except:
            pass
        return ['127.0.0.1', '::1']
    
    # 加载配置
    @staticmethod
    def load_config():
        try:
            if Config.CONFIG_FILE.exists():
                with open(Config.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {}

# ==================== 数据管理 ====================

class DataManager:
    """管理访问日志、审批状态和管理员会话"""
    
    def __init__(self):
        self.data_dir = Config.DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载白名单
        Config.WHITELIST_IPS = Config.load_whitelist()
        
        # 文件路径
        self.pending_file = Config.PENDING_APPROVALS_FILE
        self.sessions_file = Config.APPROVED_SESSIONS_FILE
        self.admin_sessions_file = Config.ADMIN_SESSIONS_FILE
        self.access_log_file = Config.ACCESS_LOG_FILE
        self.audit_log_file = Config.AUDIT_LOG_FILE
        
        # 加载数据
        self.pending_approvals = self._load_json(self.pending_file, {})
        self.approved_sessions = self._load_json(self.sessions_file, {})
        self.admin_sessions = self._load_json(self.admin_sessions_file, {})
        
        # 清理过期数据
        self._cleanup_expired()
    
    def _load_json(self, filepath, default):
        try:
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return default
    
    def _save_json(self, filepath, data):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _cleanup_expired(self):
        """清理过期的会话"""
        now = time.time()
        session_timeout = now - (Config.SESSION_TIMEOUT_HOURS * 3600)
        admin_timeout = now - (Config.ADMIN_SESSION_TIMEOUT_HOURS * 3600)
        pending_timeout = now - (Config.PENDING_TIMEOUT_MINUTES * 60)
        
        # 清理过期会话
        self.approved_sessions = {
            k: v for k, v in self.approved_sessions.items()
            if v.get('expires_at', 0) > session_timeout
        }
        
        # 清理过期管理员会话
        self.admin_sessions = {
            k: v for k, v in self.admin_sessions.items()
            if v.get('expires_at', 0) > admin_timeout
        }
        
        # 清理过期待审批
        self.pending_approvals = {
            k: v for k, v in self.pending_approvals.items()
            if v.get('timestamp', 0) > pending_timeout
        }
        
        self._save_json(self.sessions_file, self.approved_sessions)
        self._save_json(self.admin_sessions_file, self.admin_sessions)
        self._save_json(self.pending_file, self.pending_approvals)
    
    def log_access(self, visitor_info):
        """记录访问日志（简化版）"""
        log_entry = {
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat(),
            **visitor_info
        }
        
        with open(self.access_log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def log_audit(self, audit_info):
        """记录审计日志（详细版）"""
        audit_entry = {
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat(),
            'event_type': audit_info.get('event_type', 'unknown'),
            'ip': audit_info.get('ip', 'Unknown'),
            'user_agent': audit_info.get('user_agent', 'Unknown'),
            'path': audit_info.get('path', '/'),
            'method': audit_info.get('method', 'GET'),
            'referer': audit_info.get('referer', ''),
            'language': audit_info.get('language', ''),
            'platform': audit_info.get('platform', ''),
            'browser': audit_info.get('browser', ''),
            'screen_resolution': audit_info.get('screen_resolution', ''),
            'timezone': audit_info.get('timezone', ''),
            'location': audit_info.get('location', 'Unknown'),
            'status': audit_info.get('status', 'unknown'),
            'session_id': audit_info.get('session_id', ''),
            'extra': audit_info.get('extra', {})
        }
        
        with open(self.audit_log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(audit_entry, ensure_ascii=False) + '\n')
        
        return audit_entry
    
    def create_pending_approval(self, visitor_info):
        """创建待审批记录"""
        approval_id = str(uuid.uuid4())
        verification_code = hashlib.md5(approval_id.encode()).hexdigest()[:6].upper()
        
        self.pending_approvals[approval_id] = {
            'approval_id': approval_id,
            'verification_code': verification_code,
            'visitor_info': visitor_info,
            'timestamp': time.time(),
            'status': 'pending'
        }
        
        self._save_json(self.pending_file, self.pending_approvals)
        return self.pending_approvals[approval_id]
    
    def approve_access(self, approval_id):
        """审批通过"""
        if approval_id not in self.pending_approvals:
            return False, 'Approval not found'
        
        record = self.pending_approvals[approval_id]
        visitor_info = record['visitor_info']
        
        session_id = str(uuid.uuid4())
        self.approved_sessions[session_id] = {
            'session_id': session_id,
            'ip': visitor_info.get('ip'),
            'approved_at': time.time(),
            'expires_at': time.time() + (Config.SESSION_TIMEOUT_HOURS * 3600),
            'approval_id': approval_id
        }
        
        record['status'] = 'approved'
        record['session_id'] = session_id
        self._save_json(self.pending_file, self.pending_approvals)
        self._save_json(self.sessions_file, self.approved_sessions)
        
        return True, session_id
    
    def reject_access(self, approval_id):
        """拒绝访问"""
        if approval_id not in self.pending_approvals:
            return False, 'Approval not found'
        
        self.pending_approvals[approval_id]['status'] = 'rejected'
        self._save_json(self.pending_file, self.pending_approvals)
        return True, 'Rejected'
    
    def check_session(self, session_id):
        """检查访问会话是否有效"""
        if session_id not in self.approved_sessions:
            return False
        
        session = self.approved_sessions[session_id]
        if session['expires_at'] < time.time():
            del self.approved_sessions[session_id]
            self._save_json(self.sessions_file, self.approved_sessions)
            return False
        
        return True
    
    def verify_admin_login(self, username, password):
        """验证管理员登录"""
        config = Config.load_config()
        admin_config = config.get('admin', {})
        
        stored_username = admin_config.get('username', '')
        stored_hash = admin_config.get('password_hash', '')
        
        # 计算密码哈希
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if username == stored_username and password_hash == stored_hash:
            return True
        return False
    
    def create_admin_session(self, username, ip):
        """创建管理员会话"""
        session_id = str(uuid.uuid4())
        self.admin_sessions[session_id] = {
            'session_id': session_id,
            'username': username,
            'ip': ip,
            'login_at': time.time(),
            'expires_at': time.time() + (Config.ADMIN_SESSION_TIMEOUT_HOURS * 3600)
        }
        self._save_json(self.admin_sessions_file, self.admin_sessions)
        return session_id
    
    def check_admin_session(self, session_id):
        """检查管理员会话是否有效"""
        if session_id not in self.admin_sessions:
            return False
        
        session = self.admin_sessions[session_id]
        if session['expires_at'] < time.time():
            del self.admin_sessions[session_id]
            self._save_json(self.admin_sessions_file, self.admin_sessions)
            return False
        
        return True
    
    def logout_admin(self, session_id):
        """管理员登出"""
        if session_id in self.admin_sessions:
            del self.admin_sessions[session_id]
            self._save_json(self.admin_sessions_file, self.admin_sessions)
            return True
        return False
    
    def get_audit_logs(self, limit=100, offset=0, filter_ip=None, filter_path=None):
        """获取审计日志"""
        logs = []
        try:
            if self.audit_log_file.exists():
                with open(self.audit_log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            log = json.loads(line.strip())
                            # 过滤
                            if filter_ip and log.get('ip') != filter_ip:
                                continue
                            if filter_path and filter_path not in log.get('path', ''):
                                continue
                            logs.append(log)
                        except:
                            continue
        except:
            pass
        
        # 按时间倒序排序
        logs.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        
        # 分页
        return logs[offset:offset+limit]
    
    def get_pending_count(self):
        """获取待审批数量"""
        return len([v for v in self.pending_approvals.values() if v['status'] == 'pending'])
    
    def get_stats(self):
        """获取统计信息"""
        total_visits = 0
        unique_ips = set()
        today_visits = 0
        today = datetime.now().date()
        
        try:
            if self.audit_log_file.exists():
                with open(self.audit_log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            log = json.loads(line.strip())
                            total_visits += 1
                            unique_ips.add(log.get('ip', ''))
                            log_date = datetime.fromtimestamp(log.get('timestamp', 0)).date()
                            if log_date == today:
                                today_visits += 1
                        except:
                            continue
        except:
            pass
        
        return {
            'total_visits': total_visits,
            'unique_ips': len(unique_ips),
            'today_visits': today_visits,
            'pending_approvals': self.get_pending_count()
        }

# 全局数据管理器
data_manager = DataManager()

# ==================== 飞书通知 ====================

class FeishuNotifier:
    """飞书消息通知"""
    
    @staticmethod
    def send_access_alert(visitor_info):
        """发送访问告警通知"""
        try:
            msg = f"""🚨 WebViewer 访问告警

🌐 IP 地址：{visitor_info.get('ip', 'Unknown')}
🖥️ 设备：{visitor_info.get('browser', 'Unknown')} / {visitor_info.get('platform', 'Unknown')}
📍 位置：{visitor_info.get('location', 'Unknown')}
🔗 路径：{visitor_info.get('path', '/')}
⏰ 时间：{visitor_info.get('datetime', 'Unknown')}
📊 状态：{visitor_info.get('status', 'unknown')}

👉 查看审计日志：https://43.153.153.62/audit"""
            
            # 通过 openclaw 发送飞书消息
            cmd = [
                'openclaw', 'message', 'send',
                '--channel', 'feishu',
                '--target', 'ou_67455f002e1316b6b05e4f3020ae2ff5',
                '--message', msg
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            print(f"📢 已发送访问告警：{visitor_info.get('ip')} - {visitor_info.get('path')}")
            return True
            
        except Exception as e:
            print(f"❌ 发送通知失败：{e}")
            return False
    
    @staticmethod
    def send_approval_request(visitor_info, approval_id):
        """发送审批请求通知"""
        try:
            verify_code = data_manager.pending_approvals[approval_id]['verification_code']
            
            msg = f"""🔐 WebViewer 访问审批请求

🌐 访问来源：{visitor_info.get('ip', 'Unknown')}
🖥️ 设备：{visitor_info.get('user_agent', 'Unknown')[:50]}...
📍 位置：{visitor_info.get('location', 'Unknown')}
⏰ 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

审批链接:
✅ 同意：https://43.153.153.62/approve/{approval_id}
❌ 拒绝：https://43.153.153.62/reject/{approval_id}

验证码：{verify_code}"""
            
            cmd = [
                'openclaw', 'message', 'send',
                '--channel', 'feishu',
                '--target', 'ou_67455f002e1316b6b05e4f3020ae2ff5',
                '--message', msg
            ]
            
            subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            print(f"📢 已发送审批请求：{visitor_info.get('ip')}")
            return True
            
        except Exception as e:
            print(f"❌ 发送通知失败：{e}")
            return False

# ==================== HTTP 请求处理 ====================

class WebViewerHandler(SimpleHTTPRequestHandler):
    """WebViewer 请求处理器（增强版）"""
    
    def get_visitor_info(self, extra_info=None):
        """获取访问者详细信息"""
        # 获取真实 IP（考虑代理）
        ip = self.headers.get('X-Forwarded-For', self.client_address[0])
        if ',' in ip:
            ip = ip.split(',')[0].strip()
        
        user_agent = self.headers.get('User-Agent', 'Unknown')
        browser, platform = self._parse_user_agent(user_agent)
        
        info = {
            'ip': ip,
            'user_agent': user_agent,
            'path': self.path,
            'method': self.command,
            'referer': self.headers.get('Referer', ''),
            'language': self.headers.get('Accept-Language', ''),
            'platform': platform,
            'browser': browser,
            'location': self._get_location(ip),
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat()
        }
        
        if extra_info:
            info.update(extra_info)
        
        return info
    
    def _parse_user_agent(self, ua):
        """解析 User-Agent"""
        browser = 'Unknown'
        platform = 'Unknown'
        
        ua_lower = ua.lower()
        
        # 浏览器
        if 'firefox' in ua_lower:
            browser = 'Firefox'
        elif 'chrome' in ua_lower and 'edg' not in ua_lower:
            browser = 'Chrome'
        elif 'safari' in ua_lower and 'chrome' not in ua_lower:
            browser = 'Safari'
        elif 'edg' in ua_lower:
            browser = 'Edge'
        elif 'msie' in ua_lower or 'trident' in ua_lower:
            browser = 'IE'
        
        # 平台
        if 'windows' in ua_lower:
            platform = 'Windows'
        elif 'mac os' in ua_lower or 'macintosh' in ua_lower:
            platform = 'macOS'
        elif 'linux' in ua_lower:
            platform = 'Linux'
        elif 'android' in ua_lower:
            platform = 'Android'
        elif 'iphone' in ua_lower or 'ipad' in ua_lower:
            platform = 'iOS'
        
        return browser, platform
    
    def _get_location(self, ip):
        """根据 IP 获取地理位置"""
        if ip.startswith('192.168.') or ip.startswith('10.') or ip == '127.0.0.1':
            return '内网'
        return '未知'
    
    def check_access(self):
        """检查访问权限（审批系统）"""
        import http.cookies
        visitor_info = self.get_visitor_info()
        ip = visitor_info['ip']
        
        # 白名单 IP 直接放行
        if ip in Config.WHITELIST_IPS:
            return True, None, visitor_info
        
        # 检查是否有有效会话
        cookie_header = self.headers.get('Cookie', '')
        cookies = http.cookies.SimpleCookie(cookie_header)
        session_id = cookies.get('wv_session')
        if session_id:
            session_id = session_id.value
            if data_manager.check_session(session_id):
                return True, session_id, visitor_info
        
        return False, None, visitor_info
    
    def check_admin_auth(self):
        """检查管理员认证"""
        import http.cookies
        cookie_header = self.headers.get('Cookie', '')
        cookies = http.cookies.SimpleCookie(cookie_header)
        admin_session = cookies.get('wv_admin_session')
        
        if admin_session:
            session_id = admin_session.value
            if data_manager.check_admin_session(session_id):
                return True, session_id
        
        return False, None
    
    def do_GET(self):
        """处理 GET 请求"""
        visitor_info = self.get_visitor_info()
        
        # 特殊路径处理
        if self.path == '/' or self.path == '':
            # 检查是否是管理员登录状态
            if self.check_admin_auth()[0]:
                self.send_response(302)
                self.send_header('Location', '/www/')
                self.end_headers()
            else:
                self.send_response(302)
                self.send_header('Location', '/login')
                self.end_headers()
            return
        elif self.path == '/login':
            self.show_login_page()
            return
        elif self.path == '/logout':
            self.handle_logout()
            return
        elif self.path == '/audit':
            self.show_audit_page()
            return
        elif self.path == '/api/audit-logs':
            self.handle_audit_logs_api()
            return
        elif self.path == '/api/stats':
            self.handle_stats_api()
            return
        elif self.path.startswith('/approve/'):
            self.handle_approval(True)
            return
        elif self.path.startswith('/reject/'):
            self.handle_approval(False)
            return
        elif self.path == '/pending':
            if not self.check_admin_auth()[0]:
                self.send_response(302)
                self.send_header('Location', '/login')
                self.end_headers()
                return
            self.show_pending_page()
            return
        elif self.path.startswith('/www/'):
            # 工具箱主页路径，直接提供静态文件
            if not self.check_admin_auth()[0]:
                self.send_response(302)
                self.send_header('Location', '/login')
                self.end_headers()
                return
            # 直接读取文件并返回
            import os
            rel_path = self.path[5:]  # 去掉 "/www"
            if rel_path == '' or rel_path == '/':
                rel_path = 'index.html'
            else:
                rel_path = rel_path.lstrip('/')
            
            file_path = Config.WWW_DIR / rel_path
            try:
                if file_path.exists() and file_path.is_file():
                    self.send_response(200)
                    if rel_path.endswith('.html'):
                        self.send_header('Content-Type', 'text/html; charset=utf-8')
                    elif rel_path.endswith('.css'):
                        self.send_header('Content-Type', 'text/css')
                    elif rel_path.endswith('.js'):
                        self.send_header('Content-Type', 'application/javascript')
                    else:
                        self.send_header('Content-Type', 'application/octet-stream')
                    self.end_headers()
                    with open(file_path, 'rb') as f:
                        self.wfile.write(f.read())
                else:
                    self.send_error(404, 'File not found')
            except Exception as e:
                self.send_error(500, str(e))
            return
        
        # 检查访问权限（审批系统）
        allowed, session_id, visitor_info = self.check_access()
        
        # 记录审计日志
        visitor_info['event_type'] = 'page_access'
        visitor_info['status'] = 'allowed' if allowed else 'blocked'
        visitor_info['session_id'] = session_id or ''
        data_manager.log_audit(visitor_info)
        
        # 发送访问告警（仅当被阻止时）
        if not allowed and session_id is None:
            # 创建待审批
            approval_record = data_manager.create_pending_approval(visitor_info)
            approval_id = approval_record['approval_id']
            # 发送通知
            FeishuNotifier.send_approval_request(visitor_info, approval_id)
            # 显示等待页面
            self.show_waiting_page(approval_id)
            return
        
        if allowed:
            # 正常访问
            super().do_GET()
            return
    
    def do_POST(self):
        """处理 POST 请求"""
        if self.path == '/api/login':
            self.handle_login()
            return
        elif self.path == '/api/audit-delete':
            if not self.check_admin_auth()[0]:
                self.send_json({'error': 'Unauthorized'}, 401)
                return
            self.handle_audit_delete()
            return
        
        self.send_response(404)
        self.end_headers()
    
    def handle_login(self):
        """处理登录请求"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body)
            username = data.get('username', '')
            password = data.get('password', '')
            
            visitor_info = self.get_visitor_info({'event_type': 'login_attempt'})
            
            if data_manager.verify_admin_login(username, password):
                # 登录成功
                session_id = data_manager.create_admin_session(username, visitor_info['ip'])
                
                visitor_info['status'] = 'success'
                data_manager.log_audit(visitor_info)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Set-Cookie', f'wv_admin_session={session_id}; Path=/; Max-Age={Config.ADMIN_SESSION_TIMEOUT_HOURS*3600}; HttpOnly')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True, 'redirect': '/www/'}).encode())
            else:
                # 登录失败
                visitor_info['status'] = 'failed'
                data_manager.log_audit(visitor_info)
                
                self.send_json({'success': False, 'error': '用户名或密码错误'}, 401)
                
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def handle_logout(self):
        """处理登出请求"""
        import http.cookies
        cookie_header = self.headers.get('Cookie', '')
        cookies = http.cookies.SimpleCookie(cookie_header)
        admin_session = cookies.get('wv_admin_session')
        
        if admin_session:
            data_manager.logout_admin(admin_session.value)
        
        self.send_response(302)
        self.send_header('Location', '/login')
        self.send_header('Set-Cookie', 'wv_admin_session=; Path=/; Max-Age=0')
        self.end_headers()
    
    def handle_audit_logs_api(self):
        """获取审计日志 API"""
        if not self.check_admin_auth()[0]:
            self.send_json({'error': 'Unauthorized'}, 401)
            return
        
        try:
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            
            limit = int(params.get('limit', [100])[0])
            offset = int(params.get('offset', [0])[0])
            filter_ip = params.get('ip', [None])[0]
            filter_path = params.get('path', [None])[0]
            
            logs = data_manager.get_audit_logs(limit, offset, filter_ip, filter_path)
            stats = data_manager.get_stats()
            
            self.send_json({
                'success': True,
                'logs': logs,
                'stats': stats,
                'total': len(logs)
            })
            
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def handle_audit_delete(self):
        """删除审计日志"""
        # 简单实现：清空日志文件
        try:
            with open(data_manager.audit_log_file, 'w') as f:
                pass
            self.send_json({'success': True})
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def handle_approval(self, approve):
        """处理审批"""
        import http.cookies
        
        path_parts = self.path.split('/')
        approval_id = path_parts[-1] if len(path_parts) > 2 else None
        
        if not approval_id:
            self.send_response(400)
            self.end_headers()
            return
        
        if approve:
            success, result = data_manager.approve_access(approval_id)
            msg = '✅ 已批准访问' if success else '❌ 审批失败'
        else:
            success, result = data_manager.reject_access(approval_id)
            msg = '❌ 已拒绝访问' if success else '❌ 审批失败'
        
        # 记录审计日志
        visitor_info = self.get_visitor_info({
            'event_type': 'approval',
            'status': 'approved' if approve else 'rejected',
            'approval_id': approval_id
        })
        data_manager.log_audit(visitor_info)
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(f'''
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>审批结果</title></head>
<body style="display:flex;justify-content:center;align-items:center;height:100vh;background:linear-gradient(135deg,#667eea,#764ba2);font-family:sans-serif;">
<div style="background:white;padding:40px;border-radius:16px;text-align:center;box-shadow:0 10px 40px rgba(0,0,0,0.2);">
<h1 style="font-size:48px;margin:0;">{"✅" if approve else "❌"}</h1>
<h2>{msg}</h2>
<p style="color:#666;">{result if isinstance(result, str) else ''}</p>
</div>
</body>
</html>
'''.encode())
    
    def show_login_page(self):
        """显示登录页面"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        
        self.wfile.write('''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>管理员登录 | WebViewer</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .login-box {
            background: white;
            padding: 40px;
            border-radius: 16px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.2);
            width: 100%;
            max-width: 400px;
        }
        h1 { color: #1f2937; margin-bottom: 30px; text-align: center; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #374151; font-weight: 500; }
        input {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.2s;
        }
        input:focus { outline: none; border-color: #667eea; }
        button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover { transform: translateY(-2px); }
        .error { color: #ef4444; margin-bottom: 20px; text-align: center; display: none; }
    </style>
</head>
<body>
    <div class="login-box">
        <h1>🔐 管理员登录</h1>
        <div class="error" id="error"></div>
        <form id="loginForm">
            <div class="form-group">
                <label>用户名</label>
                <input type="text" id="username" required placeholder="请输入用户名">
            </div>
            <div class="form-group">
                <label>密码</label>
                <input type="password" id="password" required placeholder="请输入密码">
            </div>
            <button type="submit">登录</button>
        </form>
    </div>
    <script>
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            try {
                const res = await fetch('/api/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({username, password})
                });
                const data = await res.json();
                
                if (data.success) {
                    window.location.href = data.redirect;
                } else {
                    document.getElementById('error').textContent = data.error || '登录失败';
                    document.getElementById('error').style.display = 'block';
                }
            } catch (err) {
                document.getElementById('error').textContent = '网络错误，请重试';
                document.getElementById('error').style.display = 'block';
            }
        });
    </script>
</body>
</html>
'''.encode())
    
    def show_home_page(self):
        """显示主页"""
        if not self.check_admin_auth()[0]:
            self.send_response(302)
            self.send_header('Location', '/login')
            self.end_headers()
            return
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        
        self.wfile.write('''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WebViewer 主页</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .home-box {
            background: white;
            padding: 60px;
            border-radius: 16px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.2);
            text-align: center;
            max-width: 500px;
        }
        h1 { color: #1f2937; margin-bottom: 20px; font-size: 32px; }
        p { color: #6b7280; margin-bottom: 30px; line-height: 1.6; }
        .nav-links { display: flex; flex-direction: column; gap: 12px; }
        .nav-links a {
            display: block;
            padding: 14px 24px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            transition: transform 0.2s;
        }
        .nav-links a:hover { transform: translateY(-2px); }
        .nav-links a.secondary {
            background: #f3f4f6;
            color: #374151;
        }
        .logout {
            margin-top: 30px;
            color: #ef4444;
            text-decoration: none;
            font-size: 14px;
        }
        .logout:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="home-box">
        <h1>🎉 欢迎回来</h1>
        <p>您已成功登录 WebViewer 管理系统<br>当前会话状态：已授权</p>
        <div class="nav-links">
            <a href="/reports/">📄 查看报告</a>
            <a href="/reports/index.html" class="secondary">📊 报告列表</a>
        </div>
        <a href="/logout" class="logout">退出登录</a>
    </div>
</body>
</html>
'''.encode())
    
    def show_audit_page(self):
        """显示审计日志页面"""
        if not self.check_admin_auth()[0]:
            self.send_response(302)
            self.send_header('Location', '/login')
            self.end_headers()
            return
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        
        self.wfile.write('''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>访问审计 | WebViewer</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f3f4f6; }
        .header { background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px 40px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 24px; }
        .header a { color: white; text-decoration: none; padding: 8px 16px; background: rgba(255,255,255,0.2); border-radius: 8px; }
        .container { max-width: 1400px; margin: 0 auto; padding: 40px 20px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 24px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .stat-value { font-size: 32px; font-weight: bold; color: #667eea; }
        .stat-label { color: #6b7280; margin-top: 8px; }
        .filters { background: white; padding: 20px; border-radius: 12px; margin-bottom: 20px; display: flex; gap: 16px; flex-wrap: wrap; }
        .filters input { padding: 10px 16px; border: 2px solid #e5e7eb; border-radius: 8px; flex: 1; min-width: 200px; }
        .filters button { padding: 10px 24px; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer; }
        .log-table { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .log-table table { width: 100%; border-collapse: collapse; }
        .log-table th, .log-table td { padding: 16px; text-align: left; border-bottom: 1px solid #e5e7eb; }
        .log-table th { background: #f9fafb; font-weight: 600; color: #374151; }
        .log-table tr:hover { background: #f9fafb; }
        .status-allowed { color: #10b981; }
        .status-blocked { color: #ef4444; }
        .status-success { color: #10b981; }
        .status-failed { color: #ef4444; }
        .refresh-btn { padding: 8px 16px; background: #10b981; color: white; border: none; border-radius: 8px; cursor: pointer; }
        .load-more { text-align: center; padding: 20px; }
        .load-more button { padding: 12px 32px; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 访问审计日志</h1>
        <div>
            <a href="/pending">待审批</a>
            <a href="/logout" style="margin-left: 10px;">退出登录</a>
        </div>
    </div>
    <div class="container">
        <div class="stats" id="stats"></div>
        <div class="filters">
            <input type="text" id="filterIp" placeholder="过滤 IP 地址">
            <input type="text" id="filterPath" placeholder="过滤路径">
            <button onclick="loadLogs()">🔍 搜索</button>
            <button class="refresh-btn" onclick="loadLogs()">🔄 刷新</button>
        </div>
        <div class="log-table">
            <table>
                <thead>
                    <tr>
                        <th>时间</th>
                        <th>IP 地址</th>
                        <th>设备</th>
                        <th>路径</th>
                        <th>事件类型</th>
                        <th>状态</th>
                        <th>位置</th>
                    </tr>
                </thead>
                <tbody id="logTable"></tbody>
            </table>
        </div>
        <div class="load-more">
            <button onclick="loadMore()">加载更多</button>
        </div>
    </div>
    <script>
        let offset = 0;
        const limit = 50;
        
        async function loadLogs(append = false) {
            if (!append) offset = 0;
            
            const ip = document.getElementById('filterIp').value;
            const path = document.getElementById('filterPath').value;
            
            let url = `/api/audit-logs?limit=${limit}&offset=${offset}`;
            if (ip) url += `&ip=${encodeURIComponent(ip)}`;
            if (path) url += `&path=${encodeURIComponent(path)}`;
            
            try {
                const res = await fetch(url);
                const data = await res.json();
                
                if (!append) {
                    document.getElementById('logTable').innerHTML = '';
                    document.getElementById('stats').innerHTML = `
                        <div class="stat-card"><div class="stat-value">${data.stats.total_visits}</div><div class="stat-label">总访问数</div></div>
                        <div class="stat-card"><div class="stat-value">${data.stats.unique_ips}</div><div class="stat-label">独立 IP</div></div>
                        <div class="stat-card"><div class="stat-value">${data.stats.today_visits}</div><div class="stat-label">今日访问</div></div>
                        <div class="stat-card"><div class="stat-value">${data.stats.pending_approvals}</div><div class="stat-label">待审批</div></div>
                    `;
                }
                
                const tbody = document.getElementById('logTable');
                data.logs.forEach(log => {
                    const row = tbody.insertRow();
                    const time = new Date(log.timestamp * 1000).toLocaleString('zh-CN');
                    const statusClass = ['allowed', 'success'].includes(log.status) ? 'status-allowed' : 'status-blocked';
                    row.innerHTML = `
                        <td>${time}</td>
                        <td>${log.ip}</td>
                        <td>${log.browser || 'Unknown'}<br><small style="color:#999">${log.platform || ''}</small></td>
                        <td>${log.path}</td>
                        <td>${log.event_type}</td>
                        <td class="${statusClass}">${log.status}</td>
                        <td>${log.location || '未知'}</td>
                    `;
                });
                
                offset += data.logs.length;
            } catch (err) {
                console.error('加载失败:', err);
            }
        }
        
        function loadMore() {
            loadLogs(true);
        }
        
        // 初始加载
        loadLogs();
        
        // 自动刷新（每 30 秒）
        setInterval(() => loadLogs(), 30000);
    </script>
</body>
</html>
'''.encode())
    
    def show_waiting_page(self, approval_id):
        """显示等待审批页面"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        
        self.wfile.write(f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>等待审批 | WebViewer</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        .container {{
            background: white;
            border-radius: 24px;
            padding: 50px;
            max-width: 500px;
            text-align: center;
            box-shadow: 0 25px 50px rgba(0,0,0,0.2);
        }}
        .icon {{ font-size: 80px; margin-bottom: 20px; }}
        h1 {{ color: #1f2937; margin-bottom: 15px; }}
        p {{ color: #6b7280; margin-bottom: 30px; line-height: 1.6; }}
        .status {{
            background: #f3f4f6;
            padding: 20px;
            border-radius: 12px;
            margin-top: 20px;
        }}
        .spinner {{
            border: 4px solid #f3f4f6;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }}
        @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">⏳</div>
        <h1>等待审批</h1>
        <p>您的访问请求已提交，正在等待管理员审批。<br>审批通过后页面将自动刷新。</p>
        <div class="status">
            <div class="spinner"></div>
            <p style="margin: 0;">审批 ID: {approval_id[:8]}...</p>
        </div>
    </div>
    <script>
        setInterval(async () => {{
            try {{
                const res = await fetch(`/check-status/{approval_id}`);
                const data = await res.json();
                if (data.approved) {{
                    window.location.reload();
                }}
            }} catch (e) {{}}
        }}, 5000);
    </script>
</body>
</html>
'''.encode())
    
    def show_pending_page(self):
        """显示待审批列表页面"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        
        pending_list = list(data_manager.pending_approvals.values())
        
        rows = ''
        for record in pending_list:
            visitor = record.get('visitor_info', {})
            status = record.get('status', 'pending')
            time_str = datetime.fromtimestamp(record.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S')
            approval_id = record.get('approval_id', '')
            
            rows += f'''
            <tr>
                <td>{time_str}</td>
                <td>{visitor.get('ip', 'Unknown')}</td>
                <td>{visitor.get('path', '/')}</td>
                <td>{visitor.get('browser', 'Unknown')}</td>
                <td>{status}</td>
                <td>
                    {f'<a href="/approve/{approval_id}" style="color:#10b981">✅ 同意</a>' if status == 'pending' else '-'}
                    {f'<a href="/reject/{approval_id}" style="color:#ef4444;margin-left:10px">❌ 拒绝</a>' if status == 'pending' else ''}
                </td>
            </tr>
            '''
        
        self.wfile.write(f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>待审批列表 | WebViewer</title>
    <style>
        body {{ font-family: sans-serif; background: #f3f4f6; padding: 40px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ margin-bottom: 20px; }}
        table {{ width: 100%; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        th, td {{ padding: 16px; text-align: left; border-bottom: 1px solid #e5e7eb; }}
        th {{ background: #f9fafb; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
        .header a {{ color: #667eea; text-decoration: none; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📋 待审批列表</h1>
            <a href="/audit">← 返回审计日志</a>
        </div>
        <table>
            <thead>
                <tr>
                    <th>时间</th>
                    <th>IP 地址</th>
                    <th>路径</th>
                    <th>设备</th>
                    <th>状态</th>
                    <th>操作</th>
                </tr>
            </thead>
            <tbody>
                {rows if rows else '<tr><td colspan="6" style="text-align:center;color:#999">暂无待审批记录</td></tr>'}
            </tbody>
        </table>
    </div>
</body>
</html>
'''.encode())
    
    def send_json(self, data, status=200):
        """发送 JSON 响应"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
    
    def log_message(self, format, *args):
        """重写日志输出"""
        print(f"[WebViewer] {datetime.now().isoformat()} - {args[0]}")

# ==================== 启动服务器 ====================

def run_server():
    """启动 HTTPS 服务器"""
    server_address = (Config.HOST, Config.HTTPS_PORT)
    httpd = HTTPServer(server_address, WebViewerHandler)
    
    # 加载 SSL 证书
    cert_file = Config.DATA_DIR / 'server.crt'
    key_file = Config.DATA_DIR / 'server.key'
    
    if cert_file.exists() and key_file.exists():
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=str(cert_file), keyfile=str(key_file))
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
        print(f"🔒 SSL 已启用")
    else:
        print(f"⚠️ 警告：SSL 证书未找到，将以 HTTP 运行")
    
    print("=" * 60)
    print("🚀 WebViewer 增强版服务器已启动")
    print("=" * 60)
    print(f"📡 监听地址：https://{socket.gethostbyname(socket.gethostname())}:{Config.HTTPS_PORT}")
    print(f"🔐 管理员登录：https://.../login")
    print(f"📊 审计日志：https://.../audit")
    print(f"📋 待审批：https://.../pending")
    print("=" * 60)
    
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
