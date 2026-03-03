# WebViewer 测试 Skill

## 🎯 技能描述

WebViewer 项目修改后的自动化测试流程，确保每次代码修改后功能正常。

**位置**: `~/.openclaw/workspace/skills/webviewer-test/SKILL.md`  
**版本**: v1.0  
**触发**: 每次修改 webviewer 相关代码后自动执行

---

## 📋 测试清单

### 1. 模块页面层级检查 ✅

```bash
# 检查所有模块页面是否存在且可访问
curl -sk https://localhost/ | grep -o "<title>.*</title>"
curl -sk https://localhost/bydesign/ | grep -o "<title>.*</title>"
curl -sk https://localhost/cherry-pick/ | grep -o "<title>.*</title>"
curl -sk https://localhost/momhand/ | grep -o "<title>.*</title>"
curl -sk https://localhost/siri-dream/ | grep -o "<title>.*</title>"
```

**预期**:
- 首页：包含"报告中心"或"WebViewer"
- By Design：包含"出行清单"
- Cherry Pick：包含"搬家管理"
- Momhand：包含"物品管理"
- Siri Dream：包含"AI 消息"

---

### 2. 数据存储方式检查 ✅

```bash
# 检查各模块数据文件
ls -la /root/.openclaw/workspace/data/momhand.db
ls -la /root/.openclaw/workspace/data/bydesign/
ls -la /root/.openclaw/workspace/data/cherry-pick/
ls -la /root/.openclaw/workspace/data/siri-dream/messages.json

# 检查模块设置文件
cat /root/.openclaw/workspace/www/bydesign/data/settings.json
cat /root/.openclaw/workspace/www/cherry-pick/data/settings.json
cat /root/.openclaw/workspace/www/momhand/data/settings.json
cat /root/.openclaw/workspace/data/siri-dream/settings.json
```

**要求**:
- Momhand 使用 SQLite 数据库
- By Design 使用 JSON 文件
- Cherry Pick 使用 JSON 文件
- Siri Dream 使用 JSON 文件
- 每个模块有独立的设置文件

---

### 3. 系统提示词分离检查 ✅

```bash
# 验证提示词存储位置
echo "=== By Design ==="
cat /root/.openclaw/workspace/www/bydesign/data/settings.json | jq .system_prompt

echo "=== Cherry Pick ==="
cat /root/.openclaw/workspace/www/cherry-pick/data/settings.json | jq .system_prompt

echo "=== Momhand ==="
cat /root/.openclaw/workspace/www/momhand/data/settings.json | jq .system_prompt

echo "=== Siri Dream ==="
cat /root/.openclaw/workspace/data/siri-dream/settings.json | jq .system_prompt

# 验证 server.py 中的 get_module_prompt 函数
grep -A 15 "def get_module_prompt" /root/.openclaw/workspace/server.py
```

**要求**:
- ✅ 每个模块提示词独立存储在各自目录
- ✅ POST 请求时动态拼接，不在 agent 配置里硬编码
- ✅ `get_module_prompt(module)` 函数正确读取对应模块设置

---

### 4. 功能模块按钮测试 ✅

#### By Design 模块
```bash
# 测试创建出行
curl -sk -X POST https://localhost/bydesign/api/trips \
  -H "Content-Type: application/json" \
  -d '{"name":"测试出行","description":"测试"}'

# 测试获取清单
curl -sk https://localhost/bydesign/api/checklist

# 测试添加检查项
curl -sk -X POST https://localhost/bydesign/api/checklist \
  -H "Content-Type: application/json" \
  -d '{"text":"测试检查项"}'
```

#### Cherry Pick 模块
```bash
# 测试获取搬家列表
curl -sk https://localhost/cherry-pick/api/moves

# 测试创建搬家
curl -sk -X POST https://localhost/cherry-pick/api/moves \
  -H "Content-Type: application/json" \
  -d '{"name":"测试搬家","description":"测试"}'

# 测试添加物品
curl -sk -X POST https://localhost/cherry-pick/api/moves/测试 ID/items \
  -H "Content-Type: application/json" \
  -d '{"name":"测试物品","before_location":"旧","after_location":"新"}'
```

#### Momhand 模块
```bash
# 测试获取物品列表
curl -sk https://localhost/momhand/api/items

# 测试添加物品
curl -sk -X POST https://localhost/momhand/api/items \
  -H "Content-Type: application/json" \
  -d '{"name":"测试物品","type":"测试","location":"测试位置","usage":"测试用途"}'

# 测试搜索
curl -sk "https://localhost/momhand/api/search?q=测试"

# 测试统计
curl -sk https://localhost/momhand/api/stats
```

#### Siri Dream 模块
```bash
# 测试发送消息
curl -sk -X POST https://localhost/siri-dream/api/message \
  -H "Content-Type: application/json" \
  -d '{"message":"测试消息"}'

# 测试获取消息列表
curl -sk https://localhost/siri-dream/api/messages?limit=5

# 测试查询单个消息
curl -sk https://localhost/siri-dream/api/message/测试 ID
```

---

### 5. 核心功能验证 ✅

```bash
# 验证服务状态
ps aux | grep "python3 server.py" | grep -v grep
netstat -tlnp | grep 443

# 验证 HTTPS 证书
curl -sk https://localhost/ -o /dev/null -w "%{http_code}"

# 验证日志无错误
tail -50 /root/.openclaw/workspace/server.log | grep -i error || echo "✅ 无错误日志"
```

---

### 6. UI 显示效果检查 🎨

```bash
# 检查各页面 HTML 结构
curl -sk https://localhost/ | grep -E "(viewport|Inter|gradient|animation)" | head -5
curl -sk https://localhost/bydesign/ | grep -E "(viewport|Inter|gradient|animation)" | head -5
curl -sk https://localhost/cherry-pick/ | grep -E "(viewport|Inter|gradient|animation)" | head -5
curl -sk https://localhost/momhand/ | grep -E "(viewport|Inter|gradient|animation)" | head -5
curl -sk https://localhost/siri-dream/ | grep -E "(viewport|Inter|gradient|animation)" | head -5
```

**要求**:
- ✅ 响应式设计（viewport meta 标签）
- ✅ 现代字体（Inter）
- ✅ 渐变背景
- ✅ 平滑动画过渡
- ✅ 元素自适应布局

---

### 7. 接口调用测试 ✅

```bash
# 测试所有 GET 接口
echo "=== 首页 ==="
curl -sk https://localhost/ | head -20

echo "=== By Design API ==="
curl -sk https://localhost/bydesign/api/checklist | head -5
curl -sk https://localhost/bydesign/api/trips | head -5

echo "=== Cherry Pick API ==="
curl -sk https://localhost/cherry-pick/api/moves | head -5

echo "=== Momhand API ==="
curl -sk https://localhost/momhand/api/items | head -5
curl -sk https://localhost/momhand/api/stats | head -5

echo "=== Siri Dream API ==="
curl -sk https://localhost/siri-dream/api/messages?limit=1 | head -5

echo "=== 系统 API ==="
curl -sk https://localhost/api/logs?lines=5 | head -5
```

---

## 🚀 执行流程

### 修改代码后自动执行

1. **保存代码** → Git commit
2. **重启服务** → 自动检测进程并重启
3. **等待启动** → sleep 5 秒
4. **执行测试** → 按顺序执行上述 7 项检查
5. **输出报告** → 生成测试报告
6. **通知结果** → 发送测试结果到 Feishu

---

## 📊 测试报告格式

```markdown
## WebViewer 测试报告

**时间**: 2026-03-03 08:00:00
**版本**: v1.5.3
**提交**: abc1234

### ✅ 通过项
- [x] 模块页面层级正确 (5/5)
- [x] 数据存储方式优化 (4/4)
- [x] 系统提示词分离存储 (4/4)
- [x] 功能按钮测试 (12/12)
- [x] 核心功能验证 (3/3)
- [x] UI 显示效果 (5/5)
- [x] 接口调用测试 (8/8)

### ❌ 失败项
- 无

### 📝 备注
所有测试通过，系统运行正常。
```

---

## ⚠️ 异常处理

### 服务启动失败
```bash
# 检查端口占用
netstat -tlnp | grep 443
# 杀死旧进程
pkill -9 -f "python3 server.py"
# 重新启动
cd /root/.openclaw/workspace
nohup python3 server.py > /tmp/webviewer.log 2>&1 &
```

### API 测试失败
```bash
# 查看详细日志
tail -100 /root/.openclaw/workspace/server.log
# 检查证书
ls -la /root/.openclaw/workspace/selfsigned.*
# 验证 Python 语法
python3 -m py_compile /root/.openclaw/workspace/server.py
```

---

## 🔄 持续集成

将此 skill 集成到开发流程：

```bash
# 添加 git hook
cat > /root/.openclaw/workspace/.git/hooks/post-commit << 'EOF'
#!/bin/bash
# 提交后自动执行测试
python3 /root/.openclaw/workspace/skills/webviewer-test/run_tests.py
EOF
chmod +x /root/.openclaw/workspace/.git/hooks/post-commit
```

---

**记住**: 每次修改代码后必须执行完整测试流程！
