import SwiftUI

// OCRReviewView: mostra il testo OCR grezzo e permette di correggerlo
// prima di mandarlo a Claude per la strutturazione

struct OCRReviewView: View {
    @EnvironmentObject var store: BookStore
    @Environment(\.dismiss) var dismiss

    let page: Page
    let bookID: UUID

    @State private var editedText: String
    @State private var isProcessingOCR  = false
    @State private var isProcessingAI   = false
    @State private var errorMessage: String?
    @State private var showingRecipe    = false
    @State private var generatedRecipe  : Recipe?

    init(page: Page, bookID: UUID) {
        self.page   = page
        self.bookID = bookID
        _editedText = State(initialValue: page.rawOCRText ?? "")
    }

    private var currentBook: Book? {
        store.books.first { $0.id == bookID }
    }

    var body: some View {
        NavigationStack {
            ZStack {
                Color.heirloomCream.ignoresSafeArea()

                VStack(spacing: 0) {

                    // Immagine pagina (collassabile)
                    if let url = page.imageURL, let img = UIImage(contentsOfFile: url.path) {
                        Image(uiImage: img)
                            .resizable()
                            .scaledToFit()
                            .frame(maxHeight: 220)
                            .cornerRadius(8)
                            .padding(16)
                    }

                    Divider()

                    // Testo OCR editabile
                    ScrollView {
                        VStack(alignment: .leading, spacing: 12) {
                            HStack {
                                Text("Testo riconosciuto")
                                    .eyebrowStyle
                                Spacer()
                                if isProcessingOCR {
                                    ProgressView()
                                        .scaleEffect(0.8)
                                } else if editedText.isEmpty {
                                    Button("Esegui OCR") { runOCR() }
                                        .font(.system(size: 12, weight: .medium))
                                        .foregroundColor(.heirloomTerracotta)
                                }
                            }

                            TextEditor(text: $editedText)
                                .font(.system(size: 14))
                                .frame(minHeight: 180)
                                .padding(8)
                                .background(Color.white)
                                .cornerRadius(8)
                                .overlay(
                                    RoundedRectangle(cornerRadius: 8)
                                        .stroke(Color.heirloomBorder, lineWidth: 0.5)
                                )

                            if let err = errorMessage {
                                Text(err)
                                    .font(.heirloomCaption)
                                    .foregroundColor(.red)
                                    .padding(.top, 4)
                            }
                        }
                        .padding(16)
                    }

                    // Bottone AI
                    aiButton
                }
            }
            .navigationTitle("Pagina \(page.number)")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Chiudi") { dismiss() }
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Salva testo") { saveOCRText() }
                        .disabled(editedText == page.rawOCRText)
                }
            }
            .sheet(isPresented: $showingRecipe) {
                if let recipe = generatedRecipe {
                    RecipeView(recipe: recipe, page: page, bookID: bookID)
                }
            }
        }
        .onAppear {
            // Se non c'è ancora testo OCR, lo eseguiamo automaticamente
            if editedText.isEmpty && page.imageURL != nil {
                runOCR()
            }
        }
    }

    // MARK: - AI Button

    private var aiButton: some View {
        VStack(spacing: 0) {
            Divider()
            VStack(spacing: 8) {
                Button {
                    runAI()
                } label: {
                    HStack(spacing: 8) {
                        if isProcessingAI {
                            ProgressView()
                                .tint(.white)
                                .scaleEffect(0.85)
                        } else {
                            Image(systemName: "wand.and.stars")
                        }
                        Text(isProcessingAI ? "Elaborazione…" : "Struttura con AI")
                            .fontWeight(.semibold)
                    }
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 14)
                    .background(editedText.isEmpty ? Color.heirloomMuted : Color.heirloomTerracotta)
                    .cornerRadius(12)
                }
                .disabled(editedText.isEmpty || isProcessingAI)

                // Crediti disponibili
                if let book = currentBook {
                    let _ = book  // suppress unused warning
                    Text("\(store.credits) crediti rimasti")
                        .font(.heirloomCaption)
                        .foregroundColor(.heirloomMuted)
                }
            }
            .padding(16)
            .background(Color.heirloomCream)
        }
    }

    // MARK: - Actions

    private func runOCR() {
        guard let url = page.imageURL else { return }
        isProcessingOCR = true
        errorMessage = nil

        Task {
            do {
                let text = try await OCRService.shared.recognizeText(fromFile: url)
                await MainActor.run {
                    editedText = text
                    isProcessingOCR = false
                    // Salva subito il testo OCR nella pagina
                    var updatedPage = page
                    updatedPage.rawOCRText = text
                    updatedPage.status = .ocrDone
                    store.updatePage(updatedPage, inBook: bookID)
                }
            } catch {
                await MainActor.run {
                    errorMessage = error.localizedDescription
                    isProcessingOCR = false
                }
            }
        }
    }

    private func saveOCRText() {
        var updatedPage = page
        updatedPage.rawOCRText = editedText
        updatedPage.status = .ocrDone
        store.updatePage(updatedPage, inBook: bookID)
    }

    private func runAI() {
        guard store.useCredit() else {
            errorMessage = "Crediti esauriti."
            return
        }

        isProcessingAI = true
        errorMessage = nil

        let book = currentBook
        Task {
            do {
                let recipe = try await ClaudeService.shared.structureRecipe(
                    ocrText: editedText,
                    bookAuthor: book?.author ?? "",
                    bookYear: book?.year ?? "",
                    pageNumber: page.number
                )
                await MainActor.run {
                    generatedRecipe = recipe
                    isProcessingAI  = false
                    // Aggiorna la pagina con la ricetta strutturata
                    var updatedPage = page
                    updatedPage.recipe = recipe
                    updatedPage.status = .structured
                    store.updatePage(updatedPage, inBook: bookID)
                    showingRecipe = true
                }
            } catch {
                await MainActor.run {
                    errorMessage = error.localizedDescription
                    isProcessingAI = false
                    // Restituisci il credito in caso di errore
                    // (nella versione prod: gestisci lato server)
                }
            }
        }
    }
}
