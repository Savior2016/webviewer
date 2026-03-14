//
//  Report.swift
//  WebViewer
//
//  报告数据模型
//

import Foundation

struct Report: Identifiable, Codable {
    let id: String
    let title: String
    let filename: String
    let date: Date
    let url: String
    
    enum CodingKeys: String, CodingKey {
        case id, title, filename, date, url
    }
    
    init(id: String = UUID().uuidString, title: String, filename: String, date: Date, url: String) {
        self.id = id
        self.title = title
        self.filename = filename
        self.date = date
        self.url = url
    }
}

// API 响应模型
struct ReportListResponse: Codable {
    let reports: [Report]
    let total: Int
    let timestamp: String
}
