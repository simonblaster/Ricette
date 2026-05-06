import AVFoundation
import UIKit
import Combine

// CameraService gestisce:
// 1. Sessione AVFoundation (preview + capture)
// 2. Timer automatico per lo scatto sequenziale
// 3. Salvataggio immagini su disco (Documents/photos/)

@MainActor
class CameraService: NSObject, ObservableObject {

    // MARK: - Published
    @Published var isRunning   = false
    @Published var timerValue  : Double = HeirloomConstants.defaultTimer  // secondi tra scatti
    @Published var countdown   : Double = 0
    @Published var lastCapture : UIImage? = nil
    @Published var capturedCount: Int = 0
    @Published var isCapturing  = false  // true durante il flash/feedback visivo
    @Published var error        : String? = nil

    // MARK: - Internal
    let session       = AVCaptureSession()
    private var output = AVCapturePhotoOutput()
    private var timerCancellable: AnyCancellable?
    private var countdownCancellable: AnyCancellable?

    private var savedFileNames: [String] = []  // nomi file nell'ordine di cattura

    // Cartella foto
    private var photosDir: URL {
        let docs = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        return docs.appendingPathComponent("photos", isDirectory: true)
    }

    // MARK: - Setup

    func setup() {
        session.beginConfiguration()
        session.sessionPreset = .photo

        // Input — fotocamera posteriore
        guard
            let device = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .back),
            let input  = try? AVCaptureDeviceInput(device: device),
            session.canAddInput(input)
        else {
            error = "Impossibile accedere alla fotocamera"
            session.commitConfiguration()
            return
        }
        session.addInput(input)

        // Output
        guard session.canAddOutput(output) else {
            error = "Impossibile configurare l'output foto"
            session.commitConfiguration()
            return
        }
        output.isHighResolutionCaptureEnabled = true
        session.addOutput(output)

        session.commitConfiguration()

        // Crea cartella foto se non esiste
        try? FileManager.default.createDirectory(at: photosDir, withIntermediateDirectories: true)
    }

    func start() {
        guard !session.isRunning else { return }
        Task.detached { [weak self] in
            self?.session.startRunning()
            await MainActor.run { self?.isRunning = true }
        }
    }

    func stop() {
        timerCancellable?.cancel()
        countdownCancellable?.cancel()
        Task.detached { [weak self] in
            self?.session.stopRunning()
            await MainActor.run {
                self?.isRunning   = false
                self?.countdown   = 0
            }
        }
    }

    // MARK: - Timer automatico

    func startAutoCapture() {
        countdown = timerValue
        // Countdown visivo ogni 0.1 s
        countdownCancellable = Timer.publish(every: 0.1, on: .main, in: .common)
            .autoconnect()
            .sink { [weak self] _ in
                guard let self else { return }
                self.countdown -= 0.1
                if self.countdown <= 0 {
                    self.countdown = self.timerValue
                    self.capturePhoto()
                }
            }
    }

    func stopAutoCapture() {
        countdownCancellable?.cancel()
        countdown = 0
    }

    // MARK: - Scatto singolo

    func capturePhoto() {
        let settings = AVCapturePhotoSettings()
        settings.isHighResolutionPhotoEnabled = true
        output.capturePhoto(with: settings, delegate: self)
    }

    // MARK: - File management

    /// Restituisce i nomi file nell'ordine di cattura (da passare a BookStore)
    func drainCapturedFileNames() -> [String] {
        defer { savedFileNames = [] }
        return savedFileNames
    }

    private func saveImage(_ image: UIImage) -> String? {
        let name = "page_\(UUID().uuidString).jpg"
        let url  = photosDir.appendingPathComponent(name)
        guard let data = image.jpegData(compressionQuality: 0.85) else { return nil }
        try? data.write(to: url)
        return name
    }
}

// MARK: - AVCapturePhotoCaptureDelegate

extension CameraService: AVCapturePhotoCaptureDelegate {
    nonisolated func photoOutput(
        _ output: AVCapturePhotoOutput,
        didFinishProcessingPhoto photo: AVCapturePhoto,
        error: Error?
    ) {
        guard
            error == nil,
            let data  = photo.fileDataRepresentation(),
            let image = UIImage(data: data)
        else { return }

        Task { @MainActor [weak self] in
            guard let self else { return }
            if let name = self.saveImage(image) {
                self.savedFileNames.append(name)
            }
            self.lastCapture  = image
            self.capturedCount += 1
            self.isCapturing  = true
            // Feedback visivo breve
            try? await Task.sleep(nanoseconds: 200_000_000)
            self.isCapturing = false
        }
    }
}
