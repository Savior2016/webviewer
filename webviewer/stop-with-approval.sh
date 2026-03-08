#!/bin/bash
# WebViewer 停止脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/server.pid"

if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "🛑 正在停止服务 (PID: $OLD_PID)..."
        kill "$OLD_PID"
        sleep 2
        if kill -0 "$OLD_PID" 2>/dev/null; then
            echo "⚠️  强制终止..."
            kill -9 "$OLD_PID"
        fi
        rm -f "$PID_FILE"
        echo "✅ 服务已停止"
    else
        echo "⚠️  服务未运行（PID 文件存在但进程不存在）"
        rm -f "$PID_FILE"
    fi
else
    echo "ℹ️  未找到 PID 文件，服务可能未启动"
    # 尝试杀死可能的进程
    pkill -f "server_with_approval.py" 2>/dev/null && echo "✅ 已清理残留进程" || echo "ℹ️  无残留进程"
fi
