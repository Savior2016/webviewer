# WebViewer Version Skill

## 用途

当用户修改 webviewer 代码后，自动检测并询问是否要 commit 并更新版本信息。

## 触发条件

- 用户提到修改了 webviewer 代码
- 用户提到更新了 webviewer
- 用户提到 webviewer 有改动
- 检测到 webviewer 目录下的文件被修改

## 执行步骤

### 1. 检查 git 状态

```bash
cd /root/.openclaw/workspace
git status webviewer/
```

### 2. 如果有未提交的更改

询问用户：

> 检测到 webviewer 有未提交的更改，是否要：
> 1. Commit 并更新版本信息
> 2. 只 Commit 不更新版本
> 3. 暂不处理

### 3. 如果用户选择更新版本

#### a. 读取当前版本号

```bash
cd /root/.openclaw/workspace/webviewer/www
grep -o 'v[0-9]\+\.[0-9]\+\.[0-9]\+' index.html | head -1
```

#### b. 计算新版本号

- 如果是新功能 → 更新次版本号 (v1.0.0 → v1.1.0)
- 如果是 bug 修复 → 更新修订号 (v1.0.0 → v1.0.1)
- 如果是重大更新 → 更新主版本号 (v1.0.0 → v2.0.0)

#### c. 更新 index.html 中的版本号

使用 `edit` 工具更新：
- 版本显示标签
- Footer 中的版本
- 更新日志部分（添加新的版本记录）

#### d. Commit 代码

```bash
cd /root/.openclaw/workspace
git add webviewer/
git commit -m "feat: v1.X.X - 更新说明"
```

或者使用 `exec` 工具执行。

### 4. 重启 WebViewer 服务（可选）

如果用户确认，重启服务使更改生效：

```bash
pkill -f "python3.*server.py"
sleep 2
nohup /usr/bin/python3 /root/.openclaw/workspace/webviewer/server.py > /tmp/webviewer.log 2>&1 &
```

## 版本号规则

遵循语义化版本 (SemVer)：

- **主版本号 (Major)**: 不兼容的 API 修改
- **次版本号 (Minor)**: 向下兼容的功能性新增
- **修订号 (Patch)**: 向下兼容的问题修正

格式：`v主版本号。次版本号.修订号`

示例：
- `v1.0.0` → 初始版本
- `v1.1.0` → 新增功能
- `v1.1.1` → Bug 修复
- `v2.0.0` → 重大更新

## 更新日志格式

在版本模态框中添加新版本记录：

```html
<div class="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-4 border border-purple-100">
  <div class="flex items-center gap-2 mb-2">
    <span class="text-lg">🎉</span>
    <span class="font-semibold text-purple-800">v1.1.0</span>
    <span class="text-xs text-purple-600 bg-purple-100 px-2 py-0.5 rounded-full">2026-02-28</span>
  </div>
  <p class="text-sm text-purple-700 mb-3">简短描述</p>
  <ul class="text-xs text-purple-600 space-y-1">
    <li>✅ 功能 1</li>
    <li>✅ 功能 2</li>
  </ul>
</div>
```

## 注意事项

1. 始终先询问用户，不要自动 commit
2. 版本号更新需要用户确认
3. 更新日志要简洁明了
4. Commit message 要描述清楚变更内容
5. 提醒用户刷新页面查看新版本

## 示例对话

**用户**: 我刚刚修改了 webviewer 的提示词

**助手**: 检测到 webviewer 有未提交的更改，是否要 commit 并更新版本信息？

当前更改:
- www/index.html (提示词更新)

请选择:
1. ✅ Commit 并更新版本 (v1.0.0 → v1.1.0)
2. 📝 只 Commit 不更新版本
3. ⏸️ 暂不处理

---

**用户**: 更新版本

**助手**: 好的，正在更新版本到 v1.1.0...

✅ 已更新 index.html 中的版本号
✅ 已添加更新日志
✅ 已提交代码：feat: v1.1.0 - 支持页面设置提示词

是否要重启 WebViewer 服务使更改生效？
