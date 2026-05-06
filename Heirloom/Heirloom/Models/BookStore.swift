import Foundation
import Combine

// BookStore: fonte di verità per tutti i libri.
// Persiste su disco come JSON — semplice, leggibile, nessuna dipendenza CoreData.

class BookStore: ObservableObject {
    @Published var books: [Book] = []
    @Published var credits: Int  = HeirloomConstants.maxCreditsStarter

    private let savePath = FileManager.default
        .urls(for: .documentDirectory, in: .userDomainMask)[0]
        .appendingPathComponent("books.json")

    init() { load() }

    // MARK: - CRUD

    func addBook(_ book: Book) {
        books.append(book)
        save()
    }

    func deleteBook(id: UUID) {
        books.removeAll { $0.id == id }
        save()
    }

    func updateBook(_ updated: Book) {
        if let i = books.firstIndex(where: { $0.id == updated.id }) {
            books[i] = updated
            save()
        }
    }

    func addPage(_ page: Page, toBook bookID: UUID) {
        guard let i = books.firstIndex(where: { $0.id == bookID }) else { return }
        books[i].pages.append(page)
        save()
    }

    func updatePage(_ page: Page, inBook bookID: UUID) {
        guard let bi = books.firstIndex(where: { $0.id == bookID }),
              let pi = books[bi].pages.firstIndex(where: { $0.id == page.id })
        else { return }
        books[bi].pages[pi] = page
        save()
    }

    func useCredit() -> Bool {
        guard credits > 0 else { return false }
        credits -= 1
        save()
        return true
    }

    // MARK: - Persistence

    private func save() {
        do {
            let data = try JSONEncoder().encode(SavedState(books: books, credits: credits))
            try data.write(to: savePath, options: .atomic)
        } catch {
            print("BookStore save error: \(error)")
        }
    }

    private func load() {
        guard let data = try? Data(contentsOf: savePath),
              let state = try? JSONDecoder().decode(SavedState.self, from: data)
        else { return }
        books   = state.books
        credits = state.credits
    }

    private struct SavedState: Codable {
        var books  : [Book]
        var credits: Int
    }
}
