import SwiftUI

struct BookDetailView: View {
    @EnvironmentObject var store: BookStore
    let book: Book

    @State private var showingAcquisition = false
    @State private var showingDeleteAlert = false
    @Environment(\.dismiss) var dismiss

    // Libro aggiornato in tempo reale dallo store
    var currentBook: Book {
        store.books.first { $0.id == book.id } ?? book
    }

    var body: some View {
        ZStack(alignment: .bottomTrailing) {
            Color.heirloomCream.ignoresSafeArea()

            ScrollView {
                VStack(alignment: .leading, spacing: 24) {

                    // Header libro
                    BookHeaderView(book: currentBook)

                    // Statistiche
                    StatsRowView(book: currentBook)

                    // Griglia pagine
                    if currentBook.pages.isEmpty {
                        EmptyPagesView(onAcquire: { showingAcquisition = true })
                    } else {
                        PagesGridView(book: currentBook)
                    }
                }
                .padding(20)
                .padding(.bottom, 80) // spazio FAB
            }

            // FAB — aggiungi pagine
            Button {
                showingAcquisition = true
            } label: {
                HStack(spacing: 8) {
                    Image(systemName: "camera.fill")
                    Text("Acquisisci")
                        .font(.system(size: 14, weight: .semibold))
                }
                .foregroundColor(.white)
                .padding(.horizontal, 20)
                .padding(.vertical, 14)
                .background(Color.heirloomTerracotta)
                .clipShape(Capsule())
            }
            .padding(24)
        }
        .navigationTitle(currentBook.name)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Menu {
                    Button(role: .destructive) {
                        showingDeleteAlert = true
                    } label: {
                        Label("Elimina ricettario", systemImage: "trash")
                    }
                } label: {
                    Image(systemName: "ellipsis.circle")
                        .foregroundColor(.heirloomBrown)
                }
            }
        }
        .fullScreenCover(isPresented: $showingAcquisition) {
            AcquisitionView(bookID: currentBook.id)
        }
        .alert("Elimina ricettario?", isPresented: $showingDeleteAlert) {
            Button("Elimina", role: .destructive) {
                store.deleteBook(id: currentBook.id)
                dismiss()
            }
            Button("Annulla", role: .cancel) {}
        } message: {
            Text("Tutte le pagine e ricette saranno eliminate. L'azione non è reversibile.")
        }
    }
}

// MARK: - Sub-components

struct BookHeaderView: View {
    let book: Book

    var body: some View {
        HStack(spacing: 16) {
            Text(book.coverEmoji)
                .font(.system(size: 56))
                .frame(width: 80, height: 80)
                .background(Color.heirloomTerracotta.opacity(0.08))
                .cornerRadius(12)

            VStack(alignment: .leading, spacing: 4) {
                Text(book.name)
                    .font(.heirloomHeading)
                    .foregroundColor(.heirloomBrown)
                if !book.author.isEmpty {
                    Text(book.author)
                        .font(.heirloomBody)
                        .foregroundColor(.heirloomMuted)
                }
                if !book.year.isEmpty {
                    Text(book.year)
                        .font(.heirloomMono)
                        .foregroundColor(.heirloomMuted)
                        .tracking(1)
                }
            }
        }
    }
}

struct StatsRowView: View {
    let book: Book

    var body: some View {
        HStack(spacing: 0) {
            StatItemView(value: "\(book.pageCount)", label: "Pagine")
            Divider().frame(height: 30)
            StatItemView(value: "\(book.recipeCount)", label: "Ricette AI")
            Divider().frame(height: 30)
            StatItemView(
                value: "\(book.pages.filter { $0.status == .exported }.count)",
                label: "Esportate"
            )
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 12)
        .cardStyle()
    }
}

struct StatItemView: View {
    let value: String
    let label: String

    var body: some View {
        VStack(spacing: 2) {
            Text(value)
                .font(.system(size: 22, weight: .semibold))
                .foregroundColor(.heirloomBrown)
            Text(label)
                .font(.heirloomCaption)
                .foregroundColor(.heirloomMuted)
        }
        .frame(maxWidth: .infinity)
    }
}

struct EmptyPagesView: View {
    let onAcquire: () -> Void

    var body: some View {
        VStack(spacing: 16) {
            Text("📷")
                .font(.system(size: 48))
            Text("Nessuna pagina ancora")
                .font(.heirloomBody)
                .foregroundColor(.heirloomBrown)
            Text("Premi Acquisisci per fotografare\nle pagine del ricettario")
                .font(.system(size: 13))
                .foregroundColor(.heirloomMuted)
                .multilineTextAlignment(.center)
            Button("Acquisisci pagine") { onAcquire() }
                .font(.system(size: 14, weight: .medium))
                .foregroundColor(.white)
                .padding(.horizontal, 24)
                .padding(.vertical, 12)
                .background(Color.heirloomTerracotta)
                .cornerRadius(10)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 40)
    }
}

struct PagesGridView: View {
    let book: Book

    let columns = [GridItem(.flexible()), GridItem(.flexible()), GridItem(.flexible())]

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Pagine (\(book.pageCount))")
                .eyebrowStyle

            LazyVGrid(columns: columns, spacing: 10) {
                ForEach(book.pages.sorted { $0.number < $1.number }) { page in
                    NavigationLink(destination: PageDetailView(page: page, bookID: book.id)) {
                        PageThumbnailView(page: page)
                    }
                    .buttonStyle(.plain)
                }
            }
        }
    }
}

struct PageThumbnailView: View {
    let page: Page

    var body: some View {
        ZStack(alignment: .bottomLeading) {
            // Immagine o placeholder
            Group {
                if let url = page.imageURL, let uiImage = UIImage(contentsOfFile: url.path) {
                    Image(uiImage: uiImage)
                        .resizable()
                        .scaledToFill()
                } else {
                    Color.heirloomBorder
                    Image(systemName: "doc.text")
                        .foregroundColor(.heirloomMuted)
                        .font(.system(size: 24))
                }
            }
            .frame(height: 110)
            .clipped()

            // Badge stato
            Text(page.status.label)
                .font(.system(size: 8, weight: .bold))
                .foregroundColor(.white)
                .padding(.horizontal, 5)
                .padding(.vertical, 2)
                .background(page.status.color)
                .cornerRadius(4)
                .padding(4)
        }
        .frame(height: 110)
        .cornerRadius(8)
        .overlay(RoundedRectangle(cornerRadius: 8).stroke(Color.heirloomBorder, lineWidth: 0.5))

        // Numero pagina
        Text("p.\(page.number)")
            .font(.heirloomCaption)
            .foregroundColor(.heirloomMuted)
            .padding(.top, 2)
    }
}
