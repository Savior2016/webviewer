#!/bin/bash
# DNS 验证脚本 - 输出 TXT 记录并等待用户确认

echo ""
echo "============================================"
echo "📋 请添加以下 DNS TXT 记录："
echo "============================================"
echo "  类型：TXT"
echo "  主机：_acme-challenge.www"
echo "  值：$CERTBOT_VALIDATION"
echo "  TTL: 600"
echo "============================================"
echo ""
echo "添加完成后，在域名控制台验证是否生效："
echo "https://toolbox.googleapps.com/apps/dig/#TXT/_acme-challenge.www.friday-keeper.icu"
echo ""
read -p "✅ 验证完成后按回车继续..."
echo "DNS 记录已确认"
