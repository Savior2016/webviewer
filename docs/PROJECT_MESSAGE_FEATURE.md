# 项目消息输入功能实现计划

## 📋 需求

1. ✅ ByDesign → By Design（已完成）
2. ⏳ 每个项目添加消息输入框
3. ⏳ 每个项目独立的提示词配置
4. ⏳ OpenClaw agent 处理
5. ⏳ 动画展示结果

## 🎯 实现方案

### 1. 配置文件结构

```
data/
└── prompts/
    ├── bydesign.json      # By Design 提示词
    ├── cherry-pick.json   # Cherry Pick 提示词
    └── momhand.json       # Momhand 提示词
```

### 2. 前端改动

每个项目页面添加：
- 输入框（固定在底部或顶部）
- 结果展示区域（动画）
- 设置按钮（配置提示词）

### 3. 后端 API

```
POST /api/process-message
Body: {
  "project": "bydesign|cherry_pick|momhand",
  "message": "用户消息"
}

GET /api/prompts/:project
PUT /api/prompts/:project
```

### 4. 动画效果

- ✅ 成功：绿色对勾 + 淡入
- ⏳ 处理中：加载动画
- ❌ 失败：红色警告

## 📝 下一步

由于功能较复杂，建议分步实现：
1. 先实现 By Design 页面
2. 测试通过后复制到其他项目
3. 统一优化

---

*创建时间：2026-02-27 19:30*
