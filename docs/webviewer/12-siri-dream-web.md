# 12 - Siri Dream Web (www/siri-dream/index.html)

## 功能概述

Siri 的尉来 - AI 消息处理 Web 界面，核心功能：
- 发送测试消息
- 消息历史查看
- 状态追踪（pending/processing/completed/failed）
- 统计面板
- API 文档展示

**文件**: `/root/.openclaw/workspace/www/siri-dream/index.html`
**行数**: 424 行
**大小**: ~17KB
**主题色**: 深蓝灰色系 (#0f172a → #334155)

---

## 页面布局

```
┌─────────────────────────────────────┐
│           Header                    │
│   🤖 Siri 的尉来 · SiriFuture       │
│   "Siri 会的我都会，我会的 Siri 不会"  │
├─────────────────────────────────────┤
│   [统计面板]                         │
│   总消息 | 待处理 | 已完成 | 失败 | 今日│
├─────────────────────────────────────┤
│   [测试消息]                         │
│   [输入框] [发送]                    │
├─────────────────────────────────────┤
│   历史消息列表                       │
│  ┌─────────────────────────────┐   │
│  │ 🟡 待处理 · 你好             │   │
│  │ 🔵 处理中 · 帮我查天气       │   │
│  │ 🟢 已完成 · 出差 3 天         │   │
│  │ 🔴 失败 · 错误消息           │   │
│  └─────────────────────────────┘   │
├─────────────────────────────────────┤
│   API 文档                           │
│   POST /siri-dream/api/message     │
└─────────────────────────────────────┘
```

---

## 核心组件

### 1. 统计面板

```html
<div id="statsCard" class="grid grid-cols-2 sm:grid-cols-5 gap-4 mb-6">
  <div class="glass-card rounded-2xl p-4 text-center">
    <div class="text-3xl font-extrabold bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text text-transparent" id="totalMessages">0</div>
    <div class="text-xs text-gray-600 font-medium mt-1">总消息</div>
  </div>
  
  <div class="glass-card rounded-2xl p-4 text-center">
    <div class="text-3xl font-extrabold bg-gradient-to-r from-amber-500 to-orange-500 bg-clip-text text-transparent" id="pendingMessages">0</div>
    <div class="text-xs text-gray-600 font-medium mt-1">待处理</div>
  </div>
  
  <div class="glass-card rounded-2xl p-4 text-center">
    <div class="text-3xl font-extrabold bg-gradient-to-r from-green-500 to-emerald-500 bg-clip-text text-transparent" id="completedMessages">0</div>
    <div class="text-xs text-gray-600 font-medium mt-1">已完成</div>
  </div>
  
  <div class="glass-card rounded-2xl p-4 text-center">
    <div class="text-3xl font-extrabold bg-gradient-to-r from-red-500 to-pink-500 bg-clip-text text-transparent" id="failedMessages">0</div>
    <div class="text-xs text-gray-600 font-medium mt-1">失败</div>
  </div>
  
  <div class="glass-card rounded-2xl p-4 text-center">
    <div class="text-3xl font-extrabold bg-gradient-to-r from-cyan-500 to-blue-500 bg-clip-text text-transparent" id="todayMessages">0</div>
    <div class="text-xs text-gray-600 font-medium mt-1">今日</div>
  </div>
</div>
```

### 2. 测试消息

```html
<div class="glass-card rounded-3xl p-6 mb-6">
  <div class="flex items-center gap-3 mb-4">
    <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-500">🧪</div>
    <h2 class="text-xl font-bold">测试消息</h2>
  </div>
  
  <div class="flex gap-3">
    <input id="testMessage" placeholder="输入测试消息..." 
           class="flex-1 px-4 py-3 rounded-xl border-2 focus:border-blue-500 outline-none">
    <button onclick="sendTestMessage()" 
            class="bg-gradient-to-r from-blue-500 to-purple-500 text-white px-5 py-3 rounded-xl font-semibold">
      发送
    </button>
  </div>
</div>
```

### 3. 消息卡片

```javascript
function renderMessageCard(message) {
  const statusClass = {
    'pending': 'status-pending',
    'processing': 'status-processing',
    'completed': 'status-completed',
    'failed': 'status-failed'
  }[message.status];
  
  const statusIcon = {
    'pending': '🟡',
    'processing': '🔵',
    'completed': '🟢',
    'failed': '🔴'
  }[message.status];
  
  return `
    <div class="glass-card rounded-2xl p-4 mb-3 slide-in message-card ${statusClass}">
      <div class="flex items-start justify-between mb-2">
        <div class="flex items-center gap-2">
          <span class="text-lg">${statusIcon}</span>
          <span class="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-600 uppercase">
            ${message.status}
          </span>
          <span class="text-xs text-gray-400">${formatTime(message.timestamp)}</span>
        </div>
        <span class="text-xs text-gray-400">${message.source}</span>
      </div>
      
      <div class="mb-3">
        <p class="text-sm text-gray-600 mb-1">📩 内容：</p>
        <p class="text-sm text-gray-800">${message.text}</p>
      </div>
      
      ${message.result ? `
        <div>
          <p class="text-sm text-gray-600 mb-1">💬 回复：</p>
          <p class="text-sm text-gray-800 bg-gray-50 rounded-lg p-3">
            ${message.result.message || '无回复内容'}
          </p>
        </div>
      ` : ''}
      
      ${message.status === 'pending' || message.status === 'processing' ? `
        <button onclick="pollStatus('${message.id}')" class="mt-3 px-3 py-1.5 bg-blue-500 text-white rounded-lg text-xs">
          🔄 刷新状态
        </button>
      ` : ''}
    </div>
  `;
}
```

---

## JavaScript 功能

### 1. 发送测试消息

```javascript
async function sendTestMessage() {
  const input = document.getElementById('testMessage');
  const text = input.value.trim();
  
  if (!text) {
    alert('请输入消息内容');
    return;
  }
  
  const button = event.target;
  button.disabled = true;
  button.textContent = '发送中...';
  
  try {
    const response = await fetch('/siri-dream/api/message', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        text: text,
        metadata: {source: 'web'}
      })
    });
    
    const result = await response.json();
    
    if (result.success) {
      input.value = '';
      
      // 显示成功提示
      showNotification('✅ 消息已发送，正在处理...');
      
      // 轮询状态
      pollStatus(result.message_id);
    } else {
      alert('发送失败：' + result.error);
    }
  } catch (error) {
    alert('发送失败：' + error.message);
  } finally {
    button.disabled = false;
    button.textContent = '发送';
  }
}
```

### 2. 加载消息列表

```javascript
async function loadMessages() {
  const response = await fetch('/siri-dream/api/messages?limit=50');
  const messages = await response.json();
  
  const container = document.getElementById('messagesList');
  
  if (messages.length === 0) {
    container.innerHTML = `
      <div class="text-center py-12">
        <div class="text-6xl mb-4">📨</div>
        <p class="text-gray-500">还没有消息，发送第一条测试消息吧~</p>
      </div>
    `;
    return;
  }
  
  container.innerHTML = messages.map(msg => renderMessageCard(msg)).join('');
  
  updateStats(messages);
}
```

### 3. 轮询状态

```javascript
async function pollStatus(messageId) {
  const response = await fetch(`/siri-dream/api/message/${messageId}`);
  const message = await response.json();
  
  if (message.status === 'completed' || message.status === 'failed') {
    // 处理完成，重新加载列表
    loadMessages();
    showNotification(message.status === 'completed' ? '✅ 处理完成' : '❌ 处理失败');
  } else {
    // 继续轮询
    setTimeout(() => pollStatus(messageId), 2000);
  }
}
```

### 4. 更新统计

```javascript
function updateStats(messages) {
  const total = messages.length;
  const pending = messages.filter(m => m.status === 'pending').length;
  const completed = messages.filter(m => m.status === 'completed').length;
  const failed = messages.filter(m => m.status === 'failed').length;
  
  const today = messages.filter(m => {
    const msgDate = new Date(m.timestamp * 1000);
    const today = new Date();
    return msgDate.toDateString() === today.toDateString();
  }).length;
  
  document.getElementById('totalMessages').textContent = total;
  document.getElementById('pendingMessages').textContent = pending;
  document.getElementById('completedMessages').textContent = completed;
  document.getElementById('failedMessages').textContent = failed;
  document.getElementById('todayMessages').textContent = today;
}
```

### 5. 刷新消息

```javascript
function refreshMessages() {
  const button = event.target;
  button.textContent = '🔄 刷新中...';
  
  loadMessages().then(() => {
    setTimeout(() => {
      button.textContent = '🔄 刷新';
    }, 500);
  });
}

// 自动刷新（每 10 秒）
setInterval(() => {
  loadMessages();
}, 10000);
```

---

## CSS 样式

### 主题色
```css
.gradient-bg {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
}
```

### 消息状态样式
```css
/* 待处理 - 黄色 */
.status-pending {
  border-left: 4px solid #f59e0b;
}

/* 处理中 - 蓝色 */
.status-processing {
  border-left: 4px solid #3b82f6;
}

/* 已完成 - 绿色 */
.status-completed {
  border-left: 4px solid #10b981;
}

/* 失败 - 红色 */
.status-failed {
  border-left: 4px solid #ef4444;
}
```

### 新消息高亮
```css
.new-message {
  animation: highlight 2s ease-out;
}
@keyframes highlight {
  0% { background-color: rgba(59, 130, 246, 0.3); }
  100% { background-color: transparent; }
}
```

### API 代码块
```css
.code-block {
  background: #0f172a;
  color: #e2e8f0;
  padding: 1rem;
  border-radius: 0.5rem;
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 0.875rem;
  overflow-x: auto;
}
```

---

## API 调用

| 端点 | 方法 | 说明 |
|------|------|------|
| `/siri-dream/api/message` | POST | 发送消息 |
| `/siri-dream/api/message/{id}` | GET | 查询单条消息 |
| `/siri-dream/api/messages` | GET | 获取消息列表 |
| `/siri-dream/api/stats` | GET | 获取统计 |
| `/siri-dream/api/messages/{id}` | DELETE | 删除消息 |

---

## API 文档展示

```html
<div class="glass-card rounded-3xl p-6 mb-6">
  <h2 class="text-xl font-bold mb-4">📚 API 文档</h2>
  
  <div class="space-y-4">
    <div>
      <h3 class="font-bold text-sm mb-2">发送消息</h3>
      <div class="code-block">
POST /siri-dream/api/message
Content-Type: application/json

{
  "text": "消息内容",
  "metadata": {"source": "web"}
}
      </div>
    </div>
    
    <div>
      <h3 class="font-bold text-sm mb-2">查询状态</h3>
      <div class="code-block">
GET /siri-dream/api/message/{message_id}

响应:
{
  "id": "uuid",
  "text": "消息内容",
  "status": "completed",
  "result": {"message": "AI 回复"}
}
      </div>
    </div>
  </div>
</div>
```

---

## 响应式设计

### 统计卡片响应
```html
<div class="grid grid-cols-2 sm:grid-cols-5 gap-4">
  <!-- 移动端 2 列，桌面端 5 列 -->
</div>
```

### 移动端适配
```css
@media (max-width: 640px) {
  h1 { font-size: 28px !important; }
  .stats-card { grid-template-columns: repeat(2, 1fr); }
}
```

---

## 动画效果

### 滑入动画
```css
.slide-in {
  animation: slideIn 0.4s ease-out;
}
@keyframes slideIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
```

### 浮动动画
```css
.floating {
  animation: floating 3s ease-in-out infinite;
}
@keyframes floating {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}
```

---

## 使用流程

### 1. 发送测试消息
```
访问页面
    ↓
在"测试消息"输入框输入内容
    ↓
点击"发送"
    ↓
立即返回 message_id
    ↓
自动轮询状态（每 2 秒）
    ↓
状态变为 completed/failed
    ↓
显示 AI 回复
```

### 2. 查看历史消息
```
页面自动加载最近 50 条消息
    ↓
查看每条消息的状态
    ↓
点击"刷新状态"手动更新
    ↓
或等待自动刷新（10 秒间隔）
```

### 3. 查看 API 文档
```
滚动到页面底部
    ↓
查看 API 文档区域
    ↓
复制示例代码
    ↓
用于开发测试
```

---

## 设计亮点

### 1. 实时状态追踪
- 4 种状态颜色区分（黄/蓝/绿/红）
- 自动轮询更新
- 手动刷新按钮

### 2. 统计面板
- 5 个维度统计（总数/待处理/已完成/失败/今日）
- 渐变色数字显示
- 实时更新

### 3. API 文档
- 内置 API 使用说明
- 代码块展示请求/响应格式
- 方便开发者快速上手

### 4. 科技感设计
- 深蓝灰色主题
- 玻璃卡片效果
- 代码块样式

---

## 常见问题

### Q: 消息处理需要多久？
A: 通常 5-30 秒，取决于 AI 响应速度。

### Q: 如何知道消息处理完成了？
A: 状态从"待处理"→"处理中"→"已完成"，或收到通知。

### Q: 消息会保存多久？
A: 最多保留 100 条，超出后自动删除最旧的。

### Q: 数据保存在哪里？
A: `/root/.openclaw/workspace/data/siri-dream/messages.json`

---

*最后更新：2026-03-02*
