# SPEC — Acquisizione Memoria: motore unico, 3 modalità

> **Stato:** Spec pronta · 2026-06-05 · brainstorming fondatore + sessione Recipees.
> **Supera:** `SPEC_multipagina.md` (multipagina come flusso isolato — archiviato).
> **Prodotto:** Memoria (iOS, codename Heirloom). **Implementa:** sessione Memoria.
> **Codice reale:** `~/Documents/Claude/Projects/Heirloom/` (repo separato, NON il
> mirror in `Ricette/Heirloom/`). Vedi `RECIPEES_HUB.md` → «DOVE VIVE IL CODICE».
> **Tempistica:** post-lancio 5 giugno (è un cambio profondo del flusso acquisizione).

---

## 1. Obiettivo

Oggi il "multipagina" è una **modalità isolata** affiancata alle altre, e la
delimitazione delle ricette esiste in **due implementazioni separate**:

- **`PageMultiRecipeEditor`** — editor ricco, ma gira su **una sola foto**, agganciato
  solo a `PageDetailView`. Spread a 2 hardcoded (`PageSide .left/.right`, larghezze 0.5),
  colonne max 2 (`twoColumnsMode`), testo = stripe a tutta larghezza, foto = riquadro libero.
- **`Block*`** (`BlockTapeView`, `BlockSessionView`, `BlockRecipeProcessor`,
  `BlockListView`, `BlockAcquisitionView`) — il "multipagina" del FAB, delimitatore
  parallelo che NON usa `PageMultiRecipeEditor`.

**Obiettivo:** un **unico motore** di delimitazione per tutte le modalità, dove
**cambia solo la foto di origine**. Stessi strumenti, stesse logiche, nessuna
reinvenzione tra una modalità e l'altra. Coprire i casi oggi scoperti: pagina
singola vera (senza spine forzato), colonne 3+/irregolari, ricette sparse, e
ricette a cavallo di pagine fisicamente non contigue (facciata→retro).

---

## 2. Principio architetturale

**Un solo delimitatore: `PageMultiRecipeEditor` generalizzato.** La logica di
delimitazione dentro i `Block*` viene **ritirata**; i `Block*` restano semmai solo
come **contenitore della sequenza di fogli** che alimenta l'editor (o vengono
assorbiti). Il modello dati ricetta-regione resta invariato:

```
RecipeRegion { recipeRects:[CGRect], photoRects:[CGRect], hint }   // coord. 0–1
```

**Downstream invariato:** la `RecipeRegion` finita va al pipeline OCR+AI esistente
(`BlockRecipeProcessor` / multi-ricetta). Il pipeline **non sa né gli importa** come
la regione è stata disegnata (colonna vs riquadro) né su quanti fogli si estende:
riceve solo i ritagli-testo della ricetta + il ritaglio-foto.

---

## 3. Due famiglie di fonti

Il menu di acquisizione (FAB in `BookDetailView`) resta organizzato per **fonte**.
La voce **"Multipagina" sparisce** come modalità a sé.

- **Fonti-immagine** — Fotocamera, Foto, File → **qui vivono le 3 modalità** (§4).
- **Fonti-non-pagina** — Audio, Video, Testo → **invariate**, nessuna scelta di
  raggruppamento. (Audio/video si registrano ricetta per ricetta; il testo è
  sequenziale e si suddivide tra ricette, non "a pagine".)

---

## 4. Tre modalità = preset sulla stessa struttura «sequenza di fogli»

La sorgente è sempre una **sequenza di fogli**; ogni foglio è di tipo **singolo**
(una pagina, niente spine) o **doppio** (spread, con spine). Le modalità sono preset:

| Modalità | Sorgente | Spine | Ricette a cavallo |
|---|---|---|---|
| **Singola** | 1 foglio singolo | ❌ nessuno | — |
| **Doppia** | 1 spread (foglio doppio) | ✅ come oggi | sx ↔ dx |
| **Multipagina** | N spread in sequenza | ✅ | dx foglio N → sx foglio N+1 (retro fisico) |

- `PageSide` (oggi 2 valori, `minX` 0/0.5, `width` 0.5 fissa) diventa una coppia
  **(indice foglio, lato)**. Lato assente sui fogli singoli, `.left/.right` sui doppi.
- Il modello tollera un foglio singolo dentro un multipagina (ogni foglio porta il
  suo tipo), ma l'esperienza multipagina è tarata sugli **spread**.
- Multipagina = "Doppia ripetuta N volte + attraversamento tra fogli".

---

## 5. Lo slider è lo strumento universale (il cuore)

**Una regione = un rettangolo definito da 4 slider** (alto, basso, sinistro, destro),
usato **per il testo e per la foto**, per colonne regolari e irregolari.

- **Niente nuovo mattone**: nessun "riquadro libero" separato. Tutto è un rettangolo
  a slider.
- **Gli slider verticali (sx/dx) sono SEMPRE attivi** → 1/2/3/N colonne, anche di
  larghezza diversa. Il toggle **`twoColumnsMode` viene rimosso**.
- **Foto con gli stessi slider**: "aggiungi foto" → gli slider diventano
  temporaneamente dedicati alla foto → riquadri → "fatto" → torni alla ricetta →
  salvi. Niente quadrante fisso, niente drag agli angoli: **stessa gestualità**.
- **Ricetta spezzata / a cavallo**: "aggiungi stripe" (gesto già esistente) infila la
  regione successiva nella ricetta corrente — generalizzato a *qualsiasi colonna /
  pagina affiancata / foglio del blocco*. (`recipeRects:[CGRect]` già lo permette.)

### 5.1 Default progressivi degli slider (LA novità chiave da costruire)

Dopo ogni salvataggio, gli slider della selezione successiva si **pre-posizionano
sull'avanzo** (il contenuto non ancora ritagliato):

- **alto** = dove finiva il taglio precedente (nella stessa colonna);
- **sinistro** = il bordo della colonna appena chiusa.

Flusso tipico, una mano sola: chiudo la ricetta in alto a sx → la prossima parte già
con l'alto e il sx giusti, sposto solo il **basso** e salvo → scendo nella colonna →
poi passo alla colonna successiva (sx già pronto) → muovo gli slider → continuo.
Le ricette irregolari/a cavallo di due colonne restano come **avanzo** e si riquadrano
con gli slider quando ci si arriva.

### 5.2 Salvataggio incrementale

Salva ricetta → la regione si **chiude e sparisce dalla vista** (vincolo
anti-sovrapposizione già esistente con le regioni completate) → si continua a
riquadrare ciò che resta, finché il foglio/sequenza è vuoto.

---

## 6. Spine

**Nessuna modifica.** Si mantiene il comportamento attuale (default + posizione
aggiustabile). Vale per i fogli doppi (Doppia e Multipagina); assente sui fogli
singoli (Singola).

---

## 7. Seed AI (`detectRecipeRegions`)

Passa da **automatico all'apertura** a **a richiesta**: un tasto «proponi con l'AI».
Le pagine pulite ci guadagnano un avvio rapido; le pagine irregolari/manoscritte
partono **vuote**, senza box sbagliati da disfare. In **Multipagina** il seed si
lancia **per-spread**, solo dove serve.

> **Sperimentale — candidato alla rimozione.** Si tiene a vista per valutarlo sul
> campo; se risulta più d'intralcio che d'aiuto, si elimina.

---

## 8. Memoria della modalità (per-libro)

Pre-selezione **morbida per-libro**: il ricettario si apre già sull'ultima modalità
usata *per quel libro*, sempre cambiabile con un tap prima di scattare (non è un
lucchetto). Gestisce l'alta variabilità tra libri senza richiedere una scelta ogni
volta.

- **Libro nuovo, senza storia → nessuna pre-selezione: la prima volta te lo chiede.**
  Dalla seconda acquisizione subentra la memoria del libro.
- Persistenza: ultimo `mode` usato sul `Book` (campo additivo, **migration-safe** —
  `decodeIfPresent`, vedi regola inviolabile dati utente in `Heirloom/AGENTS.md`).

---

## 9. Cosa cambia nel codice (riepilogo per l'implementazione)

Generalizzazioni mirate su componenti esistenti — **non un motore nuovo**:

1. **Convergenza**: `PageMultiRecipeEditor` diventa l'unico delimitatore; ritirare la
   delimitazione dei `Block*` (assorbire/declassare a contenitore di fogli).
2. **Sorgente a sequenza di fogli**: `PageSide` → `(indice foglio, lato)`; supporto a
   foglio singolo (no spine, pagina a tutta larghezza 0–1) e a N spread in sequenza.
3. **Attraversamento tra fogli**: "aggiungi stripe" può puntare a un altro foglio
   (dx N → sx N+1), non solo all'altro lato dello spread corrente.
4. **Slider verticali sempre attivi** → N/colonne irregolari; **rimuovere
   `twoColumnsMode`**.
5. **Default progressivi degli slider** sull'avanzo (alto = fine taglio precedente,
   sx = colonna appena chiusa) — §5.1. È il pezzo nuovo principale.
6. **Crop foto unificato sugli slider** (stessa gestualità del testo).
7. **Seed AI a richiesta** (tasto), per-spread in multipagina.
8. **Memoria per-libro** della modalità + scelta alla prima acquisizione di un libro nuovo.
9. **Entry/menu**: rimuovere la voce FAB "Multipagina"; per le fonti-immagine la
   modalità (Singola/Doppia/Multipagina) è una proprietà del flusso (toggle in camera;
   per Foto/File la modalità pre-selezionata dalla memoria del libro).

**Invariato:** modello `RecipeRegion`, slider top/bottom, salva-e-prossima,
anti-overlap, coordinate 0–1, associazione foto, pipeline OCR+AI a valle
(`BlockRecipeProcessor`), comportamento spine.

---

## 10. Fuori scope (esplicito)

- **Asse lingue / multilingua**: tracciato a parte (`ROADMAP_funzionalita.md` →
  «Acquisizione multilingua»). Non è oggetto di questa spec.
- **Strumenti dedicati per-tipo-di-libro** (tassonomia regolare/denso/manoscritto):
  scartato come overkill — il "tipo di libro" si dissolve nella memoria per-libro
  della modalità (§8) + scelta degli slider.
- **Pipeline unica "singola = blocco da 1 foglio"**: valutata e **non** adottata come
  default (snaturerebbe la lavorazione indipendente della singola). Resta possibile
  in futuro, non ora.
- Audio / Video / Testo: nessuna modifica.

---

## 11. Note di processo

- **Regola inviolabile dati utente**: ogni campo nuovo persistito (`Book.mode`, ecc.)
  migration-safe con `decodeIfPresent`; nessuna sovrascrittura su load fallito.
- **Verifica a vista** prima di "fatto": è una feature UI: niente "Risolto" senza
  prova sul device (regola condivisa in `RECIPEES_HUB.md`).
- Deliverable di questa sessione (Recipees): **questa spec**. Il piano di
  implementazione e il codice li produce la **sessione Memoria**, idealmente lanciata
  da `~/Documents/Claude/Projects/Heirloom/`.
