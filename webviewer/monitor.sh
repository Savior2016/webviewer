#!/bin/bash
# WebViewer 服务监控脚本
# 功能：监控服务状态，崩溃时自动重启并记录日志

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/server.pid"
LOG_FILE="$SCRIPT_DIR/server.log"
CRASH_LOG="$SCRIPT_DIR/crash_history.log"
MONITOR_LOG="$SCRIPT_DIR/monitor.log"

# 服务启动脚本
START_SCRIPT="$SCRIPT_DIR/../start-webviewer.sh"

# 最大重启次数（防止无限重启循环）
MAX_RESTARTS=5
# 重启时间窗口（秒）
RESTART_WINDOW=300

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$MONITOR_LOG"
}

log_crash() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$CRASH_LOG"
}

# 检查服务是否在运行
check_service() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            return 0  # 服务正在运行
        else
            log "⚠️  PID 文件存在但进程不存在 (PID: $PID)"
            rm -f "$PID_FILE"
            return 1  # 服务已停止
        fi
    else
        return 1  # PID 文件不存在
    fi
}

# 获取进程运行时间
get_uptime() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            # 获取进程启动时间
            START_TIME=$(ps -o lstart= -p "$PID" 2>/dev/null)
            if [ -n "$START_TIME" ]; then
                START_EPOCH=$(date -d "$START_TIME" +%s 2>/dev/null)
                if [ -n "$START_EPOCH" ]; then
                    NOW_EPOCH=$(date +%s)
                    UPTIME=$((NOW_EPOCH - START_EPOCH))
                    echo "$UPTIME"
                    return
                fi
            fi
        fi
    fi
    echo "0"
}

# 收集崩溃信息
collect_crash_info() {
    local crash_time="$1"
    local uptime="$2"
    
    log_crash "=========================================="
    log_crash "崩溃时间：$crash_time"
    log_crash "运行时长：${uptime}秒"
    log_crash "------------------------------------------"
    
    # 记录最后的日志
    if [ -f "$LOG_FILE" ]; then
        log_crash "最后 50 行日志:"
        tail -50 "$LOG_FILE" >> "$CRASH_LOG"
    fi
    
    # 检查系统资源
    log_crash "------------------------------------------"
    log_crash "系统内存:"
    free -h >> "$CRASH_LOG" 2>/dev/null || echo "无法获取内存信息" >> "$CRASH_LOG"
    
    log_crash "------------------------------------------"
    log_crash "磁盘空间:"
    df -h "$SCRIPT_DIR" >> "$CRASH_LOG" 2>/dev/null || echo "无法获取磁盘信息" >> "$CRASH_LOG"
    
    # 检查是否有 OOM 记录
    log_crash "------------------------------------------"
    log_crash "OOM 检查:"
    dmesg 2>/dev/null | grep -i "killed\|oom" | tail -5 >> "$CRASH_LOG" || echo "无法检查 OOM" >> "$CRASH_LOG"
    
    log_crash "=========================================="
    log_crash ""
}

# 启动服务
start_service() {
    log "🚀 启动 WebViewer 服务..."
    cd "$SCRIPT_DIR"
    nohup python3 server_enhanced.py >> "$LOG_FILE" 2>&1 &
    NEW_PID=$!
    echo "$NEW_PID" > "$PID_FILE"
    sleep 3
    
    if kill -0 "$NEW_PID" 2>/dev/null; then
        log "✅ 服务已启动 (PID: $NEW_PID)"
        return 0
    else
        log "❌ 服务启动失败"
        rm -f "$PID_FILE"
        return 1
    fi
}

# 主监控循环
monitor_count=0
restart_count=0
last_restart_time=0

log "🔍 WebViewer 监控程序已启动"
log "📁 工作目录：$SCRIPT_DIR"
log "📊 监控间隔：30 秒"

while true; do
    monitor_count=$((monitor_count + 1))
    
    # 每 10 次检查输出一次状态（5 分钟）
    if [ $((monitor_count % 10)) -eq 0 ]; then
        uptime=$(get_uptime)
        uptime_min=$((uptime / 60))
        uptime_sec=$((uptime % 60))
        log "💓 心跳检查 #${monitor_count} - 服务运行时间：${uptime_min}分${uptime_sec}秒"
    fi
    
    if ! check_service; then
        crash_time=$(date '+%Y-%m-%d %H:%M:%S')
        uptime=$(get_uptime)
        
        log "❌ 检测到服务崩溃！"
        log_crash "服务崩溃 - $crash_time (运行 ${uptime}秒)"
        
        # 收集崩溃信息
        collect_crash_info "$crash_time" "$uptime"
        
        # 检查重启频率
        current_time=$(date +%s)
        if [ $((current_time - last_restart_time)) -lt $RESTART_WINDOW ]; then
            restart_count=$((restart_count + 1))
            if [ $restart_count -ge $MAX_RESTARTS ]; then
                log "⚠️ 在 ${RESTART_WINDOW}秒内已重启${MAX_RESTARTS}次，停止自动重启"
                log "🔔 请检查 $CRASH_LOG 文件分析崩溃原因"
                exit 1
            fi
        else
            restart_count=1
        fi
        last_restart_time=$current_time
        
        # 尝试重启
        log "🔄 尝试重启服务 (第${restart_count}次)..."
        if start_service; then
            log "✅ 服务重启成功"
        else
            log "❌ 服务重启失败，等待 60 秒后重试..."
            sleep 60
        fi
    fi
    
    sleep 30
done
