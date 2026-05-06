import Vision
import UIKit

// OCRService: estrae testo da immagini usando Vision.framework (on-device, gratuito, offline)
// Supporta italiano e testi misti italiano/inglese

actor OCRService {

    static let shared = OCRService()

    // MARK: - Riconoscimento testo

    func recognizeText(in image: UIImage) async throws -> String {
        guard let cgImage = image.cgImage else {
            throw OCRError.invalidImage
        }

        return try await withCheckedThrowingContinuation { continuation in
            let request = VNRecognizeTextRequest { request, error in
                if let error {
                    continuation.resume(throwing: error)
                    return
                }
                let observations = request.results as? [VNRecognizedTextObservation] ?? []
                let text = observations
                    .compactMap { $0.topCandidates(1).first?.string }
                    .joined(separator: "\n")
                continuation.resume(returning: text)
            }

            // Configurazione ottimale per ricette manoscritte
            request.recognitionLevel       = .accurate
            request.usesLanguageCorrection = true
            request.recognitionLanguages   = ["it-IT", "en-US"]
            request.minimumTextHeight      = 0.01  // cattura anche testo piccolo

            let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
            do {
                try handler.perform([request])
            } catch {
                continuation.resume(throwing: error)
            }
        }
    }

    // MARK: - Elaborazione da file su disco

    func recognizeText(fromFile url: URL) async throws -> String {
        guard
            let data  = try? Data(contentsOf: url),
            let image = UIImage(data: data)
        else {
            throw OCRError.fileNotFound
        }
        return try await recognizeText(in: image)
    }
}

// MARK: - Errors

enum OCRError: LocalizedError {
    case invalidImage
    case fileNotFound

    var errorDescription: String? {
        switch self {
        case .invalidImage:  return "Immagine non valida per il riconoscimento testo"
        case .fileNotFound:  return "File immagine non trovato"
        }
    }
}
