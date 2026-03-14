#!/usr/bin/env python3
"""
WebViewer 访问审核服务器
功能：
- 拦截所有访问请求
- 记录访问者信息（IP、User-Agent、时间等）
- 发送飞书审批通知
- 等待用户确认后放行或拒绝
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

# ==================== 配置 ====================

class Config:
    # 服务器配置
    HOST = '0.0.0.0'
    PORT = 8888
    HTTPS_PORT = 443  # 使用标准 HTTPS 端口
    
    # 飞书配置（从环境变量读取）
    FEISHU_APP_ID = os.getenv('FEISHU_APP_ID', '')
    FEISHU_APP_SECRET = os.getenv('FEISHU_APP_SECRET', '')
    FEISHU_USER_OPEN_ID = os.getenv('FEISHU_USER_OPEN_ID', '')  # 需要使用当前应用对应的 Open ID
    FEISHU_RECEIVE_ID_TYPE = os.getenv('FEISHU_RECEIVE_ID_TYPE', 'open_id')  # open_id 或 user_id
    
    # 会话配置
    SESSION_TIMEOUT_HOURS = 24  # 审批通过后有效期
    PENDING_TIMEOUT_MINUTES = 30  # 待审批超时时间
    
    # 数据目录
    DATA_DIR = Path('/root/.openclaw/workspace/webviewer/data')
    WWW_DIR = Path('/root/.openclaw/workspace/webviewer/www')
    ACCESS_LOG_FILE = DATA_DIR / 'access_log.jsonl'
    PENDING_APPROVALS_FILE = DATA_DIR / 'pending_approvals.json'
    APPROVED_SESSIONS_FILE = DATA_DIR / 'approved_sessions.json'
    
    # 白名单 IP（已关闭，所有访问都需要审批）
    WHITELIST_IPS = []

# ==================== 数据管理 ====================

class DataManager:
    """管理访问日志和审批状态"""
    
    def __init__(self):
        self.data_dir = Config.DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.pending_file = Config.PENDING_APPROVALS_FILE
        self.sessions_file = Config.APPROVED_SESSIONS_FILE
        self.log_file = Config.ACCESS_LOG_FILE
        
        # 加载数据
        self.pending_approvals = self._load_json(self.pending_file, {})
        self.approved_sessions = self._load_json(self.sessions_file, {})
        
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
        """清理过期的待审批和会话"""
        now = time.time()
        pending_timeout = now - (Config.PENDING_TIMEOUT_MINUTES * 60)
        session_timeout = now - (Config.SESSION_TIMEOUT_HOURS * 3600)
        
        # 清理过期待审批
        self.pending_approvals = {
            k: v for k, v in self.pending_approvals.items()
            if v.get('timestamp', 0) > pending_timeout
        }
        
        # 清理过期会话
        self.approved_sessions = {
            k: v for k, v in self.approved_sessions.items()
            if v.get('expires_at', 0) > session_timeout
        }
        
        self._save_json(self.pending_file, self.pending_approvals)
        self._save_json(self.sessions_file, self.approved_sessions)
    
    def log_access(self, visitor_info):
        """记录访问日志"""
        log_entry = {
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat(),
            **visitor_info
        }
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def create_pending_approval(self, visitor_info):
        """创建待审批记录"""
        approval_id = str(uuid.uuid4())
        verification_code = hashlib.md5(approval_id.encode()).hexdigest()[:6].upper()
        
        self.pending_approvals[approval_id] = {
            'approval_id': approval_id,
            'verification_code': verification_code,
            'visitor_info': visitor_info,
            'timestamp': time.time(),
            'status': 'pending'  # pending, approved, rejected
        }
        
        self._save_json(self.pending_file, self.pending_approvals)
        return self.pending_approvals[approval_id]
    
    def approve_access(self, approval_id):
        """审批通过"""
        if approval_id not in self.pending_approvals:
            return False, 'Approval not found'
        
        record = self.pending_approvals[approval_id]
        visitor_info = record['visitor_info']
        
        # 创建会话
        session_id = str(uuid.uuid4())
        self.approved_sessions[session_id] = {
            'session_id': session_id,
            'ip': visitor_info.get('ip'),
            'approved_at': time.time(),
            'expires_at': time.time() + (Config.SESSION_TIMEOUT_HOURS * 3600),
            'approval_id': approval_id
        }
        
        # 更新审批记录
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
        """检查会话是否有效"""
        if session_id not in self.approved_sessions:
            return False
        
        session = self.approved_sessions[session_id]
        if session['expires_at'] < time.time():
            del self.approved_sessions[session_id]
            self._save_json(self.sessions_file, self.approved_sessions)
            return False
        
        return True
    
    def get_pending_count(self):
        """获取待审批数量"""
        return len([v for v in self.pending_approvals.values() if v['status'] == 'pending'])

# 全局数据管理器
data_manager = DataManager()

# ==================== 飞书通知 ====================

class FeishuNotifier:
    """飞书消息通知（简化版 - 使用 openclaw 通道）"""
    
    @staticmethod
    def send_approval_request(visitor_info, approval_id):
        """发送审批请求 - 打印到日志，由 openclaw 转发"""
        try:
            verify_code = data_manager.pending_approvals[approval_id]['verification_code']
            server_ip = socket.gethostbyname(socket.gethostname())
            
            # 构建审批信息
            msg = f"""
🔐 WebViewer 访问审批请求

🌐 访问来源：{visitor_info.get('ip', 'Unknown')}
🖥️ 设备：{visitor_info.get('user_agent', 'Unknown')[:50]}...
📍 位置：{visitor_info.get('location', 'Unknown')}
⏰ 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

审批链接:
✅ 同意：https://{server_ip}:{Config.HTTPS_PORT}/approve/{approval_id}
❌ 拒绝：https://{server_ip}:{Config.HTTPS_PORT}/reject/{approval_id}

验证码：{verify_code}
"""
            print("=" * 60)
            print("📢 审批请求（请通过 openclaw 飞书通道转发）:")
            print(msg)
            print("=" * 60)
            
            # TODO: 集成 openclaw message API
            # 目前通过日志输出，管理员可以查看 pending 页面审批
            
            return True
            
        except Exception as e:
            print(f"❌ 发送通知失败：{e}")
            return False

# ==================== HTTP 请求处理 ====================

class WebViewerHandler(SimpleHTTPRequestHandler):
    """WebViewer 请求处理器（带访问审核）"""
    
    def get_visitor_info(self):
        """获取访问者信息"""
        # 获取真实 IP（考虑代理）
        ip = self.headers.get('X-Forwarded-For', self.client_address[0])
        if ',' in ip:
            ip = ip.split(',')[0].strip()
        
        return {
            'ip': ip,
            'user_agent': self.headers.get('User-Agent', 'Unknown'),
            'path': self.path,
            'method': self.command,
            'location': self._get_location(ip)
        }
    
    def _get_location(self, ip):
        """根据 IP 获取地理位置（简化版）"""
        # 实际项目中可以调用 IP 地理位置 API
        if ip.startswith('192.168.') or ip.startswith('10.') or ip == '127.0.0.1':
            return '内网'
        return '未知'
    
    def check_access(self):
        """检查访问权限"""
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
    
    def do_GET(self):
        """处理 GET 请求"""
        # 特殊路径处理
        if self.path.startswith('/approve/'):
            self.handle_approval(True)
            return
        elif self.path.startswith('/reject/'):
            self.handle_approval(False)
            return
        elif self.path == '/pending':
            self.show_pending_page()
            return
        
        # 检查访问权限
        allowed, session_id, visitor_info = self.check_access()
        
        if allowed:
            # 正常访问
            super().do_GET()
            return
        
        # 需要审批
        # 记录访问日志
        data_manager.log_access(visitor_info)
        
        # 创建审批请求
        approval_record = data_manager.create_pending_approval(visitor_info)
        approval_id = approval_record['approval_id']
        
        # 发送飞书通知
        FeishuNotifier.send_approval_request(visitor_info, approval_id)
        
        # 显示等待页面
        self.show_waiting_page(approval_id)
    
    def show_waiting_page(self, approval_id):
        """显示等待审批页面"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        html = f'''
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
            margin-bottom: 20px;
        }}
        .status-label {{ color: #6b7280; font-size: 14px; }}
        .status-value {{ color: #1f2937; font-weight: 600; margin-top: 5px; }}
        .spinner {{
            border: 3px solid #f3f4f6;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }}
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        .note {{
            font-size: 13px;
            color: #9ca3af;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">🔐</div>
        <h1>等待访问审批</h1>
        <p>您的访问请求已提交，正在等待管理员审批。<br>审批结果将通过飞书通知。</p>
        
        <div class="status">
            <div class="status-label">申请 ID</div>
            <div class="status-value">{approval_id[:8]}...</div>
        </div>
        
        <div class="spinner"></div>
        
        <p class="note">
            页面将自动刷新检查审批状态<br>
            如长时间未响应，请联系管理员
        </p>
    </div>
    
    <script>
        // 每 5 秒检查一次审批状态
        setTimeout(() => {{
            fetch('/check-status/{approval_id}')
                .then(r => r.json())
                .then(data => {{
                    if (data.status === 'approved') {{
                        window.location.reload();
                    }} else if (data.status === 'rejected') {{
                        document.querySelector('h1').textContent = '❌ 访问已拒绝';
                        document.querySelector('p').textContent = '您的访问请求已被管理员拒绝。';
                        document.querySelector('.spinner').remove();
                    }}
                }});
        }}, 5000);
    </script>
</body>
</html>
'''
        self.wfile.write(html.encode('utf-8'))
    
    def show_pending_page(self):
        """显示待审批列表（管理页面）"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        pending_list = [v for v in data_manager.pending_approvals.values() if v['status'] == 'pending']
        
        rows = ''
        for p in pending_list:
            visitor = p['visitor_info']
            rows += f'''
            <tr>
                <td>{p['approval_id'][:8]}...</td>
                <td>{visitor.get('ip', 'Unknown')}</td>
                <td>{visitor.get('user_agent', 'Unknown')[:30]}...</td>
                <td>{datetime.fromtimestamp(p['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}</td>
                <td>
                    <a href="/approve/{p['approval_id']}" style="color:green;margin-right:10px;">✅ 同意</a>
                    <a href="/reject/{p['approval_id']}" style="color:red;">❌ 拒绝</a>
                </td>
            </tr>
            '''
        
        html = f'''
<!DOCTYPE html>
<html>
<head>
    <title>待审批列表</title>
    <style>
        body {{ font-family: sans-serif; padding: 20px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background: #667eea; color: white; }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
    </style>
</head>
<body>
    <h1>🔐 待审批访问请求 ({len(pending_list)})</h1>
    <table>
        <tr>
            <th>申请 ID</th>
            <th>IP 地址</th>
            <th>设备信息</th>
            <th>申请时间</th>
            <th>操作</th>
        </tr>
        {rows if rows else '<tr><td colspan="5">暂无待审批请求</td></tr>'}
    </table>
    <p style="margin-top:20px;"><a href="/">← 返回首页</a></p>
</body>
</html>
'''
        self.wfile.write(html.encode('utf-8'))
    
    def handle_approval(self, is_approved):
        """处理审批请求"""
        approval_id = self.path.split('/')[-1]
        
        if is_approved:
            success, result = data_manager.approve_access(approval_id)
            status = 'approved' if success else 'error'
        else:
            success, result = data_manager.reject_access(approval_id)
            status = 'rejected' if success else 'error'
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            'success': success,
            'status': status,
            'message': result if isinstance(result, str) else ('Approved' if is_approved else 'Rejected')
        }
        
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def do_POST(self):
        """处理 POST 请求（飞书卡片回调）"""
        if self.path == '/api/approval':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)
            
            # 处理飞书卡片按钮点击
            approval_id = data.get('approval_id')
            action = data.get('type')
            
            if approval_id and action:
                if action == 'approve':
                    data_manager.approve_access(approval_id)
                elif action == 'reject':
                    data_manager.reject_access(approval_id)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"success": true}')
        else:
            super().do_POST()

# ==================== 主程序 ====================

def run_server():
    """启动 HTTPS 服务器"""
    import ssl
    
    server_address = (Config.HOST, Config.HTTPS_PORT)
    httpd = HTTPServer(server_address, WebViewerHandler)
    
    # 配置 SSL（自签名证书）
    cert_file = Config.DATA_DIR / 'server.crt'
    key_file = Config.DATA_DIR / 'server.key'
    
    if cert_file.exists() and key_file.exists():
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=str(cert_file), keyfile=str(key_file))
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
        print(f"🔒 HTTPS 服务器已启动")
    else:
        print(f"⚠️ SSL 证书未找到，使用 HTTP 模式")
    
    print(f"📡 监听地址：https://{socket.gethostbyname(socket.gethostname())}:{Config.HTTPS_PORT}")
    print(f"📋 管理页面：https://...:{Config.HTTPS_PORT}/pending")
    print(f"📜 按 Ctrl+C 停止服务")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 正在关闭服务...")
        httpd.shutdown()

if __name__ == '__main__':
    run_server()
