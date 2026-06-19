> Aggiornata: 2026-06-20  ·  Fonti: RECIPEES_HUB.md, ROADMAP_*, CLAUDE.md, repo git (Ricette/Heirloom/recipees-domus)
> Stato live al 2026-06-20: ✅ recipees.app 200 · ✅ tre repo con remote su GitHub · Memoria su branch `feat/acquisizione-motore-unico`

# Soluzione: Ecosistema Recipees (Memoria · Domus · Folio)

# 👤 Vista utente

## Cosa fa
Recipees è il tuo ecosistema per le ricette di famiglia, in tre gesti: **riscopri**
(Memoria, l'app iOS che digitalizza ricette da foto/voce/video/testo), **condividi**
(Domus, il ricettario di famiglia online su recipees.app), **tramanda** (Folio, il
libro stampato, da settembre). I tre prodotti non sono scollegati: una ricetta
acquisita con Memoria può finire su Domus e, un giorno, dentro Folio.

## A cosa ti serve
A non perdere il patrimonio di ricette di famiglia — quaderni scritti a mano, voci
di chi non c'è più, ritagli — e a renderlo vivo: cercabile, condivisibile con i
parenti, e infine stampabile come oggetto da tramandare.

## Memorandum — comandi e Shortcut
Questo NON è un sistema con comandi tuoi: si lavora dentro le app. La tabella sotto
è la mappa di "dove si fa cosa".

| Per… | Si attiva con | Tipo | Stato |
|------|---------------|------|-------|
| Digitalizzare una ricetta da quaderno/foto/voce/video | App **Memoria** (iOS) → FAB nel ricettario | app iOS | live (beta TestFlight) |
| Consultare/condividere il ricettario di famiglia | **recipees.app** (web, login) | web | live dal 14 mag |
| Esportare un ricettario da Memoria verso Domus | Memoria → Esporta (Pack v3 ZIP) → import su recipees.app | app+web | live |
| Acquistare/prevedere il libro stampato | **recipees.app/folio** | web (vetrina) | prevendita da set 2026 |

## Funzionalità in dettaglio

### Memoria — riscopri (app iOS, codename Heirloom)
- **Cosa fa**: acquisisce ricette da fotocamera (pagina singola/doppia/multipagina), import foto/PDF/file, **voce** (registri e l'AI struttura), **video**, testo; OCR + strutturazione AI; editor multi-ricetta; player immersivo per voce/video originali.
- **Come si attiva**: apri l'app, entri in un ricettario, usi il FAB (Fotocamera/Foto/File/Audio/Video/Testo).
- **Passo per passo**: scegli la fonte → acquisisci → l'AI propone la ricetta strutturata → rivedi/correggi → "Salva e concludi". Per i quaderni a colonne usi gli slider per riquadrare ricetta e foto.
- **Cosa ottieni**: ricette strutturate sul telefono, esportabili verso Domus, con la voce/video originali allegati.

### Domus — condividi (web, recipees.app)
- **Cosa fa**: ricettario di famiglia online; CRUD ricette/ricettari, ricerca con tag e filtro per ricettario, lista della spesa aggregata con scaling, **Crea Menu** (menù per occasioni + stampa + segnaposto), condivisione e fork tra parenti, import da Memoria e da web.
- **Come si attiva**: login su recipees.app.
- **Passo per passo**: importi (da Memoria o web) o crei a mano → organizzi in ricettari → condividi via email → i parenti vedono/forkano → componi menù e liste della spesa.
- **Cosa ottieni**: il ricettario di famiglia vivo e condiviso, con voce/video originali riprodotti nel dettaglio ricetta.

### Folio — tramanda (libro stampato)
- **Cosa fa**: il libro di carta, tre formati (Tascabile/Classico/Deluxe).
- **Come si attiva**: vetrina su recipees.app/folio; prevendita da settembre 2026.
- **Passo per passo**: — (nessun flusso prodotto prima di set 2026).
- **Cosa ottieni**: l'oggetto fisico da tramandare.

## La catena causale
Acquisisci con Memoria → esporti il ricettario (Pack v3) → lo importi su Domus → la
ricetta vive online, condivisibile e con voce/video → da ciò che è su Domus, un
domani, nasce Folio. Gli output non sono magie separate: sono la conseguenza di ciò
che digitalizzi all'inizio. È per questo che la qualità dell'acquisizione (Memoria)
determina tutto il resto.

# 🔧 Vista creator

## 1. In una frase
Tre prodotti (app iOS, web app, libro) coordinati da una sessione-supervisore via un
hub condiviso, con un contratto di export stabile Memoria→Domus.

## 2. Il racconto
La sessione **Recipees** (root del monorepo `Ricette/`) non scrive codice di prodotto:
coordina, tiene coerenti hub e roadmap, fa da arbitro sui contratti e merge in `main`
di Domus. **Memoria** è un'app iOS Swift 6/SwiftUI (repo separato `simonblaster/Heirloom`);
**Domus** è Next.js 16 + Firebase (`recipees-domus/`, deploy Vercel su push a `main`);
**Folio** è copy di vetrina. Il flusso di valore: Memoria digitalizza → esporta un Pack
v3 ZIP → Domus lo importa (parser `heirloom-import.ts`) creando Cookbook+Recipe e
caricando i media su Firebase Storage. Le sessioni si parlano via `RECIPEES_HUB.md`
(fonte unica di stato) e la sua CASELLA BRIEF.

## 3. Trigger & comandi
| Trigger | Innesca |
|---------|---------|
| Sessione Claude lanciata da `Heirloom/` / `recipees-domus/` / root | Carica il `CLAUDE.md` di prodotto (guardia "chi sei?" nel root) |
| Push su `main` di `recipees-domus` | Deploy automatico Vercel (~2 min) |
| Merge `feat/*` o `fix/*` Domus → `main` | Lo fa la sessione Recipees |
| Export da Memoria | Genera Pack v3 ZIP per import in Domus |

## 4. Schedule (job)
— (nessun job launchd/cron per l'ecosistema; Domus ha un backup Firestore giornaliero lato Firebase, vedi sez. 7)

## 5. Output & dove finisce
recipees.app (Domus, Vercel) · TestFlight interno (Memoria) · ZIP Pack v3 (export) ·
GitHub Pages legacy `simonblaster.github.io/Ricette/` (vedi scheda **Sito ricettario**) ·
recipees.app/folio (vetrina).

## 6. Dati & file di stato
`RECIPEES_HUB.md` (stato + decisioni + casella brief) · `ROADMAP_bug.md` · `ROADMAP_funzionalita.md` ·
`HUB_archivio.md` (brief storici) · `SPEC_*.md` (spec prodotto) · `test_exports/` (fixture Pack v3) ·
Firestore `recipees-domus` (region Frankfurt eur3, dato utente, soft-delete) ·
Memoria: `books.json` su device (no cloud).

## 7. Integrazioni & credenziali
- **GitHub**: `simonblaster/Ricette` (monorepo coord+Domus+docs), `simonblaster/Heirloom` (privato, app iOS), entrambi via SSH.
- **Vercel**: deploy Domus da `main` (env Firebase per Production+Development; **non** per Preview).
- **Firebase** (`recipees-domus`): Auth, Firestore, Storage; backup giornaliero schedulato (retention 14gg).
- **Anthropic API**: strutturazione AI (Memoria via `Config.plist` gitignorato; Domus import AI via env).
- **Resend**: email inviti Domus.

## 8. Stato attuale
- **Domus**: live su recipees.app dal 14 mag, backlog bug a zero; Crea Menu, lista spesa aggregata, ricerca rifinita in produzione.
- **Memoria**: build verde, fix data-loss confermato; **acquisizione motore unico** implementata su branch `feat/acquisizione-motore-unico` (upgrade editor completato; **convergenza 3-modalità differita post-lancio**).
- **Folio**: nessun lavoro prima di set 2026.
- Contratto Pack v3: stabile, verde sul fixture (141/141).

## 9. Runbook — "come faccio a…"
- **Coordinare**: leggi `RECIPEES_HUB.md` per intero a inizio sessione; aggiorna "Ultimo aggiornamento" a fine.
- **Mergiare un branch Domus**: verifica `tsc`+`eslint`, conferma a vista se UI, fast-forward/merge su `main`, push (Vercel autodeploya).
- **Far partire una sessione prodotto**: `cd ~/Documents/Claude/Projects/Heirloom` (Memoria) o `cd .../Ricette/recipees-domus` (Domus), poi `claude`.
- **Pubblicare le schede**: `python3 ~/.claude/skills/scheda/scripts/render_briefs.py --project "Recipees" --accent orange`.

## 10. Troubleshooting
| Sintomo | Causa probabile | Fix |
|---------|-----------------|-----|
| Codice Memoria "non c'è" nel monorepo | il vero repo è `~/Documents/Claude/Projects/Heirloom/` (separato) | usa quello, non il mirror `Ricette/Heirloom/` |
| Preview Vercel Domus fallisce build | env Firebase non impostate per environment Preview | testare in locale `npm run dev` o dopo merge in `main` |
| Due sessioni Domus in conflitto su git | commit paralleli sullo stesso `main` | worktree `feat/*`/`fix/*`, merge fatto da Recipees |

## 11. Stato live (2026-06-20)
- ✅ **recipees.app** → HTTP 200.
- ✅ **GitHub Pages legacy** → HTTP 200.
- ✅ **Repo**: Ricette (`0d17c37`), Heirloom (`22909aa`, branch `feat/acquisizione-motore-unico`), recipees-domus (`98d54f6`) — tutti con remote.
- ⚠️ Sezioni STATO PER PRODOTTO dell'hub aggiornate al 30 mag (gli "Ultimo aggiornamento" in testa sono più recenti, fino al 6 giu).
