import SwiftUI

@main
struct HeirloomApp: App {
    @StateObject private var store = BookStore()

    var body: some Scene {
        WindowGroup {
            LibraryView()
                .environmentObject(store)
        }
    }
}
