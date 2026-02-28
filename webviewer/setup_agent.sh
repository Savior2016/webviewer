#!/bin/bash
# 配置 WebViewer OpenClaw Agent

echo "🔧 配置 WebViewer OpenClaw Agent..."

# 1. 创建 agent 配置目录
AGENT_DIR="$HOME/.openclaw/agents"
mkdir -p "$AGENT_DIR"

# 2. 创建 webviewer agent 配置
cat > "$AGENT_DIR/webviewer.json" << 'EOF'
{
  "name": "webviewer",
  "description": "WebViewer 消息处理助手",
  "system_prompt": "你是一个智能助手，帮助用户管理 webviewer 的三个项目：\n\n1. 已读不回 (ByDesign) - 出行管理 (/bydesign/)\n2. 一搬不丢 (Cherry Pick) - 搬家物品管理 (/cherry-pick/)\n3. 妈妈的手 (Momhand) - 物品管理 (/momhand/)\n\n请理解用户意图，选择合适的项目，返回 JSON 格式的处理结果。",
  "model": "default",
  "thinking": "minimal",
  "tools": []
}
EOF

echo "✅ Agent 配置已创建：$AGENT_DIR/webviewer.json"

# 3. 测试配置
echo ""
echo "🧪 测试 Agent 配置..."
openclaw agents list

echo ""
echo "✅ 配置完成！"
echo ""
echo "使用方法:"
echo "  openclaw agent --agent webviewer --message \"我要出差 3 天\" --json"
echo ""
