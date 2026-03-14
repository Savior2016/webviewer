# WebViewer iOS App

基于 WebViewer 报告中心的 iOS 原生应用

## 项目结构

```
WebViewer/
├── WebViewer/
│   ├── AppDelegate.swift
│   ├── SceneDelegate.swift
│   ├── ContentView.swift
│   ├── Models/
│   │   └── Report.swift
│   ├── Views/
│   │   ├── ReportListView.swift
│   │   ├── ReportDetailView.swift
│   │   └── ReportRowView.swift
│   ├── ViewModels/
│   │   └── ReportViewModel.swift
│   ├── Services/
│   │   └── APIService.swift
│   └── Assets.xcassets
├── WebViewer.xcodeproj
└── README.md
```

## 功能特性

- ✅ 报告列表展示
- ✅ WebView 内嵌查看报告
- ✅ 下拉刷新
- ✅ 加载状态指示
- ✅ 错误处理
- ✅ 支持深色模式

## 技术栈

- SwiftUI (UI 框架)
- WKWebView (报告渲染)
- URLSession (网络请求)
- Combine (响应式编程)

## 部署步骤

1. 在 Xcode 中打开项目
2. 修改 `APIService.swift` 中的服务器地址
3. 选择目标设备（iPhone/iPad）
4. 编译运行

## 配置说明

### 服务器地址

编辑 `Services/APIService.swift`:
```swift
let baseURL = "http://your-server-ip:port/webviewer/www/reports"
```

### ATS 配置 (Info.plist)

如果服务器是 HTTP 而非 HTTPS，需要配置 ATS:
```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
</dict>
```
