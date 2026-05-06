import Foundation

// ClaudeService: chiama l'API di Anthropic per strutturare il testo OCR in una Recipe
// Usa claude-haiku-4-5 per velocità/costo (≈$0.003/ricetta)
// Risponde con JSON che viene decodificato in Recipe

actor ClaudeService {

    static let shared = ClaudeService()

    // MARK: - Config
    // Nota: in produzione l'API key va gestita tramite backend proxy o Keychain.
    // Per il prototipo si usa un valore iniettato all'avvio via Settings bundle.
    private var apiKey: String {
        Bundle.main.object(forInfoDictionaryKey: "CLAUDE_API_KEY") as? String ?? ""
    }

    // MARK: - Struttura ricetta da testo OCR

    func structureRecipe(
        ocrText: String,
        bookAuthor: String,
        bookYear: String,
        pageNumber: Int
    ) async throws -> Recipe {

        let prompt = buildPrompt(
            ocrText: ocrText,
            author: bookAuthor,
            year: bookYear,
            page: pageNumber
        )

        let requestBody: [String: Any] = [
            "model": HeirloomConstants.claudeModel,
            "max_tokens": 1024,
            "messages": [
                ["role": "user", "content": prompt]
            ]
        ]

        var request = URLRequest(url: URL(string: HeirloomConstants.apiBaseURL)!)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("Bearer \(apiKey)", forHTTPHeaderField: "Authorization")
        request.setValue("2023-06-01", forHTTPHeaderField: "anthropic-version")
        request.httpBody = try JSONSerialization.data(withJSONObject: requestBody)
        request.timeoutInterval = 30

        let (data, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw ClaudeError.networkError("Risposta non valida")
        }
        guard httpResponse.statusCode == 200 else {
            throw ClaudeError.apiError(httpResponse.statusCode)
        }

        return try parseResponse(data: data, source: "\(bookAuthor) · p.\(pageNumber) · \(bookYear)")
    }

    // MARK: - Prompt engineering

    private func buildPrompt(ocrText: String, author: String, year: String, page: Int) -> String {
        """
        Hai ricevuto il testo OCR di una pagina di un ricettario scritto a mano da \(author) circa nel \(year).
        Il testo può avere errori OCR, abbreviazioni tipiche della cucina italiana, e stile informale.

        Testo OCR:
        ---
        \(ocrText)
        ---

        Estrai la ricetta e rispondi SOLO con JSON valido in questo formato (nessun testo prima o dopo):
        {
          "title": "Nome della ricetta",
          "servings": "4 persone",
          "ingredients": [
            {"qty": "500", "unit": "g", "name": "rigatoni"},
            {"qty": "2", "unit": "", "name": "uova"}
          ],
          "directions": [
            "Primo passaggio...",
            "Secondo passaggio..."
          ],
          "notes": "Note aggiuntive se presenti, altrimenti stringa vuota",
          "tags": ["pasta", "primo piatto"]
        }

        Regole:
        - Se qty o unit sono assenti usa stringa vuota ""
        - directions: ogni passaggio è una stringa separata
        - tags: massimo 5 tag in italiano, minuscolo
        - Se il testo non contiene una ricetta, usa title "Pagina non riconosciuta" e array vuoti
        """
    }

    // MARK: - Parsing risposta

    private func parseResponse(data: Data, source: String) throws -> Recipe {
        // La risposta Anthropic ha struttura: { content: [ { type: "text", text: "..." } ] }
        guard
            let json     = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
            let content  = json["content"] as? [[String: Any]],
            let first    = content.first,
            let text     = first["text"] as? String
        else {
            throw ClaudeError.parseError("Struttura risposta API non riconosciuta")
        }

        // Estrai JSON dalla risposta (può avere spazi/newline prima/dopo)
        guard
            let jsonStart = text.firstIndex(of: "{"),
            let jsonEnd   = text.lastIndex(of: "}"),
            jsonStart <= jsonEnd
        else {
            throw ClaudeError.parseError("JSON non trovato nella risposta")
        }

        let jsonString = String(text[jsonStart...jsonEnd])
        guard let recipeData = jsonString.data(using: .utf8) else {
            throw ClaudeError.parseError("Impossibile convertire JSON")
        }

        let raw = try JSONDecoder().decode(RawRecipeResponse.self, from: recipeData)

        return Recipe(
            title: raw.title,
            source: source,
            servings: raw.servings,
            ingredients: raw.ingredients.map {
                Ingredient(qty: $0.qty, unit: $0.unit, name: $0.name)
            },
            directions: raw.directions,
            notes: raw.notes,
            tags: raw.tags,
            aiGenerated: true
        )
    }
}

// MARK: - Decodable intermedi

private struct RawRecipeResponse: Decodable {
    let title      : String
    let servings   : String
    let ingredients: [RawIngredient]
    let directions : [String]
    let notes      : String
    let tags       : [String]
}

private struct RawIngredient: Decodable {
    let qty : String
    let unit: String
    let name: String
}

// MARK: - Errors

enum ClaudeError: LocalizedError {
    case networkError(String)
    case apiError(Int)
    case parseError(String)
    case noCredits

    var errorDescription: String? {
        switch self {
        case .networkError(let msg): return "Errore di rete: \(msg)"
        case .apiError(let code):   return "Errore API: HTTP \(code)"
        case .parseError(let msg):  return "Errore parsing: \(msg)"
        case .noCredits:            return "Crediti esauriti. Acquista un pacchetto per continuare."
        }
    }
}
