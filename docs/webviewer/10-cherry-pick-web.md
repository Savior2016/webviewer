# 10 - Cherry Pick Web (www/cherry-pick/index.html)

## 功能概述

搬家物品追踪 Web 界面，核心功能：
- 创建搬家活动
- 记录物品位置变化
- 物品状态追踪（待打包/已打包/已放置）
- 自动同步到 Momhand
- AI 助手对话

**文件**: `/root/.openclaw/workspace/www/cherry-pick/index.html`
**行数**: 483 行
**大小**: ~19KB
**主题色**: 紫色系 (#4c1d95 → #6d28d9)

---

## 页面布局

```
┌─────────────────────────────────────┐
│           Header                    │
│   🏠 一搬不丢 · Cherry Pick         │
│   一直搬家，东西也不会弄丢            │
├─────────────────────────────────────┤
│   [统计卡片]                         │
│   总物品：10 | 已同步：6 | 待拆封：4  │
├─────────────────────────────────────┤
│   [创建搬家活动]                     │
│   [输入框] [创建]                    │
├─────────────────────────────────────┤
│   搬家活动列表                       │
│  ┌─────────────────────────────┐   │
│  │ 📦 春节搬家 (2026-02-01)    │   │
│  │ 10 个物品 · 6 已放置          │   │
│  │                              │   │
│  │ [添加物品] [查看] [编辑]     │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

---

## 核心组件

### 1. 统计卡片

```html
<div id="statsCard" class="grid grid-cols-3 gap-4 mb-6">
  <div class="glass-card rounded-2xl p-4 text-center">
    <div class="text-3xl font-extrabold bg-gradient-to-r from-purple-500 to-pink-500 bg-clip-text text-transparent" id="totalItems">0</div>
    <div class="text-xs text-gray-600 font-medium mt-1">总物品</div>
  </div>
  
  <div class="glass-card rounded-2xl p-4 text-center">
    <div class="text-3xl font-extrabold bg-gradient-to-r from-green-500 to-emerald-500 bg-clip-text text-transparent" id="syncedItems">0</div>
    <div class="text-xs text-gray-600 font-medium mt-1">已同步</div>
  </div>
  
  <div class="glass-card rounded-2xl p-4 text-center">
    <div class="text-3xl font-extrabold bg-gradient-to-r from-amber-500 to-orange-500 bg-clip-text text-transparent" id="pendingItems">0</div>
    <div class="text-xs text-gray-600 font-medium mt-1">待拆封</div>
  </div>
</div>
```

### 2. 创建搬家活动

```html
<div class="glass-card rounded-3xl p-6 mb-6">
  <div class="flex items-center gap-3 mb-4">
    <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500">📦</div>
    <h2 class="text-xl font-bold">创建搬家活动</h2>
  </div>
  
  <div class="flex gap-3">
    <input id="moveName" placeholder="搬家名称（如：搬到新家）" 
           class="flex-1 px-4 py-3 rounded-xl border-2 focus:border-purple-500 outline-none">
    <button onclick="createMove()" 
            class="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-5 py-3 rounded-xl font-semibold">
      创建
    </button>
  </div>
</div>
```

### 3. 搬家活动卡片

```html
<div class="glass-card rounded-2xl p-4 mb-3 slide-in">
  <div class="flex items-center justify-between mb-2">
    <div class="flex items-center gap-3">
      <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-xl">🏠</div>
      <div>
        <h3 class="font-bold text-lg">春节搬家</h3>
        <p class="text-xs text-gray-500">创建于 2026-02-01</p>
      </div>
    </div>
    <div class="text-right">
      <div class="text-sm font-bold text-purple-600">10 个物品</div>
      <div class="text-xs text-gray-500">6 个已放置</div>
    </div>
  </div>
  
  <!-- 进度条 -->
  <div class="mb-3">
    <div class="flex justify-between text-xs mb-1">
      <span>放置进度</span>
      <span>60%</span>
    </div>
    <div class="w-full bg-gray-200 rounded-full h-2">
      <div class="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full" style="width: 60%"></div>
    </div>
  </div>
  
  <!-- 操作按钮 -->
  <div class="flex gap-2">
    <button onclick="addNewItem('moveId')" class="flex-1 px-3 py-2 bg-purple-500 text-white rounded-lg text-sm">添加物品</button>
    <button onclick="viewMove('moveId')" class="flex-1 px-3 py-2 bg-blue-500 text-white rounded-lg text-sm">查看</button>
    <button onclick="editMove('moveId')" class="flex-1 px-3 py-2 bg-amber-500 text-white rounded-lg text-sm">编辑</button>
  </div>
</div>
```

---

## JavaScript 功能

### 1. 加载搬家活动

```javascript
async function loadMoves() {
  const response = await fetch('/cherry-pick/api/moves');
  const moves = await response.json();
  
  const container = document.getElementById('movesList');
  container.innerHTML = moves.map(move => {
    const items = getItemsByMove(move.id);
    const placedCount = items.filter(i => i.after_location && i.after_location !== '未指定').length;
    const percent = items.length > 0 ? Math.round(placedCount / items.length * 100) : 0;
    
    return `
      <div class="glass-card rounded-2xl p-4 mb-3 slide-in">
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-xl">🏠</div>
            <div>
              <h3 class="font-bold text-lg">${move.name}</h3>
              <p class="text-xs text-gray-500">创建于 ${formatDate(move.created_at)}</p>
            </div>
          </div>
          <div class="text-right">
            <div class="text-sm font-bold text-purple-600">${items.length} 个物品</div>
            <div class="text-xs text-gray-500">${placedCount} 个已放置</div>
          </div>
        </div>
        
        <!-- 进度条 -->
        <div class="mb-3">
          <div class="flex justify-between text-xs mb-1">
            <span>放置进度</span>
            <span>${percent}%</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div class="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full" style="width: ${percent}%"></div>
          </div>
        </div>
        
        <div class="flex gap-2">
          <button onclick="addNewItem('${move.id}')" class="flex-1 px-3 py-2 bg-purple-500 text-white rounded-lg text-sm">添加物品</button>
          <button onclick="viewMove('${move.id}')" class="flex-1 px-3 py-2 bg-blue-500 text-white rounded-lg text-sm">查看</button>
        </div>
      </div>
    `;
  }).join('');
  
  updateStats();
}
```

### 2. 创建搬家活动

```javascript
async function createMove() {
  const nameInput = document.getElementById('moveName');
  const name = nameInput.value.trim();
  
  if (!name) {
    alert('请输入搬家活动名称');
    return;
  }
  
  const response = await fetch('/cherry-pick/api/moves', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({name})
  });
  
  const move = await response.json();
  
  nameInput.value = '';
  loadMoves();  // 重新加载
  
  // 自动添加物品
  addNewItem(move.id);
}
```

### 3. 添加物品

```javascript
async function addNewItem(moveId) {
  // 打开模态框或展开面板
  const panel = document.getElementById('addItemPanel');
  panel.classList.remove('hidden');
  
  // 保存当前 moveId
  panel.dataset.moveId = moveId;
}

async function saveItem() {
  const panel = document.getElementById('addItemPanel');
  const moveId = panel.dataset.moveId;
  
  const itemData = {
    name: document.getElementById('itemName').value,
    before_location: document.getElementById('beforeLocation').value,
    pack_location: document.getElementById('packLocation').value,
    after_location: document.getElementById('afterLocation').value
  };
  
  const response = await fetch(`/cherry-pick/api/moves/${moveId}/items`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(itemData)
  });
  
  const item = await response.json();
  
  // 关闭面板
  panel.classList.add('hidden');
  
  // 重新加载
  loadMoves();
}
```

### 4. 更新统计

```javascript
function updateStats() {
  const moves = getAllMoves();
  const allItems = moves.flatMap(move => getItemsByMove(move.id));
  
  const total = allItems.length;
  const synced = allItems.filter(i => i.synced_to_momhand).length;
  const pending = allItems.filter(i => !i.after_location || i.after_location === '未指定').length;
  
  document.getElementById('totalItems').textContent = total;
  document.getElementById('syncedItems').textContent = synced;
  document.getElementById('pendingItems').textContent = pending;
  
  // 显示/隐藏统计卡片
  const statsCard = document.getElementById('statsCard');
  statsCard.classList.toggle('hidden', total === 0);
}
```

### 5. 物品状态样式

```javascript
function getItemClass(item) {
  if (item.after_location && item.after_location !== '未指定') {
    return 'item-done';  // 已放置 - 蓝色
  } else if (item.pack_location && item.pack_location !== '未指定') {
    return 'item-placed';  // 已打包 - 绿色
  } else {
    return 'item-pending';  // 待打包 - 黄色
  }
}
```

---

## CSS 样式

### 主题色
```css
.gradient-bg {
  background: linear-gradient(135deg, #4c1d95 0%, #6d28d9 50%, #7c3aed 100%);
}
```

### 物品状态样式
```css
/* 已打包 - 绿色 */
.item-placed {
  border-left: 4px solid #10b981;
  background: linear-gradient(to right, #d1fae5, #f0fdf4);
}

/* 待打包 - 黄色 */
.item-pending {
  border-left: 4px solid #f59e0b;
  background: linear-gradient(to right, #fef3c7, #fffbeb);
}

/* 已放置 - 蓝色 */
.item-done {
  border-left: 4px solid #3b82f6;
  background: linear-gradient(to right, #dbeafe, #eff6ff);
}
```

### 玻璃卡片
```css
.glass-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}
```

---

## API 调用

| 端点 | 方法 | 说明 |
|------|------|------|
| `/cherry-pick/api/moves` | GET | 获取所有搬家活动 |
| `/cherry-pick/api/moves` | POST | 创建搬家活动 |
| `/cherry-pick/api/moves/{id}` | GET | 获取单个活动 |
| `/cherry-pick/api/moves/{id}` | DELETE | 删除活动 |
| `/cherry-pick/api/moves/{id}/items` | GET | 获取物品列表 |
| `/cherry-pick/api/moves/{id}/items` | POST | 添加物品 |
| `/cherry-pick/api/items/{id}` | PUT | 更新物品 |
| `/cherry-pick/api/items/{id}` | DELETE | 删除物品 |

---

## 数据流

### 添加物品流程
```
用户点击"添加物品"
    ↓
打开添加面板
    ↓
填写物品信息（名称、原位置、打包位置、新位置）
    ↓
POST /cherry-pick/api/moves/{id}/items
    ↓
保存到 moves.json
    ↓
检查 after_location 是否为空
    ↓
如果不为空 → 自动同步到 Momhand
    ↓
重新加载列表
```

### 同步到 Momhand
```javascript
// 后端自动处理（cherry_pick_manager.py）
if after_location and after_location != "未指定":
    _sync_to_momhand(item)
```

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

### 统计卡片响应
```html
<div class="grid grid-cols-3 gap-3 sm:gap-4">
  <!-- 自动适应屏幕宽度 -->
</div>
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

### 悬停效果
```css
.item-card:hover {
  transform: translateY(-3px);
}
```

---

## 相关文件

| 文件 | 说明 |
|------|------|
| `www/cherry-pick/index.html` | 主页面 |
| `www/cherry-pick/move.html` | 活动详情页（待创建） |
| `www/js/agent-chat.js` | AI 聊天组件 |

---

## 使用流程

### 1. 创建搬家活动
```
访问页面
    ↓
输入搬家名称（如"春节搬家"）
    ↓
点击"创建"
    ↓
自动打开添加物品面板
```

### 2. 添加物品
```
点击"添加物品"
    ↓
填写信息：
  - 物品名称：相机
  - 原位置：旧家客厅
  - 打包位置：3 号纸箱
  - 新位置：新家书房
    ↓
保存
    ↓
如果新位置不为空 → 自动同步到 Momhand
```

### 3. 更新物品状态
```
打开活动详情
    ↓
找到对应物品
    ↓
点击编辑
    ↓
更新位置信息
    ↓
保存
```

---

## 设计亮点

### 1. 三色状态系统
- **黄色** (待打包) - 还未处理
- **绿色** (已打包) - 已装箱
- **蓝色** (已放置) - 已归位

### 2. 实时统计
- 总物品数
- 已同步到 Momhand 的数量
- 待拆封/待放置的数量

### 3. 进度可视化
- 每个活动显示放置进度条
- 百分比直观展示完成度

### 4. 智能同步
- 设置新位置后自动同步到 Momhand
- 无需手动重复录入

---

## 常见问题

### Q: 如何删除搬家活动？
A: 在活动卡片上点击"编辑"，找到删除按钮（需确认）。

### Q: 物品同步到 Momhand 后还能修改吗？
A: 可以，但需要手动在 Momhand 中同步更新。

### Q: 一个物品可以有多个位置吗？
A: 物品有三个位置字段：原位置、打包位置、新位置，分别对应搬家的不同阶段。

### Q: 数据保存在哪里？
A: `/root/.openclaw/workspace/webviewer/data/cherry-pick/moves.json`

---

*最后更新：2026-03-02*
