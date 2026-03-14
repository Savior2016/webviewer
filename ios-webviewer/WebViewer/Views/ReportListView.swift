//
//  ReportListView.swift
//  WebViewer
//
//  报告列表视图
//

import SwiftUI

struct ReportListView: View {
    @StateObject private var viewModel = ReportViewModel()
    @State private var showingDetail = false
    
    var body: some View {
        NavigationView {
            Group {
                if viewModel.isLoading && viewModel.reports.isEmpty {
                    loadingView
                } else if let error = viewModel.errorMessage {
                    errorView(error)
                } else if viewModel.reports.isEmpty {
                    emptyView
                } else {
                    reportList
                }
            }
            .navigationTitle("📊 报告中心")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        viewModel.loadReports()
                    }) {
                        Image(systemName: "arrow.clockwise")
                    }
                }
            }
            .refreshable {
                viewModel.loadReports()
            }
            .navigationDestination(item: $viewModel.selectedReport) { report in
                ReportDetailView(report: report)
            }
        }
        .onAppear {
            viewModel.loadReports()
        }
    }
    
    // MARK: - Subviews
    
    private var loadingView: some View {
        VStack(spacing: 16) {
            ProgressView()
                .scaleEffect(1.5)
            Text("加载中...")
                .foregroundColor(.secondary)
        }
    }
    
    private func errorView(_ message: String) -> some View {
        VStack(spacing: 16) {
            Image(systemName: "exclamationmark.triangle")
                .font(.system(size: 50))
                .foregroundColor(.orange)
            Text("加载失败")
                .font(.headline)
            Text(message)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
            Button("重试") {
                viewModel.loadReports()
            }
            .buttonStyle(.borderedProminent)
        }
        .padding()
    }
    
    private var emptyView: some View {
        VStack(spacing: 16) {
            Image(systemName: "doc.text")
                .font(.system(size: 50))
                .foregroundColor(.gray)
            Text("暂无报告")
                .font(.headline)
            Text("报告生成后将在此显示")
                .foregroundColor(.secondary)
        }
    }
    
    private var reportList: some View {
        List(viewModel.reports) { report in
            ReportRowView(report: report)
                .onTapGesture {
                    viewModel.selectReport(report)
                }
        }
        .listStyle(.insetGrouped)
    }
}

#Preview {
    ReportListView()
}
