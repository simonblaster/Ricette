#!/usr/bin/env python3
"""
sync_commenti.py — Scarica i commenti nuovi da Firebase Firestore e li
appende alle note (ZNOTES) delle ricette nel database Paprika 3.

Il formato aggiunto a ZNOTES:
  ---
  [Nome Utente via sito, 03/05/2026]: Testo del commento.

Richiede:
  pip install firebase-admin --break-system-packages
  File di service account: firebase-service-account.json nella cartella del progetto

Uso:
  python3 sync_commenti.py [--dry-run]

Variabili ambiente:
  PAPRIKA_BASE_OVERRIDE  — path alternativo alla cartella Data di Paprika (sandbox)
"""

import sqlite3, os, sys, json
from pathlib import Path
from datetime import datetime

SCRIPT_DIR    = Path(__file__).parent
SA_FILE       = SCRIPT_DIR / 'firebase-service-account.json'
DRY_RUN       = '--dry-run' in sys.argv

_override    = os.environ.get('PAPRIKA_BASE_OVERRIDE')
PAPRIKA_BASE = Path(_override) if _override else \
               Path.home() / 'Library' / 'Group Containers' / \
               '72KVKW69K8.com.hindsightlabs.paprika.mac.v3' / 'Data'
PAPRIKA_DB   = PAPRIKA_BASE / 'Database' / 'Paprika.sqlite'


def main():
    print("💬 sync_commenti.py — sincronizza commenti Firebase → Paprika")

    # ── Verifica prerequisiti ─────────────────────────────────────────────────
    if not SA_FILE.exists():
        print("   ⏭  firebase-service-account.json non trovato — sincronizzazione saltata")
        print("      (crea il progetto Firebase e scarica il service account per attivare)")
        return

    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
    except ImportError:
        print("   ⏭  firebase-admin non installato — esegui:")
        print("      pip install firebase-admin --break-system-packages")
        return

    # ── Inizializza Firebase Admin ────────────────────────────────────────────
    try:
        app = firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate(str(SA_FILE))
        app  = firebase_admin.initialize_app(cred)

    db = firestore.client()

    # ── Leggi commenti non ancora sincronizzati ────────────────────────────────
    query    = db.collection('commenti').where('synced', '==', False).stream()
    commenti = list(query)

    if not commenti:
        print("   ✅ Nessun commento nuovo da sincronizzare")
        return

    print(f"   {len(commenti)} commenti nuovi trovati")

    # ── Apri Paprika DB ───────────────────────────────────────────────────────
    con = sqlite3.connect(str(PAPRIKA_DB))
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA journal_mode=WAL')

    for doc in commenti:
        c = doc.to_dict()
        recipe_uid  = c.get('recipeUid', '')
        testo       = c.get('testo', '').strip()
        author_name = c.get('authorName', 'Anonimo')
        data_ts     = c.get('data')

        if not recipe_uid or not testo:
            continue

        # Formatta la data
        if data_ts:
            try:
                data_str = data_ts.strftime('%d/%m/%Y')
            except Exception:
                data_str = datetime.now().strftime('%d/%m/%Y')
        else:
            data_str = datetime.now().strftime('%d/%m/%Y')

        riga = f"\n---\n[{author_name} via sito, {data_str}]: {testo}"

        # Trova la ricetta nel DB Paprika per ZUID
        row = con.execute(
            'SELECT Z_PK, ZNOTES FROM ZRECIPE WHERE ZUID = ? AND (ZINTRASH = 0 OR ZINTRASH IS NULL)',
            (recipe_uid,)
        ).fetchone()

        if not row:
            print(f"   ⚠️  ricetta non trovata: uid={recipe_uid}")
            continue

        note_attuali = row['ZNOTES'] or ''
        note_nuove   = note_attuali + riga

        print(f"   ✚ Commento di {author_name} ({data_str}) → ricetta uid={recipe_uid[:8]}…")
        if not DRY_RUN:
            con.execute(
                'UPDATE ZRECIPE SET ZNOTES = ? WHERE Z_PK = ?',
                (note_nuove, row['Z_PK'])
            )
            # Marca il commento come sincronizzato su Firestore
            doc.reference.update({'synced': True})

    if not DRY_RUN:
        con.commit()

    con.close()
    print(f"   ✅ Sincronizzazione completata{' (DRY-RUN)' if DRY_RUN else ''}")


if __name__ == '__main__':
    main()
