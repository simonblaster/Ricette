> Aggiornata: 2026-06-20  ·  Fonti: RECIPEES_HUB.md, ROADMAP_*, CLAUDE.md, memory/*, script, repo git
> Stato live al 2026-06-20: ✅ recipees.app 200 · ✅ sito legacy 200 · ✅ tre repo con remote · Memoria su `feat/acquisizione-motore-unico`

# Soluzione: Recipees (ecosistema completo)

# 👤 Vista utente

## Cosa fa
Recipees è il tuo ecosistema per le ricette di famiglia, in tre gesti: **riscopri**
(Memoria, l'app iOS che digitalizza ricette da foto/voce/video/testo), **condividi**
(Domus, il ricettario di famiglia online su recipees.app), **tramanda** (Folio, il
libro stampato, da set 2026). Sotto, due strumenti "storici" ancora vivi: il **sito
ricettario** (Paprika → web) e l'**import ricette in Paprika**.

## A cosa ti serve
A non perdere il patrimonio di ricette di famiglia — quaderni a mano, voci di chi non
c'è più, ritagli — e a renderlo vivo: cercabile, condivisibile coi parenti, e infine
stampabile come oggetto da tramandare.

## Memorandum — comandi e Shortcut
| Per… | Si attiva con | Tipo | Stato |
|------|---------------|------|-------|
| Digitalizzare una ricetta (quaderno/foto/voce/video) | App **Memoria** (iOS) → FAB nel ricettario | app iOS | live (beta TestFlight) |
| Consultare/condividere il ricettario di famiglia | **recipees.app** (login) | web | live dal 14 mag |
| Esportare un ricettario Memoria → Domus | Memoria → Esporta (Pack v3 ZIP) → import su recipees.app | app+web | live |
| Vetrina/prevendita libro | **recipees.app/folio** | web | prevendita da set 2026 |
| Pubblicare il sito ricettario legacy | `python3 aggiorna_sito.py` + commit/push di `docs/` | comando | esiste |
| Importare/convertire ricette in Paprika | skill `/paprika-recipe-importer` | comando | esiste |

## Funzionalità in dettaglio

### Memoria — riscopri (app iOS, codename Heirloom)
- **Cosa fa**: acquisisce ricette da fotocamera (pagina singola/doppia/multipagina), import foto/PDF/file, **voce** e **video** (l'AI struttura), testo; OCR + strutturazione AI; editor multi-ricetta; player di voce/video originali.
- **Come si attiva**: apri l'app, entri in un ricettario, usi il FAB (Fotocamera/Foto/File/Audio/Video/Testo).
- **Passo per passo**: scegli la fonte → acquisisci → l'AI propone la ricetta strutturata → rivedi/correggi (per i quaderni a colonne riquadri con gli slider) → "Salva e concludi".
- **Cosa ottieni**: ricette strutturate sul telefono, esportabili verso Domus, con voce/video originali allegati.

### Domus — condividi (web, recipees.app)
- **Cosa fa**: ricettario di famiglia online; CRUD ricette/ricettari, ricerca con tag e filtro per ricettario, lista spesa aggregata con scaling, **Crea Menu** (menù per occasioni + stampa + segnaposto), condivisione e fork tra parenti, import da Memoria e da web.
- **Come si attiva**: login su recipees.app.
- **Passo per passo**: importi (da Memoria o web) o crei a mano → organizzi in ricettari → condividi via email → i parenti vedono/forkano → componi menù e liste della spesa.
- **Cosa ottieni**: il ricettario di famiglia vivo e condiviso, con voce/video riprodotti nel dettaglio ricetta.

### Folio — tramanda (libro stampato)
- **Cosa fa**: il libro di carta, tre formati (Tascabile/Classico/Deluxe).
- **Come si attiva**: vetrina su recipees.app/folio; prevendita da set 2026.
- **Passo per passo**: — (nessun flusso prodotto prima di set 2026).
- **Cosa ottieni**: l'oggetto fisico da tramandare.

### Sito ricettario (Paprika → GitHub Pages)
- **Cosa fa**: pubblica il ricettario "storico" (pizze/focacce/famiglia) come sito statico su https://simonblaster.github.io/Ricette/, partendo da Paprika 3.
- **Come si attiva**: `python3 aggiorna_sito.py` dalla root, poi `git add -A && git commit && git push`.
- **Passo per passo**: lo script genera `docs/recipes.js` + `docs/photo-uids.js` → push → GitHub Pages serve `docs/`.
- **Cosa ottieni**: il sito aggiornato (specchio del DB Paprika all'ultimo `aggiorna_sito`).

### Import ricette in Paprika
- **Cosa fa**: trasforma ricette grezze (testo/foto/URL) in ricette pulite in Paprika 3, con convenzioni coerenti (naming, scaling, parsing ingredienti, foto).
- **Come si attiva**: skill `/paprika-recipe-importer` (convenzioni in `memory/paprika_workflow.md`); per le pizze gli script dedicati (`genera_archivio_pizze.py`, `inserisci_varianti.py`).
- **Passo per passo**: fornisci la fonte → la skill applica le convenzioni → ottieni un `.paprikarecipes` importabile in Paprika.
- **Cosa ottieni**: ricetta pulita in Paprika, pronta per il sito.

## La catena causale
Acquisisci con Memoria → esporti (Pack v3) → importi su Domus → la ricetta vive online,
condivisibile e con voce/video → un domani diventa Folio. In parallelo, il binario
storico: importi/converti in Paprika → `aggiorna_sito.py` → il sito legacy si aggiorna.
Gli output non sono magie separate: sono la conseguenza di ciò che digitalizzi all'inizio
— per questo la qualità dell'acquisizione (Memoria) e dell'import (Paprika) determina tutto il resto.

# 🔧 Vista creator

## 1. In una frase
Tre prodotti (app iOS, web app, libro) + due pipeline legacy (sito statico, import Paprika), coordinati da una sessione-supervisore via un hub condiviso e un contratto di export stabile Memoria→Domus.

## 2. Il racconto
La sessione **Recipees** (root del monorepo `Ricette/`) non scrive codice di prodotto:
coordina, tiene coerenti hub e roadmap, fa da arbitro sui contratti e merge in `main` di
Domus. **Memoria** è un'app iOS Swift 6/SwiftUI (repo separato `simonblaster/Heirloom`);
**Domus** è Next.js 16 + Firebase (`recipees-domus/`, deploy Vercel su push a `main`);
**Folio** è copy di vetrina. Flusso di valore: Memoria digitalizza → esporta Pack v3 ZIP →
Domus lo importa (parser `heirloom-import.ts`) creando Cookbook+Recipe e caricando i media
su Firebase Storage. Le sessioni si parlano via `RECIPEES_HUB.md` (fonte unica di stato) e
la sua CASELLA BRIEF. A monte/lato, il **sito legacy**: `aggiorna_sito.py` traduce il DB
Paprika in JS statico dentro `docs/` (servito da GitHub Pages); l'**import Paprika** (skill
+ convenzioni in `memory/paprika_workflow.md`) produce i `.paprikarecipes`.

## 3. Trigger & comandi
| Trigger | Innesca |
|---------|---------|
| Sessione Claude da `Heirloom/`/`recipees-domus/`/root | Carica il `CLAUDE.md` di prodotto (guardia "chi sei?" nel root) |
| Push su `main` di `recipees-domus` | Deploy automatico Vercel (~2 min) |
| Merge `feat/*`/`fix/*` Domus → `main` | Lo fa la sessione Recipees |
| Export da Memoria | Pack v3 ZIP per import in Domus |
| `python3 aggiorna_sito.py` + push `docs/` | Ripubblica il sito legacy |
| `/paprika-recipe-importer` | Converte una ricetta grezza → `.paprikarecipes` |

## 4. Schedule (job)
— (nessun job launchd/cron locale; Domus ha un backup Firestore giornaliero lato Firebase, retention 14gg)

## 5. Output & dove finisce
recipees.app (Domus, Vercel) · TestFlight interno (Memoria) · ZIP Pack v3 (export) ·
GitHub Pages legacy `simonblaster.github.io/Ricette/` · recipees.app/folio (vetrina) ·
`.paprikarecipes` → Paprika 3.

## 6. Dati & file di stato
`RECIPEES_HUB.md` · `ROADMAP_bug.md` · `ROADMAP_funzionalita.md` · `HUB_archivio.md` · `SPEC_*.md` ·
`test_exports/` (fixture Pack v3) · Firestore `recipees-domus` (Frankfurt eur3, dato utente, soft-delete) ·
Memoria `books.json` su device · sito: `docs/recipes.js`+`docs/photo-uids.js`, `categorie_tracciate.json` ·
import: `*.paprikarecipes`, `MacGourmet.mgdb`, `memory/paprika_workflow.md`.

## 7. Integrazioni & credenziali
- **GitHub** (SSH): `simonblaster/Ricette` (monorepo coord+Domus+docs+sito), `simonblaster/Heirloom` (privato, app iOS).
- **Vercel**: deploy Domus da `main` (env Firebase per Production+Development, **non** Preview).
- **Firebase** (`recipees-domus`): Auth/Firestore/Storage + backup giornaliero.
- **Anthropic API**: strutturazione AI (Memoria via `Config.plist` gitignorato; Domus via env).
- **Resend**: email inviti Domus.
- iCloud Drive (source di lavoro sito) · Paprika 3 (app macOS) — nessun token.

## 8. Stato attuale
- **Domus**: live su recipees.app dal 14 mag, backlog bug a zero; Crea Menu, lista spesa aggregata, ricerca rifinita in produzione.
- **Memoria**: build verde, fix data-loss confermato; **acquisizione motore unico** implementata su branch `feat/acquisizione-motore-unico` (editor completato; **convergenza 3-modalità differita post-lancio**).
- **Folio**: nessun lavoro prima di set 2026.
- **Sito legacy** + **import Paprika**: live e stabili (binario storico, manutenzione on-demand).
- Contratto Pack v3: stabile, verde sul fixture (141/141).

## 9. Runbook — "come faccio a…"
- **Coordinare**: leggi `RECIPEES_HUB.md` per intero a inizio sessione; aggiorna "Ultimo aggiornamento" a fine.
- **Mergiare un branch Domus**: `tsc`+`eslint`, conferma a vista se UI, fast-forward/merge su `main`, push.
- **Far partire una sessione prodotto**: `cd ~/Documents/Claude/Projects/Heirloom` (Memoria) o `.../Ricette/recipees-domus` (Domus), poi `claude`.
- **Pubblicare il sito**: `python3 aggiorna_sito.py` → commit/push `docs/`.
- **Importare una ricetta in Paprika**: `/paprika-recipe-importer`.
- **Aggiornare/pubblicare questa scheda**: `/scheda aggiorna`, poi `python3 ~/.claude/skills/scheda/scripts/render_briefs.py --project "Recipees" --accent orange`.

## 10. Troubleshooting
| Sintomo | Causa probabile | Fix |
|---------|-----------------|-----|
| Codice Memoria "non c'è" nel monorepo | il vero repo è `~/Documents/Claude/Projects/Heirloom/` (separato) | usa quello, non il mirror `Ricette/Heirloom/` |
| Preview Vercel Domus fallisce build | env Firebase non impostate per Preview | testa in locale `npm run dev` o dopo merge in `main` |
| Due sessioni Domus in conflitto su git | commit paralleli sullo stesso `main` | worktree `feat/*`/`fix/*`, merge fatto da Recipees |
| Sito non aggiornato dopo push | Pages non ha ribuildato o `docs/` non committato | attendi 1-2 min; verifica `git status` di `docs/` |
| Dati Paprika vecchi nel sito | DB letto con WAL non checkpointato | copia sqlite+wal+shm, checkpoint, rigenera |
| Scrittura iCloud fallita ("Resource deadlock") | `cp` da bash verso iCloud | usa i file-tool Read/Edit/Write |

## 11. Stato live (2026-06-20)
- ✅ **recipees.app** → HTTP 200 · ✅ **GitHub Pages legacy** → HTTP 200 · ✅ **docs/** completo (index.html, recipes.js, photo-uids.js).
- ✅ **Repo**: Ricette (`0d17c37`), Heirloom (`22909aa`, branch `feat/acquisizione-motore-unico`), recipees-domus (`98d54f6`) — tutti con remote.
- ✅ Skill `paprika-recipe-importer.skill` + `MacGourmet.mgdb` presenti.
- ⚠️ Sezioni STATO-prodotto dell'hub aggiornate al 30 mag (gli "Ultimo aggiornamento" in testa arrivano al 6 giu).
