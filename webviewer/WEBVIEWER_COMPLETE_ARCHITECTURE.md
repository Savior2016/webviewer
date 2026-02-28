# WebViewer 完整架构文档

> ⚠️ **重要**：修改本项目前必须阅读此文档，确保不破坏已有功能。

**创建时间**: 2026-02-28  
**最后更新**: 2026-02-28  
**维护者**: Friday

---

## 📋 目录

1. [项目概述](#项目概述)
2. [系统架构](#系统架构)
3. [核心组件](#核心组件)
4. [数据流](#数据流)
5. [API 端点](#api-端点)
6. [数据库结构](#数据库结构)
7. [前端页面](#前端页面)
8. [部署与运行](#部署与运行)
9. [修改注意事项](#修改注意事项)

---

## 项目概述

### 项目名称
**WebViewer** - 本地 HTTPS 智能生活服务系统

### 项目定位
一个运行在本地的 HTTPS Web 服务，提供三个生活管理工具的统一入口，支持通过自然语言对话进行数据录入和管理。

### 三个核心应用

| 应用 | 口号 | 路径 | 用途 |
|------|------|------|------|
| **已读不回 (By Design)** | 出远门前读了这个，就不需要单独返回 | `/bydesign/` | 出行检查清单管理 |
| **一搬不丢 (Cherry Pick)** | 一直搬家，东西也不会弄丢 | `/cherry-pick/` | 搬家物品追踪 |
| **妈妈的手 (Momhand)** | "你这孩子，这不就在电视柜上嘛！" | `/momhand/` | 物品全生命周期管理 |

### 技术栈
- **后端**: Python 3 + 原生 HTTP Server
- **前端**: HTML5 + TailwindCSS + Vanilla JavaScript
- **数据库**: SQLite (Momhand) + JSON 文件 (By Design, Cherry Pick)
- **安全**: 自签名 SSL 证书 (HTTPS 443 端口)
- **AI 集成**: OpenClaw Agent (自然语言处理)

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户浏览器                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────┐  │
│  │  首页    │  │ ByDesign │  │CherryPick│  │   Momhand      │  │
│  │ index.html│ │ index.html│ │ index.html│ │   index.html   │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS (443)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      server.py (Web 服务器)                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  路由处理                                                │    │
│  │  • GET  /api/send-message                               │    │
│  │  • POST /api/send-message                               │    │
│  │  • GET/POST/PUT/DELETE /{app}/api/*                     │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  openclaw_agent_processor.py (AI 消息处理)                │    │
│  │  • 调用 OpenClaw Agent 理解用户意图                        │    │
│  │  • 返回结构化操作指令                                     │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐    │
│  │ bydesign_    │ │ cherry_pick_ │ │ momhand_manager_     │    │
│  │ manager.py   │ │ manager.py   │ │ db.py (SQLite)       │    │
│  └──────────────┘ └──────────────┘ └──────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        数据存储                                  │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐    │
│  │ bydesign/    │ │ cherry-pick/ │ │ momhand.db           │    │
│  │ checklist.json│ │ moves.json   │ │ (SQLite)             │    │
│  │ trips.json   │ │              │ │                      │    │
│  └──────────────┘ └──────────────┘ └──────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 核心组件

### 1. server.py - Web 服务器 (40.8KB)

**职责**:
- HTTPS 服务器 (443 端口)
- 静态文件服务
- API 路由分发
- OpenClaw Agent 集成

**关键方法**:

```python
class WebViewerHandler(BaseHTTPRequestHandler):
    # HTTP 方法处理
    def do_GET(self)      # GET 请求路由
    def do_POST(self)     # POST 请求路由
    def do_PUT(self)      # PUT 请求路由 ⚠️ 曾出现重复定义问题
    def do_DELETE(self)   # DELETE 请求路由
    
    # API 处理
    def handle_send_message()        # AI 消息处理入口
    def handle_momhand_api()         # Momhand API
    def handle_cherry_pick_api()     # Cherry Pick API
    def handle_bydesign_api()        # By Design API
    def handle_cherry_pick_post()    # Cherry Pick POST
    def handle_cherry_pick_put()     # Cherry Pick PUT ⚠️ 关键修复点
    # ... 更多 handler
```

**⚠️ 重要注意事项**:
- `do_PUT` 方法只能有一个定义！2026-02-28 曾因重复定义导致 Cherry Pick 更新失败
- 所有 API 路由必须在一个 `do_PUT` 方法内完整定义
- SSL 证书路径：`selfsigned.crt` / `selfsigned.key`

---

### 2. openclaw_agent_processor.py - AI 消息处理器 (5KB)

**职责**:
- 调用 OpenClaw Agent 理解用户意图
- 解析返回的 JSON 结果
- 执行数据保存操作

**处理流程**:

```python
def process_via_openclaw_agent(message: str) -> dict:
    # 1. 构建系统提示词
    system_prompt = """理解这些信息的意图，并选择 webviewer 中合适的模块保存这些信息..."""
    
    # 2. 调用 OpenClaw Agent
    cmd = ['openclaw', 'agent', '--agent', 'main', '-m', full_prompt]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    
    # 3. 提取 JSON
    json_data = extract_json_from_output(result.stdout + result.stderr)
    
    # 4. 返回结果
    return {
        "success": True,
        "project": "bydesign/cherry_pick/momhand",
        "action": "操作类型",
        "message": "友好回复",
        "refresh": "/页面路径/",
        "data": {...}
    }
```

**返回格式**:
```json
{
  "success": true,
  "project": "momhand",
  "action": "add_item",
  "message": "✅ 已记录物品位置",
  "refresh": "/momhand/",
  "data": {"name": "大疆 action4", "location": "电视柜上面的透明箱子"},
  "processed_by": "openclaw_agent"
}
```

---

### 3. bydesign_manager.py - 出行管理器 (6.5KB)

**数据存储**: JSON 文件
- `/data/bydesign/checklist.json` - 通用检查清单
- `/data/bydesign/trips.json` - 出行记录

**核心功能**:
```python
class ByDesignManager:
    # Checklist 管理
    get_checklist()              # 获取检查清单
    add_checklist_item(text)     # 添加检查项
    update_checklist_item()      # 更新检查项
    reset_checklist()            # 重置所有项
    
    # Trip 管理
    create_trip(name, desc)      # 创建出行记录
    get_all_trips()              # 获取所有出行
    add_custom_item(trip_id)     # 添加自定义物品
    complete_trip(trip_id)       # 完成出行
    get_trip_progress(trip_id)   # 获取进度百分比
```

**数据结构**:
```json
// checklist.json
{
  "items": [
    {"id": "1", "text": "关闭所有窗户", "completed": false, "created_at": 1234567890}
  ]
}

// trips.json
{
  "trips": [
    {
      "id": "uuid",
      "name": "北京出差",
      "description": "3 天出差",
      "created_at": 1234567890,
      "status": "planning|ongoing|completed",
      "checklist_snapshot": [...],
      "custom_items": [...]
    }
  ]
}
```

---

### 4. cherry_pick_manager.py - 搬家管理器 (6.4KB)

**数据存储**: JSON 文件
- `/data/cherry-pick/moves.json` - 搬家活动和物品

**核心功能**:
```python
class CherryPickManager:
    create_move(name, desc)              # 创建搬家活动
    get_all_moves()                      # 获取所有活动
    add_item(move_id, name, before, pack, after)  # 添加物品
    get_items(move_id)                   # 获取物品列表
    update_item(item_id, updates)        # 更新物品 ⚠️ 关键方法
    delete_item(item_id)                 # 删除物品
    _sync_to_momhand(item)               # 同步到 Momhand
```

**数据结构**:
```json
// moves.json
{
  "moves": [
    {"id": "uuid", "name": "搬到新家", "created_at": 1234567890, "status": "active"}
  ],
  "items": [
    {
      "id": "uuid",
      "move_id": "uuid",
      "name": "书籍",
      "before_location": "书房书架",
      "pack_location": "纸箱 1",
      "after_location": "新家书房",
      "synced_to_momhand": true,
      "created_at": 1234567890,
      "updated_at": 1234567890
    }
  ]
}
```

**⚠️ 关键修复历史**:
- 2026-02-28: `server.py` 中 `do_PUT` 方法重复定义导致 `update_item` 无法调用
- 修复：合并所有 PUT 路由到一个 `do_PUT` 方法

---

### 5. momhand_manager_db.py - 物品管理器 (6.2KB)

**数据存储**: SQLite 数据库
- `/data/momhand.db` - SQLite 数据库

**数据库表结构**:
```sql
CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT DEFAULT '其他',
    photo TEXT,
    usage TEXT,
    purchase_date TEXT,
    price REAL,
    production_date TEXT,
    expiry_date TEXT,
    location TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_items_name ON items(name);
CREATE INDEX idx_items_type ON items(type);
CREATE INDEX idx_items_location ON items(location);
CREATE INDEX idx_items_expiry ON items(expiry_date);
```

**核心功能**:
```python
class MomhandManager:
    get_all_items()           # 获取所有物品
    add_item(item_data)       # 添加物品
    get_item_by_id(item_id)   # 根据 ID 获取
    delete_item(item_id)      # 删除物品
    search_items(keyword)     # 搜索物品
    get_statistics()          # 获取统计信息
    update_location(item_id, new_location)  # 更新位置
```

**统计信息**:
```python
{
    "total": 150,              # 总物品数
    "expiring_soon": 5,        # 7 天内过期
    "expired": 2,              # 已过期
    "by_location": {           # 按位置统计
        "电视柜": 10,
        "书房": 25,
        ...
    }
}
```

---

## 数据流

### 完整消息处理流程

```
用户在前端输入："帮我记一下，感冒药放在了药箱里"
                              │
                              ▼
┌─────────────────────────────────────────┐
│ 前端 JavaScript                          │
│ POST /api/send-message                  │
│ {message: "...", timestamp: 123}        │
└─────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────┐
│ server.py                                │
│ handle_send_message()                    │
│ 1. 接收消息                              │
│ 2. 调用 openclaw_agent_processor         │
│ 3. 保存结果到 /data/results/{id}.json   │
│ 4. 返回结果给前端                        │
└─────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────┐
│ openclaw_agent_processor.py              │
│ 1. 构建系统提示词                        │
│ 2. 执行：openclaw agent --agent main -m │
│ 3. 解析返回的 JSON                       │
│ 4. 返回结构化结果                        │
└─────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────┐
│ OpenClaw Agent                           │
│ 理解意图 → 选择项目 → 调用 API           │
│ 返回：{project: "momhand", ...}         │
└─────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────┐
│ server.py (执行保存)                     │
│ execute_save_action(result)              │
│ 调用对应的 manager.add_item()            │
└─────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────┐
│ momhand_manager_db.py                    │
│ INSERT INTO items ...                    │
│ 保存到 SQLite 数据库                      │
└─────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────┐
│ 前端显示结果                             │
│ ✅ 已记录物品位置                        │
│ 3 秒后跳转到 /momhand/                   │
└─────────────────────────────────────────┘
```

---

## API 端点

### 通用 API

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/send-message` | 发送消息到 AI 处理器 |
| GET | `/api/message-result?msg_id=xxx` | 轮询消息处理结果 |
| GET | `/api/settings` | 获取系统设置 |
| PUT | `/api/settings` | 保存系统设置 |

### By Design API

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/bydesign/api/checklist` | 获取检查清单 |
| POST | `/bydesign/api/checklist` | 添加检查项 |
| PUT | `/bydesign/api/checklist/:id` | 更新检查项 |
| DELETE | `/bydesign/api/checklist/:id` | 删除检查项 |
| GET | `/bydesign/api/trips` | 获取所有出行 |
| POST | `/bydesign/api/trips` | 创建出行 |
| GET | `/bydesign/api/trips/:id` | 获取出行详情 |
| POST | `/bydesign/api/trips/:id/items` | 添加自定义物品 |
| PUT | `/bydesign/api/trips/:id/items/:id` | 更新物品 |
| POST | `/bydesign/api/trips/:id/complete` | 完成出行 |
| GET | `/bydesign/api/trips/:id/progress` | 获取进度 |
| DELETE | `/bydesign/api/trips/:id` | 删除出行 |

### Cherry Pick API

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/cherry-pick/api/moves` | 获取所有搬家活动 |
| POST | `/cherry-pick/api/moves` | 创建搬家活动 |
| DELETE | `/cherry-pick/api/moves/:id` | 删除搬家活动 |
| GET | `/cherry-pick/api/moves/:id/items` | 获取物品列表 |
| POST | `/cherry-pick/api/moves/:id/items` | 添加物品 |
| PUT | `/cherry-pick/api/items/:id` | 更新物品 ⚠️ |
| DELETE | `/cherry-pick/api/items/:id` | 删除物品 |

### Momhand API

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/momhand/api/items` | 获取所有物品 |
| GET | `/momhand/api/search?q=xxx` | 搜索物品 |
| GET | `/momhand/api/stats` | 统计信息 |
| GET | `/momhand/api/expiring?days=7` | 即将过期物品 |
| POST | `/momhand/api/items` | 添加物品 |
| DELETE | `/momhand/api/items/:id` | 删除物品 |

---

## 数据库结构

### SQLite (Momhand)

```sql
-- 表结构
CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,           -- 物品名称
    type TEXT DEFAULT '其他',      -- 分类
    photo TEXT,                   -- 照片路径
    usage TEXT,                   -- 用途描述
    purchase_date TEXT,           -- 购买日期
    price REAL,                   -- 价格
    production_date TEXT,         -- 生产日期
    expiry_date TEXT,             -- 过期日期
    location TEXT,                -- 存放位置
    created_at TEXT,              -- 创建时间
    updated_at TEXT               -- 更新时间
);

-- 索引
CREATE INDEX idx_items_name ON items(name);
CREATE INDEX idx_items_type ON items(type);
CREATE INDEX idx_items_location ON items(location);
CREATE INDEX idx_items_expiry ON items(expiry_date);
```

### JSON 文件 (By Design, Cherry Pick)

详见各管理器的数据结构部分。

---

## 前端页面

### 1. 首页 (www/index.html)

**功能**:
- 三个应用的统一入口
- 精美卡片式设计
- 渐变色主题
- 移动端适配

**设计**:
- 深色主题背景 (gray-900 → purple-900)
- 每个工具独立配色：
  - By Design: 蓝色系
  - Cherry Pick: 紫色系
  - Momhand: 绿色系

---

### 2. By Design (www/bydesign/index.html)

**功能**:
- 通用检查清单管理
- 出行记录创建
- 进度追踪 (圆形进度条)
- 自定义物品添加

**UI 特点**:
- 蓝色渐变主题
- 悬浮对话按钮
- 实时进度显示
- 勾选交互

---

### 3. Cherry Pick (www/cherry-pick/index.html)

**功能**:
- 搬家活动管理
- 物品三位置记录 (打包前/打包后/拆封后)
- 状态标记
- 自动同步到 Momhand

**UI 特点**:
- 紫色渐变主题
- 物品卡片三种状态：
  - 待拆封 (黄色)
  - 已同步 (蓝色)
  - 已完成 (绿色)
- 三栏位置输入框

**⚠️ 关键修复**:
- 2026-02-28: 修复 PUT 请求无法更新位置的问题
- 确保 `updateItem()` 函数正确调用 `/cherry-pick/api/items/:id` PUT 接口

---

### 4. Momhand (www/momhand/index.html)

**功能**:
- 物品列表展示 (网格布局)
- 搜索功能 (实时搜索)
- 分类筛选
- 过期提醒
- 统计卡片

**UI 特点**:
- 绿色渐变主题
- 响应式网格 (1-3 列)
- 过期警告标签
- 快速搜索标签

---

## 部署与运行

### 环境要求

- Python 3.6+
- SSL 证书 (自签名或正式)
- OpenClaw (用于 AI 消息处理)
- 443 端口权限

### 启动步骤

```bash
# 1. 进入项目目录
cd /root/.openclaw/workspace/webviewer

# 2. 确保 SSL 证书存在
ls -la selfsigned.crt selfsigned.key

# 3. 启动服务
python3 server.py

# 或使用后台运行
nohup python3 server.py > /tmp/webviewer.log 2>&1 &
```

### 访问地址

```
https://<服务器 IP>/
https://<服务器 IP>/bydesign/
https://<服务器 IP>/cherry-pick/
https://<服务器 IP>/momhand/
```

### 停止服务

```bash
pkill -f "python3 server.py"
```

---

## 修改注意事项

### ⚠️ 历史问题记录

#### 1. do_PUT 方法重复定义 (2026-02-28)

**问题**: `server.py` 中有两个 `do_PUT` 方法定义，Python 只使用最后一个，导致 Cherry Pick 的 PUT 请求路由丢失。

**症状**: 在 Cherry Pick 页面填写"打包前位置"时显示更新失败。

**修复**:
```python
# ❌ 错误：两个 do_PUT 方法
def do_PUT(self):
    # 处理 cherry-pick 和 bydesign
    ...

def do_PUT(self):  # 这个会覆盖上面的！
    # 处理 prompts 和 settings
    ...

# ✅ 正确：合并到一个方法
def do_PUT(self):
    if path.startswith("/cherry-pick/api/items/"):
        self.handle_cherry_pick_put(path, data)
    elif path.startswith("/bydesign/api/"):
        self.handle_bydesign_put(path, data)
    elif path.startswith("/api/prompts/"):
        self.handle_save_prompt(path, data)
    elif path == "/api/settings":
        self.handle_save_settings(data)
    else:
        self.send_response(404)
```

**验证方法**:
```bash
# 检查 do_PUT 方法数量
grep -n "def do_PUT" /root/.openclaw/workspace/webviewer/server.py
# 应该只输出一行：282:    def do_PUT(self):
```

---

### 修改检查清单

在修改任何代码前，请确认：

- [ ] 已阅读本架构文档
- [ ] 已备份相关数据文件
- [ ] 已测试现有功能不受影响
- [ ] 已更新本文档（如有架构变更）

---

### 测试用例

#### 测试 1: Cherry Pick 位置更新

```bash
# 1. 创建搬家活动
curl -k -X POST https://localhost/cherry-pick/api/moves \
  -H "Content-Type: application/json" \
  -d '{"name":"测试搬家"}'

# 2. 添加物品
curl -k -X POST https://localhost/cherry-pick/api/moves/{moveId}/items \
  -H "Content-Type: application/json" \
  -d '{"name":"测试物品"}'

# 3. 更新打包前位置 (关键测试)
curl -k -X PUT https://localhost/cherry-pick/api/items/{itemId} \
  -H "Content-Type: application/json" \
  -d '{"before_location":"书房"}'

# 预期：返回 {"success": true}
```

#### 测试 2: Momhand 物品添加

```bash
curl -k -X POST https://localhost/momhand/api/items \
  -H "Content-Type: application/json" \
  -d '{"name":"测试物品","type":"测试","location":"测试位置"}'

# 预期：返回物品对象
```

#### 测试 3: By Design 出行创建

```bash
curl -k -X POST https://localhost/bydesign/api/trips \
  -H "Content-Type: application/json" \
  -d '{"name":"测试出行","description":"测试"}'

# 预期：返回出行对象
```

---

## 文件结构总览

```
webviewer/
├── server.py                          # ⚠️ 主服务器 (40.8KB)
├── bydesign_manager.py                # By Design 管理器 (6.5KB)
├── cherry_pick_manager.py             # Cherry Pick 管理器 (6.4KB)
├── momhand_manager_db.py              # Momhand 管理器 (SQLite, 6.2KB)
├── openclaw_agent_processor.py        # OpenClaw AI 处理器 (5KB)
├── message_engine.py                  # 消息处理引擎 (12.6KB)
├── message_processor.py               # 消息处理器 (2.5KB)
├── openclaw_bridge.py                 # OpenClaw 桥接 (3.6KB)
├── openclaw_processor.py              # OpenClaw 处理器 (3.1KB)
├── openclaw_shell_processor.py        # OpenClaw Shell 处理器 (5.2KB)
├── webviewer_handler.py               # WebViewer 处理器 (3.5KB)
│
├── www/                               # 前端页面
│   ├── index.html                     # 首页 (Friday 的小弟)
│   ├── bydesign/index.html            # By Design 页面
│   ├── cherry-pick/index.html         # Cherry Pick 页面
│   ├── momhand/index.html             # Momhand 页面
│   └── reports/                       # 报告页面
│       └── index.html
│
├── data/                              # 数据存储
│   ├── bydesign/
│   │   ├── checklist.json             # 通用检查清单
│   │   └── trips.json                 # 出行记录
│   ├── cherry-pick/
│   │   └── moves.json                 # 搬家活动和物品
│   ├── prompts/                       # AI 提示词配置
│   ├── results/                       # 消息处理结果
│   ├── momhand.db                     # SQLite 数据库 (28KB)
│   └── settings.json                  # 系统设置
│
├── skills/
│   └── webviewer/
│       └── SKILL.md                   # WebViewer 技能文档
│
├── docs/                              # 文档
│   ├── OPENCLAW_AGENT_SETUP.md
│   ├── OPENCLAW_SHELL_IMPLEMENTATION.md
│   ├── OPENCLAW_SHELL_COMPLETE.md
│   ├── OPENCLAW_TUI_INTEGRATION_PLAN.md
│   ├── UPDATE_SUMMARY.md
│   └── IMPLEMENTATION_SUMMARY.md
│
├── selfsigned.crt                     # SSL 证书
├── selfsigned.key                     # SSL 私钥
│
├── README.md                          # 项目说明
├── PROJECTS.md                        # 项目总结
├── SYSTEM_ARCHITECTURE.md             # 系统架构 (旧)
├── OPENCLAW_INTEGRATION.md            # OpenClaw 集成 (旧)
├── CHAT_SYSTEM.md                     # 聊天系统
├── SHELL_OPENCLAW_INTEGRATION.md      # Shell 集成
├── GENERATE_CERT.md                   # 证书生成指南
└── WEBVIEWER_COMPLETE_ARCHITECTURE.md # 📋 本文档
```

---

## 总结

WebViewer 是一个集成了三个生活管理工具的本地 HTTPS Web 服务，通过 OpenClaw Agent 实现自然语言交互。

**核心价值**:
1. **统一入口** - 一个首页访问所有工具
2. **智能交互** - 对话式数据录入
3. **数据互通** - Cherry Pick 自动同步到 Momhand
4. **本地部署** - 数据完全私有
5. **移动友好** - 所有页面适配手机

**关键维护点**:
- ⚠️ `server.py` 的 `do_PUT` 方法只能有一个定义
- ⚠️ 修改前必须测试现有 API 不受影响
- ⚠️ 数据文件修改前务必备份

---

*文档结束*
