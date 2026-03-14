# WebViewer iOS 快速启动指南

## 🚀 5 分钟创建项目

### 方法 1：使用 Xcode 命令行工具

```bash
# 1. 进入项目目录
cd ~/.openclaw/workspace/ios-webviewer

# 2. 创建 Xcode 项目
mkdir -p WebViewer.xcodeproj

# 3. 生成项目文件（需要 Xcode 命令行工具）
# 或者直接在 Xcode 中打开并添加文件
```

### 方法 2：手动在 Xcode 中创建

1. **打开 Xcode** → File → New → Project
2. 选择 **iOS** → **App**
3. 配置:
   - Product Name: `WebViewer`
   - Interface: **SwiftUI**
   - Language: **Swift**
4. 将以下文件拖入项目:
   - `ContentView.swift`
   - `AppDelegate.swift`
   - `SceneDelegate.swift`
   - `Models/Report.swift`
   - `ViewModels/ReportViewModel.swift`
   - `Views/*.swift`
   - `Services/APIService.swift`

---

## ⚙️ 配置服务器地址

编辑 `Services/APIService.swift`:

```swift
// 修改为你的实际服务器地址
private let baseURL = "http://YOUR_SERVER_IP:PORT/webviewer/www/reports"
```

例如:
```swift
private let baseURL = "http://192.168.1.100:8080/webviewer/www/reports"
```

---

## 🏃 运行项目

1. 在 Xcode 中选择目标设备 (iPhone 模拟器或真机)
2. 点击 **Run** (⌘R)
3. App 启动后会自动加载报告列表

---

## 📱 功能预览

- **首页**: 报告列表，下拉刷新
- **详情页**: WebView 内嵌显示 HTML 报告
- **支持**: 深色模式、横竖屏切换

---

## 🔧 常见问题

### Q: 网络请求失败？
A: 检查:
1. 服务器地址是否正确
2. 服务器是否可访问
3. Info.plist 中 ATS 配置是否正确

### Q: 如何打包发布？
A: 
1. Xcode → Product → Archive
2. 选择 Distribute App
3. 按照向导完成打包

### Q: 支持 iPad 吗？
A: 当前代码已支持 iPad，在 Xcode 中选择 iPad 模拟器即可测试。

---

## 📄 文件结构

```
ios-webviewer/
├── WebViewer/
│   ├── AppDelegate.swift          # 应用入口
│   ├── SceneDelegate.swift        # 场景代理
│   ├── ContentView.swift          # 主视图
│   ├── Models/
│   │   └── Report.swift           # 数据模型
│   ├── ViewModels/
│   │   └── ReportViewModel.swift  # 视图模型
│   ├── Views/
│   │   ├── ReportListView.swift   # 列表视图
│   │   ├── ReportRowView.swift    # 行视图
│   │   └── ReportDetailView.swift # 详情视图
│   ├── Services/
│   │   └── APIService.swift       # 网络服务
│   └── Info.plist                 # 应用配置
├── README.md                      # 本文档
└── WebViewer.xcodeproj            # Xcode 项目 (需手动创建)
```

---

需要帮助？查看完整 README.md 或联系开发者。
