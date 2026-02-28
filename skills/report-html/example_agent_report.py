#!/usr/bin/env python3
"""
示例：生成一份 Agent 热门资讯报告
"""
import sys
sys.path.insert(0, "/root/.openclaw/workspace/skills/report-html")
from report import create_report

content = """
<h2>📰 热门资讯 #1: AI Agent 自主性突破</h2>
<p>最新研究表明，新一代 AI Agent 已能独立完成复杂任务链，无需人工干预。研究人员展示了 Agent 自主完成"研究 - 规划 - 执行 - 验证"完整流程的能力。</p>
<blockquote>关键突破：任务完成率从 65% 提升至 89%</blockquote>

<h2>📰 热门资讯 #2: 多 Agent 协作框架发布</h2>
<p>主流 AI 公司推出多 Agent 协作框架，支持多个 AI 助手分工合作完成大型项目。框架包含任务分配、进度跟踪、结果整合等核心功能。</p>
<ul>
<li>支持 2-10 个 Agent 同时协作</li>
<li>自动任务分解与分配</li>
<li>实时进度同步与冲突解决</li>
</ul>

<h2>📰 热门资讯 #3: Agent 开发工具链成熟</h2>
<p>2025 年下半年以来，Agent 开发工具快速成熟，包括可视化编排工具、调试框架、性能监控等。开发者创建自定义 Agent 的门槛大幅降低。</p>
<p><code>平均开发时间从 2 周缩短至 2 天</code></p>

<h2>📊 总结</h2>
<p>AI Agent 领域正处于快速发展期，自主性、协作性、易用性是三大核心趋势。预计 2026 年将有更多企业级应用落地。</p>
"""

url = create_report(
    title="🤖 AI Agent 热门资讯报告",
    content=content,
    tags=["AI", "Agent", "热门资讯", "2026"]
)

print(f"✅ 报告已生成")
print(f"🔗 访问地址：https://<你的公网IP>{url}")
print(f"📋 报告列表：https://<你的公网IP>/reports/index.html")
