#!/usr/bin/env python3
"""
fix_recipe_links.py — sistema cluster-based per collegare ricette correlate in Paprika 3.

FASE 1 – Exact matching:
  - ZINGREDIENTS:     riga per riga — se la riga corrisponde a un nome ricetta → [recipe:Nome]
  - ZDIRECTIONS / ZDESCRIPTIONTEXT / ZNOTES: inline — cerca nomi ricetta nel testo

FASE 2 – Cluster-based:
  Aggiunge sezioni con link tematici nei campi appropriati:
  → ZINGREDIENTS  ricette "necessarie":      brodo, soffritto, creme pasticcere
  → ZNOTES        ricette di accompagnamento: salse, patate, ragù, pizza cross-link

MODALITÀ:
  python3 fix_recipe_links.py                      → dry-run (nessuna modifica)
  python3 fix_recipe_links.py --apply              → scrive nel DB + backup
  python3 fix_recipe_links.py --only-clusters      → solo cluster, no exact matching
  python3 fix_recipe_links.py --only-clusters --apply
  (--only-fuzzy accettato come alias di --only-clusters per compatibilità)
"""

import sqlite3, sys, re, unicodedata, shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import os

# ── Percorso DB ──────────────────────────────────────────────────────────────
PAPRIKA_BASE = Path.home() / 'Library' / 'Group Containers' / \
               '72KVKW69K8.com.hindsightlabs.paprika.mac.v3' / 'Data'
if 'PAPRIKA_BASE_OVERRIDE' in os.environ:
    PAPRIKA_BASE = Path(os.environ['PAPRIKA_BASE_OVERRIDE'])
DB_PATH    = PAPRIKA_BASE / 'Database' / 'Paprika.sqlite'
BACKUP_DIR = Path(__file__).parent / 'Backup Paprika'

APPLY        = '--apply'         in sys.argv
ONLY_CLUSTER = '--only-clusters' in sys.argv or '--only-fuzzy' in sys.argv


# ══════════════════════════════════════════════════════════════════════════════
# NORMALIZZAZIONE
# ══════════════════════════════════════════════════════════════════════════════
def norm(s: str) -> str:
    """Minuscolo, senza accenti, apostrofi uniformi → stringa confrontabile."""
    if not s:
        return ''
    s = s.replace('’', "'").replace('‘', "'").replace('—', '-')
    s = unicodedata.normalize('NFD', s.lower())
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn')


# ══════════════════════════════════════════════════════════════════════════════
# FASE 1 – EXACT MATCHING
# ══════════════════════════════════════════════════════════════════════════════
def fix_ingredienti(text: str, nome_map: dict) -> tuple:
    """
    Per ogni riga: se la riga (stripped) corrisponde esattamente al nome
    normalizzato di una ricetta, sostituisce con [recipe:NomeEsatto].
    Salta righe già taggate o header (== ... ==).
    """
    if not text:
        return text, []
    lines, result, changes = text.split('\n'), [], []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('==') or '[recipe:' in stripped:
            result.append(line)
            continue
        n = norm(stripped)
        if n in nome_map:
            tag = f"[recipe:{nome_map[n]}]"
            changes.append((stripped, tag))
            result.append(tag)
        else:
            result.append(line)
    return '\n'.join(result), changes


def fix_directions(text: str, nomi_ordinati: list, self_nome: str = '') -> tuple:
    """
    Cerca nel testo i nomi di ricette (>= 6 char) e sostituisce
    inline con [recipe:NomeEsatto]. Non tocca testo già taggato.
    """
    if not text:
        return text, []
    result, changes = text, []
    self_n = norm(self_nome)
    for nome_esatto, norm_nome in nomi_ordinati:
        if len(nome_esatto) < 6 or norm_nome == self_n:
            continue
        tag = f"[recipe:{nome_esatto}]"
        if tag in result:
            continue
        escaped = re.escape(nome_esatto)
        pattern = r'(?<![A-Za-zÀ-ÿ\d])' + escaped + r'(?![A-Za-zÀ-ÿ\d])'
        count = [0]
        def repl(m, _tag=tag, _count=count):
            _count[0] += 1
            return _tag
        new_result = re.sub(pattern, repl, result, flags=re.IGNORECASE)
        if count[0]:
            changes.append((nome_esatto, tag, count[0]))
            result = new_result
    return result, changes


# ══════════════════════════════════════════════════════════════════════════════
# FASE 2 – CLUSTER DEFINITIONS
# ══════════════════════════════════════════════════════════════════════════════

# ── Rilevamento proteina ─────────────────────────────────────────────────────
# Ordine importante: crostacei/molluschi/pesce PRIMA di carne, per evitare
# che "brodo di crostacei" in una ricetta di mare venga classificato come 'neutro'.
PROTEIN_DETECT = [
    ('crostacei', ['crostacei', 'gambero', 'gamberi', 'scampi', 'aragosta',
                   'granchio', 'astice', 'mazzancolla', 'cicala di mare']),
    ('molluschi', ['molluschi', 'cozze', 'vongole', 'polpo', 'calamaro',
                   'calamari', 'seppie', 'seppia', 'totano']),
    ('pesce',     ['pesce', 'baccala', 'merluzzo', 'salmone', 'tonno', 'orata',
                   'spigola', 'branzino', 'sogliola', 'trota', 'sardine',
                   'acciughe', 'alici', 'dentice', 'ricciola', 'sgombro']),
    ('vitello',   ['vitello']),
    ('pollo',     ['pollo', 'gallina', 'tacchino', 'anatra', 'oca', 'quaglia',
                   'cappone', 'faraona']),
    ('manzo',     ['manzo', 'bue', 'bovino', 'bistecca', 'hamburger',
                   'roastbeef', 'roast-beef', 'roast beef']),
    ('maiale',    ['maiale', 'suino', 'pancetta', 'guanciale', 'lardo',
                   'prosciutto', 'salsiccia', 'cotechino', 'porchetta',
                   'costine', 'braciola', 'capocollo', 'lonza']),
    ('agnello',   ['agnello', 'capretto', 'abbacchio']),
]

def detect_protein(nome: str, ingr: str) -> str:
    t = norm(nome + ' ' + (ingr or ''))
    for protein, keywords in PROTEIN_DETECT:
        if any(kw in t for kw in keywords):
            return protein
    return 'neutro'


# ── Cluster 1: BRODO → ZINGREDIENTS ─────────────────────────────────────────
BRODO_TRIGGER = 'brodo'   # cercato in full_text normalizzato

BRODO_BY_PROTEIN = {
    'pollo':     ['Brodo di pollo', 'Brodo universale'],
    'manzo':     ['Brodo di manzo', 'Brodo universale'],
    'vitello':   ['Brodo di vitello', 'Brodo di manzo', 'Brodo universale'],
    'maiale':    ['Brodo universale'],
    'agnello':   ['Brodo universale'],
    'pesce':     ['Brodo di pesce', 'Fondo di pesce'],
    'crostacei': ['Brodo di crostacei'],
    'molluschi': ['Brodo di pesce'],
    'neutro':    ['Brodo di verdure'],
}
BRODO_RICETTE = {r for rs in BRODO_BY_PROTEIN.values() for r in rs}


# ── Cluster 2: SOFFRITTO → ZINGREDIENTS ─────────────────────────────────────
SOFFRITTO_TRIGGER = 'soffritto'

SOFFRITTO_BASE = [
    'Soffritto all’italiana',
    'Soffritto di cipolle',
    'Soffritto di porri',
    'Soffritto di scalogni',
]
SOFFRITTO_PANCETTA       = 'Soffritto all’italiana con pancetta'
SOFFRITTO_CARNE_PROTEINS = {'pollo', 'manzo', 'vitello', 'maiale', 'agnello'}
SOFFRITTO_RICETTE        = set(SOFFRITTO_BASE) | {SOFFRITTO_PANCETTA}


# ── Cluster 3: CREME → ZINGREDIENTS ─────────────────────────────────────────
CREMA_CLUSTERS = {
    'crema pasticcera': ['Crema Pasticcera', 'Crema Pasticcera al Cioccolato'],
    'crema inglese':    ['Crema Inglese', 'Crema Inglese di Natale',
                         'Crema Inglese di Natale al Cioccolato'],
}
CREMA_RICETTE = {r for rs in CREMA_CLUSTERS.values() for r in rs}


# ── Cluster 4: PATATE → ZNOTES ───────────────────────────────────────────────
PATATE_ALL = [
    'Patate Croccanti',
    'Patate Novelle Arrosto',
    'Patate Schiacciate',
    'Patate al Forno',
    'Patate alla parmentier',
    'Patate, Pastinache e Carote arrostite',
    'Puré Di Patate',
]
# Ricette che SONO di patate ma non hanno "patate" nel nome normalizzato
PATATE_RICETTE_EXTRA = {'jacket potatoes'}
# Tipi di ricette da escludere dai suggerimenti patate (per nome)
PATATE_EXCLUDE_FROM_NOME = ['brodo', 'roux', 'crema inglese', 'crema pasticcera',
                             'gelatina', 'torta', 'crostata', 'biscotti', 'dolce',
                             'sfoglia', 'frolla', 'chantilly']
PATATE_ARROSTO_LIST = [
    'Patate Novelle Arrosto',
    'Patate al Forno',
    'Patate, Pastinache e Carote arrostite',
    'Patate Croccanti',
]
PATATE_PURE_LIST = [
    'Puré Di Patate',
    'Patate Schiacciate',
    'Patate alla parmentier',
]
PATATE_RICETTE = set(PATATE_ALL)


# ── Cluster 5: SALSE → ZNOTES ────────────────────────────────────────────────
SALSA_TARTARA_NOME     = 'Salsa Tartara'
SALSA_TARTARA_TRIGGERS = [
    'fritto', 'fritta', 'fritti', 'fritte', 'frittura',
    'grigliato', 'grigliata', 'alla griglia',
    'bollito', 'bollita', 'lesso', 'lessa',
    'tartare', 'impanato', 'impanata',
]
# Esclude ricette dove sarebbe fuori luogo (pasta/risotto/dolci/zuppe/lievitati)
SALSA_TARTARA_EXCLUDE  = [
    'pasta', 'risotto', 'dessert', 'dolce', 'torta', 'pizza',
    'focaccia', 'sfincione', 'zuppa', 'minestra',
]

SALSA_MENTA_NOME     = 'Salsa di Menta'
SALSA_MENTA_TRIGGERS = ['agnello', 'capretto', 'abbacchio']

SALSE_RICETTE = {SALSA_TARTARA_NOME, SALSA_MENTA_NOME}


# ── Cluster 6: RAGÙ / SUGO → ZNOTES ─────────────────────────────────────────
RAGU_TRIGGERS         = ['ragu', 'ragù']   # norm() rimuove accenti → 'ragu' copre entrambi
SUGO_ARROSTO_TRIGGERS = [
    "sugo d’arrosto", "sugo d'arrosto",
    'fondo di cottura', 'sugo di cottura',
]

RAGU_SUGGESTIONS  = ['Ragù di Carne']
SUGO_SUGGESTIONS  = ["Sugo d'arrosto", 'Sugo da Roast-Beef ultra rapido']
RAGU_RICETTE      = set(RAGU_SUGGESTIONS) | set(SUGO_SUGGESTIONS)
RAGU_PROTEINS_OK  = {'pollo', 'manzo', 'vitello', 'maiale', 'agnello'}


# ── Cluster 7: PIZZA cross-link → ZNOTES ─────────────────────────────────────
PIZZA_KEYWORDS   = {
    'pizza', 'focaccia', 'sfincione', 'schiacciata', 'ciabatta',
    'trancio', 'lingue di pizza',
}
IMPASTO_KEYWORDS = {'impasto', 'biga', 'poolish', 'licoli', 'li.co.li', 'lievito madre'}

def is_pizza_recipe(nome: str) -> bool:
    n = nome.lower()
    return any(kw in n for kw in PIZZA_KEYWORDS)

def is_impasto_recipe(nome: str) -> bool:
    n = nome.lower()
    return any(kw in n for kw in IMPASTO_KEYWORDS)

def get_pizza_family(nome: str):
    if not is_pizza_recipe(nome):
        return None
    if ' — ' in nome:
        return nome.split(' — ')[0].strip()
    if ' - ' in nome:
        return nome.split(' - ')[0].strip()
    return nome

def build_pizza_index(all_recipes: list) -> dict:
    """
    Restituisce: family → {'impasti': [nome, ...], 'farciture': [nome, ...]}
    Solo famiglie che hanno ALMENO un impasto E una farcitura.
    """
    raw = defaultdict(lambda: {'impasti': [], 'farciture': []})
    for nome, _ in all_recipes:
        family = get_pizza_family(nome)
        if family is None:
            continue
        if is_impasto_recipe(nome):
            raw[family]['impasti'].append(nome)
        else:
            raw[family]['farciture'].append(nome)
    # Tieni solo le famiglie che hanno almeno un impasto E almeno una farcitura
    return {f: d for f, d in raw.items()
            if d['impasti'] and d['farciture']}


# ══════════════════════════════════════════════════════════════════════════════
# HELPER: aggiungi sezione a un testo
# ══════════════════════════════════════════════════════════════════════════════
def aggiungi_sezione(testo: str, header: str, links: list) -> tuple:
    """
    Aggiunge links sotto header.
    - Se header NON esiste: crea sezione in fondo al testo.
    - Se header ESISTE già: aggiunge solo i link mancanti in fondo alla sezione.
    Restituisce (nuovo_testo, link_effettivamente_aggiunti).
    """
    if not links:
        return testo, []
    nuovi = [l for l in links if f"[recipe:{l}]" not in testo]
    if not nuovi:
        return testo, []

    nuovi_lines = '\n'.join(f"[recipe:{l}]" for l in nuovi)

    if header in testo:
        # Trova la fine della sezione header e inserisci dopo l'ultima riga di quella sezione
        idx     = testo.find(header)
        eol     = testo.find('\n', idx)
        if eol == -1:
            return testo + '\n' + nuovi_lines, nuovi
        # Trova il prossimo header (== ... ==) o fine stringa
        rest = testo[eol + 1:]
        m    = re.search(r'\n== ', rest)
        if m:
            insert_at = eol + 1 + m.start()
            return (testo[:insert_at] + nuovi_lines + '\n' + testo[insert_at:]), nuovi
        else:
            return testo.rstrip() + '\n' + nuovi_lines, nuovi
    else:
        sezione = header + '\n\n' + nuovi_lines
        base    = testo.rstrip()
        return (base + '\n' + sezione if base else sezione), nuovi


# ══════════════════════════════════════════════════════════════════════════════
# CLUSTER – ZINGREDIENTS  (brodo, soffritto, creme)
# ══════════════════════════════════════════════════════════════════════════════
def apply_clusters_ingr(nome: str, ingr: str, full_text: str, protein: str) -> tuple:
    new_ingr = ingr or ''
    logs     = []
    nome_n   = norm(nome)
    full_n   = norm(full_text)

    # ── Brodo ────────────────────────────────────────────────────────────────
    # Escludi ricette che SONO brodi (per nome o per appartenenza a BRODO_RICETTE)
    if 'brodo' not in nome_n and nome_n not in {norm(b) for b in BRODO_RICETTE}:
        if BRODO_TRIGGER in full_n:
            suggeriti = BRODO_BY_PROTEIN.get(protein, BRODO_BY_PROTEIN['neutro'])
            new_ingr, aggiunti = aggiungi_sezione(new_ingr, '== 🍲 Brodi ==', suggeriti)
            if aggiunti:
                logs.append(f"   [brodo/{protein}] → {aggiunti}")

    # ── Soffritto ────────────────────────────────────────────────────────────
    if nome_n not in {norm(s) for s in SOFFRITTO_RICETTE}:
        if SOFFRITTO_TRIGGER in full_n:
            base = list(SOFFRITTO_BASE)
            if protein in SOFFRITTO_CARNE_PROTEINS:
                base.append(SOFFRITTO_PANCETTA)
            new_ingr, aggiunti = aggiungi_sezione(new_ingr, '== 🧅 Soffritti ==', base)
            if aggiunti:
                logs.append(f"   [soffritto/{protein}] → {aggiunti}")

    # ── Creme pasticcere ─────────────────────────────────────────────────────
    if nome_n not in {norm(c) for c in CREMA_RICETTE}:
        for trigger, suggestions in CREMA_CLUSTERS.items():
            if trigger in full_n:
                new_ingr, aggiunti = aggiungi_sezione(new_ingr, '== 🍮 Creme ==', suggestions)
                if aggiunti:
                    logs.append(f"   [crema/{trigger}] → {aggiunti}")

    return new_ingr, logs


# ══════════════════════════════════════════════════════════════════════════════
# CLUSTER – ZNOTES  (patate, salse, ragù, pizza)
# ══════════════════════════════════════════════════════════════════════════════
def apply_clusters_note(
    nome: str,
    notes: str,
    full_text: str,
    protein: str,
    pizza_index: dict,
) -> tuple:
    new_notes = notes or ''
    logs      = []
    nome_n    = norm(nome)
    full_n    = norm(full_text)

    # ── Patate ───────────────────────────────────────────────────────────────
    # Escludi: ricette che SONO di patate, ricette di brodo/roux/dolci/pastry
    patate_self   = nome_n in {norm(p) for p in PATATE_RICETTE} or nome_n in PATATE_RICETTE_EXTRA
    patate_exclude = any(ex in nome_n for ex in PATATE_EXCLUDE_FROM_NOME)
    if not patate_self and not patate_exclude:
        if 'pata' in full_n:
            if any(t in full_n for t in ['arrosto', 'arrostit', 'roast']):
                suggeriti = PATATE_ARROSTO_LIST
            elif any(t in full_n for t in ['pure', 'puree', 'schiaccia', 'lessa', 'lessata']):
                suggeriti = PATATE_PURE_LIST
            else:
                # Controlla che 'patate' sia citato come accompagnamento,
                # non come ingrediente principale (evita ricette di patate che citano patate)
                suggeriti = PATATE_ALL
            new_notes, aggiunti = aggiungi_sezione(new_notes, '== 🥔 Contorni ==', suggeriti)
            if aggiunti:
                logs.append(f"   [patate] → {aggiunti}")

    # ── Salsa Tartara ────────────────────────────────────────────────────────
    if nome_n != norm(SALSA_TARTARA_NOME):
        # Verifica che non sia una ricetta di pasta/dolci/pizza (escludi)
        is_excluded = any(ex in full_n for ex in SALSA_TARTARA_EXCLUDE)
        # Usa word boundary per evitare che "fritto" in "soffritto" triggeri la salsa
        has_trigger = any(re.search(r'\b' + re.escape(t) + r'\b', full_n)
                          for t in SALSA_TARTARA_TRIGGERS)
        if not is_excluded and has_trigger:
            new_notes, aggiunti = aggiungi_sezione(new_notes, '== 🫙 Salse ==', [SALSA_TARTARA_NOME])
            if aggiunti:
                logs.append(f"   [salsa tartara]")

    # ── Salsa di Menta ───────────────────────────────────────────────────────
    if nome_n != norm(SALSA_MENTA_NOME):
        if any(t in full_n for t in SALSA_MENTA_TRIGGERS):
            new_notes, aggiunti = aggiungi_sezione(new_notes, '== 🫙 Salse ==', [SALSA_MENTA_NOME])
            if aggiunti:
                logs.append(f"   [salsa di menta]")

    # ── Ragù di Carne ────────────────────────────────────────────────────────
    # Escludi ricette che SONO ragù/sugo (per nome o per appartenenza a RAGU_RICETTE)
    if nome_n not in {norm(r) for r in RAGU_RICETTE} and 'ragu' not in nome_n:
        if protein in RAGU_PROTEINS_OK:
            # Trigger "ragù" → suggerisci Ragù di Carne
            if any(t in full_n for t in [norm(t) for t in RAGU_TRIGGERS]):
                new_notes, aggiunti = aggiungi_sezione(
                    new_notes, '== 🥘 Sughi ==', RAGU_SUGGESTIONS)
                if aggiunti:
                    logs.append(f"   [ragù] → {aggiunti}")
            # Trigger "sugo d'arrosto" → suggerisci sughi da cottura
            if any(norm(t) in full_n for t in SUGO_ARROSTO_TRIGGERS):
                new_notes, aggiunti = aggiungi_sezione(
                    new_notes, '== 🥘 Sughi ==', SUGO_SUGGESTIONS)
                if aggiunti:
                    logs.append(f"   [sugo d'arrosto] → {aggiunti}")

    # ── Pizza cross-link ─────────────────────────────────────────────────────
    family = get_pizza_family(nome)
    if family and family in pizza_index:
        fam = pizza_index[family]
        if is_impasto_recipe(nome):
            # Impasto → suggerisci farciture
            farciture = [n for n in fam['farciture'] if norm(n) != nome_n]
            new_notes, aggiunti = aggiungi_sezione(new_notes, '== 🎨 Varianti ==', farciture)
            if aggiunti:
                logs.append(f"   [pizza/farciture ×{len(aggiunti)}]")
        else:
            # Farcitura → suggerisci impasti
            impasti = [n for n in fam['impasti'] if norm(n) != nome_n]
            new_notes, aggiunti = aggiungi_sezione(new_notes, '== 🍕 Impasti ==', impasti)
            if aggiunti:
                logs.append(f"   [pizza/impasti ×{len(aggiunti)}]")

    return new_notes, logs


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    mode = '🔧 APPLY MODE' if APPLY else '🔍 DRY-RUN (nessuna modifica)'
    if ONLY_CLUSTER:
        mode += ' — solo cluster'
    print(f"{mode}")
    print(f"   DB: {DB_PATH}\n")

    con = sqlite3.connect(str(DB_PATH))
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cur.execute("SELECT ZUID, ZNAME FROM ZRECIPE WHERE (ZINTRASH=0 OR ZINTRASH IS NULL)")
    rows_nomi = cur.fetchall()

    nome_map = {norm(r['ZNAME']): r['ZNAME'] for r in rows_nomi}

    nomi_ordinati = sorted(
        [(r['ZNAME'], norm(r['ZNAME'])) for r in rows_nomi],
        key=lambda x: -len(x[0])
    )

    all_recipes  = [(r['ZNAME'], r['ZUID']) for r in rows_nomi]
    pizza_index  = build_pizza_index(all_recipes)

    print(f"   Famiglie pizza con impasti+farciture: {len(pizza_index)}")
    for fam in sorted(pizza_index):
        d = pizza_index[fam]
        print(f"     {fam}: {len(d['impasti'])} impasti, {len(d['farciture'])} varianti")
    print()

    cur.execute(
        "SELECT Z_PK, ZUID, ZNAME, ZINGREDIENTS, ZDIRECTIONS, "
        "ZDESCRIPTIONTEXT, ZNOTES "
        "FROM ZRECIPE WHERE (ZINTRASH=0 OR ZINTRASH IS NULL)"
    )
    ricette = cur.fetchall()

    modifiche   = []
    totale_link = 0

    for r in ricette:
        pk         = r['Z_PK']
        nome       = r['ZNAME']
        ingr_orig  = r['ZINGREDIENTS']     or ''
        dirs_orig  = r['ZDIRECTIONS']      or ''
        desc_orig  = r['ZDESCRIPTIONTEXT'] or ''
        notes_orig = r['ZNOTES']           or ''

        # ── Fase 1: exact matching ──────────────────────────────────────────
        if ONLY_CLUSTER:
            ingr_new = ingr_orig
            dirs_new = dirs_orig
            desc_new = desc_orig
            notes_new = notes_orig
            ingr_ch = dirs_ch = desc_ch = notes_ch = []
        else:
            ingr_new,  ingr_ch  = fix_ingredienti(ingr_orig, nome_map)
            dirs_new,  dirs_ch  = fix_directions(dirs_orig,  nomi_ordinati, nome)
            desc_new,  desc_ch  = fix_directions(desc_orig,  nomi_ordinati, nome)
            notes_new, notes_ch = fix_directions(notes_orig, nomi_ordinati, nome)

        # ── Fase 2: cluster-based ───────────────────────────────────────────
        protein  = detect_protein(nome, ingr_orig)
        full_txt = '\n'.join([ingr_new, dirs_new, desc_new, notes_new])

        ingr_new,  logs_ingr  = apply_clusters_ingr(
            nome, ingr_new, full_txt, protein)
        notes_new, logs_notes = apply_clusters_note(
            nome, notes_new, full_txt, protein, pizza_index)

        # ── Verifica modifiche ──────────────────────────────────────────────
        has_changes = (
            ingr_new  != ingr_orig  or
            dirs_new  != dirs_orig  or
            desc_new  != desc_orig  or
            notes_new != notes_orig
        )
        if not has_changes:
            continue

        n_exact   = len(ingr_ch) + sum(c for _, _, c in dirs_ch) + \
                    sum(c for _, _, c in desc_ch) + sum(c for _, _, c in notes_ch)
        n_cluster = len(logs_ingr) + len(logs_notes)
        totale_link += n_exact + n_cluster
        modifiche.append((pk, ingr_new, dirs_new, desc_new, notes_new))

        print(f"📖  {nome}  [{protein}]")
        for old, new in ingr_ch:
            print(f"   [ingr exact]  {repr(old)} → {repr(new)}")
        for n, tag, cnt in dirs_ch:
            print(f"   [dirs exact]  '{n}' ×{cnt}")
        for n, tag, cnt in desc_ch:
            print(f"   [desc exact]  '{n}' ×{cnt}")
        for n, tag, cnt in notes_ch:
            print(f"   [note exact]  '{n}' ×{cnt}")
        for l in logs_ingr:
            print(l)
        for l in logs_notes:
            print(l)
        print()

    # ── Riepilogo ─────────────────────────────────────────────────────────────
    sep = '─' * 52
    print(sep)
    print(f"Ricette da modificare : {len(modifiche)}")
    print(f"Modifiche totali      : {totale_link}")
    print(sep)

    if not APPLY:
        print("\n  Riesegui con --apply per scrivere le modifiche.")
        con.close()
        return

    # ── Backup ────────────────────────────────────────────────────────────────
    BACKUP_DIR.mkdir(exist_ok=True)
    ts     = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup = BACKUP_DIR / f'Paprika_pre_links_{ts}.sqlite'
    shutil.copy2(str(DB_PATH), str(backup))
    print(f"\n💾 Backup: {backup.name}")

    # ── Scrittura ─────────────────────────────────────────────────────────────
    for pk, ingr_new, dirs_new, desc_new, notes_new in modifiche:
        cur.execute(
            "UPDATE ZRECIPE SET ZINGREDIENTS=?, ZDIRECTIONS=?, "
            "ZDESCRIPTIONTEXT=?, ZNOTES=? WHERE Z_PK=?",
            (ingr_new, dirs_new, desc_new, notes_new, pk)
        )
    con.commit()
    print(f"✅ {len(modifiche)} ricette aggiornate nel DB.")
    print("   Riavvia Paprika per vedere le modifiche.")
    con.close()


if __name__ == '__main__':
    main()
