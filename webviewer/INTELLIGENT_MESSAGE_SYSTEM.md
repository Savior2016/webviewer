# 智能消息处理系统

## ✅ 完整功能实现

### 功能流程

```
用户在 Web 页面发送消息
         ↓
POST /api/send-message
         ↓
消息处理引擎解析意图
         ↓
路由到对应项目处理
         ↓
保存结果 + 发送到 Feishu
         ↓
Web 页面轮询获取结果
         ↓
显示结果 + 更新页面
```

---

## 🎯 支持的消息类型

### 1. ✈️ By Design - 出行管理

**示例消息**:
- "我要出差 3 天，帮我创建一个出行清单"
- "下周去北京旅行，创建出行记录"
- "帮我创建一个出差清单"

**处理结果**:
- ✅ 创建出行记录
- ✅ 自动加载通用检查清单
- ✅ 返回出行详情
- ✅ 提供快速链接

---

### 2. 🏠 Cherry Pick - 搬家管理

**示例消息**:
- "帮我记录搬家物品：书籍，原位置书房，新位置新家书架"
- "创建一个搬家活动：搬到新家"
- "记录物品：电脑，原位置客厅，新位置卧室"

**处理结果**:
- ✅ 添加到最新搬家活动
- ✅ 记录物品信息（名称、原位置、新位置）
- ✅ 返回物品详情
- ✅ 提供快速链接

---

### 3. 📦 Momhand - 物品查询

**示例消息**:
- "找一下感冒药放在哪里"
- "查询工具在哪里"
- "找证件"

**处理结果**:
- ✅ 搜索物品
- ✅ 返回物品列表（最多 5 个）
- ✅ 显示位置信息
- ✅ 提供快速链接

---

## 🔧 技术实现

### 消息处理引擎 (`message_engine.py`)

**核心方法**:
```python
def parse_intent(message):
    """解析用户意图"""
    # 关键词匹配
    # 返回：(project, action, params)

def process(project, action, params):
    """处理消息"""
    # 路由到对应项目
    # 返回：(success, result_message)
```

**意图识别**:
- 出差/旅行/出行 → By Design
- 搬家/打包/物品 → Cherry Pick
- 找/查询/在哪里 → Momhand

---

### 后端 API (`server.py`)

#### 1. 发送消息 API
```
POST /api/send-message
Body: {"message": "消息内容", "timestamp": 123456}
```

**处理流程**:
1. 解析消息意图
2. 调用对应项目管理器
3. 保存结果到 `/data/results/{msg_id}.json`
4. 通过 Feishu API 发送结果到用户
5. 返回 msg_id 给前端

**响应**:
```json
{
  "success": true,
  "message": "消息已处理",
  "msg_id": "xxx-xxx-xxx",
  "project": "bydesign",
  "action": "create_trip",
  "result": "处理结果文本"
}
```

#### 2. 轮询结果 API
```
GET /api/message-result?msg_id=xxx
```

**响应**:
```json
{
  "success": true,
  "processed": true,
  "data": {
    "msg_id": "xxx",
    "original_message": "原始消息",
    "project": "bydesign",
    "success": true,
    "result": "处理结果",
    "timestamp": 123456
  }
}
```

---

### 前端实现 (`index.html`)

#### 消息发送
```javascript
async function sendMessage() {
  const response = await fetch('/api/send-message', {
    method: 'POST',
    body: JSON.stringify({ message, timestamp })
  });
  
  const result = await response.json();
  startPolling(result.msg_id);
}
```

#### 结果轮询
```javascript
function startPolling(msgId) {
  pollTimer = setInterval(async () => {
    const result = await fetch(`/api/message-result?msg_id=${msgId}`);
    
    if (result.processed) {
      displayResult(result.data);
      clearInterval(pollTimer);
    }
  }, 500); // 每 500ms 轮询
}
```

#### 结果显示
- ✅ 项目图标识别
- ✅ 处理状态显示
- ✅ 结果详情展示
- ✅ 快速链接跳转
- ✅ 15 秒后自动隐藏

---

## 📊 测试结果

### 测试 1: 创建出行清单
**消息**: "我要出差 3 天，帮我创建一个出行清单"

**响应**:
```json
{
  "success": true,
  "project": "bydesign",
  "action": "create_trip",
  "result": "✅ 已创建出行记录\n\n📝 名称：出差 3 天\n📋 已自动加载通用检查清单..."
}
```

**Feishu 收到**:
```
✅ 已创建出行记录

📝 名称：出差 3 天
📅 创建时间：2026-02-27 11:59

📋 已自动加载通用检查清单...

---
💬 原始消息：我要出差 3 天，帮我创建一个出行清单
🕐 处理时间：2026-02-27 11:59:23
```

---

## 🎨 UI/UX 优化

### 状态显示
1. **发送中** - ⏳ Dummy 正在处理
2. **轮询中** - 🔄 正在获取处理结果（带 loading 动画）
3. **处理完成** - ✅ 显示详细结果
4. **处理失败** - ⚠️ 显示错误信息

### 结果卡片
- 项目图标（✈️/🏠/📦）
- 项目名称（已读不回/一搬不丢/妈妈的手）
- 处理结果详情
- 原始消息预览
- 快速链接按钮

---

## 🔐 安全性

### 错误处理
- 完整的异常捕获
- 详细的日志记录
- 友好的错误提示

### 数据验证
- 空消息检查
- 参数验证
- 超时控制（15 秒）

---

## 📈 性能优化

### 轮询策略
- 轮询间隔：500ms
- 最大轮询次数：30 次（15 秒）
- 超时自动停止
- 页面关闭清理定时器

### 结果存储
- 文件存储：`/data/results/{msg_id}.json`
- 自动清理机制（待实现）

---

## 🧪 测试清单

- [x] 消息发送到 Feishu
- [x] 意图识别正确
- [x] By Design 创建出行
- [x] Cherry Pick 添加物品
- [x] Momhand 搜索物品
- [x] 结果返回到 Feishu
- [x] Web 页面轮询结果
- [x] 结果显示在页面
- [x] 错误处理正常

---

## 💡 后续优化

1. **自然语言处理** - 使用 LLM 提升意图识别准确率
2. **上下文理解** - 支持多轮对话
3. **结果缓存** - Redis 存储结果
4. **WebSocket** - 替代轮询，实时推送
5. **消息历史** - 记录所有交互历史
6. **语音输入** - Web Speech API

---

## 🔍 故障排查

### 消息未处理
1. 检查 `message_engine.py` 语法
2. 查看服务器日志
3. 测试 API 端点

### Feishu 未收到
1. 检查 Token 是否有效
2. 检查用户 Open ID
3. 查看 API 响应

### 页面未更新
1. 检查轮询是否启动
2. 查看浏览器控制台
3. 检查网络连接

---

*完成时间：2026-02-27 11:59*
