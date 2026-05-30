# RECIPEES — HUB DI COORDINAMENTO

> Fonte unica condivisa tra le sessioni Claude del progetto Recipees:
> **Recipees** (supervisione), **Memoria** (app iOS), **Domus** (web).
> In futuro anche **Folio** (stampa).
>
> **Ultimo aggiornamento:** 2026-05-30 (sessione Memoria) — build Xcode VERDE (0 errori, commit `e613e47`). Fix data-loss confermato: `Book.init(from:)` in extension preserva il memberwise init + `decodeIfPresent([Block])` testato su JSON pre-2026-05-23 → OK. Tutti e 6 i bug *In fix* Memoria → **Risolto** in ROADMAP_bug.md. Prossimi passi: App Store Connect + TestFlight interno + export Pack v3 reale su iPhone fisico.
>
> **2026-05-30 (sessione Recipees)** — riorganizzazione hub + sessioni. (1) CASELLA BRIEF snellita ai soli brief vivi; tutto il gestito/chiuso (≤24 mag) spostato in **`HUB_archivio.md`** (hub da 1435 → ~590 righe). (2) Nuova convenzione **worktree per le due sessioni Domus** (`feat/*` e `fix/*`, merge in `main` fatto da Recipees) — sostituisce «un committente per volta»; in CONVENZIONI, `recipees-domus/CLAUDE.md`, `CLAUDE.md` root. (3) Regola «una sessione = un prodotto = una verità».
>
> **2026-05-30 (sessione Recipees, 2° giro)** — check sessioni esistenti: 6 sessioni su `/Ricette`, **tutte lanciate da root** → non caricavano i CLAUDE.md di prodotto. **Fix:** guardia "chi sei?" in cima a `CLAUDE.md` root (ogni sessione prodotto legge subito il proprio `CLAUDE.md`+`AGENTS.md`). Legacy Memoria/Domus: il fondatore le tiene per ora (non archiviate). Dettaglio: brief in cima alla CASELLA BRIEF.

---

## COME SI USA QUESTO FILE

Regola per ogni sessione, senza eccezioni:

1. **A inizio sessione:** leggi questo file per intero prima di lavorare.
2. **A fine sessione** (o dopo una decisione/consegna importante): aggiorna
   **la tua sezione** in "STATO PER PRODOTTO" e, se serve, scrivi nella
   "CASELLA BRIEF".
3. **Non riscrivere le sezioni delle altre sessioni.** Se ti serve qualcosa
   da un'altra sessione, scrivilo nella CASELLA BRIEF.
4. Aggiorna sempre la riga "Ultimo aggiornamento" in cima, con data + nome
   sessione.
5. Le memorie interne di ogni sessione restano dove sono. Qui va **solo ciò
   che serve alle altre sessioni**: stato, contratti, decisioni, richieste.

La sessione **Recipees** è proprietaria del file: tiene la coerenza,
archivia le decisioni cross-product, segnala i disallineamenti. Memoria e
Domus mantengono la propria sezione e la casella brief.

---

## I TRE PRODOTTI

Recipees è l'ecosistema. Tre problemi reali, tre prodotti, tre gesti:

| Prodotto | Gesto | Cos'è | Sessione |
|----------|-------|-------|----------|
| **Memoria** | riscopri | App iOS, acquisizione ricette (quaderno, voce, video, pagina trovata). Codename Xcode: *Heirloom*. | Memoria |
| **Domus** | condividi | Web, il ricettario di famiglia online — `recipees.app`. Next.js + Firebase. | Domus |
| **Folio** | tramanda | Il libro di carta stampato. Apre a settembre 2026. | — (non attiva) |

**Identità dell'app iOS** (3 livelli): display utente "Memoria" · App Store
"Recipees Memoria" · marketing "Memoria, by Recipees" · codename interno
Xcode "Heirloom" (non cambia mai).

**Voce del brand:** memoir, sostantivi concreti, niente urgenza, niente
tech-speak. Claim: *Riscoperte. Condivise. Tramandate.*

---

## TIMELINE CONDIVISA

| Data | Milestone |
|------|-----------|
| 14 mag 2026 | Domus online in beta amici (utenti reali) |
| ~21-23 mag | Memoria consegna il fixture Pack v3 a Domus (prima possibile) |
| 2 giu 2026 | Checkpoint Pack v3 end-to-end · TestFlight Memoria |
| **5 giu 2026** | **Lancio beta amici unificato (Memoria + Domus)** |
| set 2026 | Folio apre (prevendita) |

Riferimento data odierna alla creazione del file: 2026-05-21 →
**15 giorni al lancio unificato**.

---

## STATO PER PRODOTTO

### Memoria — *(mantenuta dalla sessione Memoria)*

Aggiornato 2026-05-30 dalla sessione Memoria. App iOS, deployment iOS 17,
Swift 6 strict concurrency, Xcode 16 sync group. Test in corso su iPhone
fisico (iOS 26 beta).

**Sessione Claude Code attiva (2026-05-30):** `Heirloom/CLAUDE.md` e
`Heirloom/AGENTS.md` creati (commit `c329c83`) — ogni sessione si avvia con
`claude` in `Heirloom/` e riceve automaticamente stack, workflow git, pattern
critici Codable e puntatori ai file di coordinamento.

**Funzionante e testato:**

- Creazione/eliminazione ricettari. Acquisizione pagine: fotocamera
  (3 modalità — manuale, timer, automatico al giro pagina), import
  PDF/foto/file, import testo.
- OCR (Vision) + strutturazione AI (Claude Haiku). Editor multi-ricetta.
- **Voce originale (audio):** registrazione → trascrizione (SFSpeech) →
  strutturazione AI → player immersivo con waveform. Bug root risolto
  (un `discardCurrent` cancellava il file prima della lettura).
- **Video originale:** registrazione, player Apple-Photos style (controlli
  auto-hide), card con thumbnail estratto. Implementato con `AVAssetWriter`
  custom perché su iOS 26 beta `AVCaptureMovieFileOutput` scrive `.mp4`
  senza traccia audio.
- **Aggiungi voce/video a ricetta esistente:** l'AI confronta la
  registrazione con la ricetta e propone arricchimenti tipati (ingrediente
  extra, passaggio, nota, trucco, introduzione); l'utente accetta/modifica
  in una review-sheet.
- **Stato "conclusa"** (`PageStatus.concluded`): a fine pipeline l'utente
  fa "Salva e concludi". Tap su ricetta conclusa → vista lettura; bottone
  "Indietro" → modalità modifica.
- **Autopilot (guida contestuale):** ~30 schermate con guida pop-up +
  bottone `?`, intro 3-schermate al primo lancio, editor testi guide in
  Impostazioni.
- **Pianifica:** tool di intake delle intenzioni utente (scrivi o detta
  cosa vorresti digitalizzare), entry-point in cima alla libreria.
- Rebrand "Memoria": UI strings e landing app già aggiornate.

**Export verso Domus — Pack v3 ALLINEATO 2026-05-21.** DTO
(`DomusExportDTO.swift`) ed `ExportService.swift` adeguati al contratto
rivisto: `schemaVersion` obbligatorio (1 per JSON v1, 3 per Pack v3),
durate a campo doppio (stringa leggibile + `*ISO` 8601 opzionale, parser
conservativo). `exportBookZIP` produce il Pack v3 (`book.json` a root +
`cover.jpg` + `recipes/<id>/` per ricetta con `recipe.json` + media);
`exportBookJSON` v1 resta intatto come rete di sicurezza. Solo ricette
`.concluded`, UUID `book.id`/`recipe.id` stabili tra re-export.
**Fixture Pack v3 v2 consegnato 2026-05-22** in
`Ricette/test_exports/memoria_packv3_fixture_2026-05-21_v2.zip` — corretto
il difetto envelope: `recipe.json` ora oggetti ricetta nudi, `book.json`
senza array `recipes` inline. Il difetto era nello script generatore del
fixture (`build_fixture.py`), non nel codice di export — `exportBookZIP`
e `DomusExportDTO` erano già conformi al contratto. Test end-to-end
Domus eseguito il 2026-05-23: verde, 141/141 assert PASS. Vedi brief.

**Da fare verso il 5 giugno:**

1. Test su iPhone dell'export Pack v3 reale (l'app deve produrre uno
   ZIP identico al fixture) + verifica end-to-end col parser Domus.
2. Rebrand — display name + 3 usage string FATTE; launch screen
   brandizzato FATTO. Modifiche pbxproj/storyboard da confermare con
   build Xcode.
3. Pulizia ~60 warning Swift 6 (actor-isolation, non bloccanti).
4. App Store Connect setup + TestFlight + build production + upload.
5. Bug fix da test sul campo (3 fix applicati 2026-05-23, da confermare).
6. **Multipagina Step 4-5 COMPLETI** (23 mag sera), Step 6 post-lancio:
   - Step 4 ✓: `BlockRecipeProcessor` — stitching frammenti, OCR Vision, Claude AI
   - Step 5 ✓: `BlockRecipeReviewView` — review + edit rapido + promozione → Page
   - Step 6: riapertura incrementale (aggiunta fogli a sessione esistente)
   - Step X: `BlockAcquisitionView` fotocamera nativa (ora stub placeholder)

**Bug camera orientamento (`ROADMAP_bug.md` sez. Memoria) — fix applicati
2026-05-23.** I due bug erano facce dello stesso problema. Bug 2 (Alta): la
preview collassava a riga sottile ruotando il telefono — root cause = l'app
non era portrait-locked (il commento in `CameraService` lo dava per
scontato, ma il pbxproj abilitava landscape su iPhone), quindi iOS ruotava
tutta la UI e il `VStack` schiacciava la preview. Fix: orientamenti iPhone
limitati a solo Portrait. Bug 1 (Media): default guida split verificato già
corretto (`.vertical` = spread orizzontale); testi guida camera
(`HelpEntry .cameraAcquisition` + tip in `AcquisitionView`) ora dicono di
tenere il telefono in orizzontale. Entrambi in stato *In fix* — confermare
con build Xcode.

**Bug pipeline acquisizione (`ROADMAP_bug.md`) — fix applicati 2026-05-23.**
Tre bug segnalati testando sul campo. (1) Dopo "Scambia ricetta ↔ foto" su
una pagina già processata, OCR/AI continuavano a girare sulla foto del
piatto: `shouldBake` valutato dopo `saveClassify`, che ne azzerava il
segnale → re-bake saltato. (2) Il thumbnail di una ricetta conclusa senza
`recipe` apriva "Audio non strutturato — 0 clip": vicolo cieco nel routing
`mediaPageDestination`. (3) L'import da libreria foto saltava la pipeline
manuale (`FileImportFlow` faceva OCR+AI al volo e scartava la foto): ora le
foto entrano nella stessa pipeline della fotocamera. Tutti *In fix*,
confermare con build Xcode.

**Bug iOS 26 beta noti** (workaround applicati, non bloccanti): schermata
bianca al primo lancio dopo rebuild (kill+relaunch); export media via
`AVAssetWriter` invece di `AVCaptureMovieFileOutput`.

### Domus — *(mantenuta dalla sessione Domus)*

Aggiornato 2026-05-30 dalla sessione Domus. Online su `recipees.app`
in beta amici dal 14 mag, utenti reali con ricette caricate. Firebase project
`recipees-domus` (region Frankfurt eur3), deploy automatico Vercel su push
a `main`. HEAD corrente: `c329c83`.

**Migrazione a Claude Code — COMPLETATA 2026-05-30.** `CLAUDE.md` +
`AGENTS.md` aggiunti per tutte le sessioni attive (commit `c329c83`):
`recipees-domus/CLAUDE.md` (già esistente da `9316d35`), `Heirloom/CLAUDE.md`,
`Heirloom/AGENTS.md`, `CLAUDE.md` root. Ogni sessione ora si avvia con
`claude` nella propria directory e riceve automaticamente stack, workflow
git, pattern critici e puntatori ai file di coordinamento.

**Funzionante (in produzione):**

- Auth completo: signup (nome, conferma password, indicatore forza,
  show/hide, accettazione termini), verifica email soft con banner persistente.
- CRUD ricette e ricettari; ricerca; empty state onboarding.
- Import modulare a N tab: Crouton, MealMaster, MasterCook, Plan to Eat,
  Smart AI universale (fallback AI per qualunque file), import cookbook da
  Memoria (formato v1 JSON). Info-box guida per Samsung Food, Pepperplate,
  BigOven, ReciMe, MacGourmet. De-dup al re-import via `digitization.sourceId`.
- Import da web/scraping (es. GialloZafferano): description, notes, foto.
- **Sharing Fase 1**: inviti via email (Resend), grant, fork "Fai tuo il
  ricettario", notifiche in-app, link ai cookbook condivisi, filtro `?owner=`.
- Modalità non-distruttiva: soft delete ricette+ricettari, backup giornaliero
  Firestore (retention 14d), policy in `recipees-domus/AGENTS.md`.
- Sistema feedback/ticketing beta tester (`/feedback`).
- Landing narrativa + pagine prodotto `/memoria` e `/folio` cross-linkate.

**Parser Pack v3 — COSTRUITO 2026-05-21** (commit `6d4ea97`, in produzione
su Vercel). L'importer "Memoria (iOS)" della dropzone `/import` ora legge il
Pack v3: rileva `book.json` con `schemaVersion 3`, ricette in
`recipes/<id>/recipe.json`, estrae foto/audio/video per nome file dichiarato
o per convenzione (`photo.*`/`audio.*`/`video.*`), crea `Cookbook` + `Recipe`
collegati, carica i media su Firebase Storage, dedup per UUID
(`digitization.sourceId`). Durate a campo doppio: usa l'ISO se presente,
altrimenti normalizza la stringa leggibile e la tiene verbatim se non
numerica. Preview pre-import con deselezione granulare per ricetta.
Implementato estendendo l'importer Memoria esistente (un solo percorso
testato, niente file paralleli); il v1 JSON resta intatto come rete di
sicurezza. `tsc --noEmit` + `eslint` puliti.

**Verifica fixture — 2026-05-21 (sessione Recipees).** Recipees ha
verificato il primo fixture Pack v3 di Memoria contro questo parser: il
parser è **corretto**, non è stato toccato. Il fixture aveva due problemi —
un envelope sbagliato in `recipe.json` (lo corregge Memoria) e il campo
`mediaAuthor` non previsto dallo schema. **Domus ha aggiunto `mediaAuthor`**
(commit `39060e7`, in produzione): `heirloomRecipeSchema` + tipo `Recipe` +
mappatura in `convertToDomusRecipe` — l'attribuzione di voce/video
(es. "Zia Francesca") ora si persiste all'import.

**Test end-to-end Pack v3 — ESEGUITO 2026-05-23 (sessione Domus). VERDE.**
Il parser reale (`heirloom-import.ts`, compilato dal repo) è stato girato
contro il fixture v2 `memoria_packv3_fixture_2026-05-21_v2.zip`: formato
`zip-v3` rilevato, `schemaVersion 3`, 6 ricette + ricettario, 11 media
estratti come blob non vuoti (6 foto, 2 audio `audio/mp4`, 2 video
`video/mp4`, 1 cover), durate a campo doppio (ISO dove presente, stringa
verbatim per "fino a doratura" / "una notte in frigo"), `mediaAuthor`
persistito, `convertToDomusRecipe` → `visibility: "private"` su tutte,
directions atomiche 1:1, dedup `digitization.sourceId` stabile fra import.
**141/141 assert PASS, 0 FAIL, 0 warning.** Dettaglio nella CASELLA BRIEF.

**Player audio/video "Voce originale" — IN PRODUZIONE 2026-05-23.** Il
dettaglio ricetta ora mostra `recipe.media`: componente `RecipeMediaSection`
con player HTML5 `<audio>` / `<video>` che leggono `media.audioUrl` /
`media.videoUrl` (URL già salvati all'import Pack v3, niente nuovo backend
né modello dati), più l'attribuzione **"Voce di {mediaAuthor}"**. Chiude il
buco dell'audit Recipees del 23 mag — i media importati venivano caricati su
Storage ma non mostrati. Implementato dalla sessione Recipees, verificato
(`tsc` + `eslint` puliti) e spedito da Domus — commit `a478610` su `main`,
Vercel deployato.

**Bug backlog — CHIUSO 2026-05-24.** Sessione bug-fix dedicata ha risolto
tutti i 9 bug aperti — 10 commit da `727565e` a `184f9f8`. Elenco commit:
filtro ricerca mobile (`44d9c13`), cluster Sharing Fase 1 — ricettari
condivisi, selettore Crea Menu, permessi lettura-only (`336f3f4`,
`ae4ae33`, `092927a`), warning `ServingsScaler` (`3296b99`), build
`/cookbooks/new` dinamica (`d72f248`), ESLint repo a **0 errori 0 warning**
(`73a482e` + `fadd1db`), layout riga ingredienti in modifica — qty/unit a
larghezza fissa, nome con `flex-1 min-w-0` (`1d016ba`), icone azioni
ricetta migrate a SVG + box `w-12 h-12` (`9318eec`), callback `onSave` al
salvataggio modifica invece di `router.push` a stesso URL (`184f9f8`). In
produzione su Vercel; fix di layout e UI confermati a vista dal fondatore.

**Lista spesa — mobile confirm() + aggregata + per-ricetta da menù + normalizzazione Parte B — CHIUSI 2026-05-24.**
Quattro commit nella sessione di continuazione: (1) `b9391aa` — fix iOS PWA:
`window.confirm()` silenziosamente bloccato in WKWebView; sostituito con
`pendingAction` state inline (nessun dialog nativo). (2) `ce0eb32` — feat
lista spesa aggregata di default: `aggregateItems()` raggruppamento per
nome normalizzato, somma quantità per unità, toggle pill "Aggregata / Per
ricetta" persistente in `localStorage`; aggregazione solo di vista, dati
Firestore intatti. (3) `5484d0f` — fix bug conseguente: `addMenuToShoppingList`
scriveva item pre-aggregati senza `fromRecipeId` → vista per-ricetta non
separava le ricette. Fix: scrittura per-ricetta con scaling (`scaleQty()`),
aggregazione spostata interamente nel layer di vista. (4) `6ff6924` — feat
normalizzazione Parte B: tabella `CANONICAL_FORMS` (plurali irregolari e
comuni, uova→uovo, carote→carota, funghi→fungo, 20+ voci), `PREP_DESCRIPTORS`
strip in coda ("cipolla tritata" = "cipolla", esclusi termini-prodotto),
`USAGE_QUALIFIERS` + `QTY_NON_SUMMABLE` per qualificatori d'uso (q.b.,
per servire/guarnire — merge silenzioso se ingrediente già presente, voce
senza qty se solo). Tutti confermati a vista dal fondatore
(ce0eb32 + 5484d0f); 6ff6924 in verifica.

**Fix login — RISOLTO DEFINITIVAMENTE 2026-05-26, commit `2ebb2b5`.**
Root cause reale: `useSearchParams()` in client component dentro `<Suspense>`
causava sospensione server-side → skeleton "Domus" al client → React non
reidratava → tutti gli handler morti. Fix definitivo: `page.tsx` legge
`searchParams` come `Promise` (Next.js 16 API), li passa come plain props a
`LoginForm`. Nessun `useSearchParams()` nel client, nessuna `<Suspense>`,
idratazione deterministica. Iter completo in ROADMAP_bug.md (7 commit,
`2d004d8` → `2ebb2b5`). tsc + eslint 0/0.

**Controllo pratiche migrazione Firestore — ESEGUITO 2026-05-24. SICURO.**
Tutte le scritture usano `updateDoc` (nessun `setDoc` che azzera il
documento); schema additive-only per policy (`AGENTS.md`);
`ignoreUndefinedProperties: true` previene la cancellazione involontaria
di campi non toccati; nessun auto-reset al boot; soft delete via `deletedAt`
(nessun `deleteDoc` su collezioni utente). Il rischio dell'incidente Memoria
non esiste lato Domus: nessun `Codable` sintetizzato, nessun `save()`
automatico su caricamento fallito.

**Feature post-lancio in produzione — 2026-05-24 (sessione Domus-funzionalità):**

- **Lista spesa — Completati collassabili** (commit `03dd361`): item spuntati
  escono dalla lista principale e scendono in una sezione «Completati (N)»
  collassabile in fondo (default chiusa). Funziona in aggregata e per-ricetta.
  Stato persistito in localStorage. «Rimuovi completati» / «Svuota tutto» invariati.
- **Ricerca — pulizia UX** (commit `c4249c8`): sezione Suggerimenti rimossa; tag
  collassabili con bottone ▼/▲ (default chiusi), tag attivi visibili da chiuso,
  stato persistito. Layout responsivo — desktop e mobile identici.
- **Ricerca — Filtra per ricettario + fix tag/ricettari su home mobile** (commit `dc64864` + `d55ceb8`):
  sezione «Filtra per ricettario» collassabile in /search (default aperta),
  logica OR su cookbookId, persistenza localStorage. Fix: rimossi tag/categorie
  E chip ricettari dalla home mobile (/recipes) — erano duplicati della sidebar
  desktop e confondevano; tutti i filtri per tag e ricettario stanno
  esclusivamente in /search (sia mobile sia desktop).
  HEAD: `d55ceb8`. tsc + eslint 0/0. Confermati a vista dal fondatore.

**Da fare verso il 5 giugno:**

1. Verifica live Sharing Fase 1 (serve un grant attivo per testare
   end-to-end fork + notifica autore).
2. Verifica a vista feature lista spesa + ricerca (fondatore su recipees.app).

**Contratto Pack v3 — lato Domus CONFERMATO e IMPLEMENTATO:** schema
additive-only, durate a campo doppio (stringa leggibile primaria + `*ISO`
opzionale), struttura per-ricetta `recipes/<id>/`, dedup per UUID. Il parser
è robusto a piccole varianti del fixture: media per nome file o per
convenzione, `recipe.json` per cartella (Pack v3) o array `recipes` inline
(v2 legacy).

**Crea Menu — IN PRODUZIONE** (merge `feat/crea-menu` → `main` il 2026-05-23,
commit `6ee9bce`). Feature post-lancio anticipata su richiesta del fondatore,
costruita su un branch dedicato e poi mergiata su decisione del fondatore. **v1** (8 step della spec
`Ricette/SPEC_crea_menu.md`): entità `Menu` + CRUD, nav + lista `/menus`,
editor, dettaglio, popup "Aggiungi a un menù" da ricetta, "Aggiungi alla
spesa" con unione ingredienti + scaling, stampa menù + segnaposto.
**Rifiniture** chieste dal fondatore testando in locale: partecipanti
distinti in padroni di casa/ospiti; titolo automatico «{occasione} con
{ospiti}» (cognome unico → «i Migone»); rubrica dei commensali
(`users/{uid}/people`) auto-popolata — i padroni di casa si ripropongono,
gli ospiti si ripescano in autocomplete; filtro per portata nel selettore
ricette; stampa ripulita (header app escluso, data fuori dal titolo,
marchio discreto). 13 commit, `tsc` + `eslint` puliti. Rules Firestore
`menus` + `users/{uid}/people` deployate. Le preview Vercel del branch
falliscono il build per un gap pre-esistente (env var Firebase non
impostate per l'environment Preview): durante lo sviluppo il test si è fatto
in locale con `npm run dev`. **Merge in `main` eseguito il 2026-05-23** dalla
sessione Recipees (decisione del fondatore), Vercel deploy Production verde.
Dettaglio nella CASELLA BRIEF.

### Folio

Solo copy della landing pubblicata (`recipees.app/folio`). Tre formati:
Tascabile, Classico, Deluxe. Nessun lavoro di prodotto prima di settembre.

---

## CONTRATTO EXPORT MEMORIA → DOMUS

**Stato:** DECISO da Recipees il 2026-05-21, RIVISTO lo stesso giorno su
indicazione del fondatore — vedi log DECISIONI CROSS-PRODUCT.

Obiettivo di lancio: **Pack v3 al 5 giugno** (foto + audio + video dentro
Domus). Il formato **v1 JSON** resta costruito e testato come **rete di
sicurezza**.

### Obiettivo di lancio (5 giugno) — Pack v3 ZIP

Struttura `.zip` esatta:

- **`book.json`** (a root) = solo metadati ricettario — oggetto `book`
  (`id`, `name`, `author`, `year`, `description`, `cover_filename`) +
  `schemaVersion: 3`. In Pack v3 **non** contiene l'array `recipes` inline.
- **`cover.jpg`** (a root, opzionale) — copertina del ricettario.
- **`recipes/<recipeId>/`** una cartella per ricetta, con:
  - **`recipe.json`** = l'oggetto **ricetta nudo** (`id`, `title`,
    `ingredients`, `directions`, durate, `*_filename`, `mediaAuthor`… a
    livello root). NON un envelope: niente wrapper `recipes`, niente
    `schemaVersion` dentro recipe.json.
  - i media co-locati: `photo.*`, `audio.*`, `video.*` (opzionali).
- `schemaVersion: 3` vive solo in `book.json` e instrada la dropzone
  `/import` di Domus al parser Pack v3.
- Porta **foto, audio e video** dentro Domus fin dal lancio.
- Parser di riferimento lato Domus: `recipees-domus/src/lib/heirloom-import.ts`
  (`parseZipBookWrapper`); `recipe.json` è validato con `heirloomRecipeSchema`
  in `src/lib/schema.ts` — la forma deve combaciare con quello schema.

### Rete di sicurezza — formato v1 JSON

- Un singolo file `.json`: wrapper `book` + array ricette, **foto inline
  base64**, niente audio/video. `schemaVersion: 1`.
- È l'`exportBookJSON` già pronto lato Memoria + il parser v1 già in
  produzione lato Domus: funziona oggi, costo di mantenimento ~zero.
- Resta costruito e verificato come fallback. Non viene buttato.

### Checkpoint 2 giugno (de-risk del lancio)

Il 2 giugno si guarda lo stato reale del Pack v3 end-to-end:
- **Verde** (export Memoria → import Domus → ricetta con media visibile):
  si lancia il 5 giugno con Pack v3.
- **Non verde:** si lancia il 5 giugno sul formato v1 JSON e Pack v3 diventa
  fast-follow a giorni. Il lancio non slitta e non fallisce, perché la rete
  di sicurezza è pronta.

La data del 5 giugno **non si sposta prima**: aggiungere Pack v3 (parser
Domus da scrivere da zero) e anticipare la data sono richieste opposte — si
tiene la scope ambiziosa e si tiene la data. Se a fine maggio si è avanti,
anticipare di un paio di giorni è un bonus, non il piano.

### Regole valide per entrambi i formati

- **`schemaVersion` obbligatorio** nel root / `book.json`. Senza, Domus non
  può riconoscere e instradare il file. Non negoziabile.
- **Durate — campo doppio.** `prepTime` / `cookTime` / `totalTime` = stringa
  leggibile, sempre presente, campo primario (regge "fino a doratura",
  "tutta la notte", "q.b."). `prepTimeISO` / `cookTimeISO` / `totalTimeISO`
  = ISO 8601 (`PT30M`), **opzionale**, valorizzato solo quando la durata è
  pulita e numerica. Domus usa l'ISO quando c'è, altrimenti normalizza la
  stringa. (Supera la vecchia regola "solo ISO 8601".)
- **UUID stabili:** `book.id` e `recipe.id` UUID persistiti, invariati tra
  export successivi — servono al dedup `digitization.sourceId` lato Domus.
- **Directions atomiche:** un passaggio = una frase; Domus le preserva, non
  le concatena.
- Schema **additive-only:** si aggiungono campi opzionali, non si rimuove né
  rinomina.
- Beta 5 giu: conferma export = tap manuale "Marca esportato in Domus" lato
  iOS, nessuna ricevuta automatica.

Spec storica: `Heirloom/_planning/MEMORY_for_recipees_space.md` +
`Ricette/HEIRLOOM_PROMPT_export_cookbooks.md`.

---

## DECISIONI CROSS-PRODUCT (log)

Solo decisioni che toccano più di un prodotto. Append-only, con data.

- **2026-05-13** — Identità app iOS a 3 livelli (Memoria / Recipees Memoria
  / Memoria, by Recipees). Codename Xcode resta Heirloom.
- **2026-05-14** — Adottato Pack v3 come formato di scambio Memoria↔Domus,
  ritirato il "v2 ZIP singola ricetta". Domus ha spostato il lancio dal
  21 mag al 5 giu per allinearsi a Memoria.
- **2026-05-21** — Creato questo hub come fonte unica di coordinamento tra
  le sessioni.
- **2026-05-21 (Recipees)** — DECISIONE formato export Memoria→Domus. Il
  beta del 5 giugno parte sul formato **v1 JSON** (testo + foto inline
  base64, già funzionante su entrambi i lati). Il **Pack v3 ZIP** (con
  audio/video, struttura per-ricetta) diventa fast-follow post-lancio.
  `schemaVersion` obbligatorio in entrambi; durate a campo doppio (stringa
  primaria + ISO 8601 opzionale). "v2.1" archiviata: non è mai stata un
  contratto ufficiale. Dettaglio nella sezione CONTRATTO EXPORT.
- **2026-05-21 (Recipees, revisione)** — Su indicazione del fondatore la
  decisione è alzata: **Pack v3 dentro il lancio del 5 giugno** (foto +
  audio + video in Domus fin da subito), non più fast-follow. Il v1 JSON
  resta come rete di sicurezza con checkpoint il 2 giugno. La data del
  5 giugno tiene, non si anticipa: scope ambiziosa + data anticipata sono
  incompatibili. Fondatore disposto a più ore di lavoro per sostenerlo.
- **2026-05-21 (Recipees, verifica)** — Verificato il primo fixture Pack v3
  contro il parser reale di Domus: difetto bloccante — `recipes/<id>/
  recipe.json` consegnato come envelope `{recipes:[…],schemaVersion}`
  invece che oggetto ricetta nudo → il parser scarterebbe tutte le ricette.
  Contratto chiarito (sezione CONTRATTO EXPORT): recipe.json = ricetta
  nuda, `schemaVersion` solo in `book.json`. Memoria rigenera il fixture;
  Domus aggiunge `mediaAuthor` allo schema.
- **2026-05-23 (Recipees, audit)** — Audit di prontezza al lancio
  (`Ricette/AUDIT_lancio_5giugno_2026-05-23.md`). Verificato che il fixture
  v2 è conforme. Scoperta principale: Domus importa audio/video ma non li
  mostra (nessun player nel dettaglio ricetta). Due decisioni del fondatore:
  (1) il player audio/video Domus + attribuzione "Voce di…" entrano nel
  lancio del 5 giugno, non fast-follow; (2) la beta amici usa TestFlight
  interno (niente Beta App Review). Recipe Keeper declassato a post-lancio
  (già coperto dal fallback Smart AI).
- **2026-05-23 (Recipees, esecuzione)** — **Crea Menu mergiata in produzione.**
  Decisione del fondatore: portare Crea Menu live senza aspettare il
  post-lancio. Merge `feat/crea-menu` → `main` (fast-forward, 13 commit,
  `6ee9bce`), `tsc` pulito, Vercel deploy Production verde, `/menus` live su
  recipees.app. Da feature post-lancio diventa parte della beta del 5 giugno.
  `SPEC_crea_menu.md` riallineata all'as-built. Emerso al merge: 33 errori
  ESLint a livello di progetto (debito `react-hooks/*`, non bloccante per il
  build Next.js 16) → tracciato in `ROADMAP_bug.md`, owner Domus.

---

## CASELLA BRIEF (coordinamento a doppio senso)

Messaggi tra sessioni. Chi scrive mette data + sessione mittente →
destinatario. Chi gestisce marca `[GESTITO]` in testa, ma non cancella.

### Aperti

- **[NUOVO] 2026-05-30 · Recipees → tutte le sessioni: organizzazione sessioni + guardia CLAUDE.md.**
  Check delle sessioni esistenti su `/Ricette`: ce ne sono sei — Recipees
  (coordinamento), **Memoria debug session** (la viva, ha fatto il fix
  data-loss), **Memoria legacy**, **Domus legacy**, **Domus feature
  development**, **Domus debug**. Due constatazioni e le scelte del fondatore:
  · **Tutte girano da `cwd = /Ricette` (root)**, nessuna dalla propria
    sottocartella → finora caricavano solo il `CLAUDE.md` di coordinamento e
    **non** i `CLAUDE.md`/`AGENTS.md` di prodotto (pattern Codable per Memoria,
    Modalità non-distruttiva + warning Next.js 16 per Domus). **Fix applicato:**
    aggiunta in cima a `CLAUDE.md` root una **guardia "chi sei?"** che istruisce
    ogni sessione prodotto a leggere subito il proprio `CLAUDE.md`+`AGENTS.md`.
    Raccomandato comunque, per le sessioni nuove, lanciarle da `Heirloom/` o
    `recipees-domus/` così l'auto-load è nativo.
  · **Duplicati legacy** (Memoria legacy, Domus legacy): superati dalle
    sessioni vive. Scelta del fondatore (30 mag): **tenerle per ora**, non
    archiviarle. Quando si decide di chiudere il ciclo, sono candidate
    all'archiviazione (restano riapribili; lo stato è già nell'hub).
  · Naming: "Memoria debug session" è di fatto **la** sessione Memoria
    (prodotto a sessione singola, non si splitta feature/debug come Domus).

- **[RISOLTO] 2026-05-30 · Memoria ↔ Recipees: fix DATA-LOSS confermato — build verde + verifica decode.**
  Build Xcode `BUILD SUCCEEDED` (0 errori, commit `e613e47`). Il bug critico nel memberwise init è stato corretto: `init(from:)` spostato in extension di `Book` → Swift rigenera il memberwise init (usato da `LibraryView`, `BookCoverCreationFlow`, `BlockListView/SessionView/RecipeReviewView`). Fix data-loss a 3 livelli verificato nel sorgente + test Swift standalone: JSON pre-2026-05-23 senza chiave `blocks` decodificato correttamente (books=1, blocks=0, credits=10). ROADMAP_bug.md → **Risolto** per tutti e 6 i bug *In fix*. Release gate superato. **Nota:** il test era via Swift CLI, non su device fisico — per il release gate completo conviene installare la build su iPhone fisico sopra una versione precedente con dati reali (5 min di test prima di TestFlight).

- **[NUOVO] 2026-05-30 · Recipees → Domus: verifica a vista del flusso login/auth — NON risulta eseguita.**
  La sessione Domus ha lavorato il login in 7 commit da `2d004d8` a `2ebb2b5` (fix definitivo: `searchParams` dal server come props, rimosso `useSearchParams()`, nessuna `<Suspense>`). Il fix è in produzione dal 26 mag. Nell'hub non risulta nessuna riga "verificato a vista dal fondatore" per questo flusso.
  **Azione richiesta:** fai una verifica a vista su `recipees.app` — signup, login email, login Google — su desktop E su mobile (iPhone Safari, in quanto molti tester useranno il mobile). Verifica in particolare:
  - Login Google non apre skeleton "Domus" → reindirizza correttamente
  - Redirect post-login funziona (nessuna pagina bianca)
  - Errori di login mostrati correttamente in cima alla card
  - Su mobile: redirect Google (non popup) → ritorno all'app dopo auth
  Conferma qui con esito + screenshot se disponibile. Regola invariata: niente «Risolto» senza conferma visiva.

- **[ATTIVO] Memoria — checklist verso il 5 giugno** (riepilogo compatto; storia completa in `HUB_archivio.md`).
  1. **Fix data-loss** — ✅ CHIUSO. Build verde, decode JSON pre-2026-05-23 verificato. Raccomandato: test su iPhone fisico sopra build precedente prima di TestFlight (5 min).
  2. **5 fix camera/pipeline** — ✅ CHIUSI. Build verde conferma i fix (camera portrait-lock pbxproj, pipeline shouldBake/routing/import). ROADMAP_bug.md → Risolto.
  3. **Export Pack v3 reale da iPhone** — ⏳ APERTO. Il fixture v2 è verde end-to-end (141/141 assert), manca un export vero da un ricettario reale su device fisico. Voce del checkpoint 2 giu.
  4. **TestFlight INTERNO** (no Beta App Review): ⏳ App Store Connect + build production + upload, tester amici come utenti interni.
  5. **Launch screen** brandizzato — ⏳ decisione di design ancora aperta (LaunchScreen.storyboard presente ma contenuto da definire).
  Già fatto: rebrand pbxproj (display name + usage string), `NSCameraUsageDescription` aggiunta, deployment target iOS 17.0, commit `e613e47`.

- **[ATTIVO] Domus — unico item aperto verso il 5 giugno:** verifica live **Sharing Fase 1** (serve un grant attivo per testare end-to-end fork + notifica autore). Più la verifica login/auth del brief 30-05 qui sopra. Backlog bug a zero.

- **[POST-LANCIO] Specs pronte — non iniziare prima che la beta del 5 giugno sia uscita:**
  - **Crea Menu** — ✅ già live in produzione (`/menus`, merge `6ee9bce`). Non più "da fare".
  - **Acquisizione multipagina (Memoria)** — `SPEC_multipagina.md`. Step 1-5 implementati, Step 6 (riapertura incrementale) post-lancio.
  - **Pianifica 2.0 (Memoria)** — `SPEC_pianifica.md`. Coda di lavoro con passi spuntabili + intake a dialogo guidato AI.

### Archiviati

I brief gestiti/chiusi (2026-05-24 e precedenti) sono in **`HUB_archivio.md`**.
Includono: negoziazione e verifica del formato Pack v3, consegne fixture,
Crea Menu (v1 + rifiniture + merge), player audio/video, chiusura del backlog
bug Domus, deployment target e usage string Memoria. Lettura solo storica.

---

## CONVENZIONI E REGOLE CONDIVISE

- **⚠️ REGOLA INVIOLABILE — i dati preesistenti dell'utente non si toccano.**
  Dal momento in cui una funzione è attiva lato utenti, tutto ciò che
  l'utente aveva già — ricettari, ricette, pagine, foto, menù — deve
  restare **intatto** attraverso ogni nuova build, aggiornamento o cambio di
  schema. Un update che cancella o corrompe dati preesistenti è un
  fallimento grave: distrugge la fiducia, e la fiducia è il prodotto.
  Conseguenze pratiche, valide per **Memoria e Domus**: (1) ogni cambio di
  schema dati è **migration-safe** — campi nuovi opzionali o con decodifica
  tollerante alle chiavi mancanti; per il `Codable` di Swift questo significa
  `decodeIfPresent`, **non** un default value (la sintesi automatica ignora
  i default in decodifica e lancia su chiave mancante); (2) la persistenza è
  **fail-safe** — se un caricamento fallisce non si sovrascrivono mai i dati
  esistenti: semmai si conserva una copia e si segnala; (3) niente
  operazioni distruttive automatiche su dati reali. Nata 2026-05-24 dopo
  l'incidente Memoria (una nuova build ha cancellato i ricettari
  preesistenti — vedi CASELLA BRIEF). La regola «Domus — dato utente sacro»
  qui sotto ne è la declinazione operativa per Domus.
- **Release gate — test di aggiornamento prima di ogni build per i tester.**
  È l'enforcement della regola qui sopra: una regola scritta non basta,
  serve un controllo che blocca la spedizione. Nessuna build Memoria
  raggiunge un beta tester senza un *test di aggiornamento*: si parte da
  dati reali salvati con la build precedente, si installa la nuova build
  sopra, si verifica che i ricettari ci siano ancora — tutti, integri.
  Per Domus l'equivalente: nessun cambio di schema va in produzione senza
  aver verificato che i documenti preesistenti restino leggibili e
  modificabili. Vale a ogni release, non come controllo una tantum. Va
  nella checklist di lancio del 5 giugno e del checkpoint del 2.
- **⚙️ Sessioni parallele su `recipees-domus` — worktree, non turni.**
  Sostituisce la vecchia regola «un solo percorso di commit per volta»
  (nata dopo il commit duplicato del 23 mag, ora archiviata). Quando più
  sessioni lavorano Domus in contemporanea — tipicamente **Domus-funzionalità**
  e **Domus-debug** — ognuna lavora in un **git worktree separato su un
  branch dedicato**, non sullo stesso checkout di `main`:
  - Domus-debug → branch `fix/<bug>`; Domus-funzionalità → branch `feat/<nome>`.
  - Ogni sessione committa e pusha **solo il proprio branch** via Desktop
    Commander (o git nativo Claude Code). Nessuna sessione committa su `main`
    direttamente.
  - **Il merge in `main` lo fa Recipees** (supervisore), come già per
    `feat/crea-menu` → `6ee9bce`: verifica `tsc` + `eslint`, conferma a vista
    quando è UI, poi fast-forward/merge e push. Vercel autodeploya da `main`.
  Così due sessioni lavorano davvero in parallelo senza pestarsi i piedi sul
  git, e nessuna resta ferma ad aspettare l'altra. Dettaglio operativo in
  `recipees-domus/CLAUDE.md`. *Eccezione:* per un hotfix urgente quando gira
  una sola sessione Domus, commit diretto su `main` resta ammesso — la regola
  worktree serve quando le sessioni sono **due o più** in contemporanea.
- **Una sessione = un prodotto = una verità di stato.** Niente sessioni
  doppie sullo stesso prodotto (es. due "Domus" che descrivono lo stato in
  `RECIPEES_HUB.md`): due contesti divergono e l'hub perde la fonte unica.
  Le sessioni legittime e distinte: **Recipees** (coordinamento),
  **Memoria** (iOS), **Domus-funzionalità** e **Domus-debug** (stesso repo,
  worktree separati, vedi regola sopra). Le vecchie sessioni Cowork
  pre-migrazione Claude Code vanno archiviate.
- **Brand voice:** memoir, sostantivi concreti, no urgenza, no tech-speak.
  Fonte: `Ricette/Recipees - La genesi.md`.
- **Domus — dato utente sacro:** soft delete, schema additive-only, niente
  script distruttivi senza dry-run + OK esplicito. Fonte:
  `recipees-domus/AGENTS.md`.
- **Bug di UI / rendering — conferma visiva prima di «Risolto».** Un bug che
  riguarda la resa a schermo (layout, larghezze, visibilità di un elemento,
  stile) non passa a «Risolto» in `ROADMAP_bug.md` senza una verifica **a
  vista** — screenshot prima/dopo o click-through sulla schermata reale.
  `tsc` + `eslint` puliti dicono che il codice compila, non che si veda
  giusto. Vale per ogni sessione. Regola nata il 2026-05-24 dopo due casi
  (Crea Menu, riga ingredienti) in cui un fix verificato solo a livello di
  codice non spostava il sintomo.
- **Memoria — Xcode 16 sync group:** mai aggiungere file a mano al
  `project.pbxproj`. Deployment iOS 17, Swift 6 strict concurrency.
- **Feedback beta:** `recipees.app/feedback` traccia le segnalazioni
  (collection Firestore `feedback`) per Memoria / Domus / Folio.
- **Gestione beta tester:** cartella privata `Ricette/beta-testers/` —
  mai in git, mai in memoria Claude. Si legge solo su richiesta esplicita.
