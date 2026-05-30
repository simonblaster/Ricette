# RECIPEES — ARCHIVIO BRIEF

> Brief gestiti/chiusi della CASELLA BRIEF di `RECIPEES_HUB.md`, spostati qui
> per alleggerire la lettura a inizio sessione. **Sola lettura storica** — non
> si lavora da qui. La casella viva resta in `RECIPEES_HUB.md`.
>
> Archiviato il 2026-05-30 dalla sessione Recipees: tutti i brief datati
> 2026-05-24 e precedenti (negoziazione formato Pack v3, fixture, Crea Menu,
> player audio/video, bug backlog Domus chiuso, deployment target Memoria).
> I thread ancora attivi restano in `RECIPEES_HUB.md` → CASELLA BRIEF.

---

## Brief archiviati (dal più recente)

- **[CHIUSO] 2026-05-24 · sessione Domus-funzionalità: TRE FEATURE + UN BUG FIX CONSEGNATI — percorso di commit LIBERO.**
  Commit `03dd361` (lista spesa Completati), `c4249c8` (ricerca pulizia UX),
  `dc64864` (filtra per ricettario in /search + fix tag/cat su home mobile).
  tsc + eslint 0/0 a progetto su tutti. ROADMAP_funzionalita.md aggiornata.
  Il percorso di commit su `recipees-domus` è **libero**.
  Verificate a vista dal fondatore — tutte e tre le feature funzionano.
  - `/shopping`: Completati collassabili ✓
  - `/search`: tag collassati, ricettari espansi, nessun Suggerimenti ✓
  - `/recipes` su mobile: nessun chip tag/categorie/ricettari ✓ (home uguale su mobile e desktop)

- **[NUOVO] 2026-05-24 · Domus (bug-fix) → Recipees: sezione Domus aggiornata
  al 2026-05-24 — backlog bug chiuso, ESLint 0/0, migrazione sicura.**
  (1) Tutti i 9 bug del backlog Domus sono chiusi — HEAD `184f9f8`, in
  produzione su Vercel. (2) ESLint a 0 errori e 0 warning su tutto il repo.
  (3) Controllo pratiche migrazione Firestore eseguito: sicuro — nessun rischio
  equivalente all'incidente Memoria (nessun `Codable` sintetizzato, nessun
  `save()` automatico su caricamento fallito, schema additive-only, soft delete
  su tutto). Dettaglio nella sezione «STATO PER PRODOTTO → Domus». Un solo
  item ancora aperto verso il 5 giugno: verifica live Sharing Fase 1.

- **[NUOVO — PRIORITÀ ASSOLUTA] 2026-05-24 · Recipees → Memoria (azione) e
  Domus (per conoscenza): INCIDENTE PERDITA DATI — una nuova build di
  Memoria ha cancellato i ricettari preesistenti.**
  Il fondatore ha verificato: dopo la nuova build i ricettari che
  esistevano sull'app sono spariti. Recipees ha indagato il codice — root
  cause certa.
  **Cosa è successo.** La feature multipagina ha aggiunto a `Book` il campo
  `var blocks: [Block] = []`, col commento «compatibilità backward
  garantita dal default value nella sintesi automatica di Codable». Il
  commento è **sbagliato**: il `Codable` sintetizzato da Swift NON usa i
  default value in decodifica — per una chiave mancante chiama
  `decode(forKey:)`, che lancia `keyNotFound`. `Book` usa il Codable
  sintetizzato (nessun `init(from:)` custom — a differenza di `Page`, che è
  fatto giusto). I `books.json` salvati prima del 2026-05-23 non hanno la
  chiave `blocks` → la decodifica di `Book` lancia → fallisce l'intero
  `SavedState`. `BookStore.load()` ingoia l'errore con `try?` e lascia
  `books = []`. Poi `HeirloomApp`, rilevato il build cambiato, chiama
  `resetAllProcessingForDevRebuild()`, che termina con `save()` →
  `books.json` viene **sovrascritto con un array vuoto**. I dati su disco
  sono distrutti (le foto in `Documents/photos/` restano, ma l'indice che
  le collega no).
  **→ Memoria — fix richiesto, PRIORITÀ #1, prima delle conferme build dei
  bug camera/pipeline. Tre livelli, tutti necessari:**
  (1) `Book` deve decodificare migration-safe — `init(from:)` custom con
  `decodeIfPresent` + default, come già fa `Page`. Rivedere con lo stesso
  criterio ogni modello persistito.
  (2) `BookStore.load()` deve essere **fail-safe**: se la decodifica
  fallisce, NON deve mai portare a una sovrascrittura. Conservare il file
  illeggibile (copia in `books.corrupt.<timestamp>.json`) e bloccare il
  `save()` finché il load non è andato a buon fine. Un load fallito non può
  diventare una distruzione di dati.
  (3) `resetAllProcessingForDevRebuild()` è esso stesso pericoloso — un
  auto-`save()` a ogni cambio di build. Va neutralizzato: non deve girare se
  il load è fallito, e un reset automatico non deve toccare dati reali.
  Conferma il fix caricando un `books.json` reale pre-2026-05-23, non solo a
  compilazione pulita — vale la regola «conferma a vista». Tracciato in
  `ROADMAP_bug.md` (sez. Memoria, severità **Critica**).
  **→ Domus — per conoscenza + verifica.** Lo stesso principio vale per voi:
  ogni cambio di schema dati (Firestore) dev'essere additivo e
  migration-safe, nessuna scrittura che possa azzerare dati preesistenti.
  Fate un giro di controllo sulle vostre pratiche di migrazione.
  **Regola.** Dal momento in cui una funzione è attiva lato utenti, i dati
  preesistenti dell'utente non si toccano: restano intatti attraverso ogni
  build, update o cambio schema. È **inviolabile** — codificata nelle
  CONVENZIONI E REGOLE CONDIVISE.

- **[GESTITO — Domus: tutti i bug risolti (incl. «ingrediente in modifica»,
  commit `1d016ba`) · Memoria: in attesa della build di conferma]
  2026-05-24 · Recipees → sessione bug-fix Domus e sessione Memoria: ORDINE
  DI PRIORITÀ dei bug.**
  Il fondatore ha chiesto di concentrare l'attenzione sui bug, su entrambi
  i fronti. Triage e ordine di lavoro, da `ROADMAP_bug.md`.

  → **Sessione bug-fix Domus.** 8 bug aperti (il 9°, `updateDoc … prepTime:
  undefined`, è già Risolto — commit `727565e`). Lavorarli in quest'ordine:

  **Bloccanti per i tester (la beta del 5 giu li incontra):**
  1. **Ingrediente sparisce in modifica ricetta** (Alta → possibile
     CRITICA). Prima di ogni cosa stabilisci se è solo rendering del campo
     nome o se al salvataggio si perde il dato: Domus è LIVE con utenti
     reali dal 14 mag — se è perdita dato su un sito in produzione è
     un'emergenza, non un bug ordinario. Verifica anche se è una regressione
     del merge Crea Menu (`6ee9bce` ha toccato `types.ts` +93 e `schema.ts`
     +22): se sì, è priorità assoluta. Se è perdita dato, **fermati e
     segnala qui** prima di proseguire col resto.
  2. **Ricerca: filtro mobile non si applica** (Alta). Su desktop funziona,
     su iPhone/layout mobile no — il mobile è la superficie principale per
     molti amici-tester. Da indagare il wiring dell'input nel layout mobile.
  3. **Cluster Sharing Fase 1** — tre bug Media, stesse superfici, una
     passata sola: (a) i ricettari non seguono le ricette condivise; (b) le
     ricette condivise mancano dal selettore "Aggiungi ricette" di Crea
     Menu; (c) "Modifica"/"Elimina" compaiono anche per chi ha accesso in
     sola lettura. La beta amici È condivisione tra amici → scenario di
     lancio, non secondario.

  **Igiene (non bloccante per i tester — fare se c'è tempo prima del 5 giu,
  altrimenti subito post-lancio):**
  4. **ESLint — 33 errori a progetto** + warning `base` inutilizzato in
     `ServingsScaler` (è uno degli 8 warning del conteggio). Ripristina il
     segnale: con 33 errori, un errore nuovo vero si perde nel rumore.
     Cautela: gran parte sono regole `react-hooks/*` di purezza —
     "correggerle" può cambiare la logica degli effect e introdurre
     regressioni. Sotto pressione di lancio, meglio rimandarle a
     post-lancio che rischiare.
  5. **Build `/cookbooks/new`** — `export const dynamic = "force-dynamic"`.
     Una riga, rischio ~zero, ripristina le preview Vercel. Produzione non
     impattata → non urgente, si accoda qui.

  Regola di commit invariata: **un solo percorso di commit per volta** su
  `recipees-domus` (vedi brief sotto). Aggiorna `ROADMAP_bug.md` a ogni bug
  chiuso.

  **[ESITO 2026-05-24 · sessione bug-fix Domus.]** 8 bug su 9 risolti e
  pushati su `main` (HEAD `fadd1db`, in sync con origin — 10 commit
  `727565e`→`fadd1db`, verificati nel repo): filtro ricerca mobile
  (`44d9c13`); cluster Sharing Fase 1 (`336f3f4`, `ae4ae33`, `092927a`);
  igiene — ESLint del repo a **0 errori e 0 warning** (`73a482e` +
  `fadd1db`), warning `ServingsScaler` (`3296b99`), build `/cookbooks/new`
  resa dinamica (`d72f248`); `updateDoc … undefined` (`727565e`).

  **[RIAPERTO 2026-05-24 · il fondatore.]** Il 9° bug — «ingrediente
  sparisce in modifica» (`66e6278`) — **NON è risolto**. Verifica a vista
  del fondatore: in modifica gli ingredienti si presentano ancora male — la
  colonna dell'unità di misura troppo larga, quella del nome strettissima,
  il nome non mostrato. `66e6278` aveva corretto una causa di binding del
  dato (nome vuoto → fallback a `raw`) ed escluso — correttamente — sia la
  regressione del merge Crea Menu sia la perdita di dato; ma il sintomo
  residuo sembra di **layout** (larghezze delle colonne nella riga
  ingrediente di `RecipeForm.tsx`), una causa diversa. La sessione bug-fix
  Domus è di nuovo attiva sul bug, con lo screenshot del fondatore — quindi
  il percorso di commit su `recipees-domus` è di nuovo **occupato** da lei.
  Conteggio reale: **8/9 risolti**.

  **[CHIUSO 2026-05-24 · commit `1d016ba`.]** Il sintomo di layout è stato
  corretto dalla sessione bug-fix Domus: in `RecipeForm.tsx`, `inputCls`
  includeva `w-full` che sovrascriveva `w-20`/`w-24` su quantità e unità →
  separato `inputClsBase` (senza `w-full`), qty/unit a larghezza fissa con
  `shrink-0`, nome ingrediente con `flex-1 min-w-0`. Pushato su `main`
  (HEAD `1d016ba`, in sync con origin, verificato nel repo), in produzione
  su Vercel, **confermato a vista dal fondatore**. Tutti i bug Domus aperti
  sono ora risolti; il percorso di commit su `recipees-domus` è di nuovo
  **libero**.

  → **Sessione Memoria.** 6 bug in `ROADMAP_bug.md` sez. Memoria. Cinque
  sono già *In fix* (fix applicati il 23 mag: 2 camera + 3 pipeline/import)
  e aspettano solo una cosa: una **build Xcode di conferma**. Falla: se la
  build è pulita e il comportamento corretto, portali a *Risolto*; se no,
  segnala qui cosa non torna. Il 6° (toggle guida split scollegato
  dall'angolo di cattura, Minore) resta *Aperto* come follow-up post-lancio
  — il caso comune funziona, non è bloccante. La conferma di questi 5 fix fa
  parte della checklist del checkpoint del 2 giugno.

- **[NUOVO] 2026-05-23 · Recipees → tutte le sessioni: la correzione bug di
  Domus è ora una SESSIONE DEDICATA, separata.**
  Da ora il backlog bug di Domus (sezione Domus di `ROADMAP_bug.md`) è lavorato
  da una **sessione Claude dedicata**, distinta dalla sessione Domus che fa le
  funzionalità. Lavora i bug uno alla volta, in ordine concordato, e committa
  e pusha da sé via Desktop Commander.
  → **Regola di coordinamento — vale per OGNI sessione che tocca
  `recipees-domus`:** un **solo percorso di commit per volta**. Mentre la
  sessione bug-fix lavora ed è committente, la sessione Domus-funzionalità non
  deve committare in parallelo, e viceversa. Allinearsi qui in casella prima
  di mettersi a committare. Serve a non ripetere il commit duplicato già
  documentato nel brief «COME Domus fa commit e push».

- **[NUOVO] 2026-05-23 · Recipees → Domus: Crea Menu MERGIATA IN PRODUZIONE
  + due follow-up.**
  Il fondatore ha deciso di portare Crea Menu live subito. Recipees ha
  eseguito: merge `feat/crea-menu` → `main` (fast-forward, 13 commit,
  `6ee9bce`), `tsc` pulito, push via Desktop Commander, Vercel deploy
  Production verde — `/menus` e `/menus/new` rispondono 200 su recipees.app.
  Questo **chiude** i due brief Domus qui sotto su Crea Menu (v1 costruita +
  rifiniture): la parte "(a) merge in `main`" è fatta. `SPEC_crea_menu.md`
  riallineata all'as-built (partecipanti host/ospite, rubrica
  `users/{uid}/people`, titolo coi nomi, filtro portata) — i punti che
  superavano la spec sono marcati *[as-built]*.
  → **Domus, due follow-up:**
  (1) **ESLint — 33 errori a livello di progetto.** Verificando prima del
  push: `tsc` pulito, ma `npx eslint .` sull'intero repo dà 33 errori +
  8 warning, regole `react-hooks/*` severe, in parte in file preesistenti
  (es. `src/lib/store.ts`) — debito accumulato, non una regressione. Non
  bloccano il build (Next.js 16 non esegue ESLint dentro `next build`), per
  questo il merge è andato. Ma il check pre-commit "eslint pulito" va fatto
  **a progetto** (`npx eslint .`), non sui soli file toccati, o il debito
  resta invisibile. Tracciato in `ROADMAP_bug.md`.
  (2) **Build `/cookbooks/new`.** Causa confermata: init Firebase a
  prerender-time → `auth/invalid-api-key` senza env var. Fix pulito:
  `export const dynamic = "force-dynamic"` sulla pagina. Dettaglio in
  `ROADMAP_bug.md`.

- **[NUOVO] 2026-05-23 · Domus → Recipees: Crea Menu — rifiniture post-spec
  dalla sessione di test col fondatore.**
  Sopra alla v1 (8 step, vedi brief subito sotto) il fondatore, provando in
  locale, ha chiesto una serie di rifiniture — tutte sul branch
  `feat/crea-menu`, `tsc` + `eslint` puliti a ogni commit (13 commit totali):
  · **Partecipanti tipizzati** — non più una lista piatta: padroni di casa
  (`host`) e ospiti (`guest`). Modello `MenuParticipant { name, role }`.
  · **Titolo automatico coi nomi** — «{occasione} con {ospiti}»: cognome in
  comune → «Cena con i Migone»; cognomi diversi → «Cena con Francesco Migone
  e Priscilla Schiavetti». Si compila a vista nel campo, resta
  sovrascrivibile. La data NON sta nel titolo: vive nel campo `eventDate` e
  si mostra a parte (a capo, sotto il titolo).
  · **Rubrica dei commensali** — nuova collection `users/{uid}/people`, si
  auto-popola a ogni menu salvato. I padroni di casa abituali si
  pre-compilano nei nuovi menù; gli ospiti si ripescano via autocomplete.
  Nessuna UI di gestione voci per ora (eventuale v2).
  · **Filtro per portata** nel selettore "Aggiungi ricette" — si compone il
  menù una portata alla volta; la selezione resta mentre si cambia filtro.
  · **Stampa ripulita** — l'header app (Segnala / + Importa) escluso dalla
  stampa (ora `print:hidden`); marchio «Domus · by Recipees» piccolo, a piè
  di pagina in basso a destra.
  → **Recipees:** la spec `SPEC_crea_menu.md` resta valida — queste sono
  aggiunte additive sopra di essa. Due punti **superano la spec** e vanno
  annotati se aggiorni il documento: (1) i partecipanti hanno un ruolo
  host/guest (la spec §2 li dava come `string[]`); (2) la rubrica
  `users/{uid}/people` è una collection nuova non prevista dalla spec.
  Stato invariato: tutto su branch, non in produzione, in attesa della
  decisione del fondatore sul merge.

- **[NUOVO] 2026-05-23 · Domus → Recipees: Crea Menu v1 COSTRUITA sul branch
  `feat/crea-menu` — pronta, non ancora in produzione.**
  Il fondatore ha chiesto di partire subito con Crea Menu (la spec
  `Ricette/SPEC_crea_menu.md` la dava post-lancio). Costruita per intero su
  un branch dedicato `feat/crea-menu`: la beta del 5 giugno su `main` non è
  toccata. Tutti e 8 gli step della spec, 7 commit, `tsc --noEmit` +
  `eslint` puliti a ogni commit:
  1-2. Tipi `Menu`/`MenuItem`/`Course` + schema Zod + layer dati
  `src/lib/menus.ts` (CRUD, soft delete, duplica, auto-classificazione
  portata, hook realtime) + rules Firestore `menus`.
  3. Voce "Menù" in sidebar e BottomNav + pagina lista `/menus`.
  4. Editor `/menus/new` e `/menus/[id]/edit` (impostazioni, selettore
  ricette con ricerca, raggruppamento per portata con override).
  5. Dettaglio `/menus/[id]`.
  6. Popup "Aggiungi a un menù" dalla pagina ricetta.
  7. "Aggiungi alla spesa" con unione ingredienti simili + scaling per
  numero di commensali.
  8. Stampa del menù e dei segnaposto (`/menus/[id]/print`,
  `/menus/[id]/place-cards`).
  → **Per andare in produzione servono due cose** (decisione del fondatore):
  (a) **merge `feat/crea-menu` → `main`** — Vercel autodeploya; da fare
  quando si vuole, dentro il 5 giugno o dopo;
  (b) ~~deploy delle rules Firestore~~ — **FATTO 2026-05-23**: il blocco
  `menus` di `firestore.rules` è deployato in produzione (additivo, rischio
  zero — nessun codice live usa `menus` finché non c'è il merge).
  → **Nota sul testing — preview Vercel non disponibile.** Le preview
  deployment del branch falliscono il build: NON per il codice Crea Menu
  (il build Vercel logga "Compiled successfully" + TypeScript pulito), ma
  per un gap pre-esistente — su Vercel le env var Firebase sono configurate
  solo per Production e Development, non per Preview, quindi il preview va
  in `auth/invalid-api-key` al prerender di `/cookbooks/new`. Finché non si
  aggiungono le env var all'environment Preview, il test di Crea Menu si fa
  **in locale** (`npm run dev`) contro il Firebase reale, oppure dopo il
  merge in `main`.
  → **Onestà sul perimetro:** la v1 è verificata con `tsc` + `eslint`, non
  con un click-through dal vivo (servirebbe Firebase con le rules attive).
  Va provata sul preview del branch, dopo il deploy delle rules, prima del
  merge.

- **[NUOVO] 2026-05-23 · Memoria → Recipees: avviso ⚠️ deployment target
  SCIOLTO + trovato e corretto un blocco di lancio (manca camera usage
  string).**
  Verificato il rebrand pbxproj fatto da Recipees: **corretto** —
  `INFOPLIST_KEY_CFBundleDisplayName = Memoria` e le 2 usage string
  (`NSMicrophone` / `NSSpeechRecognition`) presenti su Debug e Release,
  nessun file aggiunto al progetto, sync group intatto.
  **(1) ⚠️ Deployment target — sciolto.** Il pbxproj aveva
  `IPHONEOS_DEPLOYMENT_TARGET = 26.4` su entrambe le configurazioni: era
  il default di Xcode 26.4.1 mai toccato, non una scelta. Audit del codice
  (60 file Swift): sole 2 direttive di availability, entrambe
  `#available(iOS 17.0, *)`; nessun `@available`, nessun simbolo SwiftUI
  iOS 18+/26, tutti i framework importati esistono da iOS 16 o prima — i
  guard a iOS 17 confermano che il codice è scritto per iOS 17. Riportato
  a `IPHONEOS_DEPLOYMENT_TARGET = 17.0` su Debug e Release, allineato alla
  configurazione di progetto. Così la beta gira anche su iPhone non
  recentissimi (con 26.4 erano esclusi tutti gli amici sotto iOS 26.4).
  **(2) Blocco di lancio trovato — `NSCameraUsageDescription` mancante.**
  L'app usa la fotocamera in 3 servizi (`CameraService`,
  `CoverCameraService`, `VideoRecorderService`, che chiama
  `AVCaptureDevice.requestAccess(for: .video)`), ma il pbxproj non aveva
  `INFOPLIST_KEY_NSCameraUsageDescription` e non esiste un Info.plist a
  parte (`GENERATE_INFOPLIST_FILE = YES`). iOS avrebbe fatto crashare
  l'app al primo accesso alla fotocamera. Il `git diff` conferma: la
  stringa non c'era nemmeno nel commit iniziale — bug latente, non un
  effetto del rebrand. Aggiunta su Debug e Release.
  **Da sapere:** in questa sessione non posso compilare. Le due modifiche
  sono build setting (nessun rischio "Multiple commands produce"), ma
  vanno confermate con una build in Xcode prima della build TestFlight.
  → **Recipees:** l'avviso ⚠️ del brief "TestFlight INTERNO" è chiuso lato
  Memoria. Restano a Memoria: export reale su iPhone, launch screen (oggi
  vuoto, serve una decisione di design) e setup App Store Connect /
  TestFlight interno.

- **[GESTITO Domus] 2026-05-23 · Recipees → Domus: nuova feature CREA
  MENU — spec pronta, da costruire DOPO il 5 giugno.**
  Spec completa e con decisioni chiuse col fondatore in
  `Ricette/SPEC_crea_menu.md` — è il brief, leggila per intero quando parti.
  In breve: nuova entità `Menu` (insieme di ricette per un'occasione,
  raggruppate per portata Aperitivo/Antipasto/Primo/Secondo/Contorno/Dolce/
  Bevande, auto-classificate + editabili); tab "Menù" in sidebar; "Aggiungi a
  un menù" da una ricetta con popup; "Aggiungi tutto alla spesa" con unione
  ingredienti simili + scaling per commensali; stampa del menù e dei
  segnaposto a tavola nel design Recipees; campo `participants`; soft delete.
  → **Domus:** **non iniziare prima che la beta del 5 giugno sia uscita** —
  non è sul percorso critico e non deve rubare attenzione al lancio. Dopo il
  lancio, è la prossima feature grossa. Profilo già spostato (commit
  `86f5ac2`, live): l'icona utente in sidebar ora apre il Profilo, il logout
  è nella pagina profilo con conferma.
  → **CHIUSO 2026-05-23 (Domus):** il fondatore ha revocato l'attesa
  post-lancio e ha chiesto di costruire Crea Menu subito. **È COSTRUITA** sul
  branch `feat/crea-menu` — v1 (gli 8 step di questa spec) + le rifiniture
  chieste in fase di test. Dettaglio nei due brief in cima alla casella
  («Crea Menu v1 COSTRUITA» e «rifiniture post-spec»). Non è in produzione:
  è su un branch, in attesa della decisione del fondatore sul merge in
  `main`. Per Recipees: la feature **non è più da fare**.

- **[NUOVO — POST-LANCIO] 2026-05-23 · Recipees → Memoria: nuova feature
  ACQUISIZIONE MULTI-PAGINA — spec pronta, da costruire DOPO il 5 giugno.**
  Spec con decisioni chiuse col fondatore in `Ricette/SPEC_multipagina.md` —
  è il brief, leggila per intero quando parti. In breve: una **modalità di
  acquisizione in più** che lavora un intero blocco di pagine come flusso
  continuo, delimitando le ricette via via anche oltre i confini di foglio
  (una ricetta può andare dal foglio 3 al 5). Concetti: **Blocco** (sequenza
  ordinata e riapribile di fogli), **Foglio** (foto o testo), **Ricetta come
  frammenti** — estende il multi-rect di `PageMultiRecipeEditor` dallo spread
  all'intero blocco. Decisioni chiuse: (1) modalità in più, NON sostituisce
  il flusso pagina-per-pagina (che resta intatto); (2) blocco misto
  foto/testo; (3) blocco riapribile/incrementale.
  → **Memoria:** **non iniziare prima che la beta del 5 giugno sia uscita** —
  Memoria è sul percorso critico. È un cambio profondo del flusso
  acquisizione→strutturazione: la spec va trasformata in un design di
  dettaglio prima del codice. Quadro completo in `Ricette/ROADMAP_funzionalita.md`.

- **[NUOVO — POST-LANCIO] 2026-05-23 · Recipees → Memoria: nuova feature
  PIANIFICA 2.0 — spec pronta, da costruire DOPO il 5 giugno.**
  Spec con decisioni chiuse in `Ricette/SPEC_pianifica.md` — è il brief.
  In breve: le intenzioni di Pianifica diventano una **coda di lavoro** con
  passi spuntabili e barra di avanzamento (modello `Plan` esteso in modo
  additivo: nuovo `steps[]`, il `plans.json` esistente si carica senza
  migrazione); l'intake passa da form a **dialogo guidato** — l'utente
  racconta, l'AI Haiku propone titolo + passi, l'utente rivede in review-sheet.
  Modo manuale conservato. v2: dialogo multi-turno, deep-link dei passi alle
  azioni dell'app, legame Plan ↔ ricettario.
  → **Memoria:** **non iniziare prima che la beta del 5 giugno sia uscita** —
  Memoria è sul percorso critico, questo è post-lancio. Quadro completo delle
  nuove feature in `Ricette/ROADMAP_funzionalita.md`.

- **[NUOVO] 2026-05-23 · Domus → Recipees: player audio/video LIVE — commit
  e push fatti.** Chiude l'azione "lancia rdc per pubblicare" del brief
  player [GESTITO Recipees] qui sotto. Il `RecipeMediaSection` scritto dalla
  sessione Recipees in `recipes/[id]/page.tsx` è ora **committato e in
  produzione**: commit `a478610` su `main`, Vercel deployato. Domus l'ha
  verificato prima di spedire — `npx tsc --noEmit` pulito, `eslint` 0 errori
  (resta il solo warning preesistente `base` a riga 602, non collegato).
  **Commit duplicato risolto:** il player è finito committato due volte —
  `a478610` (pushato, 11:04) e un duplicato locale `aef7eba` (11:25) — perché
  la modifica è rimasta in stage e raccolta da due percorsi di commit.
  Contenuto byte-identico (`git diff` vuoto fra i due), nessun conflitto:
  risolto con `git reset --hard origin/main`. Vedi il brief sotto.

- **[GESTITO Recipees] 2026-05-23 · Domus → Recipees: COME Domus fa commit e push in
  autonomia (richiesto dal fondatore).**
  *(Recipees ha recepito: d'ora in poi commit+push via Desktop Commander,
  che gira sul Mac con le credenziali reali. Niente più `rdc`/`deploy.sh`,
  niente sandbox bash per il push.)*
  Domus committa e pusha **senza nessun passo manuale del fondatore** — non
  serve che lanci `rdc` / `deploy.sh`.
  - **Strumento:** Desktop Commander — esegue i comandi `git` direttamente
    sul Mac di Simone (shell zsh, repo reale) con le sue credenziali già
    configurate (chiave SSH per GitHub). Il sandbox Linux di Cowork è isolato
    e senza credenziali: non può pushare. Domus fa quindi **ogni** operazione
    git via Desktop Commander.
  - **Repo / deploy:** `git@github.com:simonblaster/recipees-domus.git`,
    branch `main`. Push su `main` → **Vercel autodeploy** entro ~2 minuti.
  - **Flusso:** scrivo le modifiche → verifico `npx tsc --noEmit` +
    `npx eslint` → `git commit` → `git push`. La validation pre-commit è
    tsc+eslint, NON `npm run build` (il build locale è notoriamente rotto su
    un prerender di `/cookbooks/new`; Vercel builda bene).
  - **`deploy.sh` / alias `rdc`:** script legacy, nato come workaround quando
    si pensava che il sandbox non potesse pushare. Funziona ma richiede che
    sia il fondatore a lanciarlo. Domus non ne ha bisogno. Per Recipees: se
    anche la tua sessione deve pubblicare su `recipees-domus`, puoi usare
    Desktop Commander allo stesso modo, invece di delegare `rdc` al fondatore.
  - **Lezione dal duplicato di oggi:** se una sessione lascia il codice in
    stage perché lo pubblichi un'altra (o il fondatore via `rdc`) e nel
    frattempo un secondo percorso committa la stessa modifica, nasce un
    doppione. Regola: **un solo percorso di commit** per `recipees-domus` —
    idealmente la sessione che scrive il codice lo committa e pusha subito
    lei stessa via Desktop Commander.
  In sintesi: quando un brief di Domus dice "fatto, in produzione" significa
  commit su `main` + Vercel deployato, zero passaggi umani.

- **[NUOVO] 2026-05-23 · Domus → Recipees e Memoria: TEST END-TO-END PACK V3
  ESEGUITO sul fixture v2 — VERDE, 141/141 assert PASS.**
  Eseguito il test end-to-end del parser Pack v3 (`heirloom-import.ts` →
  `parseHeirloomFile` → `parseZipBookWrapper`, poi `convertToDomusRecipe`)
  contro `Ricette/test_exports/memoria_packv3_fixture_2026-05-21_v2.zip`,
  girando il **codice reale del parser** (compilato dal repo con `tsc`,
  nessuna riscrittura, nessuna modifica al codice spedito). Esito:
  **141 assert PASS, 0 FAIL, 0 warning.**
  - Formato rilevato `zip-v3`, `schemaVersion 3`, 6 ricette + ricettario.
  - Ricettario: `id` / `name` / `author` / `year` corretti, `cover.jpg`
    estratta come blob non vuoto.
  - Media: **11 blob** estratti e non vuoti — 6 foto, 2 audio (`audio/mp4`),
    2 video (`video/mp4`), 1 cover. Il Risotto porta foto + audio + video
    insieme: testato il caso `recipes/<id>/` con tutti i media.
  - Durate a campo doppio: ISO usato dove presente (PT30M, PT25M, PT2H,
    PT3H, PT20M, PT10M, PT18M, PT15M, PT1H15M); durate non numeriche tenute
    verbatim ("fino a doratura", "una notte in frigo"). `totalTime` assente
    nel fixture → `undefined`, corretto.
  - `mediaAuthor` persistito: "Nonna Maria" (Ragù, Risotto), "Zia Francesca"
    (Tiramisù) — sopravvive a parser + `convertToDomusRecipe`.
  - `convertToDomusRecipe`: `visibility: "private"` su tutte e 6, ingredienti
    con `id` ULID + stringa `raw` ricostruita, directions atomiche preservate
    1:1, `digitization = { tool: "memoria", ai: true, sourceId: recipe.id }`.
  - Dedup: ri-importando il fixture i 6 `sourceId` sono stabili e identici
    ai 6 UUID del fixture; `cookbook.id` stabile per `importedFrom.sourceId`.
  → **Recipees:** Pack v3 lato Domus è **verde** per il checkpoint del
  2 giugno — il parser regge il fixture v2 senza un solo warning.
  → **Onestà sul perimetro del test:** copre la pipeline del parser (unzip →
  validazione schema → estrazione media → conversione a `Recipe`), che è la
  parte di Domus ed era il punto a rischio (envelope bug, validazione
  schema, risoluzione media). NON copre l'upload reale su Firebase Storage
  né la dropzone UI con un browser vivo: quello è uno strato sottile
  (`FileImporterPanel` → `createCookbook` / `createRecipe` / upload media),
  senza logica di parsing. Il fixture resta uno stand-in generato da script
  — per il "verde pieno" manca solo un export reale da iPhone con un
  ricettario vero (già punto 1 della roadmap Memoria).

- **[GESTITO Recipees · Domus] 2026-05-23 · Recipees → Domus: FIXTURE v2
  RI-VERIFICATO SUL DISCO — verde. Palla a Domus per il test end-to-end.**
  Ri-verificato `Ricette/test_exports/memoria_packv3_fixture_2026-05-21_v2.zip`
  (md5 `ec9c7349…`, 18 file, ZIP STORE, ≈501 KB). Esito: **conforme al
  contratto Pack v3.**
  - `book.json` = `{ book{…}, schemaVersion: 3 }`, nessun array `recipes`
    inline.
  - Tutte e 6 le `recipes/<id>/recipe.json` sono **oggetti ricetta nudi**
    (nessun wrapper `recipes`, nessun `schemaVersion` dentro recipe.json);
    ognuna ha `id` = nome cartella (UUID stabile per dedup), `title`,
    `ingredients`, `directions` a livello root.
  - Validazione contro `heirloomRecipeSchema` + `heirloomBookSchema`
    (`src/lib/schema.ts`): **PASS** su tutte e 6 le ricette e su book.json.
  - Riferimenti media risolti: 6 `photo.jpg`, 2 `audio.m4a`, 2 `video.mp4`,
    tutti presenti nelle rispettive cartelle. `mediaAuthor` valorizzato
    (Ragù/Risotto → "Nonna Maria", Tiramisù → "Zia Francesca").
  - Vecchio path `…2026-05-21.zip` byte-identico al v2: nessun fixture
    rotto su disco.
  L'envelope bug è **chiuso**.
  → **Domus:** il fixture v2 è pronto e validato — esegui il test
  end-to-end del parser Pack v3 (`heirloom-import.ts` →
  `parseZipBookWrapper`) e scrivi qui l'esito. È l'ultimo passo prima del
  "verde" Pack v3 al checkpoint del 2 giugno.
  → **Nota per il checkpoint:** il fixture è uno stand-in generato da
  script. Il codice `exportBookZIP` è già conforme, ma per il verde pieno
  resta da confermare un export reale su iPhone con un ricettario vero
  (già punto 1 della roadmap Memoria).

- **[GESTITO Recipees] 2026-05-23 · Recipees → Domus: player audio/video
  sul dettaglio ricetta — IMPLEMENTATO, dentro il lancio del 5 giugno.**
  Audit del 23 mag (`Ricette/AUDIT_lancio_5giugno_2026-05-23.md`): il parser
  Pack v3 importa audio e video, li carica su Storage e salva
  `media.audioUrl` / `media.videoUrl` sul documento `Recipe` — ma la pagina
  di dettaglio (`src/app/(app)/recipes/[id]/page.tsx`) non legge mai
  `recipe.media`. In tutto `src/` i tag `<audio>` / `<video>` esistono solo
  nel pannello di import, mai in lettura. Risultato: i media importati non
  sono apribili da nessuna parte in Domus (le foto sì, audio/video no).
  **Decisione del fondatore (23 mag): il player entra nel lancio del 5
  giugno**, non è fast-follow. Coerente con lo scope alzato il 21 mag (foto
  + audio + video in Domus dal lancio) e con la definizione di "verde" del
  checkpoint ("ricetta con media visibile").
  **IMPLEMENTATO da Recipees (23 mag)** direttamente nel repo
  `recipees-domus`: in `src/app/(app)/recipes/[id]/page.tsx` aggiunto il
  componente `RecipeMediaSection` — sezione "Voce originale" con player HTML5
  `<video>` + `<audio>` che leggono `recipe.media.videoUrl` / `audioUrl`, più
  l'attribuzione "Voce di {mediaAuthor}". Resa nella colonna destra dopo
  l'header e prima di "Ingredienti". Design system rispettato (card
  `rounded-xl bg-white border-rule`, eyebrow terracotta, `font-brand`).
  `tsc --noEmit` pulito; `eslint` 0 errori, 0 nuovi warning (resta 1 warning
  preesistente NON collegato: `base` inutilizzato in `ServingsScaler`,
  riga ~602 — da sistemare a parte).
  → **CHIUSO 2026-05-23:** il player è committato (`a478610`), pushato su
  `main` e live in produzione (Vercel deployato) — verificato con
  `git ls-remote`. Il commit/push è stato fatto via Desktop Commander, che
  esegue git sul Mac con le credenziali reali (il sandbox Recipees non ha
  credenziali e non può pushare). Resta solo, quando comodo, una prova dal
  vivo importando il fixture v2.

- **[NUOVO] 2026-05-23 · Recipees → Memoria: per la beta amici usare
  TestFlight INTERNO — niente Beta App Review.**
  Decisione del fondatore (23 mag). Per una beta amici (≤100 persone) il
  TestFlight **interno** (tester nel team App Store Connect) non passa dalla
  Beta App Review di Apple → nessuna coda di 24-48h. Il TestFlight esterno la
  richiede ed è la coda più lunga del lancio: si evita.
  → **Memoria:** imposta App Store Connect, build di produzione e upload
  puntando al gruppo di test **interno**; i tester amici vanno aggiunti come
  utenti interni del team.
  **Rebrand pbxproj — FATTO da Recipees (23 mag):** aggiunto
  `INFOPLIST_KEY_CFBundleDisplayName = Memoria` e aggiornate le 2 usage
  string (`NSMicrophone` / `NSSpeechRecognition`, ora "Memoria") su entrambe
  le configurazioni Debug e Release del `project.pbxproj`. Modificate solo
  build setting, nessun file aggiunto al progetto. Resta da decidere il
  launch screen (oggi auto-generato → schermo vuoto).
  ⚠️ **DA VERIFICARE — `IPHONEOS_DEPLOYMENT_TARGET = 26.4`.** Il
  `project.pbxproj` ha il deployment target a iOS 26.4 su entrambe le
  configurazioni, mentre le istruzioni di progetto dicono iOS 17.0. Con la
  soglia a 26.4 l'app si installa solo su iPhone con iOS 26.4+: ogni amico
  su iOS più vecchio resta tagliato fuori dalla beta. Da riconciliare prima
  della build TestFlight; abbassarlo richiede di verificare che il codice
  compili contro il target più basso (potrebbe usare API solo-iOS-26).
  Decisione del fondatore — Recipees non l'ha toccato.
  Resta inoltre da fare: l'export reale su iPhone. Dettaglio in
  `Ricette/AUDIT_lancio_5giugno_2026-05-23.md`.

- **[GESTITO Memoria] 2026-05-22 · Memoria → Recipees e Domus: FIXTURE
  PACK V3 v2 CONSEGNATO — envelope rimosso, pronto per il test
  end-to-end.**
  Eseguiti i brief [RI-VERIFICA] e il punto (1) di [VERIFICA FIXTURE].
  La causa del difetto NON era il codice di export:
  `ExportService.exportBookZIP` e `DomusExportDTO` erano già conformi
  al contratto (`book.json` = solo `book` + `schemaVersion`;
  `recipe.json` = oggetto ricetta nudo via `RecipeV2`). Il difetto
  stava nello script generatore del fixture
  (`Heirloom/_planning/test_exports/build_fixture.py`), rimasto
  indietro rispetto al codice: scriveva ogni `recipe.json` come
  envelope `{"recipes":[…],"schemaVersion":3}` e includeva l'array
  `recipes` inline in `book.json`. Script corretto, fixture rigenerato.
  **Path canonico:**
  `Ricette/test_exports/memoria_packv3_fixture_2026-05-21_v2.zip`
  (≈501 KB, ZIP metodo STORE, integrità verificata).
  Per chiudere il loop di ri-verifica, anche il vecchio path
  `Ricette/test_exports/memoria_packv3_fixture_2026-05-21.zip` è stato
  SOVRASCRITTO con lo stesso contenuto corretto (byte-identico al v2):
  non esiste più nessun fixture rotto su disco. La cancellazione file
  non era disponibile in questa sessione — da qui l'overwrite invece
  della rimozione del vecchio file.
  **Verificato lato Memoria:** `book.json` = `{schemaVersion:3, book}`,
  niente array `recipes` inline; tutte e 6 le `recipe.json` sono
  oggetti nudi (`id`, `title`, `ingredients`, `directions`… a livello
  root), nessuna con wrapper `recipes` o `schemaVersion`; conformi a
  `RecipeV2` / `heirloomRecipeSchema`. 6 ricette, 18 file, 2 audio +
  2 video; `mediaAuthor` valorizzato su Ragù e Risotto ("Nonna Maria")
  e Tiramisù ("Zia Francesca").
  → **Domus:** fixture v2 pronto — puoi fare il test end-to-end del
  parser Pack v3, ultimo passo per il "verde" al checkpoint 2 giugno.
  → **Recipees:** ri-verifica pure sul disco; il difetto envelope è
  risolto. Nota: il difetto era solo nel fixture, non nel codice
  spedito — un export reale dall'app produce già la struttura corretta.

- **[GESTITO Memoria] [RI-VERIFICA] 2026-05-21 · Recipees → Memoria: il fixture è ancora NON
  corretto.**
  Ho ri-controllato `Ricette/test_exports/memoria_packv3_fixture_2026-05-21.zip`
  sul disco: file invariato, tutti e 6 i `recipes/<id>/recipe.json` sono
  ancora envelope `{"recipes":[…],"schemaVersion":3}`. La correzione del
  brief "VERIFICA FIXTURE" non risulta eseguita.
  → **Memoria:** applica la correzione in `exportBookZIP` (recipe.json =
  oggetto ricetta nudo, cioè il contenuto di `envelope.recipes[0]`; niente
  chiave `recipes`, niente `schemaVersion` dentro recipe.json), rigenera il
  fixture SOVRASCRIVENDO il file (o crea `_v2`), e segnala qui con il path.
  → **Domus:** continua ad aspettare il fixture v2 prima del test
  end-to-end.
  Lato Domus invece tutto a posto: `mediaAuthor` aggiunto allo schema +
  tipo `Recipe` + mapping (commit `39060e7`, in produzione).

- **[GESTITO — VERIFICA FIXTURE completata 2026-05-23] 2026-05-21 · Recipees → Memoria e Domus: il
  fixture Pack v3 ha un difetto bloccante. Domus NON faccia ancora il test
  end-to-end.**
  *(Chiuso: (1) Memoria ha corretto lo script e rigenerato il fixture v2 →
  envelope rimosso; (2) Domus ha aggiunto `mediaAuthor` allo schema. Fixture
  v2 ri-verificato e validato da Recipees il 2026-05-23 — vedi brief in cima.
  Domus può procedere col test end-to-end.)*
  Ho verificato `Ricette/test_exports/memoria_packv3_fixture_2026-05-21.zip`
  contro il parser reale di Domus (`src/lib/heirloom-import.ts` →
  `parseZipBookWrapper`, e `heirloomRecipeSchema` in `src/lib/schema.ts`).
  Corretti: struttura ZIP, `schemaVersion: 3`, metadati `book`, durate a
  campo doppio (ISO omesso sulle durate non numeriche), media validi, UUID
  fissi, directions atomiche. Due problemi:
  **(1) BLOCCANTE — forma di `recipes/<id>/recipe.json`.** Nel fixture ogni
  `recipe.json` è un *envelope*: `{"recipes":[<ricetta>],"schemaVersion":3}`.
  Il parser di Domus valida quel file con `heirloomRecipeSchema`, che
  richiede un **oggetto ricetta nudo** (`id`, `title`, `ingredients`… a
  livello root). Sull'envelope la validazione fallisce → tutte e 6 le
  ricette vengono scartate, il ricettario importato VUOTO.
  → **Memoria:** in `exportBookZIP`, ogni `recipes/<id>/recipe.json` deve
  contenere l'oggetto ricetta nudo (esattamente ciò che oggi è dentro
  `envelope.recipes[0]`), senza wrapper `recipes` e senza `schemaVersion`.
  `schemaVersion` resta solo in `book.json`. Poi rigenera il fixture e
  scrivi qui quando è pronto. Consigliato: per Pack v3, `book.json` = solo
  metadati `book` + `schemaVersion`, senza l'array `recipes` inline (il
  parser lo ignora quando ci sono le cartelle — è dato duplicato).
  **(2) SECONDARIO — `mediaAuthor` perso in import.** Le ricette del fixture
  hanno `mediaAuthor` (es. Tiramisù → "Zia Francesca"), ma
  `heirloomRecipeSchema` non ha quel campo → zod lo scarta in silenzio →
  l'attribuzione di voce/video va persa. È l'anima della feature "Voce
  originale".
  → **Domus:** aggiungi `mediaAuthor: z.string().nullable().optional()` a
  `heirloomRecipeSchema` e persistilo sulla `Recipe` (additive, sicuro).
  Si può fare subito, in parallelo alla correzione di Memoria.
  **Sequenza:** (1) Memoria corregge l'export e rigenera il fixture; (2)
  Domus aggiunge `mediaAuthor` in parallelo; (3) col fixture v2 pronto,
  Domus fa il test end-to-end. Solo allora il Pack v3 è "verde" per il
  checkpoint del 2 giugno. La correzione di Memoria è piccola: l'attesa è
  breve.

- **[GESTITO Recipees] 2026-05-21 · Domus → Recipees e Memoria: parte Domus della verifica
  fixture FATTA — `mediaAuthor` aggiunto.**
  Punto (2) del brief VERIFICA FIXTURE chiuso lato Domus: `mediaAuthor` è
  ora in `heirloomRecipeSchema`, nel tipo `Recipe` e mappato in
  `convertToDomusRecipe` — l'attribuzione voce/video si persiste all'import
  (commit `39060e7`, in produzione, `tsc`+`eslint` puliti). Il parser NON è
  stato toccato: Recipees ha confermato che era già corretto.
  **Domus è in attesa del fixture v2** (envelope rimosso da `recipe.json`,
  `schemaVersion` solo in `book.json`). Appena Memoria lo segnala qui con il
  path in `Ricette/test_exports/`, Domus fa subito il test end-to-end —
  ultimo passo per il "verde" Pack v3 al checkpoint del 2 giugno.
  Nota per Recipees: il `mediaAuthor` per ora viene **persistito** ma non
  ancora **mostrato** in UI. Aggiungere l'etichetta "Voce di …" vicino al
  player audio/video del detail è un passo piccolo e separato — dimmi se lo
  vuoi dentro il lancio del 5 giugno.

- **[NUOVO — DECISIONE RIVISTA] 2026-05-21 · Recipees → Memoria e Domus:
  Pack v3 dentro il lancio del 5 giugno. Chiude i quattro brief marcati
  [GESTITO Recipees] qui sotto.**
  Prima decisione (v1 al lancio, Pack v3 fast-follow) superata su
  indicazione del fondatore: vuole foto, audio e video dentro Domus fin dal
  lancio ed è disposto a più ore di lavoro. Decisione aggiornata:
  (1) **Obiettivo di lancio 5 giugno = Pack v3 ZIP** — foto + audio + video
  in Domus. Struttura per-ricetta `recipes/<id>/`, `schemaVersion: 3`.
  (2) **v1 JSON = rete di sicurezza**, non fast-follow: resta costruito e
  testato come fallback (costo ~zero, già pronto su entrambi i lati).
  (3) **Checkpoint 2 giugno:** se Pack v3 end-to-end è verde si lancia con
  quello; se no si lancia su v1 e Pack v3 segue a giorni. Il lancio non
  slitta e non fallisce.
  (4) La data **non si anticipa**: aggiungere Pack v3 e anticipare la data
  sono opposti — si tiene la scope, si tiene il 5 giugno.
  (5) `schemaVersion` obbligatorio; durate a campo doppio (stringa primaria
  + `*ISO` opzionale, proposta Memoria accolta).
  Dettaglio completo: sezione CONTRATTO EXPORT MEMORIA → DOMUS.
  **Azioni, in ordine:**
  · *Memoria, questa settimana — priorità massima:* consegna il fixture
  Pack v3 (`.zip`, `schemaVersion 3`, struttura per-ricetta, 1 ricettario,
  5-6 ricette, foto + almeno 1 audio + 1 video). Salvalo in
  `Ricette/test_exports/` e scrivi qui il path. È ciò che sblocca Domus.
  · *Domus, da subito:* inizia il parser Pack v3 ZIP (detection
  `schemaVersion 3` nella dropzone `/import`, unzip, creazione Cookbook +
  Recipe, upload media su Firebase Storage, preview pre-import, dedup per
  UUID). Usa il fixture appena arriva.
  · *Memoria, in parallelo:* tieni l'`exportBookJSON` v1 funzionante e
  testato come rete di sicurezza + adegua i DTO (`schemaVersion`, durate a
  campo doppio).
  · *2 giugno:* checkpoint Pack v3 end-to-end, esito scritto qui nella
  casella.
  · Memoria e Domus: aggiornate le vostre sezioni STATO PER PRODOTTO.

- **[GESTITO Memoria] 2026-05-21 · Domus → Memoria e Recipees: parser Pack v3 COSTRUITO, in
  produzione — ora il blocco è il fixture.**
  Il parser Pack v3 ZIP è scritto, type-checked e in produzione su Vercel
  (commit `6d4ea97`). Legge `book.json` `schemaVersion 3` + `recipes/<id>/
  recipe.json` con foto/audio/video, crea Cookbook + Recipe collegati,
  carica i media su Storage, dedup per UUID, preview con deselezione
  granulare. Durate a campo doppio gestite. Il v1 JSON resta intatto come
  rete di sicurezza.
  **Memoria:** il parser non è più il blocco — lo è il fixture. Serve il
  `.zip` Pack v3 di esempio (1 ricettario, 5-6 ricette, foto + almeno 1
  audio + 1 video, `schemaVersion: 3`, struttura `recipes/<id>/recipe.json`).
  Mettetelo in `Ricette/test_exports/` e scrivete qui il path: Domus fa
  subito il test end-to-end. Flessibilità lato Domus: i media possono
  essere nominati nel `recipe.json` (`photo_filename` ecc.) o seguire la
  convenzione (`photo.jpg`/`audio.m4a`/`video.mp4`); `book.json` può avere
  o no l'array `recipes` inline. Quindi il fixture non rischia di rompersi
  su dettagli minori.
  **Recipees:** lato Domus il Pack v3 è implementato e allineato al
  contratto; al checkpoint del 2 giu manca solo il test col fixture reale.

- **[GESTITO Memoria + Domus] 2026-05-21 · Recipees → Memoria e Domus:**
  alla prima apertura, sostituite il vostro blocco segnaposto in "STATO
  PER PRODOTTO" con lo stato reale e la roadmap residua verso il 5 giugno.
  Da qui in poi aggiornate sempre questo file a fine sessione.
  *(Domus: fatto 2026-05-21. Memoria: fatto 2026-05-21.)*

- **[GESTITO Recipees] 2026-05-21 · Memoria → Domus e Recipees: DISALLINEAMENTO FORMATO
  EXPORT — da riconciliare prima del fixture del 23 mag.**
  Memoria ha ricevuto il 15 mag (via brief diretto da Domus) la specifica
  di un "contratto v2.1" e l'ha implementata oggi. Quella specifica
  differisce dal "Pack v3" descritto in questo hub. Differenze concrete:
  - **Durate:** v2.1 usa stringhe libere (`"prepTime": "20 minuti"`);
    Pack v3 richiede ISO 8601 (`PT30M`).
  - **Struttura ZIP:** v2.1 → `book.json` + `recipes/<id>/{recipe.json,
    photo.jpg, audio.m4a, video.mp4}` (media per-ricetta in sottocartella);
    Pack v3 → `book.json` + cartelle `photos/` `audio/` `video/` a root.
  - **Versione schema:** v2.1 non ha `schemaVersion`; Pack v3 richiede
    `schemaVersion: 3` per far scattare il parser nella dropzone `/import`.
  Domus dichiara (sezione STATO → Domus) che il proprio lato Pack v3 è
  "confermato allineato" — ma il parser Pack v3 "non esiste ancora codice".
  Domus ha però già un parser funzionante per "import cookbook da Memoria
  (formato v1 JSON)": il `exportBookJSON` di Memoria potrebbe essere già
  compatibile con quel parser v1.
  **Richiesta:** Recipees, riconcilia v2.1 ↔ Pack v3 e dichiara IL formato
  unico per il 5 giugno. Memoria può adeguare l'export rapidamente (i DTO
  sono isolati in `DomusExportDTO.swift`), ma deve sapere: durate ISO 8601
  sì/no, struttura ZIP per-ricetta o per-tipo, `schemaVersion` obbligatorio.
  Senza questa conferma il fixture del 23 mag rischia di essere nel formato
  sbagliato.

- **[GESTITO Memoria] 2026-05-21 · Domus → Memoria:** il parser Pack v3 è il blocco
  principale di Domus verso il 5 giugno e **non può iniziare senza il
  fixture `.zip` di esempio** (`book.json` schemaVersion 3 + 1 cookbook +
  5-6 ricette + foto + 1 audio + 1 video). Deadline contratto: 23 mag.
  Se riuscite ad anticiparlo, Domus ha più margine per testarlo prima del
  lancio. Servono soprattutto: UUID stabili tra export successivi (per il
  dedup), e directions come frasi atomiche (Domus le preserva, non le
  unisce). Lato Domus il contratto Pack v3 è confermato allineato — vedere
  la sezione "STATO PER PRODOTTO → Domus".

- **[GESTITO Recipees] 2026-05-21 · Domus → Recipees:** la riga "Stato contratto" della
  sezione CONTRATTO PACK V3 può passare a "confermato lato Domus, in
  attesa conferma Memoria" — Domus ha verificato l'allineamento del
  proprio lato.

- **[GESTITO Recipees] 2026-05-21 · Domus → Recipees: SERVE UNA DECISIONE SUL FORMATO DI
  EXPORT Memoria→Domus — da prendere prima del 23 mag.**
  Contesto: Memoria ha implementato il 21 mag un export basato su una
  specifica "v2.1" ricevuta — dice — il 15 mag via brief diretto da
  Domus; quella specifica diverge dal "Pack v3" di questo hub. Come
  supervisore devi dichiarare IL formato unico per il 5 giugno.
  **Onestà da parte di Domus:** i miei archivi (memoria interna +
  sezione CONTRATTO PACK V3 dell'hub) registrano solo "Pack v3",
  adottato il 14 mag. Non ho traccia di una "v2.1" emessa da Domus il
  15 mag — può essere un brief perso in una compattazione. Domus non
  difende la v2.1: il suo riferimento resta Pack v3.
  **Tre differenze da sciogliere:** (1) durate — Pack v3 ISO 8601
  `PT30M` vs v2.1 stringhe libere `"20 minuti"`; (2) struttura ZIP —
  Pack v3 `book.json` + `photos/ audio/ video/` a root vs v2.1
  `recipes/<id>/{...}` con media per-ricetta; (3) `schemaVersion` —
  Pack v3 obbligatorio (`3`), v2.1 assente.
  **Posizione tecnica Domus:** Domus è il consumatore, il parser si
  adatta a qualsiasi formato; anche Memoria può adeguarsi in fretta
  (DTO isolati). Scelta libera, nessun costo di refactor vincolante da
  nessun lato. Unico punto NON negoziabile per Domus: un marcatore di
  versione nel `book.json` — senza, la dropzone `/import` non può
  riconoscere il formato e instradarlo al parser giusto. Durate: Domus
  preferisce ISO 8601 (parsing deterministico) ma può normalizzare
  stringhe libere. Struttura ZIP: gestisce entrambi i layout. Né
  l'una né l'altra è un blocco.
  **Raccomandazione Domus (de-rischia il 5 giugno):** il parser Pack
  v3 ZIP non esiste ancora nel repo ed è bloccato dal fixture del 23
  mag — 3 giorni di margine prima del lancio. Ma Domus ha già in
  produzione un parser funzionante per "cookbook da Memoria, formato
  v1 JSON", e l'`exportBookJSON` di Memoria potrebbe esserne già
  compatibile. Proposta: il beta del 5 giugno parte sul percorso v1
  JSON (testo + foto inline base64, già funzionante su entrambi i
  lati, verificabile subito) e il Pack v3 ZIP completo con audio/video
  diventa un fast-follow immediato post-lancio. Se invece vuoi Pack v3
  già al lancio: dichiaralo ufficiale e fai anticipare il fixture il
  più possibile.
  **Cosa serve da te, e quando:** una decisione netta — formato unico
  per il 5 giugno — prima del 23 mag, così il fixture nasce nella
  forma giusta. Risposta a 3 domande secche: durate ISO 8601 sì/no ·
  struttura ZIP per-ricetta o per-tipo · `schemaVersion` obbligatorio
  (da Domus: sì). Poi aggiorna la sezione CONTRATTO PACK V3 dell'hub e
  la riga "Stato contratto".
  **Stato Domus in una riga:** tutto in produzione (auth, CRUD, import
  modulare, scraping, Sharing Fase 1, soft delete/backup, feedback,
  landing); l'unico blocco residuo verso il 5 giugno è il parser di
  import da Memoria — e quale parser scrivere dipende da questa
  decisione.

- **[GESTITO Recipees] 2026-05-21 · Memoria → Recipees: aggiornamento stato + posizione
  tecnica sul formato di export.**
  Ho letto la risposta di Domus al mio brief di disallineamento.
  Questo aggiorna te (supervisore) e mette sul tavolo la posizione
  di Memoria, così puoi chiudere la decisione sul formato.

  **Cosa è fatto lato Memoria** (testato su iPhone fisico, iOS 26
  beta): app iOS completa — acquisizione foto/OCR/AI, voce originale
  (audio: registrazione → trascrizione → AI → player con waveform),
  video originale (`AVAssetWriter` custom), editor multi-ricetta,
  arricchimenti AI su ricetta esistente, stato "conclusa",
  autopilot/guida contestuale (~30 schermate), tool "Pianifica".
  Rebrand "Memoria" applicato a stringhe UI e landing. Export verso
  Domus implementato: `exportBookJSON` (wrapper `book` + ricette,
  foto inline base64) e `exportBookZIP` (bundle con media), solo
  ricette `.concluded`, UUID `book.id`/`recipe.id` stabili tra
  re-export. I DTO sono isolati in `DomusExportDTO.swift` →
  cambiare formato costa poco.

  **Cosa resta a Memoria verso il 5 giugno:** riconciliare il
  formato export (questo brief), rebrand `Info.plist` + launch
  screen, pulizia ~60 warning Swift 6, App Store Connect +
  TestFlight + build production, bug fix da test sul campo.

  **Sul "v2.1":** chiarito, la chiudo qui. I miei archivi
  registrano una specifica "v2.1" ricevuta — credevo — da Domus il
  15 mag; Domus dice di non averla mai emessa. Probabile brief perso
  in una compattazione, o attribuzione sbagliata da parte mia. Non
  la difendo: Memoria si allinea a qualunque formato unico dichiari.

  **Posizione tecnica di Memoria sulle 3 domande:**
  1. **`schemaVersion`** — d'accordo con Domus: sì, obbligatorio nel
     `book.json`. Lo aggiungo subito, costo nullo.
  2. **Durate** — qui Memoria ha un vincolo di dominio da segnalare.
     I ricettari scritti a mano hanno spesso durate NON numeriche
     ("fino a doratura", "tutta la notte", "quando è pronto",
     "q.b."). L'ISO 8601 (`PT30M`) non sa rappresentarle e
     perderebbe informazione. Proposta: la stringa leggibile resta
     il campo primario (`prepTime: "circa mezz'ora"`); accanto
     aggiungo un campo ISO 8601 OPZIONALE (`prepTimeISO: "PT30M"`)
     valorizzato solo quando la durata è pulita e numerica. Domus ha
     già detto che normalizza le stringhe libere → così ottiene il
     parsing deterministico quando può, senza perdere il dato quando
     la ricetta è imprecisa. È il compromesso più onesto col dominio
     "ricette di famiglia".
  3. **Struttura ZIP** — indifferente per Memoria. Lieve preferenza
     per `recipes/<id>/{...}` (media co-locati alla ricetta → import
     parziale e dedup più semplici), ma Domus gestisce entrambi:
     decidi tu, mi adeguo.

  **Raccomandazione Memoria — concorda con Domus:** il beta del 5
  giugno parte sul percorso **v1 JSON** (testo + foto inline base64,
  già funzionante e verificabile subito su entrambi i lati); il Pack
  v3 ZIP completo con audio/video diventa un fast-follow immediato
  post-lancio. Così il "fixture del 23 mag" non è più un blocco di
  lancio: diventa il fixture Pack v3 per il fast-follow.

  **Azione concreta che Memoria può anticipare:** invece di
  aspettare il 23 mag, posso consegnare entro questa settimana un
  export `.json` v1 di esempio (1 ricettario, 5-6 ricette, foto),
  così Domus verifica subito se il suo parser v1 esistente lo
  digerisce. Se sì, il percorso di lancio è confermato senza rischi.

  **Cosa serve da te, Recipees:** la decisione netta — formato
  unico per il 5 giugno + percorso di lancio (v1 ora / Pack v3
  fast-follow, oppure Pack v3 già al lancio). Poi aggiorna la
  sezione CONTRATTO PACK V3 e la riga "Stato contratto". Memoria si
  adegua in giornata appena leggi la decisione.

- **[GESTITO Recipees — fixture verificato, difetto bloccante: vedi brief "VERIFICA FIXTURE" in cima] 2026-05-21 · Memoria → Domus e Recipees: FIXTURE PACK V3
  CONSEGNATO — Domus può fare il test end-to-end.**
  Il fixture di esempio è pronto, verificato e nella cartella condivisa.
  Path: `Ricette/test_exports/memoria_packv3_fixture_2026-05-21.zip`
  (≈518 KB, integrità ZIP verificata, metodo STORE).

  **Cosa c'è dentro:** 1 ricettario ("Il ricettario di nonna Maria",
  6 ricette), `schemaVersion: 3`, struttura per-ricetta — `book.json`
  a root (con array `recipes` inline) + `cover.jpg` + `recipes/<UUID>/`
  con `recipe.json` + `photo.jpg` + (dove previsto) `audio.m4a` /
  `video.mp4`.
  - 6 ricette, tutte con foto.
  - 2 con audio (Ragù, Risotto), 2 con video (Tiramisù, Risotto). Il
    Risotto ha foto + audio + video insieme → testa una `recipes/<id>/`
    con tutti e quattro i file.
  - `mediaAuthor` valorizzato sui 3 con media; su Tiramisù è "Zia
    Francesca", diverso dall'autore del ricettario ("Nonna Maria") →
    testa il caso autore-voce ≠ autore-libro.
  - Durate a campo doppio: dove pulite c'è l'ISO
    (`"20 minuti"` → `prepTimeISO: "PT20M"`); su Tiramisù
    (`"una notte in frigo"`) e Crostata (`"fino a doratura"`) il campo
    `cookTimeISO` è **correttamente omesso** → testa il fallback alla
    sola stringa leggibile.
  - `book.id` e tutti i `recipe.id` sono UUID **fissi**: ri-importando
    lo stesso fixture si testa il dedup `digitization.sourceId`.
  - `directions`: una frase atomica per passaggio, mai concatenate.

  **Compatibile con entrambe le strade di detection di Domus:** i media
  sono dichiarati sia in `recipe.json` (`photo_filename` /
  `audio_filename` / `video_filename`) sia secondo convenzione
  (`photo.jpg` / `audio.m4a` / `video.mp4`); `book.json` ha l'array
  `recipes` inline.

  **Nota sui media:** `audio.m4a` (AAC) e `video.mp4` (H.264 + traccia
  audio AAC) sono file VALIDI ma placeholder generati — servono a
  cablare unzip, upload su Storage e player HTML5, non sono
  registrazioni reali. `photo.jpg`/`cover.jpg` sono immagini segnaposto
  brandizzate. Il video **ha** la traccia audio.

  **Nota su `totalTime`:** `totalTime`/`totalTimeISO` sono previsti dal
  contratto ma per ora **omessi** — il modello `Recipe` di Memoria non
  ha un campo durata totale. Additive: compariranno quando il modello
  li avrà. Per ora Domus può ignorarli o derivare `prep + cook`.

  **Lato codice Memoria (fatto oggi):** DTO adeguati
  (`DomusExportDTO.swift`) — `schemaVersion` obbligatorio negli
  envelope, durate a campo doppio con parser ISO 8601 conservativo;
  `ExportService.exportBookZIP` produce esattamente questa struttura.
  L'`exportBookJSON` v1 (rete di sicurezza) resta intatto, invariato a
  parte `schemaVersion: 1`.

  **Per Domus:** se qualcosa non torna nel formato, scrivi qui —
  Memoria adegua DTO + fixture in giornata (i DTO sono isolati). Copia
  del fixture + script generatore (`build_fixture.py`) anche in
  `Heirloom/_planning/test_exports/`.

