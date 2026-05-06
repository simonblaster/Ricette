#!/usr/bin/env python3
import sqlite3, os, re

db = os.path.expanduser(
    '~/Library/Group Containers/'
    '72KVKW69K8.com.hindsightlabs.paprika.mac.v3/Data/Database/Paprika.sqlite'
)
conn = sqlite3.connect(db)

RINOMINA = [
    ('== Brodi ==',     '== \U0001F372 Brodi =='),
    ('== Soffritti ==', '== \U0001F9C5 Soffritti =='),
    ('== Creme ==',     '== \U0001F36E Creme =='),
    ('== Contorni ==',  '== \U0001F954 Contorni =='),
    ('== Salse ==',     '== \U0001FAD9 Salse =='),
    ('== Sughi ==',     '== \U0001F958 Sughi =='),
    ('== Impasti ==',   '== \U0001F355 Impasti =='),
    ('== Varianti ==',  '== \U0001F3A8 Varianti =='),
]

# 1) Rinomina header + spaziatura su ZINGREDIENTS e ZNOTES
n = 0
for campo in ['ZINGREDIENTS', 'ZNOTES']:
    cur = conn.execute(
        f'SELECT Z_PK, {campo} FROM ZRECIPE '
        f'WHERE {campo} LIKE "%== %" AND (ZINTRASH=0 OR ZINTRASH IS NULL)'
    )
    for pk, testo in cur.fetchall():
        if not testo:
            continue
        nuovo = testo
        for vecchio, nuovo_h in RINOMINA:
            nuovo = nuovo.replace(vecchio, nuovo_h)
        # Aggiunge riga vuota dopo header se mancante
        nuovo = re.sub(r'(== [^\n]+ ==)\n([^\n])', r'\1\n\n\2', nuovo)
        if nuovo != testo:
            conn.execute(f'UPDATE ZRECIPE SET {campo}=? WHERE Z_PK=?', (nuovo, pk))
            n += 1
print(f'Header/spaziatura: {n} campi aggiornati')

# 2) Arrosto di Manzo — rimuovi == per servire: == da ZDIRECTIONS
cur = conn.execute(
    "SELECT Z_PK, ZDIRECTIONS FROM ZRECIPE WHERE ZNAME='Arrosto di Manzo'"
)
row = cur.fetchone()
if row:
    pk, dirs = row
    nuovo = re.sub(r'\n*== per servire: ==\n[\s\S]*', '', dirs).rstrip()
    conn.execute('UPDATE ZRECIPE SET ZDIRECTIONS=? WHERE Z_PK=?', (nuovo, pk))
    print('Arrosto di Manzo: sezione per servire rimossa da ZDIRECTIONS')

conn.commit()
conn.close()
print('Fatto.')
