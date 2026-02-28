# WebViewer Version Manager

自动检测 WebViewer 代码变更，协助 commit 和版本更新。

## 功能

- 🔍 检测 webviewer 目录的 git 变更
- 📝 协助编写 commit message
- 🏷️ 自动更新版本号（遵循 SemVer）
- 📋 更新更新日志
- 🔄 可选重启 WebViewer 服务

## 使用方式

当用户提到修改了 webviewer 代码时，AI 会自动：

1. 检查 `git status webviewer/`
2. 如果有未提交更改，询问是否 commit
3. 如果确认，协助更新版本信息
4. 提交代码
5. 可选重启服务

## 版本规则

- **Major**: 不兼容的重大更新
- **Minor**: 向下兼容的新功能
- **Patch**: 向下兼容的 bug 修复

## 文件结构

```
webviewer-version/
├── SKILL.md      # 技能说明
└── README.md     # 本文件
```

## 示例

```
用户：我改了 webviewer 的提示词
助手：检测到 webviewer 有未提交的更改，是否要 commit 并更新版本？

用户：更新
助手：好的，版本已从 v1.0.0 更新到 v1.1.0，代码已提交。
```
