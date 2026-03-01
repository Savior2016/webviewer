#!/usr/bin/env python3
"""
WebViewer 消息处理器
监听 Feishu 消息，处理来自 Web 页面的请求
"""

import json
import os
import time
from pathlib import Path
from datetime import datetime

class WebViewerMessageHandler:
    def __init__(self):
        self.result_dir = Path("/root/.openclaw/workspace/webviewer/data/results")
        self.result_dir.mkdir(parents=True, exist_ok=True)
        
    def handle_web_message(self, message: str, user_id: str = "ou_67455f002e1316b6b05e4f3020ae2ff5"):
        """
        处理来自 Web 页面的消息
        根据消息内容调用相应的功能
        """
        import sys
        sys.path.insert(0, "/root/.openclaw/workspace/webviewer")
        
        # 导入消息处理引擎
        from message_engine import processor
        
        # 解析意图
        project, action, params = processor.parse_intent(message)
        print(f"📊 解析结果：project={project}, action={action}, params={params}")
        
        # 处理消息
        success, result_message = processor.process(project, action, params)
        
        # 生成消息 ID
        import uuid
        msg_id = str(uuid.uuid4())
        
        # 保存结果
        result_data = {
            "msg_id": msg_id,
            "user_id": user_id,
            "original_message": message,
            "project": project,
            "action": action,
            "success": success,
            "result": result_message,
            "timestamp": int(time.time()),
            "processed_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        result_file = self.result_dir / f"{msg_id}.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 消息已处理：{msg_id}")
        print(f"   项目：{project}")
        print(f"   结果：{result_message[:100]}...")
        
        return result_data
    
    def send_to_feishu(self, message: str, user_open_id: str = None):
        """通过 Feishu API 发送消息
        
        注意：APP_ID 和 APP_SECRET 应从环境变量或配置文件中读取
        不要硬编码在代码中！
        
        示例：
            export FEISHU_APP_ID="your_app_id"
            export FEISHU_APP_SECRET="your_app_secret"
        """
        import requests
        
        # 从环境变量读取（安全做法）
        APP_ID = os.getenv("FEISHU_APP_ID", "")
        APP_SECRET = os.getenv("FEISHU_APP_SECRET", "")
        
        if not APP_ID or not APP_SECRET:
            raise ValueError("Feishu APP_ID 和 APP_SECRET 未配置，请设置环境变量")
        
        # 获取 token
        token_response = requests.post(
            "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
            json={"app_id": APP_ID, "app_secret": APP_SECRET},
            timeout=10
        )
        
        tenant_token = token_response.json().get('tenant_access_token', '')
        headers = {
            "Authorization": f"Bearer {tenant_token}",
            "Content-Type": "application/json"
        }
        
        # 发送消息
        send_response = requests.post(
            "https://open.feishu.cn/open-apis/im/v1/messages",
            headers=headers,
            params={"receive_id_type": "open_id"},
            json={
                "receive_id": user_open_id,
                "content": json.dumps({"text": message}, ensure_ascii=False),
                "msg_type": "text"
            },
            timeout=10
        )
        
        return send_response.json()


# 全局实例
handler = WebViewerMessageHandler()

if __name__ == "__main__":
    # 测试
    test_message = "我要出差 3 天，帮我创建一个出行清单"
    result = handler.handle_web_message(test_message)
    print(f"\n处理结果：{json.dumps(result, ensure_ascii=False, indent=2)}")
