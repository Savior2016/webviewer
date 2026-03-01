#!/bin/bash
# WebViewer 看门狗脚本
# 检测服务是否卡死并自动重启

LOG_FILE="/tmp/webviewer-watchdog.log"
PORT=443
CHECK_INTERVAL=60  # 每 60 秒检查一次
MAX_RESTARTS=3     # 最大重启次数
RESTART_WINDOW=300 # 5 分钟内最多重启 3 次

# 记录重启历史
RESTART_HISTORY_FILE="/tmp/webviewer-restarts.json"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# 检查服务是否在运行
check_process() {
    pgrep -f "python3 server.py" > /dev/null 2>&1
    return $?
}

# 检查服务是否响应
check_response() {
    curl -sk --max-time 5 https://localhost/ > /dev/null 2>&1
    return $?
}

# 记录重启
record_restart() {
    local now=$(date +%s)
    local history="[]"
    
    if [ -f "$RESTART_HISTORY_FILE" ]; then
        history=$(cat "$RESTART_HISTORY_FILE" 2>/dev/null || echo "[]")
    fi
    
    # 使用 Python 处理 JSON（更可靠）
    python3 << EOF
import json
import sys

try:
    with open('$RESTART_HISTORY_FILE', 'r') as f:
        history = json.load(f)
except:
    history = []

# 添加新记录
history.append($now)

# 只保留最近 5 分钟的记录
cutoff = $now - $RESTART_WINDOW
history = [t for t in history if t > cutoff]

with open('$RESTART_HISTORY_FILE', 'w') as f:
    json.dump(history, f)

print(len(history))
EOF
}

# 获取重启次数
get_restart_count() {
    local now=$(date +%s)
    python3 << EOF 2>/dev/null || echo "0"
import json
try:
    with open('$RESTART_HISTORY_FILE', 'r') as f:
        history = json.load(f)
    cutoff = $now - $RESTART_WINDOW
    recent = [t for t in history if t > cutoff]
    print(len(recent))
except:
    print("0")
EOF
}

# 重启服务
restart_service() {
    local count=$(get_restart_count)
    
    if [ "$count" -ge "$MAX_RESTARTS" ]; then
        log "❌ 5 分钟内已重启 $count 次，达到上限，跳过本次重启"
        return 1
    fi
    
    log "🔄 重启服务..."
    
    # 终止旧进程
    pkill -9 -f "python3 server.py" 2>/dev/null
    sleep 1
    
    # 启动新进程
    cd /root/.openclaw/workspace/webviewer
    nohup python3 server.py > /tmp/webviewer.log 2>&1 &
    local new_pid=$!
    
    sleep 2
    
    # 验证启动成功
    if check_process && check_response; then
        log "✅ 服务重启成功，PID: $new_pid"
        record_restart
        return 0
    else
        log "❌ 服务重启失败"
        return 1
    fi
}

# 主循环
log "🐕 WebViewer 看门狗启动"

while true; do
    # 检查进程是否存在
    if ! check_process; then
        log "⚠️  进程不存在，尝试重启"
        restart_service
        sleep $CHECK_INTERVAL
        continue
    fi
    
    # 检查服务是否响应
    if ! check_response; then
        log "⚠️  服务无响应，尝试重启"
        restart_service
        sleep $CHECK_INTERVAL
        continue
    fi
    
    # 服务正常
    sleep $CHECK_INTERVAL
done
