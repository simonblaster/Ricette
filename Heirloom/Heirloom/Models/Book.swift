import Foundation
import SwiftUI

// MARK: - Book
struct Book: Identifiable, Codable {
    var id        = UUID()
    var name      : String
    var author    : String          // es. "Nonna Concetta"
    var year      : String          // es. "1962"
    var coverEmoji: String          // emoji per la copertina
    var pages     : [Page]          = []
    var createdAt : Date            = .now

    var pageCount  : Int  { pages.count }
    var recipeCount: Int  { pages.filter { $0.status == .structured }.count }
}

// MARK: - Page
struct Page: Identifiable, Codable {
    var id         = UUID()
    var number     : Int
    var imageFileName: String?      // nome file in Documents/photos/
    var rawOCRText : String?        // testo grezzo da Vision
    var status     : PageStatus     = .raw
    var recipe     : Recipe?        // valorizzato dopo elaborazione AI

    var imageURL: URL? {
        guard let name = imageFileName else { return nil }
        return FileManager.default
            .urls(for: .documentDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("photos/\(name)")
    }
}

enum PageStatus: String, Codable, CaseIterable {
    case raw        = "raw"        // solo foto
    case ocrDone    = "ocr_done"   // testo estratto
    case structured = "structured" // elaborato da AI
    case exported   = "exported"   // esportato

    var label: String {
        switch self {
        case .raw:        return "Grezzo"
        case .ocrDone:    return "OCR"
        case .structured: return "AI"
        case .exported:   return "Esportato"
        }
    }

    var color: Color {
        switch self {
        case .raw:        return .gray
        case .ocrDone:    return Color(hex: "#1a7a40")
        case .structured: return Color(hex: "#6b2da8")
        case .exported:   return Color(hex: "#a83d20")
        }
    }
}

// MARK: - Recipe
struct Recipe: Identifiable, Codable {
    var id          = UUID()
    var title       : String
    var source      : String        // "Nonna Concetta · p.5 · 1962"
    var servings    : String
    var ingredients : [Ingredient]  = []
    var directions  : [String]      = []
    var notes       : String        = ""
    var tags        : [String]      = []
    var aiGenerated : Bool          = false
}

struct Ingredient: Identifiable, Codable {
    var id   = UUID()
    var qty  : String   // "500"
    var unit : String   // "g"
    var name : String   // "rigatoni"

    var display: String {
        [qty, unit, name].filter { !$0.isEmpty }.joined(separator: " ")
    }
}
