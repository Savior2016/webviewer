# WebViewer iOS 项目结构

```
~/.openclaw/workspace/ios-webviewer/
│
├── README.md                          # 项目说明文档
├── QUICKSTART.md                      # 快速启动指南
│
├── WebViewer/                         # iOS 应用源代码
│   ├── AppDelegate.swift              # 应用代理入口
│   ├── SceneDelegate.swift            # 场景代理
│   ├── ContentView.swift              # 主视图入口
│   │
│   ├── Models/
│   │   └── Report.swift               # 报告数据模型
│   │
│   ├── ViewModels/
│   │   └── ReportViewModel.swift      # 视图模型 (MVVM)
│   │
│   ├── Views/
│   │   ├── ReportListView.swift       # 报告列表页
│   │   ├── ReportRowView.swift        # 列表行组件
│   │   └── ReportDetailView.swift     # 报告详情页 (WebView)
│   │
│   ├── Services/
│   │   └── APIService.swift           # 网络请求服务
│   │
│   └── Info.plist                     # 应用配置文件
│
├── scripts/
│   └── generate_index.py              # 生成报告索引 JSON
│
└── WebViewer.xcodeproj/               # Xcode 项目文件 (需手动创建)
    └── project.pbxproj
```

## 核心文件说明

### 应用入口
- **AppDelegate.swift**: 应用生命周期管理
- **SceneDelegate.swift**: 场景生命周期 (iOS 13+)
- **ContentView.swift**: SwiftUI 根视图

### 数据层
- **Models/Report.swift**: 报告数据结构
- **Services/APIService.swift**: HTTP 请求封装

### 视图层 (MVVM)
- **ViewModels/ReportViewModel.swift**: 业务逻辑和状态管理
- **Views/ReportListView.swift**: 主页面 (列表 + 刷新)
- **Views/ReportRowView.swift**: 列表项组件
- **Views/ReportDetailView.swift**: WebView 报告查看器

### 配置文件
- **Info.plist**: 应用权限和配置 (含 ATS 网络配置)

## 依赖

- iOS 15.0+
- Xcode 14.0+
- Swift 5.7+

## 技术栈

- **UI 框架**: SwiftUI
- **架构模式**: MVVM
- **网络**: URLSession + Combine
- **WebView**: WKWebView
- **响应式**: Combine Framework
