import SwiftUI
import AVFoundation

struct AcquisitionView: View {
    @EnvironmentObject var store: BookStore
    @Environment(\.dismiss) var dismiss
    let bookID: UUID

    @StateObject private var camera = CameraService()
    @State private var isAutoMode   = false
    @State private var showDone     = false

    var body: some View {
        ZStack {
            Color.black.ignoresSafeArea()

            VStack(spacing: 0) {

                // Top bar
                topBar

                // Preview fotocamera
                CameraPreviewView(session: camera.session)
                    .overlay(captureFlash)
                    .overlay(lastCaptureThumb, alignment: .bottomLeading)

                // Pannello controlli
                controlPanel
            }
        }
        .onAppear {
            camera.setup()
            camera.start()
        }
        .onDisappear { camera.stop() }
        .sheet(isPresented: $showDone) {
            AcquisitionSummaryView(
                bookID: bookID,
                fileNames: camera.drainCapturedFileNames(),
                count: camera.capturedCount
            )
        }
        .alert("Errore fotocamera", isPresented: .constant(camera.error != nil)) {
            Button("OK") { dismiss() }
        } message: {
            Text(camera.error ?? "")
        }
    }

    // MARK: - Subviews

    private var topBar: some View {
        HStack {
            Button { finishSession() } label: {
                Image(systemName: "xmark")
                    .font(.system(size: 18, weight: .medium))
                    .foregroundColor(.white)
                    .padding(12)
            }

            Spacer()

            Text("\(camera.capturedCount) pagine")
                .font(.heirloomBody)
                .foregroundColor(.white)

            Spacer()

            // Timer selector
            Menu {
                ForEach(HeirloomConstants.timerOptions, id: \.self) { sec in
                    Button("\(Int(sec)) secondi") {
                        camera.timerValue = sec
                    }
                }
            } label: {
                Label("\(Int(camera.timerValue))s", systemImage: "timer")
                    .font(.system(size: 14, weight: .medium))
                    .foregroundColor(.white)
                    .padding(12)
            }
        }
        .padding(.horizontal, 8)
        .background(Color.black.opacity(0.6))
    }

    private var captureFlash: some View {
        Color.white
            .opacity(camera.isCapturing ? 0.6 : 0)
            .ignoresSafeArea()
            .animation(.easeOut(duration: 0.15), value: camera.isCapturing)
    }

    private var lastCaptureThumb: some View {
        Group {
            if let img = camera.lastCapture {
                Image(uiImage: img)
                    .resizable()
                    .scaledToFill()
                    .frame(width: 56, height: 80)
                    .clipped()
                    .cornerRadius(6)
                    .overlay(RoundedRectangle(cornerRadius: 6).stroke(Color.white, lineWidth: 1.5))
                    .padding(12)
            }
        }
    }

    private var controlPanel: some View {
        VStack(spacing: 20) {

            // Countdown visualizzato
            if isAutoMode {
                CountdownArc(progress: camera.countdown / camera.timerValue)
                    .frame(width: 60, height: 60)
                    .overlay(
                        Text(String(format: "%.1f", max(0, camera.countdown)))
                            .font(.system(size: 14, weight: .semibold, design: .monospaced))
                            .foregroundColor(.white)
                    )
            }

            HStack(spacing: 40) {

                // Scatto manuale
                Button {
                    camera.capturePhoto()
                } label: {
                    Image(systemName: "camera.circle.fill")
                        .font(.system(size: 52))
                        .foregroundColor(.white)
                }
                .disabled(isAutoMode)
                .opacity(isAutoMode ? 0.4 : 1)

                // Auto / Stop
                Button {
                    isAutoMode.toggle()
                    if isAutoMode {
                        camera.startAutoCapture()
                    } else {
                        camera.stopAutoCapture()
                    }
                } label: {
                    VStack(spacing: 4) {
                        Image(systemName: isAutoMode ? "stop.circle.fill" : "play.circle.fill")
                            .font(.system(size: 52))
                            .foregroundColor(isAutoMode ? .red : .heirloomTerracotta)
                        Text(isAutoMode ? "Stop" : "Auto")
                            .font(.heirloomCaption)
                            .foregroundColor(.white)
                    }
                }
            }

            // Fine sessione
            if camera.capturedCount > 0 {
                Button("Fine — salva \(camera.capturedCount) pagine") {
                    finishSession()
                }
                .font(.system(size: 14, weight: .semibold))
                .foregroundColor(.white)
                .padding(.horizontal, 28)
                .padding(.vertical, 12)
                .background(Color.heirloomTerracotta)
                .clipShape(Capsule())
            }
        }
        .padding(.vertical, 24)
        .frame(maxWidth: .infinity)
        .background(Color.black.opacity(0.85))
    }

    private func finishSession() {
        camera.stopAutoCapture()
        if camera.capturedCount > 0 {
            showDone = true
        } else {
            dismiss()
        }
    }
}

// MARK: - Camera Preview (UIViewRepresentable)

struct CameraPreviewView: UIViewRepresentable {
    let session: AVCaptureSession

    func makeUIView(context: Context) -> PreviewUIView {
        let view = PreviewUIView()
        view.session = session
        return view
    }

    func updateUIView(_ uiView: PreviewUIView, context: Context) {}

    class PreviewUIView: UIView {
        var session: AVCaptureSession? {
            didSet {
                guard let s = session else { return }
                (layer as! AVCaptureVideoPreviewLayer).session = s
            }
        }
        override class var layerClass: AnyClass { AVCaptureVideoPreviewLayer.self }
        override func layoutSubviews() {
            super.layoutSubviews()
            (layer as! AVCaptureVideoPreviewLayer).videoGravity = .resizeAspectFill
        }
    }
}

// MARK: - Countdown Arc

struct CountdownArc: View {
    let progress: Double  // 0…1

    var body: some View {
        ZStack {
            Circle()
                .stroke(Color.white.opacity(0.2), lineWidth: 4)
            Circle()
                .trim(from: 0, to: CGFloat(progress))
                .stroke(Color.heirloomTerracotta, style: StrokeStyle(lineWidth: 4, lineCap: .round))
                .rotationEffect(.degrees(-90))
                .animation(.linear(duration: 0.1), value: progress)
        }
    }
}

// MARK: - Acquisition Summary

struct AcquisitionSummaryView: View {
    @EnvironmentObject var store: BookStore
    @Environment(\.dismiss) var dismiss

    let bookID: UUID
    let fileNames: [String]
    let count: Int

    @State private var startPage: String = ""
    @State private var didSave = false

    var body: some View {
        NavigationStack {
            VStack(spacing: 24) {
                Text("🎉")
                    .font(.system(size: 56))
                Text("Scattate \(count) pagine")
                    .font(.heirloomHeading)
                    .foregroundColor(.heirloomBrown)
                Text("Da quale numero di pagina iniziano?")
                    .font(.heirloomBody)
                    .foregroundColor(.heirloomMuted)

                TextField("Numero prima pagina (es. 1)", text: $startPage)
                    .keyboardType(.numberPad)
                    .multilineTextAlignment(.center)
                    .font(.system(size: 28, weight: .medium))
                    .padding()
                    .background(Color.white)
                    .cornerRadius(10)
                    .overlay(RoundedRectangle(cornerRadius: 10).stroke(Color.heirloomBorder))
                    .padding(.horizontal, 40)

                Button("Salva pagine") {
                    savePages()
                }
                .disabled(startPage.isEmpty)
                .font(.system(size: 16, weight: .semibold))
                .foregroundColor(.white)
                .padding(.horizontal, 40)
                .padding(.vertical, 14)
                .frame(maxWidth: .infinity)
                .background(startPage.isEmpty ? Color.heirloomMuted : Color.heirloomTerracotta)
                .cornerRadius(12)
                .padding(.horizontal, 40)
                .animation(.easeInOut, value: startPage)
            }
            .padding(24)
            .navigationTitle("Salva acquisizione")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Salta") { dismiss() }
                }
            }
        }
    }

    private func savePages() {
        let start = Int(startPage) ?? 1
        for (idx, name) in fileNames.enumerated() {
            let page = Page(number: start + idx, imageFileName: name)
            store.addPage(page, toBook: bookID)
        }
        dismiss()
    }
}
