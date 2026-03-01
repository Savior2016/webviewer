# WebViewer + OpenClaw Agent 集成指南

## 📋 当前状态

### ✅ 已完成
1. 创建了 webviewer agent 配置文件
2. 创建了 agent 处理器代码
3. 更新了 server.py 使用 agent 处理器

### ⚠️ 待解决
OpenClaw Agent 需要 Gateway 支持，当前配置还未生效。

---

## 🔧 配置步骤

### 方案 A: 使用 Gateway Agent（推荐）

#### 1. 创建 Agent 目录结构

```bash
mkdir -p ~/.openclaw/agents/webviewer/agent
```

#### 2. 创建 Agent 配置

```bash
cat > ~/.openclaw/agents/webviewer/agent/config.json << 'EOF'
{
  "name": "webviewer",
  "description": "WebViewer 消息处理助手",
  "system_prompt": "你是一个智能助手，帮助用户管理 webviewer 的三个项目...",
  "model": "default",
  "thinking": "minimal"
}
EOF
```

#### 3. 重启 Gateway

```bash
openclaw gateway restart
```

#### 4. 测试调用

```bash
openclaw agent --agent webviewer --message "我要出差 3 天" --json
```

---

### 方案 B: 使用 Local Fallback（当前可用）

由于 Gateway Agent 配置较复杂，当前使用 **本地引擎 Fallback** 方案。

**工作流程**:
```
Web 页面 → server.py → openclaw_agent_processor.py
                              ↓
                   尝试调用 OpenClaw Agent
                              ↓
                   失败（需要 Gateway）
                              ↓
                   Fallback 到本地引擎
                              ↓
                   message_engine 处理
                              ↓
                   返回结果
```

**优点**:
- ✅ 立即可用
- ✅ 快速可靠
- ✅ 不依赖 Gateway

**缺点**:
- ⚠️ 不是真正的 OpenClaw 处理
- ⚠️ 规则引擎不够智能

---

## 📊 测试结果

### 测试 1: 记录物品

**输入**: "帮我记一下，我的大疆 action4 放在了电视柜上面的透明箱子里"

**输出**:
```json
{
  "success": true,
  "project": "momhand",
  "action": "add_item",
  "message": "✅ 已记录物品位置\n\n📦 物品：大疆 action4\n📍 位置：电视柜上面的透明箱子里\n📂 类型：电子产品",
  "refresh": "/momhand/",
  "processed_by": "local_fallback",
  "note": "OpenClaw Agent 需要配置 session，当前使用本地引擎"
}
```

---

## 🎯 下一步

### 选项 1: 完成 Gateway Agent 配置

需要：
1. 创建正确的目录结构
2. 配置 agent config.json
3. 重启 Gateway
4. 测试调用

**优点**: 真正的 OpenClaw 处理，支持 LLM 理解

**缺点**: 配置复杂，需要 Gateway 支持

---

### 选项 2: 继续使用 Local Fallback

**现状**: 已经工作正常

**优点**: 
- 简单快速
- 不依赖外部服务
- 已经支持自然语言

**缺点**: 
- 规则引擎
- 不够灵活

---

### 选项 3: 混合方案

**简单消息** → 本地引擎（快速）
**复杂消息** → OpenClaw Agent（智能）

自动判断消息复杂度，选择合适的处理方式。

---

## 💡 建议

**当前阶段**: 使用 **方案 2 (Local Fallback)**
- 已经实现并测试通过
- 支持自然语言理解
- 快速可靠

**未来升级**: 配置 **Gateway Agent**
- 当需要更智能的理解时
- 当需要多轮对话时
- 当需要 LLM 能力时

---

## 📝 文件清单

```
webviewer/
├── openclaw_agent_processor.py    # Agent 处理器（含 fallback）
├── message_engine.py               # 本地消息引擎
├── server.py                       # Web 服务器
├── setup_agent.sh                  # Agent 配置脚本
├── agent/
│   └── webviewer-agent.md          # Agent 配置说明
└── docs/
    └── OPENCLAW_AGENT_SETUP.md     # 本文档
```

---

*更新时间：2026-02-27 13:50*
