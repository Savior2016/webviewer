#!/usr/bin/env python3
"""
通过 OpenClaw Agent 处理 WebViewer 消息
使用命令：openclaw agent --agent dummy -m "消息内容"

⚠️ 修复历史：
- 2026-02-28: 添加超时保护，防止长消息导致服务崩溃
- 超时从 60 秒缩短到 30 秒
- 添加直接解析意图的后备方案
"""

import subprocess
import json
import re
from pathlib import Path
import threading

class TimeoutError(Exception):
    pass


def run_with_timeout(func, args=(), kwargs=None, timeout=30):
    """
    带超时控制的函数执行
    """
    if kwargs is None:
        kwargs = {}
    
    result = [None]
    exception = [None]
    
    def target():
        try:
            result[0] = func(*args, **kwargs)
        except Exception as e:
            exception[0] = e
    
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    thread.join(timeout)
    
    if thread.is_alive():
        raise TimeoutError(f"函数执行超时（{timeout}秒）")
    
    if exception[0]:
        raise exception[0]
    
    return result[0]


def process_via_openclaw_agent(message: str) -> dict:
    """
    通过 OpenClaw Agent 处理消息
    
    Args:
        message: 用户消息
    
    Returns:
        处理结果字典
    """
    
    # 构建系统提示词（要求不仅返回操作，还要执行记录）
    system_prompt = """理解这些信息的意图，并选择 webviewer 中合适的模块保存这些信息，然后刷新页面的显示。

用户消息："{message}"

可用项目：
1. 出行相关（出差、旅行、出行）→ By Design (/bydesign/)
   - 动作：创建出行记录
   - API: POST /bydesign/api/trips
   - 数据：{{name, description}}

2. 搬家相关（搬家、打包、物品记录）→ Cherry Pick (/cherry-pick/)
   - 动作：记录物品位置
   - API: POST /cherry-pick/api/moves/{{moveId}}/items
   - 数据：{{name, before_location, after_location}}

3. 物品相关（找、查询、记录位置）→ Momhand (/momhand/)
   - 动作：添加/搜索物品
   - API: POST /momhand/api/items 或 GET /momhand/api/search?q=xxx
   - 数据：{{name, type, location, usage}}

请：
1. 理解用户意图
2. 选择合适的项目
3. **执行具体的记录动作**（调用相应的 API 保存数据）
4. 返回确认消息

返回 JSON 格式：
{{
  "success": true,
  "project": "bydesign 或 cherry_pick 或 momhand",
  "action": "操作类型",
  "message": "友好的回复，确认已保存",
  "refresh": "/页面路径/",
  "data": {{保存的数据}}
}}"""

    full_prompt = system_prompt.format(message=message)
    
    print(f"📤 发送消息到 OpenClaw Agent: {message[:50]}...")
    
    try:
        # 使用超时控制执行
        result = run_with_timeout(
            _execute_openclaw_command,
            args=(full_prompt,),
            timeout=30
        )
        
        if result:
            print(f"✅ JSON 解析成功")
            result['processed_by'] = 'openclaw_agent'
            return result
        else:
            # 没有 JSON，尝试直接解析意图
            print(f"⚠️  无 JSON，尝试直接解析")
            return parse_intent_directly(message)
            
    except TimeoutError:
        print(f"❌ 超时（30 秒）")
        return {
            "success": False,
            "message": "处理超时，请稍后重试",
            "processed_by": "timeout",
            "error": "OpenClaw Agent 响应超时"
        }
    except Exception as e:
        print(f"❌ 错误：{e}")
        return {
            "success": False,
            "message": f"处理失败：{str(e)}",
            "processed_by": "error"
        }


def _execute_openclaw_command(full_prompt: str) -> dict:
    """
    执行 OpenClaw 命令（内部函数，用于超时控制）
    """
    cmd = [
        'openclaw',
        'agent',
        '--agent', 'dummy',
        '-m', full_prompt
    ]
    
    print(f"🔧 执行：openclaw agent --agent dummy -m \"...\"")
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=30  # subprocess 级别的超时
    )
    
    print(f"✅ 执行完成，返回码：{result.returncode}")
    
    full_output = result.stdout + result.stderr
    json_data = extract_json_from_output(full_output)
    
    if json_data:
        return json_data
    else:
        return None


def parse_intent_directly(message: str) -> dict:
    """
    直接解析用户意图（AI 超时时的后备方案）
    """
    msg = message.lower()
    
    # By Design - 出行相关
    if any(kw in msg for kw in ['出差', '旅行', '出行', ' trip', ' travel']):
        return {
            "success": True,
            "project": "bydesign",
            "action": "create_trip",
            "message": "✅ 已理解出行意图，但由于 AI 处理超时，请手动创建出行记录",
            "refresh": "/bydesign/",
            "data": {},
            "processed_by": "direct_parse"
        }
    
    # Cherry Pick - 搬家相关
    if any(kw in msg for kw in ['搬家', '打包', 'cherry', 'move']):
        return {
            "success": True,
            "project": "cherry_pick",
            "action": "add_item",
            "message": "✅ 已理解搬家意图，但由于 AI 处理超时，请手动添加物品",
            "refresh": "/cherry-pick/",
            "data": {},
            "processed_by": "direct_parse"
        }
    
    # Momhand - 物品相关
    if any(kw in msg for kw in ['物品', '东西', '放在', '位置', '找', 'momhand']):
        return {
            "success": True,
            "project": "momhand",
            "action": "add_item",
            "message": "✅ 已理解物品意图，但由于 AI 处理超时，请手动添加",
            "refresh": "/momhand/",
            "data": {},
            "processed_by": "direct_parse"
        }
    
    # 检查清单相关
    if any(kw in msg for kw in ['检查', '清单', 'checklist']):
        return {
            "success": True,
            "project": "bydesign",
            "action": "add_checklist",
            "message": "✅ 已理解检查清单意图，但由于 AI 处理超时，请手动添加",
            "refresh": "/bydesign/",
            "data": {},
            "processed_by": "direct_parse"
        }
    
    # 默认返回
    return {
        "success": True,
        "project": "unknown",
        "message": "消息已接收，但无法自动处理，请手动操作",
        "refresh": None,
        "data": {},
        "processed_by": "direct_parse"
    }


def extract_json_from_output(output: str) -> dict:
    """从输出中提取 JSON"""
    print(f"📝 尝试从输出中提取 JSON...")
    
    # 清理输出（移除日志行）
    lines = output.split('\n')
    clean_lines = []
    for line in lines:
        # 跳过日志行
        if line.startswith('[plugins]') or line.startswith('gateway') or line.startswith('Error:'):
            continue
        clean_lines.append(line)
    
    cleaned = '\n'.join(clean_lines).strip()
    
    # 尝试 1: 直接解析
    try:
        return json.loads(cleaned)
    except:
        pass
    
    # 尝试 2: 查找 JSON 对象
    json_pattern = r'\{[^{}]*"success"[^{}]*\}'
    match = re.search(json_pattern, cleaned, re.DOTALL)
    
    if match:
        json_str = match.group(0)
        print(f"📦 找到 JSON: {json_str[:100]}...")
        try:
            return json.loads(json_str)
        except Exception as e:
            print(f"⚠️  解析失败：{e}")
    
    # 尝试 3: 查找代码块
    code_pattern = r'```(?:json)?\s*({.*?})\s*```'
    match = re.search(code_pattern, cleaned, re.DOTALL)
    
    if match:
        try:
            return json.loads(match.group(1))
        except:
            pass
    
    return None


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
        result = process_via_openclaw_agent(message)
        print("\n📊 结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
