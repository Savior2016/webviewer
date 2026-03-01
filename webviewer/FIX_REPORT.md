# WebViewer 服务卡死问题修复报告

## 📋 问题描述

WebViewer 服务运行约 8-10 小时后会自动卡死，表现为：
- 进程仍在运行（PID 存在）
- 端口 443 仍在监听
- 但无法响应任何 HTTP 请求
- curl 请求超时（error 28）

## 🔍 根本原因分析

### 1. **单线程 HTTP 服务器**
原代码使用 `http.server.HTTPServer`，默认是**同步单线程**模型：
```python
# 原代码
httpd = socketserver.TCPServer(("", PORT), WebViewerHandler)
```

问题：一次只能处理一个请求，如果某个请求阻塞，整个服务器就卡死。

### 2. **无限制的后台线程**
每次 `/api/send-message` 请求都会创建一个新的 `threading.Thread`：
```python
# 原代码
thread = threading.Thread(target=self._process_message_async, args=(msg_id, message), daemon=True)
thread.start()
```

问题：
- 没有线程池限制，大量并发请求会创建数百个线程
- 线程耗尽系统资源（内存、文件描述符）
- 线程竞争 SQLite 数据库锁

### 3. **SQLite 并发锁问题**
momhand/cherry_pick/bydesign 的 manager 都使用 SQLite：
```python
conn = sqlite3.connect(DB_FILE)
```

问题：
- SQLite 默认使用文件锁
- 多个线程同时写入时会产生锁等待
- 没有超时机制，可能无限期等待

### 4. **没有请求超时保护**
- HTTP 请求没有超时限制
- 后台任务没有超时限制
- 一旦某个操作卡住，永远无法恢复

## ✅ 修复方案

### 1. 使用 ThreadingMixIn 支持并发
```python
class TimeoutHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True
    request_queue_size = 20
    timeout = 30  # 套接字超时
```

改进：
- 每个请求一个独立线程
- 请求队列限制为 20
- 套接字超时 30 秒

### 2. 使用线程池限制后台任务
```python
from concurrent.futures import ThreadPoolExecutor

# 最大 5 个 worker 线程，防止资源耗尽
executor = ThreadPoolExecutor(max_workers=5, thread_name_prefix="webviewer-worker")

# 使用线程池提交任务
future = executor.submit(self._process_message_async, msg_id, message)
```

改进：
- 限制最多 5 个并发后台任务
- 超出任务进入队列等待
- 避免线程爆炸

### 3. 添加超时保护
```python
REQUEST_TIMEOUT = 30
BACKGROUND_TASK_TIMEOUT = 60

class WebViewerHandler(http.server.BaseHTTPRequestHandler):
    timeout = REQUEST_TIMEOUT
```

改进：
- HTTP 请求 30 秒超时
- 后台任务 60 秒超时
- 超时时自动终止并记录错误

### 4. 添加看门狗自动重启
创建 `watchdog.sh` 脚本：
- 每 60 秒检查服务是否响应
- 检测到卡死自动重启
- 限制 5 分钟内最多重启 3 次（防止重启循环）

## 📦 部署内容

### 修改的文件
1. `/root/.openclaw/workspace/webviewer/server.py` - 修复版主服务器
2. `/root/.openclaw/workspace/webviewer/server.py.bak` - 原文件备份

### 新增的文件
1. `/root/.openclaw/workspace/webviewer/watchdog.sh` - 看门狗脚本
2. `/root/.openclaw/workspace/webviewer/server_fixed.py` - 修复版副本（已部署）

### 日志文件
- `/tmp/webviewer.log` - 主服务日志
- `/tmp/webviewer-watchdog.log` - 看门狗日志
- `/tmp/webviewer-restarts.json` - 重启历史记录

## 🚀 验证方法

### 1. 检查服务状态
```bash
# 查看进程
ps aux | grep "python3 server.py"

# 测试响应
curl -sk --max-time 5 https://localhost/

# 查看日志
tail -f /tmp/webviewer.log
```

### 2. 压力测试
```bash
# 并发发送 10 个请求
for i in {1..10}; do
    curl -sk https://localhost/api/settings &
done
wait

# 应该所有请求都成功返回
```

### 3. 监控看门狗
```bash
# 查看看门狗状态
tail -f /tmp/webviewer-watchdog.log

# 查看重启历史
cat /tmp/webviewer-restarts.json
```

## 📊 预期效果

| 指标 | 修复前 | 修复后 |
|------|--------|--------|
| 并发请求 | 1 个 | 20 个队列 |
| 后台线程 | 无限制 | 最多 5 个 |
| 请求超时 | 无 | 30 秒 |
| 后台任务超时 | 无 | 60 秒 |
| 自动恢复 | ❌ 需手动重启 | ✅ 看门狗自动重启 |
| 平均无故障时间 | ~8 小时 | 显著提升 |

## 🔧 后续优化建议

1. **数据库连接池** - 使用 SQLite WAL 模式提升并发
2. **异步框架** - 考虑迁移到 FastAPI + uvicorn
3. **健康检查端点** - 添加 `/health` API 用于监控
4. **指标收集** - 记录请求延迟、错误率等指标
5. **日志轮转** - 防止日志文件过大

## 📝 部署时间

2026-03-01 08:11

## 👤 部署者

Friday (AI Assistant)
