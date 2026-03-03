# 09 - By Design Web (www/bydesign/index.html)

## 功能概述

出行检查清单 Web 界面，核心功能：
- 通用检查清单管理
- 出行记录创建/查看
- 检查项完成状态追踪
- 进度可视化
- AI 助手对话

**文件**: `/root/.openclaw/workspace/www/bydesign/index.html`
**行数**: 872 行
**大小**: ~35KB
**主题色**: 蓝色系 (#1e3a5f → #0f4c75)

---

## 页面布局

```
┌─────────────────────────────────────┐
│           Header                    │
│   ✈️ 已读不回 · By Design           │
│   出远门前读了这个，就不需要单独返回  │
├─────────────────────────────────────┤
│   [通用检查清单]  │  [最新出行]     │
│   📋 5 项          │  📝 上海出差 3 天 │
│   □ 关闭窗户      │  进度：60%      │
│   □ 关闭电源      │  □□□■□□        │
│   □ 检查门锁      │  [查看] [完成]  │
│   □ 清空垃圾      │                │
│   □ 检查水龙头    │                │
├─────────────────────────────────────┤
│         历史出行记录列表             │
│  ┌─────────────────────────────┐   │
│  │ 上海出差 3 天 · 60%          │   │
│  │ 北京旅行 5 天 · 100% ✅      │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

---

## 核心组件

### 1. 通用检查清单

```html
<div class="glass-card rounded-3xl p-6">
  <div class="flex items-center gap-3 mb-4">
    <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-500">📋</div>
    <div>
      <h2 class="text-xl font-bold">通用检查清单</h2>
      <p class="text-xs text-gray-500" id="checklistCount">0 项 · 每次出行都会同步</p>
    </div>
  </div>
  
  <!-- 添加输入框 -->
  <div class="flex gap-2 mb-3">
    <input id="checklistInput" placeholder="添加通用检查项..." class="flex-1 px-3 py-2 rounded-lg border-2">
    <button onclick="addChecklistItem()" class="px-4 py-2 bg-gradient-to-r from-indigo-500 to-purple-500 text-white rounded-lg">添加</button>
  </div>
  
  <!-- 检查项列表 -->
  <div id="checklistItems" class="space-y-2 max-h-64 overflow-y-auto">
    <!-- 动态生成 -->
  </div>
</div>
```

### 2. 最新出行卡片

```html
<div class="glass-card rounded-3xl p-6">
  <div class="flex items-center gap-3 mb-4">
    <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500">📝</div>
    <div>
      <h2 class="text-xl font-bold">最新出行</h2>
      <p class="text-xs text-gray-500" id="latestTripInfo">暂无出行记录</p>
    </div>
  </div>
  
  <div id="latestTripContent">
    <!-- 出行详情 -->
    <h3 class="text-lg font-bold mb-2">上海出差 3 天</h3>
    
    <!-- 进度条 -->
    <div class="mb-3">
      <div class="flex justify-between text-xs mb-1">
        <span>进度</span>
        <span>60%</span>
      </div>
      <div class="w-full bg-gray-200 rounded-full h-2">
        <div class="bg-gradient-to-r from-blue-500 to-cyan-500 h-2 rounded-full" style="width: 60%"></div>
      </div>
    </div>
    
    <!-- 检查项预览 -->
    <div class="space-y-2 mb-4">
      <label class="flex items-center gap-2 checklist-item">
        <input type="checkbox" class="w-4 h-4">
        <span class="item-text text-sm">关闭所有窗户</span>
      </label>
    </div>
    
    <!-- 操作按钮 -->
    <div class="flex gap-2">
      <button onclick="viewTrip()" class="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg">查看</button>
      <button onclick="completeTrip()" class="flex-1 px-4 py-2 bg-green-500 text-white rounded-lg">完成</button>
    </div>
  </div>
</div>
```

---

## JavaScript 功能

### 1. 加载检查清单

```javascript
async function loadChecklist() {
  const response = await fetch('/bydesign/api/checklist');
  const checklist = await response.json();
  
  const container = document.getElementById('checklistItems');
  container.innerHTML = checklist.items.map(item => `
    <div class="checklist-item flex items-center gap-3 p-3 rounded-lg ${item.completed ? 'completed' : ''}">
      <input type="checkbox" ${item.completed ? 'checked' : ''} 
             onchange="toggleChecklistItem('${item.id}', this.checked)"
             class="w-4 h-4 text-indigo-600 rounded">
      <span class="item-text flex-1 text-sm">${item.text}</span>
      <button onclick="deleteChecklistItem('${item.id}')" class="text-gray-400 hover:text-red-500">🗑️</button>
    </div>
  `).join('');
  
  document.getElementById('checklistCount').textContent = `${checklist.items.length} 项 · 每次出行都会同步`;
}
```

### 2. 添加检查项

```javascript
async function addChecklistItem() {
  const input = document.getElementById('checklistInput');
  const text = input.value.trim();
  
  if (!text) return;
  
  const response = await fetch('/bydesign/api/checklist/items', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({text})
  });
  
  const result = await response.json();
  if (result.success) {
    input.value = '';
    loadChecklist();  // 重新加载
  }
}
```

### 3. 创建出行

```javascript
async function createTrip() {
  const name = document.getElementById('tripName').value.trim();
  const description = document.getElementById('tripDesc').value.trim();
  
  const response = await fetch('/bydesign/api/trips', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({name, description})
  });
  
  const trip = await response.json();
  
  // 跳转到出行详情页
  window.location.href = `/bydesign/trip.html?id=${trip.id}`;
}
```

### 4. 加载出行列表

```javascript
async function loadTrips() {
  const response = await fetch('/bydesign/api/trips');
  const trips = await response.json();
  
  const container = document.getElementById('tripsList');
  container.innerHTML = trips.map(trip => {
    const progress = calculateProgress(trip);
    return `
      <div class="glass-card rounded-2xl p-4 mb-3 slide-in">
        <div class="flex items-center justify-between mb-2">
          <h3 class="font-bold text-lg">${trip.name}</h3>
          <span class="text-xs px-2 py-1 rounded-full ${trip.status === 'completed' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'}">
            ${trip.status === 'completed' ? '✅ 已完成' : '📝 计划中'}
          </span>
        </div>
        
        <div class="flex items-center gap-2 text-xs text-gray-500 mb-2">
          <span>📅 ${formatDate(trip.created_at)}</span>
          <span>·</span>
          <span>📋 ${trip.checklist_snapshot.length} 项检查</span>
        </div>
        
        <!-- 进度条 -->
        <div class="mb-3">
          <div class="flex justify-between text-xs mb-1">
            <span>进度</span>
            <span>${progress.percent}%</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div class="bg-gradient-to-r from-blue-500 to-cyan-500 h-2 rounded-full" style="width: ${progress.percent}%"></div>
          </div>
        </div>
        
        <div class="flex gap-2">
          <button onclick="viewTrip('${trip.id}')" class="flex-1 px-3 py-2 bg-blue-500 text-white rounded-lg text-sm">查看</button>
          ${trip.status !== 'completed' ? `<button onclick="completeTrip('${trip.id}')" class="flex-1 px-3 py-2 bg-green-500 text-white rounded-lg text-sm">完成</button>` : ''}
        </div>
      </div>
    `;
  }).join('');
}
```

### 5. 计算进度

```javascript
function calculateProgress(trip) {
  const checklist = trip.checklist_snapshot || [];
  const custom = trip.custom_items || [];
  
  const checklistTotal = checklist.length;
  const checklistDone = checklist.filter(i => i.completed).length;
  const customTotal = custom.length;
  const customDone = custom.filter(i => i.completed).length;
  
  const total = checklistTotal + customTotal;
  const done = checklistDone + customDone;
  
  return {
    checklist: {total: checklistTotal, done: checklistDone},
    custom: {total: customTotal, done: customDone},
    overall: {
      total,
      done,
      percent: total > 0 ? Math.round(done / total * 100) : 0
    }
  };
}
```

---

## CSS 样式

### 主题色
```css
.gradient-bg {
  background: linear-gradient(135deg, #1e3a5f 0%, #0f4c75 50%, #1b5e8b 100%);
}
```

### 玻璃卡片
```css
.glass-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}
```

### 检查项完成状态
```css
.checklist-item.completed {
  opacity: 0.6;
}
.checklist-item.completed .item-text {
  text-decoration: line-through;
  color: #9ca3af;
}
```

### 分隔线
```css
.section-separator {
  border-top: 2px dashed rgba(209, 213, 219, 0.5);
  margin: 1rem 0;
  position: relative;
}
.section-separator::after {
  content: '通用检查清单';
  position: absolute;
  left: 50%;
  top: -10px;
  transform: translateX(-50%);
  background: linear-gradient(135deg, #1e3a5f 0%, #0f4c75 50%, #1b5e8b 100%);
  padding: 0 1rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  color: rgba(255,255,255,0.7);
}
```

---

## API 调用

| 端点 | 方法 | 说明 |
|------|------|------|
| `/bydesign/api/checklist` | GET | 获取通用检查清单 |
| `/bydesign/api/checklist/items` | POST | 添加检查项 |
| `/bydesign/api/checklist/items/{id}` | PUT | 更新检查项 |
| `/bydesign/api/checklist/items/{id}` | DELETE | 删除检查项 |
| `/bydesign/api/trips` | GET | 获取所有出行 |
| `/bydesign/api/trips` | POST | 创建出行 |
| `/bydesign/api/trips/{id}` | GET | 获取单个出行 |
| `/bydesign/api/trips/{id}` | PUT | 更新出行 |
| `/bydesign/api/trips/{id}` | DELETE | 删除出行 |

---

## 响应式设计

### 移动端适配
```css
@media (max-width: 640px) {
  .fab-button { bottom: 16px; right: 16px; }
  .fab-panel { bottom: 90px; right: 16px; left: 16px; }
  h1 { font-size: 28px !important; }
}
```

### 布局响应
```html
<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
  <!-- 左侧：通用检查清单 -->
  <!-- 右侧：最新出行 -->
</div>
```

---

## 动画效果

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

### 展开动画
```css
.expand-in {
  animation: expandIn 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
@keyframes expandIn {
  0% { transform: scale(0.9) translateY(20px); opacity: 0; }
  100% { transform: scale(1) translateY(0); opacity: 1; }
}
```

---

## 相关文件

| 文件 | 说明 |
|------|------|
| `www/bydesign/index.html` | 主页面 |
| `www/bydesign/trip.html` | 出行详情页（待创建） |
| `www/js/agent-chat.js` | AI 聊天组件 |
| `www/transitions.css` | 过渡动画 |

---

## 使用流程

### 1. 首次使用
```
访问页面
    ↓
自动加载通用检查清单
    ↓
查看默认 5 项检查
    ↓
可添加自定义检查项
```

### 2. 创建出行
```
点击"创建出行"
    ↓
输入名称和描述
    ↓
自动复制通用检查清单
    ↓
跳转到出行详情页
    ↓
逐项完成检查
```

### 3. 完成出行
```
打开出行详情
    ↓
完成所有检查项
    ↓
点击"完成出行"
    ↓
状态变为 completed
    ↓
进度 100%
```

---

## 设计亮点

### 1. 双栏布局
- 左侧：通用检查清单（每次出行同步）
- 右侧：最新出行（当前任务）

### 2. 进度可视化
- 进度条显示完成百分比
- 颜色区分状态（蓝=进行中，绿=已完成）

### 3. 智能提示
- 检查项完成时自动划线
- 透明度降低表示已完成

### 4. 悬浮按钮
- 右下角 AI 助手入口
- 点击展开对话面板

---

## 常见问题

### Q: 如何添加自定义检查项？
A: 在通用检查清单输入框中输入，点击"添加"按钮。

### Q: 出行创建后能修改吗？
A: 可以，在出行详情页可以修改名称、描述和检查项。

### Q: 如何删除出行？
A: 在出行列表中找到对应出行，点击删除按钮（需确认）。

### Q: 数据保存在哪里？
A: `/root/.openclaw/workspace/webviewer/data/bydesign/trips.json`

---

*最后更新：2026-03-02*
