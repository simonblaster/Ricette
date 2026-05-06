#!/usr/bin/env python3
"""
Genera il sito web statico delle ricette leggendo direttamente dal database Paprika 3.
Output nella cartella docs/ pronta per GitHub Pages.
Esegue anche un backup del database Paprika nella cartella "Backup Paprika/".

Uso:
  python3 aggiorna_sito.py
"""

import sqlite3, json, os, sys, re, shutil, io, base64, gzip, zipfile as _zipfile, uuid as _uuid
import subprocess
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
DOCS_DIR   = SCRIPT_DIR / 'docs'
PHOTOS_DIR = DOCS_DIR / 'photos'
BACKUP_DIR = SCRIPT_DIR / 'Backup Paprika'

_paprika_override = os.environ.get('PAPRIKA_BASE_OVERRIDE')
PAPRIKA_BASE   = Path(_paprika_override) if _paprika_override else \
                 Path.home() / 'Library' / 'Group Containers' / '72KVKW69K8.com.hindsightlabs.paprika.mac.v3' / 'Data'
PAPRIKA_DB     = PAPRIKA_BASE / 'Database' / 'Paprika.sqlite'
PAPRIKA_PHOTOS = PAPRIKA_BASE / 'Photos'

DOCS_DIR.mkdir(exist_ok=True)
PHOTOS_DIR.mkdir(exist_ok=True)
BACKUP_DIR.mkdir(exist_ok=True)

# ── 0. Script helper: env condiviso (per passare PAPRIKA_BASE_OVERRIDE al sandbox) ──
_env_extra = {**os.environ}
if _paprika_override:
    _env_extra['PAPRIKA_BASE_OVERRIDE'] = _paprika_override

def _run_helper(script_name, extra_args=None):
    """Esegue uno script Python nella stessa cartella, con lo stesso env."""
    script = SCRIPT_DIR / script_name
    if not script.exists():
        print(f"   ⚠️  {script_name} non trovato — saltato")
        return
    cmd = [sys.executable, str(script)] + (extra_args or [])
    result = subprocess.run(cmd, env=_env_extra, capture_output=False)
    if result.returncode != 0:
        print(f"   ⚠️  {script_name} terminato con codice {result.returncode}")

# ── 0a. Sincronizza commenti Firebase → Paprika (prima del backup, così il
#         backup include già i commenti) ─────────────────────────────────────
print("💬 Sincronizzazione commenti Firebase...")
_run_helper('sync_commenti.py')

# ── 1. Backup database Paprika ────────────────────────────────────────────────
print("💾 Backup database Paprika...")
backup_name = f"Paprika_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.sqlite"
backup_path = BACKUP_DIR / backup_name

try:
    src_con = sqlite3.connect(f'file:{PAPRIKA_DB}?mode=ro', uri=True)
    dst_con = sqlite3.connect(str(backup_path))
    src_con.backup(dst_con)
    dst_con.close()
    src_con.close()
except Exception:
    # Fallback: copia diretta del file
    try: dst_con.close()
    except Exception: pass
    shutil.copy2(str(PAPRIKA_DB), str(backup_path))

# Rimuovi file journal/shm/wal lasciati da sqlite accanto ai backup
for junk in BACKUP_DIR.glob('*.sqlite-*'):
    try: junk.unlink()
    except Exception: pass

# Mantieni solo gli ultimi 10 backup (pattern specifico: Paprika_YYYY-... esclude pre_links_* ecc.)
backups = sorted(BACKUP_DIR.glob('Paprika_[0-9]*.sqlite'))
for old in backups[:-10]:
    try:
        old.unlink()
    except Exception:
        pass

print(f"   ✅ {backup_name} ({backup_path.stat().st_size // 1024} KB)")

# ── 1b. Assegna categorie automatiche alle ricette nuove ─────────────────────
print("🏷  Assegnazione categorie automatiche...")
_run_helper('assegna_categorie.py')   # modalità incrementale (solo ricette nuove)

# ── 2. Lettura database Paprika ───────────────────────────────────────────────
print("📖 Lettura database Paprika...")
con = sqlite3.connect(f'file:{PAPRIKA_DB}?mode=ro', uri=True)
con.row_factory = sqlite3.Row
cur = con.cursor()

cur.execute('''
    SELECT r.*, GROUP_CONCAT(c.ZNAME, '|||') AS categories
    FROM ZRECIPE r
    LEFT JOIN Z_12CATEGORIES j ON j.Z_12RECIPES = r.Z_PK
    LEFT JOIN ZRECIPECATEGORY c ON c.Z_PK = j.Z_13CATEGORIES
    WHERE r.ZINTRASH = 0 OR r.ZINTRASH IS NULL
    GROUP BY r.Z_PK
    ORDER BY r.ZNAME COLLATE NOCASE
''')
raw_recipes = cur.fetchall()
con.close()
print(f"   {len(raw_recipes)} ricette trovate")

# ── 3. Copia foto ─────────────────────────────────────────────────────────────
print("🖼  Copia foto...")
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("   ⚠️  Pillow non trovato — foto copiate senza ridimensionamento")

photos_copied = 0
for r in raw_recipes:
    uid = r['ZUID']
    photo_file = r['ZPHOTO']
    if not photo_file or not uid:
        continue
    src = PAPRIKA_PHOTOS / uid / photo_file
    dst = PHOTOS_DIR / f"{uid}.jpg"
    if dst.exists() or not src.exists():
        continue
    if HAS_PIL:
        try:
            img = Image.open(src)
            img.thumbnail((600, 600))
            img.save(dst, 'JPEG', quality=85)
        except Exception:
            shutil.copy2(src, dst)
    else:
        shutil.copy2(src, dst)
    photos_copied += 1

print(f"   {photos_copied} nuove foto copiate")

# ── 4. Preparazione dati JSON ─────────────────────────────────────────────────
CATS_ESCLUSE = {'Test'}

def fmt_ingredients(text):
    lines = (text or '').strip().splitlines()
    out = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        m = re.match(r'^==\s*(.+?)\s*==\s*$', line)
        if m:
            out.append({'type': 'header', 'text': m.group(1)})
        else:
            out.append({'type': 'item', 'text': line})
    return out

recipes_for_js = []
for r in raw_recipes:
    uid = r['ZUID'] or ''
    cats_raw = r['categories'] or ''
    categories = [c.strip() for c in cats_raw.split('|||')
                  if c.strip() and c.strip() not in CATS_ESCLUSE]

    has_photo = bool(r['ZPHOTO']) and (PHOTOS_DIR / f"{uid}.jpg").exists()

    recipes_for_js.append({
        'uid':         uid,
        'name':        (r['ZNAME'] or '').strip(),
        'categories':  categories,
        'servings':    (r['ZSERVINGS'] or '').strip(),
        'prep_time':   (r['ZPREPTIME'] or '').strip(),
        'cook_time':   (r['ZCOOKTIME'] or '').strip(),
        'total_time':  (r['ZTOTALTIME'] or '').strip(),
        'description': (r['ZDESCRIPTIONTEXT'] or '').strip(),
        'ingredients': fmt_ingredients(r['ZINGREDIENTS']),
        'directions':  (r['ZDIRECTIONS'] or '').strip(),
        'notes':       (r['ZNOTES'] or '').strip(),
        'rating':      round(int(r['ZRATING'] or 0) / 5),  # Paprika scala 0-25 → 0-5
        'source':      (r['ZSOURCE'] or '').strip(),
        'source_url':  (r['ZSOURCEURL'] or '').strip(),
        'has_photo':   has_photo,
        'favorites':   bool(r['ZONFAVORITES']),
    })

all_cats  = sorted(set(c for r in recipes_for_js for c in r['categories'] if c))
updated   = datetime.now().strftime('%d/%m/%Y %H:%M')
n_recipes = len(recipes_for_js)

# ── 5. Genera docs/recipes.js e docs/photo-uids.js ───────────────────────────
print("📄 Genera docs/recipes.js e docs/photo-uids.js...")

recipes_raw_js = json.dumps(recipes_for_js, ensure_ascii=False, separators=(',', ':'))
cats_raw_js    = json.dumps(all_cats,        ensure_ascii=False, separators=(',', ':'))
photo_uids     = sorted(p.stem for p in PHOTOS_DIR.iterdir() if p.suffix == '.jpg')
photo_uids_js  = json.dumps(photo_uids,      ensure_ascii=False, separators=(',', ':'))

(DOCS_DIR / 'recipes.js').write_text(
    f"// Auto-generato da aggiorna_sito.py — non modificare a mano.\n"
    f"// Aggiornato: {updated} — {n_recipes} ricette\n"
    f"window.RECIPES_RAW={recipes_raw_js};\n"
    f"window.CATS_RAW={cats_raw_js};\n",
    encoding='utf-8'
)
(DOCS_DIR / 'photo-uids.js').write_text(
    f"// Auto-generato da aggiorna_sito.py — non modificare a mano.\n"
    f"window.PHOTO_UIDS=new Set({photo_uids_js});\n",
    encoding='utf-8'
)
print(f"   ✅ {n_recipes} ricette, {len(all_cats)} categorie, {len(photo_uids)} foto indicizzate")

# ── 5b. Genera docs/links.js — cross-reference tra ricette ───────────────────
print("🔗 Calcola link tra ricette...")
import unicodedata as _ud

def _norm(s: str) -> str:
    s = s.replace('’', "'").replace('‘', "'")
    s = _ud.normalize('NFD', s.lower())
    return ''.join(c for c in s if _ud.category(c) != 'Mn')

# uid → nome_normalizzato (per matching)
uid_to_norm = {r['uid']: _norm(r['name']) for r in recipes_for_js}
# nome_normalizzato → uid
norm_to_uid = {v: k for k, v in uid_to_norm.items()}

# Per ogni ricetta cerca tag [recipe:Nome] in ingredienti e passi
# (aggiorna_sito.py legge dal DB già aggiornato da fix_recipe_links.py)
RECIPE_TAG = re.compile(r'\[recipe:([^\]]+)\]')

uses    = {}   # uid_sorgente  → set di uid_destinazione
used_in = {}   # uid_destinazione → set di uid_sorgente

for r in raw_recipes:
    uid_src = (r['Zuid'] or '').strip()
    if not uid_src:
        continue
    # Testo grezzo (prima della trasformazione fmt_ingredients)
    testo = ((r['ZINGREDIENTS'] or '') + '\n' +
             (r['ZDIRECTIONS'] or '') + '\n' +
             (r['ZDESCRIPTIONTEXT'] or '') + '\n' +
             (r['ZNOTES'] or ''))
    for m in RECIPE_TAG.finditer(testo):
        linked_name = m.group(1).strip()
        linked_norm = _norm(linked_name)
        uid_dst = norm_to_uid.get(linked_norm)
        if uid_dst and uid_dst != uid_src:
            uses.setdefault(uid_src, set()).add(uid_dst)
            used_in.setdefault(uid_dst, set()).add(uid_src)

# Combina in un unico dict serializzabile
links_combined = {}
for uid in set(list(uses.keys()) + list(used_in.keys())):
    links_combined[uid] = {
        'uses':    sorted(uses.get(uid, [])),
        'used_in': sorted(used_in.get(uid, [])),
    }

links_js = json.dumps(links_combined, ensure_ascii=False, separators=(',', ':'))
(DOCS_DIR / 'links.js').write_text(
    f"// Auto-generato da aggiorna_sito.py — non modificare a mano.\n"
    f"window.RECIPE_LINKS={links_js};\n",
    encoding='utf-8'
)
n_links = sum(len(v['uses']) for v in links_combined.values())
print(f"   ✅ {n_links} link tra {len(links_combined)} ricette")

# ── 6. .nojekyll per GitHub Pages ─────────────────────────────────────────────
(DOCS_DIR / ".nojekyll").write_text("")

# ── 6b. Cache-busting: aggiorna il timestamp ?v= nei tag <script> di index.html ──
import re as _re, time as _time
_idx = DOCS_DIR / 'index.html'
_v   = str(int(_time.time()))
_html = _idx.read_text(encoding='utf-8')
_html = _re.sub(r'(v2/\w[\w\-]*\.jsx)(\?v=\d+)?', lambda m: f'{m.group(1)}?v={_v}', _html)
_html = _re.sub(r'<!-- v=\d+', f'<!-- v={_v}', _html)
_idx.write_text(_html, encoding='utf-8')
print(f"   🔖 Cache-bust JSX: ?v={_v}")

# ── 7. Export completo .paprikarecipes ────────────────────────────────────────
print("📦 Export Paprika → .paprikarecipes...")

def _photo_b64(uid, photo_file):
    """Legge la foto originale da Paprika e la restituisce come JPEG base64."""
    src = PAPRIKA_PHOTOS / uid / photo_file
    if not src.exists():
        return None
    try:
        img = Image.open(src).convert('RGB')
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=85)
        return base64.b64encode(buf.getvalue()).decode('utf-8')
    except Exception:
        return None

# Rileggi ricette con tutti i campi (incluso ZPHOTO)
con2 = sqlite3.connect(f'file:{PAPRIKA_DB}?mode=ro', uri=True)
con2.row_factory = sqlite3.Row
cur2 = con2.cursor()
cur2.execute('''
    SELECT r.*, GROUP_CONCAT(c.ZNAME, '|||') AS categories
    FROM ZRECIPE r
    LEFT JOIN Z_12CATEGORIES j ON j.Z_12RECIPES = r.Z_PK
    LEFT JOIN ZRECIPECATEGORY c ON c.Z_PK = j.Z_13CATEGORIES
    WHERE r.ZINTRASH = 0 OR r.ZINTRASH IS NULL
    GROUP BY r.Z_PK
    ORDER BY r.ZNAME COLLATE NOCASE
''')
all_rows = cur2.fetchall()
con2.close()

export_file = SCRIPT_DIR / "paprika_export_complete.paprikarecipes"
n_with_photo = 0

with _zipfile.ZipFile(str(export_file), 'w', _zipfile.ZIP_DEFLATED) as zf:
    for r in all_rows:
        uid       = r['ZUID'] or str(_uuid.uuid4())
        cats_raw  = r['categories'] or ''
        cats      = [c.strip() for c in cats_raw.split('|||') if c.strip()]
        photo_b64 = None
        if r['ZPHOTO'] and r['ZUID']:
            photo_b64 = _photo_b64(r['ZUID'], r['ZPHOTO'])
            if photo_b64:
                n_with_photo += 1

        recipe_dict = {
            'uid':         uid,
            'name':        (r['ZNAME'] or '').strip(),
            'ingredients': (r['ZINGREDIENTS'] or '').strip(),
            'directions':  (r['ZDIRECTIONS'] or '').strip(),
            'notes':       (r['ZNOTES'] or '').strip(),
            'description': (r['ZDESCRIPTIONTEXT'] or '').strip(),
            'servings':    (r['ZSERVINGS'] or '').strip(),
            'prep_time':   (r['ZPREPTIME'] or '').strip(),
            'cook_time':   (r['ZCOOKTIME'] or '').strip(),
            'total_time':  (r['ZTOTALTIME'] or '').strip(),
            'source':      (r['ZSOURCE'] or '').strip(),
            'source_url':  (r['ZSOURCEURL'] or '').strip(),
            'categories':  cats,
            'rating':      int(r['ZRATING'] or 0),
            'difficulty':  (r['ZDIFFICULTY'] or '').strip(),
            'photo_data':  photo_b64,
            'hash':        uid,
        }
        payload = json.dumps(recipe_dict, ensure_ascii=False)
        gz_data = gzip.compress(payload.encode('utf-8'))
        zf.writestr(f"{uid}.paprikarecipe", gz_data)

print(f"   ✅ {len(all_rows)} ricette esportate ({n_with_photo} con foto) → {export_file.name}")

print(f"\n✅ Fatto! {n_recipes} ricette · backup DB in 'Backup Paprika/{backup_name}' · export in '{export_file.name}'")
