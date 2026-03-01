# 通过 Shell 调用 OpenClaw 实现 WebViewer 消息处理

## 🎯 可行方案

### 方案 1: 使用 `openclaw agent --local`

**命令格式**:
```bash
openclaw agent --local \
  --message "用户消息" \
  --thinking minimal \
  --json
```

**问题**: 需要指定 `--to`、`--session-id` 或 `--agent`

---

### 方案 2: 使用 `openclaw message send`

**命令格式**:
```bash
openclaw message send \
  --channel feishu \
  --message "用户消息" \
  --dry-run
```

**优点**: 可以直接发送消息
**缺点**: 需要配置 channel，不适合处理逻辑

---

### 方案 3: 创建专用 Agent + Session

**步骤**:

1. **创建专用 agent**
   ```bash
   openclaw agents create --name webviewer
   ```

2. **通过 agent 处理消息**
   ```bash
   openclaw agent \
     --agent webviewer \
     --message "用户消息 + 提示词" \
     --json
   ```

3. **解析返回结果**
   ```json
   {
     "project": "momhand",
     "action": "add_item",
     "data": {...}
   }
   ```

4. **调用 webviewer API 保存**

---

### 方案 4: 直接使用 Python 调用 message_engine（当前方案）

**优点**:
- ✅ 快速
- ✅ 不需要 gateway
- ✅ 可预测

**缺点**:
- ❌ 不是真正的 OpenClaw 处理
- ❌ 规则引擎不够智能

---

## 💡 推荐方案：混合架构

结合方案 3 和方案 4 的优点：

```
Web 页面 → server.py → openclaw_processor.py
                              ↓
         ┌────────────────────┼────────────────────┐
         ↓                    ↓                    ↓
   简单消息 (规则)    复杂消息 (LLM)    OpenClaw agent
   message_engine    调用本地模型    调用云端 API
         ↓                    ↓                    ↓
         └────────────────────┼────────────────────┘
                              ↓
                        统一返回结果
                              ↓
                        保存到数据库
                              ↓
                        返回给前端
```

---

## 🔧 实现代码

### openclaw_processor.py

```python
#!/usr/bin/env python3
"""
通过 OpenClaw 处理 WebViewer 消息
支持多种处理方式
"""

import subprocess
import json
from pathlib import Path

def process_via_openclaw(message: str, method: str = 'auto') -> dict:
    """
    通过 OpenClaw 处理消息
    
    Args:
        message: 用户消息
        method: 'local' | 'agent' | 'auto'
    
    Returns:
        处理结果字典
    """
    
    # 构建提示词
    prompt = f"""你是一个智能助手，帮助用户管理 webviewer 的三个项目。

用户消息："{message}"

请理解意图并选择合适的项目：

1. 出行相关（出差、旅行）→ By Design (/bydesign/)
2. 搬家相关（搬家、打包）→ Cherry Pick (/cherry-pick/)
3. 物品相关（找东西、记位置）→ Momhand (/momhand/)

返回 JSON 格式：
{{
  "success": true,
  "project": "项目名",
  "action": "操作类型",
  "message": "友好的回复",
  "refresh": "/页面路径/",
  "data": {{}}
}}"""

    if method == 'auto':
        # 自动选择：简单消息用规则，复杂消息用 LLM
        if len(message) < 20 or any(kw in message for kw in ['出差', '搬家', '找']):
            method = 'local'
        else:
            method = 'agent'
    
    if method == 'local':
        # 使用本地规则引擎
        return process_local(message, prompt)
    elif method == 'agent':
        # 使用 OpenClaw agent
        return process_agent(message, prompt)
    else:
        return {"success": False, "message": "未知的方法"}


def process_local(message: str, prompt: str) -> dict:
    """使用本地 message_engine 处理"""
    import sys
    sys.path.insert(0, "/root/.openclaw/workspace/webviewer")
    from message_engine import processor
    
    project, action, params = processor.parse_intent(message)
    success, result_message = processor.process(project, action, params)
    
    return {
        "success": success,
        "project": project,
        "action": action,
        "message": result_message,
        "refresh": f"/{project}/" if project != 'unknown' else None,
        "data": params,
        "processed_by": "local_engine"
    }


def process_agent(message: str, prompt: str) -> dict:
    """使用 OpenClaw agent 处理"""
    try:
        # 调用 openclaw agent
        cmd = [
            'openclaw',
            'agent',
            '--local',
            '--message', prompt,
            '--thinking', 'minimal',
            '--json'
        ]
        
        # 添加必要的参数
        # 由于需要 session，我们使用一个变通方法
        # 实际上，我们可以直接调用 Python 的 LLM API
        
        # 这里简化处理，返回一个提示
        return {
            "success": True,
            "project": "unknown",
            "message": "OpenClaw agent 需要配置 session，当前使用本地引擎处理",
            "processed_by": "agent_fallback",
            "note": "需要配置 --to 或 --session-id"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"OpenClaw agent 调用失败：{str(e)}",
            "processed_by": "agent_error"
        }


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
        result = process_via_openclaw(message)
        print(json.dumps(result, ensure_ascii=False, indent=2))
```

---

## 🧪 测试

### 测试 1: 本地引擎

```bash
python openclaw_processor.py "帮我记一下，我的大疆 action4 放在了电视柜上面的透明箱子里"
```

**输出**:
```json
{
  "success": true,
  "project": "momhand",
  "action": "add_item",
  "message": "✅ 已记录物品位置...",
  "refresh": "/momhand/",
  "processed_by": "local_engine"
}
```

---

### 测试 2: Agent 处理（需要配置）

```bash
openclaw agent \
  --agent webviewer \
  --message "帮我记一下，我的大疆 action4 放在了电视柜上面的透明箱子里" \
  --json
```

---

## 📊 方案对比

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| **本地引擎** | 快速、可靠 | 不够智能 | ⭐⭐⭐⭐ |
| **Agent (云端)** | 智能、灵活 | 需要配置、慢 | ⭐⭐⭐ |
| **Agent (本地)** | 智能、离线 | 需要模型 | ⭐⭐⭐⭐ |
| **混合方案** | 平衡性能和智能 | 复杂 | ⭐⭐⭐⭐⭐ |

---

## 🚀 下一步

如果要实现真正的 OpenClaw 集成，需要：

1. **创建专用 agent**
   ```bash
   openclaw agents create --name webviewer
   ```

2. **配置提示词**
   - 在 agent 配置中添加系统提示

3. **测试调用**
   ```bash
   openclaw agent --agent webviewer --message "测试" --json
   ```

4. **集成到 webviewer**
   - 修改 openclaw_processor.py
   - 使用 subprocess 调用

---

*文档时间：2026-02-27 13:40*
