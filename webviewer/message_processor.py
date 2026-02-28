#!/usr/bin/env python3
"""
消息队列处理器
定期检查 WebViewer 消息队列并发送到 Feishu
"""

import json
import os
import time
import subprocess
from pathlib import Path

MSG_DIR = Path("/root/.openclaw/workspace/webviewer/data/messages")
PROCESSED_DIR = MSG_DIR / "processed"

# 确保目录存在
MSG_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def process_messages():
    """处理消息队列"""
    print("📬 开始检查消息队列...")
    
    msg_files = list(MSG_DIR.glob("msg_*.json"))
    
    if not msg_files:
        print("  暂无新消息")
        return
    
    for msg_file in msg_files:
        try:
            with open(msg_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            message = data.get('message', '')
            timestamp = data.get('timestamp', '')
            
            print(f"\n📨 处理消息：{message[:50]}...")
            
            # 使用 openclaw message send 发送到 Feishu
            # 注意：这里需要正确的 target 配置
            # 由于是 DM，我们可以使用当前用户的 ID
            
            # 方法 1: 使用 broadcast 发送到所有 Feishu 通道
            cmd = [
                'openclaw',
                'message',
                'broadcast',
                '--channel', 'feishu',
                '--message', f'🌐 [来自 WebViewer 的消息]\n\n{message}'
            ]
            
            print(f"  执行命令：{' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"  ✅ 发送成功")
                # 移动到已处理目录
                msg_file.rename(PROCESSED_DIR / msg_file.name)
            else:
                print(f"  ❌ 发送失败：{result.stderr}")
                # 重命名为错误文件
                error_file = msg_file.with_suffix('.json.error')
                msg_file.rename(error_file)
                
        except Exception as e:
            print(f"  ❌ 处理失败：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("🚀 消息队列处理器启动")
    print(f"📂 监控目录：{MSG_DIR}")
    
    while True:
        process_messages()
        time.sleep(5)  # 每 5 秒检查一次
