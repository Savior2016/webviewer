#!/bin/bash
# Let's Encrypt 证书申请脚本

DOMAIN="www.friday-keeper.icu"
EMAIL="admin@friday-keeper.icu"
CERT_DIR="/etc/letsencrypt/live/$DOMAIN"
WEBVIEWER_DATA="/root/.openclaw/workspace/webviewer/data"

echo "🔐 开始申请 Let's Encrypt 证书..."
echo "域名：$DOMAIN"
echo ""

# 检查是否已有证书
if [ -f "$CERT_DIR/fullchain.pem" ]; then
    echo "✅ 证书已存在，尝试续期..."
    certbot renew --cert-name "$DOMAIN" --non-interactive
else
    echo "⚠️  需要手动添加 DNS TXT 记录"
    echo ""
    echo "请在域名控制台添加以下 TXT 记录："
    echo "  类型：TXT"
    echo "  主机：_acme-challenge.www"
    echo "  值：(运行 certbot 后显示)"
    echo ""
    read -p "添加完成后按回车继续..."
fi

# 申请证书
certbot certonly --manual --preferred-challenges dns \
    -d "$DOMAIN" \
    --email "$EMAIL" \
    --agree-tos

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 证书申请成功！"
    echo ""
    echo "📋 正在复制证书到 WebViewer..."
    
    # 备份旧证书
    cp "$WEBVIEWER_DATA/server.crt" "$WEBVIEWER_DATA/server.crt.old" 2>/dev/null
    cp "$WEBVIEWER_DATA/server.key" "$WEBVIEWER_DATA/server.key.old" 2>/dev/null
    
    # 复制新证书
    cp "$CERT_DIR/fullchain.pem" "$WEBVIEWER_DATA/server.crt"
    cp "$CERT_DIR/privkey.pem" "$WEBVIEWER_DATA/server.key"
    
    echo "✅ 证书已复制到："
    echo "   $WEBVIEWER_DATA/server.crt"
    echo "   $WEBVIEWER_DATA/server.key"
    echo ""
    echo "🔄 请重启 WebViewer 服务使证书生效"
else
    echo "❌ 证书申请失败"
    exit 1
fi
