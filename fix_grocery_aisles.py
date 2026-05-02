"""
Fix corsie nella lista della spesa di Paprika.
Aggiorna ZGROCERYITEM.ZAISLE e ZAISLENAME per gli item esistenti
basandosi su ZGROCERYINGREDIENT.
Eseguire con Paprika CHIUSO.
"""
import sqlite3
from pathlib import Path

DB = Path.home() / 'Library' / 'Group Containers' / '72KVKW69K8.com.hindsightlabs.paprika.mac.v3' / 'Data' / 'Database' / 'Paprika.sqlite'

con = sqlite3.connect(str(DB))
con.row_factory = sqlite3.Row
cur = con.cursor()

# Mappa aisle PK → nome
cur.execute("SELECT Z_PK, ZNAME FROM ZGROCERYAISLE")
aisle_names = {r['Z_PK']: r['ZNAME'] for r in cur.fetchall()}

# Dizionario ingrediente → aisle PK
cur.execute("SELECT ZNAME, ZAISLE FROM ZGROCERYINGREDIENT")
ing_to_aisle = {r['ZNAME'].lower(): r['ZAISLE'] for r in cur.fetchall()}

# Tutti gli item nella lista
cur.execute("SELECT Z_PK, ZINGREDIENT, ZAISLE, ZAISLENAME FROM ZGROCERYITEM")
items = cur.fetchall()
print(f"Item in lista: {len(items)}")

aggiornati = 0
non_trovati = []
for item in items:
    ing = (item['ZINGREDIENT'] or '').strip().lower()
    if not ing:
        continue
    
    # Cerca corrispondenza esatta
    new_aisle = ing_to_aisle.get(ing)
    
    # Se non trovata, prova senza parentesi
    if new_aisle is None:
        import re
        ing_clean = re.sub(r'\s*\(.*?\)', '', ing).strip()
        new_aisle = ing_to_aisle.get(ing_clean)
    
    if new_aisle and new_aisle != item['ZAISLE']:
        new_name = aisle_names.get(new_aisle, '')
        cur.execute(
            "UPDATE ZGROCERYITEM SET ZAISLE=?, ZAISLENAME=?, Z_OPT=Z_OPT+1 WHERE Z_PK=?",
            (new_aisle, new_name, item['Z_PK'])
        )
        print(f"  ✅ '{item['ZINGREDIENT']}' → {new_name}")
        aggiornati += 1
    elif new_aisle is None:
        non_trovati.append(item['ZINGREDIENT'])

con.commit()
con.close()

print(f"\n✅ Aggiornati: {aggiornati} item")
if non_trovati:
    print(f"⚠️  Non trovati nel dizionario ({len(non_trovati)}):")
    for x in non_trovati: print(f"   {x}")
