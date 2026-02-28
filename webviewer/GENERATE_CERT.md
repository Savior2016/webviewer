# 生成自签名证书的简易方法（如需手动操作）

如果你希望手动生成自签名证书，而不是由 server.py 自动生成，可以按如下方式操作：

## 1. 安装 openssl（如未安装）

在 Linux/macOS 终端或 Windows 的 WSL/Git Bash 中运行：

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install openssl

# CentOS/RHEL
sudo yum install openssl

# macOS (通常已预装，或通过 brew)
# brew install openssl

# Windows: 推荐使用 Git Bash / WSL / 或下载 OpenSSL for Windows
```

## 2. 生成私钥和自签名证书
在 `webviewer/` 目录下运行：

```bash
openssl req -x509 -newkey rsa:2048 -keyout selfsigned.key -out selfsigned.crt -days 365 -nodes -subj "/C=CN/ST=Beijing/L=Beijing/O=WebViewer/OU=Local/CN=localhost"
```

这将在当前目录生成：
- `selfsigned.key`：私钥文件
- `selfsigned.crt`：证书文件

然后将这两个文件放在 `webviewer/` 项目根目录，确保 `server.py` 能读取到它们。

> 📌 server.py 会优先使用你手动放置的证书，如不存在才会尝试自动生成（需安装 cryptography）。

## 3. 启动服务
确保文件结构如下：
```
webviewer/
├── server.py
├── selfsigned.crt
├── selfsigned.key
└── README.md
```
然后运行：
```bash
python server.py
```

访问：https://localhost:443

---

如你在生成或使用 HTTPS 证书时遇到问题，也可暂时使用 HTTP（不加密，不推荐外网暴露），或使用 ngrok/frp 等工具做外网转发。