import SwiftUI

struct BookCardView: View {
    let book: Book

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {

            // Cover
            ZStack {
                Color.heirloomTerracotta.opacity(0.08)
                Text(book.coverEmoji)
                    .font(.system(size: 48))
            }
            .frame(height: 110)
            .frame(maxWidth: .infinity)

            // Info
            VStack(alignment: .leading, spacing: 4) {
                Text(book.name)
                    .font(.heirloomBody)
                    .fontWeight(.medium)
                    .foregroundColor(.heirloomBrown)
                    .lineLimit(2)

                if !book.author.isEmpty {
                    Text(book.author)
                        .font(.heirloomCaption)
                        .foregroundColor(.heirloomMuted)
                        .lineLimit(1)
                }

                HStack(spacing: 4) {
                    if !book.year.isEmpty {
                        Text(book.year)
                            .font(.heirloomMono)
                            .foregroundColor(.heirloomMuted)
                    }
                    Spacer()
                    Text("\(book.pageCount) pag.")
                        .font(.heirloomCaption)
                        .foregroundColor(.heirloomMuted)
                }
                .padding(.top, 2)
            }
            .padding(10)
        }
        .cardStyle()
    }
}
