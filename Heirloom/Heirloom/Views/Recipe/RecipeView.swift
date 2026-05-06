import SwiftUI

struct RecipeView: View {
    @EnvironmentObject var store: BookStore
    @Environment(\.dismiss) var dismiss

    let recipe: Recipe
    let page: Page
    let bookID: UUID

    @State private var showingExport = false

    var body: some View {
        NavigationStack {
            ZStack(alignment: .bottomTrailing) {
                Color.heirloomCream.ignoresSafeArea()

                ScrollView {
                    VStack(alignment: .leading, spacing: 24) {

                        // Header ricetta
                        recipeHeader

                        // Ingredienti
                        if !recipe.ingredients.isEmpty {
                            ingredientsSection
                        }

                        // Preparazione
                        if !recipe.directions.isEmpty {
                            directionsSection
                        }

                        // Note
                        if !recipe.notes.isEmpty {
                            notesSection
                        }

                        // Tags
                        if !recipe.tags.isEmpty {
                            tagsSection
                        }

                        // Sorgente AI
                        aiSourceBadge

                        Spacer(minLength: 80)
                    }
                    .padding(20)
                }

                // FAB Esporta
                Button {
                    showingExport = true
                } label: {
                    HStack(spacing: 6) {
                        Image(systemName: "square.and.arrow.up")
                        Text("Esporta")
                            .font(.system(size: 14, weight: .semibold))
                    }
                    .foregroundColor(.white)
                    .padding(.horizontal, 20)
                    .padding(.vertical, 12)
                    .background(Color.heirloomTerracotta)
                    .clipShape(Capsule())
                }
                .padding(24)
            }
            .navigationTitle(recipe.title)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Chiudi") { dismiss() }
                }
            }
            .sheet(isPresented: $showingExport) {
                ExportView(recipe: recipe, page: page, bookID: bookID)
            }
        }
    }

    // MARK: - Sections

    private var recipeHeader: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(recipe.title)
                .font(.heirloomTitle)
                .foregroundColor(.heirloomBrown)

            HStack(spacing: 8) {
                Label(recipe.source, systemImage: "book.closed")
                    .font(.heirloomCaption)
                    .foregroundColor(.heirloomMuted)
                Spacer()
                if !recipe.servings.isEmpty {
                    Label(recipe.servings, systemImage: "person.2")
                        .font(.heirloomCaption)
                        .foregroundColor(.heirloomMuted)
                }
            }
        }
    }

    private var ingredientsSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Ingredienti")
                .eyebrowStyle

            VStack(alignment: .leading, spacing: 0) {
                ForEach(recipe.ingredients) { ingredient in
                    HStack(alignment: .top) {
                        Circle()
                            .fill(Color.heirloomTerracotta)
                            .frame(width: 5, height: 5)
                            .padding(.top, 8)
                        Text(ingredient.display)
                            .font(.heirloomBody)
                            .foregroundColor(.heirloomBrown)
                        Spacer()
                    }
                    .padding(.vertical, 6)

                    if ingredient.id != recipe.ingredients.last?.id {
                        Divider()
                    }
                }
            }
            .padding(14)
            .cardStyle()
        }
    }

    private var directionsSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Preparazione")
                .eyebrowStyle

            VStack(alignment: .leading, spacing: 12) {
                ForEach(Array(recipe.directions.enumerated()), id: \.offset) { idx, step in
                    HStack(alignment: .top, spacing: 12) {
                        Text("\(idx + 1)")
                            .font(.system(size: 13, weight: .bold))
                            .foregroundColor(.white)
                            .frame(width: 24, height: 24)
                            .background(Color.heirloomTerracotta)
                            .clipShape(Circle())
                            .padding(.top, 1)

                        Text(step)
                            .font(.heirloomBody)
                            .foregroundColor(.heirloomBrown)
                            .fixedSize(horizontal: false, vertical: true)

                        Spacer()
                    }
                }
            }
            .padding(14)
            .cardStyle()
        }
    }

    private var notesSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Note")
                .eyebrowStyle
            Text(recipe.notes)
                .font(.heirloomBody)
                .foregroundColor(.heirloomMuted)
                .italic()
                .padding(14)
                .cardStyle()
        }
    }

    private var tagsSection: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                ForEach(recipe.tags, id: \.self) { tag in
                    Text("#\(tag)")
                        .font(.heirloomCaption)
                        .foregroundColor(.heirloomTerracotta)
                        .padding(.horizontal, 10)
                        .padding(.vertical, 5)
                        .background(Color.heirloomTerracotta.opacity(0.1))
                        .cornerRadius(12)
                }
            }
        }
    }

    private var aiSourceBadge: some View {
        HStack(spacing: 6) {
            Image(systemName: "sparkles")
                .font(.system(size: 10))
            Text("Strutturato da AI · Heirloom by Recipees")
                .font(.heirloomMono)
        }
        .foregroundColor(.heirloomMuted)
        .padding(.top, 8)
    }
}
