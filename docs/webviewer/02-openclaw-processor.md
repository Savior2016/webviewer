# 02 - OpenClaw 处理器 (openclaw_agent_processor.py)

## 功能概述

WebViewer 与 OpenClaw Agent 的桥接模块，核心功能：
- 调用 `openclaw agent` 命令处理用户消息
- 超时控制（30 秒）
- JSON 结果提取
- 意图解析（后备方案）

**文件**: `/root/.openclaw/workspace/openclaw_agent_processor.py`
**行数**: 302 行

---

## 核心函数

### 1. process_via_openclaw_agent

```python
def process_via_openclaw_agent(message: str) -> dict:
    """
    通过 OpenClaw Agent 处理消息
    
    参数:
        message: 用户消息
    
    返回:
        {
            "success": True/False,
            "project": "bydesign/cherry_pick/momhand/unknown/null",
            "action": "操作类型/null",
            "message": "回复消息",
            "refresh": "/页面路径/null",
            "data": {保存的数据},
            "processed_by": "openclaw_agent/timeout/error/direct_parse"
        }
    """
```

### 2. run_with_timeout

```python
def run_with_timeout(func, args=(), kwargs=None, timeout=30):
    """
    带超时控制的函数执行
    
    实现方式：
    1. 在子线程中执行函数
    2. 等待 timeout 秒
    3. 如果线程还在运行 → 抛出 TimeoutError
    """
```

### 3. _execute_openclaw_command

```python
def _execute_openclaw_command(full_prompt: str) -> dict:
    """
    执行 OpenClaw 命令（内部函数）
    
    命令:
    /root/.nvm/versions/node/v22.22.0/bin/openclaw \
        agent \
        --agent dummy \
        -m "{full_prompt}"
    """
```

### 4. extract_json_from_output

```python
def extract_json_from_output(output: str) -> dict:
    """
    从输出中提取 JSON
    
    尝试策略:
    1. 直接解析整个输出
    2. 正则匹配 JSON 对象 {...}
    3. 匹配 Markdown 代码块 ```json {...} ```
    """
```

### 5. parse_intent_directly

```python
def parse_intent_directly(message: str) -> dict:
    """
    直接解析用户意图（AI 超时时的后备方案）
    
    关键词匹配:
    - 出差/旅行/出行 → bydesign
    - 搬家/打包 → cherry_pick
    - 物品/东西/放在 → momhand
    - 检查/清单 → bydesign
    """
```

---

## 系统提示词

```python
system_prompt = """你是 WebViewer 的助手 Dummy，负责处理用户的出行、搬家和物品记录请求。

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
```

---

## 处理流程

### 完整流程
```
用户消息
    ↓
构建系统提示词
    ↓
run_with_timeout(_execute_openclaw_command, timeout=30)
    ↓
执行 openclaw agent --agent dummy -m "..."
    ↓
捕获 stdout + stderr
    ↓
extract_json_from_output()
    ↓
如果成功 → 返回 JSON
如果失败 → parse_intent_directly()
    ↓
返回结果字典
```

### 超时处理
```
超时（30 秒）
    ↓
捕获 TimeoutError
    ↓
返回 {
    "success": False,
    "message": "处理超时，请稍后重试",
    "processed_by": "timeout"
}
```

### 错误处理
```
异常（命令不存在、权限问题等）
    ↓
捕获 Exception
    ↓
返回 {
    "success": False,
    "message": "处理失败：{error}",
    "processed_by": "error"
}
```

---

## 返回格式

### 成功 - 需要保存数据
```json
{
  "success": true,
  "project": "bydesign",
  "action": "create_trip",
  "message": "已创建出行记录",
  "refresh": "/bydesign/",
  "data": {
    "name": "上海出差 3 天",
    "description": "业务会议"
  }
}
```

### 成功 - 闲聊回复
```json
{
  "success": false,
  "project": null,
  "action": null,
  "message": "你好！我是 WebViewer 助手 Dummy，可以帮你记录出行、搬家和物品信息。",
  "refresh": null,
  "data": null
}
```

### 超时
```json
{
  "success": false,
  "message": "处理超时，请稍后重试",
  "processed_by": "timeout"
}
```

### 后备方案（直接解析）
```json
{
  "success": true,
  "project": "cherry_pick",
  "action": "add_item",
  "message": "✅ 已理解搬家意图，但由于 AI 处理超时，请手动添加物品",
  "refresh": "/cherry-pick/",
  "data": {},
  "processed_by": "direct_parse"
}
```

---

## 意图识别规则

### By Design（出行）
```python
if any(kw in msg for kw in ['出差', '旅行', '出行', ' trip', ' travel']):
    return ('bydesign', 'create_trip', {...})
```

### Cherry Pick（搬家）
```python
if any(kw in msg for kw in ['搬家', '打包', 'cherry', 'move']):
    return ('cherry_pick', 'add_item', {...})
```

### Momhand（物品）
```python
if any(kw in msg for kw in ['物品', '东西', '放在', '位置', '找', 'momhand']):
    return ('momhand', 'add_item', {...})
```

### Checklist（检查清单）
```python
if any(kw in msg for kw in ['检查', '清单', 'checklist']):
    return ('bydesign', 'add_checklist', {...})
```

---

## 与服务器集成

### 调用位置
```python
# server.py 中的 _process_message_async 方法
from openclaw_agent_processor import process_via_openclaw_agent

result = process_via_openclaw_agent(message)
```

### 结果处理
```python
# server.py 中的 execute_project_save 函数
if result.get('project') and result.get('data'):
    execute_save_action(result)
```

---

## 性能优化

### 1. 超时控制
- **函数级超时**: `run_with_timeout(timeout=30)`
- **subprocess 级超时**: `subprocess.run(timeout=30)`
- 双重保护，防止卡死

### 2. 环境变量
```python
env = os.environ.copy()
env['PATH'] = '/root/.nvm/versions/node/v22.22.0/bin:' + env.get('PATH', '')
```
确保能找到 `openclaw` 命令

### 3. 输出清理
```python
# 移除日志行
if line.startswith('[plugins]') or line.startswith('gateway') or line.startswith('Error:'):
    continue
```

---

## 相关文件

| 文件 | 说明 |
|------|------|
| `openclaw_agent_processor.py` | 处理器主文件 |
| `server.py` | 调用方 |
| `message_engine.py` | 备用处理器 |

---

## 调试技巧

### 1. 测试单个消息
```bash
cd /root/.openclaw/workspace
python3 openclaw_agent_processor.py "我要出差 3 天"
```

### 2. 查看日志
```bash
grep "📤 发送消息到 OpenClaw" /root/.openclaw/workspace/server.log
```

### 3. 手动测试命令
```bash
/root/.nvm/versions/node/v22.22.0/bin/openclaw agent --agent dummy -m "测试消息"
```

---

## 常见问题

### Q: 为什么设置 30 秒超时？
A: 平衡响应时间和复杂任务处理，避免单个请求卡死整个服务。

### Q: 超时后会发生什么？
A: 返回超时错误，前端显示"处理超时，请稍后重试"。

### Q: 如何调整超时时间？
A: 修改 `process_via_openclaw_agent` 函数中的 `timeout=30` 参数。

### Q: direct_parse 什么时候触发？
A: 当 AI 输出无法解析为 JSON 时，作为后备方案使用关键词匹配。

---

*最后更新：2026-03-02*
