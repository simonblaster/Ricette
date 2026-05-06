#!/usr/bin/env python3
"""Fix puntuale per Arrosto di Manzo:
  1. Rimuove == per servire: == e tutto il seguito da ZDIRECTIONS
  2. Rimuove la riga con tag parziale "Sugo da [recipe:..." da ZNOTES
"""
import sqlite3, os, re

db = os.path.expanduser(
    '~/Library/Group Containers/'
    '72KVKW69K8.com.hindsightlabs.paprika.mac.v3/Data/Database/Paprika.sqlite'
)
conn = sqlite3.connect(db)

# Trova TUTTI i record "Arrosto di Manzo" (potrebbero esserci duplicati)
rows = conn.execute(
    "SELECT Z_PK, ZNAME, ZDIRECTIONS, ZNOTES FROM ZRECIPE "
    "WHERE ZNAME='Arrosto di Manzo' AND (ZINTRASH=0 OR ZINTRASH IS NULL)"
).fetchall()

print(f"Trovati {len(rows)} record 'Arrosto di Manzo'")

for pk, nome, dirs, notes in rows:
    print(f"\n  PK={pk}")
    changed = False

    # 1) Rimuovi == per servire: == e tutto ciò che segue da ZDIRECTIONS
    if dirs and '== per servire' in dirs:
        nuovo_dirs = re.sub(r'\s*== per servire:.*', '', dirs, flags=re.DOTALL).rstrip()
        print(f"    ZDIRECTIONS: rimossa sezione per servire ({len(dirs)-len(nuovo_dirs)} char)")
        conn.execute('UPDATE ZRECIPE SET ZDIRECTIONS=? WHERE Z_PK=?', (nuovo_dirs, pk))
        changed = True
    else:
        print(f"    ZDIRECTIONS: ok (nessun per servire)")

    # 2) Rimuovi righe con tag parziale "Sugo da [recipe:..." da ZNOTES
    if notes and 'Sugo da [recipe:' in notes:
        lines = notes.split('\n')
        pulite = [l for l in lines if not ('Sugo da [recipe:' in l)]
        nuovo_notes = '\n'.join(pulite)
        print(f"    ZNOTES: rimossa riga tag parziale Roast-Beef")
        conn.execute('UPDATE ZRECIPE SET ZNOTES=? WHERE Z_PK=?', (nuovo_notes, pk))
        changed = True
    else:
        print(f"    ZNOTES: ok")

    if not changed:
        print(f"    (nessuna modifica)")

conn.commit()
conn.close()
print("\nFatto.")
