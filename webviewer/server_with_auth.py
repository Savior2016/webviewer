#!/usr/bin/env python3
"""
WebViewer 服务器 - 带账号密码登录和 Token 认证
功能：
- 账号密码登录（浏览器访问）
- Token 认证（API/POST 请求）
- IP 白名单自动放行
- 访客审批（可选）
"""

import json
import os
import time
import uuid
import hashlib
import socket
from pathlib import Path
from datetime import datetime, timedelta
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse, urlencode
import threading
import requests
import secrets

# ==================== 配置 ====================

class Config:
    # 服务器配置
    HOST = '0.0.0.0'
    PORT = 8888
    HTTPS_PORT = 8443
    
    # 加载配置文件
    CONFIG_FILE = Path('/root/.openclaw/workspace/webviewer/config.json')
    
    @classmethod
    def load_config(cls):
        if cls.CONFIG_FILE.exists():
            with open(cls.CONFIG_FILE) as f:
                return json.load(f)
        return {}
    
    @classmethod
    def verify_password(cls, username, password):
        config = cls.load_config()
        admin = config.get('admin', {})
        if admin.get('username') != username:
            return False
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return admin.get('password_hash') == password_hash
    
    @classmethod
    def verify_token(cls, token):
        config = cls.load_config()
        return config.get('api_token') == token
    
    @classmethod
    def get_api_token(cls):
        config = cls.load_config()
        return config.get('api_token', '')
    
    @classmethod
    def is_whitelist_ip(cls, ip):
        config = cls.load_config()
        whitelist = config.get('whitelist_ips', [])
        return ip in whitelist
    
    # 会话配置
    SESSION_TIMEOUT_HOURS = 24
    
    # 数据目录
    DATA_DIR = Path('/root/.openclaw/workspace/webviewer/data')
    WWW_DIR = Path('/root/.openclaw/workspace/webviewer/www')
    ACCESS_LOG_FILE = DATA_DIR / 'access_log.jsonl'
    SESSIONS_FILE = DATA_DIR / 'sessions.json'

# ==================== 会话管理 ====================

class SessionManager:
    """管理登录会话"""
    
    def __init__(self):
        self.sessions_file = Config.SESSIONS_FILE
        self.sessions = self._load_sessions()
        self._cleanup_expired()
    
    def _load_sessions(self):
        try:
            if self.sessions_file.exists():
                with open(self.sessions_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def _save_sessions(self):
        with open(self.sessions_file, 'w') as f:
            json.dump(self.sessions, f, indent=2)
    
    def _cleanup_expired(self):
        now = time.time()
        timeout = Config.SESSION_TIMEOUT_HOURS * 3600
        self.sessions = {
            k: v for k, v in self.sessions.items()
            if v.get('expires_at', 0) > now
        }
        self._save_sessions()
    
    def create_session(self, username, ip):
        session_id = secrets.token_urlsafe(32)
        expires_at = time.time() + (Config.SESSION_TIMEOUT_HOURS * 3600)
        self.sessions[session_id] = {
            'username': username,
            'ip': ip,
            'created_at': time.time(),
            'expires_at': expires_at
        }
        self._save_sessions()
        return session_id
    
    def verify_session(self, session_id):
        session = self.sessions.get(session_id)
        if not session:
            return False
        if session.get('expires_at', 0) < time.time():
            del self.sessions[session_id]
            self._save_sessions()
            return False
        return True
    
    def get_session_user(self, session_id):
        session = self.sessions.get(session_id)
        return session.get('username') if session else None

# 全局会话管理器
session_manager = SessionManager()

# ==================== 访问日志 ====================

def log_access(visitor_info):
    """记录访问日志"""
    log_entry = {
        'timestamp': time.time(),
        'datetime': datetime.now().isoformat(),
        **visitor_info
    }
    with open(Config.ACCESS_LOG_FILE, 'a') as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

# ==================== HTTP 请求处理 ====================

class WebViewerHandler(SimpleHTTPRequestHandler):
    """WebViewer 请求处理器（带认证）"""
    
    def get_client_ip(self):
        """获取客户端 IP（支持代理）"""
        forwarded = self.headers.get('X-Forwarded-For')
        if forwarded:
            return forwarded.split(',')[0].strip()
        return self.client_address[0]
    
    def check_auth(self):
        """检查认证（Session / Token / IP 白名单）"""
        ip = self.get_client_ip()
        
        # 1. 检查 IP 白名单
        if Config.is_whitelist_ip(ip):
            return True, 'whitelist'
        
        # 2. 检查 Session（从 Cookie）
        cookie = self.headers.get('Cookie', '')
        if 'session_id=' in cookie:
            for c in cookie.split(';'):
                if c.strip().startswith('session_id='):
                    session_id = c.split('=')[1].strip()
                    if session_manager.verify_session(session_id):
                        return True, 'session'
        
        # 3. 检查 Token（从 Authorization Header）
        auth_header = self.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            if Config.verify_token(token):
                return True, 'token'
        
        # 4. 检查 URL 参数中的 token
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        if 'token' in params:
            if Config.verify_token(params['token'][0]):
                return True, 'token'
        
        return False, None
    
    def do_GET(self):
        # 特殊路径处理
        parsed = urlparse(self.path)
        path = parsed.path
        
        # 登录页面
        if path == '/login':
            self.show_login_page()
            return
        
        # 登录 API
        if path == '/api/login':
            self.handle_login()
            return
        
        # 登出 API
        if path == '/api/logout':
            self.handle_logout()
            return
        
        # API Token 查询
        if path == '/api/token':
            self.show_api_token()
            return
        
        # 健康检查
        if path == '/health' or path == '/global/health':
            self.send_json({'status': 'ok', 'timestamp': datetime.now().isoformat()})
            return
        
        # 检查认证
        allowed, auth_type = self.check_auth()
        
        if not allowed:
            # 重定向到登录页
            self.send_response(302)
            self.send_header('Location', '/login')
            self.end_headers()
            return
        
        # 记录访问日志
        log_access({
            'ip': self.get_client_ip(),
            'user_agent': self.headers.get('User-Agent', 'Unknown'),
            'path': self.path,
            'method': 'GET',
            'auth_type': auth_type
        })
        
        # 正常处理请求
        super().do_GET()
    
    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        # API 端点
        if path.startswith('/api/'):
            # 检查 Token 认证
            auth_header = self.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
                if Config.verify_token(token):
                    self.handle_api_request()
                    return
            
            # URL 参数 token
            params = parse_qs(parsed.query)
            if 'token' in params and Config.verify_token(params['token'][0]):
                self.handle_api_request()
                return
            
            # 认证失败
            self.send_error(401, 'Unauthorized')
            return
        
        # 登录 API
        if path == '/api/login':
            self.handle_login()
            return
        
        # 其他 POST 请求检查认证
        allowed, auth_type = self.check_auth()
        if not allowed:
            self.send_error(401, 'Unauthorized')
            return
        
        # 正常处理
        super().do_POST()
    
    def handle_login(self):
        """处理登录请求"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body) if body else {}
            
            # 从表单或 JSON 获取凭据
            username = data.get('username', '')
            password = data.get('password', '')
            
            # 也支持表单提交
            if not username and hasattr(self, 'post_data'):
                username = self.post_data.get('username', [''])[0]
                password = self.post_data.get('password', [''])[0]
            
            if Config.verify_password(username, password):
                # 创建会话
                session_id = session_manager.create_session(username, self.get_client_ip())
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Set-Cookie', f'session_id={session_id}; Path=/; Max-Age={Config.SESSION_TIMEOUT_HOURS*3600}; HttpOnly')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': True,
                    'message': '登录成功',
                    'username': username
                }).encode())
            else:
                self.send_json({'success': False, 'message': '用户名或密码错误'}, 401)
        except Exception as e:
            self.send_json({'success': False, 'message': str(e)}, 500)
    
    def handle_logout(self):
        """处理登出请求"""
        cookie = self.headers.get('Cookie', '')
        session_id = None
        for c in cookie.split(';'):
            if c.strip().startswith('session_id='):
                session_id = c.split('=')[1].strip()
                break
        
        if session_id and session_id in session_manager.sessions:
            del session_manager.sessions[session_id]
            session_manager._save_sessions()
        
        self.send_response(302)
        self.send_header('Location', '/login')
        self.send_header('Set-Cookie', 'session_id=; Path=/; Max-Age=0')
        self.end_headers()
    
    def handle_api_request(self):
        """处理 API 请求"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b'{}'
        
        try:
            data = json.loads(body) if body else {}
        except:
            data = {}
        
        parsed = urlparse(self.path)
        path = parsed.path
        
        # API 路由
        if path == '/api/info':
            self.send_json({
                'service': 'WebViewer',
                'version': '2.0',
                'auth': 'token',
                'token': Config.get_api_token()
            })
        elif path == '/api/status':
            self.send_json({
                'status': 'running',
                'timestamp': datetime.now().isoformat(),
                'ip': self.get_client_ip()
            })
        else:
            # 默认返回接收到的数据
            self.send_json({
                'success': True,
                'path': path,
                'method': 'POST',
                'data': data,
                'timestamp': datetime.now().isoformat()
            })
    
    def show_login_page(self):
        """显示登录页面"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        
        html = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>登录 | WebViewer</title>
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
        .container {
            background: white;
            border-radius: 24px;
            padding: 50px;
            max-width: 400px;
            width: 100%;
            box-shadow: 0 25px 50px rgba(0,0,0,0.2);
        }
        h1 { color: #1f2937; margin-bottom: 10px; text-align: center; }
        p { color: #6b7280; margin-bottom: 30px; text-align: center; }
        .form-group { margin-bottom: 20px; }
        label { display: block; color: #374151; margin-bottom: 8px; font-weight: 500; }
        input {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e5e7eb;
            border-radius: 12px;
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
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover { transform: translateY(-2px); }
        button:active { transform: translateY(0); }
        .error { color: #ef4444; margin-bottom: 20px; text-align: center; display: none; }
        .api-info {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
            font-size: 14px;
            color: #6b7280;
        }
        .api-info code {
            background: #f3f4f6;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 WebViewer 登录</h1>
        <p>请输入管理员账号</p>
        <div class="error" id="error"></div>
        <form id="loginForm">
            <div class="form-group">
                <label>用户名</label>
                <input type="text" id="username" name="username" required autocomplete="username">
            </div>
            <div class="form-group">
                <label>密码</label>
                <input type="password" id="password" name="password" required autocomplete="current-password">
            </div>
            <button type="submit">登录</button>
        </form>
        <div class="api-info">
            <p><strong>API Token 认证：</strong></p>
            <p>请求头：<code>Authorization: Bearer &lt;token&gt;</code></p>
            <p>或 URL 参数：<code>?token=&lt;token&gt;</code></p>
        </div>
    </div>
    <script>
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const errorEl = document.getElementById('error');
            
            try {
                const resp = await fetch('/api/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({username, password})
                });
                const result = await resp.json();
                
                if (result.success) {
                    window.location.href = '/';
                } else {
                    errorEl.textContent = result.message || '登录失败';
                    errorEl.style.display = 'block';
                }
            } catch (err) {
                errorEl.textContent = '网络错误，请重试';
                errorEl.style.display = 'block';
            }
        });
    </script>
</body>
</html>
'''
        self.wfile.write(html.encode())
    
    def show_api_token(self):
        """显示 API Token"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        
        token = Config.get_api_token()
        html = f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>API Token | WebViewer</title>
    <style>
        body {{ font-family: monospace; padding: 40px; background: #1f2937; color: #10b981; }}
        .token {{ font-size: 24px; padding: 20px; background: #111827; border-radius: 8px; margin: 20px 0; }}
        code {{ color: #fbbf24; }}
    </style>
</head>
<body>
    <h1>🔑 API Token</h1>
    <div class="token">{token}</div>
    <h2>使用示例：</h2>
    <pre><code>curl -X POST https://10.7.0.13:8443/api/info \\
  -H "Authorization: Bearer {token}"</code></pre>
</body>
</html>
'''
        self.wfile.write(html.encode())
    
    def send_json(self, data, status=200):
        """发送 JSON 响应"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {self.get_client_ip()} - {format % args}")

# ==================== 服务器启动 ====================

def run_server():
    """启动 HTTPS 服务器"""
    import ssl
    
    server_address = (Config.HOST, Config.HTTPS_PORT)
    httpd = HTTPServer(server_address, WebViewerHandler)
    
    # SSL 配置
    cert_file = Config.DATA_DIR / 'server.crt'
    key_file = Config.DATA_DIR / 'server.key'
    
    if cert_file.exists() and key_file.exists():
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(str(cert_file), str(key_file))
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
        print(f"🔐 HTTPS 服务器已启动")
    else:
        print(f"⚠️  SSL 证书未找到，使用 HTTP")
    
    print(f"📡 访问地址：https://{socket.gethostbyname(socket.gethostname())}:{Config.HTTPS_PORT}")
    print(f"🔑 API Token: {Config.get_api_token()}")
    print(f"📜 日志：{Config.ACCESS_LOG_FILE}")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
