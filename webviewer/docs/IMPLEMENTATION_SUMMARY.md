# 功能实现总结

## ✅ 已完成

### 1. ByDesign → By Design
- ✅ 所有文件中的 ByDesign 已替换为 By Design
- ✅ 包括 HTML、Markdown、Python 文件

### 2. 提示词配置结构
- ✅ 创建配置目录：`data/prompts/`
- ✅ By Design 配置：`bydesign.json`
- ✅ Cherry Pick 配置：`cherry-pick.json`
- ✅ Momhand 配置：`momhand.json`

每个配置包含：
- `project`: 项目标识
- `name`: 项目名称
- `system_prompt`: 系统提示词（支持 {message} 占位符）

---

## ⏳ 待实现（需要前端修改）

### 每个项目页面需要添加：

#### 1. 输入框 UI
```html
<!-- 固定在页面底部 -->
<div class="fixed bottom-0 left-0 right-0 p-4 bg-white/95 backdrop-blur border-t">
  <div class="max-w-3xl mx-auto flex gap-3">
    <input type="text" id="messageInput" placeholder="描述要添加的内容..." 
           class="flex-1 px-4 py-3 rounded-xl border-2 focus:border-blue-500 outline-none">
    <button onclick="sendMessage()" class="bg-blue-500 text-white px-6 py-3 rounded-xl">
      发送
    </button>
  </div>
</div>
```

#### 2. 结果展示动画
```html
<div id="resultArea" class="hidden fixed bottom-20 left-0 right-0 p-4">
  <div class="max-w-3xl mx-auto">
    <div class="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-xl slide-in">
      ✅ 已添加成功！
    </div>
  </div>
</div>
```

#### 3. JavaScript 处理
```javascript
async function sendMessage() {
  const input = document.getElementById('messageInput');
  const message = input.value.trim();
  
  if (!message) return;
  
  // 显示处理中
  showLoading();
  
  try {
    const response = await fetch('/api/process-message', {
      method: 'POST',
      body: JSON.stringify({
        project: 'bydesign',  // 根据项目修改
        message: message
      })
    });
    
    const result = await response.json();
    
    // 显示结果动画
    showResult(result.success, result.message);
    
    if (result.success) {
      // 刷新页面数据
      loadData();
    }
  } catch (error) {
    showResult(false, '处理失败');
  }
}
```

---

## 🔧 后端 API（需要添加）

### server.py 添加：

```python
def do_POST(self):
    # ... 现有代码 ...
    
    # 项目消息处理 API
    elif path == "/api/process-message":
        self.handle_process_message(data)
    
    # 提示词配置 API
    elif path.startswith("/api/prompts/"):
        if self.command == 'GET':
            self.handle_get_prompt(path)
        elif self.command == 'PUT':
            self.handle_save_prompt(path, data)

def handle_process_message(self, data):
    """处理项目消息"""
    project = data.get('project')
    message = data.get('message')
    
    # 读取项目提示词配置
    prompt_file = f"/root/.openclaw/workspace/webviewer/data/prompts/{project}.json"
    with open(prompt_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    system_prompt = config['system_prompt'].format(message=message)
    
    # 调用 OpenClaw agent
    cmd = ['openclaw', 'agent', '--agent', 'main', '-m', system_prompt]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    
    # 解析结果并执行保存
    # ...
    
    # 返回结果
    self.send_response(200)
    self.send_header("Content-Type", "application/json; charset=utf-8")
    self.end_headers()
    self.wfile.write(json.dumps(response, ensure_ascii=False).encode("utf-8"))
```

---

## 📝 建议实现顺序

1. **先实现 By Design 页面**
   - 添加输入框
   - 添加结果展示
   - 添加 JavaScript 处理
   - 测试

2. **复制到其他项目**
   - Cherry Pick 页面
   - Momhand 页面
   - 修改 project 标识

3. **添加设置功能**
   - 每个页面的设置按钮
   - 提示词编辑模态框
   - 保存/加载配置

---

## 🎨 动画效果建议

### 成功动画
```css
@keyframes successPop {
  0% { transform: scale(0.8); opacity: 0; }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); opacity: 1; }
}
.success {
  animation: successPop 0.4s ease-out;
}
```

### 加载动画
```css
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
.loading {
  animation: pulse 1.5s ease-in-out infinite;
}
```

---

*文档时间：2026-02-27 19:35*
