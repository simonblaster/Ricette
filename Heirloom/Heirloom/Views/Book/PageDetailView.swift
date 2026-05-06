import SwiftUI

// PageDetailView: mostra la foto della pagina a schermo intero
// con accesso rapido a OCR, AI e visualizzazione ricetta

struct PageDetailView: View {
    @EnvironmentObject var store: BookStore
    let page: Page
    let bookID: UUID

    @State private var showingOCR    = false
    @State private var showingRecipe = false

    // Pagina aggiornata in tempo reale
    var currentPage: Page? {
        store.books
            .first { $0.id == bookID }?
            .pages
            .first { $0.id == page.id }
    }

    var effectivePage: Page { currentPage ?? page }

    var body: some View {
        ZStack(alignment: .bottom) {
            Color.black.ignoresSafeArea()

            // Foto pagina
            if let url = effectivePage.imageURL,
               let img = UIImage(contentsOfFile: url.path) {
                Image(uiImage: img)
                    .resizable()
                    .scaledToFit()
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else {
                Image(systemName: "doc.text")
                    .font(.system(size: 80))
                    .foregroundColor(.white.opacity(0.3))
            }

            // Pannello azioni in basso
            actionPanel
        }
        .navigationTitle("Pagina \(effectivePage.number)")
        .navigationBarTitleDisplayMode(.inline)
        .toolbarColorScheme(.dark, for: .navigationBar)
        .sheet(isPresented: $showingOCR) {
            OCRReviewView(page: effectivePage, bookID: bookID)
        }
        .sheet(isPresented: $showingRecipe) {
            if let recipe = effectivePage.recipe {
                RecipeView(recipe: recipe, page: effectivePage, bookID: bookID)
            }
        }
    }

    private var actionPanel: some View {
        VStack(spacing: 12) {
            // Badge stato
            Text(effectivePage.status.label)
                .font(.heirloomCaption)
                .foregroundColor(.white)
                .padding(.horizontal, 12)
                .padding(.vertical, 4)
                .background(effectivePage.status.color)
                .cornerRadius(8)

            HStack(spacing: 12) {

                // OCR / Testo
                ActionButton(
                    icon: "text.viewfinder",
                    label: effectivePage.rawOCRText == nil ? "Esegui OCR" : "Modifica testo"
                ) {
                    showingOCR = true
                }

                // AI
                if effectivePage.recipe != nil {
                    ActionButton(
                        icon: "fork.knife",
                        label: "Vedi ricetta",
                        tint: .green
                    ) {
                        showingRecipe = true
                    }
                } else {
                    ActionButton(
                        icon: "wand.and.stars",
                        label: "Struttura AI",
                        tint: .purple
                    ) {
                        showingOCR = true
                    }
                }
            }
        }
        .padding(20)
        .frame(maxWidth: .infinity)
        .background(
            LinearGradient(
                colors: [.clear, .black.opacity(0.8)],
                startPoint: .top,
                endPoint: .bottom
            )
        )
    }
}

// MARK: - Action Button

struct ActionButton: View {
    let icon  : String
    let label : String
    var tint  : Color = Color.heirloomTerracotta
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 6) {
                Image(systemName: icon)
                    .font(.system(size: 20))
                Text(label)
                    .font(.heirloomCaption)
            }
            .foregroundColor(.white)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 14)
            .background(tint.opacity(0.85))
            .cornerRadius(12)
        }
        .buttonStyle(.plain)
    }
}
