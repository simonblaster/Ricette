import SwiftUI

// MARK: - Brand Colors (Recipees identity)
extension Color {
    static let heirloomTerracotta = Color(hex: "#a83d20")
    static let heirloomCream      = Color(hex: "#faf8f3")
    static let heirloomBrown      = Color(hex: "#1a1714")
    static let heirloomMuted      = Color(hex: "#857c6e")
    static let heirloomBorder     = Color(hex: "#e0ddd5")

    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let r = Double((int >> 16) & 0xFF) / 255
        let g = Double((int >> 8)  & 0xFF) / 255
        let b = Double(int         & 0xFF) / 255
        self.init(red: r, green: g, blue: b)
    }
}

// MARK: - Typography
extension Font {
    static let heirloomTitle    = Font.custom("Georgia", size: 28).weight(.medium)
    static let heirloomHeading  = Font.custom("Georgia", size: 20).weight(.medium)
    static let heirloomBody     = Font.system(size: 15)
    static let heirloomCaption  = Font.system(size: 11, weight: .medium)
    static let heirloomMono     = Font.system(size: 10, design: .monospaced)
}

// MARK: - Common Modifiers
struct CardModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .background(Color.white)
            .cornerRadius(12)
            .overlay(RoundedRectangle(cornerRadius: 12).stroke(Color.heirloomBorder, lineWidth: 0.5))
    }
}

extension View {
    func cardStyle() -> some View { modifier(CardModifier()) }

    var eyebrowStyle: some View {
        self.font(.system(size: 10, weight: .semibold, design: .default))
            .tracking(2)
            .foregroundColor(.heirloomMuted)
    }
}

// MARK: - App Constants
enum HeirloomConstants {
    static let timerOptions: [Double] = [3, 5, 8]
    static let defaultTimer: Double   = 5
    static let apiBaseURL             = "https://api.anthropic.com/v1/messages"
    static let claudeModel            = "claude-haiku-4-5"
    static let maxCreditsStarter      = 50
}
