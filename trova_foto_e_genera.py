#!/usr/bin/env python3
"""
Scarica le foto da GialloZafferano (URL già raccolti via Chrome)
e genera il file MacGourmet_Ricette.paprikarecipes completo.
"""

import sqlite3, json, gzip, zipfile, uuid, datetime, io, os, base64, hashlib
import urllib.request, urllib.parse, time
from PIL import Image

# ── Percorsi ──────────────────────────────────────────────────────────────────
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
DB_PATH     = os.path.join(SCRIPT_DIR, "MacGourmet.mgdb")
IMG_DIR     = os.path.join(SCRIPT_DIR, "Images")
FOUND_DIR   = os.path.join(SCRIPT_DIR, "Images_web")   # nuove foto scaricate
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "MacGourmet_Ricette.paprikarecipes")
GZ_URLS_FILE = os.path.join(SCRIPT_DIR, "gz_image_urls.json")  # URL raccolti via Chrome
os.makedirs(FOUND_DIR, exist_ok=True)

# ── URL GialloZafferano pre-raccolti ─────────────────────────────────────────
with open(GZ_URLS_FILE) as f:
    GZ_IMAGE_URLS = {int(k): v for k, v in json.load(f).items()}

# ── Funzioni di ricerca immagini ───────────────────────────────────────────────
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def giallozafferano_search_image(query):
    """Cerca su GialloZafferano e restituisce l'URL dell'immagine."""
    try:
        q = urllib.parse.quote(query)
        url = f"https://www.giallozafferano.it/ricerca-ricette/{q}/"
        req = urllib.request.Request(url, headers={**HEADERS, 'Accept-Language': 'it-IT,it;q=0.9'})
        with urllib.request.urlopen(req, timeout=12) as r:
            html = r.read().decode('utf-8', errors='replace')
        # Cerca il primo src di immagine ricetta nella pagina
        import re
        # Cerca pattern immagini GZ tipo /images/NNN-NNNNN/Nome_360x300.jpg
        matches = re.findall(r'(https://www\.giallozafferano\.it/images/[^"\'>\s]+\.jpg)', html)
        if matches:
            return matches[0]
        # Fallback: cerca qualsiasi img src
        matches2 = re.findall(r'src="(https://[^"]+(?:360x300|300x300|400x300|_[0-9]+x[0-9]+)[^"]*\.jpg)"', html)
        if matches2:
            return matches2[0]
    except Exception:
        pass
    return None

def download_and_resize(url, max_size=600):
    """Scarica un'immagine, la ridimensiona e restituisce i bytes JPEG."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'Accept-Language': 'it-IT,it;q=0.9',
        'Referer': 'https://www.giallozafferano.it/',
        'Sec-Fetch-Dest': 'image',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Site': 'same-origin',
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as r:
        data = r.read()
    img = Image.open(io.BytesIO(data)).convert('RGB')
    img.thumbnail((max_size, max_size), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=85)
    return buf.getvalue()

# ── Termini di ricerca personalizzati ────────────────────────────────────────
SEARCH_OVERRIDE = {
    "Pitoni fritti alla Messinese":     "pitoni messinesi",
    "Pitoni alla Messinese di Natale":  "pitoni messinesi",
    "Pitoni alla panzerotto":           "panzerotto fritto",
    "Pangrattato condito alla Messinese": "pangrattato condito",
    "Zucchina Lunga Al Sapore Di Sicilia": "zucchine siciliane",
    "Pannocchie Abbrustolite":          "pannocchie grigliate",
    "Ragout di pesce":                  "ragù di pesce",
    "Stoccafisso alla ghiotta messinese": "stoccafisso alla ghiotta",
    "Pescestocco Alla Messinese":       "stoccafisso alla ghiotta",
    "Rigatoni Col Sugo Dell'agglassato": "rigatoni al sugo di carne",
    "Rigatoni al ragout di pesce":      "pasta ragù di pesce",
    "Mum's Everyday Red Lentils":       "zuppa lenticchie rosse",
    "Egyptian Red Lentil Soup":         "zuppa lenticchie rosse egiziana",
    "Winter Crunch Salad with A Mind-blowing Sauce": "insalata invernale croccante",
    "Pane 3":                           "pane fatto in casa",
    "Pane Bianco":                      "pane bianco",
    "Pane Con La Macchina Del Pane":    "pane macchina del pane",
    "Pane bianco standard":             "pane bianco",
    "Roux":                             "roux burro farina",
    "Soffritto all'italiana":           "soffritto verdure",
    "Soffritto all'italiana con pancetta": "soffritto pancetta",
    "Soffritto di cipolle":             "cipolle soffritte",
    "Soffritto di porri":               "porri soffritti",
    "Soffritto di scalogni":            "scalogno soffrito",
    "Sugo d'arrosto":                   "sugo di arrosto",
    "Sugo da Roast-Beef ultra rapido":  "sugo di carne",
    "Salse per l'arrosto":              "salsa per arrosto",
    "Salse di Mele di Natale":          "salsa di mele natale",
    "Puré di Piselli \"A Modo Mio\"":  "purè di piselli",
    "FIletto di Tonno in padella":      "filetto di tonno in padella",
    "Fondo di pesce":                   "fondo di pesce brodo",
    "Ristretto di zucca con polpettine speziate": "vellutata di zucca polpette",
    "Stelle alla gelatina di lampone":  "biscotti gelatina lampone",
    "Schiacciata Alla Fiorentina \"tradizionale\" (2)": "schiacciata fiorentina",
    "Schiacciata Alla Fiorentina \"tradizionale\" (3)": "schiacciata fiorentina",
    "Schiacciata Alla Fiorentina \"tradizionale\" (4)": "schiacciata fiorentina",
    "Peanut Butter Biscuit":            "biscotti burro di arachidi",
    "Pasta 'ncasciata A' Missinisi":    "pasta ncasciata",
    "Spaghetti O' Niuru De Sicci":      "spaghetti al nero di seppia",
    "Pasta Con La Mollica":             "pasta con la mollica",
    "Pasta Con Le Sarde":               "pasta con le sarde",
    "Ragu alla Messinese":              "ragù alla messinese",
    "Pollo alla Mascalzona":            "pollo alla cacciatora",
    "Scaloppine del nonno Stefano":     "scaloppine al limone",
    "Terrina D'anatra":                 "terrina d anatra",
    "Terrina D'anatra Alle Mele":       "terrina d anatra mele",
    "Terrina Di Fegati Di Pollo":       "terrina fegatini pollo",
    "Torta Salata Alla Scarola":        "torta salata scarola",
    "Torta di Pollo":                   "torta salata pollo",
    "Teglia di Pollo":                  "pollo in teglia",
}

# ── Lettura database ──────────────────────────────────────────────────────────
print("📂 Lettura database MacGourmet...")
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("SELECT image_id, file_name FROM image")
image_map = {r['image_id']: r['file_name'] for r in cur.fetchall()}

cur.execute("SELECT recipe_id, note_text FROM recipe_note")
notes_map = {}
for r in cur.fetchall():
    notes_map.setdefault(r['recipe_id'], []).append(r['note_text'] or '')

cur.execute("""SELECT c.name, j.recipe_id FROM category c
               JOIN recipe_category_join j ON c.category_id=j.category_id
               WHERE c.is_hidden=0""")
cats_map = {}
for r in cur.fetchall():
    cats_map.setdefault(r['recipe_id'], []).append(r['name'])

cur.execute("SELECT * FROM time")
prep_map, cook_map, total_map = {}, {}, {}
for r in cur.fetchall():
    mins = r['amount'] * (60 if r['time_unit_id']==1 else 1)
    if r['amount_2']:
        mins += r['amount_2'] * (60 if r['time_unit_2_id']==1 else 1)
    def fmt(m):
        h, mn = divmod(int(m), 60)
        if h and mn: return f"{h} {'ora' if h==1 else 'ore'} {mn} min"
        if h: return f"{h} {'ora' if h==1 else 'ore'}"
        return f"{mn} min"
    if r['time_type_id']==9:  prep_map[r['recipe_id']]  = fmt(mins)
    elif r['time_type_id']==5: cook_map[r['recipe_id']] = fmt(mins)
    elif r['time_type_id']==30: total_map[r['recipe_id']] = fmt(mins)

def format_ingredient(row):
    if row['is_divider']:
        return f"== {row['description']} =="
    parts = []
    for f in ['quantity', 'measurement', 'description']:
        v = (row[f] or '').strip()
        if v: parts.append(v)
    note = (row['direction'] or '').strip()
    if note: parts.append(f"({note})")
    return ' '.join(parts)

def load_local_image(file_name):
    for suffix in ['.jpg', '_large.jpg']:
        path = os.path.join(IMG_DIR, file_name + suffix)
        if os.path.exists(path):
            try:
                img = Image.open(path).convert('RGB')
                img.thumbnail((600, 600), Image.LANCZOS)
                buf = io.BytesIO()
                img.save(buf, format='JPEG', quality=85)
                return buf.getvalue()
            except: pass
    return None

cur.execute("SELECT * FROM recipe WHERE has_been_deleted=0 OR has_been_deleted IS NULL ORDER BY recipe_id")
recipes = cur.fetchall()

# ── Scarica foto mancanti da GialloZafferano ──────────────────────────────────
print(f"\n📥 Scarico foto da GialloZafferano ({len(GZ_IMAGE_URLS)} URL disponibili)...\n")
web_images = {}   # recipe_id -> bytes

recipes_no_photo = []
for recipe in recipes:
    rid = recipe['recipe_id']
    img_id = recipe['image_id']
    fname = image_map.get(img_id, '') if img_id and img_id > 0 else ''
    has_local = fname and any(os.path.exists(os.path.join(IMG_DIR, fname+s)) for s in ['.jpg','_large.jpg'])
    if not has_local:
        recipes_no_photo.append(recipe)

print(f"   Ricette senza foto locale: {len(recipes_no_photo)}\n")

found_web = 0
not_found = []

for i, recipe in enumerate(recipes_no_photo):
    rid  = recipe['recipe_id']
    name = recipe['name'] or ''

    cached = os.path.join(FOUND_DIR, f"{rid}.jpg")
    if os.path.exists(cached):
        with open(cached, 'rb') as f:
            web_images[rid] = f.read()
        found_web += 1
        print(f"  [{i+1:2}/{len(recipes_no_photo)}] ✅ (cache) {name}")
        continue

    img_url = GZ_IMAGE_URLS.get(rid)
    if img_url:
        try:
            img_bytes = download_and_resize(img_url)
            with open(cached, 'wb') as f:
                f.write(img_bytes)
            web_images[rid] = img_bytes
            found_web += 1
            print(f"  [{i+1:2}/{len(recipes_no_photo)}] ✅ {name}")
        except Exception as e:
            not_found.append(name)
            print(f"  [{i+1:2}/{len(recipes_no_photo)}] ⚠️  Download fallito: {name} ({e})")
    else:
        not_found.append(name)
        print(f"  [{i+1:2}/{len(recipes_no_photo)}] ❌ Nessun URL: {name}")

    time.sleep(0.1)

print(f"\n   Scaricate: {found_web}/{len(recipes_no_photo)}")
if not_found:
    print(f"   Non trovate ({len(not_found)}):")
    for n in not_found:
        print(f"     - {n}")

# ── Genera file Paprika ───────────────────────────────────────────────────────
print(f"\n📦 Genero {OUTPUT_FILE}...")
diff_map = {0:'', 1:'Easy', 2:'Medium', 3:'Hard'}

photos_local = photos_web = photos_none = 0

with zipfile.ZipFile(OUTPUT_FILE, 'w', zipfile.ZIP_STORED) as zf:
    for recipe in recipes:
        rid = recipe['recipe_id']

        cur.execute("SELECT * FROM ingredient WHERE recipe_id=? ORDER BY sort_order", (rid,))
        ing_lines = [format_ingredient(r) for r in cur.fetchall()]

        cur.execute("SELECT directions_text FROM direction WHERE recipe_id=? ORDER BY sort_order", (rid,))
        directions_text = '\n\n'.join(r['directions_text'] for r in cur.fetchall() if r['directions_text'])

        # Foto: prima locale, poi web
        photo_data = photo_hash = None
        img_id = recipe['image_id']
        fname = image_map.get(img_id, '') if img_id and img_id > 0 else ''
        if fname:
            img_bytes = load_local_image(fname)
            if img_bytes:
                photo_data = base64.b64encode(img_bytes).decode('ascii')
                photo_hash = hashlib.md5(img_bytes).hexdigest()
                photos_local += 1
        if photo_data is None and rid in web_images:
            img_bytes = web_images[rid]
            photo_data = base64.b64encode(img_bytes).decode('ascii')
            photo_hash = hashlib.md5(img_bytes).hexdigest()
            photos_web += 1
        if photo_data is None:
            photos_none += 1

        try:
            created = datetime.datetime.fromtimestamp(recipe['date_created']).strftime('%Y-%m-%d %H:%M:%S')
        except:
            created = '2012-01-01 00:00:00'

        srv = recipe['servings']
        servings_str = f"{srv} persone" if srv and srv > 0 else (recipe['yield'] or '')

        paprika = {
            "uid":             str(uuid.uuid4()).upper(),
            "name":            recipe['name'] or '',
            "servings":        servings_str,
            "source":          recipe['source'] or '',
            "source_url":      recipe['url'] or '',
            "prep_time":       prep_map.get(rid, ''),
            "cook_time":       cook_map.get(rid, ''),
            "total_time":      total_map.get(rid, ''),
            "on_favorites":    bool(recipe['has_flag']),
            "categories":      cats_map.get(rid, []),
            "rating":          int(recipe['rating'] * 5) if recipe['rating'] else 0,
            "description":     recipe['summary'] or '',
            "ingredients":     '\n'.join(ing_lines),
            "directions":      directions_text,
            "notes":           '\n\n'.join(notes_map.get(rid, [])),
            "nutritional_info": recipe['nutrition_info'] or '',
            "difficulty":      diff_map.get(recipe['difficulty'], ''),
            "photo":           None,
            "photo_data":      photo_data,
            "photo_hash":      photo_hash,
            "photo_large":     None,
            "image_url":       "",
            "created":         created,
            "hash":            str(uuid.uuid4()).upper(),
        }

        json_bytes = json.dumps(paprika, ensure_ascii=False).encode('utf-8')
        gz_buf = io.BytesIO()
        with gzip.GzipFile(fileobj=gz_buf, mode='wb') as gz:
            gz.write(json_bytes)
        safe_name = ''.join(c for c in (recipe['name'] or 'recipe') if c.isalnum() or c in ' -_')[:50]
        zf.writestr(f"{safe_name}_{rid}.paprikarecipe", gz_buf.getvalue())

conn.close()
size_mb = os.path.getsize(OUTPUT_FILE) / (1024*1024)
print(f"\n✅ Completato!")
print(f"   Foto originali:  {photos_local}")
print(f"   Foto da web:     {photos_web}")
print(f"   Senza foto:      {photos_none}")
print(f"   Dimensione file: {size_mb:.1f} MB")
print(f"\n   File pronto in: {OUTPUT_FILE}")
print(f"   Fai doppio click per importare in Paprika (cancella prima le vecchie ricette con Cmd+A)")
