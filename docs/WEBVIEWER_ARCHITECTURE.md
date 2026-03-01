# WebViewer 项目架构文档

## 📋 项目概述

WebViewer 是一个基于 Python 的 HTTPS Web 服务，提供四个生活管理模块，运行在 443 端口。

**版本**: v1.5.1  
**运行环境**: Python 3.11+  
**服务地址**: https://43.153.153.62

---

## 🏗️ 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                    用户浏览器                            │
│                  (HTTPS 访问 443 端口)                    │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│                    server.py                             │
│            (HTTPS Web 服务器 - ThreadingMixIn)            │
│  - 静态文件服务                                          │
│  - API 路由分发                                           │
│  - 异步消息处理                                          │
└───────────────────┬─────────────────────────────────────┘
                    │
        ┌───────────┼───────────┬────────────┬──────────┐
        │           │           │            │          │
        ▼           ▼           ▼            ▼          ▼
   ┌────────┐  ┌──────────┐ ┌────────┐ ┌─────────┐ ┌──────┐
   │ByDesign│  │CherryPick│ │Momhand │ │SiriDream│ │ 其他 │
   │Manager │  │ Manager  │ │Manager │ │ Manager │ │ API  │
   └────┬───┘  └────┬─────┘ └───┬────┘ └────┬────┘ └──┬───┘
        │           │           │          │          │
        ▼           ▼           ▼          ▼          ▼
   ┌─────────────────────────────────────────────────────┐
   │                  data/ (数据存储)                    │
   │  - JSON 文件 (bydesign/, cherry-pick/)               │
   │  - SQLite 数据库 (momhand.db)                        │
   │  - 消息结果 (results/)                               │
   └─────────────────────────────────────────────────────┘
```

---

## 📂 目录结构

```
/root/.openclaw/workspace/
├── server.py                      # 主服务器（HTTPS, 443 端口）
├── watchdog.sh                    # 看门狗监控脚本
├── siri_dream_manager.py          # Siri 的尉来数据管理器
├── momhand_manager_db.py          # Momhand SQLite 管理器
├── bydesign_manager.py            # By Design 管理器
├── cherry_pick_manager.py         # Cherry Pick 管理器
│
├── www/                           # Web 前端文件
│   ├── index.html                 # 首页（Dummy 的小弟）
│   ├── bydesign/
│   │   └── index.html             # By Design 页面
│   ├── cherry-pick/
│   │   └── index.html             # Cherry Pick 页面
│   ├── momhand/
│   │   └── index.html             # Momhand 页面
│   ├── siri-dream/
│   │   └── index.html             # Siri 的尉来页面
│   └── js/
│       └── agent-chat.js          # 共享聊天组件
│
├── data/                          # 数据存储（根目录）
│   ├── bydesign/                  # By Design 数据
│   │   ├── checklist.json
│   │   ├── trips.json
│   │   └── templates.json
│   ├── cherry-pick/               # Cherry Pick 数据
│   │   └── moves.json
│   ├── siri-dream/                # Siri 的尉来数据
│   │   ├── messages.json
│   │   └── settings.json
│   ├── results/                   # 消息处理结果
│   └── settings.json              # 全局设置
│
├── webviewer/data/                # WebViewer 数据（旧路径）
│   └── momhand.db                 # Momhand SQLite 数据库
│
└── momhand/data/                  # Momhand 旧数据
    └── items.json                 # 物品数据（JSON 格式）
```

---

## 🔌 四个核心模块

### 1. By Design (已读不回) - 出行管理

**路径**: `/bydesign/`  
**颜色**: 蓝色渐变 (#3b82f6 → #06b6d4)  
**数据**: `data/bydesign/*.json`

**功能**:
- 通用检查清单（每次出行都要做的事）
- 单次出行记录
- 进度追踪
- 模板系统

**API**:
```
GET  /bydesign/api/checklist      # 获取检查清单
POST /bydesign/api/checklist      # 添加检查项
PUT  /bydesign/api/checklist/:id  # 更新检查项
DELETE /bydesign/api/checklist/:id # 删除检查项

GET  /bydesign/api/trips          # 获取所有出行
POST /bydesign/api/trips          # 创建出行
GET  /bydesign/api/trips/:id      # 获取出行详情
POST /bydesign/api/trips/:id/items # 添加自定义物品
POST /bydesign/api/trips/:id/complete # 完成出行
```

---

### 2. Cherry Pick (一搬不丢) - 搬家管理

**路径**: `/cherry-pick/`  
**颜色**: 紫色渐变 (#8b5cf6 → #ec4899)  
**数据**: `data/cherry-pick/moves.json`

**功能**:
- 创建搬家活动
- 记录物品位置（打包前/打包后/拆封后）
- 已放置物品自动同步到 Momhand
- 状态统计

**API**:
```
GET  /cherry-pick/api/moves           # 获取所有搬家活动
POST /cherry-pick/api/moves           # 创建搬家活动
GET  /cherry-pick/api/moves/:id/items # 获取物品列表
POST /cherry-pick/api/moves/:id/items # 添加物品
PUT  /cherry-pick/api/items/:id       # 更新物品
DELETE /cherry-pick/api/moves/:id     # 删除搬家活动
DELETE /cherry-pick/api/items/:id     # 删除物品
```

---

### 3. Momhand (妈妈的手) - 物品管理

**路径**: `/momhand/`  
**颜色**: 绿色渐变 (#10b981 → #3b82f6)  
**数据**: `webviewer/data/momhand.db` (SQLite)

**功能**:
- 物品登记（名称、类型、位置、用途）
- 快速搜索
- 分类统计
- 过期提醒

**API**:
```
GET  /momhand/api/items          # 获取所有物品
GET  /momhand/api/search?q=xxx   # 搜索物品
GET  /momhand/api/stats          # 统计信息
GET  /momhand/api/expiring?days=7 # 即将过期物品
POST /momhand/api/items          # 添加物品
PUT  /momhand/api/items/:id      # 更新物品
DELETE /momhand/api/items/:id    # 删除物品
```

**⚠️ 重要**: Momhand 使用 SQLite 数据库，路径为 `webviewer/data/momhand.db`

---

### 4. Siri 的尉来 (SiriFuture) - 外部 API 接入

**路径**: `/siri-dream/`  
**颜色**: 蓝紫渐变 (#3b82f6 → #9333ea)  
**数据**: `data/siri-dream/messages.json`

**功能**:
- 接收外部 HTTP POST 消息
- 转发给 OpenClaw Agent (Dummy) 处理
- 异步处理，支持状态查询
- 历史消息记录

**API**:
```
# 发送消息（立即返回）
POST /siri-dream/api/message
Body: {"text": "消息内容", "metadata": {...}}
Response: {success: true, message_id: "uuid", status: "processing"}

# 查询结果（使用相同的 API）
POST /siri-dream/api/message
Body: {"message_id": "uuid"}
Response: {success: true, status: "completed", result: {...}}

# 或使用 GET 查询
GET /siri-dream/api/message/:id
Response: {success: true, status: "completed", result: {...}}

# 获取历史消息
GET /siri-dream/api/messages?limit=50
Response: {success: true, data: [...]}

# 获取统计
GET /siri-dream/api/stats
Response: {success: true, data: {total, pending, completed, failed}}
```

**状态流转**:
```
pending → processing → completed
                    ↘ failed
```

**超时**: 90 秒

---

## 🔧 核心技术实现

### server.py - 主服务器

**特点**:
- 基于 `http.server.HTTPServer` + `ThreadingMixIn`
- 支持并发请求（每个请求一个线程）
- HTTPS (自签名证书)
- 请求超时：30 秒
- 后台任务超时：90 秒

**关键配置**:
```python
PORT = 443
REQUEST_TIMEOUT = 30
BACKGROUND_TASK_TIMEOUT = 90

class TimeoutHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True
    request_queue_size = 20
    timeout = REQUEST_TIMEOUT
```

**路由分发**:
```python
def do_GET(self):
    if path.startswith("/momhand/api/"):
        self.handle_momhand_api(path, query)
    elif path.startswith("/cherry-pick/api/"):
        self.handle_cherry_pick_api(path, query)
    elif path.startswith("/bydesign/api/"):
        self.handle_bydesign_api(path, query)
    elif path.startswith("/siri-dream/api/"):
        self.handle_siri_dream_api(path, query)
    else:
        self.serve_static_file(path, WEB_ROOT)
```

---

### 异步消息处理 (Siri 的尉来)

**流程**:
```
1. POST /siri-dream/api/message
   ↓
2. 保存消息到数据库 (status: pending)
   ↓
3. 立即返回 message_id (status: processing)
   ↓
4. 后台线程处理:
   - 调用 OpenClaw Agent
   - 超时 90 秒
   - 更新状态 (completed/failed)
   ↓
5. 前端轮询 GET /api/message/:id
   ↓
6. 显示结果
```

**代码示例**:
```python
def handle_siri_dream_message(self, data):
    # 异步处理
    message = manager['add_message'](text, 'api', metadata)
    thread = threading.Thread(
        target=self._process_siri_dream_message_sync,
        args=(message['id'], text),
        daemon=True
    )
    thread.start()
    
    # 立即返回
    return {"success": True, "message_id": message['id'], "status": "processing"}
```

---

## 📊 数据管理

### JSON 文件存储

**适用**: By Design, Cherry Pick, Siri 的尉来

**优点**:
- 简单直观
- 易于调试
- 无需数据库

**缺点**:
- 并发写入可能冲突
- 大数据性能差

### SQLite 存储

**适用**: Momhand

**优点**:
- 支持复杂查询
- 并发安全
- 支持索引

**缺点**:
- 需要数据库管理
- 路径依赖

**⚠️ 重要路径**:
```python
# Momhand 数据库路径
DB_FILE = Path("/root/.openclaw/workspace/webviewer/data/momhand.db")
```

---

## 🔒 安全配置

### SSL 证书

**路径**:
- 证书：`/root/.openclaw/workspace/selfsigned.crt`
- 私钥：`/root/.openclaw/workspace/selfsigned.key`

**配置**:
```python
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)
httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
```

**SAN 配置**:
```
Subject: CN = 43.153.153.62
SAN: IP Address:43.153.153.62
```

### 环境变量（可选）

```bash
# Feishu API（如果使用）
export FEISHU_APP_ID="your_app_id"
export FEISHU_APP_SECRET="your_app_secret"
```

---

## 🐕 监控与运维

### watchdog.sh - 看门狗脚本

**功能**:
- 每 60 秒检查服务状态
- 检测到卡死自动重启
- 限制 5 分钟内最多重启 3 次

**检查方式**:
```bash
# 1. 检查进程是否存在
pgrep -f "python3 server.py"

# 2. 检查服务是否响应
curl -sk --max-time 5 https://localhost/
```

**日志**:
- 主服务：`/tmp/webviewer.log`
- 看门狗：`/tmp/webviewer-watchdog.log`

---

## 📝 修改规范

### ⚠️ 重要规则

1. **修改前必读**:
   - 阅读本文档
   - 检查相关模块代码
   - 确保不破坏现有功能

2. **数据路径**:
   - 使用 `data/` 根目录（新模块）
   - Momhand 使用 `webviewer/data/momhand.db`
   - 不要混用路径

3. **API 设计**:
   - RESTful 风格
   - 统一返回格式：`{success: bool, data/error: ...}`
   - 添加 CORS 头：`Access-Control-Allow-Origin: *`

4. **前端修改**:
   - 返回首页链接使用绝对 URL：`https://43.153.153.62/`
   - 保持统一的 UI 风格
   - 响应式设计（移动端适配）

5. **测试**:
   - 修改后重启服务
   - 测试所有 API 端点
   - 检查前端页面是否正常

---

## 🚀 部署流程

### 启动服务

```bash
cd /root/.openclaw/workspace
nohup python3 server.py > /tmp/webviewer.log 2>&1 &
```

### 验证

```bash
# 检查进程
ps aux | grep "python3 server.py"

# 检查端口
netstat -tlnp | grep 443

# 测试访问
curl -sk https://localhost/
```

### 停止服务

```bash
pkill -9 -f "python3 server.py"
```

---

## 📚 相关文档

- `SSL_CERT_GUIDE.md` - SSL 证书配置指南
- `FIX_REPORT.md` - v1.2.8 修复报告
- `SYSTEM_ARCHITECTURE.md` - 详细系统架构
- `www/js/agent-chat.js` - 共享聊天组件文档

---

**最后更新**: 2026-03-02  
**版本**: v1.5.1  
**维护者**: WebViewer Team
