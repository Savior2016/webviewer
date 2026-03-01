#!/usr/bin/env python3
"""
通过 Shell 调用 OpenClaw 处理 WebViewer 消息
优化版本：更好的 JSON 提取和错误处理
"""

import subprocess
import json
import re
import uuid
from pathlib import Path

def process_via_openclaw_shell(message: str) -> dict:
    """
    通过 Shell 调用 OpenClaw 处理消息
    """
    
    # 构建系统提示词
    system_prompt = """你是一个智能助手，帮助用户管理 webviewer 的三个项目。

用户消息："{message}"

请理解意图并选择合适的项目：
1. 出行相关（出差、旅行、出行）→ By Design (/bydesign/)
2. 搬家相关（搬家、打包、物品记录）→ Cherry Pick (/cherry-pick/)
3. 物品相关（找、查询、记录位置）→ Momhand (/momhand/)

必须返回 JSON 格式：
{{
  "success": true,
  "project": "bydesign 或 cherry_pick 或 momhand",
  "action": "操作类型",
  "message": "友好的回复",
  "refresh": "/页面路径/",
  "data": {{}}
}}

只返回 JSON，不要其他内容。"""

    full_prompt = system_prompt.format(message=message)
    
    print(f"📤 发送消息到 OpenClaw: {message[:50]}...")
    
    try:
        # 生成 session-id
        session_id = f"webviewer_{uuid.uuid4().hex[:8]}"
        
        # 构建命令
        cmd = [
            'openclaw',
            'agent',
            '--local',
            '--session-id', session_id,
            '--message', full_prompt,
            '--thinking', 'minimal',
            '--json',
            '--log-level', 'error'  # 减少日志输出
        ]
        
        print(f"🔧 执行：openclaw agent --local --session-id {session_id} ...")
        
        # 执行命令
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        print(f"✅ 执行完成，返回码：{result.returncode}")
        
        # 合并 stdout 和 stderr
        full_output = result.stdout + result.stderr
        
        # 提取 JSON
        json_data = extract_json_from_output(full_output)
        
        if json_data:
            print(f"✅ JSON 解析成功")
            json_data['processed_by'] = 'openclaw_shell'
            return json_data
        else:
            print(f"⚠️  无法解析 JSON，使用 fallback")
            return process_local_fallback(message)
            
    except subprocess.TimeoutExpired:
        print(f"❌ 超时")
        return {
            "success": False,
            "message": "处理超时",
            "processed_by": "timeout"
        }
    except Exception as e:
        print(f"❌ 错误：{e}")
        return process_local_fallback(message)


def extract_json_from_output(output: str) -> dict:
    """
    从输出中提取 JSON
    """
    print(f"📝 尝试从输出中提取 JSON...")
    
    # 清理输出
    output = output.strip()
    
    # 尝试 1: 直接解析（如果是纯 JSON）
    try:
        return json.loads(output)
    except:
        pass
    
    # 尝试 2: 查找 JSON 对象
    # 匹配 { ... } 结构
    json_pattern = r'\{[^{}]*"success"[^{}]*\}'
    match = re.search(json_pattern, output, re.DOTALL)
    
    if match:
        json_str = match.group(0)
        print(f"📦 找到 JSON: {json_str[:100]}...")
        try:
            return json.loads(json_str)
        except Exception as e:
            print(f"⚠️  解析失败：{e}")
    
    # 尝试 3: 查找代码块中的 JSON
    code_pattern = r'```(?:json)?\s*({.*?})\s*```'
    match = re.search(code_pattern, output, re.DOTALL)
    
    if match:
        json_str = match.group(1)
        try:
            return json.loads(json_str)
        except:
            pass
    
    # 尝试 4: 清理日志后解析
    # 移除 [xxx] 格式的日志行
    cleaned = re.sub(r'\[.*?\]\s*.*?\n', '', output)
    cleaned = cleaned.strip()
    
    # 查找第一个 { 和最后一个 }
    start = cleaned.find('{')
    end = cleaned.rfind('}') + 1
    
    if start >= 0 and end > start:
        json_str = cleaned[start:end]
        try:
            return json.loads(json_str)
        except:
            pass
    
    print(f"❌ 无法提取 JSON，输出：{output[:200]}...")
    return None


def process_local_fallback(message: str) -> dict:
    """本地引擎 fallback"""
    import sys
    sys.path.insert(0, "/root/.openclaw/workspace/webviewer")
    from message_engine import processor
    
    print(f"🔄 使用本地引擎处理")
    
    project, action, params = processor.parse_intent(message)
    success, result_message = processor.process(project, action, params)
    
    return {
        "success": success,
        "project": project,
        "action": action,
        "message": result_message,
        "refresh": f"/{project}/" if project != 'unknown' else None,
        "data": params,
        "processed_by": "local_fallback"
    }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
        result = process_via_openclaw_shell(message)
        print("\n📊 结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
