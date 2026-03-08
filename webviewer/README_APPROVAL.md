# WebViewer 访问审核系统 - 快速上手

## 🎯 功能概述

为 WebViewer 添加访问控制功能：
- ✅ 所有访问者需要审批
- ✅ 记录 IP、设备、时间
- ✅ 飞书实时通知管理员
- ✅ 一键同意/拒绝
- ✅ 会话 24 小时有效

---

## 🚀 5 分钟快速部署

### 步骤 1：设置飞书配置（3 分钟）

```bash
# 编辑 ~/.bashrc，添加以下内容
export FEISHU_APP_ID="你的 App ID"
export FEISHU_APP_SECRET="你的 App Secret"
export FEISHU_USER_OPEN_ID="你的 Open ID"

# 使配置生效
source ~/.bashrc
```

**如何获取？**
1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 创建企业自建应用 → 获取 App ID 和 App Secret
3. 在飞书中查看自己的 Open ID（或联系管理员）

---

### 步骤 2：启动服务（1 分钟）

```bash
cd ~/.openclaw/workspace/webviewer
chmod +x start-with-approval.sh
./start-with-approval.sh
```

看到以下输出表示成功：
```
✅ 服务已启动 (PID: xxxxx)
📡 访问地址：https://192.168.x.x:8443
📋 管理页面：https://192.168.x.x:8443/pending
```

---

### 步骤 3：测试访问（1 分钟）

1. 在浏览器访问：`https://你的服务器 IP:8443`
2. 看到"等待审批"页面
3. 在飞书中收到审批通知
4. 点击"✅ 同意"
5. 页面自动刷新，进入网站

---

## 📱 使用示例

### 访问者体验

```
1. 访问网站
   ↓
2. 被拦截，显示"等待审批"
   ↓
3. 5 秒后自动检查审批状态
   ↓
4. 审批通过 → 自动进入网站
   审批拒绝 → 显示拒绝页面
```

### 管理员体验

```
1. 收到飞书消息：
   ┌─────────────────────────────┐
   │ 🔐 WebViewer 访问审批请求    │
   ├─────────────────────────────┤
   │ 🌐 访问来源：192.168.1.100   │
   │ 🖥️ 设备：Mozilla/5.0...     │
   │ ⏰ 时间：2026-03-07 09:30   │
   ├─────────────────────────────┤
   │  [✅ 同意访问]  [❌ 拒绝访问] │
   └─────────────────────────────┘

2. 点击"同意"或"拒绝"
   ↓
3. 访问者实时收到结果
```

---

## 🔧 常用操作

### 查看待审批列表

```bash
# 浏览器访问
https://你的服务器 IP:8443/pending
```

### 查看访问日志

```bash
# 实时查看
tail -f ~/.openclaw/workspace/webviewer/data/access_log.jsonl

# 或查看完整日志
cat ~/.openclaw/workspace/webviewer/data/access_log.jsonl
```

### 查看已批准的会话

```bash
cat ~/.openclaw/workspace/webviewer/data/approved_sessions.json
```

### 重启服务

```bash
./stop-with-approval.sh
./start-with-approval.sh
```

### 检查配置

```bash
python3 check_config.py
```

---

## 🛡️ 安全特性

| 特性 | 说明 |
|------|------|
| **HTTPS 加密** | 所有通信使用 SSL/TLS 加密 |
| **会话管理** | 审批通过后 24 小时有效 |
| **IP 记录** | 完整记录访问者 IP 地址 |
| **设备指纹** | 记录 User-Agent 等信息 |
| **白名单** | 支持配置自动放行的 IP |
| **超时清理** | 自动清理过期审批和会话 |

---

## 📊 数据文件

```
data/
├── server.crt              # SSL 证书
├── server.key              # SSL 私钥
├── access_log.jsonl        # 访问日志（JSONL 格式）
├── pending_approvals.json  # 待审批记录
└── approved_sessions.json  # 已批准会话
```

### 访问日志格式

每条记录包含：
```json
{
  "timestamp": 1772841600,
  "datetime": "2026-03-07T09:30:00",
  "ip": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "path": "/reports/index.html",
  "method": "GET",
  "location": "内网"
}
```

---

## 🐛 常见问题

### Q: 收不到飞书通知？

**A:** 检查：
1. 环境变量是否正确设置
2. 飞书应用权限是否配置
3. 查看日志：`tail -f server.log`

### Q: 浏览器提示证书不安全？

**A:** 正常现象（自签名证书），点击"继续访问"即可。
生产环境建议使用正式 SSL 证书。

### Q: 如何添加白名单 IP？

**A:** 编辑 `server_with_approval.py`，修改 `Config.WHITELIST_IPS`：
```python
WHITELIST_IPS = ['127.0.0.1', '192.168.1.0/24']
```

### Q: 会话有效期能改吗？

**A:** 可以，修改 `Config.SESSION_TIMEOUT_HOURS`：
```python
SESSION_TIMEOUT_HOURS = 48  # 改为 48 小时
```

---

## 📞 需要帮助？

1. 查看日志：`tail -f server.log`
2. 检查配置：`python3 check_config.py`
3. 查看完整文档：`cat DEPLOYMENT.md`

---

**祝使用愉快！** 🎉
