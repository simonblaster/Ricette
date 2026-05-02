# Memory Index — Progetto Ricette
*Aggiornato: 2026-05-02 (sessione 2)*

## File di memoria

- [Paprika Workflow](paprika_workflow.md) — Skill, convenzioni pizza/focaccia, scaling, naming, foto da chat, fonti elaborate

## Da ricordare in futuro

- **Lingua di lavoro**: italiano
- **Progetto**: conversione e gestione ricette in Paprika 3 per macOS
- **Cartella progetto**: `/Users/simone/Documents/Claude/Projects/Ricette/`
- **`present_files` è rotto nelle sessioni continuate** → usare sempre `open` via Desktop Commander
- **Immagini inline chat**: non vanno in uploads, vanno estratte dal JSONL del transcript
- **WAL checkpoint**: quando si interroga il DB Paprika, copiare tutti e 3 i file (sqlite, -wal, -shm) e fare checkpoint prima di leggere
