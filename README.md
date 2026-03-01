# WebViewer - 智能生活管理 Web 系统

<div align="center">

![Version](https://img.shields.io/badge/version-1.2.8-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.11+-orange.svg)

**三个生活管理工具的统一 Web 平台**

[English](README_EN.md) | 简体中文

</div>

---

## 📖 项目简介

WebViewer 是一个集成了三个生活管理工具的 HTTPS Web 服务平台，提供精美的卡片式界面和智能消息处理能力。

### 🎯 三大核心应用

| 应用 | 名称 | 用途 | 访问路径 |
|------|------|------|----------|
| ✈️ **By Design** | 已读不回 | 出远门前的检查清单管理 | `/bydesign/` |
| 🏠 **Cherry Pick** | 一搬不丢 | 搬家物品追踪系统 | `/cherry-pick/` |
| 📦 **Momhand** | 妈妈的手 | 个人物品位置管理 | `/momhand/` |

---

## 🚀 快速开始

### 环境要求

- Python 3.11+
- OpenSSL（用于 HTTPS 证书）
- 现代浏览器（Chrome/Firefox/Safari）

### 安装步骤

```bash
# 1. 克隆项目
git clone git@github.com:Savior2016/webviewer.git
cd webviewer

# 2. 安装依赖（如有）
pip install -r requirements.txt

# 3. 生成自签名证书（首次运行）
openssl req -x509 -newkey rsa:4096 -keyout selfsigned.key -out selfsigned.crt -days 365 -nodes

# 4. 启动服务
python3 server.py
```

### 访问服务

- **首页**: `https://localhost/` 或 `https://<你的 IP>/`
- **By Design**: `https://localhost/bydesign/`
- **Cherry Pick**: `https://localhost/cherry-pick/`
- **Momhand**: `https://localhost/momhand/`

> ⚠️ **注意**: 使用自签名证书时，浏览器会显示安全警告，点击"继续访问"即可。

---

## 📱 功能特性

### ✈️ By Design - 出行检查清单

**适用场景**: 出差、旅行、回老家等需要离家数天的情况

**核心功能**:
- ✅ 通用检查清单：每次出行都要做的待办事项（关窗、断电、锁门等）
- ✅ 单次出行记录：特别携带的物品和单次事项
- ✅ 进度追踪：实时显示完成进度百分比
- ✅ 易于核对：逐项勾选，完成出行准备
- ✅ 模板系统：快速创建标准化出行清单

**API 示例**:
```bash
# 创建出行记录
curl -X POST https://localhost/bydesign/api/trips \
  -H "Content-Type: application/json" \
  -d '{"name": "北京出差", "description": "3 天会议"}'

# 获取检查清单
curl https://localhost/bydesign/api/checklist

# 添加检查项
curl -X POST https://localhost/bydesign/api/checklist \
  -H "Content-Type: application/json" \
  -d '{"text": "关闭总电源"}'
```

---

### 🏠 Cherry Pick - 搬家物品管理

**适用场景**: 搬家时记录和追踪所有物品的位置变化

**核心功能**:
- ✅ 创建搬家活动：记录每次搬家事件
- ✅ 物品追踪：名称、原位置、新位置、打包位置
- ✅ 放置确认：标记物品是否已放置到新位置
- ✅ 自动同步：已放置物品自动同步到 Momhand 系统
- ✅ 状态统计：实时显示打包和放置进度

**API 示例**:
```bash
# 创建搬家活动
curl -X POST https://localhost/cherry-pick/api/moves \
  -H "Content-Type: application/json" \
  -d '{"name": "搬家到望京", "description": "2026 年春节搬家"}'

# 添加物品
curl -X POST https://localhost/cherry-pick/api/moves/{moveId}/items \
  -H "Content-Type: application/json" \
  -d '{"name": "书籍", "before_location": "书房书架", "after_location": "新家书架"}'
```

---

### 📦 Momhand - 物品位置管理

**适用场景**: 记录和查找家中物品的位置，避免找不到东西

**核心功能**:
- ✅ 物品登记：名称、类型、位置、用途
- ✅ 快速搜索：按关键词查找物品
- ✅ 分类统计：按类型查看物品分布
- ✅ 过期提醒：支持记录有效期，提前提醒
- ✅ 智能推荐：根据历史记录推荐存放位置

**API 示例**:
```bash
# 添加物品
curl -X POST https://localhost/momhand/api/items \
  -H "Content-Type: application/json" \
  -d '{"name": "感冒药", "type": "药品", "location": "客厅药箱", "usage": "感冒时服用"}'

# 搜索物品
curl "https://localhost/momhand/api/search?q=感冒药"

# 获取统计信息
curl https://localhost/momhand/api/stats
```

---

## 🔧 技术架构

### 系统架构

```
┌─────────────────┐
│   Web 浏览器     │
│  (HTTPS 访问)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   server.py     │  ← HTTPS 服务器 (Port 443)
│  (ThreadingMixIn)│
└────────┬────────┘
         │
    ┌────┴────┬────────────┬──────────┐
    ▼         ▼            ▼          ▼
┌────────┐ ┌──────────┐ ┌───────┐ ┌──────────┐
│ByDesign│ │CherryPick│ │Momhand│ │OpenClaw  │
│Manager │ │ Manager  │ │Manager│ │Processor │
└────┬───┘ └────┬─────┘ └───┬───┘ └────┬─────┘
     │          │           │          │
     ▼          ▼           ▼          ▼
┌─────────────────────────────────────────┐
│          data/ (JSON + SQLite)          │
└─────────────────────────────────────────┘
```

### 技术栈

- **后端**: Python 3.11+
  - `http.server` + `ThreadingMixIn` - 并发 HTTP 服务器
  - `ThreadPoolExecutor` - 后台任务线程池
  - `sqlite3` - 轻量级数据库
  - `requests` - HTTP 客户端

- **前端**: 
  - HTML5 + CSS3 + JavaScript (原生)
  - TailwindCSS - 样式框架
  - Fetch API - 异步请求

- **安全**:
  - HTTPS (TLS/SSL)
  - 自签名证书
  - 请求超时保护
  - 线程池资源限制

### 性能特性

- ✅ **并发支持**: ThreadingMixIn 实现多线程请求处理
- ✅ **资源限制**: 线程池限制最多 5 个并发后台任务
- ✅ **超时保护**: HTTP 请求 30 秒超时，后台任务 60 秒超时
- ✅ **自动恢复**: 看门狗脚本自动检测并重启卡死服务
- ✅ **稳定性**: 修复了单线程服务器卡死问题 (v1.2.8)

---

## 📂 项目结构

```
webviewer/
├── server.py                  # HTTPS 主服务器 (v1.2.8 修复版)
├── watchdog.sh                # 看门狗监控脚本
├── .env.example               # 环境变量配置示例
├── .gitignore                 # Git 忽略规则
│
├── # 核心管理器
├── bydesign_manager.py        # By Design 出行管理器
├── cherry_pick_manager.py     # Cherry Pick 搬家管理器
├── momhand_manager_db.py      # Momhand 物品管理器 (SQLite)
│
├── # OpenClaw 集成
├── openclaw_agent_processor.py # OpenClaw Agent 处理器
├── message_engine.py          # 消息处理引擎
├── message_processor.py       # 消息处理器
│
├── # Web 界面
├── www/
│   ├── index.html             # 首页 - Dummy 的小弟（工具索引）
│   ├── bydesign/
│   │   └── index.html         # By Design 页面
│   ├── cherry-pick/
│   │   └── index.html         # Cherry Pick 页面
│   ├── momhand/
│   │   └── index.html         # Momhand 页面
│   └── js/
│       └── agent-chat.js      # Agent 聊天组件
│
├── # 数据存储
├── data/
│   ├── bydesign/              # 出行数据
│   │   ├── checklist.json     # 检查清单
│   │   ├── trips.json         # 出行记录
│   │   └── templates.json     # 模板
│   ├── cherry-pick/           # 搬家数据
│   │   └── moves.json         # 搬家活动
│   ├── results/               # 消息处理结果
│   └── settings.json          # 系统设置
│
└── # 文档
├── README.md                  # 中文文档（本文件）
├── README_EN.md               # English documentation
├── FIX_REPORT.md              # v1.2.8 修复报告
├── SYSTEM_ARCHITECTURE.md     # 系统架构文档
├── DESIGN.md                  # 设计文档
└── VERSION.md                 # 版本信息
```

---

## 🔐 安全配置

### 环境变量

敏感配置应通过环境变量设置，不要硬编码在代码中：

```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env 文件（不要提交到 Git！）
vim .env
```

### Feishu API 配置（可选）

如需集成飞书消息通知：

```bash
export FEISHU_APP_ID="your_app_id"
export FEISHU_APP_SECRET="your_app_secret"
```

> ⚠️ **重要**: `.env` 文件已添加到 `.gitignore`，不会被提交到 Git。

### SSL 证书

项目使用自签名证书，生产环境建议：

1. 使用 Let's Encrypt 免费证书
2. 或使用商业 SSL 证书
3. 定期更新证书（建议每年）

生成新证书：
```bash
openssl req -x509 -newkey rsa:4096 -keyout server.key -out server.crt -days 365 -nodes
```

---

## 🐛 故障排查

### 服务无法访问

```bash
# 1. 检查进程
ps aux | grep "python3 server.py"

# 2. 检查端口
netstat -tlnp | grep 443

# 3. 查看日志
tail -f /tmp/webviewer.log

# 4. 测试连接
curl -sk https://localhost/
```

### 服务卡死无响应

```bash
# 看门狗会自动检测并重启
tail -f /tmp/webviewer-watchdog.log

# 手动重启
pkill -9 -f "python3 server.py"
cd /root/.openclaw/workspace/webviewer
nohup python3 server.py > /tmp/webviewer.log 2>&1 &
```

### 证书过期

```bash
# 重新生成证书
openssl req -x509 -newkey rsa:4096 -keyout selfsigned.key -out selfsigned.crt -days 365 -nodes

# 重启服务
pkill -9 -f "python3 server.py"
python3 server.py
```

---

## 📊 版本历史

### v1.2.8 (2026-03-01) - 稳定性修复 🛠️
- 🔧 使用 ThreadingMixIn 支持并发 HTTP 请求
- 🧵 线程池限制后台任务（最多 5 个并发）
- ⏱️ 添加请求超时保护（30 秒）
- 🐕 自动看门狗监控和重启
- 📊 详细修复文档

### v1.2.7 (2026-02-28) - UI 优化
- 修复悬浮窗被背景虚化层影响
- 减少玻璃卡片模糊度

### v1.2.6 (2026-02-27) - 消息系统
- 修复消息重复问题
- 优化模糊效果

### v1.0.0 (2026-02-26) - 初始发布 🎉
- WebViewer 服务正式发布
- 三个核心应用上线
- OpenClaw Agent 集成

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 📞 联系方式

- **GitHub**: https://github.com/Savior2016/webviewer
- **Issues**: https://github.com/Savior2016/webviewer/issues

---

<div align="center">

**Made with ❤️ by OpenClaw Community**

[返回顶部](#webviewer---智能生活管理-web-系统)

</div>
