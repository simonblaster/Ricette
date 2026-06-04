> ⚠️ **SUPERATA — archiviata il 2026-06-05.** Questa spec trattava il multipagina
> come **flusso isolato** (`Block*`). È stata sostituita da **`SPEC_acquisizione.md`**,
> che unifica tutto in un **motore unico** (`PageMultiRecipeEditor` generalizzato) con
> 3 modalità (Singola / Doppia / Multipagina) dove cambia solo la foto di origine.
> Tenuta solo come riferimento storico. **Non implementare da qui.**

---

# SPEC — Acquisizione multi-pagina continua (Memoria)

> Specifica / brief per la sessione Memoria, sessione Recipees, 2026-05-23.
> Decisioni di prodotto chiuse col fondatore.
> **Tempistica: post-lancio** (dopo il 5 giugno). Memoria è sul percorso
> critico della beta — questo parte dopo. È un cambio profondo del flusso
> acquisizione→strutturazione: questa spec va trasformata in un design di
> dettaglio prima di scrivere codice.

---

## 1. Cos'è e perché

Oggi Memoria acquisisce **una pagina (o uno spread) alla volta**: ogni foto è
un'unità a sé, lavorata in isolamento. Ma un ricettario scritto a mano è un
**flusso continuo**. I confini di pagina non coincidono con quelli delle
ricette:

- una foto può contenere **due pagine** di libro (uno spread);
- una ricetta può **iniziare a pagina 2 e finire a pagina 3** — o estendersi
  dalla foto 3 alla foto 5;
- tra una ricetta e la successiva il confine cade **a metà pagina**.

L'**acquisizione multi-pagina** permette di acquisire un intero blocco di
pagine (es. 15 foto, oppure testo) e lavorarlo come **un flusso unico**: si
scorre dalla prima all'ultima delimitando le ricette via via, con le ricette
libere di attraversare i confini di foglio. Estende il meccanismo
multi-ricetta dal singolo spread all'intero blocco acquisito.

---

## 2. Decisioni chiuse (2026-05-23, fondatore)

1. **Modalità in più.** Il multipagina **si affianca** al flusso di
   acquisizione pagina-per-pagina esistente, non lo sostituisce. Il flusso
   per la ricetta singola resta intatto.
2. **Blocco misto.** Un blocco può contenere **insieme** pagine fotografate
   e testo.
3. **Blocco riapribile / incrementale.** Un blocco **persiste**: si possono
   aggiungere fogli e riprendere la delimitazione in sessioni diverse. Un
   ricettario grande si digitalizza un po' alla volta — coerente col claim
   «non c'è fretta».

---

## 3. Concetti

- **Blocco** — nuovo contenitore: una sequenza **ordinata e riapribile** di
  *fogli* acquisiti, dentro un ricettario. È il piano di lavoro del
  multipagina. Porta: i fogli ordinati, le ricette delimitate finora, un
  **cursore di delimitazione** (fin dove si è arrivati lungo il blocco), uno
  stato (in corso / concluso).
- **Foglio** — un'unità acquisita nel blocco. Tipo: **foto** o **testo**. Un
  foglio-foto porta un'immagine (può essere uno spread = 2 pagine di libro);
  un foglio-testo porta un blocco di testo. I fogli sono ordinati nella
  sequenza di acquisizione.
- **Ricetta come frammenti** — nel blocco una ricetta è definita da un
  **elenco ordinato di frammenti**; ogni frammento punta a *un foglio + una
  regione* (un rettangolo sull'immagine, oppure un intervallo di testo). Una
  ricetta può avere frammenti su **fogli diversi** → attraversa i confini di
  foglio. È l'estensione del multi-rect-per-ricetta di `PageMultiRecipeEditor`:
  da «dentro uno spread» a «lungo tutto il blocco».

---

## 4. Flusso UX

**4.1 Entry point.** In `BookDetailView`, accanto ai 3 FAB esistenti
(fotocamera / foto / file), una nuova voce **«Scansione multipagina»**. Apre
la modalità multipagina. I 3 FAB attuali restano per la ricetta singola.

**4.2 Acquisizione del blocco.** L'utente compone il blocco aggiungendo
fogli: fotografa le pagine (riusando la fotocamera col timer automatico al
giro pagina), importa foto dalla libreria, importa PDF/file, incolla testo.
I fogli si accodano in ordine. L'utente può fermarsi in qualsiasi momento.

**4.3 Delimitazione continua.** L'utente scorre il blocco come un **nastro
continuo** e delimita le ricette **una dopo l'altra**. Estende il workflow
sequenziale-per-ricetta del `PageMultiRecipeEditor` v2: si marca dove inizia
e dove finisce la ricetta 1 (i suoi frammenti, anche su più fogli), si
conferma, si passa alla ricetta 2 — che parte dove la 1 è finita — e così
via. Una ricetta può andare dal foglio 3 al foglio 5.

**4.4 Strutturazione AI.** A ricetta delimitata, i suoi frammenti si
raccolgono **in ordine**: OCR (Vision) per i frammenti-foto, testo diretto
per i frammenti-testo, concatenati in ordine di lettura → Claude Haiku
struttura → una `Recipe`. Riusa la pipeline OCR+AI per-ricetta già esistente.

**4.5 Incrementale.** Il blocco resta. L'utente può tornare, **aggiungere
fogli** e riprendere la delimitazione **dal cursore**, in una sessione
successiva.

Le ricette prodotte sono `Recipe` normali nel ricettario, concluse come oggi
(`PageStatus.concluded`) e con il modello foto esistente. Il blocco è
l'impalcatura; il prodotto sono ricette regolari.

---

## 5. Cosa estende, cosa NON tocca

- **Si appoggia a `PageMultiRecipeEditor`** (già gestisce spread, cross-page,
  multi-rect per ricetta). L'estensione: la «tela» passa da un singolo spread
  all'intero blocco ordinato; i frammenti puntano a qualsiasi foglio.
- **Riusa** la fotocamera col timer automatico, gli importer foto/file, la
  pipeline OCR+AI per-ricetta.
- **NON tocca** il flusso di acquisizione pagina-per-pagina (`AcquisitionView`,
  flusso `Page` singola): resta intatto per la ricetta singola — decisione 1.

---

## 6. Decisioni da chiudere / proposte

- **Timing AI** — *proposta:* una ricetta alla volta (delimiti → AI struttura
  → passi alla successiva), coerente col workflow multi-ricetta v2 («skip AI
  iniziale»). Alternativa: batch a fine blocco. Da confermare.
- **Frammenti misti in una ricetta** — una ricetta può avere frammenti foto
  *e* testo insieme? Caso raro. *Proposta v1:* il modello lo consente, ma
  l'interazione si concentra sul caso omogeneo; foto+testo nella stessa
  ricetta è v2.
- **Modello dati lato iOS** — se il «foglio» sia una nuova entità o si
  appoggi a `Page` esistente: lo decide Memoria, che conosce `BookStore` /
  `Page`. Questa spec descrive i concetti, non le classi.
- **Chiusura del blocco** — quando tutte le ricette di un blocco sono
  delimitate e strutturate: *proposta:* il blocco si chiude, le ricette
  restano nel ricettario; il blocco resta consultabile come archivio.

---

## 7. Fasi

**v1** — blocco (entità + persistenza + riapribile); fogli misti foto/testo;
vista a nastro continuo; delimitazione sequenziale per ricetta estesa
all'intero blocco; ricette che attraversano i fogli; AI per ricetta; aggiunta
incrementale di fogli e ripresa dal cursore.

**v2** — assistenza AI alla delimitazione (l'AI propone dove iniziano/finiscono
le ricette nel blocco); frammenti foto+testo nella stessa ricetta; operazioni
batch sulla strutturazione.

---

## 8. Note tecniche e rischi

- **Cambio profondo del flusso.** Design di dettaglio accurato prima del
  codice; non è un incremento piccolo.
- **Persistenza.** Il blocco va salvato (come `Book`/`Page`, su JSON in
  Documents) perché è riapribile e incrementale.
- **Performance.** Un blocco di 15+ foto ad alta risoluzione: gestione
  memoria nello scroll continuo — lazy loading delle immagini, thumbnail.
- **Percorso critico.** Memoria è sul percorso critico del 5 giugno: questo
  lavoro parte **dopo** il lancio.

---

## 9. Piano di sviluppo v1 (ordine consigliato)

1. Modello Blocco + Foglio + Ricetta-come-frammenti; persistenza (riapribile).
2. Entry point «Scansione multipagina» in `BookDetailView` + acquisizione del
   blocco (fogli foto/testo, riuso fotocamera e importer).
3. Vista a nastro continuo del blocco (scroll, lazy loading delle immagini).
4. Delimitazione sequenziale per ricetta estesa al blocco — estensione di
   `PageMultiRecipeEditor` dai confini dello spread a quelli del blocco.
5. Raccolta frammenti in ordine → OCR (foto) / testo → AI per ricetta.
6. Riapertura del blocco + aggiunta incrementale di fogli + ripresa dal
   cursore di delimitazione.
