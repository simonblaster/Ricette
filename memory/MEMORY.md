# Memory Index — Progetto Ricette
*Aggiornato: 2026-05-04 (sessione 4)*

## File di memoria

- [Paprika Workflow](paprika_workflow.md) — Skill, convenzioni pizza/focacce, scaling, naming, foto da chat, fonti elaborate

## Pattern UX — copia manuale verso app esterne (widget guida/documento)

**Comando trigger**: "mostrami la guida processi" · "crea widget copia per [documento]" · "voglio copiare questo in OneNote/Notion/…"

Quando devo consegnare un documento/guida da copiare in un'app esterna (OneNote, Notion, email…):
1. Usare `mcp__visualize__show_widget` con layout a due elementi:
   - **Pulsante "Copia tutto"** in cima (full-width, stile secondario)
   - **`<div id="content">`** con tutto il contenuto formattato in HTML (h1/h2/h3, `<strong>`, `<code>`, `<pre>`, `<ol>/<ul>`, `<table>`)
2. **Copia ricca** (preserva grassetti, codice, tabelle in OneNote):
   ```js
   var blob = new Blob([el.innerHTML], {type: 'text/html'});
   navigator.clipboard.write([new ClipboardItem({'text/html': blob})]);
   ```
   Fallback con `window.getSelection() + execCommand('copy')` se ClipboardItem non disponibile.
3. Non duplicare il testo nella risposta — è già nel widget.
4. **Rispettare TUTTI i grassetti** del documento originale — controllare ogni `**...**` nel markdown e convertirlo in `<strong>`.
5. Stile CSS minimo per il widget (da includere sempre):
   ```css
   #copyBtn{display:block;width:100%;padding:10px;margin-bottom:16px;font-size:14px;
     font-weight:500;cursor:pointer;background:var(--color-background-secondary);
     border:0.5px solid var(--color-border-secondary);border-radius:var(--border-radius-md);
     color:var(--color-text-primary)}
   #content h2{font-size:16px;font-weight:500;margin:0 0 6px}
   #content h3{font-size:14px;font-weight:500;margin:12px 0 4px}
   #content pre{background:var(--color-background-secondary);border:0.5px solid var(--color-border-tertiary);
     border-radius:var(--border-radius-md);padding:8px 12px;font-family:var(--font-mono);
     font-size:12px;white-space:pre-wrap;margin:4px 0 8px}
   #content code{font-family:var(--font-mono);font-size:12px;background:var(--color-background-secondary);
     padding:1px 4px;border-radius:3px}
   #content table{border-collapse:collapse;width:100%;font-size:13px;margin:8px 0}
   #content th,#content td{border:0.5px solid var(--color-border-tertiary);padding:5px 8px}
   #content th{font-weight:500;background:var(--color-background-secondary)}
   ```

## Da ricordare in futuro

- **Lingua di lavoro**: italiano
- **Progetto**: conversione e gestione ricette in Paprika 3 per macOS + sito web ricettario
- **Cartella progetto**: `/Users/simone/Documents/Claude/Projects/Ricette/`
- **`present_files` è rotto nelle sessioni continuate** → usare sempre `open` via Desktop Commander
- **Immagini inline chat**: non vanno in uploads, vanno estratte dal JSONL del transcript
- **WAL checkpoint**: quando si interroga il DB Paprika, copiare tutti e 3 i file (sqlite, -wal, -shm) e fare checkpoint prima di leggere
- **iCloud write da bash**: `cp` verso `~/Library/Mobile Documents/...` fallisce con "Resource deadlock" → usare i file tool Read/Edit/Write di Cowork
- **git da bash**: operazioni git sul repo montato possono lasciare `.git/index.lock` → rimuovere con `rm` oppure far eseguire i comandi git dal terminale utente

## Sito web — Recipees

- **URL**: https://simonblaster.github.io/Ricette/
- **Source canonica**: `~/Library/Mobile Documents/com~apple~CloudDocs/Ricette/Recipees website/dist/`
- **Deploy**: `docs/` nel repo `~/Documents/Claude/Projects/Ricette/`
- **Stack**: React + Babel-standalone (transpilato a runtime), responsive mobile (<880px) / desktop (>880px)
- **File chiave**:
  - `docs/index.html` — entry point, splash, polling mount
  - `docs/recipes.js` — `window.RECIPES_RAW=[...]` + `window.CATS_RAW=[...]` (generato da aggiorna_sito.py)
  - `docs/photo-uids.js` — `window.PHOTO_UIDS=new Set([...])` (generato da aggiorna_sito.py)
  - `docs/adapter.js` — trasforma RAW → `window.RECIPES` (formato prototipo)
  - `docs/v2/system.jsx` — design tokens (T), icone (II), Store, useApp, useServings, Photo, Tag…
  - `docs/v2/mobile-1.jsx` + `mobile-2.jsx` — schermate mobile
  - `docs/v2/desktop.jsx` + `desktop-2.jsx` — schermate desktop
  - `docs/v2/app.jsx` — router MobileApp / DesktopApp
- **Flusso aggiornamento**: `python3 aggiorna_sito.py` → genera recipes.js + photo-uids.js → `git add -A && git commit && git push`
- **Ingredienti**: `adapter.js::parseIngredient` gestisce "200 g cipolle", "50g cheddar" (no spazio), "Farina 00, 500 g" (formato invertito), "Sale q.b."
