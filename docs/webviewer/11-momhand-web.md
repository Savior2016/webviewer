# 11 - Momhand Web (www/momhand/index.html)

## 功能概述

物品管理 Web 界面，核心功能：
- 物品搜索（名称、位置、用途）
- 分类筛选
- 物品卡片展示
- 快速添加（AI 对话）
- 过期提醒
- 统计面板

**文件**: `/root/.openclaw/workspace/www/momhand/index.html`
**行数**: 397 行
**大小**: ~16KB
**主题色**: 绿色系 (#065f46 → #10b981)

---

## 页面布局

```
┌─────────────────────────────────────┐
│           Header                    │
│   👋 妈妈的手 · Momhand             │
│   "你这孩子，这不就在电视柜上嘛！"    │
├─────────────────────────────────────┤
│   [统计面板]                         │
│   总数 | 即将过期 | 已过期 | 位置数  │
├─────────────────────────────────────┤
│   [搜索框] [分类筛选]                │
│   🔍 找什么东西？...                 │
│   [💊 药品] [🔧 工具] [📄 证件]      │
├─────────────────────────────────────┤
│   物品卡片网格                       │
│  ┌──────┐ ┌──────┐ ┌──────┐        │
│  │相机  │ │感冒药│ │护照  │        │
│  │📷    │ │💊    │ │📄    │        │
│  │电视柜│ │药箱  │ │抽屉  │        │
│  └──────┘ └──────┘ └──────┘        │
└─────────────────────────────────────┘
```

---

## 核心组件

### 1. 统计面板

```javascript
async function loadStats() {
  const response = await fetch('/momhand/api/stats');
  const stats = await response.json();
  
  const container = document.getElementById('stats');
  container.innerHTML = `
    <div class="glass-card rounded-2xl p-4 text-center">
      <div class="text-3xl font-extrabold bg-gradient-to-r from-green-500 to-emerald-500 bg-clip-text text-transparent">${stats.total}</div>
      <div class="text-xs text-gray-600 font-medium mt-1">总物品</div>
    </div>
    <div class="glass-card rounded-2xl p-4 text-center">
      <div class="text-3xl font-extrabold bg-gradient-to-r from-amber-500 to-orange-500 bg-clip-text text-transparent">${stats.expiring_soon}</div>
      <div class="text-xs text-gray-600 font-medium mt-1">即将过期</div>
    </div>
    <div class="glass-card rounded-2xl p-4 text-center">
      <div class="text-3xl font-extrabold bg-gradient-to-r from-red-500 to-pink-500 bg-clip-text text-transparent">${stats.expired}</div>
      <div class="text-xs text-gray-600 font-medium mt-1">已过期</div>
    </div>
    <div class="glass-card rounded-2xl p-4 text-center">
      <div class="text-3xl font-extrabold bg-gradient-to-r from-blue-500 to-cyan-500 bg-clip-text text-transparent">${Object.keys(stats.by_location).length}</div>
      <div class="text-xs text-gray-600 font-medium mt-1">位置数</div>
    </div>
  `;
}
```

### 2. 搜索和筛选

```html
<div class="glass-card rounded-3xl p-6 mb-8">
  <!-- 搜索框 + 分类 -->
  <div class="flex flex-col sm:flex-row gap-4">
    <div class="flex-1 flex items-center gap-3">
      <span class="text-2xl">🔍</span>
      <input id="searchInput" placeholder="找什么东西？试试搜索名称、位置、用途..." 
             class="flex-1 px-4 py-3 rounded-xl border-2 focus:border-green-500 outline-none">
    </div>
    <div class="flex items-center gap-2">
      <span class="text-2xl">📂</span>
      <select id="categoryFilter" class="px-4 py-3 rounded-xl border-2">
        <option value="">全部分类</option>
        <option value="电子产品">电子产品</option>
        <option value="药品">药品</option>
        <option value="书籍">书籍</option>
        <option value="工具">工具</option>
        <option value="证件">证件</option>
      </select>
    </div>
  </div>
  
  <!-- 快速搜索标签 -->
  <div class="mt-4 flex flex-wrap gap-2">
    <button onclick="quickSearch('药品')" class="px-3 py-1.5 bg-green-100 text-green-700 rounded-full text-sm">💊 药品</button>
    <button onclick="quickSearch('工具')" class="px-3 py-1.5 bg-blue-100 text-blue-700 rounded-full text-sm">🔧 工具</button>
    <button onclick="quickSearch('证件')" class="px-3 py-1.5 bg-purple-100 text-purple-700 rounded-full text-sm">📄 证件</button>
    <button onclick="quickSearch('厨房')" class="px-3 py-1.5 bg-orange-100 text-orange-700 rounded-full text-sm">🍳 厨房</button>
  </div>
</div>
```

### 3. 物品卡片

```javascript
function renderItemCard(item) {
  const isExpired = item.expiry_date && new Date(item.expiry_date) < new Date();
  const isExpiringSoon = item.expiry_date && 
    new Date(item.expiry_date) <= new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);
  
  return `
    <div class="glass-card rounded-2xl p-4 slide-in item-card">
      <div class="flex items-start justify-between mb-3">
        <div>
          <h3 class="font-bold text-lg text-gray-800">${item.name}</h3>
          <span class="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-600">${item.type}</span>
        </div>
        ${item.expiry_date ? `
          <span class="text-xs px-2 py-1 rounded-full ${isExpired ? 'bg-red-100 text-red-700' : isExpiringSoon ? 'bg-amber-100 text-amber-700' : 'bg-green-100 text-green-700'}">
            ${isExpired ? '已过期' : isExpiringSoon ? '即将过期' : '正常'}
          </span>
        ` : ''}
      </div>
      
      <div class="space-y-2 text-sm text-gray-600">
        <div class="flex items-center gap-2">
          <span>📍</span>
          <span>${item.location || '未指定'}</span>
        </div>
        ${item.usage ? `
          <div class="flex items-center gap-2">
            <span>💡</span>
            <span class="line-clamp-2">${item.usage}</span>
          </div>
        ` : ''}
        ${item.expiry_date ? `
          <div class="flex items-center gap-2">
            <span>📅</span>
            <span>过期：${item.expiry_date}</span>
          </div>
        ` : ''}
      </div>
      
      <div class="mt-4 flex gap-2">
        <button onclick="editItem(${item.id})" class="flex-1 px-3 py-2 bg-blue-500 text-white rounded-lg text-sm">编辑</button>
        <button onclick="deleteItem(${item.id})" class="flex-1 px-3 py-2 bg-red-500 text-white rounded-lg text-sm">删除</button>
      </div>
    </div>
  `;
}
```

---

## JavaScript 功能

### 1. 加载物品

```javascript
async function loadItems() {
  const response = await fetch('/momhand/api/items');
  const items = await response.json();
  
  const container = document.getElementById('itemsGrid');
  
  if (items.length === 0) {
    container.innerHTML = `
      <div class="text-center py-12 col-span-full">
        <div class="text-6xl mb-4">📦</div>
        <p class="text-gray-500">还没有物品，点击上方按钮添加第一个物品吧~</p>
      </div>
    `;
    return;
  }
  
  container.innerHTML = items.map(item => renderItemCard(item)).join('');
}
```

### 2. 搜索物品

```javascript
async function searchItems() {
  const keyword = document.getElementById('searchInput').value.trim();
  const category = document.getElementById('categoryFilter').value;
  
  if (!keyword && !category) {
    loadItems();
    return;
  }
  
  let url = '/momhand/api/search?q=' + encodeURIComponent(keyword);
  if (category) {
    url += '&category=' + encodeURIComponent(category);
  }
  
  const response = await fetch(url);
  const items = await response.json();
  
  const container = document.getElementById('itemsGrid');
  container.innerHTML = items.map(item => renderItemCard(item)).join('');
}

// 快速搜索
function quickSearch(keyword) {
  document.getElementById('searchInput').value = keyword;
  searchItems();
}
```

### 3. 加载分类

```javascript
async function loadCategories() {
  const response = await fetch('/momhand/api/items');
  const items = await response.json();
  
  // 提取所有类型
  const categories = [...new Set(items.map(i => i.type))];
  
  const select = document.getElementById('categoryFilter');
  categories.forEach(cat => {
    const option = document.createElement('option');
    option.value = cat;
    option.textContent = cat;
    select.appendChild(option);
  });
}
```

### 4. 编辑物品

```javascript
async function editItem(itemId) {
  const response = await fetch(`/momhand/api/items/${itemId}`);
  const item = await response.json();
  
  // 打开编辑模态框
  const modal = document.getElementById('editModal');
  modal.classList.remove('hidden');
  
  // 填充表单
  document.getElementById('editName').value = item.name;
  document.getElementById('editType').value = item.type;
  document.getElementById('editLocation').value = item.location;
  document.getElementById('editUsage').value = item.usage;
  document.getElementById('editExpiry').value = item.expiry_date || '';
  
  // 保存按钮绑定
  document.getElementById('saveEditBtn').onclick = async () => {
    const updates = {
      name: document.getElementById('editName').value,
      type: document.getElementById('editType').value,
      location: document.getElementById('editLocation').value,
      usage: document.getElementById('editUsage').value,
      expiry_date: document.getElementById('editExpiry').value
    };
    
    await fetch(`/momhand/api/items/${itemId}`, {
      method: 'PUT',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(updates)
    });
    
    modal.classList.add('hidden');
    loadItems();
  };
}
```

---

## CSS 样式

### 主题色
```css
.gradient-bg {
  background: linear-gradient(135deg, #065f46 0%, #059669 50%, #10b981 100%);
}
```

### 物品卡片悬停
```css
.item-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.item-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.2);
}
```

### 过期状态
```css
/* 已过期 - 红色 */
.status-expired {
  background: rgba(239, 68, 68, 0.1);
  border-left: 4px solid #ef4444;
}

/* 即将过期 - 黄色 */
.status-expiring-soon {
  background: rgba(245, 158, 11, 0.1);
  border-left: 4px solid #f59e0b;
}

/* 正常 - 绿色 */
.status-normal {
  background: rgba(16, 185, 129, 0.1);
  border-left: 4px solid #10b981;
}
```

---

## API 调用

| 端点 | 方法 | 说明 |
|------|------|------|
| `/momhand/api/items` | GET | 获取所有物品 |
| `/momhand/api/items` | POST | 添加物品 |
| `/momhand/api/items/{id}` | GET | 获取单个物品 |
| `/momhand/api/items/{id}` | PUT | 更新物品 |
| `/momhand/api/items/{id}` | DELETE | 删除物品 |
| `/momhand/api/search?q=x` | GET | 搜索物品 |
| `/momhand/api/stats` | GET | 获取统计 |
| `/momhand/api/expiring?days=7` | GET | 即将过期物品 |

---

## 响应式设计

### 网格布局
```html
<div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
  <!-- 自适应列数 -->
</div>
```

### 移动端适配
```css
@media (max-width: 640px) {
  .fab-button { bottom: 16px; right: 16px; }
  .fab-panel { bottom: 90px; right: 16px; left: 16px; }
  h1 { font-size: 28px !important; }
}
```

---

## 使用流程

### 1. 搜索物品
```
输入关键词（名称/位置/用途）
    ↓
自动搜索或点击搜索按钮
    ↓
显示匹配结果
    ↓
点击卡片查看详情
```

### 2. 添加物品
```
点击右下角悬浮按钮
    ↓
展开 AI 对话面板
    ↓
输入"帮我记一下，相机放在电视柜上"
    ↓
AI 自动解析并保存
    ↓
刷新列表显示新物品
```

### 3. 编辑物品
```
找到目标物品卡片
    ↓
点击"编辑"按钮
    ↓
修改信息
    ↓
保存
```

---

## 设计亮点

### 1. 智能搜索
- 支持名称、位置、用途多字段搜索
- 快速搜索标签（药品、工具、证件、厨房）
- 分类筛选

### 2. 过期提醒
- 红色标记已过期物品
- 黄色标记即将过期（7 天内）
- 统计面板显示数量

### 3. 卡片设计
- 悬停上浮效果
- 信息层次清晰
- 状态标签直观

### 4. 快速操作
- 悬浮按钮（AI 对话）
- 编辑/删除按钮
- 一键搜索标签

---

## 常见问题

### Q: 如何设置物品过期日期？
A: 编辑物品时，在"过期日期"字段输入 YYYY-MM-DD 格式。

### Q: 搜索支持模糊匹配吗？
A: 支持，使用 LIKE 进行模糊匹配。

### Q: 如何批量添加物品？
A: 使用 AI 对话功能，可以说"帮我记录：相机在电视柜，感冒药在药箱"。

### Q: 数据保存在哪里？
A: SQLite 数据库 `/root/.openclaw/workspace/webviewer/data/momhand.db`

---

*最后更新：2026-03-02*
