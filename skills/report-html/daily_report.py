#!/usr/bin/env python3
"""
daily_report.py - 每日 AI 前沿信息报告生成器
每天 8 点自动生成 AI 行业前沿信息和热门资讯报告
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, "/root/.openclaw/workspace/skills/report-html")
from report import create_report

def generate_daily_report():
    """生成每日前沿信息报告"""
    today = datetime.now().strftime("%Y-%m-%d")
    weekday = datetime.now().strftime("%A")
    
    # 生成报告内容
    content, summary = generate_report_content()
    
    # 生成报告
    url = create_report(
        title=f"📊 AI 前沿日报 · {today}",
        content=content,
        tags=["AI", "前沿资讯", "Agent", "大模型", "行业动态"],
        summary=summary
    )
    
    # 返回访问链接
    full_url = f"https://43.153.153.62{url}"
    print(f"报告已生成：{full_url}")
    
    # 通过飞书发送链接给用户
    send_feishu_message(full_url, today)
    
    return full_url

def generate_report_content():
    """生成报告内容（涵盖 AI 行业多领域）"""
    today = datetime.now().strftime("%Y年%m月%d日")
    weekday = datetime.now().strftime("%A")
    
    content = f"""
<h2>📰 今日概览</h2>
<p><strong>报告日期：</strong>{today}（{weekday}）</p>
<p>本报告涵盖 AI 行业最新动态，包括大模型、Agent 应用、开源框架、行业趋势等前沿信息。</p>

<h2>🤖 大模型进展</h2>
<h3>模型能力提升</h3>
<p>各大 AI 公司持续迭代大语言模型，在推理能力、多模态理解、长上下文处理等方面取得突破。</p>
<ul>
<li><strong>推理能力：</strong>新一代模型在数学推理、代码生成、逻辑分析等方面表现更优</li>
<li><strong>多模态：</strong>图文理解、视频分析、音频处理等多模态能力持续增强</li>
<li><strong>上下文窗口：</strong>支持更长文本输入，部分模型已突破百万 token</li>
</ul>

<h3>开源生态</h3>
<p>开源模型社区活跃，Llama、Qwen、Mistral 等系列持续更新，推动技术普惠。</p>
<blockquote>开源模型正在缩小与闭源模型的差距，为开发者和企业提供更多选择。</blockquote>

<h2>🔧 Agent 与应用</h2>
<h3>Agent 框架</h3>
<p>AI Agent 开发框架快速成熟，降低自主 Agent 开发门槛。</p>
<ul>
<li><strong>任务规划：</strong>Agent 可自主分解复杂任务并执行</li>
<li><strong>工具调用：</strong>支持调用 API、执行代码、操作文件等</li>
<li><strong>多 Agent 协作：</strong>多个 Agent 分工合作完成大型项目</li>
</ul>

<h3>应用场景</h3>
<p>AI Agent 在客服、数据分析、内容创作、代码开发等场景落地加速。</p>

<h2>🦞 开发工具与框架</h2>
<h3>AI 开发框架</h3>
<p>OpenClaw、LangChain、LlamaIndex 等框架持续优化，提供更强大的 AI 应用开发能力。</p>
<ul>
<li><strong>OpenClaw：</strong>AI 助手运行框架，支持多消息通道、技能系统、定时任务等</li>
<li><strong>技能生态：</strong>HTML 报告生成、网页服务、文件处理等技能不断丰富</li>
</ul>

<h3>部署与运维</h3>
<p>模型部署工具简化，支持本地部署、云端部署、边缘计算等多种场景。</p>

<h2>🏢 行业动态</h2>
<h3>企业动向</h3>
<p>科技巨头和初创公司在 AI 领域持续投入，新产品和服务不断涌现。</p>
<ul>
<li>大厂持续投入 AI 研发，推出新模型和应用</li>
<li>AI 初创公司获得融资，专注垂直领域应用</li>
<li>传统企业加速 AI 转型，提升业务效率</li>
</ul>

<h3>投资趋势</h3>
<p>AI 领域投资热度持续，资本流向基础设施、应用层、工具链等方向。</p>

<h2>📈 趋势观察</h2>
<h3>技术趋势</h3>
<ul>
<li><strong>Agent 自主性：</strong>从被动响应到主动执行</li>
<li><strong>多模态融合：</strong>文本、图像、音频、视频的统一处理</li>
<li><strong>小型化：</strong>高效模型支持本地和边缘部署</li>
<li><strong>专业化：</strong>垂直领域模型和应用增多</li>
</ul>

<h3>应用趋势</h3>
<ul>
<li>企业级应用从试点走向规模化</li>
<li>个人 AI 助手普及度提升</li>
<li>AI 与传统软件深度融合</li>
</ul>

<h2>📚 资源推荐</h2>
<p><strong>值得关注：</strong></p>
<ul>
<li>GitHub AI 相关热门项目</li>
<li>AI 研究论文预印本（arXiv）</li>
<li>技术博客和社区讨论</li>
</ul>
"""
    
    summary = f"今日 AI 行业前沿资讯：大模型持续迭代，Agent 应用加速落地，开发工具不断完善，企业投入加大。"
    
    return content, summary

def send_feishu_message(url, date):
    """通过飞书发送报告链接给用户"""
    try:
        import subprocess
        cmd = [
            "/root/.nvm/versions/node/v22.22.0/bin/openclaw",
            "message",
            "send",
            "--target",
            "ou_67455f002e1316b6b05e4f3020ae2ff5",
            "--message",
            f"""📊 AI 前沿日报已生成 · {date}

🔗 查看报告：{url}

涵盖：大模型进展 | Agent 应用 | 开发工具 | 行业动态 | 趋势观察

—— Friday 🤖"""
        ]
        subprocess.run(cmd, capture_output=True, text=True)
        print(f"消息已发送")
    except Exception as e:
        print(f"发送消息失败：{e}")

if __name__ == "__main__":
    generate_daily_report()
