# 06 - Siri Dream 管理器 (siri_dream_manager.py)

## 功能概述

Siri 的梦 - 外部消息接收和 AI 处理模块，核心功能：
- 接收外部消息（API/Web）
- 转发给 Agent Dummy 处理
- 保存历史记录
- 状态追踪（pending/processing/completed/failed）

**文件**: `/root/.openclaw/workspace/siri_dream_manager.py`
**行数**: 184 行
**数据存储**: JSON 文件

---

## 数据模型

### Message（消息）
```json
{
  "id": "uuid",
  "text": "用户消息内容",
  "source": "api",  // "api" 或 "web"
  "timestamp": 1234567890,
  "created_at": "2026-03-02 10:00:00",
  "status": "pending",  // pending, processing, completed, failed
  "result": {
    "message": "AI 回复内容"
  },
  "metadata": {}
}
```

### 状态流转
```
pending → processing → completed
                      → failed
```

---

## 数据存储

### 文件路径
```
/root/.openclaw/workspace/data/siri-dream/
├── messages.json     # 消息历史
└── settings.json     # 设置（含系统提示词）
```

### messages.json 结构
```json
[
  {
    "id": "uuid",
    "text": "...",
    "source": "api",
    "timestamp": 1234567890,
    "status": "completed",
    "result": {...}
  }
]
```

### 数据保留策略
- 最多保留 100 条消息
- 新消息插入到数组开头（最新在前）

---

## API 接口

### 消息管理

| 函数 | 说明 |
|------|------|
| `add_message(text, source, metadata)` | 添加新消息 |
| `get_messages(limit, offset)` | 获取消息列表 |
| `get_message(message_id)` | 获取单条消息 |
| `update_message_status(id, status, result)` | 更新状态 |
| `delete_message(message_id)` | 删除消息 |
| `clear_messages()` | 清空所有消息 |

### 设置管理

| 函数 | 说明 |
|------|------|
| `load_settings()` | 加载设置 |
| `save_settings(settings)` | 保存设置 |
| `get_system_prompt()` | 获取系统提示词 |
| `save_system_prompt(prompt)` | 保存系统提示词 |

### 统计

| 函数 | 说明 |
|------|------|
| `get_statistics()` | 获取统计信息 |

---

## 默认系统提示词

```python
DEFAULT_SYSTEM_PROMPT = """你是 WebViewer 的助手 Dummy，负责处理用户的各种请求。

用户消息："{message}"

请：
1. 理解用户的意图
2. 提供有帮助的回复
3. 只返回纯文本回复，不要返回 JSON

示例回复：
- "收到你的消息了"
- "我已经理解了你的需求"
- "这是一个测试消息"

注意：不要返回 JSON 格式，只返回简单的中文回复。"""
```

---

## 使用示例

### 添加消息
```python
from siri_dream_manager import manager

message = manager['add_message'](
    message_text="你好，帮我查一下天气",
    source='api',
    metadata={'user_agent': 'iOS'}
)
print(f"消息 ID: {message['id']}")
# 状态：pending
```

### 更新状态
```python
# 开始处理
manager['update_message_status'](message['id'], 'processing')

# 处理完成
manager['update_message_status'](
    message['id'],
    'completed',
    result={'message': '今天天气晴朗，气温 25 度'}
)
```

### 查询消息
```python
message = manager['get_message'](message_id)
print(f"状态：{message['status']}")
print(f"结果：{message['result']}")
```

### 获取统计
```python
stats = manager['get_statistics']()
print(stats)
# {
#   "total": 50,
#   "pending": 2,
#   "completed": 45,
#   "failed": 3,
#   "today": 10
# }
```

### 获取消息列表
```python
messages = manager['get_messages'](limit=20, offset=0)
for msg in messages:
    print(f"{msg['created_at']}: {msg['text']}")
```

---

## 与服务器集成

### API 端点（server.py）
```python
# GET
/siri-dream/api/message/{message_id}  # 查询单条消息
/siri-dream/api/messages              # 获取消息列表
/siri-dream/api/stats                 # 获取统计

# POST
/siri-dream/api/message               # 发送消息
/siri-dream/api/messages              # 查询消息（带 message_id）
```

### 处理流程
```python
# server.py 中的 handle_siri_dream_message
def handle_siri_dream_message(self, data):
    # 1. 添加消息（pending）
    message = manager['add_message'](text, 'api', metadata)
    
    # 2. 启动后台线程
    thread = threading.Thread(
        target=self._process_siri_dream_message_sync,
        args=(message['id'], text),
        daemon=True
    )
    thread.start()
    
    # 3. 立即返回
    return {
        "success": True,
        "message_id": message['id'],
        "status": "processing"
    }
```

### 后台处理
```python
# server.py 中的 _process_siri_dream_message_sync
def _process_siri_dream_message_sync(self, message_id, text):
    # 1. 更新状态为 processing
    manager['update_message_status'](message_id, 'processing')
    
    # 2. 获取提示词
    system_prompt = manager['get_system_prompt']()
    full_prompt = system_prompt.format(message=text)
    
    # 3. 调用 OpenClaw Agent
    cmd = ['openclaw', 'agent', '--agent', 'dummy', '-m', full_prompt]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    
    # 4. 解析输出
    output = result.stdout + result.stderr
    
    # 5. 更新状态为 completed
    manager['update_message_status'](message_id, 'completed', {'message': output})
```

---

## 消息处理流程

### 完整流程
```
POST /siri-dream/api/message
    ↓
siri_dream_manager.add_message()
    ↓
保存到 messages.json（status: pending）
    ↓
立即返回 message_id
    ↓
后台线程启动
    ↓
update_message_status(processing)
    ↓
调用 openclaw agent
    ↓
解析输出
    ↓
update_message_status(completed/failed)
    ↓
前端轮询 /siri-dream/api/messages/{message_id}
```

### 轮询机制
```javascript
// 前端轮询
setInterval(async () => {
  const response = await fetch(`/siri-dream/api/message/${message_id}`);
  const result = await response.json();
  
  if (result.message.status === 'completed') {
    // 显示结果
    console.log(result.message.result.message);
  }
}, 1000);
```

---

## 相关文件

| 文件 | 说明 |
|------|------|
| `siri_dream_manager.py` | 管理器主文件 |
| `www/siri-dream/index.html` | Web 界面 |
| `data/siri-dream/messages.json` | 消息历史 |
| `data/siri-dream/settings.json` | 设置 |
| `server.py` | 服务器集成 |

---

## 设计亮点

### 1. 异步处理
- 立即返回 message_id
- 后台线程处理
- 前端轮询结果

### 2. 状态追踪
- pending: 等待处理
- processing: 处理中
- completed: 处理完成
- failed: 处理失败

### 3. 灵活配置
- 可自定义系统提示词
- 支持元数据（metadata）
- 可配置消息保留数量

### 4. 简单存储
- JSON 文件格式
- 易于备份和迁移
- 手动可读可编辑

---

## 统计信息

```python
def get_statistics():
    messages = load_messages()
    return {
        'total': len(messages),
        'pending': len([m for m in messages if m['status'] == 'pending']),
        'completed': len([m for m in messages if m['status'] == 'completed']),
        'failed': len([m for m in messages if m['status'] == 'failed']),
        'today': len([m for m in messages 
                     if datetime.fromtimestamp(m['timestamp']).date() == datetime.now().date()])
    }
```

---

## 常见问题

### Q: 消息最多保留多少条？
A: 100 条，超出后自动删除最旧的消息。

### Q: 如何处理超时？
A: subprocess 设置 timeout=90 秒，超时后状态变为 failed。

### Q: 如何自定义提示词？
A: 使用 `save_system_prompt(prompt)` 方法保存新提示词。

### Q: 数据文件在哪里？
A: `/root/.openclaw/workspace/data/siri-dream/messages.json`

### Q: 如何清空历史消息？
A: 使用 `clear_messages()` 方法。

---

*最后更新：2026-03-02*
