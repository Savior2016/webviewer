# WebViewer 修改记录 - 2026-03-14

## 修改目标

1. **账号密码登录流程**：从主页点击账号密码登录后，进入工具箱主页，并可通过底部入口进入审批页面
2. **访客登录流程**：从主页点击访客登录后，等待审批，不发送飞书通知

## 修改内容

### 1. server_enhanced.py

#### 1.1 添加审批状态检查 API (`/check-status/{approval_id}`)

在 `do_GET` 方法中添加了对 `/check-status/` 路径的处理：

```python
elif self.path.startswith('/check-status/'):
    # 访客等待审批状态检查 API
    self.handle_check_status()
    return
```

新增 `handle_check_status` 方法，用于访客等待页面轮询审批状态：

```python
def handle_check_status(self):
    """处理访客等待审批状态检查"""
    # 检查审批状态并返回 JSON 响应
    # 支持三种状态：pending, approved, rejected
```

#### 1.2 移除飞书通知

在访客登录流程中移除了飞书通知调用：

**修改前**：
```python
if not allowed:
    approval_record = data_manager.create_pending_approval(visitor_info)
    approval_id = approval_record['approval_id']
    FeishuNotifier.send_approval_request(visitor_info, approval_id)  # ❌ 移除
    self.show_waiting_page(approval_id)
    return
```

**修改后**：
```python
if not allowed:
    # 未授权，创建待审批并显示等待页面（不发送飞书通知）
    approval_record = data_manager.create_pending_approval(visitor_info)
    approval_id = approval_record['approval_id']
    # 访客登录不发送飞书通知，等待管理员审批即可
    self.show_waiting_page(approval_id)
    return
```

#### 1.3 优化等待审批页面

更新了 `show_waiting_page` 方法，增强了用户体验：

- 添加了审批超时处理（6 分钟后显示超时）
- 改进了状态显示（审批通过/拒绝/等待）
- 审批通过后自动跳转到工具箱主页 (`/www/`)
- 审批被拒绝时显示友好提示

### 2. www/index.html（工具箱主页）

#### 2.1 添加待审批入口

在底部导航中添加了"待审批"入口，仅管理员可见：

```html
<!-- 管理员专属功能 -->
<div class="grid grid-cols-2 gap-3 w-full" id="adminLinks">
  <a href="/audit" id="auditLink" class="hidden">
    <span class="text-2xl">📊</span>
    <span>审计日志</span>
  </a>
  <a href="/pending" id="pendingLink" class="hidden">
    <span class="text-2xl">⏳</span>
    <span>待审批</span>
  </a>
</div>
```

#### 2.2 更新 JavaScript 逻辑

修改了管理员权限检测逻辑，同时控制审计日志和待审批入口的显示：

```javascript
if (isAdmin) {
  // 管理员模式：显示审计和待审批
  if (auditLink) auditLink.classList.remove('hidden');
  if (pendingLink) pendingLink.classList.remove('hidden');
} else {
  // 访客模式：隐藏管理员功能
  if (adminLinks) adminLinks.classList.add('hidden');
}
```

## 用户流程

### 流程 1：管理员登录

1. 访问主页 (`/`)
2. 点击"管理员登录"悬浮球
3. 输入用户名和密码
4. 登录成功后重定向到工具箱主页 (`/www/`)
5. 底部导航显示"审计日志"和"待审批"入口
6. 可点击"待审批"查看和管理待审批请求

### 流程 2：访客登录

1. 访问主页 (`/`)
2. 点击"访客申请"悬浮球
3. 自动创建待审批记录并显示等待页面
4. **不发送飞书通知**，等待管理员主动审批
5. 每 5 秒轮询一次审批状态
6. 审批通过后自动跳转到工具箱主页
7. 审批被拒绝时显示拒绝提示

## 测试验证

```bash
# 验证服务运行
curl -k -s -o /dev/null -w "%{http_code}" https://127.0.0.1:443/
# 输出：200

# 验证登录页面
curl -k -s https://127.0.0.1:443/ | grep -o "管理员登录\|访客申请"
# 输出：管理员登录 \n 访客申请
```

## 文件清单

- ✅ `/root/.openclaw/workspace/webviewer/server_enhanced.py` - 主要服务器代码
- ✅ `/root/.openclaw/workspace/www/index.html` - 工具箱主页
- ✅ `/root/.openclaw/workspace/webviewer/MODIFICATIONS_20260314.md` - 修改记录（本文件）

## 注意事项

1. 访客登录不再发送飞书通知，需要管理员主动访问 `/pending` 页面查看待审批请求
2. 访客等待页面最多轮询 6 分钟（72 次 × 5 秒），超时后显示超时提示
3. 管理员会话有效期为 12 小时，访客会话有效期为 24 小时
4. 所有修改已生效，服务运行正常

## 修复记录 - 2026-03-14 10:57

### 问题
用户反馈登录后仍然显示"等待审批"页面

### 原因
`/www/` 路径只检查访客会话 (`wv_session`)，但管理员登录后设置的是管理员会话 (`wv_admin_session`)

### 修复
修改 `/www/` 路径处理逻辑，优先检查管理员会话：

```python
# 优先检查管理员会话
if self.check_admin_auth()[0]:
    # 管理员直接放行
    pass  # 继续向下执行，提供静态文件
else:
    # 非管理员，检查访客会话
    allowed, session_id, visitor_info = self.check_access()
    if not allowed:
        self.show_waiting_page(approval_id)
        return
```

### 验证
- ✅ 主页正常显示登录选项
- ✅ 管理员登录后正常访问工具箱
- ✅ 访客申请后显示等待页面

## 新增功能 - 2026-03-14 11:44

### 退出登录功能

#### 修改内容
在工具箱主页 (`www/index.html`) 底部导航添加"退出登录"按钮：

- 🚪 **退出登录** - 仅管理员可见，点击后清除会话并返回登录页

#### 布局调整
管理员底部导航从 2 列改为 3 列：
```
[📊 审计日志] [⏳ 待审批] [🚪 退出登录]
```

#### 已有退出登录的页面
- ✅ 审计日志页面 (`/audit`) - 顶部导航
- ✅ 待审批页面 (`/pending`) - 顶部导航
- ✅ 工具箱主页 (`/www/`) - 底部导航（新增）

#### 登出流程
1. 点击"退出登录"
2. 清除管理员会话 Cookie
3. 重定向到登录页面 (`/login`)

### 验证
```bash
# 工具箱主页退出登录按钮
curl -k -s https://127.0.0.1:443/www/ | grep "退出登录"
# 输出：退出登录

# 登出接口测试
curl -k -s -o /dev/null -w "%{http_code}" https://127.0.0.1:443/logout
# 输出：302 (重定向到登录页)
```
