# WebViewer 项目功能描述

> 📜 **维护规则**：每次修改项目代码时，必须参考此文档并同步更新。
> 
> **最后更新**：2026-03-09 - 新增账号密码登录、增强访问审计功能

---

## 📁 项目结构

```
/root/.openclaw/workspace/webviewer/
├── server_enhanced.py           # 增强版主服务器（登录 + 审批 + 审计）
├── server_with_approval.py      # 旧版主服务器（保留）
├── server_with_auth.py          # 备用服务器（带认证功能）
├── auto_notify.py               # 自动审批通知监控脚本
├── feishu_callback.py           # 飞书回调处理器
├── check_config.py              # 配置检查工具
├── generate_ssl_cert.sh         # SSL 证书生成脚本
├── start-with-approval.sh       # 启动脚本
├── stop-with-approval.sh        # 停止脚本
├── get_open_id.py               # 获取飞书 Open ID 工具
├── get_user_id.py               # 获取飞书 User ID 工具
├── config.json                  # 项目配置文件
├── .env                         # 环境变量配置
├── server.log                   # 运行日志
├── server.pid                   # 进程 PID 文件
├── DEPLOYMENT.md                # 部署指南
├── PROJECT_SUMMARY.md           # 项目总结
├── README_APPROVAL.md           # 快速上手指南
├── USAGE_GUIDE.md               # 使用指南
├── FUNCTIONS.md                 # 功能描述（本文档）
├── data/                        # 数据目录
│   ├── server.crt               # SSL 证书
│   ├── server.key               # SSL 私钥
│   ├── access_log.jsonl         # 访问日志（简化版）
│   ├── audit_log.jsonl          # 审计日志（详细版）⭐新增
│   ├── pending_approvals.json   # 待审批记录
│   ├── approved_sessions.json   # 已批准会话
│   ├── admin_sessions.json      # 管理员会话 ⭐新增
│   ├── sessions.json            # 会话数据
│   ├── notify_state.json        # 通知状态
│   ├── bydesign/checklist.json  # bydesign 项目数据
│   └── cherry-pick/moves.json   # cherry-pick 项目数据
└── www/                         # 静态网站目录
    └── reports/index.json       # 报告数据
```

---

## 🎯 核心功能

### 0. 账号密码登录 ⭐新增

**功能描述**：管理员需要通过账号密码登录才能访问管理页面。

**工作流程**：
1. 访问 `/login` 显示登录页面
2. 输入用户名和密码
3. 验证通过 → 生成管理员会话（12 小时有效）
4. 会话存储在 Cookie 中（`wv_admin_session`）
5. 访问管理页面时验证会话
6. 登出时清除会话

**相关代码**：
- `DataManager.verify_admin_login()` - 验证登录
- `DataManager.create_admin_session()` - 创建会话
- `DataManager.check_admin_session()` - 验证会话
- `WebViewerHandler.handle_login()` - 处理登录请求
- `WebViewerHandler.show_login_page()` - 显示登录页面

**配置项**：
- `ADMIN_SESSION_TIMEOUT_HOURS = 12` - 管理员会话有效期
- 账号密码存储在 `config.json` 的 `admin` 字段

**密码加密**：使用 SHA-256 哈希存储

---

### 1. 访问审核系统

**功能描述**：拦截所有未授权的 Web 访问请求，强制经过管理员审批。

**工作流程**：
1. 用户访问网站 → 拦截请求
2. 记录访问者信息（IP、User-Agent、时间、路径）
3. 生成唯一审批 ID 和验证码
4. 发送飞书审批通知给管理员
5. 显示"等待审批"页面给访问者
6. 访问者页面每 5 秒轮询审批状态
7. 管理员审批通过 → 生成 24 小时有效会话
8. 访问者自动刷新进入网站

**相关代码**：
- `server_with_approval.py` - 主逻辑
- `DataManager.create_pending_approval()` - 创建审批记录
- `DataManager.approve_access()` - 批准访问
- `DataManager.reject_access()` - 拒绝访问
- `WebViewerHandler.check_access()` - 访问权限检查

**配置项**（`server_with_approval.py` 中的 `Config` 类）：
- `HOST = '0.0.0.0'` - 监听地址
- `HTTPS_PORT = 443` - HTTPS 端口（标准端口）
- `SESSION_TIMEOUT_HOURS = 24` - 会话有效期
- `PENDING_TIMEOUT_MINUTES = 30` - 待审批超时
- `WHITELIST_IPS = []` - 白名单 IP 列表

**数据文件**：
- `data/pending_approvals.json` - 待审批记录
- `data/approved_sessions.json` - 已批准会话
- `data/access_log.jsonl` - 访问日志（JSONL 格式）

---

### 2. 增强访问审计 ⭐新增

**功能描述**：详细记录每次访问尝试的完整信息，提供审计日志查看页面和实时通知。

**记录的审计信息**：
- 时间戳（timestamp, datetime）
- IP 地址
- User-Agent（完整）
- 浏览器类型（Chrome/Firefox/Safari/Edge/IE）
- 操作系统平台（Windows/macOS/Linux/Android/iOS）
- 访问路径
- HTTP 方法
- Referer
- Accept-Language
- 地理位置（内网/未知）
- 事件类型（page_access, login_attempt, approval 等）
- 访问状态（allowed/blocked/success/failed）
- 会话 ID
- 额外信息（extra 字段）

**审计日志查看**：
- **页面**：`/audit`（需要管理员登录）
- **功能**：
  - 实时显示访问日志（自动刷新 30 秒）
  - 按 IP 过滤
  - 按路径过滤
  - 统计面板（总访问数、独立 IP、今日访问、待审批数）
  - 分页加载（每次 50 条）
- **API**：`/api/audit-logs?limit=50&offset=0&ip=&path=`

**实时通知**：
- 有人访问时自动发送飞书通知
- 通知内容：IP、设备、位置、路径、时间、状态
- 包含审计日志页面链接

**相关代码**：
- `DataManager.log_audit()` - 记录审计日志
- `DataManager.get_audit_logs()` - 获取审计日志
- `DataManager.get_stats()` - 获取统计信息
- `FeishuNotifier.send_access_alert()` - 发送访问告警
- `WebViewerHandler.show_audit_page()` - 显示审计页面
- `WebViewerHandler.handle_audit_logs_api()` - 审计日志 API

**数据文件**：
- `data/audit_log.jsonl` - 审计日志文件

---

### 3. 会话管理

**功能描述**：审批通过后生成会话令牌，24 小时内无需重复审批。

**实现机制**：
- 会话 ID：UUID v4
- 存储位置：Cookie (`wv_session`)
- 有效期：24 小时（可配置）
- 自动清理：过期会话自动删除

**相关代码**：
- `DataManager.approve_access()` - 创建会话
- `DataManager.check_session()` - 验证会话
- `DataManager._cleanup_expired()` - 清理过期数据

---

### 4. 飞书通知集成

**通知内容**：
- 访问者 IP 地址
- 设备信息（User-Agent）
- 访问路径
- 访问时间
- 审批链接（同意/拒绝）
- 验证码

**配置方式**：
```bash
export FEISHU_APP_ID="cli_xxxxx"
export FEISHU_APP_SECRET="xxxxx"
export FEISHU_USER_OPEN_ID="ou_xxxxx"
```

**相关代码**：
- `FeishuNotifier.send_approval_request()` - 发送通知
- `feishu_callback.py` - 处理飞书回调

---

### 4. 自动通知监控

**功能描述**：`auto_notify.py` 监控待审批列表，通过 OpenClaw 飞书通道发送通知。

**工作方式**：
- 定期扫描 `data/pending_approvals.json`
- 对比 `data/notify_state.json` 避免重复通知
- 通过 `openclaw message send` 命令发送飞书消息
- 记录已通知的审批 ID

**配置项**（`auto_notify.py`）：
- `USER_IP = '43.153.153.62'` - 用户外网 IP
- `INTERNAL_IP = '221.219.243.106'` - 用户内网 IP

---

### 6. 管理功能

#### 6.1 管理员登录
- **路径**：`/login`
- **功能**：管理员账号密码登录
- **访问条件**：公开访问

#### 6.2 管理员登出
- **路径**：`/logout`
- **功能**：清除管理员会话
- **访问条件**：公开访问

#### 6.3 审计日志页面 ⭐新增
- **路径**：`/audit`
- **功能**：查看详细的访问审计日志
- **访问条件**：需要管理员登录
- **功能特性**：
  - 实时刷新（30 秒自动更新）
  - IP 过滤
  - 路径过滤
  - 统计面板
  - 分页加载

#### 6.4 审计日志 API ⭐新增
- **路径**：`/api/audit-logs`
- **方法**：GET
- **参数**：
  - `limit` - 每页数量（默认 50）
  - `offset` - 偏移量（默认 0）
  - `ip` - 按 IP 过滤
  - `path` - 按路径过滤
- **返回**：JSON 格式日志列表和统计信息
- **访问条件**：需要管理员登录

#### 6.5 待审批列表页面
- **路径**：`/pending`
- **功能**：显示所有待审批请求，支持页面内审批
- **访问条件**：需要管理员登录

#### 5.2 访问日志
- **文件**：`data/access_log.jsonl`
- **格式**：每行一条 JSON 记录
- **字段**：timestamp, datetime, ip, user_agent, path, method, location

#### 5.3 审批链接
- **同意**：`https://{IP}/approve/{approval_id}`
- **拒绝**：`https://{IP}/reject/{approval_id}`

---

### 6. SSL/HTTPS 加密

**功能描述**：所有通信使用 HTTPS 加密。

**证书管理**：
- 生成脚本：`generate_ssl_cert.sh`
- 证书文件：`data/server.crt`
- 私钥文件：`data/server.key`
- 类型：自签名证书（生产环境建议用正式证书）

---

### 7. 白名单机制

**功能描述**：配置白名单 IP 可直接访问，无需审批。

**配置位置**：
- `config.json` 中的 `whitelist_ips` 数组
- 当前白名单：`["43.153.153.62", "221.219.243.106"]`

**相关代码**：
- `WebViewerHandler.check_access()` - 白名单检查

---

### 9. 多项目支持

**功能描述**：支持托管多个子项目。

**已配置项目**：
- **momhand**：`/momhand/api/items`, `/momhand/`
- **cherry-pick**：`/cherry-pick/api/moves`, `/cherry-pick/`
- **bydesign**：`/bydesign/api/checklist`, `/bydesign/`

**数据文件**：
- `data/bydesign/checklist.json`
- `data/cherry-pick/moves.json`

---

## 🔌 API 端点

### 公开端点
| 路径 | 方法 | 说明 |
|------|------|------|
| `/login` | GET | 管理员登录页面 |
| `/api/login` | POST | 登录 API |
| `/logout` | GET | 登出 |
| `/approve/{id}` | GET | 批准访问 |
| `/reject/{id}` | GET | 拒绝访问 |
| `/check-status/{id}` | GET | 检查审批状态 |

### 需要管理员登录
| 路径 | 方法 | 说明 |
|------|------|------|
| `/audit` | GET | 审计日志页面 |
| `/api/audit-logs` | GET | 审计日志 API |
| `/pending` | GET | 待审批列表页面 |
| `/api/audit-delete` | POST | 删除审计日志 |

---

## 📊 数据格式

### 审计日志 (`audit_log.jsonl`)
```json
{
  "timestamp": 1234567890,
  "datetime": "2026-03-09T21:00:00",
  "event_type": "page_access",
  "ip": "x.x.x.x",
  "user_agent": "Mozilla/5.0...",
  "browser": "Chrome",
  "platform": "Windows",
  "path": "/",
  "method": "GET",
  "referer": "",
  "language": "zh-CN",
  "location": "未知",
  "status": "allowed",
  "session_id": "uuid",
  "extra": {}
}
```

### 管理员会话 (`admin_sessions.json`)
```json
{
  "session_id": {
    "session_id": "uuid",
    "username": "yangjiukui",
    "ip": "x.x.x.x",
    "login_at": 1234567890,
    "expires_at": 1234567890
  }
}
```

---

## 🔧 工具脚本

### `check_config.py`
- **功能**：检查配置是否完整
- **检查项**：环境变量、SSL 证书、端口占用

### `generate_ssl_cert.sh`
- **功能**：生成自签名 SSL 证书
- **输出**：`data/server.crt`, `data/server.key`

### `start-with-approval.sh`
- **功能**：启动 WebViewer 服务
- **后台运行**：使用 nohup

### `stop-with-approval.sh`
- **功能**：停止 WebViewer 服务
- **清理**：删除 PID 文件

### `get_open_id.py` / `get_user_id.py`
- **功能**：获取飞书用户标识
- **用途**：配置飞书通知时使用

---

## 📊 数据格式

### 待审批记录 (`pending_approvals.json`)
```json
{
  "approval_id": {
    "approval_id": "uuid",
    "verification_code": "6 位验证码",
    "visitor_info": {
      "ip": "x.x.x.x",
      "user_agent": "...",
      "path": "/",
      "method": "GET",
      "location": "未知"
    },
    "timestamp": 1234567890,
    "status": "pending|approved|rejected"
  }
}
```

### 已批准会话 (`approved_sessions.json`)
```json
{
  "session_id": {
    "session_id": "uuid",
    "ip": "x.x.x.x",
    "approved_at": 1234567890,
    "expires_at": 1234567890,
    "approval_id": "xxx"
  }
}
```

### 访问日志 (`access_log.jsonl`)
```jsonl
{"timestamp": 1234567890, "datetime": "2026-03-09T12:00:00", "ip": "x.x.x.x", "user_agent": "...", "path": "/", "method": "GET", "location": "未知"}
```

---

## 🚀 启动流程

```bash
# 1. 设置环境变量
export FEISHU_APP_ID="cli_xxxxx"
export FEISHU_APP_SECRET="xxxxx"
export FEISHU_USER_OPEN_ID="ou_xxxxx"

# 2. 检查配置
python3 check_config.py

# 3. 启动服务
./start-with-approval.sh

# 4. 验证
ps aux | grep server_with_approval
curl -k https://127.0.0.1:443
```

---

## 🔍 管理命令

```bash
# 查看服务状态
ps aux | grep server_enhanced

# 查看实时日志
tail -f server.log

# 查看审计日志（原始数据）
cat data/audit_log.jsonl

# 查看访问日志（简化版）
cat data/access_log.jsonl

# 查看待审批
cat data/pending_approvals.json

# 查看管理员会话
cat data/admin_sessions.json

# 重启服务
pkill -f server_enhanced.py
cd /root/.openclaw/workspace/webviewer && nohup python3 server_enhanced.py > server.log 2>&1 &

# 清理过期数据
python3 -c "from server_enhanced import data_manager; data_manager._cleanup_expired()"

# 查看统计信息
python3 -c "from server_enhanced import data_manager; print(data_manager.get_stats())"
```

---

## 🛡️ 安全特性

1. **HTTPS 加密**：所有通信使用 SSL/TLS
2. **会话令牌**：审批通过后生成唯一会话 ID
3. **访问日志**：记录所有访问尝试
4. **白名单机制**：可信 IP 直接放行
5. **审批超时**：30 分钟未审批自动清理
6. **会话过期**：24 小时后自动失效

---

## 📈 可扩展功能（待实现）

- [ ] 管理页面登录认证
- [ ] IP 地理位置查询（调用 API）
- [ ] 访问频率限制
- [ ] 黑名单功能
- [ ] 邮件通知备用
- [ ] 多管理员审批
- [ ] 审批理由填写
- [ ] 访问统计分析
- [ ] 数据库存储（替代 JSON 文件）
- [ ] WebSocket 实时推送审批结果

---

## 📝 修改历史

| 日期 | 修改内容 | 修改人 |
|------|----------|--------|
| 2026-03-09 | 初始版本，基于现有代码生成功能描述 | Friday |
| 2026-03-09 | 新增账号密码登录功能、增强访问审计功能、实时飞书通知 | Friday |

**本次更新详情**：
- 创建 `server_enhanced.py` 增强版服务器
- 新增管理员登录/登出功能
- 新增详细审计日志记录（浏览器、平台、Referer 等）
- 新增审计日志查看页面（`/audit`）
- 新增审计日志 API（`/api/audit-logs`）
- 新增访问告警飞书通知
- 新增统计面板（总访问、独立 IP、今日访问、待审批）

---

## ⚠️ 注意事项

1. **修改代码前**：必须先阅读此文档了解整体架构
2. **修改代码后**：必须同步更新此文档的相关章节
3. **新增功能**：必须在此文档中添加对应章节
4. **删除功能**：必须在此文档中标记为"已废弃"
5. **配置变更**：必须更新配置项说明

---

**文档维护责任**：每次修改项目代码时，必须同时更新此文档。
