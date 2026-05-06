import Foundation
import UIKit

// ExportService: converte una Recipe nei formati supportati
// Formati: Testo semplice, HTML (per il web Recipees), Paprika 3, JSON generico

struct ExportService {

    static let shared = ExportService()

    enum ExportFormat: String, CaseIterable, Identifiable {
        case plainText   = "Testo"
        case html        = "HTML"
        case paprika     = "Paprika 3"
        case json        = "JSON"

        var id: String { rawValue }
        var fileExtension: String {
            switch self {
            case .plainText: return "txt"
            case .html:      return "html"
            case .paprika:   return "paprikarecipes"
            case .json:      return "json"
            }
        }
        var icon: String {
            switch self {
            case .plainText: return "doc.text"
            case .html:      return "globe"
            case .paprika:   return "fork.knife"
            case .json:      return "curlybraces"
            }
        }
    }

    // MARK: - Esporta

    func export(recipe: Recipe, format: ExportFormat) throws -> Data {
        switch format {
        case .plainText: return try exportPlainText(recipe)
        case .html:      return try exportHTML(recipe)
        case .paprika:   return try exportPaprika(recipe)
        case .json:      return try exportJSON(recipe)
        }
    }

    func fileName(for recipe: Recipe, format: ExportFormat) -> String {
        let safe = recipe.title
            .replacingOccurrences(of: "/", with: "-")
            .replacingOccurrences(of: ":", with: "")
            .prefix(50)
        return "\(safe).\(format.fileExtension)"
    }

    // MARK: - Plain Text

    private func exportPlainText(_ recipe: Recipe) throws -> Data {
        var lines: [String] = []
        lines.append(recipe.title.uppercased())
        lines.append(String(repeating: "─", count: min(recipe.title.count, 40)))
        lines.append(recipe.source)
        if !recipe.servings.isEmpty {
            lines.append("Porzioni: \(recipe.servings)")
        }
        lines.append("")
        if !recipe.ingredients.isEmpty {
            lines.append("INGREDIENTI")
            recipe.ingredients.forEach { lines.append("• \($0.display)") }
            lines.append("")
        }
        if !recipe.directions.isEmpty {
            lines.append("PREPARAZIONE")
            recipe.directions.enumerated().forEach { i, step in
                lines.append("\(i + 1). \(step)")
            }
            lines.append("")
        }
        if !recipe.notes.isEmpty {
            lines.append("NOTE")
            lines.append(recipe.notes)
        }
        lines.append("")
        lines.append("Creato con Heirloom by Recipees")

        guard let data = lines.joined(separator: "\n").data(using: .utf8) else {
            throw ExportError.encodingFailed
        }
        return data
    }

    // MARK: - HTML (stile Recipees)

    private func exportHTML(_ recipe: Recipe) throws -> Data {
        let ingredientRows = recipe.ingredients.map {
            "<li>\($0.display)</li>"
        }.joined(separator: "\n")

        let directionRows = recipe.directions.enumerated().map { i, step in
            "<li>\(step)</li>"
        }.joined(separator: "\n")

        let html = """
        <!DOCTYPE html>
        <html lang="it">
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>\(recipe.title)</title>
          <style>
            body { font-family: Georgia, serif; max-width: 640px; margin: 40px auto; padding: 0 20px; color: #1a1714; background: #faf8f3; }
            h1 { color: #a83d20; border-bottom: 1px solid #e0ddd5; padding-bottom: 8px; }
            .meta { color: #857c6e; font-size: 13px; margin-bottom: 24px; }
            h2 { font-size: 11px; letter-spacing: 2px; text-transform: uppercase; color: #857c6e; }
            ul, ol { padding-left: 20px; line-height: 1.8; }
            .notes { font-style: italic; color: #857c6e; }
            .tags span { display: inline-block; background: rgba(168,61,32,0.1); color: #a83d20; border-radius: 12px; padding: 2px 10px; font-size: 11px; margin-right: 6px; }
            footer { margin-top: 40px; font-size: 11px; color: #857c6e; text-align: center; }
          </style>
        </head>
        <body>
          <h1>\(recipe.title)</h1>
          <p class="meta">\(recipe.source)\(recipe.servings.isEmpty ? "" : " · \(recipe.servings)")</p>

          \(recipe.ingredients.isEmpty ? "" : "<h2>Ingredienti</h2><ul>\(ingredientRows)</ul>")
          \(recipe.directions.isEmpty  ? "" : "<h2>Preparazione</h2><ol>\(directionRows)</ol>")
          \(recipe.notes.isEmpty       ? "" : "<h2>Note</h2><p class=\"notes\">\(recipe.notes)</p>")
          \(recipe.tags.isEmpty ? "" : "<div class=\"tags\">\(recipe.tags.map { "<span>#\($0)</span>" }.joined())</div>")

          <footer>Creato con <strong>Heirloom by Recipees</strong></footer>
        </body>
        </html>
        """
        guard let data = html.data(using: .utf8) else { throw ExportError.encodingFailed }
        return data
    }

    // MARK: - Paprika 3 (formato .paprikarecipes = gzip di JSON)

    private func exportPaprika(_ recipe: Recipe) throws -> Data {
        let paprikaRecipe: [String: Any] = [
            "uid":          recipe.id.uuidString,
            "name":         recipe.title,
            "servings":     recipe.servings,
            "source":       recipe.source,
            "source_url":   "",
            "prep_time":    "",
            "cook_time":    "",
            "on_favorites": false,
            "ingredients":  recipe.ingredients.map { $0.display }.joined(separator: "\n"),
            "directions":   recipe.directions.enumerated()
                                .map { "\($0.offset + 1). \($0.element)" }
                                .joined(separator: "\n\n"),
            "notes":        recipe.notes,
            "categories":   recipe.tags,
            "nutritional_info": "",
            "difficulty":   "",
            "rating":       0,
            "description":  "",
            "photo":        "",
            "photo_hash":   NSNull(),
            "photo_data":   NSNull(),
            "scale":        NSNull(),
            "hash":         recipe.id.uuidString,
            "created":      ISO8601DateFormatter().string(from: .now)
        ]

        let wrapper: [String: Any] = [
            "recipes": [paprikaRecipe]
        ]

        let jsonData = try JSONSerialization.data(withJSONObject: wrapper)
        // Paprika usa gzip
        return try (jsonData as NSData).compressed(using: .zlib) as Data
    }

    // MARK: - JSON generico

    private func exportJSON(_ recipe: Recipe) throws -> Data {
        return try JSONEncoder().encode(recipe)
    }
}

// MARK: - Errors

enum ExportError: LocalizedError {
    case encodingFailed

    var errorDescription: String? { "Impossibile codificare il file di esportazione" }
}
