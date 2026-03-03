# WebViewer 安全配置指南

## 🔒 已实施的安全措施

### 1. 速率限制 (Rate Limiting)
- **默认**: 每个 IP 每分钟最多 100 个请求
- **配置位置**: `server.py` 第 47-48 行
```python
RATE_LIMIT_REQUESTS = 100  # 每分钟最大请求数
RATE_LIMIT_WINDOW = 60     # 时间窗口（秒）
```

### 2. CORS 来源验证
- **允许的域名**: 只允许特定域名访问 API
- **配置位置**: `server.py` 第 38-42 行
```python
ALLOWED_ORIGINS = [
    'https://43.153.153.62',
    'https://localhost',
    'https://127.0.0.1',
]
```

### 3. IP 白名单 (可选)
- **状态**: 默认关闭
- **启用方法**: 编辑 `server.py` 第 45-50 行
```python
IP_WHITELIST = [
    '223.104.40.171',  # 添加允许的 IP
]
ENABLE_IP_WHITELIST = True  # 设为 True 启用
```

### 4. API Token 认证 (可选)
- **状态**: 默认关闭
- **启用方法**: 编辑 `server.py` 第 52-57 行
```python
API_TOKENS = {
    'your-secret-token-here': 'admin',  # 添加 Token
}
ENABLE_TOKEN_AUTH = True  # 设为 True 启用
```

### 5. TLS/SSL 加密
- **最低版本**: TLS 1.2
- **密码套件**: 仅允许强加密算法
```python
TLS_MIN_VERSION = ssl.TLSVersion.TLSv1_2
TLS_CIPHERS = 'ECDHE+AESGCM:DHE+AESGCM:ECDHE+CHACHA20:DHE+CHACHA20'
```

### 6. 安全响应头
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`

### 7. 请求日志审计
- 所有 API 访问都会记录到日志
- 安全事件（速率限制、认证失败等）会特别标记

## 🛡️ 推荐的安全配置

### 生产环境配置

1. **启用 IP 白名单**（如果访问 IP 固定）
```python
IP_WHITELIST = ['你的固定 IP']
ENABLE_IP_WHITELIST = True
```

2. **启用 Token 认证**（推荐）
```python
API_TOKENS = {
    '生成一个强随机 Token': 'admin',
}
ENABLE_TOKEN_AUTH = True
```

3. **降低速率限制**（如果正常访问不多）
```python
RATE_LIMIT_REQUESTS = 60   # 每分钟 60 次
RATE_LIMIT_WINDOW = 60
```

4. **添加更多敏感路径**
```python
SENSITIVE_PATHS = [
    '/api/settings',
    '/api/prompts/',
    '/api/logs',
    '/momhand/api/',      # 物品管理
    '/cherry-pick/api/',  # 搬家管理
    '/bydesign/api/',     # 出行管理
]
```

## 📊 安全监控

### 查看安全日志
```bash
# 查看最近的安全事件
grep "🔒 安全事件" /root/.openclaw/workspace/server.log | tail -50

# 查看被拒绝的请求
grep "403\|401\|429" /root/.openclaw/workspace/server.log | tail -50

# 实时监控
tail -f /root/.openclaw/workspace/server.log | grep "🔒"
```

### 常见安全事件类型
- `RATE_LIMIT`: 请求过于频繁
- `IP_BLOCKED`: IP 不在白名单
- `AUTH_FAILED`: Token 验证失败
- `INVALID_ORIGIN`: 来源未授权

## 🔑 使用 Token 认证

启用 Token 认证后，访问 API 需要在请求头中添加：

```bash
# curl 示例
curl -sk https://43.153.153.62/api/settings \
  -H "Authorization: Bearer your-secret-token-here"

# JavaScript 示例
fetch('/api/settings', {
  headers: {
    'Authorization': 'Bearer your-secret-token-here'
  }
})
```

## 🚨 应急响应

### 如果发现恶意攻击

1. **立即启用 IP 白名单**，只允许信任的 IP
2. **降低速率限制**到更严格的值（如每分钟 20 次）
3. **启用 Token 认证**
4. **查看日志**分析攻击来源
5. **考虑使用防火墙**在系统层面封禁 IP

### 使用防火墙封禁 IP
```bash
# 使用 iptables 封禁 IP
iptables -A INPUT -s 恶意 IP -j DROP

# 永久封禁（添加到规则文件）
iptables-save > /etc/iptables/rules.v4
```

## 📝 更新历史

- **2026-03-03**: 添加完整安全配置
  - 速率限制
  - IP 白名单
  - Token 认证
  - 安全响应头
  - TLS 强化

---

**注意**: 修改配置后需要重启服务才能生效：
```bash
pkill -9 -f "python3 server.py"
cd /root/.openclaw/workspace
nohup python3 server.py > /tmp/webviewer.log 2>&1 &
```
