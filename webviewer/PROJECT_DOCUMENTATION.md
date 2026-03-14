# WebViewer 项目说明书

> **版本**: v2.0  
> **更新日期**: 2026-03-14  
> **项目状态**: 生产就绪  
> **维护团队**: OpenClaw Workspace

---

## 目录

1. [项目概述](#1-项目概述)
2. [核心功能](#2-核心功能)
3. [技术架构](#3-技术架构)
4. [系统模块](#4-系统模块)
5. [API 接口](#5-api-接口)
6. [数据设计](#6-数据设计)
7. [安全特性](#7-安全特性)
8. [部署指南](#8-部署指南)
9. [使用说明](#9-使用说明)
10. [运维管理](#10-运维管理)
11. [项目亮点](#11-项目亮点)
12. [附录](#12-附录)

---

## 1. 项目概述

### 1.1 项目简介

WebViewer 是一个**企业级 Web 访问审批与审计系统**，专为需要严格控制访问权限的内部 Web 应用设计。系统提供完整的访客审批流程、管理员认证、访问审计日志和实时飞书通知功能。

### 1.2 应用场景

- 🔐 **内部工具访问控制** - 保护公司内部 Web 工具不被未授权访问
- 📊 **敏感数据展示** - 报表、仪表板等敏感信息的访问审批
- 👥 **访客临时访问** - 为外部访客提供临时访问权限
- 📝 **审计合规** - 记录所有访问行为，满足审计要求

### 1.3 核心价值

| 价值维度 | 说明 |
|----------|------|
| **安全可控** | 所有访客访问需经管理员审批，白名单 IP 自动放行 |
| **实时通知** | 飞书即时推送审批请求，管理员随时随地审批 |
| **完整审计** | 记录 IP、设备、时间、路径等完整访问信息 |
| **便捷管理** | Web 管理后台，可视化查看审批和日志 |
| **零依赖** | 基于 Python 标准库，无需额外安装依赖 |

### 1.4 版本历史

| 版本 | 日期 | 主要更新 |
|------|------|----------|
| v1.0 | 2026-03-07 | 初始版本，基础审批功能 |
| v1.5 | 2026-03-08 | 增加飞书通知、审计日志 |
| v2.0 | 2026-03-14 | 管理员登录、增强审计、退出登录 |

---

## 2. 核心功能

### 2.1 双模式访问控制

#### 管理员模式
- 🔐 **账号密码登录** - SHA256 加密存储密码
- 🎫 **会话管理** - 12 小时有效会话
- 📊 **完整权限** - 访问所有功能和审计后台

#### 访客模式
- 🚀 **访客申请** - 一键提交访问申请
- ⏳ **等待审批** - 实时轮询审批状态
- 🕐 **临时会话** - 审批通过后 24 小时有效

### 2.2 访问审批流程

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   访问者     │         │   系统      │         │   管理员     │
└──────┬──────┘         └──────┬──────┘         └──────┬──────┘
       │                       │                        │
       │  1. 访问网站          │                        │
       │ ─────────────────────>│                        │
       │                       │                        │
       │  2. 创建待审批记录     │                        │
       │  显示等待页面         │                        │
       │ <─────────────────────│                        │
       │                       │                        │
       │                       │  3. 飞书通知           │
       │                       │ ──────────────────────>│
       │                       │                        │
       │                       │                        │ 4. 查看信息
       │                       │                        │    点击审批
       │                       │                        │
       │                       │  5. 审批结果回调       │
       │                       │ <──────────────────────│
       │                       │                        │
       │  6. 轮询获取状态      │                        │
       │ <─────────────────────│                        │
       │                       │                        │
       │  7. 审批通过          │                        │
       │  自动跳转工具箱       │                        │
       │                       │                        │
       │  (24 小时内无需再审批) │                        │
```

### 2.3 审计日志系统

#### 记录内容
- 🌐 **IP 地址** - 支持 X-Forwarded-For 代理转发
- 🖥️ **设备信息** - 浏览器、操作系统、设备类型
- 📍 **地理位置** - 基于 IP 的简化地理位置
- 🔗 **访问路径** - 完整 URL 路径
- ⏰ **时间戳** - 精确到秒的访问时间
- 📱 **语言设置** - 浏览器首选语言
- 📊 **屏幕分辨率** - 设备屏幕信息
- 🕐 **时区信息** - 客户端时区

#### 日志查询
- 🔍 **多维度筛选** - IP、浏览器、平台、设备类型、事件类型、状态
- 📈 **统计卡片** - 总访问数、独立 IP、今日访问、浏览器分布、平台分布
- 📄 **分页加载** - 每次加载 50 条，支持无限滚动
- 💾 **导出删除** - 支持日志导出和清空

### 2.4 飞书集成

#### 通知类型
| 通知类型 | 触发条件 | 内容 |
|----------|----------|------|
| 访问告警 | 未授权访问被阻止 | IP、设备、位置、路径、时间 |
| 审批请求 | 访客提交访问申请 | 访问者信息 + 审批链接 |

#### 消息格式
```
🔐 WebViewer 访问审批请求

🌐 访问来源：192.168.1.100
🖥️ 设备：Mozilla/5.0 (Windows NT 10.0; Win64; x64)...
📍 位置：🇨🇳 中国
⏰ 时间：2026-03-14 10:30:00

审批链接:
✅ 同意：https://43.153.153.62/approve/{approval_id}
❌ 拒绝：https://43.153.153.62/reject/{approval_id}

验证码：ABC123
```

---

## 3. 技术架构

### 3.1 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                      客户端层                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │  浏览器   │  │  飞书 App │  │  移动端   │              │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
└───────┼─────────────┼─────────────┼─────────────────────┘
        │             │             │
        │ HTTPS       │ 飞书 API    │
        │ (443 端口)   │             │
        ▼             ▼             ▼
┌─────────────────────────────────────────────────────────┐
│                   WebViewer 服务器                       │
│  ┌──────────────────────────────────────────────────┐   │
│  │              WebViewerHandler                     │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  │   │
│  │  │ 路由处理   │  │ 会话管理   │  │ 权限检查   │  │   │
│  │  └────────────┘  └────────────┘  └────────────┘  │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │               DataManager                         │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  │   │
│  │  │ 会话存储   │  │ 审批管理   │  │ 日志记录   │  │   │
│  │  └────────────┘  └────────────┘  └────────────┘  │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │             FeishuNotifier                        │   │
│  │  ┌────────────┐  ┌────────────┐                  │   │
│  │  │ Token 管理  │  │ 消息发送   │                  │   │
│  │  └────────────┘  └────────────┘                  │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│                     数据存储层                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │JSON 文件   │  │ SSL 证书  │  │ 配置文件  │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└─────────────────────────────────────────────────────────┘
```

### 3.2 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **后端语言** | Python 3.11+ | 标准库为主，零依赖 |
| **Web 框架** | http.server | Python 内置 HTTP 服务器 |
| **SSL/TLS** | ssl 模块 | OpenSSL 绑定 |
| **数据存储** | JSON 文件 | 轻量级，易维护 |
| **前端** | HTML5 + CSS3 + JS | 响应式设计，无框架 |
| **通知集成** | 飞书开放 API | 企业自建应用 |

### 3.3 目录结构

```
webviewer/
├── 🔧 核心代码
│   ├── server_enhanced.py        # 主服务器（88KB, 2100+ 行）
│   ├── server_with_approval.py   # 审批版本（历史）
│   └── server_with_auth.py       # 认证版本（历史）
│
├── 🔌 集成模块
│   ├── feishu_callback.py        # 飞书回调处理器
│   └── auto_notify.py            # 自动通知模块
│
├── 🔐 安全工具
│   ├── generate_ssl_cert.sh      # SSL 证书生成
│   ├── generate_password.py      # 密码哈希生成
│   ├── get_open_id.py            # 飞书 OpenID 获取
│   └── get_user_id.py            # 飞书 UserID 获取
│
├── 🚀 运维脚本
│   ├── start.sh                  # 快速启动
│   ├── start-with-approval.sh    # 审批模式启动
│   ├── stop-with-approval.sh     # 停止服务
│   ├── diagnose.sh               # 诊断工具
│   └── monitor.sh                # 监控脚本
│
├── ⚙️ 配置文件
│   ├── config.json               # 主配置（白名单、管理员）
│   └── .env                      # 环境变量
│
├── 📊 数据目录
│   └── data/
│       ├── server.crt            # SSL 证书
│       ├── server.key            # SSL 私钥
│       ├── access_log.jsonl      # 访问日志
│       ├── audit_log.jsonl       # 审计日志
│       ├── pending_approvals.json # 待审批记录
│       ├── approved_sessions.json # 已批准会话
│       └── admin_sessions.json   # 管理员会话
│
├── 📖 文档
│   ├── PROJECT_DOCUMENTATION.md  # 项目说明书（本文档）
│   ├── DEPLOYMENT.md             # 部署指南
│   ├── USAGE_GUIDE.md            # 使用指南
│   ├── FUNCTIONS.md              # 功能说明
│   ├── README_APPROVAL.md        # 审批系统说明
│   ├── MONITOR_README.md         # 监控说明
│   └── MODIFICATIONS_20260314.md # 修改记录
│
└── 🌐 静态资源
    └── www/ -> ../../www/        # 工具箱主页（符号链接）
```

---

## 4. 系统模块

### 4.1 配置模块 (Config)

```python
class Config:
    # 服务器配置
    HOST = '0.0.0.0'
    HTTPS_PORT = 443
    
    # 会话配置
    SESSION_TIMEOUT_HOURS = 24      # 访客会话有效期
    ADMIN_SESSION_TIMEOUT_HOURS = 12 # 管理员会话有效期
    PENDING_TIMEOUT_MINUTES = 30    # 待审批超时
    
    # 数据目录
    DATA_DIR = Path('/root/.openclaw/workspace/webviewer/data')
    WWW_DIR = Path('/root/.openclaw/workspace/www')
    
    # 白名单 IP
    WHITELIST_IPS = ['127.0.0.1', '::1']
```

**配置项说明**：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `HOST` | 0.0.0.0 | 监听地址，0.0.0.0 表示所有网卡 |
| `HTTPS_PORT` | 443 | HTTPS 监听端口 |
| `SESSION_TIMEOUT_HOURS` | 24 | 访客会话有效期（小时） |
| `ADMIN_SESSION_TIMEOUT_HOURS` | 12 | 管理员会话有效期（小时） |
| `PENDING_TIMEOUT_MINUTES` | 30 | 待审批记录保留时间（分钟） |

### 4.2 数据管理模块 (DataManager)

**核心功能**：
- 📝 访问日志记录
- 🎫 会话创建与验证
- ⏳ 审批流程管理
- 🧹 过期数据清理
- 📊 统计分析

**主要方法**：

| 方法 | 功能 | 参数 | 返回值 |
|------|------|------|--------|
| `log_access()` | 记录访问日志 | visitor_info | None |
| `log_audit()` | 记录审计日志 | audit_info | audit_entry |
| `create_pending_approval()` | 创建待审批 | visitor_info | approval_record |
| `approve_access()` | 审批通过 | approval_id | (success, session_id) |
| `reject_access()` | 审批拒绝 | approval_id | (success, message) |
| `check_session()` | 验证会话 | session_id | bool |
| `verify_admin_login()` | 验证管理员 | username, password | bool |
| `create_admin_session()` | 创建管理员会话 | username, ip | session_id |
| `get_audit_logs()` | 获取审计日志 | limit, offset, filters | logs[] |
| `get_stats()` | 获取统计信息 | - | stats_dict |

### 4.3 飞书通知模块 (FeishuNotifier)

**核心功能**：
- 🔑 Tenant Access Token 管理
- 📨 审批请求通知
- 🚨 访问告警通知
- ✅ 发送状态追踪

**通知流程**：
```
1. 构建消息内容
   ↓
2. 获取 Tenant Access Token
   ↓
3. 调用飞书 API 发送消息
   ↓
4. 记录发送状态
   ↓
5. 异常重试（最多 3 次）
```

### 4.4 HTTP 请求处理模块 (WebViewerHandler)

**路由表**：

| 路径 | 方法 | 功能 | 认证要求 |
|------|------|------|----------|
| `/` | GET | 主页（登录选择） | 无 |
| `/login` | GET | 登录页面 | 无 |
| `/logout` | GET | 退出登录 | - |
| `/www/*` | GET | 工具箱主页 | 会话或审批 |
| `/audit` | GET | 审计日志页面 | 管理员 |
| `/pending` | GET | 待审批列表 | 管理员 |
| `/approve/{id}` | GET | 审批通过 | 管理员 |
| `/reject/{id}` | GET | 审批拒绝 | 管理员 |
| `/check-status/{id}` | GET | 审批状态检查 | 无 |
| `/api/login` | POST | 管理员登录 | 无 |
| `/api/audit-logs` | GET | 审计日志 API | 管理员 |
| `/api/stats` | GET | 统计信息 API | 管理员 |
| `/api/audit-delete` | POST | 删除日志 | 管理员 |

---

## 5. API 接口

### 5.1 认证 API

#### POST /api/login

管理员登录接口

**请求**：
```json
{
  "username": "yangjiukui",
  "password": "your_password"
}
```

**响应**（成功）：
```json
{
  "success": true,
  "redirect": "/www/"
}
```

**响应**（失败）：
```json
{
  "success": false,
  "error": "用户名或密码错误"
}
```

**Cookie**：
```
Set-Cookie: wv_admin_session={session_id}; Path=/; Max-Age=43200; HttpOnly
```

### 5.2 审计 API

#### GET /api/audit-logs

获取审计日志列表

**参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| limit | int | 否 | 每页数量，默认 100 |
| offset | int | 否 | 偏移量，默认 0 |
| ip | string | 否 | IP 过滤 |
| path | string | 否 | 路径过滤 |
| browser | string | 否 | 浏览器过滤 |
| platform | string | 否 | 平台过滤 |
| device | string | 否 | 设备类型过滤 |
| event | string | 否 | 事件类型过滤 |
| status | string | 否 | 状态过滤 |

**响应**：
```json
{
  "success": true,
  "logs": [...],
  "stats": {
    "total_visits": 1234,
    "unique_ips": 56,
    "today_visits": 89,
    "unique_browsers": 12,
    "unique_platforms": 8,
    "pending_approvals": 3
  },
  "total": 100
}
```

#### POST /api/audit-delete

删除所有审计日志

**响应**：
```json
{
  "success": true
}
```

### 5.3 审批状态 API

#### GET /check-status/{approval_id}

访客轮询审批状态

**路径参数**：
- `approval_id` - 审批记录 ID

**响应**（等待中）：
```json
{
  "approved": false,
  "status": "pending"
}
```

**响应**（已通过）：
```json
{
  "approved": true,
  "session_id": "uuid...",
  "status": "approved"
}
```

**响应**（已拒绝）：
```json
{
  "approved": false,
  "rejected": true,
  "status": "rejected"
}
```

---

## 6. 数据设计

### 6.1 数据文件

| 文件 | 格式 | 说明 | 大小示例 |
|------|------|------|----------|
| `access_log.jsonl` | JSONL | 访问日志 | 37KB |
| `audit_log.jsonl` | JSONL | 审计日志 | 577KB |
| `pending_approvals.json` | JSON | 待审批记录 | 5KB |
| `approved_sessions.json` | JSON | 已批准会话 | 2KB |
| `admin_sessions.json` | JSON | 管理员会话 | <1KB |

### 6.2 数据结构

#### 访问日志记录
```json
{
  "timestamp": 1773516000,
  "datetime": "2026-03-14T10:30:00",
  "ip": "221.219.243.106",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
  "path": "/www/index.html",
  "method": "GET",
  "referer": "",
  "language": "zh-CN",
  "platform": "Windows 10/11",
  "browser": "Chrome",
  "device_type": "Desktop",
  "screen_resolution": "1920x1080",
  "timezone": "UTC+8",
  "location": "🇨🇳 中国",
  "event_type": "page_access",
  "status": "allowed",
  "session_id": "uuid..."
}
```

#### 待审批记录
```json
{
  "approval_id": "550e8400-e29b-41d4-a716-446655440000",
  "verification_code": "ABC123",
  "visitor_info": {
    "ip": "221.219.243.106",
    "user_agent": "Mozilla/5.0...",
    "path": "/www/",
    "location": "🇨🇳 中国"
  },
  "timestamp": 1773516000,
  "status": "pending"
}
```

#### 会话记录
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440001",
  "ip": "221.219.243.106",
  "approved_at": 1773516000,
  "expires_at": 1773602400,
  "approval_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 6.3 数据清理策略

| 数据类型 | 清理条件 | 清理时间 |
|----------|----------|----------|
| 访客会话 | expires_at < now | 启动时 + 每次访问 |
| 管理员会话 | expires_at < now | 启动时 + 每次访问 |
| 待审批记录 | timestamp < now - 30min | 启动时 + 每次访问 |

---

## 7. 安全特性

### 7.1 认证安全

#### 密码存储
- 🔐 **SHA256 哈希** - 密码永不明文存储
- 🎲 **盐值保护** - 防止彩虹表攻击

#### 会话管理
- 🎫 **UUID 会话 ID** - 不可预测的会话标识
- ⏰ **自动过期** - 管理员 12 小时，访客 24 小时
- 🔒 **HttpOnly Cookie** - 防止 XSS 窃取

### 7.2 通信安全

#### HTTPS 加密
- 🔒 **SSL/TLS 1.2+** - 全链路加密
- 📜 **自签名证书** - 开发环境便捷部署
- ⚠️ **生产建议** - 使用正式 CA 证书

#### 证书管理
```bash
# 生成自签名证书（有效期 365 天）
./generate_ssl_cert.sh

# 证书信息
openssl x509 -in data/server.crt -text -noout
```

### 7.3 访问控制

#### IP 白名单
```json
{
  "whitelist_ips": [
    "43.153.153.62",      // 服务器公网 IP
    "221.219.243.106",    // 管理员家庭 IP
    "223.104.41.9",       // 公司网络 IP
    "127.0.0.1",          // 本地回环
    "::1"                 // IPv6 本地
  ]
}
```

#### 权限分级
| 角色 | 权限 |
|------|------|
| **未认证** | 仅可访问登录页和等待页 |
| **访客** | 访问工具箱（需审批） |
| **管理员** | 全部权限（审计、审批、配置） |

### 7.4 审计追踪

#### 审计事件
| 事件类型 | 说明 | 记录内容 |
|----------|------|----------|
| `page_access` | 页面访问 | IP、路径、设备、状态 |
| `login_attempt` | 登录尝试 | IP、用户名、结果 |
| `approval` | 审批操作 | 审批 ID、结果 |

#### 日志保护
- 📝 **只追加写入** - 防止篡改
- 💾 **定期备份** - 避免数据丢失
- 🗑️ **手动删除** - 防止误操作

---

## 8. 部署指南

### 8.1 环境要求

| 项目 | 要求 | 说明 |
|------|------|------|
| **操作系统** | Linux/macOS/Windows | 推荐 Linux |
| **Python 版本** | 3.11+ | 需要 pathlib、ssl 模块 |
| **内存** | ≥ 50MB | 轻量级运行 |
| **磁盘** | ≥ 100MB | 含日志存储 |
| **网络** | 443 端口 | HTTPS 服务 |

### 8.2 快速部署

#### 步骤 1：生成 SSL 证书
```bash
cd /root/.openclaw/workspace/webviewer
./generate_ssl_cert.sh
```

#### 步骤 2：配置飞书应用
```bash
# 获取飞书凭证
export FEISHU_APP_ID="cli_xxxxxxxxxxxxx"
export FEISHU_APP_SECRET="xxxxxxxxxxxxxxxxxxxx"
export FEISHU_USER_OPEN_ID="ou_xxxxxxxxxxxxx"
```

#### 步骤 3：配置管理员账号
```bash
# 生成密码哈希
python3 generate_password.py

# 编辑 config.json
{
  "admin": {
    "username": "your_username",
    "password_hash": "生成的哈希值"
  },
  "whitelist_ips": ["你的 IP"]
}
```

#### 步骤 4：启动服务
```bash
# 方式 1：前台运行
python3 server_enhanced.py

# 方式 2：后台运行
nohup python3 server_enhanced.py > server.log 2>&1 &

# 方式 3：使用启动脚本
./start.sh
```

#### 步骤 5：验证部署
```bash
# 检查服务状态
curl -k -s -o /dev/null -w "%{http_code}" https://127.0.0.1:443/

# 预期输出：200
```

### 8.3 Systemd 服务部署

#### 创建服务文件
```bash
sudo tee /etc/systemd/system/webviewer.service << 'EOF'
[Unit]
Description=WebViewer Access Control System
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/.openclaw/workspace/webviewer
Environment="FEISHU_APP_ID=your_app_id"
Environment="FEISHU_APP_SECRET=your_secret"
Environment="FEISHU_USER_OPEN_ID=your_open_id"
ExecStart=/usr/bin/python3 /root/.openclaw/workspace/webviewer/server_enhanced.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
```

#### 启用服务
```bash
sudo systemctl daemon-reload
sudo systemctl enable webviewer
sudo systemctl start webviewer
sudo systemctl status webviewer
```

### 8.4 防火墙配置

#### firewalld（CentOS/RHEL）
```bash
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload
```

#### ufw（Ubuntu/Debian）
```bash
sudo ufw allow 443/tcp
sudo ufw enable
```

#### iptables（通用）
```bash
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables-save > /etc/iptables/rules.v4
```

---

## 9. 使用说明

### 9.1 管理员使用指南

#### 登录流程
1. 访问 `https://你的服务器 IP/`
2. 点击 **🔐 管理员登录** 悬浮球
3. 输入用户名和密码
4. 登录成功后自动跳转到工具箱主页

#### 管理功能
| 功能 | 入口 | 说明 |
|------|------|------|
| **审计日志** | 底部 📊 或 `/audit` | 查看所有访问记录 |
| **待审批** | 底部 ⏳ 或 `/pending` | 管理访客审批 |
| **退出登录** | 底部 🚪 或 `/logout` | 安全退出 |

#### 审批操作
1. 收到飞书通知 或 访问 `/pending`
2. 查看访问者信息（IP、设备、时间）
3. 点击 **✅ 同意** 或 **❌ 拒绝**
4. 访问者实时收到审批结果

### 9.2 访客使用指南

#### 申请访问
1. 访问 `https://你的服务器 IP/`
2. 点击 **🚀 访客申请** 悬浮球
3. 自动进入等待审批页面

#### 等待审批
- ⏳ 页面每 5 秒自动检查审批状态
- 📱 可关闭页面，稍后重新访问
- ⏰ 最长等待 6 分钟（超时需重新申请）

#### 审批通过
- ✅ 自动跳转到工具箱主页
- 🕐 24 小时内无需再次审批
- 🚪 离开后重新访问自动进入

### 9.3 飞书配置指南

#### 创建应用
1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 点击 **企业自建应用** → **创建应用**
3. 填写应用名称和图标

#### 获取凭证
1. 进入应用管理页面
2. 点击 **凭证与基础信息**
3. 复制 **App ID** 和 **App Secret**

#### 配置权限
1. 点击 **权限管理**
2. 添加以下权限：
   - `im:message` - 发送消息
   - `im:message.p2p` - 发送单聊消息
3. 提交审核（通常自动通过）

#### 获取 Open ID
1. 在飞书中打开 **开发者工具**
2. 使用 **获取用户 ID** 工具
3. 输入自己的飞书账号
4. 复制 **Open ID**

---

## 10. 运维管理

### 10.1 监控命令

```bash
# 查看服务状态
ps aux | grep server_enhanced

# 查看端口监听
netstat -tlnp | grep :443

# 查看实时日志
tail -f server.log

# 查看访问统计
cat data/audit_log.jsonl | wc -l

# 查看待审批数量
cat data/pending_approvals.json | python3 -c "import sys,json; print(len(json.load(sys.stdin)))"
```

### 10.2 日志管理

#### 日志轮转
```bash
# 创建日志轮转脚本
cat > /etc/logrotate.d/webviewer << 'EOF'
/root/.openclaw/workspace/webviewer/server.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}
EOF
```

#### 日志分析
```bash
# 今日访问量
grep $(date +%Y-%m-%d) data/audit_log.jsonl | wc -l

# 独立 IP 统计
cat data/audit_log.jsonl | python3 -c "
import sys,json
ips = set()
for line in sys.stdin:
    ips.add(json.loads(line)['ip'])
print(len(ips))
"

# 浏览器分布
cat data/audit_log.jsonl | python3 -c "
import sys,json
from collections import Counter
browsers = Counter(json.loads(line)['browser'] for line in sys.stdin)
for b, c in browsers.most_common(5):
    print(f'{b}: {c}')
"
```

### 10.3 数据备份

```bash
# 完整备份
BACKUP_DIR="/backup/webviewer/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR
cp -r /root/.openclaw/workspace/webviewer/data $BACKUP_DIR/
cp /root/.openclaw/workspace/webviewer/config.json $BACKUP_DIR/

# 压缩备份
tar -czf $BACKUP_DIR.tar.gz -C /root/.openclaw/workspace/webviewer data config.json

# 清理 30 天前备份
find /backup/webviewer -name "*.tar.gz" -mtime +30 -delete
```

### 10.4 故障排查

#### 问题 1：服务无法启动
```bash
# 检查端口占用
lsof -i :443

# 检查 Python 版本
python3 --version

# 检查证书文件
ls -la data/server.*

# 查看错误日志
tail -50 server.log
```

#### 问题 2：飞书通知失败
```bash
# 验证环境变量
echo $FEISHU_APP_ID
echo $FEISHU_APP_SECRET
echo $FEISHU_USER_OPEN_ID

# 测试 Token 获取
python3 -c "
import requests
r = requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    json={'app_id': '$FEISHU_APP_ID', 'app_secret': '$FEISHU_APP_SECRET'})
print(r.json())
"

# 检查日志中的飞书错误
grep -i "feishu\|飞书" server.log | tail -20
```

#### 问题 3：证书错误
```bash
# 重新生成证书
./generate_ssl_cert.sh

# 验证证书
openssl x509 -in data/server.crt -text -noout

# 检查证书权限
chmod 644 data/server.crt
chmod 600 data/server.key
```

---

## 11. 项目亮点

### 11.1 创新设计

#### 🎨 悬浮球交互设计
- 主页采用**双悬浮球**设计，视觉吸引力强
- 管理员登录（🔐 紫色）和访客申请（🚀 绿色）清晰区分
- 悬浮动画效果，提升用户体验

#### 📱 响应式等待页面
- 访客等待页面自动轮询审批状态
- 审批通过自动跳转，无需手动刷新
- 超时保护机制（6 分钟），避免无限等待

#### 📊 增强审计日志
- 记录 15+ 维度访问信息
- 支持多维度筛选和统计
- 设备类型自动识别（Desktop/Mobile/iPhone/Tablet/Bot）

### 11.2 技术优势

#### 🚀 零依赖部署
- 仅使用 Python 标准库
- 无需 pip 安装任何包
- 单文件核心代码，易维护

#### 💾 轻量级存储
- JSON 文件存储，无需数据库
- 数据格式人类可读
- 易于备份和迁移

#### 🔌 灵活集成
- 飞书通知可替换为其他 IM
- 支持自定义白名单策略
- 会话超时时间可配置

### 11.3 安全特性

#### 🛡️ 多层防护
1. **HTTPS 加密** - 全链路通信加密
2. **会话令牌** - 不可预测的 UUID
3. **HttpOnly Cookie** - 防止 XSS 攻击
4. **密码哈希** - SHA256 加密存储
5. **IP 白名单** - 可信 IP 自动放行

#### 📝 完整审计
- 所有访问行为可追溯
- 审批操作有记录
- 登录尝试有日志

### 11.4 用户体验

#### ✨ 流畅交互
- 登录成功自动跳转
- 审批通过实时通知
- 退出登录一键完成

#### 🎯 清晰反馈
- 审批状态实时更新
- 错误信息友好提示
- 操作结果即时显示

---

## 12. 附录

### 12.1 配置文件示例

#### config.json
```json
{
  "admin": {
    "username": "yangjiukui",
    "password_hash": "393a58a897f871b6c803f5b283ec31edcce18d97979a6e6df406438d5391bbc9"
  },
  "api_token": "wv_tok_3feb60dd2164cd04bdc1f644449919c3",
  "whitelist_ips": [
    "43.153.153.62",
    "221.219.243.106",
    "223.104.41.9"
  ],
  "session_timeout_hours": 24
}
```

#### .env
```bash
FEISHU_APP_ID=cli_a9f6713611785bd7
FEISHU_APP_SECRET=LZXIXtcD0p2k3fZ2oOO7GbiXCZPCT76L
FEISHU_USER_OPEN_ID=ou_bf3abf3dd2329a3b640bd95a55cf54c8
```

### 12.2 常用命令速查

```bash
# 启动服务
cd /root/.openclaw/workspace/webviewer
python3 server_enhanced.py

# 停止服务
pkill -f server_enhanced.py

# 重启服务
pkill -f server_enhanced.py && python3 server_enhanced.py &

# 查看日志
tail -f server.log

# 查看审计日志
cat data/audit_log.jsonl | tail -20

# 查看待审批
cat data/pending_approvals.json | python3 -m json.tool

# 生成密码哈希
python3 generate_password.py

# 生成 SSL 证书
./generate_ssl_cert.sh

# 检查配置
python3 check_config.py

# 诊断问题
./diagnose.sh
```

### 12.3 相关文档

| 文档 | 说明 | 路径 |
|------|------|------|
| 部署指南 | 完整部署步骤 | DEPLOYMENT.md |
| 使用指南 | 详细使用说明 | USAGE_GUIDE.md |
| 功能说明 | 功能列表和细节 | FUNCTIONS.md |
| 审批系统 | 审批流程说明 | README_APPROVAL.md |
| 监控说明 | 监控配置指南 | MONITOR_README.md |
| 修改记录 | 历史修改日志 | MODIFICATIONS_20260314.md |

### 12.4 联系方式

- **项目仓库**: `/root/.openclaw/workspace/webviewer`
- **在线文档**: `/root/.openclaw/workspace/webviewer/PROJECT_DOCUMENTATION.md`
- **技术支持**: 查看 server.log 日志文件

---

## 📄 文档信息

| 项目 | 内容 |
|------|------|
| **文档版本** | v2.0 |
| **创建日期** | 2026-03-14 |
| **最后更新** | 2026-03-14 |
| **文档状态** | ✅ 完成 |
| **总字数** | ~15,000 字 |

---

**WebViewer - 让访问更安全，让管理更简单** 🔐
