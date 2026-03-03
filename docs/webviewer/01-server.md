# 01 - 主服务器 (server.py)

## 功能概述

WebViewer 的核心 HTTPS 服务器，提供：
- 多模块 Web 应用托管
- API 路由分发
- 异步消息处理
- 日志记录系统

**文件**: `/root/.openclaw/workspace/server.py`
**行数**: 1473 行
**版本**: v1.5.3

---

## 架构设计

### 技术栈
- **Python 3** + `http.server` + `ssl`
- **ThreadingHTTPServer** - 并发请求支持
- **ThreadPoolExecutor** - 后台任务池（5 worker, 10 队列）
- **logging** - 统一日志系统

### 核心配置
```python
PORT = 443
WEB_ROOT = "/root/.openclaw/workspace/www"
THREAD_POOL = ThreadPoolExecutor(max_workers=5)
REQUEST_TIMEOUT = 30 秒
BACKGROUND_TASK_TIMEOUT = 60 秒
LOG_FILE = "server.log"
MAX_LOG_LINES = 500
```

---

## API 路由

### GET 路由
| 路径 | 处理函数 | 说明 |
|------|----------|------|
| `/` | `serve_static_file` | 主页 |
| `/api/settings` | `handle_get_settings` | 获取设置 |
| `/api/logs` | `handle_get_logs` | 获取运行日志 |
| `/api/message-result?msg_id=xxx` | `handle_message_result` | 查询消息处理结果 |
| `/momhand/api/*` | `handle_momhand_api` | Momhand API |
| `/cherry-pick/api/*` | `handle_cherry_pick_api` | Cherry Pick API |
| `/bydesign/api/*` | `handle_bydesign_api` | By Design API |
| `/siri-dream/api/*` | `handle_siri_dream_api` | Siri Dream API |

### POST 路由
| 路径 | 处理函数 | 说明 |
|------|----------|------|
| `/api/send-message` | `handle_send_message` | 发送消息（异步处理） |
| `/siri-dream/api/message` | `handle_siri_dream_message` | Siri Dream 消息 |
| `/momhand/api/items` | `handle_momhand_post` | 添加物品 |
| `/cherry-pick/api/moves/{id}/items` | `handle_cherry_pick_post` | 添加搬家物品 |
| `/bydesign/api/trips` | `handle_bydesign_post` | 创建出行 |

---

## 核心函数

### 1. 消息处理流程

```python
def do_POST(self):
    """
    POST 请求入口
    1. 解析请求体
    2. 路由到对应处理函数
    3. 立即返回 + 后台异步处理
    """
```

### 2. 异步消息处理

```python
def handle_send_message(self, data):
    """
    处理用户消息
    1. 生成 msg_id (UUID)
    2. 立即返回 {success: true, processing: true, msg_id: xxx}
    3. 线程池提交 _process_message_async
    """
    
def _process_message_async(self, msg_id: str, message: str):
    """
    后台处理消息（线程池运行）
    1. 调用 openclaw_agent_processor
    2. 保存结果到 data/results/{msg_id}.json
    3. 执行保存操作（write to DB/JSON）
    """
```

### 3. 日志系统

```python
# 日志配置（第 29-39 行）
LOG_FILE = "server.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# API: GET /api/logs?lines=100
def handle_get_logs(self, query):
    """返回最后 N 行日志（JSON 格式）"""
```

### 4. 项目保存执行器

```python
def execute_project_save(project: str, result: dict):
    """
    根据 AI 返回的 project/action 执行数据保存
    
    支持项目:
    - bydesign: 创建出行、添加检查项
    - cherry_pick: 记录搬家物品
    - momhand: 添加物品
    """
```

---

## 数据流

### 消息处理流程
```
用户发送消息
    ↓
POST /api/send-message
    ↓
生成 msg_id，立即返回
    ↓
线程池异步处理
    ↓
调用 OpenClaw Agent
    ↓
解析 JSON 结果
    ↓
保存结果到 data/results/{msg_id}.json
    ↓
执行项目保存（写入数据库/文件）
    ↓
前端轮询 /api/message-result?msg_id=xxx
```

### 日志记录点
- ✅ 服务启动/停止
- ✅ 每个请求（时间、IP、路径、状态码）
- ✅ 消息提交线程池
- ✅ OpenClaw 处理完成/失败
- ✅ 项目保存操作
- ✅ API 错误

---

## 并发控制

### 线程池配置
```python
executor = ThreadPoolExecutor(
    max_workers=5,           # 最大 5 个 worker
    thread_name_prefix="webviewer-worker"
)
```

### 超时保护
- **请求超时**: 30 秒（`REQUEST_TIMEOUT`）
- **后台任务超时**: 60 秒（`BACKGROUND_TASK_TIMEOUT`）
- **OpenClaw 命令超时**: 30 秒（`subprocess.run(timeout=30)`）

---

## 错误处理

### 全局异常捕获
每个处理函数都包含：
```python
try:
    # 业务逻辑
except Exception as e:
    logger.error(f"错误：{e}")
    traceback.print_exc()
    # 返回 500 + 错误信息
```

### 超时处理
```python
except FuturesTimeoutError:
    logger.info(f"❌ 后台处理超时 {msg_id}")
    self._save_error_result(msg_id, message, "处理超时")
```

---

## 启动/停止

### 启动
```bash
./start-webviewer.sh
# 或
nohup python3 server.py > /tmp/webviewer.log 2>&1 &
```

### 停止
```bash
./stop-webviewer.sh
# 或
kill $(cat server.pid)
```

### 启动输出
```
🔒 WebViewer HTTPS 服务已启动（修复版）：https://0.0.0.0:443
📂 网站根目录：/root/.openclaw/workspace/www
🧵 线程池：最大 5 worker，队列 10 任务
⏱️  请求超时：30 秒
```

---

## 相关文件

| 文件 | 说明 |
|------|------|
| `server.py` | 主服务器 |
| `server.log` | 运行日志 |
| `server.pid` | 进程 ID |
| `start-webviewer.sh` | 启动脚本 |
| `stop-webviewer.sh` | 停止脚本 |
| `openclaw_agent_processor.py` | Agent 调用桥接 |

---

## 常见问题

### Q: 服务自动退出怎么办？
A: 查看 `server.log` 最后 100 行，搜索 `ERROR` 或 `❌`

### Q: 如何查看实时日志？
A: 
```bash
tail -f /root/.openclaw/workspace/server.log
# 或访问主页 → 底部「运行日志」按钮
```

### Q: 请求超时怎么调整？
A: 修改 `server.py` 第 36 行：
```python
REQUEST_TIMEOUT = 60  # 改为 60 秒
```

---

*最后更新：2026-03-02*
