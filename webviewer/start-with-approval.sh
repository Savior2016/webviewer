#!/bin/bash
# WebViewer 带审批功能 - 快速启动脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔐 WebViewer 访问审核系统"
echo "=========================="
echo ""

# 检查 SSL 证书
if [ ! -f "data/server.crt" ] || [ ! -f "data/server.key" ]; then
    echo "⚠️  SSL 证书未找到，正在生成..."
    ./generate_ssl_cert.sh
    echo ""
fi

# 检查飞书配置
echo "📋 检查配置..."
if [ -z "$FEISHU_APP_ID" ]; then
    echo "⚠️  FEISHU_APP_ID 未设置"
    echo "   请运行：export FEISHU_APP_ID=\"your_app_id\""
else
    echo "✅ FEISHU_APP_ID 已配置"
fi

if [ -z "$FEISHU_APP_SECRET" ]; then
    echo "⚠️  FEISHU_APP_SECRET 未设置"
    echo "   请运行：export FEISHU_APP_SECRET=\"your_secret\""
else
    echo "✅ FEISHU_APP_SECRET 已配置"
fi

if [ -z "$FEISHU_USER_OPEN_ID" ]; then
    echo "⚠️  FEISHU_USER_OPEN_ID 未设置"
    echo "   请运行：export FEISHU_USER_OPEN_ID=\"your_open_id\""
else
    echo "✅ FEISHU_USER_OPEN_ID 已配置"
fi

echo ""

# 检查是否已有服务在运行
PID_FILE="$SCRIPT_DIR/server.pid"
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "⚠️  服务已在运行 (PID: $OLD_PID)"
        echo "   停止旧服务：./stop-webviewer.sh"
        exit 0
    else
        rm -f "$PID_FILE"
    fi
fi

# 启动服务
echo "🚀 启动 WebViewer 审核服务..."
echo ""

nohup python3 server_with_approval.py >> server.log 2>&1 &
NEW_PID=$!
echo "$NEW_PID" > "$PID_FILE"

sleep 3

if kill -0 "$NEW_PID" 2>/dev/null; then
    echo "✅ 服务已启动 (PID: $NEW_PID)"
    echo ""
    echo "📡 访问地址：https://$(hostname -I | awk '{print $1}'):8443"
    echo "📋 管理页面：https://$(hostname -I | awk '{print $1}'):8443/pending"
    echo "📜 日志文件：$SCRIPT_DIR/server.log"
    echo ""
    echo "⚠️  首次访问需要审批，请留意飞书通知！"
else
    echo "❌ 服务启动失败"
    echo "查看日志：tail -f server.log"
    rm -f "$PID_FILE"
    exit 1
fi
