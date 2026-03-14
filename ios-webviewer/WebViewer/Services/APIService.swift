//
//  APIService.swift
//  WebViewer
//
//  网络请求服务
//

import Foundation
import Combine

class APIService {
    static let shared = APIService()
    
    // ⚠️ 修改为你的服务器地址
    private let baseURL = "http://localhost:8080/webviewer/www/reports"
    
    private let session: URLSession
    private let decoder: JSONDecoder
    
    init() {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        config.timeoutIntervalForResource = 300
        self.session = URLSession(configuration: config)
        
        self.decoder = JSONDecoder()
        self.decoder.dateDecodingStrategy = .iso8601
    }
    
    /// 获取报告列表
    func fetchReports() -> AnyPublisher<[Report], Error> {
        guard let url = URL(string: "\(baseURL)/index.json") else {
            return Fail(error: URLError(.badURL)).eraseToAnyPublisher()
        }
        
        return session.dataTaskPublisher(for: url)
            .tryMap { data, response in
                guard let httpResponse = response as? HTTPURLResponse,
                      (200...299).contains(httpResponse.statusCode) else {
                    throw URLError(.badServerResponse)
                }
                return data
            }
            .decode(type: ReportListResponse.self, decoder: decoder)
            .map { $0.reports }
            .eraseToAnyPublisher()
    }
    
    /// 获取报告 HTML 内容
    func fetchReportHTML(filename: String) -> AnyPublisher<String, Error> {
        guard let url = URL(string: "\(baseURL)/\(filename)") else {
            return Fail(error: URLError(.badURL)).eraseToAnyPublisher()
        }
        
        return session.dataTaskPublisher(for: url)
            .tryMap { data, response in
                guard let httpResponse = response as? HTTPURLResponse,
                      (200...299).contains(httpResponse.statusCode) else {
                    throw URLError(.badServerResponse)
                }
                return String(data: data, encoding: .utf8) ?? ""
            }
            .eraseToAnyPublisher()
    }
}
