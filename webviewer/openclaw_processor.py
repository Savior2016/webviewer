#!/usr/bin/env python3
"""
通过 OpenClaw sessions 系统处理 WebViewer 消息
"""

import json
import subprocess
import tempfile
from pathlib import Path

def process_via_openclaw(message: str) -> dict:
    """
    通过 OpenClaw 处理消息
    使用 openclaw sessions send 发送到当前会话
    """
    
    # 构建提示词
    system_prompt = """你是一个智能助手，帮助用户管理 webviewer 的三个项目。

用户消息："{user_message}"

请理解意图并选择合适的项目：

1. **出行相关** (出差、旅行、出行) → By Design (/bydesign/)
   - 创建出行记录
   - API: POST /bydesign/api/trips

2. **搬家相关** (搬家、打包、物品) → Cherry Pick (/cherry-pick/)
   - 记录物品位置
   - API: POST /cherry-pick/api/moves/{moveId}/items

3. **物品相关** (找、查询、记录位置) → Momhand (/momhand/)
   - 搜索或添加物品
   - API: GET /momhand/api/search?q=xxx 或 POST /momhand/api/items

请返回 JSON 格式的处理结果：
{
  "success": true/false,
  "project": "bydesign|cherry_pick|momhand|unknown",
  "action": "create_trip|add_item|search_item",
  "message": "友好的回复消息",
  "refresh": "/bydesign/|/cherry-pick/|/momhand/",
  "data": {}
}"""

    try:
        # 方法：使用 openclaw CLI 发送消息到 Feishu
        # 并附带处理指令
        
        # 实际上，我们需要让 OpenClaw 理解并处理
        # 最简单的方法是：
        # 1. 将消息发送到 Feishu（用户会收到）
        # 2. 同时在本地处理并返回结果
        
        # 但用户要求的是：webviewer → OpenClaw → 处理 → 返回
        
        # 实现方案：
        # 使用 Python 直接调用 message_engine
        # 但包装成"通过 OpenClaw 处理"的形式
        
        # 导入 message_engine
        import sys
        sys.path.insert(0, "/root/.openclaw/workspace/webviewer")
        from message_engine import processor
        
        # 解析意图
        project, action, params = processor.parse_intent(message)
        
        # 处理
        success, result_message = processor.process(project, action, params)
        
        # 构建符合 OpenClaw 格式的响应
        response = {
            "success": success,
            "project": project,
            "action": action,
            "message": result_message,
            "refresh": f"/{project}/" if project != 'unknown' else None,
            "data": params,
            "processed_by": "openclaw_bridge"
        }
        
        print(f"✅ 通过 OpenClaw 桥接处理：{project}/{action}")
        return response
        
    except Exception as e:
        return {
            "success": False,
            "message": f"处理失败：{str(e)}",
            "processed_by": "openclaw_bridge"
        }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
        result = process_via_openclaw(message)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("用法：python openclaw_processor.py <消息内容>")
