# ROADMAP — Nuove funzionalità

> Lista viva delle nuove funzionalità dell'ecosistema Recipees, organizzata per
> area. Si lavora a questo **in parallelo** al completamento della beta del
> 5 giugno. I bug noti sono tracciati a parte in `ROADMAP_bug.md`.
> Aggiornato: 2026-05-24 — sessione Recipees.

**Come si lavora.** Spec e design procedono in parallelo già ora. La
*costruzione* delle feature grosse parte **dopo il 5 giugno**, per non
destabilizzare il lancio. Ogni voce indica la sua tempistica.

**Stati:** Idea · Spec in bozza · Spec pronta · In sviluppo · Fatto.

**Documento vivo:** aggiungere qui le nuove idee man mano, nell'area giusta.
Anche le idee ancora grezze vanno bene — basta segnarle come "Idea".

---

## Memoria — *riscopri* (app iOS)

| Funzionalità | Descrizione | Stato | Riferimento / tempistica |
|---|---|---|---|
| Pianifica 2.0 | Le intenzioni diventano una coda di lavoro con passi spuntabili e avanzamento; intake guidato e conversazionale con l'AI invece del form. | Spec pronta | `SPEC_pianifica.md` · post-lancio |
| Acquisizione multi-pagina continua | Lavorare un intero blocco di pagine (es. 15) come un flusso unico: si procede dalla prima all'ultima delimitando le ricette via via — foto e testo, anche misti. Serve perché i confini di pagina non coincidono con quelli delle ricette (una foto può contenere 2 pagine; una ricetta può iniziare a pag. 2 e finire a pag. 3). Estende il meccanismo multi-ricetta dal singolo spread all'intero blocco. | In sviluppo | `SPEC_multipagina.md` · Memoria · post-lancio. Step 1-5 già implementati dalla sessione Memoria (23 mag), manca lo Step 6 (riapertura incrementale del blocco). Decisioni chiuse: modalità in più (non sostituisce il flusso pagina-per-pagina), blocco misto foto/testo, blocco riapribile/incrementale. Si appoggia a `PageMultiRecipeEditor`. |
| Import ricetta da video social (TikTok / Instagram / YouTube / Facebook) | Da un link a un video di cucina social, Memoria estrae la ricetta e la struttura. Fonti dentro il video: l'audio (trascrizione speech-to-text), la didascalia/descrizione, ed eventualmente il testo a schermo. L'AI struttura il tutto in una `Recipe`. Entry point iOS naturale: il **share sheet** — dall'app TikTok/Instagram «Condividi → Memoria». È acquisizione, nel DNA «riscopri» di Memoria. | Idea | Memoria · post-lancio. **Cross-prodotto:** l'entry point cambia per piattaforma — share sheet su iOS (Memoria), incolla-URL su web (Domus, dove si appoggerebbe all'hub di import esistente). Riusa la strutturazione AI e, per l'audio, lo speech-to-text (Memoria ha già SFSpeech; su web servirebbe un STT diverso). **Nota di fattibilità:** le piattaforme non sono uguali — YouTube espone spesso trascrizioni/sottotitoli e descrizioni, è il caso più trattabile; TikTok, Instagram Reels e Facebook sono più chiusi, senza API pubbliche di trascrizione, con limiti di ToS sullo scraping e contenuti effimeri. Una v1 onesta parte da YouTube + didascalia, con l'audio→testo come percorso portante; il resto va verificato piattaforma per piattaforma. Da scrivere una spec prima dello sviluppo. |

---

## Domus — *condividi* (web, recipees.app)

| Funzionalità | Descrizione | Stato | Riferimento / tempistica |
|---|---|---|---|
| Crea Menu | Insiemi di ricette legate a un'occasione: raggruppo automatico per portata, lista della spesa unita con scaling per commensali, stampa del menù e dei segnaposto, salvato come ricordo. | Fatto · in produzione | `SPEC_crea_menu.md` (riallineata as-built). Costruita da Domus su `feat/crea-menu` (13 commit) e **mergiata in `main` il 2026-05-23** (commit `6ee9bce`), Vercel deploy verde — `/menus` live su recipees.app. |
| Profilo nella sidebar | L'icona utente apre il Profilo (icona + nome); il logout è dentro la pagina profilo con conferma. | Fatto | commit `86f5ac2` |
| Icone azione ricetta — SVG custom | Le icone delle azioni su una ricetta passano da caratteri Unicode a SVG custom, con i box più grandi — più nitide e più facili da toccare. | Fatto | commit `9318eec`. Ritocco UI realizzato dalla sessione bug-fix Domus; tracciato qui a posteriori su richiesta del fondatore (24 mag). |
| Categorie vs Tag | Separare due concetti oggi fusi. **Categorie**: vocabolario predefinito e controllato, gestito solo dall'utente (lista iniziale, correzioni, aggiunte); l'AI assegna un piatto a una o più categorie *esistenti*, non ne crea di nuove. **Tag**: liberi, assegnati dall'AI, descrittivi, evitando di sovrapporsi alle categorie. Si filtra per entrambi. | Idea | Cross-prodotto: modello e filtri in Domus, ma l'AI di Memoria deve pescare dalla lista categorie. Da pianificare la migrazione dei `tags` esistenti (Domus è live). |
| Crea Menu — composizione assistita dall'AI | Estende Crea Menu: invece di sceglierle a mano, l'AI propone un menù coerente tra le portate (antipasto, primo, secondo, dolce). Tre punti di partenza: (a) **da una ricetta** → l'AI trova piatti che si abbinano per affinità di ingredienti; (b) **dalla stagionalità** → l'AI non propone il cocomero in inverno né il cavolo in estate; (c) **da ciò che si ha già in casa** → un menù completo con quello che c'è. L'AI fa da filtro intelligente su criteri prestabiliti o definiti al momento. | Idea | Domus · post-lancio. Si appoggia a Crea Menu (`SPEC_crea_menu.md`); motore AI condiviso col concept Locanda — è la versione "famiglia" dello stesso meccanismo. |
| Crea Menu — abbinamento bevande (vino/birra) | A menù composto, l'AI propone **2-3 abbinamenti ideali** di vino o birra (vino o birra è una scelta fatta a monte dall'utente). Ragiona sugli ingredienti portanti dei piatti — carne, presenza di pomodoro, speziatura — e abbina sia al singolo piatto sia al menù nel suo insieme. Logica per portata: un primo strutturato può chiedere un bianco importante e invecchiato, o un bianco aromatico se il piatto è speziato; il secondo, più strutturato, vira spesso sul rosso; il dessert chiama sempre un vino dolce, con la struttura calibrata sul dolce stesso (cioccolato ricco → vino strutturato e alcolico; crema e fragole → vino da dessert leggero e delicato). | Idea | Domus · post-lancio. Estende Crea Menu / composizione AI; vale anche per Locanda (anzi, lì è cruciale). Implementazione: valutare skill o MCP dedicati al pairing sommelier come base di conoscenza. |
| Crea Menu — template di stampa selezionabili | 3-4 stili grafici per il menù stampato: l'utente sceglie quello che preferisce. Oggi la stampa di Crea Menu ha un solo layout. Da valutare se i template coprono anche i segnaposto a tavola, per coerenza visiva. | Idea | Domus · post-lancio. Estende la stampa di Crea Menu (`SPEC_crea_menu.md`); il lavoro sui template potrà poi alimentare Folio. |
| Lista spesa — vista aggregata di default + normalizzazione avanzata | La lista della spesa mostra gli ingredienti **aggregati di default**: lo stesso ingrediente che arriva da ricette diverse si fonde in una riga sola, quantità sommate (3 uova + 4 uova → 7 uova). Vista **per ricetta** disponibile come opzione secondaria; toggle persistente in `localStorage`. **Parte B** (normalizzazione avanzata): plurali irregolari (tabella `CANONICAL_FORMS`), strip descrittori di preparazione in coda ("cipolla tritata" = "cipolla"), qualificatori d'uso non sommabili ("q.b.", "per servire" — merge silenzioso se ingrediente già presente, altrimenti voce senza quantità). Principio: nel dubbio NON fondere. | Fatto · in produzione | Domus · commit `ce0eb32` (vista aggregata, toggle, `aggregateItems()`), `5484d0f` (fix bug `addMenuToShoppingList` senza `fromRecipeId`), `6ff6924` (normalizzazione Parte B). Confermato a vista dal fondatore. |
| Lista spesa — nome canonico dell'ingrediente (AI) | Per unire in modo affidabile ingredienti che sono lo stesso prodotto ma scritti diversamente — sinonimi (panna / crema di latte), generico vs specificato (zucchero / zucchero semolato; **non** zucchero a velo o di canna, che restano distinti) — la decisione va presa alla **strutturazione**, non all'aggregazione. Quando l'AI struttura una ricetta, per ogni ingrediente produce, oltre al nome visualizzato, un **nome canonico per la spesa** e un **flag d'uso** (normale / guarnizione / q.b.). L'aggregazione della lista diventa allora un confronto esatto sul nome canonico. | Idea | Domus + Memoria · post-lancio. È la **v3** dell'aggregazione lista spesa: la v1/v2 (`ce0eb32` + `6ff6924`) copre plurali irregolari, descrittori di preparazione e qualificatori d'uso con regole di stringa deterministiche; questa v3 copre sinonimi e specificatori, che le stringhe non sanno distinguere. **Cross-prodotto:** campo additivo sul modello ingrediente (in Memoria la decodifica dev'essere migration-safe — vale la regola inviolabile dei dati utente) + ritocco ai prompt di strutturazione di Memoria (Haiku) e dell'import AI di Domus. Merita una mini-spec dedicata prima dello sviluppo. |
| Lista spesa — nascondere i completati (non solo rimuoverli) | Gli item completati (spuntati mentre si fa la spesa) devono poter essere **nascosti**, non solo rimossi. Proposta: un item spuntato non sparisce ma scende in una sezione «Completati (N)» in fondo alla lista; la sezione è collassabile — chiusa, la lista mostra solo ciò che resta da comprare; aperta, si rivedono i completati e si possono de-spuntare. Default consigliato: sezione collassata, con intestazione e contatore sempre visibili. Preferenza «nascondi completati» persistente per utente. «Rimuovi» resta come azione esplicita e distinta (per-item + «svuota completati»). Nascondere è un filtro di vista **non distruttivo** — l'item resta nel dato, spuntato; rimuovere cancella. Funziona in entrambe le viste, aggregata e per ricetta. | Fatto | Domus · commit `03dd361`. Sezione «Completati (N)» collassabile (default chiusa), stato persistito in `localStorage`. Funziona in entrambe le viste: aggregata (aggregateItems sugli unchecked, completati in formato riga aggregata) e per ricetta (groupByRecipe sugli unchecked, completati in flat-list). De-spuntare riporta l'item nella lista principale. Footer «Rimuovi completati» / «Svuota tutto» invariati. |
| Lista spesa → export verso app di spesa online | Esportare la lista della spesa verso una o più app di spesa online (Esselunga a Casa, Carrefour, Cortilia e analoghi, in Italia e all'estero): definisci cosa ti serve e te lo fai consegnare a casa. **Allarga il modello di business** — possibile flusso di ricavi via affiliazione / revenue-share sulle vendite generate, stile Amazon Associates. | Idea | Domus · post-lancio. Leva di modello di business, non solo feature. Dipende da integrazioni di terze parti che variano molto per insegna e mercato — vedi nota di fattibilità sotto la tabella. |
| Modalità Cucina a voce | Una modalità a mani libere mentre si cucina: è Domus a leggere ad alta voce ingredienti e passaggi, non l'utente; si avanza a voce ("vai avanti", "ingrediente preparato", "ripeti"). Schermo grande, un passo alla volta, schermo sempre acceso. | Idea | Domus · post-lancio. Vedi nota di fattibilità sotto la tabella. |
| Import nativo in Domus da foto / testo / file (AI logica Memoria) | Domus deve poter importare una ricetta direttamente sul web da una **foto** (anche pagina scritta a mano), da **testo** incollato/grezzo e da **file** generici, strutturandola con l'AI — la stessa logica di strutturazione di Memoria. Serve a chi non ha l'app iOS: oggi sul web non si digitalizza una ricetta "grezza" senza passare da Memoria. | Idea | Domus · post-lancio. È l'acquisizione *nativa* di Domus, distinta dalla pipeline di export Memoria→Domus. Cross-prodotto: la logica di strutturazione AI (prompt + schema → `Recipe`) va condivisa con Memoria, non reinventata. L'OCR su web non può usare Apple Vision: via naturale = mandare la foto direttamente a Claude (vision), che fa OCR + strutturazione in un passo. Da chiarire la sovrapposizione con l'import "Smart AI universale" già esistente — verosimilmente va esteso, non duplicato. |
| Ricerca — pulizia della UX | Snellire la schermata di ricerca. (a) **Rimuovere la sezione "suggerimenti"** — presente solo sul web, giudicata poco utile. (b) Tag e categorie oggi appaiono tutti insieme appena si apre la ricerca, formando un elenco lunghissimo (sia web sia mobile): renderli **espandibili / collassabili** con un piccolo bottone. | Fatto | Domus · commit `c4249c8`. (a) Sezione Suggerimenti rimossa. (b) Tag collassabili con bottone ▼/▲ nell'intestazione «Filtra per tag», default chiusi; tag attivi visibili anche da chiuso per permettere la deselezione; stato persistito in `localStorage`. Layout unico responsivo — funziona identicamente su desktop e mobile. |
| Crea Menu — viste della lista menù (riquadri / elenco) | La pagina lista dei menù (`/menus`) deve poter cambiare densità di visualizzazione **come fa già la lista delle ricette**: riquadri grandi, riquadri medi, riquadri piccoli, oppure elenco. L'utente sceglie la vista e la preferenza resta. | Idea | Domus · post-lancio. Estende Crea Menu (`/menus`, `SPEC_crea_menu.md`). Riusa il controllo di vista **già esistente** nella lista ricette — stesso componente, stesse 4 opzioni: va riusato, non reinventato. Preferenza preferibilmente persistente per utente. |
| Profilo — liste «Cucinate» e «Preferite» apribili ed editabili | Nella pagina Profilo i riquadri statistici **Cucinate** e **Preferite** sono oggi solo contatori. Devono diventare un punto d'accesso alle liste vere delle ricette corrispondenti, e quelle liste devono essere **editabili**: (1) togliere una ricetta che Domus segna come cucinata ma che l'utente non ha cucinato, o aggiungerne una a mano; (2) lo stesso per le preferite. L'utente deve avere il controllo di cosa c'è in quegli elenchi — un link per aprirli e, dentro, poter aggiungere, rimuovere, correggere. | Idea | Domus · post-lancio. Tocca la pagina Profilo. Le tab «Preferite» e «Cronologia» già presenti nel Profilo sono la base delle liste — vanno rese raggiungibili dai riquadri e dotate di editing. Da chiarire a parte: *perché* Domus segna come cucinate ricette che l'utente non ha cucinato — verificare la logica che marca una ricetta «cucinata» (rischio falsi positivi, es. la sola apertura della ricetta che la conta come cucinata); se è un comportamento errato è un bug per `ROADMAP_bug.md`, distinto da questa miglioria. |

**Nota fattibilità — export lista spesa (ricerca 2026-05-23).** Il modello
"trasferisci il carrello via API + prendi una commissione" esiste maturo
**solo negli USA**, con l'Instacart Developer Platform: endpoint che generano
una pagina-ricetta acquistabile (scegli negozio → ingredienti nel carrello →
checkout, 100k+ negozi), un MCP per agenti AI, e un programma di affiliazione
via Impact (~5-10 $ per nuovo cliente). **In Italia** nessuna grande insegna
(Esselunga, Carrefour, Conad, Coop) espone un'API pubblica di trasferimento
carrello: l'accesso di terze parti passa da aggregatori che fanno la spesa
fisicamente (Everli, Glovo) — Esselunga a Casa stessa si appoggia a Everli.
Strade italiane realistiche: deep-link / ricerca pre-compilata sul sito
dell'insegna (fragile, niente carrello vero né commissione); partnership o
affiliazione con un aggregatore (Everli, Glovo); reti di affiliazione (Awin,
TradeDoubler) per le insegne che vi partecipano; Amazon Fresh via Amazon
Associates. La combinazione pulita "API + revenue-share" è una realtà USA,
non ancora italiana: per l'Italia una v1 onesta è un export curato della
lista senza contare su ricavi da commissione, con la revenue-share come
opportunità da trattare a parte.

**Approfondimento Amazon (ricerca 2026-05-23).** Un'API Amazon per
pre-riempire un carrello esiste davvero: l'"Add to Cart form" della Product
Advertising API costruisce un URL con ASIN + quantità, valido su tutti i
marketplace. Tre limiti seri: è basato su **ASIN** — ogni ingrediente va
mappato a un prodotto preciso, ed è qui il vero costo per i freschi; la
Product Advertising API è **in deprecazione** (15 mag 2026, subentra la
"Creators API" — chi costruisce oggi va su quella); serve l'iscrizione ad
Amazon Associates con vendite qualificanti. Amazon Fresh **non copre "tutta
Europa"**: è città per città (poche città UK/FR/DE, Madrid, Milano). In
Italia la spesa Amazon passa sempre più dallo store **Cortilia su
`amazon.it/cortilia`** — partnership reale e in espansione (2025-2026), ma è
uno storefront gestito in autonomia da Cortilia, non un'API grocery di
Amazon. È comunque la strada più concreta rispetto alle insegne italiane,
pur non essendo un "manda la lista → carrello" pulito.

**Direzione strategica — decisa 2026-05-23.** Recipees **non** costruisce una
piattaforma logistica ("una Instacart europea"): resta il **livello di
origine** — l'intenzione, cioè ricetta, menù, lista della spesa — e fa da
**broker di domanda qualificata**, con ricavo da affiliazione / referral, non
da margine logistico. Approccio a due tempi: **breve termine → Amazon**
(Add-to-Cart + Amazon Associates, da rifare sulla "Creators API"); **resto →
partnership con aggregatori** (Glovo, Everli e affini), portando loro carrelli
ad alta intenzione d'acquisto. Nessuna logistica propria. Motivazione completa:
il settore della consegna spesa in Europa ha bruciato capitale e si è
consolidato, la Direttiva UE sul lavoro tramite piattaforme alza costo e
rischio del modello gig, e sarebbe comunque un'azienda diversa da Recipees.

**Nota fattibilità — Modalità Cucina a voce (ricerca 2026-05-23).** Due metà
con maturità tecnica diversa. La **lettura ad alta voce** (Web Speech API,
`SpeechSynthesis`) è facile, gratuita, supportata ovunque, niente backend —
ed è anche una funzione di accessibilità preziosa per un pubblico anziano. I
**comandi vocali** (`SpeechRecognition`) sono il pezzo fragile: funzionano su
Chrome/Android e in Safari iOS *come scheda del browser*, ma **non nelle PWA
installate su iOS**, sono cloud-based (serve rete) e poco affidabili in
ascolto continuo (ambiente rumoroso). Quindi la voce in *input* è un
miglioramento progressivo, mai l'unico canale: sempre fallback con zone-tocco
enormi (colpibili con la nocca / il gomito a mani sporche) e Screen Wake Lock
per non far spegnere lo schermo. La versione davvero robusta del mani-libere
vivrebbe meglio nell'app nativa Memoria (ha già il framework Speech di iOS).
Si appoggia alle directions atomiche del modello ricetta (un passaggio = una
frase). v1: route dedicata full-screen, tutto lato client, zero costi
marginali.

---

## Folio — *tramanda* (libro stampato)

Nessuna iniziativa di prodotto prima di **settembre 2026** (apertura
prevendita). Area pronta: quando si attiva, le idee — incluso il riuso del
materiale di stampa di Crea Menu — si raccolgono qui.

---

## Locanda — *(nuovo concept · B2B ristorazione)*

> **Concept affiancato a Domus**, dedicato ai piccoli ristoratori e alle
> piccole realtà della ristorazione: chi ha difficoltà a gestire il menu o a
> mantenere ordinato un ricettario professionale. Stesso DNA di Recipees — il
> ricettario che conta, curato e tramandato — applicato a chi cucina per
> mestiere. Non sostituisce Domus: gli sta accanto come linea dedicata. Il
> nome è in linea con la famiglia del brand (Memoria · Domus · Folio · Locanda).
>
> **Stato: Concept.** Da mettere a fuoco prima di una spec. Tempistica: ben
> oltre il 5 giugno — nessun lavoro di prodotto previsto a breve.

**Per chi:** chef e piccoli ristoranti con difficoltà nella gestione del menu
o nella manutenzione di un ricettario professionale.

**I due pilastri**

| Pilastro | Cosa fa | Stato |
|---|---|---|
| Gestione e backup del ricettario | (a) Lo chef mantiene il ricettario professionale per i propri scopi operativi. (b) Il proprietario ha un backup delle ricette indipendente dallo chef: se il cuoco cambia ristorante, se ne va o è malato, le ricette restano alla casa. | Idea |
| Composizione dei menu del ristorante | (a) Aiuta lo chef a comporre i menu del locale — i menu di servizio del ristorante, non i menu di una "scena"/occasione come in Domus. (b) Menu costruiti su criteri di stagionalità. (c) Affinamenti specifici dei piatti, curati dallo chef o proposti in prima battuta dall'AI. | Idea |

**Da mettere a fuoco prima di scrivere una spec**

- **Rapporto con Domus:** prodotto separato o piano/modalità "Pro" dentro
  Domus? Condividono modello ricetta, autenticazione, dominio?
- **Modello proprietario ↔ chef:** chi possiede l'account e come si gestisce
  il passaggio di consegne quando lo chef cambia. È il cuore del pilastro
  "backup" e la differenza vera rispetto a Domus.
- **Affinamenti:** definire cosa sono di preciso (varianti di un piatto?
  evoluzioni stagionali? note di rifinitura?) e quanto pesa l'AI.
- **Posizionamento:** è il primo prodotto B2B dell'ecosistema — pricing,
  supporto e aspettative cambiano rispetto a un prodotto di famiglia.
- **Il "gesto" di Locanda** nella famiglia del brand (Memoria = riscopri,
  Domus = condividi, Folio = tramanda): serve una parola sua.

---

## Idee da mettere a fuoco

Spazio per le idee grezze, prima di assegnarle a un'area o scrivere una spec.

*(vuoto — aggiungi qui)*
