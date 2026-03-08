# WebViewer 访问审核系统 - 完整使用指南

## 🎉 功能已实现

✅ **访问拦截审核** - 所有访问者需经审批
✅ **信息记录** - IP、设备、时间完整记录
✅ **飞书通知** - 实时推送审批请求
✅ **一键审批** - 卡片按钮同意/拒绝
✅ **会话管理** - 24 小时有效自动续期
✅ **管理后台** - /pending 查看待审批列表

---

## 📁 项目文件

```
webviewer/
├── 🔧 server_with_approval.py       # 主服务器（核心）
├── 🔧 feishu_callback.py            # 飞书回调处理
├── 🔐 generate_ssl_cert.sh          # SSL 证书生成
├── 🚀 start-with-approval.sh        # 快速启动
├── 🛑 stop-with-approval.sh         # 停止服务
├── 🔍 check_config.py               # 配置检查
├── 📖 DEPLOYMENT.md                 # 部署文档
├── 📖 README_APPROVAL.md            # 快速上手
├── 📖 PROJECT_SUMMARY.md            # 项目总结
└── data/
    ├── server.crt                   # SSL 证书 ✅
    ├── server.key                   # SSL 私钥 ✅
    ├── access_log.jsonl             # 访问日志
    ├── pending_approvals.json       # 待审批
    └── approved_sessions.json       # 已批准会话
```

---

## 🚀 立即开始

### 方式 1：临时启动（当前终端有效）

```bash
cd ~/.openclaw/workspace/webviewer

# 设置环境变量
export FEISHU_APP_ID="cli_a9f6713611785bd7"
export FEISHU_APP_SECRET="LZXIXtcD0p2k3fZ2oOO7GbiXCZPCT76L"
export FEISHU_USER_OPEN_ID="ou_bf3abf3dd2329a3b640bd95a55cf54c8"

# 启动服务
./start-with-approval.sh
```

### 方式 2：永久配置（推荐）

```bash
# 添加到 ~/.bashrc
cat >> ~/.bashrc << 'EOF'

# WebViewer 飞书配置
export FEISHU_APP_ID="cli_a9f6713611785bd7"
export FEISHU_APP_SECRET="LZXIXtcD0p2k3fZ2oOO7GbiXCZPCT76L"
export FEISHU_USER_OPEN_ID="ou_bf3abf3dd2329a3b640bd95a55cf54c8"
EOF

# 生效
source ~/.bashrc

# 启动服务
./start-with-approval.sh
```

---

## 📱 使用流程

### 访问者视角

```
1. 浏览器访问：https://你的服务器 IP:8443
   ↓
2. 看到"🔐 等待访问审批"页面
   ↓
3. 等待管理员审批（页面每 5 秒自动检查）
   ↓
4. ✅ 审批通过 → 自动刷新进入网站
   ❌ 审批拒绝 → 显示拒绝页面
   ↓
5. 24 小时内再次访问无需审批
```

### 管理员视角

```
1. 收到飞书消息通知
   ┌─────────────────────────────────┐
   │ 🔐 WebViewer 访问审批请求        │
   ├─────────────────────────────────┤
   │ 🌐 访问来源：192.168.1.100       │
   │ 🖥️ 设备：Mozilla/5.0 (Windows)  │
   │ 📍 位置：内网                    │
   │ ⏰ 时间：2026-03-07 09:30:00    │
   ├─────────────────────────────────┤
   │  [✅ 同意访问]  [❌ 拒绝访问]    │
   └─────────────────────────────────┘
   ↓
2. 点击按钮审批
   ↓
3. 访问者实时收到结果
```

---

## 🔧 常用命令

### 启动服务
```bash
./start-with-approval.sh
```

### 停止服务
```bash
./stop-with-approval.sh
```

### 重启服务
```bash
./stop-with-approval.sh && ./start-with-approval.sh
```

### 检查配置
```bash
python3 check_config.py
```

### 查看日志
```bash
tail -f server.log
```

### 查看访问记录
```bash
cat data/access_log.jsonl | python3 -m json.tool
```

### 查看待审批
```bash
cat data/pending_approvals.json | python3 -m json.tool
```

---

## 🌐 访问地址

| 用途 | 地址 |
|------|------|
| **主站** | `https://你的服务器 IP:8443` |
| **管理后台** | `https://你的服务器 IP:8443/pending` |
| **审批通过链接** | `https://你的服务器 IP:8443/approve/{approval_id}` |
| **审批拒绝链接** | `https://你的服务器 IP:8443/reject/{approval_id}` |

---

## 📊 数据结构

### 访问日志 (access_log.jsonl)
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

### 待审批 (pending_approvals.json)
```json
{
  "approval_id": "uuid...",
  "verification_code": "ABC123",
  "visitor_info": {...},
  "timestamp": 1772841600,
  "status": "pending"  // pending/approved/rejected
}
```

### 已批准会话 (approved_sessions.json)
```json
{
  "session_id": "uuid...",
  "ip": "192.168.1.100",
  "approved_at": 1772841600,
  "expires_at": 1772928000,  // 24 小时后
  "approval_id": "uuid..."
}
```

---

## 🛡️ 安全配置

### 白名单 IP（自动放行）

编辑 `server_with_approval.py`：
```python
WHITELIST_IPS = [
    '127.0.0.1',      # 本地
    '192.168.1.0/24', # 内网段
    '10.0.0.0/8'      # 公司网络
]
```

### 修改会话有效期

```python
SESSION_TIMEOUT_HOURS = 48  # 改为 48 小时
```

### 修改审批超时

```python
PENDING_TIMEOUT_MINUTES = 60  # 改为 60 分钟
```

---

## 🐛 故障排查

### 问题 1：收不到飞书通知

**检查：**
```bash
# 1. 验证环境变量
echo $FEISHU_APP_ID
echo $FEISHU_APP_SECRET
echo $FEISHU_USER_OPEN_ID

# 2. 查看日志
tail -f server.log | grep "飞书"

# 3. 测试飞书 API
python3 -c "
import requests
r = requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    json={'app_id': '$FEISHU_APP_ID', 'app_secret': '$FEISHU_APP_SECRET'})
print(r.json())
"
```

### 问题 2：服务启动失败

**检查：**
```bash
# 1. 端口占用
lsof -i :8443

# 2. SSL 证书
ls -la data/server.*

# 3. Python 错误
python3 server_with_approval.py
```

### 问题 3：浏览器无法访问

**检查：**
```bash
# 1. 防火墙
sudo firewall-cmd --list-ports
sudo firewall-cmd --add-port=8443/tcp --permanent

# 2. 服务器 IP
hostname -I

# 3. 服务状态
ps aux | grep server_with_approval
```

---

## 📈 监控与维护

### 实时监控访问
```bash
watch -n 1 'cat data/access_log.jsonl | tail -5'
```

### 统计今日访问
```bash
cat data/access_log.jsonl | grep $(date +%Y-%m-%d) | wc -l
```

### 清理过期数据
```bash
# 自动清理（服务启动时执行）
# 或手动清理
python3 -c "
from server_with_approval import data_manager
data_manager._cleanup_expired()
print('清理完成')
"
```

### 备份数据
```bash
cp -r data/ data.backup.$(date +%Y%m%d_%H%M%S)
```

---

## 📞 获取帮助

1. **查看完整文档**
   ```bash
   cat DEPLOYMENT.md    # 部署文档
   cat README_APPROVAL.md  # 快速上手
   cat PROJECT_SUMMARY.md  # 项目总结
   ```

2. **查看实时日志**
   ```bash
   tail -f server.log
   ```

3. **重新生成证书**
   ```bash
   ./generate_ssl_cert.sh
   ```

---

## ✅ 完成清单

部署前检查：
- [ ] SSL 证书已生成
- [ ] 飞书环境变量已配置
- [ ] 端口 8443 未被占用
- [ ] 防火墙已开放端口
- [ ] 飞书应用权限已配置

启动后检查：
- [ ] 服务正常运行
- [ ] 飞书消息能收到
- [ ] 审批按钮可点击
- [ ] 访问日志有记录
- [ ] 会话管理正常

---

**部署完成！开始使用吧！** 🎉
