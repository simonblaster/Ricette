# Paprika Recipe Importer — Workflow & Conventions

## File e percorsi chiave
- **Skill**: `/Users/simone/Documents/Claude/Projects/Ricette/paprika-recipe-importer.skill`
- **Skill source (SKILL.md)**: nella sessione di lavoro, in `outputs/paprika-recipe-importer/SKILL.md`
- **Script build**: `build_paprikarecipes.py` bundled nel .skill zip
- **DB Paprika**: `/Users/simone/Library/Group Containers/72KVKW69K8.com.hindsightlabs.paprika.mac.v3/Data/Database/Paprika.sqlite` (WAL mode — copiare tutti e 3 i file prima di interrogare)
- **Output**: `/Users/simone/Documents/Claude/Projects/Ricette/*.paprikarecipes`

## Consegna file
- `present_files` è **rotto nelle sessioni continuate** → usare sempre Desktop Commander:
  ```
  open "/Users/simone/Documents/Claude/Projects/Ricette/file.paprikarecipes"
  ```

## Flusso "trasforma in ricetta" — da menu/archivio a Paprika

Quando l'utente incolla una pizza nel formato archivio (4 righe):
```
Nome pizza          ← RIGA 1: nome della pizza (es. "DOC", "Elena Ferrante")
[emoji tipo]        ← RIGA 2: 🍅 rossa · 🤍 bianca · 🥙 calzone · 🔥 fritta
Pizzeria · Sezione  ← RIGA 3: es. "Carmnella · Per Mano Mia — 30 Anni di Banco"
ingrediente 1, …    ← RIGA 4: ingredienti
```
⚠️ **Riga 1 = nome pizza. Quello dopo il "·" in riga 3 è la sezione/categoria del menu, NON il nome della pizza.** Non usare mai la sezione come nome ricetta.

oppure in qualsiasi formato testuale libero da un menu o sito, il workflow è:

1. **Invoca subito lo skill `paprika-recipe-importer`** prima di fare qualsiasi altra cosa.
2. **Classifica**: 🍅 = rossa, 🤍 = bianca, 🥙 = calzone, 🔥 = fritta.
3. **Tipo ricetta**: sempre **Type 2 versione teglia 40×30** (a meno che l'utente non specifichi diversamente — es. napoletana tonda).
4. **Nome Paprika**: `Pizza in Teglia alla Romana — [nome pizza] ([Pizzeria])` per rosse · `Pizza in Teglia alla Romana — [nome pizza] ([Pizzeria], bianca)` per bianche. Esempi: `Pizza in Teglia alla Romana — DOC (Carmnella)` · `Pizza in Teglia alla Romana — Reginella (Carmnella, bianca)`. La pizzeria è sempre in parentesi, subito dopo il nome; `bianca` aggiunta dopo la virgola se 🤍.
5. **Impasto di riferimento** (prima riga degli ingredienti, subito dopo l'header): `Impasto per teglia romana, 1 panetto da circa 600 g` — testo plain, nessun link Paprika `[recipe:...]`.
6. **Pesi standard per 1 teglia 40×30** (da usare salvo indicazioni diverse):
   - Salsa di pomodoro: 150 g
   - Fior di latte / fiordilatte: 230 g
   - Mozzarella di bufala DOP: 200 g
   - Pomodorini datterini (confit/saltati/filetto): 120 g
   - Parmigiano / Grana (scaglie o grattugiato): 30 g
   - Pecorino Romano: 25 g
   - Prosciutto crudo / bresaola / mortadella (a crudo): 80 g
   - Prosciutto cotto: 100 g
   - Salsiccia / salamino: 80 g
   - Provola affumicata: 120 g
   - Scamorza affumicata: 120 g
   - Gorgonzola / erborinati: 100 g
   - Stracciatella / burrata: 150 g
   - Ricotta: 150 g
   - Funghi (trifolati): 100 g
   - Verdure (zucchine, melanzane, peperoni, carciofi): 120 g
   - Olive: 40 g
   - Alici / acciughe: 30 g
   - Capperi: 15 g
   - Nduja: 50 g
   - Basilico / erbe fresche: q.b.
   - Per ingredienti non in lista: usa `*` e aggiungi nota "* Quantità indicativa — assaggia e aggiusta."
7. **Scaling factor**: usa il factor dell'impasto scelto. Per APiTeR (×0.65) i pesi sopra sono già calibrati per 1 teglia — **non** riapplicare il factor ai condimenti, sono già per 1 teglia.
8. **Directions**: usa il template standard (sezione E dello skill). Rossa = doppia cottura con prima a 325°/225°; bianca = doppia cottura con prima a 300°/200°.
9. **source**: `"Maestro — Pizzeria, Città"` (es. `"Vincenzo Esposito — Carmnella, Napoli"`). Se il maestro non è noto nell'input, cercalo via web prima di procedere. Se non trovato, usa solo `"Pizzeria, Città"`.
10. **Consegna**: salva in `/Users/simone/Documents/Claude/Projects/Ricette/` e apri con Desktop Commander: `open "/Users/simone/Documents/Claude/Projects/Ricette/file.paprikarecipes"`

## Convenzioni pizza/focaccia

### Naming
- **Type 1 impasto**: `[Base] — [tipo impasto] ([ore lievitazione] ore, [fonte])`
- **Type 2 versione rossa**: `[Base] — [nome pizza] ([Pizzeria])`
- **Type 2 versione bianca**: `[Base] — [nome pizza] ([Pizzeria], bianca)`
- La pizzeria va **sempre** in parentesi dopo il nome pizza, separata da virgola da `bianca` se bianca
- Esempi: `Pizza in Teglia alla Romana — DOC (Carmnella)` · `Pizza in Teglia alla Romana — Reginella (Carmnella, bianca)`
- Sottotitoli commemorativi/marketing (es. "30 Anni di Banco") vanno omessi dal nome salvo siano parte strutturale del nome originale
- **Categorie impasto**: `["Impasti per pizze, focacce & co."]`
- **Categorie versione**: `["Pizze, focacce & co."]`

### Scaling a 1kg farina
- `factor = 1000 / total_flour_g`
- Rounding: ≥100g→5g, 10-99g→1g, 1-9.9g→0.1g, <1g→0.01g
- Header impasto teglia: `**Dosi per 3 teglie da 40×30 — fattore ×X.XX**`
- Header versione teglia: `**Dosi per 1 teglia 40×30**` (nessun fattore nelle versioni)

### Formati
- **Teglia 40×30**: 3 teglie per 1kg farina, panetto ~600g, idratazione ~75-80%
- **Tonda ~250g** (napoletana): 6 pizze per 1kg farina, panetto ~250g, idratazione ~65%
- **Teglia tonda** (focacce/schiacciate, es. 32cm): trattare come 40×30, 3 teglie standard
- **NON** applicare convenzione tonda napoletana alle focacce

### Impasto nelle versioni (testo plain, no link Paprika)
Prima e seconda riga degli ingredienti versione:
```
**Dosi per 1 teglia 40×30**
Impasto per teglia romana, 1 panetto da circa 600 g
```
Riga vuota obbligatoria dopo, poi gli ingredienti del condimento.
⚠️ Non usare mai `[recipe:...]` nelle versioni. Non usare header con fattore `×X.XX`.

### Template cottura teglia — versioni (solo ingredienti)

Anche quando la fonte fornisce solo ingredienti, le directions vanno sempre incluse usando il template standard.

**Classificazione automatica rossa/bianca:**
- Rossa → ingredienti contengono pomodoro/passata/pelati
- Bianca → nessun pomodoro

**A caldo / a crudo:**
- A caldo: mozzarella, fior di latte, provola, scamorza, proteine cotte, salse
- A crudo: prosciutto crudo, bresaola, mortadella, stracciatella, burrata, ricotta fresca, erbe fresche, verdure crude

**Temperature (forno Nettuno, camera 17 cm — da aggiornare con l'esperienza):**

| | Platea | Cielo | Durata | Rotazione |
|---|---|---|---|---|
| Prima cottura rossa | 325° | 225° | 5-6 min | dopo 3 min |
| Prima cottura bianca | 300° | 200° | 5-6 min | dopo 3 min |
| Seconda cottura (tutte) | 300° | 200° | 5-6 min | — |

**Napoletana:** directions vuote a meno che non ci siano ingredienti a crudo → `"Cuocere la pizza. All'uscita dal forno aggiungere [X] e [Y]."`

**Note standard da aggiungere sempre alle versioni teglia:**
```
Temperature e tempi indicativi basati su esperienza attuale con forno Nettuno (camera 17 cm) — da aggiornare con nuove esperienze.
Tra un'infornata e l'altra, attendere 2-3 minuti per il recupero calore della pietra refrattaria.
```

### Formattazione directions
- Sezioni: `**N. Titolo sezione**` + riga vuota dopo
- Steps: testo plain, nessun bullet, riga vuota tra steps
- Fine step: punto, non punto e virgola
- Strip artefatti PDF: numeri pagina, "academia.tv", "guarda la videoricetta"

## Estrazione foto dalla chat (Cowork)

Le immagini inline in Cowork **NON** vanno in uploads — vanno estratte dal transcript JSONL:

```python
jsonl = "mnt/.claude/projects/[path]/[uuid].jsonl"  # main, non subagents/

def find_base64_images(obj):
    results = []
    if isinstance(obj, dict):
        if obj.get('type') == 'image' and obj.get('source', {}).get('type') == 'base64':
            results.append(obj['source']['data'])
        for v in obj.values(): results.extend(find_base64_images(v))
    elif isinstance(obj, list):
        for item in obj: results.extend(find_base64_images(item))
    return results
```

- Immagini inviate "while working" → tipo `attachment` nel JSONL (estratte ugualmente in modo ricorsivo)
- Filtrare per posizione: le foto ricetta sono sempre alla fine del JSONL
- Encode: `PIL.Image → JPEG quality=85 → base64`

## Formati speciali — Lo Stocco "Pizza Croccante"
- **Padellino 25 cm** (crustica): panetto ~250g, ~8 padellini per 1kg farina → header impasto `**Dosi per ~8 padellini da 25 cm (panetti da ~250 g) — fattore ×X.XX**`; versione header `**Dosi per 1 padellino da 25 cm — fattore ×0.50**` (dosi source per 2 pizze → halved)
- **Pala croccante** (supercrust): panetti 300g (bassa) o 400g (alta), ~5-6 pizze per 1kg → header `**Dosi per ~5-6 pizze in pala (panetti da 300-400 g) — fattore ×X.XX**`; versione header `**Dosi per 1 pizza in pala (base da Xg) — fattore ×0.50**`

## Archivio menu pizzerie — "Pizze che raccontano una storia"
- **DB**: `menu_pizzerie.json` — struttura `{pizzerie: [{nome, citta, maestro, stile, note_menu, pizze: [...]}]}`
- **Sito locale**: `menu_pizzerie.html` — generato da `outputs/genera_menu_files.py`
- **Sito GitHub Pages**: `docs/pizze-che-raccontano-una-storia.html` → https://simonblaster.github.io/Ricette/pizze-che-raccontano-una-storia.html
- **Script generazione**: `aggiorna_sito.py` (nella root del progetto) — legge direttamente dal DB Paprika, genera `docs/index.html` + copia foto, esegue backup DB. Dopo ogni sessione: `python3 aggiorna_sito.py` → `git add -A && git commit && git push`
- **Regola contenuto**: includere SOLO pizze e simili (calzoni, fritte, montanare). MAI antipasti, dolci, bevande, snack.
- **fonte**: `"Maestro — Pizzeria, Città"` (es. `"Antonio Starita — Pizzeria Starita, Napoli"`)
- **tipo emoji**: 🍅 rossa · 🤍 bianca · 🥙 calzone · 🔥 fritta
- **Pizzerie archiviate** (aggiornato 2026-05-02): O' Sarracin/Milano (22), Carmnella/Napoli — Vincenzo Esposito (49), Pizzeria Starita/Napoli — Antonio Starita (38), Factory/Caserta — Francesco Martucci (23) → **132 totali**
- **Flusso aggiunta pizzeria**: menu incollato → script Python in outputs/ → aggiunge a JSON → riesegui genera_menu_files.py → copia in docs/ → commit + push
- **Rete sandbox**: pizzeriestarita.it e la maggior parte dei domini non sono raggiungibili dalla sandbox. Usare Chrome MCP (solo tab del gruppo MCP) oppure copia-incolla dell'utente.

## Fonti elaborate (aggiornato 2026-05-02)
| File | Contenuto |
|------|-----------|
| `pizza_napoletana_avpn.paprikarecipes` | 7 ricette AVPN (impasto + 6 versioni), ×0.65 |
| `pizza_alla_pala_spampatti.paprikarecipes` | Spampatti — pala |
| `Ricette_Jacopo_Mercuro.paprikarecipes` | Mercuro — teglia romana |
| `pizza_teglia_romana_disciplinare.paprikarecipes` | APiTeR disciplinare |
| `pizza_in_teglia_75.paprikarecipes` | Teglia romana 75% |
| `ricette_aggiornate.paprikarecipes` | Pizza teglia 3ore, Focaccia Messinese (2), Schiacciata toscana |
| `tesauro_tecniche_impastamento.paprikarecipes` | 6 ricette academia.tv (Tesauro) |
| `focaccia_messinese_ada_parisi.paprikarecipes` | Ada Parisi — impasto + versione tradizionale (indivia, tuma, acciughe) |
| `pizza_croccante_lo_stocco.paprikarecipes` | Lo Stocco — 2 impasti (crustica poolish + supercrust biga) + 4 versioni |
| `margherita_teglia.paprikarecipes` | Versione teglia — Margherita (rossa) |
| `stracciatella_mortadella_teglia.paprikarecipes` | Versione teglia — stracciatella e mortadella (bianca, tutto a crudo) |
| `zucchine_cotto_scamorza_teglia.paprikarecipes` | Versione teglia — zucchine, cotto e scamorza affumicata (bianca) |
| `patate_rosmarino_teglia.paprikarecipes` | Versione teglia — patate e rosmarino (bianca) |
| `nduja_olive_teglia.paprikarecipes` | Versione teglia — 'nduja e olive taggiasche (rossa) |
| `salamino_gorgonzola_teglia.paprikarecipes` | Versione teglia — salamino piccante e gorgonzola (rossa) |
