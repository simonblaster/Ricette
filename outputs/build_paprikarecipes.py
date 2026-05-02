#!/usr/bin/env python3
"""
build_paprikarecipes.py — Genera un file .paprikarecipes da un JSON di ricette.

Uso:
  python3 build_paprikarecipes.py --input ricette.json --output output.paprikarecipes

Il JSON in input deve essere un array di oggetti con i campi Paprika 3:
  name, ingredients, directions, servings, prep_time, cook_time, total_time,
  description, notes, source, source_url, categories, difficulty, rating, photo_data

Tutti i campi tranne 'name', 'ingredients', 'directions' sono opzionali.
photo_data deve essere una stringa base64 di un JPEG (o null).
"""

import argparse, gzip, json, sys, uuid, zipfile
from datetime import datetime
from pathlib import Path


REQUIRED_FIELDS = {"name", "ingredients", "directions"}

DEFAULTS = {
    "servings": "",
    "source": "",
    "source_url": "",
    "prep_time": "",
    "cook_time": "",
    "total_time": "",
    "on_favorites": False,
    "categories": [],
    "rating": None,
    "description": "",
    "notes": "",
    "nutritional_info": "",
    "difficulty": "",
    "photo": None,
    "photo_data": None,
    "photo_hash": None,
    "photo_large": None,
    "image_url": "",
    "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
}


def normalize(recipe: dict) -> dict:
    """Merge defaults, generate uid/hash, validate required fields."""
    missing = REQUIRED_FIELDS - set(recipe.keys())
    if missing:
        raise ValueError(f"Ricetta '{recipe.get('name', '?')}': campi mancanti: {missing}")

    out = dict(DEFAULTS)
    out.update(recipe)

    # Garantisci uid e hash univoci
    if not out.get("uid"):
        out["uid"] = str(uuid.uuid4()).upper()
    if not out.get("hash"):
        out["hash"] = str(uuid.uuid4()).upper()

    # categories deve essere una lista
    if isinstance(out.get("categories"), str):
        out["categories"] = [c.strip() for c in out["categories"].split(",") if c.strip()]

    # Pulisci campi stringa None → ""
    for k, v in out.items():
        if v is None and k not in ("rating", "photo", "photo_data", "photo_hash", "photo_large"):
            out[k] = ""

    return out


def recipe_to_gz(recipe: dict) -> bytes:
    """Serializza la ricetta come gzip(JSON UTF-8)."""
    json_bytes = json.dumps(recipe, ensure_ascii=False, indent=2).encode("utf-8")
    return gzip.compress(json_bytes)


def build(input_path: Path, output_path: Path) -> list[str]:
    """Legge il JSON, genera il .paprikarecipes, restituisce i nomi delle ricette."""
    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        data = [data]  # singola ricetta passata come oggetto

    if not isinstance(data, list):
        raise ValueError("Il JSON deve essere un array (o un singolo oggetto) di ricette.")

    names = []
    with zipfile.ZipFile(str(output_path), "w", zipfile.ZIP_DEFLATED) as zf:
        for raw in data:
            recipe = normalize(raw)
            name_safe = recipe["name"].replace("/", "-").replace("\\", "-")
            filename = f"{name_safe}.paprikarecipe"
            zf.writestr(filename, recipe_to_gz(recipe))
            names.append(recipe["name"])

    return names


def main():
    parser = argparse.ArgumentParser(description="Genera .paprikarecipes da JSON")
    parser.add_argument("--input", required=True, help="File JSON con le ricette")
    parser.add_argument("--output", required=True, help="File .paprikarecipes di output")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"Errore: file non trovato: {input_path}", file=sys.stderr)
        sys.exit(1)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        names = build(input_path, output_path)
    except (ValueError, json.JSONDecodeError) as e:
        print(f"Errore: {e}", file=sys.stderr)
        sys.exit(1)

    size_kb = output_path.stat().st_size // 1024
    print(f"✅ {len(names)} ricetta/e → {output_path.name} ({size_kb} KB)")
    for n in names:
        print(f"   • {n}")


if __name__ == "__main__":
    main()
