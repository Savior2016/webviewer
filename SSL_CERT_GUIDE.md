# WebViewer SSL 证书配置指南

当前使用的是**自签名证书**，浏览器会显示安全警告。以下是配置可信任证书的方案。

---

## 🎯 方案对比

| 方案 | 费用 | 有效期 | 信任度 | 推荐度 |
|------|------|--------|--------|--------|
| Let's Encrypt | 免费 | 90 天 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 阿里云免费 SSL | 免费 | 1 年 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 腾讯云免费 SSL | 免费 | 1 年 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 商业 SSL 证书 | ¥500+/年 | 1-3 年 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 📌 方案一：Let's Encrypt（推荐）

### 前提条件
- 有公网 IP
- 域名已解析到服务器
- 80 端口可访问

### 安装 Certbot

```bash
# CentOS/RHEL
sudo yum install -y certbot

# Ubuntu/Debian
sudo apt install -y certbot
```

### 获取证书

```bash
# Standalone 模式（需要停止 WebViewer）
sudo certbot certonly --standalone -d your-domain.com

# 或 DNS 验证模式（不需要 80 端口）
sudo certbot certonly --manual --preferred-challenges dns -d your-domain.com
```

### 证书位置

```
/etc/letsencrypt/live/your-domain.com/fullchain.pem
/etc/letsencrypt/live/your-domain.com/privkey.pem
```

### 配置到 WebViewer

```bash
# 备份原证书
cd /root/.openclaw/workspace
cp selfsigned.crt selfsigned.crt.bak
cp selfsigned.key selfsigned.key.bak

# 复制 Let's Encrypt 证书
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem selfsigned.crt
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem selfsigned.key

# 设置权限
sudo chmod 644 selfsigned.crt
sudo chmod 600 selfsigned.key

# 重启服务
pkill -9 -f "python3 server.py"
nohup python3 server.py > /tmp/webviewer.log 2>&1 &
```

### 自动续期

```bash
# 添加 cron 任务
sudo crontab -e

# 添加以下行（每月 1 号凌晨 3 点检查续期）
0 3 1 * * certbot renew --quiet && cp /etc/letsencrypt/live/your-domain.com/fullchain.pem /root/.openclaw/workspace/selfsigned.crt && cp /etc/letsencrypt/live/your-domain.com/privkey.pem /root/.openclaw/workspace/selfsigned.key && pkill -9 -f "python3 server.py" && nohup python3 server.py > /tmp/webviewer.log 2>&1 &
```

---

## 📌 方案二：阿里云免费 SSL

### 申请步骤

1. 登录阿里云控制台
2. 进入 **SSL 证书服务**
3. 点击 **免费证书** → **购买**（0 元）
4. 填写域名信息，完成验证
5. 下载证书（选择 Nginx 格式）

### 配置到 WebViewer

```bash
cd /root/.openclaw/workspace

# 备份原证书
cp selfsigned.crt selfsigned.crt.bak
cp selfsigned.key selfsigned.key.bak

# 上传证书文件后重命名
# 将下载的 .pem 文件重命名为 selfsigned.crt
# 将下载的 .key 文件重命名为 selfsigned.key

# 设置权限
chmod 644 selfsigned.crt
chmod 600 selfsigned.key

# 重启服务
pkill -9 -f "python3 server.py"
nohup python3 server.py > /tmp/webviewer.log 2>&1 &
```

---

## 📌 方案三：腾讯云免费 SSL

### 申请步骤

1. 登录腾讯云控制台
2. 进入 **SSL 证书** 服务
3. 申请免费证书
4. 完成域名验证
5. 下载证书

### 配置到 WebViewer

与阿里云方案相同，将证书文件复制到 `/root/.openclaw/workspace/` 目录即可。

---

## 🔧 当前证书信息

```bash
# 查看当前证书
openssl x509 -in /root/.openclaw/workspace/selfsigned.crt -text -noout | head -20

# 查看证书过期时间
openssl x509 -in /root/.openclaw/workspace/selfsigned.crt -noout -dates
```

---

## ⚠️ 注意事项

1. **证书文件权限**
   - `.crt` 文件：644（可读）
   - `.key` 文件：600（仅所有者可读写）

2. **证书文件格式**
   - WebViewer 使用 PEM 格式
   - 如果是其他格式（如 .pfx），需要转换：
     ```bash
     openssl pkcs12 -in certificate.pfx -out certificate.pem -nodes
     ```

3. **重启服务**
   - 每次更换证书后必须重启 WebViewer 服务
   - 确保证书路径正确：`/root/.openclaw/workspace/selfsigned.crt` 和 `selfsigned.key`

4. **防火墙**
   - 确保 443 端口开放
   - Let's Encrypt 验证时需要 80 端口开放

---

## 📞 需要帮助？

如果需要我帮你配置证书，请提供：
1. 你的域名
2. 服务器系统（CentOS/Ubuntu 等）
3. 是否有公网 IP

我可以自动帮你完成配置！
