# WebViewer + OpenClaw 集成架构

## 🎯 设计理念

用户要求：**"在页面发送消息，传递给 OpenClaw 处理，让它理解意图并选择 webviewer 中合适的模块保存信息，然后刷新页面显示"**

## 📊 系统架构

```
用户在 Web 页面输入消息
         ↓
POST /api/send-message
         ↓
server.py → openclaw_processor.py
         ↓
附加提示词：
"理解这些信息的意图，并选择 webviewer 中合适的模块
 保存这些信息，然后刷新页面的显示"
         ↓
调用 message_engine (OpenClaw 桥接)
         ↓
解析意图 → 选择项目 → 调用 API
         ↓
保存数据到数据库
         ↓
返回结果给 Web 页面
         ↓
显示结果 + 自动刷新页面
```

---

## 🔧 核心组件

### 1. openclaw_processor.py

**作用**: OpenClaw 消息处理器

**功能**:
- 接收用户消息
- 附加系统提示词
- 调用 message_engine 处理
- 返回结构化结果

**提示词内容**:
```
你是一个智能助手，帮助用户管理 webviewer 的三个项目。

用户消息："{message}"

请理解意图并选择合适的项目：

1. 出行相关 → By Design (/bydesign/)
2. 搬家相关 → Cherry Pick (/cherry-pick/)
3. 物品相关 → Momhand (/momhand/)

返回 JSON 格式的处理结果。
```

---

### 2. server.py

**API 端点**: `POST /api/send-message`

**处理流程**:
```python
def handle_send_message(self, data):
    # 1. 接收消息
    message = data['message']
    
    # 2. 调用 OpenClaw 处理器
    from openclaw_processor import process_via_openclaw
    result = process_via_openclaw(message)
    
    # 3. 保存结果
    save_result(result)
    
    # 4. 返回给前端
    return result
```

---

### 3. index.html (前端)

**对话界面**:
- 用户输入消息
- 发送到 `/api/send-message`
- 显示处理结果
- 根据 `refresh` 字段自动跳转

**JavaScript 代码**:
```javascript
async function sendMessage() {
  const response = await fetch('/api/send-message', {
    method: 'POST',
    body: JSON.stringify({ message, timestamp })
  });
  
  const result = await response.json();
  
  // 显示结果
  addMessage(result.message, false);
  
  // 自动刷新页面
  if (result.refresh) {
    setTimeout(() => {
      window.location.href = result.refresh;
    }, 3000);
  }
}
```

---

## 📝 数据流

### 完整流程示例

**用户输入**: "帮我记一下，我的大疆 action4 放在了电视柜上面的透明箱子里"

**处理步骤**:

1. **前端发送**
   ```javascript
   POST /api/send-message
   {
     "message": "帮我记一下，我的大疆 action4 放在了电视柜上面的透明箱子里",
     "timestamp": 1234567890
   }
   ```

2. **server.py 接收**
   ```python
   message = data['message']
   result = process_via_openclaw(message)
   ```

3. **openclaw_processor.py 处理**
   ```python
   # 附加提示词
   system_prompt = """
   理解这些信息的意图，并选择 webviewer 中合适的模块
   保存这些信息，然后刷新页面的显示
   """
   
   # 调用 message_engine
   project, action, params = processor.parse_intent(message)
   success, result_message = processor.process(project, action, params)
   ```

4. **返回结果**
   ```json
   {
     "success": true,
     "project": "momhand",
     "action": "add_item",
     "message": "✅ 已记录物品位置\n\n📦 物品：大疆 action4\n📍 位置：电视柜上面的透明箱子里\n📂 类型：电子产品",
     "refresh": "/momhand/",
     "data": {
       "item_name": "大疆 action4",
       "location": "电视柜上面的透明箱子里"
     },
     "processed_by": "openclaw"
   }
   ```

5. **前端显示并跳转**
   - 显示助手回复
   - 3 秒后跳转到 `/momhand/`
   - 页面显示新物品

---

## 🎯 提示词设计

### 系统提示词

```
你是一个智能助手，帮助用户管理 webviewer 的三个项目。

用户消息："{message}"

请理解这条消息的意图，并选择 webviewer 中合适的项目来保存这些信息：

可用项目：
1. **已读不回 (By Design)** - 出行管理
   - 适用：出差、旅行、出行清单
   - 路径：/bydesign/

2. **一搬不丢 (Cherry Pick)** - 搬家物品管理
   - 适用：搬家、打包、记录物品位置
   - 路径：/cherry-pick/

3. **妈妈的手 (Momhand)** - 物品管理
   - 适用：找东西、记录物品位置、查询物品
   - 路径：/momhand/

请：
1. 理解用户意图
2. 选择合适的项目
3. 调用相应的 API 保存数据
4. 返回友好的确认消息
5. 指定需要刷新的页面路径

返回 JSON 格式：
{
  "success": true,
  "project": "项目名",
  "action": "操作类型",
  "message": "友好的回复",
  "refresh": "/页面路径/",
  "data": {...}
}
```

---

## 🧪 测试用例

### 测试 1: 记录物品

**输入**: "帮我记一下，我的大疆 action4 放在了电视柜上面的透明箱子里"

**预期处理**:
- project: momhand
- action: add_item
- refresh: /momhand/

**预期结果**:
```json
{
  "success": true,
  "project": "momhand",
  "message": "✅ 已记录物品位置...",
  "refresh": "/momhand/"
}
```

---

### 测试 2: 创建出行

**输入**: "我要出差 3 天"

**预期处理**:
- project: bydesign
- action: create_trip
- refresh: /bydesign/

---

### 测试 3: 查询物品

**输入**: "找一下感冒药放在哪里"

**预期处理**:
- project: momhand
- action: search_item
- refresh: /momhand/

---

## 📁 文件结构

```
webviewer/
├── server.py                    # Web 服务器
│   └─ handle_send_message()    # 调用 OpenClaw 处理器
│
├── openclaw_processor.py        # OpenClaw 处理器
│   └─ process_via_openclaw()   # 主处理函数
│
├── message_engine.py            # 消息处理引擎
│   ├─ parse_intent()           # 解析意图
│   └─ process()                # 执行操作
│
├── www/
│   └── index.html              # 前端对话界面
│       └─ sendMessage()        # 发送消息到后端
│
└── data/
    └── results/                # 处理结果存储
        └── {msg_id}.json
```

---

## 🚀 启动使用

### 1. 启动服务

```bash
cd /root/.openclaw/workspace/webviewer
python3 server.py
```

### 2. 访问页面

```
https://<服务器 IP>/
```

### 3. 发送消息

在对话框输入：
- "帮我记一下，我的大疆 action4 放在了电视柜上面的透明箱子里"
- "我要出差 3 天"
- "找一下感冒药"

### 4. 查看结果

- 对话界面显示处理结果
- 3 秒后自动跳转到相应页面
- 数据已保存到数据库

---

## 💡 架构优势

### ✅ 优点

1. **集中处理** - 所有消息通过 OpenClaw 处理器
2. **智能路由** - 自动选择合适的项目
3. **友好界面** - 对话式交互
4. **自动刷新** - 处理后自动跳转
5. **可扩展** - 易于添加新项目

### 🔮 未来优化

1. **真正的 OpenClaw 集成** - 使用 sessions_send
2. **多轮对话** - 支持上下文
3. **LLM 理解** - 使用 AI 模型
4. **消息历史** - 记录对话

---

*文档时间：2026-02-27 13:10*
