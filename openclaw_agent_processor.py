#!/usr/bin/env python3
"""
通过 OpenClaw Agent 处理 WebViewer 消息
使用命令：openclaw agent --agent dummy -m "消息内容"

⚠️ 修复历史：
- 2026-02-28: 添加超时保护，防止长消息导致服务崩溃
- 超时从 60 秒缩短到 30 秒
- 添加直接解析意图的后备方案
- 2026-03-03: 系统提示词从各模块独立设置文件读取，动态拼接
"""

import subprocess
import json
import re
import os
from pathlib import Path
import threading


# 各模块提示词配置文件路径
MODULE_PROMPTS = {
    'bydesign': Path("/root/.openclaw/workspace/www/bydesign/data/settings.json"),
    'cherry_pick': Path("/root/.openclaw/workspace/www/cherry-pick/data/settings.json"),
    'momhand': Path("/root/.openclaw/workspace/www/momhand/data/settings.json"),
    'siri_dream': Path("/root/.openclaw/workspace/data/siri-dream/settings.json")
}

DEFAULT_PROMPT = """你是 WebViewer 的助手 Dummy，负责处理用户的出行、搬家和物品记录请求。

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

处理规则：
1. 如果用户想记录出行、搬家、物品等信息：
   - 选择合适的项目
   - **执行具体的记录动作**（调用相应的 API 保存数据）
   - 返回 success=true，包含 project、action、data、refresh

2. 如果用户是问候、闲聊、提问（如"你好"、"你是谁"、"能做什么"）：
   - 正常对话回复
   - 返回 success=false，project=null，action=null
   - message 字段回复用户的问题

**重要要求：**
- message 字段使用简洁的中文，**不要使用任何表情符号（emoji）**
- 只返回必要的文字信息，保持专业简洁

返回 JSON 格式：
{{
  "success": true/false,
  "project": "bydesign 或 cherry_pick 或 momhand 或 null",
  "action": "操作类型或 null",
  "message": "简洁的中文回复，不含表情符号",
  "refresh": "/页面路径/ 或 null",
  "data": {{保存的数据}} 或 null
}}"""


def get_module_prompt(module: str) -> str:
    """
    获取指定模块的系统提示词
    
    Args:
        module: 模块名 (bydesign, cherry_pick, momhand, siri_dream)
    
    Returns:
        系统提示词字符串
    """
    try:
        prompt_file = MODULE_PROMPTS.get(module)
        if prompt_file and prompt_file.exists():
            with open(prompt_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                prompt = settings.get('system_prompt', '')
                print(f"📝 加载 {module} 模块提示词：{prompt[:50]}...")
                return prompt
    except Exception as e:
        print(f"⚠️  读取 {module} 模块提示词失败：{e}")
    
    # 返回默认提示词
    return DEFAULT_PROMPT


def build_full_prompt(module: str, message: str) -> str:
    """
    构建完整的提示词（模块提示词 + 用户消息）
    """
    system_prompt = get_module_prompt(module)
    
    # JSON 格式要求
    json_format_requirement = """

**重要：必须返回以下 JSON 格式**
```json
{
  "success": true,
  "project": "bydesign|cherry_pick|momhand|null",
  "action": "操作类型或null",
  "message": "简洁的中文回复，不含emoji",
  "refresh": "/页面路径/ 或 null",
  "data": {}
}
```

项目映射：bydesign=出行, cherry_pick=搬家, momhand=物品, null=问候"""

    # 构建提示词（避免 format 的花括号问题）
    if '{message}' in system_prompt:
        base_prompt = system_prompt.replace('{message}', message)
    else:
        base_prompt = system_prompt + "\n\n用户消息：\n" + message
    
    return base_prompt + json_format_requirement

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


def process_via_openclaw_agent(message: str, module: str = 'siri_dream') -> dict:
    """
    通过 OpenClaw Agent 处理消息
    
    Args:
        message: 用户消息
        module: 模块名，用于选择对应的系统提示词 (默认 siri_dream)
    
    Returns:
        处理结果字典
    """
    
    # 构建完整提示词（从模块设置文件读取 + 用户消息）
    full_prompt = build_full_prompt(module, message)
    
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
    # 设置环境变量，确保能找到 openclaw 命令
    env = os.environ.copy()
    env['PATH'] = '/root/.nvm/versions/node/v22.22.0/bin:' + env.get('PATH', '')
    
    cmd = [
        '/root/.nvm/versions/node/v22.22.0/bin/openclaw',
        'agent',
        '--agent', 'dummy',
        '-m', full_prompt
    ]
    
    print(f"🔧 执行：openclaw agent --agent dummy -m \"...\"")
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=30,  # subprocess 级别的超时
        env=env  # 使用包含 node bin 目录的 PATH
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
    
    # 尝试 2: 查找 markdown 代码块中的 JSON（优先）
    # 匹配 ```json ... ``` 或 ``` ... ``` 格式
    code_block_patterns = [
        r'```json\s*\n([\s\S]*?)\n```',  # ```json\n{...}\n```
        r'```\s*\n([\s\S]*?)\n```',       # ```\n{...}\n```
        r'```json\s+([\s\S]*?)\n```',     # ```json {...}\n```
        r'```([\s\S]*?)```',              # ```{...}```
    ]
    
    for pattern in code_block_patterns:
        match = re.search(pattern, cleaned)
        if match:
            content = match.group(1).strip()
            print(f"📦 找到代码块: {content[:100]}...")
            try:
                return json.loads(content)
            except Exception as e:
                print(f"⚠️  代码块解析失败：{e}")
                continue
    
    # 尝试 3: 查找独立的 JSON 对象（包含 success 字段）
    # 使用更宽松的正则，匹配完整的 JSON 对象
    json_pattern = r'\{[\s\S]*?"success"[\s\S]*?\}'
    match = re.search(json_pattern, cleaned)
    
    if match:
        json_str = match.group(0)
        print(f"📦 找到 JSON: {json_str[:100]}...")
        try:
            return json.loads(json_str)
        except Exception as e:
            print(f"⚠️  解析失败：{e}")
    
    return None


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
        result = process_via_openclaw_agent(message)
        print("\n📊 结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
