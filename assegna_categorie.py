#!/usr/bin/env python3
"""
assegna_categorie.py — Analizza le ricette Paprika 3 e assegna le categorie
automaticamente in base al nome e agli ingredienti.

Modalità:
  --full     : processa TUTTE le ricette (prima esecuzione o reset)
  --dry-run  : mostra cosa farebbe senza modificare il DB
  default    : processa solo le ricette nuove (non ancora processate)

Uso:
  python3 assegna_categorie.py [--full] [--dry-run]

Variabili ambiente:
  PAPRIKA_BASE_OVERRIDE  — path alternativo alla cartella Data di Paprika (sandbox)
"""

import sqlite3, json, os, sys, uuid
from pathlib import Path
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────────────
SCRIPT_DIR    = Path(__file__).parent
TRACKING_FILE = SCRIPT_DIR / 'categorie_tracciate.json'

_override    = os.environ.get('PAPRIKA_BASE_OVERRIDE')
PAPRIKA_BASE = Path(_override) if _override else \
               Path.home() / 'Library' / 'Group Containers' / \
               '72KVKW69K8.com.hindsightlabs.paprika.mac.v3' / 'Data'
PAPRIKA_DB   = PAPRIKA_BASE / 'Database' / 'Paprika.sqlite'

FULL_MODE = '--full' in sys.argv
DRY_RUN   = '--dry-run' in sys.argv

CATS_ESCLUSE = {'Test'}  # stessa logica di aggiorna_sito.py

# ── Nuove categorie da creare se non esistono ─────────────────────────────────
# Le categorie già esistenti in Paprika (Messinese, Ricette base, 30 minuti,
# Aiutacuochi, Pizze/focacce, Impasti, Pollo, Manzo, Maiale, Desserts, Pasqua,
# Pane) NON vanno qui — esistono già nel DB.
# Nota: 'Desserts' sarà eliminata dal DB — le ricette migrano in 'Dolce'.
# Nota: 'Pane' rimane nel DB ma le ricette pane migrano in 'Impasti per pizze...'
NUOVE_CATEGORIE = [
    # PORTATA
    'Antipasto', 'Primo', 'Secondo', 'Contorno', 'Dolce',
    'Zuppa, Minestra & Vellutate', 'Piatto unico', 'Sughi per primi',
    # PROTEINE
    'Pesce', 'Frutti di mare', 'Selvaggina e volatili',
    'Vegetariano', 'Vegano', 'Legumi',
    'Vitello', 'Verdure', 'Formaggio', 'Affettati',
    # INGREDIENTE SPECIFICO
    'Funghi', 'Patate',
    # TECNICA
    'Fritto', 'Lento e Brasato', 'Arrosto', 'Lesso e Bollito',
    'Gratinato', 'Cotto o saltato in padella', 'Al forno', 'Alla griglia & BBQ',
    # OCCASIONE
    'Natale', 'Internazionale',
    # MOMENTO PASTO
    'Pranzo', 'Cena', 'Colazione', 'Merenda',
    # PREPARAZIONI BASE
    'Salse, sughi e intingoli vari',
]

# ── Regole di assegnazione ────────────────────────────────────────────────────
# (categoria, name_keywords, ingr_keywords, name_exclude)
# Assegna la categoria se:
#   nome contiene ALMENO UNA name_keyword
#   OPPURE ingredienti contengono ALMENO UNA ingr_keyword
#   E nome NON contiene nessuna name_exclude
# Le categorie non sono esclusive: una ricetta può averne più di una.
RULES = [

    # ══ PORTATA ══════════════════════════════════════════════════════════════

    ('Dolce',
     ['brownie', 'crostata', 'cheese cake', 'cheesecake', 'crème brûlée',
      'creme brulée', 'crème brulèe', 'creme brule', 'creme brulèe', 'pandoro', 'schiacciata fiorentina', 'tarte tatin',
      'lebkuchen', 'pan dei morti', 'stelle alla gelatina', 'pignolata',
      'cannoli', 'iris fritte', 'flan al cioccolato', 'crema inglese',
      'crema pasticcera', 'crema al cioccolato', 'pasta frolla',
      'peanut butter biscuit', 'classico alberello', 'banana sour cream bread',
      'schiacciata toscana con li.co.li'],
     [],
     ['salata', 'scarola']),   # torta salata → non dolce

    ('Antipasto',
     ['hummus', 'guacamole', 'crudité', 'crudite', 'terrina', 'rillettes',
      'fonduta', 'insalata di polpo', 'winter crunch salad', 'crumble niçois',
      'crumble nicois', 'passatina', 'ristretto di zucca', 'uova in camicia',
      'peperoni arlecchino', 'peperoni ripieni al forno', 'carciofi alla messinese',
      'caponata di melanzane'],
     [],
     []),

    # soufflé salato = antipasto/secondo
    ('Antipasto',
     ['soufflé', 'souffle'],
     [],
     ['dolce']),

    ('Zuppa, Minestra & Vellutate',
     ['crema di asparagi', 'crema di gamberi', 'passatina di piselli',
      'ristretto di zucca', 'zuppa di lenticchie', 'zuppa di pomodoro',
      'brodo con royale', 'egyptian red lentil', 'red lentil soup',
      "mum's everyday red lentil", "mum's everyday",
      'macco', 'lentil soup'],
     [],
     []),

    ('Primo',
     ['spaghetti', 'rigatoni', 'orecchiette', 'linguine', 'tagliatelle',
      'lasagne', 'gnocchi', 'risotto',
      "pasta 'ncasciata", 'pasta alla norma', 'pasta con i broccoli',
      'pasta con la mollica', 'pasta con le sarde',
      'macco', 'ragout di pesce', 'rigatoni col sugo', 'rigatoni al ragout',
      'zuppa di', 'brodo con royale', 'crema di asparagi', 'crema di gamberi',
      'lentil soup', 'red lentil', 'everyday red lentil', 'zuppa di lenticchie',
      'egyptian red lentil', "mum's everyday"],
     [],
     # Escludi brodi/fondi base e ragù come preparazioni base
     ['brodo di', 'brodo universale', 'soffritto', 'roux',
      "sugo d'arrosto", 'sugo da roast', 'ragù napoletano', 'ragù di carne',
      'fondo di', 'ragù alla messinese']),

    ('Secondo',
     ['scaloppine', 'polpettone', 'braciole', 'falso magro', 'rotolo di vitello',
      'filetto di manzo', 'filetto di tonno', 'aggrassato',
      'carne murata', 'baccalà alla', 'stoccafisso', 'pescestocco',
      'pollo arrosto', 'pollo al vino', 'pollo alla mascalzona',
      'teglia di pollo', 'torta di pollo', 'tacchino ripieno',
      "jamie's christmas turkey", 'beef and ale stew', 'hash di manzo',
      'calamari ripieni', 'melanzane ripiene', 'pomodori ripieni', 'zucchine ripiene',
      'stinco alla', 'buddy\'s chicken', 'chicken fajitas',
      'merluzzo in crosta', 'ragout di pesce', 'crocchette di pesce'],
     [],
     ['impasto', 'soffritto', 'roux', 'sugo da', "sugo d'"]),

    # Roast beef e arrosto
    ('Secondo',
     ['roast beef', 'roast-beef', 'arrosto di manzo'],
     [],
     ['sugo da', "sugo d'"]),

    ('Contorno',
     ['patate al forno', 'patate novelle', 'patate croccanti', 'patate schiacciate',
      'patate alla parmentier', 'patate, pastinache', 'jacket potatoes',
      'pannocchie abbrustolite', 'verdure croccanti', 'spinaci cremosi',
      'piselli alla francese', 'purè di patate', 'purè di piselli',
      'winter crunch salad', 'zucchina lunga al sapore'],
     [],
     []),

    # Piatto unico: non esclusivo, si sovrappone con Primo/Secondo
    ('Piatto unico',
     ['paella', 'arancini di riso', 'beef and ale stew', "buddy's chicken fajitas",
      'chicken fajitas', 'falso magro', 'macco', 'orecchiette con polpette',
      "pasta 'ncasciata", 'teglia di pollo', 'torta di pollo',
      'torta pasqualina', 'torta salata alla scarola',
      'zuppa di lenticchie', 'egyptian red lentil', "mum's everyday"],
     [],
     ['impasto', 'soffritto']),

    ('Sughi per primi',
     ['ragù di carne', 'ragù napoletano', 'ragù alla messinese',
      'ragù di agnello', 'sugo alla', 'sugo di'],
     [],
     ['sugo da roast', "sugo d'arrosto", 'soffritto', 'brodo']),

    # Pane → migra in "Impasti per pizze, focacce & co." (cat già esistente)
    ('Impasti per pizze, focacce & co.',
     ['ciabatta', 'pane bianco', 'pane 3', 'pane con la macchina del pane',
      'pane bianco standard', 'schiacciata toscana', 'focaccia'],
     [],
     ['pizza', 'lingue di pizza', 'trancio', 'sfincione',
      'pitoni', 'alla fiorentina', 'con li.co.li']),

    # ══ PROTEINE / INGREDIENTE PRINCIPALE ════════════════════════════════════

    ('Pesce',
     ['baccalà', 'stoccafisso', 'pescestocco', 'filetto di tonno',
      'crocchette di pesce', 'ragout di pesce', 'rigatoni al ragout di pesce',
      'fondo di pesce', 'brodo di pesce', 'merluzzo in crosta',
      'pasta con le sarde'],
     ['pesce', 'tonno', 'baccalà', 'stoccafisso', 'merluzzo', 'salmone',
      'sogliola', 'trota', 'alici', 'acciughe'],
     ['caponata', 'focaccia messinese']),

    ('Frutti di mare',
     ['calamari ripieni', 'insalata di polpo', 'niuru de sicci', 'niuru',
      'spaghetti allo scoglio', 'passatina di piselli con gamberi',
      'crema di gamberi'],
     ['gamberi', 'gamberone', 'gamberoni', 'calamaro', 'calamari', 'polpo',
      'cozze', 'vongole', 'scoglio', 'aragosta', 'astice', 'seppia',
      'molluschi', 'crostacei'],
     []),

    ('Manzo',
     ['arrosto di manzo', 'roast beef', 'roast-beef', 'hash di manzo',
      'filetto di manzo', 'beef and ale stew', 'aggrassato',
      'rigatoni col sugo dell', 'braciole messinesi'],
     ['manzo', 'bistecca'],
     ['brodo di manzo', 'soffritto', 'sugo', 'vitello']),

    # Pollo: solo name-based per evitare falsi positivi da brodi/fondi
    ('Pollo',
     ['pollo arrosto', 'pollo al vino', 'pollo alla mascalzona', 'teglia di pollo',
      'torta di pollo', "buddy's chicken", 'chicken fajitas',
      'terrina di fegati di pollo'],
     [],
     ['brodo di pollo']),

    ('Maiale',
     ['stinco alla', 'polpettone alla messinese'],
     ['maiale', 'pancetta', 'lardo', 'salsiccia', 'prosciutto', 'guanciale',
      'speck', 'salame', 'lonza', 'chorizo'],
     # Escludi quando la proteina principale è un'altra
     ['brodo', 'soffritto',
      'filetto di manzo', 'pollo al vino', 'teglia di pollo',
      'tacchino', 'turkey', 'terrina', 'anatra', 'duck']),

    ('Selvaggina e volatili',
     ['anatra', 'duck', "terrina d'anatra", 'terrina di fegati', 'tacchino', 'turkey'],
     ['anatra', 'duck', 'tacchino'],
     []),

    ('Legumi',
     ['hummus', 'macco', 'zuppa di lenticchie', 'egyptian red lentil',
      'red lentil', 'everyday red lentil', "mum's everyday",
      'piselli alla francese', 'purè di piselli', 'passatina di piselli'],
     ['lenticchie', 'ceci', 'fagioli', 'fave'],
     []),

    ('Vitello',
     ['rotolo di vitello', 'brodo di vitello', 'scaloppine', 'falso magro'],
     [],
     # No ingr_kws: evita falsi positivi da ricette che usano vitello come ingrediente secondario
     []),

    ('Verdure',
     ['melanzane ripiene', 'melenzane alla parmigiana', 'caponata di melanzane',
      'peperoni arlecchino', 'peperoni ripieni al forno',
      'pomodori ripieni al forno', 'carciofi alla messinese',
      'zucchine ripiene', 'zucchina lunga al sapore'],
     [],
     []),

    # ══ TECNICA DI COTTURA ═══════════════════════════════════════════════════

    ('Fritto',
     ['iris fritte', 'pignolata alla messinese', 'pitoni fritti',
      'pizza fritta', 'crocchette di pesce'],
     [],
     []),

    ('Lento e Brasato',
     ['aggrassato', 'beef and ale stew', 'carne murata', 'falso magro',
      'ragù napoletano', 'ragù di carne', 'ragù alla messinese', 'stinco alla',
      'arrosto di manzo'],
     [],
     ['impasto', 'soffritto', 'sugo da', "sugo d'"]),

    ('Arrosto',
     ['arrosto di manzo', 'roast beef', 'roast-beef', 'pollo arrosto',
      'patate novelle arrosto', 'patate croccanti', 'patate al forno',
      'patate, pastinache', 'patate alla parmentier', 'jacket potatoes',
      "jamie's christmas turkey", 'tacchino ripieno', 'rotolo di vitello',
      'falso magro', 'carne murata', 'pannocchie abbrustolite'],
     [],
     ['impasto', 'soffritto', 'sugo da', "sugo d'"]),

    ('Lesso e Bollito',
     ['insalata di polpo', 'macco', 'uova in camicia'],
     [],
     []),

    ('Gratinato',
     ['carciofi alla messinese', 'calamari ripieni', 'melanzane ripiene',
      'melenzane alla parmigiana', 'peperoni arlecchino al gratin',
      'peperoni ripieni al forno', 'pomodori ripieni al forno',
      'zucchine ripiene'],
     [],
     []),

    ('Cotto o saltato in padella',
     ['filetto di tonno in padella', 'hash di manzo', 'pollo alla mascalzona',
      'scaloppine', 'spinaci cremosi', 'piselli alla francese'],
     [],
     []),

    # ══ OCCASIONE ════════════════════════════════════════════════════════════

    ('Natale',
     ['natale', 'natalizia', 'natalizie', 'christmas',
      'classico alberello', 'lebkuchen', 'stelle alla gelatina',
      'brodo con royale', 'crostata di natale', 'crema inglese di natale',
      'salse di mele di natale', 'pitoni alla messinese di natale', 'pandoro',
      'pignolata alla messinese'],
     [],
     []),

    # Pan dei Morti = Ognissanti, non Natale → rimosso da Natale

    ('Internazionale',
     ['banana sour cream bread', 'beef and ale stew', "buddy's chicken fajitas",
      'chicken fajitas', 'brownie', 'cheese cake', 'cheesecake',
      'crumble niçois', 'crumble nicois', 'duck rillettes',
      'egyptian red lentil', 'guacamole', 'hummus', 'jacket potatoes',
      "jamie's christmas turkey", 'lebkuchen', "mum's everyday",
      'paella', 'peanut butter biscuit', 'red lentil soup',
      'winter crunch salad', 'yorkshire pudding', 'crème brulèe', 'creme brule',
      'soufflé', 'souffle', 'terrina'],
     [],
     # Evita falsi positivi: soufflé e terrina italiane non sono "internazionali"
     # ma per ora le includiamo — l'utente può correggere
     []),

    # ══ MOMENTO PASTO ════════════════════════════════════════════════════════

    ('Colazione',
     ['banana sour cream bread', 'peanut butter biscuit', 'crèpes', 'crepes',
      'schiacciata alla fiorentina', 'schiacciata fiorentina'],
     [],
     ['impasto indiretto', 'impasto diretto']),  # solo le schiacciata-dolce, non gli impasti

    ('Merenda',
     ['brownie', 'cannoli alla siciliana', 'cheese cake', 'cheesecake',
      'crostata di frutta', 'pan dei morti', 'peanut butter biscuit',
      'schiacciata alla fiorentina', 'schiacciata fiorentina',
      'flan al cioccolato', 'tarte tatin'],
     [],
     []),

    # Pranzo: pasta, zuppe, piatti veloci e informali
    ('Pranzo',
     ['spaghetti', 'rigatoni', 'orecchiette', 'pasta alla norma',
      "pasta 'ncasciata", 'pasta con i broccoli', 'pasta con la mollica',
      'pasta con le sarde', 'rigatoni col sugo', 'rigatoni al ragout',
      'macco', 'zuppa di lenticchie', 'zuppa di pomodoro',
      'hash di manzo', 'carne murata', 'egyptian red lentil', 'red lentil soup',
      "mum's everyday", 'crema di asparagi'],
     [],
     ['brodo di', 'brodo universale', 'soffritto', 'impasto', 'roux']),

    # ══ NUOVE TECNICHE & PROTEINE ════════════════════════════════════════════

    ('Al forno',
     ['al forno', 'patate al forno', 'patate novelle arrosto'],
     [],
     ['soffritto', 'impasto', 'sugo da', "sugo d'"]),

    ('Alla griglia & BBQ',
     ['alla griglia', 'bbq', 'grigliata', 'pannocchie abbrustolite'],
     [],
     []),

    ('Formaggio',
     ['fonduta', 'au fromage', 'fromage', 'soufflé classico al formaggio'],
     [],
     []),

    ('Affettati',
     ['rillettes'],
     [],
     []),

    ('Funghi',
     ['trifolat', 'alla boscaiola', 'ai funghi', 'con funghi'],
     ['porcini', 'funghi', 'champignon', 'shiitake', 'cremini', 'pleurotus'],
     ['soffritto', 'impasto']),

    ('Patate',
     ['patate', 'jacket potatoes', 'gattò di patate'],
     [],
     ['impasto', 'soffritto']),

    ('Salse, sughi e intingoli vari',
     ['salsa ', 'salse per', 'soffritto', "sugo d'arrosto", 'sugo da roast',
      'roux', 'pangrattato', 'fondo di'],
     [],
     []),

    # Cena: secondi elaborati, piatti da occasione
    ('Cena',
     ['aggrassato', 'arrosto di manzo', 'beef and ale stew',
      'duck rillettes', 'falso magro', 'filetto di manzo', 'filetto di tonno',
      'fonduta', "jamie's christmas turkey", 'pollo arrosto', 'pollo al vino',
      'roast beef', 'roast-beef', 'rotolo di vitello', 'stinco alla',
      'tacchino ripieno', "terrina d'anatra", 'terrina di fegati',
      'torta di pollo', 'paella', 'calamari ripieni', 'baccalà alla',
      'stoccafisso', 'pescestocco'],
     [],
     ['impasto', 'brodo di', 'soffritto', 'sugo da', "sugo d'"]),
]

# ── Override vegetariano: ricette con ingredienti facoltativi di carne/pesce ──
# Ricette che il sistema classifica come non-veg ma che per scelta sono veg.
VEGETARIANO_FORCE = {
    'caponata di melanzane',  # alici elencate come "aggiunte non usate"
}

# ── Rilevamento Vegetariano/Vegano (basato su ingredienti) ────────────────────
CARNE_KW = [
    'manzo', 'vitello', 'maiale', 'pollo', 'anatra', 'duck', 'tacchino', 'turkey',
    'cinghiale', 'coniglio', 'lepre', 'gamberi', 'gamberone', 'calamaro', 'calamari',
    'polpo', 'vongole', 'cozze', 'tonno', 'merluzzo', 'baccalà', 'stoccafisso',
    'salmone', 'pesce', 'carne', 'prosciutto', 'salsiccia', 'pancetta', 'lardo',
    'guanciale', 'speck', 'salame', 'bresaola', 'mortadella', 'bistecca', 'braciole',
    'chorizo', 'alici', 'acciughe', 'sogliola', 'trota', 'lonza',
    'fegato', 'fegatini', 'rognone', 'carne tritata', 'carne macinata',
    # Parole nel NOME che indicano carne
    'ragù', 'ragu', 'agglassato', 'aggrassato', 'polpett',
    # Termini dialettali siciliani
    'sicci',  # seppia (spaghetti o' niuru de sicci)
    # English
    'beef', 'chicken', 'pork', 'lamb', 'veal', 'bacon', 'ham', 'sausage',
    'duck', 'turkey', 'anchovy', 'tuna', 'salmon', 'shrimp', 'prawn',
    'stewing beef', 'diced beef', 'ground beef',
]
LATTICINI_KW = [
    'burro', 'latte', 'panna', 'formaggio', 'mozzarella', 'fontina', 'groviera',
    'pecorino', 'parmigiano', 'ricotta', 'gorgonzola', 'philadelphia', 'stracchino',
    'scamorza', 'stracciatella', 'caciocavallo', 'uova', 'uovo', 'tuorli', 'albumi',
    'yogurt', 'cream', 'milk', 'butter', 'cheese',
]

NOME_NON_VEGETARIANO = CARNE_KW


def _match(testo, keywords):
    """True se testo (lowercase) contiene almeno una keyword."""
    t = testo.lower()
    return any(k in t for k in keywords)


def is_vegetariano(nome, ingr):
    """True se nessun ingrediente carnivoro nel nome o negli ingredienti."""
    return not _match(nome + ' ' + ingr, CARNE_KW)


def is_vegano(nome, ingr):
    """True se vegetariano E senza latticini/uova."""
    return is_vegetariano(nome, ingr) and not _match(ingr, LATTICINI_KW)


def calcola_categorie(nome, ingr):
    """Restituisce il set di categorie da assegnare alla ricetta."""
    cats = set()
    n = nome.lower()
    i_text = (ingr or '').lower()

    for (cat, name_kws, ingr_kws, name_excl) in RULES:
        if name_excl and _match(n, name_excl):
            continue
        if _match(n, name_kws) or _match(i_text, ingr_kws):
            cats.add(cat)

    if is_vegano(n, i_text):
        cats.add('Vegano')
        cats.add('Vegetariano')
    elif is_vegetariano(n, i_text) or n in VEGETARIANO_FORCE:
        cats.add('Vegetariano')

    return cats


# ── Lettura/scrittura tracking ────────────────────────────────────────────────
def load_tracking():
    if TRACKING_FILE.exists():
        with open(TRACKING_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'version': 1, 'last_run_full': None, 'processed_uids': []}


def save_tracking(data):
    with open(TRACKING_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print(f"🏷  assegna_categorie.py — modalità: {'FULL' if FULL_MODE else 'INCREMENTALE'}"
          f"{' (DRY-RUN)' if DRY_RUN else ''}")

    tracking = load_tracking()
    processed_set = set(tracking.get('processed_uids', []))

    # Apri DB in scrittura (non read-only)
    con = sqlite3.connect(str(PAPRIKA_DB))
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA journal_mode=WAL')
    cur = con.cursor()

    # ── 1. Leggi tutte le categorie esistenti ─────────────────────────────────
    existing_cats = {}  # name → Z_PK
    for row in cur.execute('SELECT Z_PK, ZNAME FROM ZRECIPECATEGORY').fetchall():
        existing_cats[row['ZNAME']] = row['Z_PK']

    # ── 2. Crea categorie mancanti ────────────────────────────────────────────
    max_pk = max(existing_cats.values()) if existing_cats else 0
    max_order = cur.execute('SELECT MAX(ZORDERFLAG) FROM ZRECIPECATEGORY').fetchone()[0] or 0

    for cat_name in NUOVE_CATEGORIE:
        if cat_name in existing_cats or cat_name in CATS_ESCLUSE:
            continue
        max_pk += 1
        max_order += 1
        cat_uid = str(uuid.uuid4()).upper()
        if not DRY_RUN:
            cur.execute(
                'INSERT INTO ZRECIPECATEGORY (Z_PK, Z_ENT, Z_OPT, ZISSYNCED, ZORDERFLAG, ZPARENT, ZNAME, ZSTATUS, ZUID) '
                'VALUES (?, 13, 1, 1, ?, NULL, ?, ?, ?)',
                (max_pk, max_order, cat_name, 'unmodified', cat_uid)
            )
            # Aggiorna il contatore PK nella tabella di metadata CoreData
            cur.execute(
                'UPDATE Z_PRIMARYKEY SET Z_MAX = ? WHERE Z_NAME = ?',
                (max_pk, 'RecipeCategory')
            )
            con.commit()
        existing_cats[cat_name] = max_pk
        print(f"   ✚ Creata categoria: {cat_name} (PK={max_pk})")

    # ── 3. Leggi ricette da processare ────────────────────────────────────────
    query = '''
        SELECT r.Z_PK, r.ZUID, r.ZNAME, r.ZINGREDIENTS,
               GROUP_CONCAT(c.ZNAME, '|||') AS cats
        FROM ZRECIPE r
        LEFT JOIN Z_12CATEGORIES j ON j.Z_12RECIPES = r.Z_PK
        LEFT JOIN ZRECIPECATEGORY c ON c.Z_PK = j.Z_13CATEGORIES
        WHERE r.ZINTRASH = 0 OR r.ZINTRASH IS NULL
        GROUP BY r.Z_PK
        ORDER BY r.ZNAME COLLATE NOCASE
    '''
    all_recipes = cur.execute(query).fetchall()

    if FULL_MODE:
        to_process = all_recipes
        print(f"   {len(to_process)} ricette da analizzare (FULL)")
    else:
        to_process = [r for r in all_recipes if r['ZUID'] not in processed_set]
        print(f"   {len(to_process)} ricette nuove da analizzare (su {len(all_recipes)} totali)")

    # ── 4. Assegna categorie ──────────────────────────────────────────────────
    n_assegnazioni = 0
    nuovi_processed = []

    for r in to_process:
        uid   = r['ZUID'] or ''
        nome  = r['ZNAME'] or ''
        ingr  = r['ZINGREDIENTS'] or ''
        r_pk  = r['Z_PK']

        # Categorie già assegnate
        cats_attuali = set(
            c.strip() for c in (r['cats'] or '').split('|||')
            if c.strip() and c.strip() not in CATS_ESCLUSE
        )

        # Categorie da aggiungere secondo le regole
        cats_target = calcola_categorie(nome, ingr)
        cats_nuove  = cats_target - cats_attuali

        if cats_nuove:
            print(f"   📌 {nome}")
            for cat in sorted(cats_nuove):
                cat_pk = existing_cats.get(cat)
                if cat_pk is None:
                    print(f"      ⚠️  categoria '{cat}' non trovata nel DB")
                    continue
                print(f"      + {cat}")
                if not DRY_RUN:
                    # Evita duplicati nella junction table
                    exists = cur.execute(
                        'SELECT 1 FROM Z_12CATEGORIES WHERE Z_12RECIPES=? AND Z_13CATEGORIES=?',
                        (r_pk, cat_pk)
                    ).fetchone()
                    if not exists:
                        cur.execute(
                            'INSERT INTO Z_12CATEGORIES (Z_12RECIPES, Z_13CATEGORIES) VALUES (?, ?)',
                            (r_pk, cat_pk)
                        )
                n_assegnazioni += 1

        nuovi_processed.append(uid)

    if not DRY_RUN:
        con.commit()

    con.close()

    # ── 5. Aggiorna tracking ──────────────────────────────────────────────────
    if not DRY_RUN:
        if FULL_MODE:
            tracking['last_run_full'] = datetime.now().isoformat()
            tracking['processed_uids'] = [r['ZUID'] for r in all_recipes if r['ZUID']]
        else:
            seen = set(tracking['processed_uids'])
            for uid in nuovi_processed:
                if uid and uid not in seen:
                    tracking['processed_uids'].append(uid)
                    seen.add(uid)
        save_tracking(tracking)

    print(f"   ✅ {n_assegnazioni} assegnazioni {'(simulazione)' if DRY_RUN else 'applicate'}"
          f" su {len(to_process)} ricette analizzate")


if __name__ == '__main__':
    main()
