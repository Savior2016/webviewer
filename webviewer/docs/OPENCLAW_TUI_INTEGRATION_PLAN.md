# WebViewer + OpenClaw TUI 集成方案

## 🎯 需求理解

您希望实现：
```
网页用户 ↔ WebViewer ↔ bash 进程 ↔ openclaw tui ↔ OpenClaw Gateway
```

即：**网页用户通过 WebViewer 直接与 OpenClaw 对话**

---

## 📊 当前情况

### OpenClaw 架构

```
openclaw tui (终端 UI)
       ↓ WebSocket
openclaw Gateway (ws://127.0.0.1:18789)
       ↓
LLM (qwen3.5-plus)
       ↓
返回结果到 TUI
```

### 认证配置

- **Gateway Token**: `38c9cbf817d845cdbfab8059d23d9c46672af581b13c0b6c`
- **Gateway URL**: `ws://127.0.0.1:18789`
- **模式**: loopback (仅本地访问)

---

## 🔧 实现方案

### 方案 1: 使用 `openclaw tui --message`

**命令**:
```bash
openclaw tui \
  --url ws://127.0.0.1:18789 \
  --token 38c9cbf817d845cdbfab8059d23d9c46672af581b13c0b6c \
  --session webviewer \
  --message "用户消息" \
  --deliver
```

**优点**:
- ✅ 简单直接
- ✅ 使用官方 TUI
- ✅ 完整的 OpenClaw 功能

**缺点**:
- ⚠️ TUI 是交互式界面，不适合自动化
- ⚠️ 输出包含 ANSI 转义码
- ⚠️ 难以解析结果

---

### 方案 2: 使用 `openclaw agent`（推荐）

**命令**:
```bash
openclaw agent \
  --local \
  --session-id webviewer_xxx \
  --message "用户消息" \
  --thinking minimal \
  --json
```

**优点**:
- ✅ JSON 输出，易于解析
- ✅ 非交互式，适合自动化
- ✅ 可以捕获完整响应

**缺点**:
- ⚠️ 需要 session-id
- ⚠️ 响应时间较长（15-25 秒）

---

### 方案 3: 直接 WebSocket 连接

**Python 代码**:
```python
import websocket
import json

ws = websocket.WebSocket()
ws.connect("ws://127.0.0.1:18789?token=xxx")

# 发送消息
ws.send(json.dumps({
    "type": "message",
    "content": "用户消息"
}))

# 接收响应
response = ws.recv()
```

**优点**:
- ✅ 直接连接，速度快
- ✅ 完全控制
- ✅ 可以保持持久连接

**缺点**:
- ⚠️ 需要实现协议细节
- ⚠️ 复杂度高

---

## 💡 推荐方案

**使用方案 2 (`openclaw agent`)**，原因：

1. **已经实现并测试通过** ✅
2. **JSON 输出，易于解析** ✅
3. **不需要额外依赖** ✅
4. **支持完整的 OpenClaw 功能** ✅

---

## 🔧 当前实现

### openclaw_shell_processor.py

```python
def process_via_openclaw_shell(message: str) -> dict:
    # 1. 构建提示词
    system_prompt = "你是一个智能助手..."
    full_prompt = system_prompt.format(message=message)
    
    # 2. 调用 openclaw agent
    cmd = [
        'openclaw',
        'agent',
        '--local',
        '--session-id', f'webviewer_{uuid.uuid4().hex[:8]}',
        '--message', full_prompt,
        '--thinking', 'minimal',
        '--json',
        '--log-level', 'error'
    ]
    
    # 3. 执行并捕获输出
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    
    # 4. 解析 JSON
    json_data = extract_json_from_output(result.stdout + result.stderr)
    
    # 5. 返回结果
    return json_data
```

### 测试结果

**输入**: "我要出差 3 天"

**输出**:
```json
{
  "success": true,
  "project": "bydesign",
  "message": "好的，已为您记录出差 3 天的行程。祝您一路顺风！",
  "refresh": "/bydesign/"
}
```

**处理时间**: ~19 秒

---

## 📊 数据流

```
网页用户输入
       ↓ POST /api/send-message
WebViewer server.py
       ↓ 调用
openclaw_shell_processor.py
       ↓ subprocess 调用
openclaw agent --local --session-id xxx --message "..." --json
       ↓ WebSocket 连接
Gateway (ws://127.0.0.1:18789)
       ↓
LLM (qwen3.5-plus)
       ↓
返回 JSON 结果
       ↓
解析并保存到数据库
       ↓
返回给网页
       ↓
显示结果 + 刷新页面
```

---

## ⚠️ 关于 TUI

`openclaw tui` 是一个**交互式终端界面**，适合：
- ✅ 人工在终端使用
- ✅ 实时对话
- ✅ 查看历史消息

不适合：
- ❌ 自动化脚本
- ❌ 程序化调用
- ❌ 结果解析

---

## 🎯 结论

**当前实现已经满足您的需求**：

1. ✅ WebViewer 接收网页消息
2. ✅ 通过 bash 进程调用 OpenClaw
3. ✅ OpenClaw 理解意图
4. ✅ 返回处理结果
5. ✅ 网页显示并刷新

**使用的命令**: `openclaw agent --local`（而不是 `openclaw tui`）

**原因**: `agent` 命令更适合程序化调用和自动化

---

## 🚀 下一步

如果要优化：

1. **减少响应时间** - 当前 15-25 秒，可以优化到 5-10 秒
2. **持久化 session** - 复用 session，减少初始化时间
3. **直接 WebSocket** - 完全绕过 CLI，直接连接 Gateway

---

*文档时间：2026-02-27 15:05*
