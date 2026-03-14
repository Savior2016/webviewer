//
//  ReportViewModel.swift
//  WebViewer
//
//  报告列表视图模型
//

import Foundation
import Combine

class ReportViewModel: ObservableObject {
    @Published var reports: [Report] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var selectedReport: Report?
    
    private var cancellables = Set<AnyCancellable>()
    private let apiService: APIService
    
    init(apiService: APIService = .shared) {
        self.apiService = apiService
    }
    
    /// 加载报告列表
    func loadReports() {
        isLoading = true
        errorMessage = nil
        
        apiService.fetchReports()
            .receive(on: DispatchQueue.main)
            .sink { completion in
                self.isLoading = false
                if case .failure(let error) = completion {
                    self.errorMessage = error.localizedDescription
                }
            } receiveValue: { [weak self] reports in
                self?.reports = reports.sorted { $0.date > $1.date }
            }
            .store(in: &cancellables)
    }
    
    /// 选择报告
    func selectReport(_ report: Report) {
        selectedReport = report
    }
    
    /// 清除选择
    func clearSelection() {
        selectedReport = nil
    }
}
