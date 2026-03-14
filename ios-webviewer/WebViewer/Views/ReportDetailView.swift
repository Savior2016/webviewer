//
//  ReportDetailView.swift
//  WebViewer
//
//  报告详情视图 (WebView)
//

import SwiftUI
import WebKit

struct ReportDetailView: View {
    let report: Report
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            WebView(url: report.url)
                .navigationTitle(report.title)
                .navigationBarTitleDisplayMode(.inline)
                .toolbar {
                    ToolbarItem(placement: .navigationBarTrailing) {
                        Button("完成") {
                            dismiss()
                        }
                    }
                }
        }
    }
}

// MARK: - WebView Representable

struct WebView: UIViewRepresentable {
    let url: String
    
    func makeUIView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        config.allowsInlineMediaPlayback = true
        config.mediaTypesRequiringUserActionForPlayback = []
        
        let webView = WKWebView(frame: .zero, configuration: config)
        webView.allowsBackForwardNavigationGestures = true
        webView.scrollView.bounces = true
        webView.scrollView.showsVerticalScrollIndicator = true
        
        return webView
    }
    
    func updateUIView(_ webView: WKWebView, context: Context) {
        guard let requestURL = URL(string: url) else { return }
        let request = URLRequest(url: requestURL)
        webView.load(request)
    }
}

#Preview {
    ReportDetailView(
        report: Report(
            title: "📊 AI 前沿日报 · 2026-03-06",
            filename: "report_20260306_080001.html",
            date: Date(),
            url: "http://localhost/reports/report_20260306_080001.html"
        )
    )
}
