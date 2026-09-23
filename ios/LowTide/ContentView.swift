import SwiftUI
import UIKit

struct ContentView: View {
    var body: some View {
        // SwiftUI keeps the web view inside the safe area. The ink background
        // fills the status bar and home indicator.
        GameWebView()
            .background(Color(uiColor: HarborColor.ui).ignoresSafeArea())
            .preferredColorScheme(.dark)
    }
}
