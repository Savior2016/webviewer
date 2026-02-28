# WebViewer 修改保护技能

> ⚠️ **重要**: 修改 WebViewer 项目前必须阅读此技能和架构文档，确保不破坏已有功能。

**技能版本**: 1.0  
**创建时间**: 2026-02-28  
**最后更新**: 2026-02-28  
**关联文档**: `/root/.openclaw/workspace/webviewer/WEBVIEWER_COMPLETE_ARCHITECTURE.md`

---

## 触发条件

当用户要求修改 WebViewer 项目时，自动激活此技能。

**触发关键词**:
- "修改 webviewer"
- "更新 webviewer"
- "添加功能到 webviewer"
- "修复 webviewer"
- "webviewer bug"
- "webviewer 项目"

---

## 核心原则

### 1. 先读文档，再动手

**必须首先读取**:
```bash
read /root/.openclaw/workspace/webviewer/WEBVIEWER_COMPLETE_ARCHITECTURE.md
```

**重点检查**:
- ⚠️ 历史问题记录（特别是 `do_PUT` 重复定义问题）
- API 端点列表
- 数据流图
- 修改检查清单

---

### 2. 禁止重复定义方法

**⚠️ 血泪教训**: 2026-02-28 曾因 `server.py` 中 `do_PUT` 方法重复定义，导致 Cherry Pick 位置更新失败。

**修改 `server.py` 前必须检查**:
```bash
# 检查方法定义数量
grep -n "def do_PUT" /root/.openclaw/workspace/webviewer/server.py
# 应该只输出一行

grep -n "def do_POST" /root/.openclaw/workspace/webviewer/server.py
# 应该只输出一行

grep -n "def do_DELETE" /root/.openclaw/workspace/webviewer/server.py
# 应该只输出一行
```

**正确做法**:
```python
# ✅ 所有 PUT 路由合并到一个方法
def do_PUT(self):
    if path.startswith("/cherry-pick/api/items/"):
        self.handle_cherry_pick_put(path, data)
    elif path.startswith("/bydesign/api/"):
        self.handle_bydesign_put(path, data)
    elif path.startswith("/api/prompts/"):
        self.handle_save_prompt(path, data)
    elif path == "/api/settings":
        self.handle_save_settings(data)
    else:
        self.send_response(404)
```

---

### 3. 修改后必须测试

**测试清单**:

#### Cherry Pick (关键！)
```bash
# 1. 创建搬家活动
curl -k -X POST https://localhost/cherry-pick/api/moves \
  -H "Content-Type: application/json" \
  -d '{"name":"测试搬家"}'

# 2. 添加物品
curl -k -X POST https://localhost/cherry-pick/api/moves/{moveId}/items \
  -H "Content-Type: application/json" \
  -d '{"name":"测试物品"}'

# 3. 更新打包前位置 (曾失败的功能！)
curl -k -X PUT https://localhost/cherry-pick/api/items/{itemId} \
  -H "Content-Type: application/json" \
  -d '{"before_location":"书房"}'
# 预期：{"success": true}

# 4. 更新打包后位置
curl -k -X PUT https://localhost/cherry-pick/api/items/{itemId} \
  -H "Content-Type: application/json" \
  -d '{"pack_location":"纸箱 1"}'
# 预期：{"success": true}

# 5. 更新拆封后位置（会同步到 Momhand）
curl -k -X PUT https://localhost/cherry-pick/api/items/{itemId} \
  -H "Content-Type: application/json" \
  -d '{"after_location":"新家书房"}'
# 预期：{"success": true}
```

#### Momhand
```bash
# 添加物品
curl -k -X POST https://localhost/momhand/api/items \
  -H "Content-Type: application/json" \
  -d '{"name":"测试物品","type":"测试","location":"测试位置"}'

# 搜索物品
curl -k "https://localhost/momhand/api/search?q=测试"

# 获取统计
curl -k https://localhost/momhand/api/stats
```

#### By Design
```bash
# 创建出行
curl -k -X POST https://localhost/bydesign/api/trips \
  -H "Content-Type: application/json" \
  -d '{"name":"测试出行","description":"测试"}'

# 获取检查清单
curl -k https://localhost/bydesign/api/checklist
```

---

## 项目结构

```
webviewer/
├── server.py                          # ⚠️ 主服务器 (40.8KB) - 修改需谨慎
├── bydesign_manager.py                # By Design 管理器
├── cherry_pick_manager.py             # Cherry Pick 管理器
├── momhand_manager_db.py              # Momhand 管理器 (SQLite)
├── openclaw_agent_processor.py        # OpenClaw AI 处理器
│
├── www/                               # 前端页面
│   ├── index.html                     # 首页
│   ├── bydesign/index.html            # 已读不回
│   ├── cherry-pick/index.html         # 一搬不丢
│   └── momhand/index.html             # 妈妈的手
│
├── data/                              # 数据存储
│   ├── bydesign/checklist.json        # 检查清单
│   ├── bydesign/trips.json            # 出行记录
│   ├── cherry-pick/moves.json         # 搬家数据
│   ├── momhand.db                     # SQLite 数据库
│   └── results/                       # AI 处理结果
│
└── WEBVIEWER_COMPLETE_ARCHITECTURE.md # 📋 完整架构文档
```

---

## 三个应用概述

### 1. 已读不回 (By Design)

**路径**: `/bydesign/`  
**口号**: 出远门前读了这个，就不需要单独返回  
**用途**: 出行检查清单管理

**核心功能**:
- 通用检查清单（关窗、断电、锁门...）
- 单次出行记录
- 进度追踪
- 自定义物品添加

**数据存储**: JSON 文件

---

### 2. 一搬不丢 (Cherry Pick)

**路径**: `/cherry-pick/`  
**口号**: 一直搬家，东西也不会弄丢  
**用途**: 搬家物品追踪

**核心功能**:
- 搬家活动管理
- 物品三位置记录（打包前/打包后/拆封后）
- 状态标记
- 自动同步到 Momhand ⚠️

**数据存储**: JSON 文件

**⚠️ 特别注意**:
- `update_item` 方法必须能正确处理三个位置字段
- `after_location` 更新时会触发同步到 Momhand
- 2026-02-28 曾发生 PUT 路由失效问题

---

### 3. 妈妈的手 (Momhand)

**路径**: `/momhand/`  
**口号**: "你这孩子，这不就在电视柜上嘛！"  
**用途**: 物品全生命周期管理

**核心功能**:
- 物品记录（名称、类型、位置、用途...）
- 搜索功能
- 分类筛选
- 过期提醒
- 统计信息

**数据存储**: SQLite 数据库

---

## 数据流

### AI 消息处理流程

```
用户输入 → POST /api/send-message
              ↓
    server.py (handle_send_message)
              ↓
    openclaw_agent_processor.py
              ↓
    OpenClaw Agent (理解意图)
              ↓
    返回：{project, action, data}
              ↓
    server.py (execute_save_action)
              ↓
    调用对应 manager.add_item()
              ↓
    保存到数据库
              ↓
    返回结果给前端
              ↓
    显示结果 + 跳转页面
```

---

## 常见修改场景

### 场景 1: 添加新的 API 端点

**步骤**:
1. 在 `server.py` 的对应 HTTP 方法中添加路由
2. 创建对应的 handler 方法
3. 在管理器中添加业务逻辑
4. 测试现有 API 不受影响

**示例** (添加 GET 端点):
```python
def do_GET(self):
    # ... 现有路由 ...
    
    # 新增路由
    elif path.startswith("/new-api/"):
        self.handle_new_api(path)
```

---

### 场景 2: 修改数据结构

**步骤**:
1. 备份现有数据文件
2. 修改管理器的数据结构
3. 添加数据迁移逻辑（如需要）
4. 更新前端显示逻辑
5. 全面测试

**⚠️ 警告**: 修改 JSON 结构前务必备份！

---

### 场景 3: 添加新功能模块

**步骤**:
1. 创建新的管理器类（参考现有管理器）
2. 在 `server.py` 添加 API 路由
3. 创建前端页面（参考现有页面）
4. 在首页添加入口
5. 测试所有功能

---

## 调试技巧

### 查看日志

```bash
# 查看 server.py 日志
tail -f /tmp/webviewer.log

# 查看实时请求
journalctl -f -u webviewer  # 如果是 systemd 服务
```

### 测试 API

```bash
# 使用 curl 测试
curl -k https://localhost/cherry-pick/api/moves

# 查看返回的 JSON
curl -k https://localhost/cherry-pick/api/moves | python3 -m json.tool
```

### 检查服务状态

```bash
# 检查进程
ps aux | grep "python3 server.py"

# 检查端口
netstat -tlnp | grep 443

# 重启服务
pkill -f "python3 server.py"
cd /root/.openclaw/workspace/webviewer && python3 server.py &
```

---

## 故障排除

### 问题 1: PUT 请求返回 404

**可能原因**: `do_PUT` 方法中没有对应的路由

**解决**:
```python
# 检查 server.py 中的 do_PUT 方法
grep -A 20 "def do_PUT" /root/.openclaw/workspace/webviewer/server.py

# 确保包含所有路由
if path.startswith("/cherry-pick/api/items/"):
    self.handle_cherry_pick_put(path, data)
```

---

### 问题 2: 数据保存失败

**可能原因**:
- 文件权限问题
- JSON 格式错误
- 数据库锁死

**解决**:
```bash
# 检查文件权限
ls -la /root/.openclaw/workspace/webviewer/data/

# 检查 JSON 文件
python3 -m json.tool /root/.openclaw/workspace/webviewer/data/cherry-pick/moves.json

# 检查数据库
sqlite3 /root/.openclaw/workspace/webviewer/data/momhand.db ".tables"
```

---

### 问题 3: AI 消息处理失败

**可能原因**:
- OpenClaw Agent 未响应
- JSON 解析失败
- 超时

**解决**:
```bash
# 测试 OpenClaw
openclaw agent --agent main -m "测试"

# 查看处理器日志
cat /root/.openclaw/workspace/webviewer/data/results/*.json | tail
```

---

## 修改检查清单

在提交任何修改前，请确认：

- [ ] 已读取 `WEBVIEWER_COMPLETE_ARCHITECTURE.md`
- [ ] 已检查 `server.py` 中没有重复的方法定义
- [ ] 已备份数据文件（`data/` 目录）
- [ ] 已测试 Cherry Pick 位置更新功能
- [ ] 已测试 Momhand 物品添加功能
- [ ] 已测试 By Design 出行创建功能
- [ ] 已测试 AI 消息处理功能
- [ ] 已更新本文档（如有架构变更）

---

## 联系与支持

如遇问题，请参考：
- 完整架构文档：`WEBVIEWER_COMPLETE_ARCHITECTURE.md`
- 项目总结：`PROJECTS.md`
- 系统架构：`SYSTEM_ARCHITECTURE.md`

---

*技能结束 - 修改前必读*
