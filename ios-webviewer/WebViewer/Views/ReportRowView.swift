//
//  ReportRowView.swift
//  WebViewer
//
//  报告行视图
//

import SwiftUI

struct ReportRowView: View {
    let report: Report
    
    private let dateFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .none
        formatter.locale = Locale(identifier: "zh_CN")
        return formatter
    }()
    
    var body: some View {
        HStack(spacing: 16) {
            // 图标
            ZStack {
                Circle()
                    .fill(
                        LinearGradient(
                            colors: [.indigo, .purple],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 50, height: 50)
                
                Image(systemName: "doc.text.fill")
                    .font(.system(size: 22))
                    .foregroundColor(.white)
            }
            
            // 内容
            VStack(alignment: .leading, spacing: 6) {
                Text(report.title)
                    .font(.headline)
                    .foregroundColor(.primary)
                    .lineLimit(2)
                
                Text(dateFormatter.string(from: report.date))
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            // 箭头
            Image(systemName: "chevron.right")
                .font(.caption)
                .foregroundColor(.gray)
        }
        .padding(.vertical, 8)
        .contentShape(Rectangle())
    }
}

#Preview {
    ReportRowView(
        report: Report(
            title: "📊 AI 前沿日报 · 2026-03-06",
            filename: "report_20260306_080001.html",
            date: Date(),
            url: "http://localhost/reports/report_20260306_080001.html"
        )
    )
    .padding()
}
