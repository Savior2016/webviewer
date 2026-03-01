# WebViewer + OpenClaw Shell 集成 - 实现方案

## 📊 数据流（按您的要求）

```
WebViewer 收到用户消息
         ↓
附加引导词（系统提示）
         ↓
新建 bash 进程
         ↓
启动 openclaw agent 命令
         ↓
捕获终端输出
         ↓
解析返回结果（JSON）
         ↓
保存到数据库
         ↓
返回给 Web 页面
```

---

## ✅ 已实现

### 1. Shell 处理器 (`openclaw_shell_processor.py`)

**功能**:
- 接收用户消息
- 附加系统提示词
- 通过 subprocess 调用 `openclaw agent`
- 捕获 stdout/stderr
- 解析 JSON 输出
- Fallback 到本地引擎

**核心代码**:
```python
def process_via_openclaw_shell(message: str) -> dict:
    # 构建提示词
    system_prompt = "你是一个智能助手..."
    full_prompt = system_prompt.format(message=message)
    
    # 调用 openclaw agent
    cmd = ['openclaw', 'agent', '--local', '--session-id', session_id, 
           '--message', full_prompt, '--thinking', 'minimal', '--json']
    
    # 执行并捕获输出
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    
    # 解析 JSON
    json_output = extract_json(result.stdout)
    
    return json_output
```

---

### 2. 系统提示词

```
你是一个智能助手，帮助用户管理 webviewer 的三个项目。

用户消息："{message}"

请理解意图并选择合适的项目：

1. 出行相关（出差、旅行、出行）→ By Design (/bydesign/)
2. 搬家相关（搬家、打包、物品记录）→ Cherry Pick (/cherry-pick/)
3. 物品相关（找、查询、记录位置）→ Momhand (/momhand/)

必须返回 JSON 格式，包含以下字段：
- success: true/false
- project: bydesign 或 cherry_pick 或 momhand
- action: 操作类型
- message: 友好的回复消息
- refresh: 页面路径
- data: 数据对象
```

---

### 3. server.py 集成

```python
def handle_send_message(self, data):
    message = data['message']
    
    # 调用 OpenClaw Shell 处理器
    from openclaw_shell_processor import process_via_openclaw_shell
    result = process_via_openclaw_shell(message)
    
    # 保存结果
    save_result(result)
    
    # 返回给前端
    return result
```

---

## ⚠️ 当前问题

### 问题 1: OpenClaw Agent 输出包含日志

**现象**:
```
[plugins] feishu_doc: Registered feishu_doc...
[plugins] plugins.allow is empty...
{JSON 输出}
```

**解决**: 需要从输出中提取 JSON 部分

---

### 问题 2: 需要 session-id

**现象**: `Error: Pass --to <E.164>, --session-id, or --agent`

**解决**: 生成随机 session-id
```python
session_id = f"webviewer_{uuid.uuid4().hex[:8]}"
```

---

### 问题 3: LLM 可能不返回 JSON

**现象**: OpenClaw 返回纯文本而不是 JSON

**解决**: 
1. 在提示词中强调 JSON 格式
2. 解析失败时 Fallback 到本地引擎

---

## 🔧 Fallback 机制

当 OpenClaw 调用失败时，自动使用本地引擎：

```python
def process_local_fallback(message: str) -> dict:
    from message_engine import processor
    
    project, action, params = processor.parse_intent(message)
    success, result_message = processor.process(project, action, params)
    
    return {
        "success": success,
        "project": project,
        "action": action,
        "message": result_message,
        "refresh": f"/{project}/"
    }
```

---

## 📝 完整流程示例

### 用户输入
```
"帮我记一下，我的大疆 action4 放在了电视柜上面的透明箱子里"
```

### 处理流程

1. **WebViewer 接收**
   ```javascript
   POST /api/send-message
   {
     "message": "帮我记一下，我的大疆 action4 放在了电视柜上面的透明箱子里"
   }
   ```

2. **附加提示词**
   ```
   你是一个智能助手...
   
   用户消息："帮我记一下，我的大疆 action4 放在了电视柜上面的透明箱子里"
   
   请理解意图...
   ```

3. **调用 OpenClaw**
   ```bash
   openclaw agent --local \
     --session-id webviewer_abc123 \
     --message "你是一个智能助手..." \
     --thinking minimal \
     --json
   ```

4. **捕获输出**
   ```
   [plugins] ...
   {
     "success": true,
     "project": "momhand",
     "action": "add_item",
     "message": "✅ 已记录...",
     "refresh": "/momhand/"
   }
   ```

5. **保存并返回**
   ```json
   {
     "success": true,
     "project": "momhand",
     "processed_by": "openclaw_shell"
   }
   ```

6. **前端显示 + 跳转**
   - 显示结果
   - 3 秒后跳转到 `/momhand/`

---

## 🚀 测试命令

### 测试 1: 直接调用处理器
```bash
cd /root/.openclaw/workspace/webviewer
timeout 60 python3 openclaw_shell_processor.py "我要出差 3 天"
```

### 测试 2: 通过 API
```bash
curl -k -X POST https://localhost/api/send-message \
  -H "Content-Type: application/json" \
  -d '{"message":"我要出差 3 天"}'
```

### 测试 3: 手动调用 OpenClaw
```bash
openclaw agent --local \
  --session-id test123 \
  --message "你是一个智能助手，用户说：我要出差 3 天" \
  --thinking minimal
```

---

## 📊 方案对比

| 方面 | 当前方案 | 理想方案 |
|------|----------|----------|
| **调用方式** | Shell subprocess | OpenClaw API |
| **Session** | 临时生成 | 持久化会话 |
| **输出** | 日志 + JSON | 纯 JSON |
| **速度** | 较慢（5-10 秒） | 快（1-2 秒） |
| **可靠性** | 依赖 OpenClaw | 稳定 |
| **Fallback** | 本地引擎 | 本地引擎 |

---

## 💡 优化建议

### 1. 提取 JSON 优化
```python
def extract_json(text: str) -> str:
    # 使用正则表达式提取 JSON
    match = re.search(r'\{.*\}', text, re.DOTALL)
    return match.group(0) if match else text
```

### 2. 添加重试机制
```python
for attempt in range(3):
    result = subprocess.run(cmd, ...)
    if result.returncode == 0:
        break
```

### 3. 缓存 Session
```python
# 使用固定 session-id
SESSION_ID = "webviewer_main"
```

---

## 📁 文件清单

```
webviewer/
├── openclaw_shell_processor.py    # Shell 调用处理器
├── message_engine.py               # 本地 fallback 引擎
├── server.py                       # Web 服务器
├── www/index.html                  # 前端对话界面
└── docs/
    └── OPENCLAW_SHELL_SETUP.md     # 本文档
```

---

*更新时间：2026-02-27 14:20*
