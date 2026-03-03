# WebViewer 项目文档计划

## 📋 总览

WebViewer 是一个基于 Python HTTPS 服务器的多模块 Web 应用平台，集成多个子项目管理功能。

**主入口**: `server.py` (1470+ 行)
**端口**: 443 (HTTPS)
**版本**: v1.5.3

---

## 🗂️ 项目结构

```
/root/.openclaw/workspace/
├── server.py                      # 主服务器 (核心)
├── www/                           # 主网站前端
│   ├── index.html                 # 主页面
│   ├── momhand/                   # 物品管理模块
│   ├── cherry-pick/               # 搬家管理模块
│   ├── bydesign/                  # 出行清单模块
│   ├── siri-dream/                # AI 消息处理模块
│   └── siri-dream/                # Siri 的梦模块
├── momhand/                       # Momhand 独立模块
│   ├── web_server.py              # 独立服务器
│   ├── momhand_api.py             # API 接口
│   └── skills/item_manager.py     # 物品管理技能
├── data/                          # 数据存储
│   ├── momhand/items.json         # 物品数据
│   ├── cherry-pick/moves.json     # 搬家数据
│   ├── bydesign/                  # 出行数据
│   └── siri-dream/messages.json   # 消息历史
└── docs/webviewer/                # 本文档目录
```

---

## 📚 文档计划

### 核心模块

| 序号 | 模块 | 文件 | 复杂度 | 优先级 | 状态 |
|------|------|------|--------|--------|------|
| 1 | 主服务器 | `server.py` | ⭐⭐⭐⭐⭐ | P0 | 待创建 |
| 2 | OpenClaw 处理器 | `openclaw_agent_processor.py` | ⭐⭐⭐⭐ | P0 | 待创建 |
| 3 | 消息引擎 | `message_engine.py` | ⭐⭐⭐⭐ | P1 | 待创建 |

### 子项目模块

| 序号 | 模块 | 文件 | 复杂度 | 优先级 | 状态 |
|------|------|------|--------|--------|------|
| 4 | Momhand 管理器 | `momhand_manager_db.py` | ⭐⭐⭐⭐ | P0 | 待创建 |
| 5 | Cherry Pick 管理器 | `cherry_pick_manager.py` | ⭐⭐⭐ | P1 | 待创建 |
| 6 | By Design 管理器 | `bydesign_manager.py` | ⭐⭐⭐ | P1 | 待创建 |
| 7 | Siri Dream 管理器 | `siri_dream_manager.py` | ⭐⭐⭐ | P1 | 待创建 |

### 前端模块

| 序号 | 模块 | 文件 | 复杂度 | 优先级 | 状态 |
|------|------|------|--------|--------|------|
| 8 | 主页面 | `www/index.html` | ⭐⭐⭐⭐ | P1 | 待创建 |
| 9 | Momhand Web | `www/momhand/index.html` | ⭐⭐⭐ | P2 | 待创建 |
| 10 | Cherry Pick Web | `www/cherry-pick/index.html` | ⭐⭐⭐ | P2 | 待创建 |
| 11 | By Design Web | `www/bydesign/index.html` | ⭐⭐⭐ | P2 | 待创建 |
| 12 | Siri Dream Web | `www/siri-dream/index.html` | ⭐⭐⭐ | P2 | 待创建 |

### 辅助模块

| 序号 | 模块 | 文件 | 复杂度 | 优先级 | 状态 |
|------|------|------|--------|--------|------|
| 13 | 日志系统 | `server.log` + API | ⭐⭐ | P2 | 待创建 |
| 14 | 启动脚本 | `start-webviewer.sh` | ⭐ | P3 | 待创建 |
| 15 | 数据格式 | `data/**/*.json` | ⭐⭐ | P2 | 待创建 |

---

## 🎯 文档模板

每个模块文档包含以下章节:

```markdown
# 模块名称

## 功能概述
- 核心职责
- 使用场景

## 文件结构
```

## API 接口
- 端点列表
- 请求/响应格式

## 核心函数
- 函数签名
- 参数说明
- 返回值

## 数据格式
- JSON 结构
- 字段说明

## 调用流程
- 时序图/流程图

## 常见问题
- FAQ

## 相关模块
- 依赖关系

```

---

## 📅 执行计划

### 第一阶段：核心模块 (P0) ✅ 100%
1. ✅ 主服务器 `server.py` - HTTP 服务器架构、路由、日志
2. ✅ OpenClaw 处理器 - Agent 调用桥接
3. ✅ Momhand 管理器 - 物品管理核心

### 第二阶段：业务模块 (P1) ✅ 100%
4. ✅ 消息引擎 - 消息处理流程
5. ✅ Cherry Pick 管理器 - 搬家记录
6. ✅ By Design 管理器 - 出行清单
7. ✅ Siri Dream 管理器 - AI 消息

### 第三阶段：前端模块 (P2) 🔄 50%
8. ✅ 主页面 - UI 架构、聊天界面
9. ⬜ 各子项目前端页面（By Design/Cherry Pick/Momhand/Siri Dream）

### 第四阶段：辅助模块 (P3) ⬜ 0%
10. ⬜ 日志系统、启动脚本、数据格式

---

## 🔗 索引

- [主服务器文档](./01-server.md)
- [OpenClaw 处理器](./02-openclaw-processor.md)
- [Momhand 管理器](./03-momhand-manager.md)
- [Cherry Pick 管理器](./04-cherry-pick-manager.md)
- [By Design 管理器](./05-bydesign-manager.md)
- [Siri Dream 管理器](./06-siri-dream-manager.md)
- [消息引擎](./07-message-engine.md)
- [主页面 UI](./08-main-ui.md)

---

*最后更新：2026-03-02*
