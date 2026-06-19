> Aggiornata: 2026-06-20  ·  Fonti: memory/MEMORY.md, memory/paprika_workflow.md, aggiorna_sito.py/sh, docs/, repo git
> Stato live al 2026-06-20: ✅ sito HTTP 200 · ✅ docs/ completo (index.html, recipes.js, photo-uids.js)

# Soluzione: Sito ricettario (Paprika → GitHub Pages)

# 👤 Vista utente

## Cosa fa
Pubblica il tuo ricettario personale come sito web statico, partendo dal database
Paprika 3 sul Mac. È il ricettario "storico" (pizze, focacce, ricette di famiglia)
online su https://simonblaster.github.io/Ricette/, responsive su mobile e desktop.

## A cosa ti serve
Ad avere le tue ricette Paprika consultabili dal browser/telefono senza aprire
Paprika, e a condividerne il link. È il predecessore di Domus, ancora vivo.

## Memorandum — comandi e Shortcut
| Per… | Si attiva con | Tipo | Stato |
|------|---------------|------|-------|
| Rigenerare e pubblicare il sito | `python3 aggiorna_sito.py` poi commit+push di `docs/` | comando | esiste |
| Pubblicare (scorciatoia) | `aggiorna_sito.sh` | comando | esiste |
| Importare nuove ricette in Paprika | skill `/paprika-recipe-importer` | comando | esiste (vedi scheda Import) |

## Funzionalità in dettaglio

### Aggiornamento del sito da Paprika
- **Cosa fa**: legge il DB Paprika, rigenera i dati del sito e li pubblica.
- **Come si attiva**: `python3 aggiorna_sito.py` dalla root del progetto.
- **Passo per passo**: lo script genera `docs/recipes.js` (`window.RECIPES_RAW`+`CATS_RAW`) e `docs/photo-uids.js` (`window.PHOTO_UIDS`) → poi `git add -A && git commit && git push` → GitHub Pages serve `docs/`.
- **Cosa ottieni**: il sito aggiornato su https://simonblaster.github.io/Ricette/ entro pochi minuti.

### Manutenzione dati ricette
- **Cosa fa**: una serie di script di servizio per categorie, varianti, foto, link, liste.
- **Come si attiva**: i singoli `*.py` in root (`applica_categorie.py`, `assegna_categorie.py`, `rimuovi_categorie.py`, `inserisci_varianti.py`, `fix_recipe_links.py`, `fix_lista.py`, `fix_grocery_aisles.py`, `genera_archivio_pizze.py`, `trova_foto_e_genera.py`, `sync_commenti.py`, `ripristina_rimozioni.py`).
- **Passo per passo**: si lanciano a mano quando serve una correzione massiva, poi si ripubblica con `aggiorna_sito.py`.
- **Cosa ottieni**: dati ricette puliti/coerenti prima della pubblicazione.

## La catena causale
Importi/correggi le ricette in Paprika → `aggiorna_sito.py` traduce il DB in JS
statico → commit/push → GitHub Pages mostra il sito. Il sito è sempre lo specchio
del DB Paprika al momento dell'ultimo `aggiorna_sito`.

# 🔧 Vista creator

## 1. In una frase
Generatore statico che trasforma il DB Paprika 3 in un sito React (Babel-standalone) servito da GitHub Pages.

## 2. Il racconto
La source canonica è il DB Paprika sul Mac (+ una copia di lavoro in iCloud,
`~/Library/Mobile Documents/com~apple~CloudDocs/Ricette/Recipees website/dist/`).
`aggiorna_sito.py` interroga il DB (attenzione al WAL checkpoint: copiare sqlite+`-wal`+`-shm`
e fare checkpoint prima di leggere), genera `recipes.js` e `photo-uids.js` dentro
`docs/`, che è la cartella pubblicata da GitHub Pages. Il front-end vive in `docs/v2/`
(system.jsx con design tokens, mobile-1/2.jsx, desktop.jsx, app.jsx router) transpilato
a runtime via Babel-standalone. `adapter.js` trasforma i RAW nel formato del prototipo.

## 3. Trigger & comandi
| Trigger | Innesca |
|---------|---------|
| `python3 aggiorna_sito.py` | rigenera recipes.js + photo-uids.js |
| `aggiorna_sito.sh` | scorciatoia di pubblicazione |
| `git push` di `docs/` | GitHub Pages ripubblica |

## 4. Schedule (job)
— (nessun job: pubblicazione manuale)

## 5. Output & dove finisce
Sito statico su **https://simonblaster.github.io/Ricette/** (sorgente in `docs/` del repo `simonblaster/Ricette`).

## 6. Dati & file di stato
`docs/recipes.js` (`window.RECIPES_RAW`, `window.CATS_RAW`) · `docs/photo-uids.js` (`window.PHOTO_UIDS`) ·
`docs/index.html` (entry) · `docs/v2/*.jsx` (UI) · `categorie_tracciate.json` · DB Paprika (`MacGourmet.mgdb` / export `.paprikarecipes`).

## 7. Integrazioni & credenziali
GitHub (SSH, repo `simonblaster/Ricette`, Pages da `docs/`). Nessun token applicativo. iCloud Drive per la source di lavoro (⚠️ write da bash verso iCloud fallisce con "Resource deadlock": usare i file-tool, non `cp`).

## 8. Stato attuale
LIVE e stabile. È il ricettario legacy; lo sviluppo nuovo è su Domus. Si mantiene per le ricette già pubblicate (pizze/focacce/famiglia).

## 9. Runbook — "come faccio a…"
- **Pubblicare un aggiornamento**: `python3 aggiorna_sito.py` → `git add -A && git commit -m "..." && git push`.
- **Correggere categorie/varianti in massa**: lo script `*.py` dedicato, poi ripubblica.
- **Leggere il DB Paprika senza corrompere**: copia i 3 file (sqlite,-wal,-shm), checkpoint, poi leggi.

## 10. Troubleshooting
| Sintomo | Causa probabile | Fix |
|---------|-----------------|-----|
| Sito non aggiornato dopo push | Pages non ha ancora ribuildato, o `docs/` non committato | attendi 1-2 min; verifica `git status` di `docs/` |
| Dati ricette vecchi/incompleti | letto il DB Paprika con WAL non checkpointato | copia sqlite+wal+shm, checkpoint, rigenera |
| Scrittura iCloud fallita | "Resource deadlock" da bash | usa i file-tool Read/Edit/Write, non `cp` |

## 11. Stato live (2026-06-20)
- ✅ **https://simonblaster.github.io/Ricette/** → HTTP 200.
- ✅ **docs/** → `index.html`, `recipes.js`, `photo-uids.js` presenti (3/3).
- ✅ Repo `simonblaster/Ricette` con remote; ultimo commit `0d17c37`.
