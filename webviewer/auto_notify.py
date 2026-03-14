#!/usr/bin/env python3
"""
WebViewer 自动审批通知
监控待审批列表，通过 OpenClaw 飞书通道发送通知
"""

import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

PENDING_FILE = Path('/root/.openclaw/workspace/webviewer/data/pending_approvals.json')
STATE_FILE = Path('/root/.openclaw/workspace/webviewer/data/notify_state.json')
USER_IP = '43.153.153.62'  # 用户外网 IP
INTERNAL_IP = '221.219.243.106'  # 用户内网 IP

def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {'notified': [], 'approved': []}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def send_feishu_message(title, content, approval_id=None):
    """通过 OpenClaw 发送飞书消息"""
    cmd = [
        'openclaw', 'message', 'send',
        '--channel', 'feishu',
        '--target', 'ou_67455f002e1316b6b05e4f3020ae2ff5',
        '--message', f'{title}\n\n{content}'
    ]
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return True
    except:
        return False

def approve_access(approval_id):
    """批准访问"""
    cmd = [
        'python3', '-c',
        f'import sys; sys.path.insert(0, "."); from server_with_approval import data_manager; data_manager.approve_access("{approval_id}")'
    ]
    try:
        subprocess.run(cmd, cwd='/root/.openclaw/workspace/webviewer', capture_output=True, timeout=5)
        return True
    except:
        return False

def check_pending():
    """检查待审批列表"""
    if not PENDING_FILE.exists():
        return []
    
    with open(PENDING_FILE) as f:
        return json.load(f)

def main():
    print(f"🔍 开始监控待审批请求...")
    state = load_state()
    
    pending = check_pending()
    new_count = 0
    
    for approval_id, record in pending.items():
        if approval_id in state['notified']:
            continue
        
        ip = record['visitor_info'].get('ip', 'Unknown')
        ua = record['visitor_info'].get('user_agent', 'Unknown')[:50]
        path = record['visitor_info'].get('path', '/')
        timestamp = datetime.fromtimestamp(record.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S')
        
        # 发送通知
        title = f"🔐 WebViewer 访问审批"
        content = f"""🌐 IP: {ip}
🖥️ 设备：{ua}
📁 路径：{path}
⏰ 时间：{timestamp}

回复 **同意** 批准 | 回复 **拒绝** 拒绝"""
        
        print(f"📢 发送通知：{ip} - {path}")
        send_feishu_message(title, content, approval_id)
        state['notified'].append(approval_id)
        new_count += 1
    
    # 清理旧记录（保留最近 100 条）
    if len(state['notified']) > 100:
        state['notified'] = state['notified'][-100:]
    if len(state['approved']) > 100:
        state['approved'] = state['approved'][-100:]
    
    save_state(state)
    print(f"✅ 检查完成，新通知：{new_count} 条")

if __name__ == '__main__':
    main()
