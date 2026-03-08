#!/bin/bash
# 生成自签名 SSL 证书

CERT_DIR="/root/.openclaw/workspace/webviewer/data"
mkdir -p "$CERT_DIR"

echo "🔐 生成 SSL 证书..."

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout "$CERT_DIR/server.key" \
    -out "$CERT_DIR/server.crt" \
    -subj "/C=CN/ST=Beijing/L=Beijing/O=WebViewer/CN=$(hostname)"

echo "✅ 证书已生成："
echo "   证书：$CERT_DIR/server.crt"
echo "   私钥：$CERT_DIR/server.key"
echo ""
echo "⚠️  浏览器会提示证书不安全，点击\"继续访问\"即可"
