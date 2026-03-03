#!/bin/bash
# WebViewer 服务启动脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/server.log"
PID_FILE="$SCRIPT_DIR/server.pid"

# 检查是否已有服务在运行
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "⚠️  服务已在运行 (PID: $OLD_PID)"
        exit 0
    else
        echo "🧹 清理旧的 PID 文件"
        rm -f "$PID_FILE"
    fi
fi

# 启动服务
echo "🚀 启动 WebViewer HTTPS 服务..."
cd "$SCRIPT_DIR"
nohup python3 server.py >> "$LOG_FILE" 2>&1 &
NEW_PID=$!

# 保存 PID
echo "$NEW_PID" > "$PID_FILE"

# 等待服务启动
sleep 3

# 检查服务是否正常启动
if kill -0 "$NEW_PID" 2>/dev/null; then
    echo "✅ 服务已启动 (PID: $NEW_PID)"
    echo "📜 日志文件：$LOG_FILE"
    echo "🔒 访问地址：https://$(hostname -I | awk '{print $1}')"
else
    echo "❌ 服务启动失败"
    rm -f "$PID_FILE"
    exit 1
fi
