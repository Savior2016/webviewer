#!/bin/bash
# WebViewer 快速诊断脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/server.log"
CRASH_LOG="$SCRIPT_DIR/crash_history.log"

echo "======================================"
echo "🔍 WebViewer 服务诊断报告"
echo "生成时间：$(date '+%Y-%m-%d %H:%M:%S')"
echo "======================================"
echo ""

# 1. 服务状态
echo "📊 服务状态:"
if [ -f "$SCRIPT_DIR/server.pid" ]; then
    PID=$(cat "$SCRIPT_DIR/server.pid")
    if kill -0 "$PID" 2>/dev/null; then
        echo "  ✅ 服务运行中 (PID: $PID)"
        UPTIME=$(ps -o lstart= -p "$PID" 2>/dev/null)
        echo "  启动时间：$UPTIME"
    else
        echo "  ❌ 服务已停止 (PID 文件存在但进程不存在)"
    fi
else
    echo "  ❌ 服务未运行 (无 PID 文件)"
fi
echo ""

# 2. 系统资源
echo "💾 系统资源:"
echo "  内存使用:"
free -h 2>/dev/null | grep -E "Mem|Swap" | sed 's/^/    /' || echo "    无法获取"
echo ""
echo "  磁盘空间:"
df -h "$SCRIPT_DIR" 2>/dev/null | tail -1 | sed 's/^/    /' || echo "    无法获取"
echo ""

# 3. 最后日志
echo "📝 最后日志 (最后 20 行):"
if [ -f "$LOG_FILE" ]; then
    tail -20 "$LOG_FILE" | sed 's/^/    /'
else
    echo "    日志文件不存在"
fi
echo ""

# 4. 崩溃历史
echo "💥 崩溃历史:"
if [ -f "$CRASH_LOG" ] && [ -s "$CRASH_LOG" ]; then
    CRASH_COUNT=$(grep -c "崩溃时间" "$CRASH_LOG" 2>/dev/null || echo "0")
    echo "  崩溃次数：$CRASH_COUNT"
    echo ""
    echo "  最近崩溃记录:"
    grep -A 5 "崩溃时间" "$CRASH_LOG" | tail -20 | sed 's/^/    /'
else
    echo "  无崩溃记录"
fi
echo ""

# 5. 端口占用
echo "🔌 端口占用 (443):"
netstat -tlnp 2>/dev/null | grep ":443" | sed 's/^/    /' || echo "    无法检查或无占用"
echo ""

# 6. 建议
echo "💡 建议:"
if [ -f "$CRASH_LOG" ] && [ -s "$CRASH_LOG" ]; then
    if grep -q "OOM\|killed" "$CRASH_LOG" 2>/dev/null; then
        echo "  ⚠️  检测到 OOM 记录，可能是内存不足导致崩溃"
        echo "  建议：增加系统内存或减少并发连接数"
    fi
    if grep -q "Address already in use" "$CRASH_LOG" 2>/dev/null; then
        echo "  ⚠️  端口被占用，可能有多个实例在运行"
        echo "  建议：pkill -f server_enhanced.py 然后重启"
    fi
else
    echo "  暂无特别建议"
fi
echo ""
echo "======================================"
echo "📁 日志文件位置:"
echo "  服务日志：$LOG_FILE"
echo "  崩溃记录：$CRASH_LOG"
echo "  监控日志：$SCRIPT_DIR/monitor.log"
echo "======================================"
