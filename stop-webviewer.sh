#!/bin/bash
# WebViewer 服务停止脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/server.pid"

# 检查 PID 文件
if [ ! -f "$PID_FILE" ]; then
    echo "⚠️  PID 文件不存在，尝试查找进程..."
    PID=$(pgrep -f "python3 server.py")
    if [ -z "$PID" ]; then
        echo "ℹ️  服务未运行"
        exit 0
    fi
else
    PID=$(cat "$PID_FILE")
fi

# 停止服务
if kill -0 "$PID" 2>/dev/null; then
    echo "🛑 停止服务 (PID: $PID)..."
    kill "$PID"
    sleep 2
    
    # 如果还在运行，强制停止
    if kill -0 "$PID" 2>/dev/null; then
        echo "⚠️  强制停止..."
        kill -9 "$PID"
    fi
    
    echo "✅ 服务已停止"
else
    echo "ℹ️  服务未运行"
fi

# 清理 PID 文件
rm -f "$PID_FILE"
