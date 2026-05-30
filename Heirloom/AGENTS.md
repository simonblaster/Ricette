# Modalità non-distruttiva — REGOLA FERREA (Memoria iOS)

Memoria è in beta amici dal 2026 con utenti reali che ci hanno affidato ricette
di famiglia digitalizzate con ore di lavoro. **Il dato dell'utente è sacro.**
Un update che cancella o corrompe dati preesistenti è un fallimento grave:
distrugge la fiducia, e la fiducia è il prodotto.

---

## 1. Migration-safe su ogni cambio di schema Codable

`Book`, `Page`, `Recipe`, `Ingredient` e qualsiasi altro tipo persistito in
`books.json` usano il `Codable` sintetizzato o un `init(from:)` custom. La
regola è la stessa in entrambi i casi:

**Ogni campo nuovo deve usare `decodeIfPresent`, non `decode` / default value.**

Il `Codable` sintetizzato di Swift NON usa i default value in fase di
decodifica: per una chiave assente chiama `decode(forKey:)` che lancia
`keyNotFound`. Un file `books.json` scritto prima dell'aggiunta del nuovo
campo non ha quella chiave → tutta la decodifica del tipo fallisce → dati
persi.

```swift
// ❌ SBAGLIATO — rompe la decodifica di tutti i file salvati in precedenza
var blocks: [Block] = []  // Codable sintetizzato usa decode(forKey:) → keyNotFound

// ✅ CORRETTO — init(from:) custom con decodeIfPresent
init(from decoder: Decoder) throws {
    let c = try decoder.container(keyedBy: CodingKeys.self)
    // campi esistenti...
    blocks = try c.decodeIfPresent([Block].self, forKey: .blocks) ?? []
}
```

Quando aggiungi un campo a un tipo `Codable` persistito su disco:
1. Aggiungi l'`init(from:)` custom se non c'è già.
2. Usa `decodeIfPresent` per il nuovo campo.
3. Prima del merge, verifica caricando un `books.json` reale senza la nuova chiave.

---

## 2. BookStore.load() fail-safe — mai sovrascrivere su errore

`BookStore.load()` deve preservare il file in caso di decodifica fallita.
Non ingoiare silenziosamente l'errore e lasciare `books = []`: a quel punto
qualsiasi `save()` successivo (incluso quello di `resetAllProcessingForDevRebuild`)
sovrascrive il file con un array vuoto — **perdita dati permanente**.

Pattern obbligato:

```swift
func load() {
    guard let data = try? Data(contentsOf: savePath) else { return }
    do {
        books = try JSONDecoder().decode([Book].self, from: data)
    } catch {
        // PRESERVA il file originale — non sovrascrivere mai
        let backup = savePath.deletingLastPathComponent()
            .appendingPathComponent("books.corrupt.\(Int(Date().timeIntervalSince1970)).json")
        try? FileManager.default.copyItem(at: savePath, to: backup)
        // NON fare save(), NON azzerare books
        print("BookStore.load() fallito — file preservato come \(backup.lastPathComponent)")
    }
}
```

---

## 3. resetAllProcessingForDevRebuild — non girare su dati reali

`resetAllProcessingForDevRebuild()` è una funzione di sviluppo. Non deve:
- Girare se `load()` ha fallito (i libri potrebbero essere vuoti per errore, non per scelta).
- Fare `save()` automatico su dati reali di un utente.

Proteggi con un flag (`loadSucceeded`) impostato solo dopo una decodifica
avvenuta con successo, prima di chiamare qualsiasi reset automatico.

---

## 4. Schema additive-only

`Book.swift` e i tipi correlati sono il contratto con i dati già salvati
nel device dell'utente. Si possono:
- Aggiungere campi opzionali con `decodeIfPresent`.
- Aggiungere case a enum `Codable` (aggiungere sempre, non rinominare).

NON si può, mai:
- Rimuovere campi esistenti dal modello (anche se "non più usati").
- Rinominare campi o case (= rimozione + aggiunta → rompe i file esistenti).
- Cambiare il tipo di un campo (`String` → `Int`, ecc.).

---

## 5. Export — UUID stabili tra re-export

I campi `book.id` e `recipe.id` sono la chiave di deduplicazione usata da
Domus al momento dell'import (`digitization.sourceId`). Non rigenerare mai
questi UUID tra export: una stessa ricetta riesportata deve avere lo stesso
UUID. Non mescolare UUID v4 con altri formati ID per gli stessi oggetti.

---

## 6. Niente operazioni di reset automatico su build senza flag esplicito

Ogni funzione che azzera o modifica in massa i dati (reset pipeline,
ri-elaborazione batch, migrazione dati) deve:
1. Essere protetta da un flag esplicito (`UserDefaults` o argomento da chiamante).
2. Stampare un log chiari di cosa sta per toccare.
3. Non girare in automatico al lancio su build di produzione.
