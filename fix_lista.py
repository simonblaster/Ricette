#!/usr/bin/env python3
"""
fix_lista.py — Corregge le corsie degli item in ZAISLE=7 in ZGROCERYITEM
usando il dizionario ZGROCERYINGREDIENT con matching multi-livello.

Uso: python3 fix_lista.py
"""

import sqlite3, re, shutil, os
from datetime import datetime
from pathlib import Path

# ── Percorso DB (supporta override via env)
BASE = os.environ.get(
    "PAPRIKA_BASE_OVERRIDE",
    str(Path.home() / "Library/Group Containers/72KVKW69K8.com.hindsightlabs.paprika.mac.v3/Data")
)
DB = Path(BASE) / "Database/Paprika.sqlite"

# ── Backup nella stessa cartella del repo
SCRIPT_DIR = Path(__file__).parent
BACKUP_DIR = SCRIPT_DIR / "Backup Paprika"
BACKUP_MAX = 10

# ── Unità/qualificatori da rimuovere per il matching
STRIP_UNITS = re.compile(
    r'^(?:'
    r'[\d\s.,/½¼¾⅓⅔⅛⅜⅝⅞]+'            # numeri/frazioni
    r'(?:\s*(?:kg|gr?|mg|ml|cl|dl|lb|oz|cc|lt?)\b\.?)?\s*'
    r'(?:cucchiai[o]?|cucchiaini?|tsp|tbsp|bicchier[ei]|bottigli[ae]|'
    r'lattine?|scatol[ae]|spicch[io]|mazzett[io]|mazz[io]|fett[ae]|'
    r'fili?|ramett[io]|foglier?|foglie?|pezz[io]|manciata?|bustina?|'
    r'stecca?|pizzich[io]|gamb[io]|gambi|'
    r'cup|cups|teaspoon|tablespoon|qb|q\.b\.)\.?\s*(?:di\s+|d\')?'
    r')?',
    re.IGNORECASE
)


def fai_backup():
    """Backup del DB prima di modificarlo. Mantieni solo gli ultimi BACKUP_MAX."""
    BACKUP_DIR.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
    dest = BACKUP_DIR / f"Paprika_{ts}.sqlite"
    try:
        src = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
        dst = sqlite3.connect(str(dest))
        src.backup(dst)
        dst.close()
        src.close()
    except Exception:
        shutil.copy2(str(DB), str(dest))
    # Pulizia file journal
    for junk in BACKUP_DIR.glob("*.sqlite-*"):
        try:
            junk.unlink()
        except Exception:
            pass
    # Tieni solo gli ultimi BACKUP_MAX
    backups = sorted(BACKUP_DIR.glob("Paprika_*.sqlite"))
    for old in backups[:-BACKUP_MAX]:
        try:
            old.unlink()
        except Exception:
            pass
    print(f"💾 Backup: {dest.name}")
    return dest


def normalizza(s):
    """Restituisce versioni semplificate del nome per il matching."""
    s = s.strip()
    candidati = []

    # 1. Originale
    candidati.append(s.lower())

    # 2. Senza note in parentesi
    s2 = re.sub(r'\s*\([^)]*\)', '', s).strip().rstrip(',.')
    if s2.lower() != s.lower():
        candidati.append(s2.lower())

    # 3. Salta intestazioni di sezione (== ... ==)
    if re.match(r'^==', s):
        return []

    # 4. Rimuovi unità/misure in testa
    s3 = STRIP_UNITS.sub('', s2).strip()
    if s3.lower() not in candidati:
        candidati.append(s3.lower())

    # 5. Prima parte prima di virgola/parentesi
    s4 = re.split(r'[,(]', s3)[0].strip().rstrip('.')
    if s4.lower() not in candidati and len(s4) > 2:
        candidati.append(s4.lower())

    # 6. Rimuovi aggettivi finali comuni
    s5 = re.sub(
        r'\s+(?:fresc[oaie]|secch[oaie]|secco|secca|bianco|bianca|'
        r'rosso|rossa|nero|nera|verde|grande|piccol[oae]|medio|media|'
        r'intero|intera|sgranato|tritato|grattugiato|a fette|a cubetti|'
        r'in polvere|macinato|crudo|cotto|scolato)$',
        '', s4, flags=re.IGNORECASE
    ).strip()
    if s5.lower() not in candidati and len(s5) > 2:
        candidati.append(s5.lower())

    return candidati


def lookup(nome, ing_dict):
    """Cerca nel dizionario con matching a più livelli. Ritorna (aisle_id, matched_key) o None."""
    for candidato in normalizza(nome):
        if candidato in ing_dict:
            return ing_dict[candidato], candidato
    # Fallback: sottostringa
    for candidato in normalizza(nome):
        for k, v in ing_dict.items():
            if candidato and candidato in k and len(candidato) > 4:
                return v, k
            if k and k in candidato and len(k) > 4:
                return v, k
    return None


def main():
    # Item da fixare?
    con = sqlite3.connect(str(DB))
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM ZGROCERYITEM WHERE ZAISLE = 7 OR ZAISLE IS NULL")
    n = cur.fetchone()[0]
    con.close()

    if n == 0:
        print("✅ Nessun item in 'Varie' — lista già ben categorizzata.")
        return

    # Backup PRIMA di modificare
    fai_backup()

    con = sqlite3.connect(str(DB))
    cur = con.cursor()

    # Dizionario ingredienti
    cur.execute("SELECT ZNAME, ZAISLE FROM ZGROCERYINGREDIENT WHERE ZNAME IS NOT NULL AND ZAISLE != 7")
    ing_dict = {r[0].lower().strip(): r[1] for r in cur.fetchall()}

    # Corsie
    cur.execute("SELECT Z_PK, ZNAME FROM ZGROCERYAISLE")
    aisle_names = {pk: name for pk, name in cur.fetchall()}

    # Item da fixare
    cur.execute("SELECT Z_PK, ZINGREDIENT FROM ZGROCERYITEM WHERE ZAISLE = 7 OR ZAISLE IS NULL")
    items = cur.fetchall()

    print(f"Item da categorizzare: {len(items)}\n")
    fixati = 0
    non_trovati = []

    for pk, ing in items:
        if not ing:
            continue
        result = lookup(ing, ing_dict)
        if result:
            aisle_id, matched = result
            aisle_name = aisle_names.get(aisle_id, "?")
            cur.execute(
                "UPDATE ZGROCERYITEM SET ZAISLE=?, ZAISLENAME=?, Z_OPT=Z_OPT+1 WHERE Z_PK=?",
                (aisle_id, aisle_name, pk)
            )
            print(f"  ✅ '{ing}'\n      → {aisle_name}  (via '{matched}')")
            fixati += 1
        else:
            non_trovati.append(ing)

    con.commit()
    con.close()

    print(f"\nFixati: {fixati}/{len(items)}")
    if non_trovati:
        print(f"\n⚠️  Non trovati ({len(non_trovati)}):")
        for x in non_trovati:
            print(f"   • {x}")


if __name__ == "__main__":
    main()
