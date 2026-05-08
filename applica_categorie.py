#!/usr/bin/env python3
"""
applica_categorie.py — Applica il diff di categorie al DB Paprika 3.
Crea le nuove categorie, aggiunge le associazioni, rimuove Pane/Desserts.
"""

import sqlite3, uuid
from pathlib import Path

PAPRIKA_DB = Path.home() / 'Library' / 'Group Containers' / \
             '72KVKW69K8.com.hindsightlabs.paprika.mac.v3' / 'Data' / \
             'Database' / 'Paprika.sqlite'

# Mappa: nomi nel diff (vecchi widget) → nomi definitivi nel DB
CAT_RENAME = {
    'Zuppa e Minestra': 'Zuppa, Minestra & Vellutate',
    'Saltato in padella': 'Cotto o saltato in padella',
}

# Tutte le categorie da creare se non esistono già
NUOVE_CATEGORIE = [
    'Antipasto', 'Primo', 'Secondo', 'Contorno', 'Dolce',
    'Zuppa, Minestra & Vellutate', 'Piatto unico', 'Sughi per primi',
    'Pesce', 'Frutti di mare', 'Selvaggina e volatili',
    'Vegetariano', 'Vegano', 'Legumi',
    'Vitello', 'Verdure', 'Formaggio', 'Affettati',
    'Funghi', 'Patate',
    'Fritto', 'Lento e Brasato', 'Arrosto', 'Lesso e Bollito',
    'Gratinato', 'Cotto o saltato in padella', 'Al forno', 'Alla griglia & BBQ',
    'Natale', 'Internazionale',
    'Pranzo', 'Cena', 'Colazione', 'Merenda',
    'Salse, sughi e intingoli vari',
]

# AGGIUNGI: {pk: [cat, ...]} — categorie da aggiungere per ricetta
# Note: nomi già normalizzati (Zuppa e Minestra → Zuppa, Minestra & Vellutate ecc.)
AGGIUNGI = {
    682: ['Cena', 'Lento e Brasato', 'Manzo', 'Secondo'],
    677: ['Piatto unico'],
    704: ['Arrosto', 'Cena', 'Lento e Brasato', 'Secondo'],
    652: ['Cena', 'Pesce', 'Secondo'],
    797: ['Colazione', 'Dolce', 'Internazionale', 'Vegetariano'],
    644: ['Cena', 'Internazionale', 'Lento e Brasato', 'Manzo', 'Piatto unico', 'Secondo'],
    648: ['Manzo', 'Secondo'],
    726: ['Natale', 'Primo', 'Vegetariano', 'Zuppa, Minestra & Vellutate'],
    716: ['Frutti di mare', 'Vegano', 'Vegetariano'],
    715: ['Pesce'],
    717: ['Vegetariano'],
    714: ['Manzo'],
    784: ['Dolce', 'Internazionale', 'Merenda', 'Vegetariano'],
    805: ['Internazionale', 'Piatto unico', 'Secondo'],
    651: ['Cena', 'Frutti di mare', 'Gratinato', 'Secondo'],
    676: ['Dolce', 'Merenda', 'Vegetariano'],
    647: ['Antipasto', 'Vegetariano'],
    649: ['Antipasto', 'Gratinato', 'Vegetariano'],
    674: ['Arrosto', 'Lento e Brasato', 'Manzo', 'Pranzo', 'Secondo'],
    783: ['Dolce', 'Internazionale', 'Merenda', 'Vegetariano'],
    886: ['Impasti per pizze, focacce & co.', 'Vegano', 'Vegetariano'],
    731: ['Dolce', 'Natale', 'Vegetariano'],
    734: ['Dolce', 'Vegetariano'],
    771: ['Pranzo', 'Primo', 'Vegetariano', 'Zuppa, Minestra & Vellutate'],
    770: ['Frutti di mare', 'Primo', 'Zuppa, Minestra & Vellutate'],
    732: ['Dolce', 'Vegetariano'],
    777: ['Dolce', 'Natale', 'Vegetariano'],
    778: ['Dolce', 'Natale', 'Vegetariano'],
    733: ['Dolce', 'Vegetariano'],
    773: ['Dolce', 'Vegetariano'],
    791: ['Dolce', 'Vegetariano'],
    759: ['Fritto', 'Pesce', 'Secondo'],
    795: ['Dolce', 'Merenda', 'Vegano', 'Vegetariano'],
    776: ['Dolce', 'Natale', 'Vegano', 'Vegetariano'],
    786: ['Antipasto', 'Vegano', 'Vegetariano'],
    725: ['Antipasto', 'Internazionale', 'Vegetariano'],
    721: ['Colazione', 'Vegetariano'],
    665: ['Antipasto', 'Cena', 'Internazionale', 'Selvaggina e volatili'],
    801: ['Internazionale', 'Legumi', 'Piatto unico', 'Pranzo', 'Primo', 'Vegano', 'Vegetariano', 'Zuppa, Minestra & Vellutate'],
    802: ['Internazionale', 'Legumi', 'Piatto unico', 'Pranzo', 'Primo', 'Vegano', 'Vegetariano', 'Zuppa, Minestra & Vellutate'],
    810: ['Arrosto', 'Cena', 'Lento e Brasato', 'Maiale', 'Manzo', 'Piatto unico', 'Secondo'],
    789: ['Cena', 'Manzo', 'Secondo'],
    792: ['Cena', 'Pesce', 'Cotto o saltato in padella', 'Secondo'],
    688: ['Dolce', 'Merenda', 'Vegetariano'],
    898: ['Vegano', 'Vegetariano'],
    903: ['Impasti per pizze, focacce & co.', 'Vegano', 'Vegetariano'],
    902: ['Vegano', 'Vegetariano'],
    901: ['Impasti per pizze, focacce & co.', 'Vegano', 'Vegetariano'],
    900: ['Impasti per pizze, focacce & co.', 'Vegano', 'Vegetariano'],
    899: ['Vegano', 'Vegetariano'],
    646: ['Impasti per pizze, focacce & co.'],
    881: ['Vegano', 'Vegetariano'],
    890: ['Vegano', 'Vegetariano'],
    882: ['Impasti per pizze, focacce & co.'],
    891: ['Impasti per pizze, focacce & co.'],
    793: ['Pesce'],
    772: ['Antipasto', 'Cena', 'Vegetariano'],
    749: ['Antipasto', 'Internazionale', 'Vegano', 'Vegetariano'],
    761: ['Manzo', 'Pranzo', 'Cotto o saltato in padella', 'Secondo'],
    785: ['Antipasto', 'Internazionale', 'Legumi', 'Vegano', 'Vegetariano'],
    653: ['Antipasto', 'Frutti di mare', 'Lesso e Bollito'],
    696: ['Dolce', 'Fritto', 'Vegetariano'],
    762: ['Arrosto', 'Contorno', 'Internazionale', 'Vegano', 'Vegetariano'],
    769: ['Arrosto', 'Cena', 'Internazionale', 'Natale', 'Secondo', 'Selvaggina e volatili'],
    724: ['Dolce', 'Internazionale', 'Natale', 'Vegetariano'],
    888: ['Vegano', 'Vegetariano'],
    887: ['Vegano', 'Vegetariano'],
    678: ['Legumi', 'Lesso e Bollito', 'Piatto unico', 'Pranzo', 'Primo', 'Vegano', 'Vegetariano', 'Zuppa, Minestra & Vellutate'],
    670: ['Gratinato', 'Secondo'],
    675: ['Gratinato', 'Pesce', 'Secondo'],
    645: ['Gratinato', 'Vegetariano'],
    755: ['Pesce', 'Secondo'],
    803: ['Internazionale', 'Legumi', 'Piatto unico', 'Pranzo', 'Primo', 'Vegano', 'Vegetariano', 'Zuppa, Minestra & Vellutate'],
    722: ['Manzo', 'Piatto unico', 'Pranzo', 'Primo'],
    742: ['Cena', 'Frutti di mare', 'Internazionale', 'Maiale', 'Pesce', 'Piatto unico'],
    807: ['Dolce', 'Merenda', 'Vegetariano'],
    768: ['Impasti per pizze, focacce & co.', 'Vegano', 'Vegetariano'],
    746: ['Impasti per pizze, focacce & co.', 'Vegetariano'],
    745: ['Impasti per pizze, focacce & co.', 'Vegetariano'],
    767: ['Impasti per pizze, focacce & co.', 'Vegano', 'Vegetariano'],
    681: ['Vegetariano'],
    744: ['Arrosto', 'Contorno', 'Vegano', 'Vegetariano'],
    728: ['Antipasto', 'Frutti di mare', 'Legumi', 'Zuppa, Minestra & Vellutate'],
    661: ['Maiale', 'Piatto unico', 'Pranzo', 'Primo'],
    654: ['Pranzo', 'Primo', 'Vegetariano'],
    662: ['Pesce', 'Pranzo', 'Primo'],
    655: ['Pesce', 'Pranzo', 'Primo'],
    658: ['Pesce', 'Pranzo', 'Primo'],
    774: ['Dolce', 'Vegetariano'],
    775: ['Dolce', 'Vegetariano'],
    736: ['Arrosto', 'Contorno', 'Vegano', 'Vegetariano'],
    788: ['Arrosto', 'Contorno', 'Vegano', 'Vegetariano'],
    766: ['Arrosto', 'Contorno', 'Vegano', 'Vegetariano'],
    760: ['Arrosto', 'Contorno', 'Vegano', 'Vegetariano'],
    753: ['Contorno', 'Vegano', 'Vegetariano'],
    701: ['Arrosto', 'Contorno', 'Vegano', 'Vegetariano'],
    673: ['Colazione', 'Dolce', 'Internazionale', 'Merenda', 'Vegetariano'],
    671: ['Antipasto', 'Gratinato', 'Vegano', 'Vegetariano'],
    660: ['Antipasto', 'Gratinato', 'Vegano', 'Vegetariano'],
    698: ['Cena', 'Pesce', 'Secondo'],
    656: ['Dolce', 'Fritto', 'Natale', 'Vegetariano'],
    751: ['Contorno', 'Legumi', 'Cotto o saltato in padella'],
    740: ['Natale', 'Vegetariano'],
    741: ['Vegetariano'],
    657: ['Fritto', 'Pesce'],
    863: ['Pesce'],
    865: ['Maiale'],
    861: ['Vegano', 'Vegetariano'],
    864: ['Vegano', 'Vegetariano'],
    862: ['Vegetariano'],
    866: ['Vegetariano'],
    893: ['Maiale'],
    894: ['Vegetariano'],
    892: ['Vegano', 'Vegetariano'],
    895: ['Vegano', 'Vegetariano'],
    896: ['Vegetariano'],
    813: ['Vegano', 'Vegetariano'],
    913: ['Vegetariano'],
    917: ['Vegano', 'Vegetariano'],
    922: ['Vegetariano'],
    870: ['Maiale'],
    852: ['Vegetariano'],
    880: ['Vegano', 'Vegetariano'],
    867: ['Vegano', 'Vegetariano'],
    869: ['Vegano', 'Vegetariano'],
    868: ['Vegano', 'Vegetariano'],
    905: ['Vegetariano'],
    915: ['Vegetariano'],
    923: ['Vegetariano'],
    912: ['Vegano', 'Vegetariano'],
    872: ['Vegetariano'],
    916: ['Vegetariano'],
    921: ['Maiale'],
    914: ['Vegetariano'],
    910: ['Maiale'],
    877: ['Maiale'],
    873: ['Vegano', 'Vegetariano'],
    875: ['Vegetariano'],
    874: ['Vegano', 'Vegetariano'],
    879: ['Fritto', 'Maiale'],
    876: ['Maiale'],
    878: ['Maiale'],
    718: ['Cena', 'Secondo'],
    743: ['Pollo', 'Cotto o saltato in padella', 'Secondo'],
    700: ['Arrosto', 'Cena', 'Secondo'],
    663: ['Maiale', 'Manzo', 'Secondo'],
    695: ['Gratinato', 'Secondo', 'Vegano', 'Vegetariano'],
    790: ['Vegetariano'],
    756: ['Vegetariano'],
    794: ['Pesce', 'Primo', 'Secondo'],
    683: [],  # Ragu alla Messinese — nessuna aggiunta
    689: ['Lento e Brasato', 'Maiale', 'Manzo', 'Sughi per primi'],
    699: ['Lento e Brasato', 'Maiale', 'Manzo', 'Sughi per primi'],
    800: ['Internazionale', 'Legumi', 'Pranzo', 'Primo', 'Zuppa, Minestra & Vellutate'],
    796: ['Pesce', 'Pranzo', 'Primo', 'Secondo'],
    697: ['Pranzo', 'Primo'],
    727: ['Antipasto', 'Zuppa, Minestra & Vellutate'],
    687: ['Arrosto', 'Cena', 'Secondo'],
    763: ['Arrosto', 'Cena', 'Manzo', 'Secondo'],
    679: ['Arrosto', 'Cena', 'Manzo', 'Secondo'],
    719: ['Vegetariano'],
    757: ['Vegano', 'Vegetariano'],
    758: ['Pesce'],
    779: ['Natale', 'Vegetariano'],
    703: ['Vegetariano'],
    672: ['Manzo', 'Cotto o saltato in padella', 'Secondo'],
    680: ['Manzo', 'Cotto o saltato in padella', 'Secondo'],
    685: ['Colazione', 'Merenda', 'Vegetariano'],
    691: ['Colazione', 'Merenda', 'Vegetariano'],
    686: ['Colazione', 'Merenda', 'Vegetariano'],
    690: ['Colazione', 'Merenda', 'Vegetariano'],
    684: ['Colazione', 'Merenda', 'Vegetariano'],
    692: ['Colazione', 'Dolce', 'Merenda', 'Vegetariano'],
    808: ['Dolce', 'Vegano', 'Vegetariano'],
    904: ['Vegano', 'Vegetariano'],
    883: ['Vegano', 'Vegetariano'],
    889: ['Vegetariano'],
    709: ['Vegetariano'],
    706: ['Vegetariano'],
    707: ['Vegetariano'],
    708: ['Vegetariano'],
    729: ['Antipasto', 'Internazionale', 'Vegetariano'],
    730: ['Antipasto', 'Internazionale', 'Vegetariano'],
    809: ['Frutti di mare', 'Pranzo', 'Primo'],
    659: ['Frutti di mare', 'Pranzo', 'Primo'],
    754: ['Contorno', 'Cotto o saltato in padella'],
    723: ['Dolce', 'Natale', 'Vegetariano'],
    720: ['Cena', 'Lento e Brasato', 'Secondo'],
    650: ['Cena', 'Pesce', 'Secondo'],
    735: ['Arrosto', 'Cena', 'Secondo', 'Selvaggina e volatili'],
    705: ['Dolce', 'Merenda', 'Vegetariano'],
    752: ['Piatto unico', 'Pollo', 'Secondo'],
    668: ['Antipasto', 'Cena', 'Internazionale', 'Manzo', 'Selvaggina e volatili'],
    667: ['Antipasto', 'Cena', 'Internazionale', 'Manzo', 'Selvaggina e volatili'],
    669: ['Antipasto', 'Cena', 'Internazionale', 'Pollo', 'Selvaggina e volatili'],
    750: ['Cena', 'Piatto unico', 'Pollo', 'Secondo'],
    811: ['Piatto unico', 'Vegano', 'Vegetariano'],
    664: ['Pesce', 'Piatto unico'],
    884: ['Vegano', 'Vegetariano'],
    885: ['Vegetariano'],
    798: ['Antipasto', 'Lesso e Bollito', 'Vegetariano'],
    748: ['Antipasto', 'Contorno', 'Internazionale', 'Vegano', 'Vegetariano'],
    666: ['Antipasto', 'Contorno', 'Internazionale'],
    764: ['Internazionale', 'Vegetariano'],
    694: ['Contorno'],
    693: ['Gratinato', 'Secondo'],
    799: ['Legumi', 'Piatto unico', 'Pranzo', 'Primo', 'Vegano', 'Vegetariano', 'Zuppa, Minestra & Vellutate'],
    747: ['Pranzo', 'Primo', 'Vegano', 'Vegetariano', 'Zuppa, Minestra & Vellutate'],
}

# RIMUOVI: {pk: [cat, ...]} — categorie da rimuovere (richiesta esplicita utente)
RIMUOVI = {
    886: ['Pane'],       # Ciabatta — elimina categoria Pane
    688: ['Desserts'],   # Flan al cioccolato — elimina Desserts, va in Dolce
    684: ['Desserts'],   # Schiacciata (4) — elimina Desserts, va in Colazione/Merenda
}


def main():
    print(f"🏷  applica_categorie.py")
    print(f"   DB: {PAPRIKA_DB}")
    if not PAPRIKA_DB.exists():
        print("   ❌ DB non trovato!")
        return

    con = sqlite3.connect(str(PAPRIKA_DB))
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA journal_mode=WAL')
    cur = con.cursor()

    # ── 1. Leggi categorie esistenti ──────────────────────────────────────────
    existing = {}  # name → Z_PK
    for row in cur.execute('SELECT Z_PK, ZNAME FROM ZRECIPECATEGORY').fetchall():
        existing[row['ZNAME']] = row['Z_PK']
    print(f"\n   Categorie esistenti nel DB: {len(existing)}")

    # ── 2. Crea categorie mancanti ────────────────────────────────────────────
    max_pk    = max(existing.values()) if existing else 0
    max_order = cur.execute('SELECT MAX(ZORDERFLAG) FROM ZRECIPECATEGORY').fetchone()[0] or 0

    created = []
    for cat_name in NUOVE_CATEGORIE:
        if cat_name in existing:
            continue
        max_pk    += 1
        max_order += 1
        cat_uid    = str(uuid.uuid4()).upper()
        cur.execute(
            'INSERT INTO ZRECIPECATEGORY '
            '(Z_PK, Z_ENT, Z_OPT, ZISSYNCED, ZORDERFLAG, ZPARENT, ZNAME, ZSTATUS, ZUID) '
            'VALUES (?, 13, 1, 1, ?, NULL, ?, ?, ?)',
            (max_pk, max_order, cat_name, 'unmodified', cat_uid)
        )
        cur.execute(
            'UPDATE Z_PRIMARYKEY SET Z_MAX = ? WHERE Z_NAME = ?',
            (max_pk, 'RecipeCategory')
        )
        existing[cat_name] = max_pk
        created.append(cat_name)

    if created:
        con.commit()
        print(f"\n   ✚ Categorie create ({len(created)}):")
        for c in created:
            print(f"      {c} (PK={existing[c]})")

    # ── 3. Leggi associazioni esistenti ───────────────────────────────────────
    existing_links = set()  # (recipe_pk, cat_pk)
    for row in cur.execute('SELECT Z_12RECIPES, Z_13CATEGORIES FROM Z_12CATEGORIES').fetchall():
        existing_links.add((row['Z_12RECIPES'], row['Z_13CATEGORIES']))

    # ── 4. Applica AGGIUNGI ───────────────────────────────────────────────────
    total_added = 0
    for r_pk, cats in AGGIUNGI.items():
        for cat_name in cats:
            cat_pk = existing.get(cat_name)
            if cat_pk is None:
                print(f"   ⚠️  categoria '{cat_name}' non trovata — skip")
                continue
            if (r_pk, cat_pk) in existing_links:
                continue  # già presente
            cur.execute(
                'INSERT INTO Z_12CATEGORIES (Z_12RECIPES, Z_13CATEGORIES) VALUES (?, ?)',
                (r_pk, cat_pk)
            )
            existing_links.add((r_pk, cat_pk))
            total_added += 1

    # ── 5. Applica RIMUOVI ────────────────────────────────────────────────────
    total_removed = 0
    for r_pk, cats in RIMUOVI.items():
        for cat_name in cats:
            cat_pk = existing.get(cat_name)
            if cat_pk is None:
                print(f"   ⚠️  categoria '{cat_name}' non trovata per RIMUOVI — skip")
                continue
            cur.execute(
                'DELETE FROM Z_12CATEGORIES WHERE Z_12RECIPES = ? AND Z_13CATEGORIES = ?',
                (r_pk, cat_pk)
            )
            if cur.rowcount:
                total_removed += 1
                existing_links.discard((r_pk, cat_pk))

    con.commit()

    print(f"\n   ✅ Aggiunte: {total_added} associazioni")
    print(f"   🗑  Rimosse:  {total_removed} associazioni (Pane/Desserts)")

    # ── 6. Report categorie vuote ─────────────────────────────────────────────
    print("\n   Verifica categorie vuote (Pane, Desserts):")
    for cat_name in ['Pane', 'Desserts']:
        cat_pk = existing.get(cat_name)
        if cat_pk is None:
            print(f"      {cat_name}: non trovata nel DB")
            continue
        count = cur.execute(
            'SELECT COUNT(*) FROM Z_12CATEGORIES WHERE Z_13CATEGORIES = ?', (cat_pk,)
        ).fetchone()[0]
        print(f"      {cat_name}: {count} ricette associate {'← vuota, eliminabile' if count == 0 else ''}")

    con.close()
    print("\n   ✅ Fatto! Riavvia Paprika per vedere le modifiche.")


if __name__ == '__main__':
    main()
