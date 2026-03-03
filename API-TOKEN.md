# WebViewer API Token 使用说明

## 🔑 你的 API Token

```
c0d5c26dc1d8eceff90020d8c00f2d1d
```

**⚠️ 重要**: 请妥善保管此 Token，不要泄露给他人！

---

## 📋 如何使用

### 1. curl 命令

```bash
# 访问 API 时添加 Authorization 头
curl -sk https://43.153.153.62/api/logs \
  -H "Authorization: Bearer c0d5c26dc1d8eceff90020d8c00f2d1d"

# 示例：获取物品列表
curl -sk https://43.153.153.62/momhand/api/items \
  -H "Authorization: Bearer c0d5c26dc1d8eceff90020d8c00f2d1d"

# 示例：获取出行清单
curl -sk https://43.153.153.62/bydesign/api/checklist \
  -H "Authorization: Bearer c0d5c26dc1d8eceff90020d8c00f2d1d"
```

### 2. JavaScript / 前端

```javascript
// 在 fetch 请求中添加 Token
const response = await fetch('https://43.153.153.62/api/logs', {
  headers: {
    'Authorization': 'Bearer c0d5c26dc1d8eceff90020d8c00f2d1d'
  }
});

// 或者使用 axios
axios.get('/api/logs', {
  headers: {
    'Authorization': 'Bearer c0d5c26dc1d8eceff90020d8c00f2d1d'
  }
});
```

### 3. Python

```python
import requests

headers = {
    'Authorization': 'Bearer c0d5c26dc1d8eceff90020d8c00f2d1d'
}

response = requests.get('https://43.153.153.62/api/logs', headers=headers)
```

---

## 🛡️ 安全保护范围

以下路径需要 Token 认证：
- ✅ `/api/*` - 所有系统 API
- ✅ `/momhand/api/*` - 物品管理 API
- ✅ `/cherry-pick/api/*` - 搬家管理 API
- ✅ `/bydesign/api/*` - 出行管理 API
- ✅ `/siri-dream/api/*` - 消息处理 API

以下路径**不需要** Token（公开访问）：
- 🌐 网页界面（`/`, `/momhand/`, `/cherry-pick/` 等）
- 🌐 静态资源（CSS, JS, 图片等）

---

## 🔄 更换 Token

如果需要更换 Token：

1. 生成新 Token：
```bash
openssl rand -hex 16
```

2. 编辑 `server.py` 第 52-56 行：
```python
API_TOKENS = {
    '新的 token': 'admin',
}
```

3. 重启服务：
```bash
pkill -9 -f "python3 server.py"
cd /root/.openclaw/workspace
nohup python3 server.py > /tmp/webviewer.log 2>&1 &
```

---

## 📊 访问日志

查看 API 访问记录：
```bash
# 查看所有 API 访问
grep "📝 API 访问" /root/.openclaw/workspace/server.log

# 查看认证失败的请求
grep "AUTH_FAILED" /root/.openclaw/workspace/server.log

# 实时监控
tail -f /root/.openclaw/workspace/server.log | grep "API"
```

---

## ⚠️ 常见问题

### Q: 忘记 Token 怎么办？
A: 查看 `server.py` 文件中的 `API_TOKENS` 配置

### Q: Token 泄露了怎么办？
A: 立即更换新 Token（见上方"更换 Token"部分）

### Q: 可以添加多个 Token 吗？
A: 可以，在 `API_TOKENS` 中添加多个键值对：
```python
API_TOKENS = {
    'token1': 'admin',
    'token2': 'user1',
    'token3': 'user2',
}
```

---

**最后更新**: 2026-03-03
