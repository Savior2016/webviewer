# WebViewer 开发规范 Skill

## 🎯 技能描述

WebViewer 开发规范，确保在添加新功能或修改时不会破坏现有功能。

**位置**: `~/.openclaw/workspace/skills/webviewer/SKILL.md`  
**版本**: v1.0  
**适用**: 所有 WebViewer 相关修改

---

## 📋 开发前必读

### 1. 阅读架构文档

在修改任何代码前，**必须**先阅读：
- `/root/.openclaw/workspace/docs/WEBVIEWER_ARCHITECTURE.md`

了解：
- 整体架构
- 四个核心模块功能
- 数据路径和存储方式
- API 设计规范

### 2. 检查现有功能

修改前检查：
```bash
# 查看相关模块代码
grep -rn "模块名" /root/.openclaw/workspace/

# 测试现有 API
curl -sk https://43.153.153.62/模块/api/端点

# 检查前端页面
curl -sk https://43.153.153.62/模块/ | grep -o "<title>.*</title>"
```

---

## 🔧 修改规范

### 1. 数据路径规范

**✅ 正确**:
```python
# 新模块使用 data/ 根目录
DATA_DIR = Path("/root/.openclaw/workspace/data/模块名")

# Momhand 使用特定路径
DB_FILE = Path("/root/.openclaw/workspace/webviewer/data/momhand.db")
```

**❌ 错误**:
```python
# 不要创建新的子目录
DATA_DIR = Path("/root/.openclaw/workspace/新模块/data")  # 错误！

# 不要混用路径
DB_FILE = Path("/root/.openclaw/workspace/data/momhand.db")  # 错误！
```

### 2. API 设计规范

**统一返回格式**:
```python
# 成功
{
    "success": True,
    "data": {...},  # 或 message, result 等
}

# 失败
{
    "success": False,
    "error": "错误信息"
}
```

**必须添加的 HTTP 头**:
```python
self.send_header("Content-Type", "application/json; charset=utf-8")
self.send_header("Access-Control-Allow-Origin", "*")
self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
```

**路由注册**:
```python
# 在 server.py 的 do_GET 和 do_POST 中添加路由
elif path.startswith("/新模块/api/"):
    self.handle_新模块_api(path, query)
```

### 3. 前端修改规范

**返回首页链接**:
```html
<!-- ✅ 正确：使用绝对 URL -->
<a href="https://43.153.153.62/">返回首页</a>

<!-- ❌ 错误：相对路径 -->
<a href="/">返回首页</a>
```

**颜色主题**（参考现有模块）:
```css
/* By Design - 蓝色 */
--from: #3b82f6; --to: #06b6d4;

/* Cherry Pick - 紫色 */
--from: #8b5cf6; --to: #ec4899;

/* Momhand - 绿色 */
--from: #10b981; --to: #3b82f6;

/* Siri 的尉来 - 蓝紫 */
--from: #3b82f6; --to: #9333ea;
```

### 4. 异步处理规范

**后台任务必须**:
```python
# 1. 使用 daemon 线程
thread = threading.Thread(target=func, args=(...), daemon=True)

# 2. 添加超时保护
result = subprocess.run(cmd, timeout=90)

# 3. 异常处理
try:
    ...
except subprocess.TimeoutExpired:
    manager['update_status'](id, 'failed', {"error": "处理超时"})
except Exception as e:
    manager['update_status'](id, 'failed', {"error": str(e)})
```

---

## 🧪 测试清单

### 修改后必须测试

- [ ] 服务能否正常启动
- [ ] 首页能否访问
- [ ] 修改的模块能否访问
- [ ] 其他三个模块是否正常
- [ ] API 端点是否正常
- [ ] 返回首页链接是否有效
- [ ] 数据是否正确保存
- [ ] 查看日志是否有错误

### 测试命令

```bash
# 1. 重启服务
pkill -9 -f "python3 server.py"
cd /root/.openclaw/workspace
nohup python3 server.py > /tmp/webviewer.log 2>&1 &
sleep 5

# 2. 检查服务
ps aux | grep "python3 server.py"
netstat -tlnp | grep 443

# 3. 测试所有模块
curl -sk https://43.153.153.62/ | grep "<title>"
curl -sk https://43.153.153.62/bydesign/ | grep "<title>"
curl -sk https://43.153.153.62/cherry-pick/ | grep "<title>"
curl -sk https://43.153.153.62/momhand/ | grep "<title>"
curl -sk https://43.153.153.62/siri-dream/ | grep "<title>"

# 4. 检查日志
tail -20 /tmp/webviewer.log
```

---

## 📝 提交规范

### Git Commit 格式

```
<类型>(<模块>): <描述>

详细说明（可选）

影响范围:
- 修改的文件
- 影响的功能
```

**类型**:
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建/工具

**示例**:
```bash
feat(siri-dream): 添加 POST 查询 message_id 功能

- 支持使用 POST + message_id 查询处理结果
- 统一 API 设计，不需要区分 GET/POST

影响范围:
- server.py - 添加 handle_siri_dream_query 函数
- www/siri-dream/index.html - 更新 API 文档
```

### 发布版本

```bash
# 1. 提交代码
git add -A
git commit -m "..."

# 2. 推送到远程
git push origin master

# 3. 创建版本标签
git tag -a v1.x.x -m "版本说明"
git push origin v1.x.x
```

---

## ⚠️ 常见错误

### 1. 数据路径错误

**现象**: 数据保存了但页面看不到

**原因**: 路径不一致

**解决**: 检查 manager 中的路径定义

### 2. 返回首页失效

**现象**: 点击返回首页 404

**原因**: 使用相对路径

**解决**: 使用绝对 URL `https://43.153.153.62/`

### 3. API 路由冲突

**现象**: API 返回 404 或错误结果

**原因**: 路由顺序错误或路径重叠

**解决**: 检查 server.py 中的路由顺序，确保具体路径在前

### 4. 服务卡死

**现象**: 进程在但不响应请求

**原因**: 单线程阻塞或死锁

**解决**: 
- 使用 ThreadingMixIn
- 后台任务使用 daemon 线程
- 添加超时保护
- 重启服务

---

## 📚 参考文档

- `docs/WEBVIEWER_ARCHITECTURE.md` - 完整架构文档
- `server.py` - 主服务器代码
- `www/js/agent-chat.js` - 共享组件
- 各模块 manager 文件

---

## 🆘 遇到问题

1. **先查日志**: `tail -f /tmp/webviewer.log`
2. **再查架构**: `docs/WEBVIEWER_ARCHITECTURE.md`
3. **测试 API**: 使用 curl 测试各端点
4. **回滚**: 如果修改导致问题，使用 git 回滚

```bash
# 查看修改历史
git log --oneline -10

# 回滚到上一个版本
git revert HEAD
```

---

**记住**: 每次修改都可能影响其他功能，务必仔细测试！
