# Guida ai processi — Ricettario Simone
*Aggiornata: 2026-05-03*

Questa guida descrive cosa dire a Claude e cosa aspettarsi, per ciascun processo legato al ricettario.

---

## 1. Aggiungere una pizza da un menu

**Quando usarlo**: hai trovato una pizza interessante in un menu (incollato, fotografato, da un PDF) e vuoi aggiungerla a Paprika come ricetta in teglia romana.

### Cosa dici a Claude
```
[incolla il testo del menu o descrivi la pizza nel formato:]

Nome pizza
[emoji: 🍅 rossa · 🤍 bianca · 🥙 calzone · 🔥 fritta]
Pizzeria · Sezione menu
ingrediente 1, ingrediente 2, …
```
Oppure semplicemente incolla il testo del menu e di' a Claude quale pizza vuoi aggiungere.

### Cosa fa Claude (in ordine)
1. Identifica nome pizza, tipo (rossa/bianca), pizzeria, città, maestro (cerca sul web se non noto)
2. Costruisce la ricetta nel formato teglia romana con pesi standard
3. **Si ferma e mostra la ricetta** per approvazione prima di generare il file
4. Se non hai allegato una foto: **chiede se vuoi allegarla** — puoi:
   - Inviare una foto dalla chat (anche ritagliata da uno screenshot)
   - Rispondere "no" per procedere senza
5. Genera il file `.paprikarecipes` e lo apre in Finder
6. Tu lo trascini in Paprika per importarlo

### Nota sul nome
Il formato è sempre: `Pizza in Teglia alla Romana — Nome (Pizzeria)` per le rosse, `Pizza in Teglia alla Romana — Nome (Pizzeria, bianca)` per le bianche.

### Dopo l'import
Ricordati di eseguire il processo **Aggiorna sito** (→ sezione 4) per rendere la ricetta visibile online.

---

## 2. Aggiungere una ricetta normale

**Quando usarlo**: vuoi aggiungere qualsiasi ricetta non-pizza (pasta, carne, dolci, basi…) a Paprika.

### Cosa dici a Claude
```
Aggiungi questa ricetta a Paprika: [incolla testo / link / foto]
```
Oppure descrivi la fonte: "è dal libro X, pagina Y" / "è una mia ricetta" / "dal sito Z".

### Cosa fa Claude (in ordine)
1. Estrae nome, ingredienti, dosi, directions, note dalla fonte
2. **Si ferma e mostra la ricetta** per approvazione — controlla soprattutto:
   - Le dosi (Claude usa il suo giudizio se mancano)
   - La categoria (chiede se non è ovvia)
3. Se non hai allegato una foto: **chiede se vuoi allegarla**
4. Genera il `.paprikarecipes` e lo apre
5. Tu importi in Paprika

### ⚠️ Non ancora definito
- Convenzione di naming per ricette non-pizza
- Template di directions per categorie specifiche (es. lievitati non-pizza)

---

## 3. Aggiungere una pizzeria all'archivio "Pizze che raccontano una storia"

**Quando usarlo**: hai il menu di una nuova pizzeria e vuoi archiviarla nel sito dedicato.

### Cosa dici a Claude
```
Aggiungi questa pizzeria all'archivio: [incolla menu o PDF]
```

### Cosa fa Claude (in ordine)
1. Legge il menu, estrae solo le pizze (niente antipasti, dolci, bevande)
2. Cerca il maestro pizzaiolo sul web se non indicato nel menu
3. **Mostra l'anteprima** delle pizze estratte per approvazione
4. Aggiunge al file `menu_pizzerie.json`
5. Rigenera `docs/pizze-che-raccontano-una-storia.html`
6. Chiede conferma prima del commit + push

### Regola contenuto
Solo pizze, focacce, calzoni, fritte, montanare. Niente altro.

---

## 4. Aggiornare il sito dopo aver modificato ricette in Paprika

**Quando usarlo**: hai aggiunto o modificato ricette direttamente in Paprika (su iPhone o Mac) e vuoi che il sito rifletta i cambiamenti.

### Cosa dici a Claude
```
Aggiorna il sito
```
Oppure fallo tu stesso dal terminale:
```bash
cd ~/Documents/Claude/Projects/Ricette
python3 aggiorna_sito.py
git add -A && git commit -m "Aggiornamento ricette" && git push
```

### Cosa fa lo script (automatico)
1. Backup del database Paprika (mantiene ultimi 10)
2. Legge tutte le ricette dal DB
3. Copia le foto nuove in `docs/photos/`
4. Genera `docs/recipes.js` e `docs/photo-uids.js`
5. Esporta tutto in `paprika_export_complete.paprikarecipes`

### Dopo il push
Il sito si aggiorna in ~1-2 minuti. Se vedi la versione vecchia: **⌘⇧R** (hard refresh).

---

## 5. Modificare il design del sito

**Quando usarlo**: vuoi cambiare qualcosa nell'aspetto o nel comportamento del sito.

### Cosa dici a Claude
Descrivi cosa vuoi cambiare, es:
- "Aggiungi un filtro per le ricette preferite nella homepage desktop"
- "Cambia il colore dei tag categoria"
- "Nella pagina ricetta aggiungi il campo note"

### File da modificare (Claude li conosce già)
- **Colori/font/spacing**: `docs/v2/system.jsx` → costante `T`
- **Vista mobile**: `docs/v2/mobile-1.jsx` e `mobile-2.jsx`
- **Vista desktop (indice + dettaglio)**: `docs/v2/desktop.jsx`
- **Vista desktop (ricerca, spesa, profilo, cucina)**: `docs/v2/desktop-2.jsx`
- **Logica dati**: `docs/adapter.js`

### Test locale prima del push
```bash
cd ~/Documents/Claude/Projects/Ricette/docs
python3 -m http.server 8787
# poi apri http://localhost:8787
```

---

## 6. Aggiungere una foto a una ricetta esistente

**⚠️ Processo non ancora definito completamente.**

Al momento, le foto vengono aggiunte solo tramite Paprika direttamente (su iPhone o Mac). Dopo averla aggiunta in Paprika, esegui **Aggiorna sito** (→ sezione 4) e la foto comparirà online.

Se vuoi che Claude aggiunga una foto a un `.paprikarecipes` che ha già generato: di' a Claude il nome della ricetta e allega la foto, Claude rigenera il file con la foto inclusa.

---

## Cheat sheet — comandi rapidi

| Voglio… | Dico a Claude… |
|---------|---------------|
| Aggiungere pizza da menu | incolla testo + emoji tipo |
| Aggiungere ricetta normale | "Aggiungi questa ricetta a Paprika: …" |
| Aggiungere pizzeria all'archivio | "Aggiungi questa pizzeria all'archivio: …" |
| Aggiornare il sito | "Aggiorna il sito" |
| Vedere il sito in anteprima locale | "Avvia il server locale" |
| Modificare il design | descrivi cosa vuoi cambiare |
| Committare e pushare | "Committa e pusha" |

---

## Note tecniche utili

- **Il sito non si aggiorna dopo il push**: aspetta 1-2 min e fai ⌘⇧R
- **Git dà errore di lock**: `rm ~/Documents/Claude/Projects/Ricette/.git/index.lock` poi riprova
- **Paprika non vede la ricetta importata**: riavvia Paprika o aspetta la sync iCloud
- **La lista della spesa si azzera**: è normale, il sito non salva stato tra sessioni (per ora)
