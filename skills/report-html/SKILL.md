# report-html Skill

生成 HTML 格式的报告，并自动部署到 WebViewer 服务供远程访问。

## 触发条件

当用户要求生成报告、总结、检索结果等，并希望以网页形式查看时。

## 使用方法

### 基础用法
```
生成一份关于 agent 的热门新闻报道
```

### 指定报告类型
```
生成 HTML 报告：检索当前最热门的有关 agent 的 3 条信息
```

## 输出

- 报告 HTML 文件保存在 `/root/.openclaw/workspace/webviewer/reports/`
- 访问地址：`https://<公网IP>/reports/<报告文件名>.html`
- 自动生成报告索引页，列出所有历史报告

## 报告模板特性

- 响应式设计，支持手机/电脑浏览
- 自动添加生成时间、报告标题
- 支持 Markdown 内容渲染
- 支持代码高亮
- 支持表格、列表等格式

## 文件结构

```
report-html/
├── SKILL.md              # 本说明文件
├── report.py             # 报告生成脚本
├── templates/
│   └── report.html       # HTML 报告模板
└── examples/
    └── sample.html       # 示例报告
```

## 依赖

- Python 3
- WebViewer 服务需运行中

## 注意事项

- 报告文件会自动添加到 WebViewer 的 reports 目录
- 每次生成报告会更新索引页
- 报告文件名使用时间戳避免冲突
