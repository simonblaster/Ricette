import SwiftUI

struct LibraryView: View {
    @EnvironmentObject var store: BookStore
    @State private var showingNewBook = false

    var body: some View {
        NavigationStack {
            ZStack(alignment: .bottomTrailing) {
                Color.heirloomCream.ignoresSafeArea()

                ScrollView {
                    VStack(alignment: .leading, spacing: 24) {

                        // Hero
                        VStack(spacing: 4) {
                            Text("Heirloom.")
                                .font(.heirloomTitle)
                                .foregroundColor(.heirloomBrown)
                            Text("by Recipees")
                                .font(.heirloomMono)
                                .foregroundColor(.heirloomMuted)
                                .tracking(2)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.top, 8)

                        // Grid libri
                        VStack(alignment: .leading, spacing: 12) {
                            Text("I miei ricettari")
                                .eyebrowStyle

                            if store.books.isEmpty {
                                EmptyLibraryView(onAdd: { showingNewBook = true })
                            } else {
                                LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                                    ForEach(store.books) { book in
                                        NavigationLink(destination: BookDetailView(book: book)) {
                                            BookCardView(book: book)
                                        }
                                        .buttonStyle(.plain)
                                    }
                                }
                            }
                        }
                    }
                    .padding(20)
                }

                // FAB
                Button {
                    showingNewBook = true
                } label: {
                    Image(systemName: "plus")
                        .font(.system(size: 20, weight: .semibold))
                        .foregroundColor(.white)
                        .frame(width: 52, height: 52)
                        .background(Color.heirloomTerracotta)
                        .clipShape(Circle())
                }
                .padding(24)
            }
            .navigationBarHidden(true)
        }
        .sheet(isPresented: $showingNewBook) {
            NewBookView()
        }
    }
}

// MARK: - Empty State
struct EmptyLibraryView: View {
    var onAdd: () -> Void

    var body: some View {
        VStack(spacing: 16) {
            Text("📖")
                .font(.system(size: 48))
            Text("Nessun ricettario ancora")
                .font(.heirloomBody)
                .foregroundColor(.heirloomBrown)
            Text("Aggiungi il primo ricettario\ndi nonna, mamma o zia")
                .font(.system(size: 13))
                .foregroundColor(.heirloomMuted)
                .multilineTextAlignment(.center)
            Button("Aggiungi ricettario") { onAdd() }
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

// MARK: - New Book Sheet
struct NewBookView: View {
    @EnvironmentObject var store: BookStore
    @Environment(\.dismiss) var dismiss

    @State private var name   = ""
    @State private var author = ""
    @State private var year   = ""
    @State private var emoji  = "📖"

    let emojiOptions = ["📖", "📗", "📘", "📕", "📙", "📓", "📔"]

    var body: some View {
        NavigationStack {
            Form {
                Section("Ricettario") {
                    TextField("Nome (es. Ricettario nonna)", text: $name)
                    TextField("Autore (es. Nonna Concetta)", text: $author)
                    TextField("Anno (es. 1962)", text: $year)
                        .keyboardType(.numberPad)
                }
                Section("Copertina") {
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack {
                            ForEach(emojiOptions, id: \.self) { e in
                                Text(e)
                                    .font(.system(size: 32))
                                    .padding(8)
                                    .background(e == emoji ? Color.heirloomTerracotta.opacity(0.15) : Color.clear)
                                    .cornerRadius(8)
                                    .onTapGesture { emoji = e }
                            }
                        }
                    }
                }
            }
            .navigationTitle("Nuovo ricettario")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Annulla") { dismiss() }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Aggiungi") {
                        let book = Book(name: name, author: author, year: year, coverEmoji: emoji)
                        store.addBook(book)
                        dismiss()
                    }
                    .disabled(name.isEmpty)
                }
            }
        }
    }
}
