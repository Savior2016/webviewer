# WebViewer 访问审核系统部署指南

## 🔐 功能说明

所有访问 WebViewer 的用户都需要经过审批：
1. 用户访问时自动拦截
2. 记录 IP、设备信息、访问时间
3. 发送飞书审批通知给管理员
4. 管理员同意后生成会话令牌（24 小时有效）
5. 拒绝则显示拒绝页面

---

## 📋 部署步骤

### 1. 生成 SSL 证书

```bash
cd ~/.openclaw/workspace/webviewer
chmod +x generate_ssl_cert.sh
./generate_ssl_cert.sh
```

会生成：
- `data/server.crt` - 证书文件
- `data/server.key` - 私钥文件

---

### 2. 配置飞书应用

#### 2.1 获取凭证

登录 [飞书开放平台](https://open.feishu.cn/)：
1. 创建企业自建应用
2. 获取 **App ID** 和 **App Secret**
3. 获取管理员的 **Open ID**（在飞书中查看）

#### 2.2 设置环境变量

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
export FEISHU_APP_ID="cli_xxxxxxxxxxxxx"
export FEISHU_APP_SECRET="xxxxxxxxxxxxxxxxxxxx"
export FEISHU_USER_OPEN_ID="ou_xxxxxxxxxxxxx"

# 使配置生效
source ~/.bashrc
```

#### 2.3 配置应用权限

在飞书开放平台添加以下权限：
- `im:message` - 发送消息
- `im:message.p2p` - 发送单聊消息

---

### 3. 启动服务

#### 方式 1：直接启动

```bash
cd ~/.openclaw/workspace/webviewer
python3 server_with_approval.py
```

#### 方式 2：后台运行

```bash
# 使用提供的启动脚本
chmod +x start-webviewer.sh
./start-webviewer.sh
```

#### 方式 3：Systemd 服务

```bash
sudo systemctl edit --force webviewer
```

添加配置：
```ini
[Unit]
Description=WebViewer with Approval System
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/.openclaw/workspace/webviewer
Environment="FEISHU_APP_ID=your_app_id"
Environment="FEISHU_APP_SECRET=your_secret"
Environment="FEISHU_USER_OPEN_ID=your_open_id"
ExecStart=/usr/bin/python3 /root/.openclaw/workspace/webviewer/server_with_approval.py
Restart=always

[Install]
WantedBy=multi-user.target
```

启动：
```bash
sudo systemctl enable webviewer
sudo systemctl start webviewer
```

---

## 🔧 配置说明

### 服务器配置

编辑 `server_with_approval.py` 中的 `Config` 类：

```python
class Config:
    HOST = '0.0.0.0'          # 监听地址
    PORT = 8888               # HTTP 端口（未使用）
    HTTPS_PORT = 8443         # HTTPS 端口
    
    SESSION_TIMEOUT_HOURS = 24     # 会话有效期
    PENDING_TIMEOUT_MINUTES = 30   # 待审批超时
    
    WHITELIST_IPS = ['127.0.0.1', '::1']  # 白名单 IP
```

### 飞书配置

| 环境变量 | 说明 | 示例 |
|----------|------|------|
| `FEISHU_APP_ID` | 飞书应用 ID | `cli_a9f6713611785bd7` |
| `FEISHU_APP_SECRET` | 飞书应用密钥 | `LZXIXtcD0p2k3fZ2oOO7GbiXCZPCT76L` |
| `FEISHU_USER_OPEN_ID` | 管理员 Open ID | `ou_bf3abf3dd2329a3b640bd95a55cf54c8` |

---

## 📱 使用流程

### 访问者视角

1. 访问 `https://your-server:8443`
2. 看到"等待审批"页面
3. 等待管理员审批
4. 审批通过后自动刷新进入网站
5. 24 小时内无需再次审批

### 管理员视角

1. 收到飞书消息通知
2. 查看访问者信息（IP、设备、时间）
3. 点击"✅ 同意"或"❌ 拒绝"
4. 审批结果实时反馈给访问者

---

## 🔍 管理功能

### 查看待审批列表

访问：`https://your-server:8443/pending`

显示所有待审批的访问请求，可直接在页面审批。

### 查看访问日志

```bash
cat ~/.openclaw/workspace/webviewer/data/access_log.jsonl
```

每条记录包含：
- 访问时间
- IP 地址
- User-Agent
- 访问路径

### 查看审批状态

```bash
cat ~/.openclaw/workspace/webviewer/data/pending_approvals.json
cat ~/.openclaw/workspace/webviewer/data/approved_sessions.json
```

---

## 🛡️ 安全建议

1. **使用 HTTPS**：已默认启用，不要关闭
2. **定期清理日志**：避免积累过多数据
3. **限制访问频率**：可添加 IP 限流逻辑
4. **白名单配置**：将内网 IP 加入白名单
5. **证书管理**：生产环境建议使用正式 SSL 证书

---

## 🐛 故障排查

### 问题 1：飞书消息发送失败

```
❌ 发送飞书通知失败：Feishu auth failed
```

**解决：**
- 检查环境变量是否正确
- 验证 App ID 和 App Secret
- 确认应用权限已配置

### 问题 2：SSL 证书错误

```
SSL certificate not found
```

**解决：**
```bash
./generate_ssl_cert.sh
```

### 问题 3：端口被占用

```
Address already in use
```

**解决：**
```bash
# 查看占用端口的进程
lsof -i :8443
# 杀死进程或修改配置中的端口
```

### 问题 4：浏览器提示证书不安全

**正常现象**，自签名证书会提示，点击"继续访问"即可。

---

## 📊 数据文件说明

```
data/
├── server.crt                  # SSL 证书
├── server.key                  # SSL 私钥
├── access_log.jsonl            # 访问日志（每行一条）
├── pending_approvals.json      # 待审批记录
└── approved_sessions.json      # 已批准会话
```

---

## 🔄 升级与维护

### 重启服务

```bash
# 使用启动脚本
./stop-webviewer.sh
./start-webviewer.sh

# 或直接杀死进程
pkill -f server_with_approval.py
python3 server_with_approval.py &
```

### 查看日志

```bash
tail -f server.log
```

### 备份数据

```bash
cp -r data/ data.backup.$(date +%Y%m%d)
```

---

## 📞 技术支持

遇到问题？检查以下内容：
1. 飞书应用配置是否正确
2. 环境变量是否生效
3. 端口是否开放
4. 防火墙设置

查看实时日志：
```bash
tail -f ~/.openclaw/workspace/webviewer/server.log
```
