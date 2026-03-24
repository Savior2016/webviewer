# WebViewer 版本信息

## 当前版本
**v1.5.5** - 2026-03-24

## 更新日志

### v1.5.5 (2026-03-24) - 单元测试与一致性修复
🧪 全面单元测试 + 跨页面一致性修复

#### 测试体系
- ✅ 123 项单元测试 (后端 74 + 前端审计 32 + 一致性 17)
- ✅ pytest 测试基础架构 (conftest.py + fixtures)
- ✅ 4 个后端 Manager 模块完整覆盖
- ✅ 前端 onclick 处理函数审计

#### Bug 修复
- ✅ 修复 Momhand escapeHtml 缺失 (XSS 漏洞)
- ✅ 修复 Momhand 设置弹窗样式 (bg-white → glass-card)
- ✅ 修复 Siri Dream 缺少 DEFAULT_SYSTEM_PROMPT

#### 一致性改进
- ✅ 统一保存按钮文本为「💾 保存设置」
- ✅ 统一所有设置弹窗使用 glass-card 样式
- ✅ Siri Dream FAB 从 inline style 改用 CSS 类
- ✅ 移除 Cherry Pick/Momhand 重复的 transitions.css 引用

### v1.5.4 (2026-03-13) - 底部功能优化
🎨 优化首页底部功能布局

#### 界面优化
- ✅ 底部 4 个功能链接移到分割线以下
- ✅ 改为网格布局，每行 4 个排列
- ✅ 响应式设计，移动端自动适配

### v1.0.0 (2026-02-28) - 初始版本
🎉 WebViewer 项目正式发布

#### 核心功能
- ✅ WebViewer 服务 (server.py) - HTTPS 网站服务
- ✅ OpenClaw Agent 集成 - 智能消息处理
- ✅ 三个项目管理模块:
  - ✈️ By Design (已读不回) - 出行管理
  - 🏠 Cherry Pick (一搬不丢) - 搬家物品管理
  - 👋 Momhand (妈妈的手) - 物品位置管理
- ✅ 统一首页 (Dummy 的小弟) - 工具索引页
- ✅ systemd 服务配置 - 开机自启动

#### 技术栈
- Python 3 + asyncio
- HTTPS (自签名证书)
- OpenClaw Agent 集成
- TailwindCSS 前端

#### 文档
- README.md - 使用指南
- DESIGN.md - 设计文档
- SYSTEM_ARCHITECTURE.md - 系统架构
- 以及其他完整文档

---
*Powered by OpenClaw | Agent: Dummy 🧪*
