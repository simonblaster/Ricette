#!/usr/bin/env python3
"""Genera doc_carmnella.paprikarecipes — estrae foto dal JSONL + build."""

import json, base64, io, os, subprocess, sys, zipfile

BASE = os.path.expanduser("~/Documents/Claude/Projects/Ricette")

# ── 0. Build script ─────────────────────────────────────────────────────────
build_script = os.path.join(BASE, "outputs", "build_paprikarecipes.py")
if not os.path.exists(build_script):
    with zipfile.ZipFile(os.path.join(BASE, "paprika-recipe-importer.skill"), 'r') as z:
        names = [n for n in z.namelist() if 'build_paprikarecipes' in n]
        with z.open(names[0]) as src, open(build_script, 'wb') as dst:
            dst.write(src.read())

# ── 1. Estrai foto dal JSONL (ultima immagine) ──────────────────────────────
JSONL = (
    os.path.expanduser("~/Library/Application Support/Claude/local-agent-mode-sessions")
    + "/92d11bfa-321a-4e61-8487-de1e3816bd12/a9be16a0-52cc-4701-9ec7-5fe9379c8053"
    + "/local_cc52c97e-d032-429b-ae86-1b36c46f9532/audit.jsonl"
)

def find_base64_images(obj):
    results = []
    if isinstance(obj, dict):
        if obj.get('type') == 'image' and obj.get('source', {}).get('type') == 'base64':
            results.append(obj['source']['data'])
        for v in obj.values():
            results.extend(find_base64_images(v))
    elif isinstance(obj, list):
        for item in obj:
            results.extend(find_base64_images(item))
    return results

all_images = []
with open(JSONL, 'r') as f:
    for line in f:
        try:
            all_images.extend(find_base64_images(json.loads(line)))
        except:
            pass
print(f"Immagini trovate nel JSONL: {len(all_images)}")

photo_b64 = None
if all_images:
    try:
        from PIL import Image
        raw = base64.b64decode(all_images[-1])
        img = Image.open(io.BytesIO(raw)).convert('RGB')
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=85)
        photo_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        print(f"Foto estratta: {img.size}")
    except Exception as e:
        print(f"Errore foto: {e}")

# ── 2. Recipe data ──────────────────────────────────────────────────────────
recipe = {
    "name": "Pizza in Teglia alla Romana — DOC (Carmnella)",
    "categories": ["Pizze, focacce & co."],
    "source": "Vincenzo Esposito — Carmnella, Napoli",
    "servings": "1 teglia 40×30 cm",
    "ingredients": (
        "**Dosi per 1 teglia 40×30**\n"
        "Impasto per teglia romana, 1 panetto da circa 600 g\n"
        "\n"
        "Pomodorini datterini a filetto, 120 g\n"
        "Mozzarella di bufala DOP, 200 g\n"
        "Parmigiano Reggiano 36 mesi, 30 g\n"
        "Basilico riccio napoletano, q.b.\n"
        "Olio EVO, q.b."
    ),
    "directions": (
        "**1. Preparazione**\n\n"
        "Stendere il panetto nella teglia oleata. "
        "Distribuire i pomodorini datterini a filetto e condire con un filo di olio EVO. "
        "Lasciare riposare 30-60 minuti.\n\n"
        "**2. Prima cottura**\n\n"
        "Infornare con platea a 325° e cielo a 225°. "
        "Cuocere per 5-6 minuti, ruotando la teglia dopo 3 minuti.\n\n"
        "**3. Seconda cottura**\n\n"
        "Abbassare la temperatura a platea 300°, cielo 200°. "
        "Cuocere per altri 5-6 minuti fino a doratura del cornicione.\n\n"
        "**4. Finitura**\n\n"
        "Sfornare e aggiungere la mozzarella di bufala DOP, "
        "le scaglie di Parmigiano Reggiano 36 mesi, "
        "le foglie di basilico riccio napoletano e un filo di olio EVO."
    ),
    "notes": (
        "Temperature e tempi indicativi basati su esperienza attuale con forno Nettuno (camera 17 cm) "
        "— da aggiornare con nuove esperienze.\n"
        "Tra un'infornata e l'altra, attendere 2-3 minuti per il recupero calore della pietra refrattaria."
    ),
    "photo_data": photo_b64,
    "rating": None, "difficulty": None, "description": None,
    "prep_time": None, "cook_time": None, "total_time": None, "source_url": None,
}

# ── 3. Build ────────────────────────────────────────────────────────────────
json_path = os.path.join(BASE, "outputs", "doc_carmnella.json")
out_path  = os.path.join(BASE, "doc_carmnella.paprikarecipes")

with open(json_path, 'w') as f:
    json.dump([recipe], f, ensure_ascii=False, indent=2)

result = subprocess.run(
    [sys.executable, build_script, "--input", json_path, "--output", out_path],
    capture_output=True, text=True
)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

if os.path.exists(out_path):
    print(f"✅ File creato: {out_path} ({os.path.getsize(out_path):,} bytes)")
    os.system(f'open "{out_path}"')
else:
    print("❌ File non creato.")
