# WebViewer 发布说明 - v1.5.3

**发布日期**: 2026-03-02  
**版本**: v1.5.3  
**提交**: c57cfbb

---

## 📋 更新内容

### ✨ 新功能

- **更新系统提示词**
  - 更简洁专业的助手定位
  - 强调实际保存操作，不只返回 JSON
  - 优化提示词结构，更易读

### 🐛 Bug 修复

- **修复设置 API 绑定问题**
  - `handle_get_settings` 现在正确读取 `data/settings.json`
  - `handle_save_settings` 现在正确保存到 `data/settings.json`
  - 之前错误地使用了 Siri Dream 的配置文件

### 🔧 改进

- **页面设置完全绑定**
  - 页面设置模态框与 `data/settings.json` 完全绑定
  - 页面修改时直接修改配置文件
  - 恢复默认功能同步更新

---

## 📁 修改文件

| 文件 | 修改说明 |
|------|----------|
| `server.py` | 修复设置 API 使用正确的配置文件 |
| `www/index.html` | 更新默认提示词 + 版本信息 |
| `data/settings.json` | 新提示词配置 |
| `PROMPT_UPDATE_2026-03-02.md` | 修改记录文档 |

---

## 🧪 测试

### API 测试
```bash
# 获取提示词
curl -sk https://43.153.153.62/api/settings

# 保存提示词
curl -sk -X PUT https://43.153.153.62/api/settings \
  -H "Content-Type: application/json" \
  -d '{"system_prompt": "测试提示词"}'
```

### 页面测试
1. 访问 https://43.153.153.62/
2. 点击右上角 ⚙️ 设置按钮
3. 查看提示词是否正确显示
4. 修改提示词并保存
5. 刷新页面确认修改已持久化

---

## 📦 安装/更新

```bash
# 拉取最新代码
cd /root/.openclaw/workspace
git pull origin master

# 重启服务
pkill -9 -f "python3 server.py"
nohup python3 server.py > /tmp/webviewer.log 2>&1 &

# 验证服务
curl -sk https://43.153.153.62/api/settings
```

---

## 🔗 相关链接

- GitHub: https://github.com/Savior2016/webviewer
- 版本标签：v1.5.3
- 提交记录：c57cfbb

---

**发布完成** ✅
