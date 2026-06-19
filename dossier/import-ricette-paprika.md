> Aggiornata: 2026-06-20  ·  Fonti: paprika-recipe-importer.skill, memory/paprika_workflow.md, file *.paprikarecipes in root
> Stato live al 2026-06-20: ✅ skill presente · ✅ molti export `.paprikarecipes` in root · DB `MacGourmet.mgdb` presente

# Soluzione: Import ricette in Paprika

# 👤 Vista utente

## Cosa fa
Trasforma ricette grezze (testo, foto di chat, pagine web, raccolte) in ricette
pulite e strutturate dentro Paprika 3, con convenzioni coerenti (naming, scaling,
foto, categorie) — pronte poi per finire sul sito ricettario.

## A cosa ti serve
A non inserire le ricette a mano una per una: porti dentro Paprika ciò che trovi
(un messaggio, una foto, un disciplinare pizza) e te lo ritrovi formattato secondo
le tue regole.

## Memorandum — comandi e Shortcut
| Per… | Si attiva con | Tipo | Stato |
|------|---------------|------|-------|
| Importare/convertire una ricetta in Paprika | skill `/paprika-recipe-importer` | comando | esiste |
| Generare un archivio pizze | `python3 genera_archivio_pizze.py` | comando | esiste |
| Recuperare foto da chat e generare ricetta | `python3 trova_foto_e_genera.py` | comando | esiste |

## Funzionalità in dettaglio

### Conversione di una ricetta grezza
- **Cosa fa**: prende testo/foto/URL e produce una ricetta in formato Paprika (`.paprikarecipes`).
- **Come si attiva**: skill `/paprika-recipe-importer` (le convenzioni stanno in `memory/paprika_workflow.md`).
- **Passo per passo**: fornisci la fonte → la skill applica naming, scaling, parsing ingredienti (gestisce "200 g cipolle", "50g cheddar", "Farina 00, 500 g", "Sale q.b.") e foto → ottieni il file importabile in Paprika.
- **Cosa ottieni**: ricetta pulita in Paprika, coerente con le tue convenzioni, pronta per il sito.

### Lavorazioni pizza/focacce
- **Cosa fa**: gestione dedicata di impasti (pesi, varianti, tecniche di impastamento, disciplinari).
- **Come si attiva**: i file/script dedicati (`genera_archivio_pizze.py`, `inserisci_varianti.py`, i tanti `*_teglia.paprikarecipes`, `tesauro_tecniche_impastamento.paprikarecipes`).
- **Passo per passo**: si compongono/aggiornano le varianti e si rigenera l'archivio.
- **Cosa ottieni**: una collezione pizza/focacce coerente in Paprika e sul sito.

## La catena causale
Importi/converti con le convenzioni → la ricetta entra pulita in Paprika → quando
pubblichi (`aggiorna_sito.py`, vedi scheda **Sito ricettario**) compare formattata sul
sito. La cura nell'import è ciò che rende il sito uniforme senza ritocchi a valle.

# 🔧 Vista creator

## 1. In una frase
Skill + convenzioni che normalizzano ricette grezze nel formato Paprika 3.

## 2. Il racconto
La conoscenza di dominio (naming, scaling, parsing ingredienti, foto da chat, fonti
elaborate) vive in `memory/paprika_workflow.md` ed è incapsulata nella skill
`paprika-recipe-importer.skill`. L'output sono file `.paprikarecipes` importabili in
Paprika 3 (DB `MacGourmet.mgdb`). Da Paprika, il sito si rigenera con `aggiorna_sito.py`.
È la pipeline "a monte" del sito ricettario.

## 3. Trigger & comandi
| Trigger | Innesca |
|---------|---------|
| `/paprika-recipe-importer` | conversione guidata → `.paprikarecipes` |
| `python3 trova_foto_e_genera.py` | foto da chat → ricetta |
| `python3 genera_archivio_pizze.py` | archivio pizze |

## 4. Schedule (job)
— (nessun job: import manuale on-demand)

## 5. Output & dove finisce
File `.paprikarecipes` in root del progetto → importati in Paprika 3 → da lì al sito via `aggiorna_sito.py`.

## 6. Dati & file di stato
`*.paprikarecipes` (molti in root: pizze/focacce/famiglia) · `MacGourmet.mgdb` / `MacGourmet_Ricette.paprikarecipes` · `categorie_tracciate.json` · `Backup Paprika/` · convenzioni in `memory/paprika_workflow.md`.

## 7. Integrazioni & credenziali
Nessun token/API esterna. Solo file locali + Paprika 3 (app macOS). Foto inline da chat: estratte dal JSONL del transcript (non da uploads).

## 8. Stato attuale
LIVE come strumento on-demand. È il workflow storico pre-Memoria; per le ricette di famiglia "nuove" il percorso è Memoria→Domus, ma questo resta per Paprika/sito.

## 9. Runbook — "come faccio a…"
- **Importare una ricetta**: invoca `/paprika-recipe-importer`, segui le convenzioni.
- **Aggiungere una pizza**: aggiorna le varianti, `genera_archivio_pizze.py`, importa in Paprika, `aggiorna_sito.py`.
- **Recuperare una foto inline**: `trova_foto_e_genera.py` (estrae dal JSONL del transcript).

## 10. Troubleshooting
| Sintomo | Causa probabile | Fix |
|---------|-----------------|-----|
| Foto della chat non trovata | cercata in uploads invece che nel JSONL | usare `trova_foto_e_genera.py` / estrarre dal transcript |
| Ingredienti mal parsati | formato non coperto da `adapter.js::parseIngredient` | normalizzare la riga o estendere il parser |
| Ricetta non compare sul sito | importata in Paprika ma sito non rigenerato | `aggiorna_sito.py` + push |

## 11. Stato live (2026-06-20)
- ✅ Skill `paprika-recipe-importer.skill` presente in root.
- ✅ Numerosi `.paprikarecipes` presenti (pizze/focacce/famiglia) + `MacGourmet.mgdb`.
- ✅ `memory/paprika_workflow.md` presente come fonte delle convenzioni.
