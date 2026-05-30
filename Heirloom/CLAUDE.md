@AGENTS.md

# Memoria — workflow Claude Code

## Cos'è questo progetto

**Memoria** (codename Xcode: *Heirloom*) è l'app iOS di Recipees — acquisisce
ricette di famiglia da foto, audio, video, testo, PDF. iOS 17+, Swift 6 strict
concurrency, SwiftUI. In beta amici dal 2026.

Fa parte dell'ecosistema Recipees insieme a **Domus** (web app, `recipees.app`)
e **Folio** (libro stampato, futuro). Il coordinamento cross-prodotto è in
`../RECIPEES_HUB.md`.

La sessione Cowork attiva si chiama **cool-modest-bardeen** (per riferimento
nei brief cross-sessione).

---

## Stack

| Layer | Tecnologia |
|---|---|
| Language | Swift 6 (strict concurrency abilitata) |
| UI | SwiftUI, iOS 17+ |
| Persistenza | JSON su disco (`books.json` in `Documents/`) via `BookStore` |
| Media | `Documents/photos/`, `Documents/audio/`, `Documents/video/` |
| OCR | Vision framework (`OCRService`) |
| AI | Claude Haiku via `ClaudeService` (chiave API da `Config.plist`, letta in `ClaudeService.swift:52`) |
| Build | Xcode 16, target iPhone + iPad (iPhone portrait-locked in beta) |
| Export | `ExportService`: Pack v3 ZIP (formato Domus), JSON v1, HTML, Paprika 3, testo |

---

## Workflow git

Il repo è **monorepo**: `simonblaster/Ricette` su GitHub. Heirloom è in
`Heirloom/` dentro quel repo, insieme a `recipees-domus/` e ai file di
coordinamento.

```bash
# Prima di ogni commit — entrambi devono essere puliti
# (Swift: build + warning critici in Xcode, non da CLI)
# Per i file di coordinamento (.md): basta leggibilità e coerenza

# Commit
git add <files>
git commit -m "tipo(area): descrizione

[note build se rilevante]"
git push origin main
```

- **Un commit per bug/feature** con messaggio chiaro
- Per le modifiche Swift: confermare il build in Xcode PRIMA del commit
- Il push non triggera deploy automatico per iOS (Xcode Cloud non attivo) —
  il build Xcode resta manuale

---

## Architettura — pattern critici

### BookStore e persistenza JSON

`BookStore` è la fonte di verità. Persiste in `books.json` (Documents/).
Nessun CoreData, nessuna dipendenza esterna.

**Regola assoluta:** ogni cambio di schema su `Book`, `Page`, `Recipe`,
`Ingredient` deve usare `decodeIfPresent` nel `init(from:)` custom —
**mai** confidare nel default value del Codable sintetizzato (non funziona
per chiavi assenti). Vedi `AGENTS.md` per il pattern completo.

### Strict concurrency (Swift 6)

Tutte le operazioni su `BookStore` (class `ObservableObject`) che mutano
`@Published var books` devono girare sul MainActor. I servizi (`OCRService`,
`ClaudeService`) usano `async/await`. Pattern tipo:

```swift
// ✅ Accesso da View o da MainActor-isolated context
await MainActor.run { store.updateBook(updated) }

// ✅ In BookStore (se annotato @MainActor)
@MainActor
func updateBook(_ updated: Book) { ... }
```

Se vedi warning `actor-isolated property … can not be mutated from a
non-isolated context`, il fix è aggiungere `@MainActor` alla proprietà o
alla funzione che la modifica.

### Export Pack v3 — contratto con Domus

Il formato `exportBookZIP` produce un archivio con questa struttura:

```
book.json               (schemaVersion: 3, metadati ricettario, NO array recipes inline)
cover.jpg               (opzionale)
recipes/<uuid>/
    recipe.json         (oggetto ricetta nudo, NO envelope)
    photo.*             (convenzione nome file per le foto)
    audio.*
    video.*
```

Questo contratto è **stabile e additivo-only**. Non cambiare la struttura
senza accordo con la sessione Domus. I campi deprecati vanno lasciati per
backward compat; i campi nuovi vanno aggiunti come opzionali.

Il parser Domus usa `digitization.sourceId` = `recipe.id` per la dedup:
lo stesso UUID tra re-export garantisce che riesportare non duplichi ricette.

### UUID stabili

`book.id` e `recipe.id` (UUID) non devono mai essere rigenerati tra un
export e il successivo. Sono la chiave di deduplicazione in Domus.

---

## File di coordinamento (aggiornare a fine sessione)

| File | Cosa aggiornare |
|---|---|
| `../RECIPEES_HUB.md` | Sezione "Memoria" con stato build, funzionalità completate, bug fix applicati, richieste cross-prodotto |
| `../ROADMAP_bug.md` | Bug risolti → stato "Risolto" con commit hash |
| `../ROADMAP_funzionalita.md` | Feature completate → stato aggiornato |

**Rituale fisso:** leggere `../RECIPEES_HUB.md` a inizio sessione,
aggiornare la sezione Memoria a fine sessione.

---

## Stato beta (riferimento 2026-05-30)

Funzionante e testato: acquisizione fotocamera (3 modalità), OCR Vision, AI
strutturazione, editor, audio originale, video originale, arricchimento ricetta
esistente con voce/video, stato "conclusa", autopilot guide contestuali,
pianifica, rebrand "Memoria".

**Multipagina — Steps 1-5 implementati (2026-05-23/30):**
- `Block.swift` — modello dati (Block, Sheet, RecipeFragment, BlockRecipe)
- `BlockListView.swift` — lista sessioni per un Book
- `BlockSessionView.swift` — tab Acquisisci / Delimita
- `BlockTapeView.swift` — nastro fogli + draw frammenti + selezione ricette
- `BlockRecipeProcessor.swift` — pipeline OCR Vision + Claude AI per BlockRecipe
- `BlockRecipeReviewView.swift` — review + edit + promozione → Page
- Step 6 (riapertura incrementale) e Step X (fotocamera nativa) post-lancio

⚠️ **ATTENZIONE — `Book.blocks` usa Codable sintetizzato (ROTTO):**
`var blocks: [Block] = []` in `Book.swift` usa il Codable sintetizzato, che
NON usa il default value per chiavi mancanti → `books.json` pre-multipagina
fallisce la decodifica → perdita dati. Questo è il **PRIMO bug da correggere**
prima di qualunque altra cosa (vedi `AGENTS.md` §1 per il fix esatto con
`init(from:)` custom + `decodeIfPresent`).

**Bug priorità assoluta:** perdita dati su nuova build (Codable + resetAllProcessingForDevRebuild)
— vedi `../ROADMAP_bug.md` sezione Memoria. I tre livelli di fix sono in
`AGENTS.md` §1-3.

**Prossimi step verso lancio 5 giu:** fix Codable data-loss (PRIMA DI TUTTO) →
TestFlight → test export Pack v3 reale → pulizia warning Swift 6 → App Store
Connect setup.
