# 08 - 主页面 UI (www/index.html)

## 功能概述

WebViewer 主页面，核心功能：
- 工具卡片导航（4 个子项目）
- AI 聊天界面
- 系统设置（提示词配置）
- 日志查看
- 版本信息

**文件**: `/root/.openclaw/workspace/www/index.html`
**行数**: 934 行
**大小**: ~37KB
**框架**: Tailwind CSS (CDN)

---

## 页面结构

```
┌─────────────────────────────────────┐
│           Header                    │
│   🤖 Dummy 的小弟们                  │
│   你的生活管理工具集                 │
├─────────────────────────────────────┤
│         Chat Interface              │
│  ┌─────────────────────────────┐   │
│  │  🤖 Dummy 助手 [💬][🗑️][⚙️]  │   │
│  ├─────────────────────────────┤   │
│  │  聊天消息区域                │   │
│  │  (可滚动)                    │   │
│  ├─────────────────────────────┤   │
│  │  [输入框] [发送]             │   │
│  │  示例：出差 3 天 | 记录物品   │   │
│  └─────────────────────────────┘   │
├─────────────────────────────────────┤
│         Tools Grid                  │
│  ┌──────┐ ┌──────┐ ┌──────┐        │
│  │已读不回│ │一搬不丢│ │妈妈的手│        │
│  └──────┘ └──────┘ └──────┘        │
│  ┌──────┐                          │
│  │Siri 尉来│                          │
│  └──────┘                          │
├─────────────────────────────────────┤
│           Footer                    │
│  🎯 让生活更有序 · [日志] [版本] [证书] │
└─────────────────────────────────────┘
```

---

## 核心组件

### 1. Header（头部）

```html
<header class="text-center mb-8">
  <div class="text-7xl floating">🤖</div>
  <h1 class="text-5xl font-extrabold bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400">
    Dummy 的小弟们
  </h1>
  <p class="text-gray-300">Dummy's Minions · 你的生活管理工具集</p>
</header>
```

**特性**:
- 渐变文字效果
- 浮动动画（floating）
- 响应式字体（sm:text-7xl）

---

### 2. Chat Interface（聊天界面）

#### Chat Header
```html
<div class="bg-gradient-to-r from-purple-500 to-pink-500 px-6 py-4">
  <div class="flex items-center justify-between">
    <div class="flex items-center gap-3">
      <div class="text-3xl">🤖</div>
      <div>
        <h3 class="text-lg font-bold text-white">Dummy 助手</h3>
        <p class="text-xs text-purple-100">理解你的意图，帮你操作三个项目</p>
      </div>
    </div>
    <div class="flex items-center gap-2">
      <span class="text-xs bg-white/20 px-3 py-1 rounded-full">💬 在线</span>
      <button onclick="clearHistory()">🗑️</button>
      <button onclick="showSettings()">⚙️</button>
    </div>
  </div>
</div>
```

#### Chat Messages
```html
<div id="chatMessages" class="h-80 overflow-y-auto p-6 space-y-4">
  <!-- 消息气泡 -->
  <div class="flex items-start gap-3">
    <div class="w-10 h-10 rounded-full bg-gradient-to-r from-purple-500 to-pink-500">🤖</div>
    <div class="bg-white rounded-2xl rounded-tl-none px-4 py-3 shadow-sm">
      <p class="text-sm text-gray-700">你好！我是 Dummy 助手 👋</p>
    </div>
  </div>
</div>
```

#### Input Area
```html
<div class="border-t p-4 bg-white">
  <div class="flex gap-3">
    <input id="messageInput" class="flex-1 px-4 py-3 rounded-xl border-2 focus:border-purple-500">
    <button onclick="sendMessage()" class="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-6 py-3">
      📤 发送
    </button>
  </div>
  <div class="flex gap-2">
    <button onclick="fillExample('我要出差 3 天')">✈️ 出差 3 天</button>
    <button onclick="fillExample('帮我记一下，我的大疆 action4 放在了电视柜...')">📦 记录物品</button>
    <button onclick="fillExample('找一下感冒药放在哪里')">🔍 找东西</button>
  </div>
</div>
```

---

### 3. Tools Grid（工具卡片）

```html
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
  <!-- By Design -->
  <a href="/bydesign/" class="tool-card" style="--from: #3b82f6; --to: #06b6d4;">
    <div class="tool-icon text-3xl">✈️</div>
    <h2 class="text-xl font-bold">已读不回</h2>
    <p class="text-xs text-gray-500">By Design</p>
    <p class="text-sm text-gray-600">出远门前读了这个，就不需要单独返回</p>
  </a>
  
  <!-- Cherry Pick -->
  <a href="/cherry-pick/" style="--from: #8b5cf6; --to: #ec4899;">
    <div class="tool-icon">🏠</div>
    <h2>一搬不丢</h2>
    <p>Cherry Pick</p>
    <p>一直搬家，东西也不会弄丢</p>
  </a>
  
  <!-- Momhand -->
  <a href="/momhand/" style="--from: #10b981; --to: #3b82f6;">
    <div class="tool-icon">👋</div>
    <h2>妈妈的手</h2>
    <p>Momhand</p>
    <p>"你这孩子，这不就在电视柜上嘛！"</p>
  </a>
  
  <!-- Siri Dream -->
  <a href="/siri-dream/" style="--from: #3b82f6; --to: #9333ea;">
    <div class="tool-icon">🤖</div>
    <h2>Siri 的尉来</h2>
    <p>SiriFuture</p>
    <p>"Siri 会的我都会啊，我会的 Siri 不会啊"</p>
  </a>
</div>
```

**卡片特效**:
- 悬停上浮（translateY(-8px)）
- 阴影增强
- 图标旋转放大
- 渐变背景

---

### 4. Footer（底部）

```html
<footer class="text-center py-4 border-t border-white/10">
  <div class="flex flex-col items-center gap-2">
    <div class="flex gap-3">
      <p>🎯 让生活更有序 · Powered by OpenClaw</p>
      <button onclick="showLogs()">📜 运行日志</button>
      <button onclick="showVersion()">📋 版本</button>
      <a href="/server.crt">🔒 证书</a>
    </div>
    <p class="text-xs">v1.5.3 · 日志增强版</p>
  </div>
</footer>
```

---

## JavaScript 功能

### 1. 消息发送

```javascript
async function sendMessage() {
  const message = document.getElementById('messageInput').value;
  
  // 添加用户消息
  addMessage(message, true);
  
  // 显示输入中
  showTyping();
  
  try {
    const response = await fetch('/api/send-message', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message, timestamp: Date.now()})
    });
    
    const result = await response.json();
    removeTyping();
    
    if (result.success) {
      if (result.processing) {
        // 异步处理，开始轮询
        pollResult(result.msg_id);
      } else {
        // 同步完成
        addMessage(formatResult(result.message), false);
      }
    }
  } catch (error) {
    addMessage('发送失败，请检查网络连接', false);
  }
}
```

### 2. 结果轮询

```javascript
function pollResult(msgId) {
  let attempts = 0;
  const maxAttempts = 60;
  
  const pollTimer = setInterval(async () => {
    attempts++;
    const response = await fetch(`/api/message-result?msg_id=${msgId}`);
    const result = await response.json();
    
    if (result.processed || !result.success) {
      clearInterval(pollTimer);
      
      if (result.data && result.data.success !== false) {
        addMessage(formatResult(result.data.message), false);
        
        if (result.data.refresh) {
          setTimeout(() => {
            window.location.href = result.data.refresh;
          }, 2000);
        }
      }
    } else if (attempts >= maxAttempts) {
      clearInterval(pollTimer);
      addMessage('处理超时，请刷新页面查看结果', false);
    }
  }, 500);
}
```

### 3. 历史记录

```javascript
function loadHistory() {
  const history = JSON.parse(localStorage.getItem('chatHistory') || '[]');
  const messagesDiv = document.getElementById('chatMessages');
  
  history.forEach(msg => {
    const messageDiv = document.createElement('div');
    messageDiv.innerHTML = msg.isUser ? userTemplate : botTemplate;
    messagesDiv.appendChild(messageDiv);
  });
}

function saveToHistory(content, isUser) {
  const history = JSON.parse(localStorage.getItem('chatHistory') || '[]');
  history.push({content, isUser, timestamp: Date.now()});
  
  // 限制最多 50 条
  if (history.length > 50) history.shift();
  
  localStorage.setItem('chatHistory', JSON.stringify(history));
}
```

### 4. 日志查看

```javascript
async function showLogs() {
  const modal = document.getElementById('logsModal');
  modal.classList.remove('hidden');
  await loadLogs();
}

async function loadLogs(lines = 200) {
  const response = await fetch(`/api/logs?lines=${lines}`);
  const result = await response.json();
  
  const logs = result.logs || [];
  document.getElementById('logsContent').innerHTML = logs.map(line => {
    let colorClass = 'text-green-400';
    if (line.includes('ERROR') || line.includes('❌')) colorClass = 'text-red-400';
    else if (line.includes('WARN')) colorClass = 'text-yellow-400';
    
    return `<div class="${colorClass}">${escapeHtml(line)}</div>`;
  }).join('');
}
```

### 5. 设置管理

```javascript
async function showSettings() {
  const modal = document.getElementById('settingsModal');
  modal.classList.remove('hidden');
  
  const response = await fetch('/api/settings');
  const data = await response.json();
  document.getElementById('systemPrompt').value = data.prompt || DEFAULT_PROMPT;
}

async function saveSettings() {
  const prompt = document.getElementById('systemPrompt').value;
  
  const response = await fetch('/api/settings', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({prompt})
  });
  
  const result = await response.json();
  if (result.success) {
    alert('✅ 设置已保存');
  }
}
```

---

## CSS 动画

### 1. 浮动动画
```css
.floating {
  animation: floating 3s ease-in-out infinite;
}
@keyframes floating {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}
```

### 2. 滑入动画
```css
.slide-in {
  animation: slideIn 0.5s ease-out;
}
@keyframes slideIn {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}
```

### 3. 输入点动画
```css
.typing-dot {
  animation: typing 1.4s infinite;
}
@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-10px); }
}
```

### 4. 卡片悬停
```css
.tool-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.25);
}
.tool-card:hover .tool-icon {
  transform: scale(1.1) rotate(-5deg);
}
```

---

## 响应式设计

### 断点
- **sm**: 640px (平板)
- **lg**: 1024px (桌面)

### 适配示例
```html
<!-- 字体大小响应 -->
<p class="text-sm sm:text-base">...</p>

<!-- 布局响应 -->
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">...</div>

<!-- 显示/隐藏响应 -->
<span class="hidden sm:inline">发送</span>
```

---

## 模态框

### 1. Settings Modal
- 系统提示词编辑
- 保存/重置功能

### 2. Version Modal
- 版本信息
- 项目说明

### 3. Logs Modal
- 日志查看
- 刷新/下载功能

---

## 相关文件

| 文件 | 说明 |
|------|------|
| `www/index.html` | 主页面 |
| `www/transitions.css` | 过渡动画 |
| `www/js/agent-chat.js` | 聊天逻辑（独立） |

---

## 性能优化

### 1. CDN 资源
- Tailwind CSS: `cdn.tailwindcss.com`
- Google Fonts

### 2. 本地存储
- 聊天记录保存在 `localStorage`
- 限制最多 50 条

### 3. 懒加载
- 管理器延迟加载
- 日志按需加载

---

## 常见问题

### Q: 如何修改欢迎消息？
A: 编辑 `index.html` 第 108 行左右的 Welcome Message 部分。

### Q: 如何添加新的示例按钮？
A: 在 Input Area 部分添加新的 `<button>`，绑定 `onclick="fillExample('...')"`.

### Q: 聊天历史保存在哪里？
A: 浏览器的 `localStorage`，键名 `chatHistory`。

### Q: 如何自定义主题颜色？
A: 修改 Tailwind 配置和 CSS 变量（`--from`, `--to`）。

---

*最后更新：2026-03-02*
