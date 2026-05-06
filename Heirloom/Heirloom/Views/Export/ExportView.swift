import SwiftUI

struct ExportView: View {
    @EnvironmentObject var store: BookStore
    @Environment(\.dismiss) var dismiss

    let recipe: Recipe
    let page: Page
    let bookID: UUID

    @State private var selectedFormat: ExportService.ExportFormat = .plainText
    @State private var exportedItem: ExportedItem?
    @State private var errorMessage: String?
    @State private var isExporting  = false

    var body: some View {
        NavigationStack {
            ZStack {
                Color.heirloomCream.ignoresSafeArea()

                VStack(spacing: 28) {

                    // Icona ricetta
                    VStack(spacing: 8) {
                        Text("📤")
                            .font(.system(size: 48))
                        Text(recipe.title)
                            .font(.heirloomHeading)
                            .foregroundColor(.heirloomBrown)
                            .multilineTextAlignment(.center)
                        Text(recipe.source)
                            .font(.heirloomCaption)
                            .foregroundColor(.heirloomMuted)
                    }
                    .padding(.top, 8)

                    // Selettore formato
                    VStack(alignment: .leading, spacing: 10) {
                        Text("Formato")
                            .eyebrowStyle
                            .padding(.horizontal, 20)

                        ForEach(ExportService.ExportFormat.allCases) { format in
                            FormatRowView(
                                format: format,
                                isSelected: selectedFormat == format
                            ) {
                                selectedFormat = format
                            }
                        }
                    }

                    if let err = errorMessage {
                        Text(err)
                            .font(.heirloomCaption)
                            .foregroundColor(.red)
                            .padding(.horizontal, 20)
                    }

                    Spacer()

                    // Bottone esporta
                    Button {
                        doExport()
                    } label: {
                        HStack(spacing: 8) {
                            if isExporting {
                                ProgressView().tint(.white).scaleEffect(0.85)
                            } else {
                                Image(systemName: "square.and.arrow.up")
                            }
                            Text("Esporta \(selectedFormat.rawValue)")
                                .fontWeight(.semibold)
                        }
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 14)
                        .background(Color.heirloomTerracotta)
                        .cornerRadius(12)
                    }
                    .disabled(isExporting)
                    .padding(.horizontal, 20)
                    .padding(.bottom, 16)
                }
            }
            .navigationTitle("Esporta ricetta")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Chiudi") { dismiss() }
                }
            }
            .sheet(item: $exportedItem) { item in
                ShareSheet(activityItems: [item.url])
            }
        }
    }

    // MARK: - Export

    private func doExport() {
        isExporting = true
        errorMessage = nil

        Task {
            do {
                let data = try ExportService.shared.export(recipe: recipe, format: selectedFormat)
                let name = ExportService.shared.fileName(for: recipe, format: selectedFormat)
                let tmpURL = FileManager.default.temporaryDirectory.appendingPathComponent(name)
                try data.write(to: tmpURL)

                // Marca come esportata
                var updatedPage = page
                updatedPage.status = .exported
                store.updatePage(updatedPage, inBook: bookID)

                await MainActor.run {
                    isExporting  = false
                    exportedItem = ExportedItem(url: tmpURL)
                }
            } catch {
                await MainActor.run {
                    isExporting  = false
                    errorMessage = error.localizedDescription
                }
            }
        }
    }
}

// MARK: - Format Row

struct FormatRowView: View {
    let format   : ExportService.ExportFormat
    let isSelected: Bool
    let onTap    : () -> Void

    var body: some View {
        Button(action: onTap) {
            HStack(spacing: 14) {
                Image(systemName: format.icon)
                    .font(.system(size: 18))
                    .frame(width: 28)
                    .foregroundColor(isSelected ? .heirloomTerracotta : .heirloomBrown)

                VStack(alignment: .leading, spacing: 2) {
                    Text(format.rawValue)
                        .font(.heirloomBody)
                        .foregroundColor(.heirloomBrown)
                    Text(".\(format.fileExtension)")
                        .font(.heirloomMono)
                        .foregroundColor(.heirloomMuted)
                }
                Spacer()
                if isSelected {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundColor(.heirloomTerracotta)
                }
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
            .background(isSelected ? Color.heirloomTerracotta.opacity(0.06) : Color.white)
            .overlay(
                RoundedRectangle(cornerRadius: 10)
                    .stroke(
                        isSelected ? Color.heirloomTerracotta.opacity(0.4) : Color.heirloomBorder,
                        lineWidth: isSelected ? 1 : 0.5
                    )
            )
            .cornerRadius(10)
            .padding(.horizontal, 20)
        }
        .buttonStyle(.plain)
        .animation(.easeInOut(duration: 0.15), value: isSelected)
    }
}

// MARK: - Helpers

struct ExportedItem: Identifiable {
    let id  = UUID()
    let url : URL
}

struct ShareSheet: UIViewControllerRepresentable {
    let activityItems: [Any]

    func makeUIViewController(context: Context) -> UIActivityViewController {
        UIActivityViewController(activityItems: activityItems, applicationActivities: nil)
    }

    func updateUIViewController(_ uiViewController: UIActivityViewController, context: Context) {}
}
