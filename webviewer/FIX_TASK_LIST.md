# WebViewer 修复 Task List

## 🎯 目标
修复管理员登录和访客登录流程问题，确保登录后正确显示对应的功能按钮。

---

## 📋 任务列表

### 第一阶段：登录流程修复

#### 任务 1: 分析当前登录流程
- [ ] 1.1 确认登录页面代码（/login 路由）
- [ ] 1.2 确认登录 API 返回结构
- [ ] 1.3 确认 localStorage 设置时机

#### 任务 2: 修复管理员登录流程
- [ ] 2.1 管理员登录成功后设置 localStorage
- [ ] 2.2 跳转到工具箱页面后正确读取 localStorage
- [ ] 2.3 显示审计日志、待审批、退出登录按钮

#### 任务 3: 修复访客登录流程
- [ ] 3.1 访客申请提交后创建待审批记录
- [ ] 3.2 审批通过后设置 localStorage
- [ ] 3.3 显示退出登录按钮（不显示管理员功能）

#### 任务 4: 修复退出登录流程
- [ ] 4.1 清除 localStorage
- [ ] 4.2 清除 Cookie
- [ ] 4.3 重定向到登录页面

---

### 第二阶段：代码质量修复

#### 任务 5: 检查并修复 server_enhanced.py
- [ ] 5.1 检查所有未定义的方法调用
- [ ] 5.2 检查重复代码
- [ ] 5.3 检查错误处理

#### 任务 6: 检查并修复 www/index.html
- [ ] 6.1 检查 JavaScript 语法错误
- [ ] 6.2 检查 DOM 元素 ID 匹配
- [ ] 6.3 检查 CSS 类名

#### 任务 7: 添加缺失的方法
- [ ] 7.1 实现 send_feishu_approval 方法（或移除调用）
- [ ] 7.2 检查其他缺失的方法

---

### 第三阶段：测试验证

#### 任务 8: 测试管理员登录
- [ ] 8.1 管理员登录
- [ ] 8.2 验证底部显示 5 个按钮
- [ ] 8.3 验证退出登录功能

#### 任务 9: 测试访客登录
- [ ] 9.1 访客申请
- [ ] 9.2 管理员审批
- [ ] 9.3 验证底部显示 3 个按钮
- [ ] 9.4 验证退出登录功能

---

## 🔧 执行计划

### 步骤 1: 创建统一的登录状态管理
### 步骤 2: 简化 checkAdminAuth 逻辑
### 步骤 3: 添加调试日志
### 步骤 4: 测试验证

---

## 📝 备注

- 文件位置：
  - 服务器代码：`/root/.openclaw/workspace/webviewer/server_enhanced.py`
  - 工具箱页面：`/root/.openclaw/workspace/www/index.html`
  - 配置文件：`/root/.openclaw/workspace/webviewer/config.json`

- Cookie 名称：
  - 管理员：`wv_admin_session`
  - 访客：`wv_guest_session`

- localStorage 键名：
  - `wv_is_admin`
  - `wv_is_logged_in`

---

*创建时间：2026-03-14*
*状态：进行中*