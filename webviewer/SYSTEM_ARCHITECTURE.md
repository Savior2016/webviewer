# WebViewer 智能消息处理系统

## 🎯 系统架构

```
用户在 Web 页面发送消息
         ↓
POST /api/send-message (server.py)
         ↓
message_engine.py (消息处理引擎)
    ├─ parse_intent()  ← 解析意图
    └─ process()       ← 执行操作
         ↓
调用对应项目管理器
    ├─ bydesign_manager.py
    ├─ cherry_pick_manager.py
    └─ momhand_manager.py (item_manager.py)
         ↓
保存结果到 /data/results/{msg_id}.json
         ↓
返回结果给 Web 页面
         ↓
Web 页面轮询获取结果
         ↓
显示结果 + 更新 UI
```

---

## 📱 完整流程示例

### 示例 1: 创建出行清单

**用户输入**: "我要出差 3 天，帮我创建一个出行清单"

**处理流程**:
1. Web 页面 → POST `/api/send-message`
2. server.py → 调用 `message_engine.parse_intent()`
3. 解析结果：`project=bydesign, action=create_trip`
4. 调用 `bydesign_manager.create_trip()`
5. 创建出行记录到数据库
6. 保存结果到 `/data/results/{msg_id}.json`
7. 返回结果给 Web 页面
8. Web 页面轮询获取结果
9. 显示："✅ 已创建出行记录 - 出差 3 天"

**数据库变化**:
- `bydesign/trips.json` 新增一条出行记录
- 包含检查清单快照

**页面更新**:
- 显示处理结果卡片
- 提供"查看出行清单"链接
- 自动跳转到 `/bydesign/` 页面

---

### 示例 2: 记录搬家物品

**用户输入**: "帮我记录搬家物品：书籍，原位置书房，新位置新家书架"

**处理流程**:
1. 解析意图：`project=cherry_pick, action=add_item`
2. 获取最新的搬家活动
3. 调用 `cherry_pick_manager.add_item()`
4. 保存物品信息
5. 返回结果

**数据库变化**:
- `cherry-pick/moves.json` 的 items 数组新增物品

**页面更新**:
- 显示："✅ 已记录物品 - 书籍"
- 显示原位置和新位置
- 提供"查看搬家物品"链接

---

### 示例 3: 查询物品位置

**用户输入**: "找一下感冒药放在哪里"

**处理流程**:
1. 解析意图：`project=momhand, action=search_item`
2. 调用 `momhand_manager.search_items("感冒药")`
3. 返回匹配的物品列表

**页面更新**:
- 显示找到的物品
- 显示存放位置
- 提供"查看物品列表"链接

---

## 🔧 核心组件

### 1. message_engine.py - 消息处理引擎

**功能**:
- `parse_intent(message)` - 解析用户意图
- `process(project, action, params)` - 执行操作

**意图识别规则**:
```python
# 出行相关
if '出差' in message or '旅行' in message:
    return ('bydesign', 'create_trip', {...})

# 搬家相关  
if '搬家' in message or '打包' in message:
    return ('cherry_pick', 'add_item', {...})

# 物品查询
if '找' in message or '哪里' in message:
    return ('momhand', 'search_item', {...})
```

---

### 2. server.py - Web 服务器

**API 端点**:

#### POST /api/send-message
```json
请求:
{
  "message": "我要出差 3 天",
  "timestamp": 1234567890
}

响应:
{
  "success": true,
  "msg_id": "xxx-xxx-xxx",
  "project": "bydesign",
  "action": "create_trip",
  "result": "✅ 已创建出行记录..."
}
```

#### GET /api/message-result?msg_id=xxx
```json
响应:
{
  "success": true,
  "processed": true,
  "data": {
    "msg_id": "xxx",
    "project": "bydesign",
    "success": true,
    "result": "处理结果文本"
  }
}
```

---

### 3. index.html - Web 前端

**关键功能**:

```javascript
// 发送消息
async function sendMessage() {
  const response = await fetch('/api/send-message', {
    method: 'POST',
    body: JSON.stringify({ message, timestamp })
  });
  
  const result = await response.json();
  startPolling(result.msg_id);  // 开始轮询
}

// 轮询结果
function startPolling(msgId) {
  setInterval(async () => {
    const result = await fetch(`/api/message-result?msg_id=${msgId}`);
    if (result.processed) {
      displayResult(result.data);  // 显示结果
      clearInterval(pollTimer);
    }
  }, 500);
}

// 显示结果
function displayResult(data) {
  // 根据 project 显示不同的图标和链接
  // bydesign → ✈️ 已读不回
  // cherry_pick → 🏠 一搬不丢
  // momhand → 📦 妈妈的手
}
```

---

## 📊 数据流

### 消息处理流程

```
用户输入
   ↓
[Web 页面]
   ↓ POST /api/send-message
[server.py]
   ↓
[message_engine.py]
   ├─ parse_intent() → 识别意图
   └─ process() → 执行操作
   ↓
[项目管理器]
   ├─ bydesign_manager.py
   ├─ cherry_pick_manager.py
   └─ momhand_manager.py
   ↓
[数据库]
   ├─ bydesign/trips.json
   ├─ cherry-pick/moves.json
   └─ momhand/data/items.json
   ↓
[保存结果]
   /data/results/{msg_id}.json
   ↓
[返回响应]
   Web 页面
   ↓
[轮询]
   GET /api/message-result
   ↓
[显示结果]
   UI 更新
```

---

## 🎨 UI/UX 设计

### 状态显示

1. **发送中**
   ```
   ⏳ Dummy 正在处理你的请求...
   [loading 动画]
   ```

2. **处理完成**
   ```
   ✅ 已读不回
   📝 名称：出差 3 天
   📋 已自动加载通用检查清单...
   👉 [查看出行清单](/bydesign/)
   ```

3. **处理失败**
   ```
   ⚠️ 抱歉，我还不太理解这条消息
   你可以试试：
   ✈️ 我要出差 3 天
   🏠 帮我记录搬家物品
   ```

---

## 🧪 测试用例

### 测试 1: 创建出行
```bash
curl -k -X POST https://localhost/api/send-message \
  -H "Content-Type: application/json" \
  -d '{"message":"我要出差 3 天，帮我创建一个出行清单","timestamp":"123"}'
```

**预期结果**:
- ✅ 创建成功
- project: bydesign
- 数据库新增出行记录

---

### 测试 2: 记录物品
```bash
curl -k -X POST https://localhost/api/send-message \
  -H "Content-Type: application/json" \
  -d '{"message":"帮我记录搬家物品：书籍，原位置书房，新位置书架","timestamp":"123"}'
```

**预期结果**:
- ✅ 记录成功
- project: cherry_pick
- 物品添加到最新搬家活动

---

### 测试 3: 查询物品
```bash
curl -k -X POST https://localhost/api/send-message \
  -H "Content-Type: application/json" \
  -d '{"message":"找一下感冒药","timestamp":"123"}'
```

**预期结果**:
- ✅ 搜索成功
- project: momhand
- 返回匹配的物品列表

---

## 📁 文件结构

```
webviewer/
├── server.py                    # Web 服务器
├── message_engine.py            # 消息处理引擎
├── bydesign_manager.py          # By Design 管理器
├── cherry_pick_manager.py       # Cherry Pick 管理器
├── www/
│   ├── index.html               # 首页（含消息发送 UI）
│   ├── bydesign/index.html      # By Design 页面
│   ├── cherry-pick/index.html   # Cherry Pick 页面
│   └── momhand/index.html       # Momhand 页面
└── data/
    ├── results/                 # 消息结果存储
    │   └── {msg_id}.json
    ├── bydesign/
    │   ├── checklist.json
    │   └── trips.json
    └── cherry-pick/
        └── moves.json
```

---

## 🔐 安全性

### 输入验证
- 空消息检查
- 消息长度限制
- XSS 防护（escapeHtml）

### 错误处理
- 完整的异常捕获
- 详细的日志记录
- 友好的错误提示

### 数据保护
- 结果文件隔离存储
- 敏感信息不暴露
- 超时控制（15 秒）

---

## 🚀 性能优化

### 轮询策略
- 间隔：500ms
- 最大次数：30 次（15 秒）
- 自动清理定时器

### 数据存储
- JSON 文件存储
- 按 msg_id 索引
- 快速读写

---

## 💡 未来优化

1. **WebSocket** - 替代轮询，实时推送
2. **Redis 缓存** - 加速结果读取
3. **LLM 意图识别** - 提升准确率
4. **多轮对话** - 上下文理解
5. **消息历史** - 记录所有交互
6. **语音输入** - Web Speech API

---

*文档更新时间：2026-02-27 12:10*
