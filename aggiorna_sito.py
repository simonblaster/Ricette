#!/usr/bin/env python3
"""
Genera il sito web statico delle ricette leggendo direttamente dal database Paprika 3.
Output nella cartella docs/ pronta per GitHub Pages.
Esegue anche un backup del database Paprika nella cartella "Backup Paprika/".

Uso:
  python3 aggiorna_sito.py
"""

import sqlite3, json, os, sys, re, shutil
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

# Mantieni solo gli ultimi 10 backup
backups = sorted(BACKUP_DIR.glob('Paprika_*.sqlite'))
for old in backups[:-10]:
    try:
        old.unlink()
    except Exception:
        pass

print(f"   ✅ {backup_name} ({backup_path.stat().st_size // 1024} KB)")

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

all_cats     = sorted(set(c for r in recipes_for_js for c in r['categories'] if c))
recipes_json = json.dumps(recipes_for_js, ensure_ascii=False, separators=(',', ':'))
cats_json    = json.dumps(all_cats, ensure_ascii=False, separators=(',', ':'))
updated      = datetime.now().strftime('%d/%m/%Y %H:%M')
n_recipes    = len(recipes_for_js)

# ── 5. Generazione HTML ───────────────────────────────────────────────────────
print("🌐 Generazione docs/index.html...")

HTML = f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Le mie ricette</title>
<style>
:root{{
  --bg:#faf7f2;--surface:#fff;--border:#e8e0d6;
  --text:#2c2412;--muted:#7a6a55;
  --accent:#c0674a;--accent2:#8b5a3c;
  --tag-bg:#f0e8df;--tag-color:#7a4a30;
  --shadow:0 2px 12px rgba(44,36,18,.10);
  --radius:14px;--font:'Segoe UI',system-ui,sans-serif;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--text);font-family:var(--font);min-height:100vh}}

/* ── Header ── */
header{{background:var(--accent);color:#fff;padding:1.5rem 1.25rem 1rem;
  position:sticky;top:0;z-index:100;box-shadow:0 2px 8px rgba(0,0,0,.18)}}
header h1{{font-size:1.5rem;font-weight:700;letter-spacing:.02em;margin-bottom:.75rem}}
header h1 span{{font-size:.9rem;opacity:.75;font-weight:400;margin-left:.5rem}}
.search-bar{{display:flex;gap:.5rem;align-items:center}}
.search-bar input{{flex:1;padding:.55rem .9rem;border:none;border-radius:99px;
  font-size:.95rem;background:rgba(255,255,255,.18);color:#fff;outline:none}}
.search-bar input::placeholder{{color:rgba(255,255,255,.65)}}
.search-bar input:focus{{background:rgba(255,255,255,.28)}}
#btn-favs{{background:rgba(255,255,255,.18);border:none;border-radius:99px;
  padding:.5rem .85rem;color:#fff;cursor:pointer;font-size:.9rem;white-space:nowrap;transition:.2s}}
#btn-favs.active,#btn-favs:hover{{background:rgba(255,255,255,.35)}}

/* ── Categorie ── */
.cats-bar{{padding:.75rem 1.25rem;display:flex;gap:.5rem;overflow-x:auto;
  border-bottom:1px solid var(--border);background:var(--surface);
  scrollbar-width:none;-webkit-overflow-scrolling:touch}}
.cats-bar::-webkit-scrollbar{{display:none}}
.cat-chip{{flex-shrink:0;padding:.35rem .85rem;border-radius:99px;border:1.5px solid var(--border);
  background:transparent;font-size:.82rem;cursor:pointer;color:var(--muted);
  transition:.18s;white-space:nowrap}}
.cat-chip:hover{{border-color:var(--accent);color:var(--accent)}}
.cat-chip.active{{background:var(--accent);border-color:var(--accent);color:#fff;font-weight:600}}

/* ── Stats bar ── */
.stats-bar{{padding:.5rem 1.25rem;font-size:.82rem;color:var(--muted);
  border-bottom:1px solid var(--border);background:var(--surface)}}

/* ── Griglia ── */
main{{padding:1.25rem;max-width:1400px;margin:0 auto}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:1rem}}
@media(max-width:480px){{.grid{{grid-template-columns:repeat(2,1fr);gap:.75rem}}}}

/* ── Card ── */
.card{{background:var(--surface);border-radius:var(--radius);overflow:hidden;
  box-shadow:var(--shadow);cursor:pointer;transition:.22s;border:1px solid var(--border)}}
.card:hover{{transform:translateY(-3px);box-shadow:0 6px 24px rgba(44,36,18,.15)}}
.card-photo{{width:100%;aspect-ratio:4/3;object-fit:cover;background:#ede8e0;display:block}}
.card-nophoto{{width:100%;aspect-ratio:4/3;background:linear-gradient(135deg,#f0e8df 0%,#e8ddd2 100%);
  display:flex;align-items:center;justify-content:center;font-size:2.5rem}}
.card-body{{padding:.7rem .8rem .8rem}}
.card-name{{font-size:.88rem;font-weight:600;line-height:1.3;margin-bottom:.4rem;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}}
.card-tags{{display:flex;flex-wrap:wrap;gap:.3rem}}
.tag{{font-size:.72rem;background:var(--tag-bg);color:var(--tag-color);border-radius:99px;padding:.15rem .55rem}}
.card-stars{{font-size:.75rem;color:#d4a017;margin-bottom:.25rem}}
.fav-badge{{float:right;font-size:.9rem}}

/* ── Modale ── */
.overlay{{position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:200;
  display:flex;align-items:flex-end;justify-content:center;
  opacity:0;pointer-events:none;transition:.25s}}
.overlay.open{{opacity:1;pointer-events:all}}
.modal{{background:var(--surface);border-radius:var(--radius) var(--radius) 0 0;
  width:100%;max-width:680px;max-height:92vh;overflow-y:auto;
  transform:translateY(100%);transition:.3s cubic-bezier(.4,0,.2,1);padding:0 0 2rem}}
.overlay.open .modal{{transform:translateY(0)}}
@media(min-width:600px){{
  .overlay{{align-items:center}}
  .modal{{border-radius:var(--radius);max-height:88vh}}
}}
.modal-photo{{width:100%;max-height:280px;object-fit:cover;display:block}}
.modal-nophoto{{width:100%;height:160px;
  background:linear-gradient(135deg,#f0e8df 0%,#e8ddd2 100%);
  display:flex;align-items:center;justify-content:center;font-size:4rem}}
.modal-content{{padding:1.25rem 1.25rem 0}}
.modal-name{{font-size:1.3rem;font-weight:700;margin-bottom:.5rem;line-height:1.3}}
.modal-meta{{display:flex;flex-wrap:wrap;gap:.75rem;font-size:.82rem;color:var(--muted);margin-bottom:.75rem}}
.modal-meta span{{display:flex;align-items:center;gap:.25rem}}
.modal-tags{{display:flex;flex-wrap:wrap;gap:.35rem;margin-bottom:.9rem}}
.modal-desc{{font-size:.9rem;color:var(--muted);margin-bottom:1rem;line-height:1.5;font-style:italic}}
.modal-section{{margin-bottom:1.2rem}}
.modal-section h3{{font-size:.95rem;font-weight:700;color:var(--accent2);
  text-transform:uppercase;letter-spacing:.07em;margin-bottom:.6rem;
  padding-bottom:.3rem;border-bottom:2px solid var(--tag-bg)}}
.ing-header{{font-size:.85rem;font-weight:700;color:var(--muted);
  margin:.6rem 0 .25rem;text-transform:uppercase;letter-spacing:.05em}}
.ing-list{{list-style:none}}
.ing-list li{{font-size:.9rem;padding:.2rem 0;border-bottom:1px solid var(--border);line-height:1.4}}
.ing-list li:last-child{{border-bottom:none}}
.directions-text{{font-size:.92rem;line-height:1.7;white-space:pre-wrap}}
.notes-text{{font-size:.88rem;line-height:1.6;color:var(--muted);
  background:var(--tag-bg);border-radius:8px;padding:.75rem 1rem;white-space:pre-wrap}}
.source-link{{font-size:.8rem;color:var(--accent);text-decoration:none;
  display:inline-flex;align-items:center;gap:.25rem;margin-top:.5rem}}
.source-link:hover{{text-decoration:underline}}
.recipe-link{{color:var(--accent);font-weight:600;text-decoration:none;cursor:pointer}}
.recipe-link:hover{{text-decoration:underline}}
.modal-close{{position:sticky;top:0;z-index:10;width:100%;display:flex;
  justify-content:flex-end;padding:.75rem 1rem .5rem;background:var(--surface)}}
.modal-close button{{background:var(--tag-bg);border:none;border-radius:99px;
  width:2rem;height:2rem;font-size:1.1rem;cursor:pointer;color:var(--muted);
  display:flex;align-items:center;justify-content:center}}

/* ── Vuoto ── */
.empty{{text-align:center;padding:4rem 1rem;color:var(--muted)}}
.empty .icon{{font-size:3rem;margin-bottom:.75rem}}
</style>
</head>
<body>

<header>
  <h1>Le mie ricette <span id="counter"></span></h1>
  <div class="search-bar">
    <input id="search" type="search" placeholder="🔍 Cerca ricetta…" autocomplete="off">
    <button id="btn-favs" title="Solo preferiti">⭐</button>
  </div>
</header>

<div class="cats-bar" id="cats-bar">
  <button class="cat-chip active" data-cat="" onclick="setCat('')">Tutte</button>
</div>

<div class="stats-bar" id="stats-bar"></div>

<main>
  <div class="grid" id="grid"></div>
  <div class="empty" id="empty" style="display:none">
    <div class="icon">🍽️</div>
    <p>Nessuna ricetta trovata.</p>
  </div>
</main>

<div class="overlay" id="overlay" role="dialog" aria-modal="true">
  <div class="modal" id="modal">
    <div class="modal-close"><button id="btn-close" aria-label="Chiudi">✕</button></div>
    <div id="modal-inner"></div>
  </div>
</div>

<script>
const RECIPES={recipes_json};
const CATS={cats_json};
const UPDATED="{updated}";

let filterCat='', filterText='', filterFavs=false;

const catsBar=document.getElementById('cats-bar');
CATS.forEach(cat=>{{
  const btn=document.createElement('button');
  btn.className='cat-chip'; btn.dataset.cat=cat; btn.textContent=cat;
  btn.onclick=()=>setCat(cat);
  catsBar.appendChild(btn);
}});

function setCat(cat){{
  filterCat=cat;
  document.querySelectorAll('.cat-chip').forEach(b=>b.classList.toggle('active',b.dataset.cat===cat));
  render();
}}

document.getElementById('search').addEventListener('input',e=>{{
  filterText=e.target.value.toLowerCase().trim(); render();
}});

document.getElementById('btn-favs').addEventListener('click',()=>{{
  filterFavs=!filterFavs;
  document.getElementById('btn-favs').classList.toggle('active',filterFavs);
  render();
}});

function stars(n){{
  if(!n) return '';
  const s=Math.min(5,Math.max(0,Math.round(n)));
  return '★'.repeat(s)+'☆'.repeat(5-s);
}}

function filtered(){{
  return RECIPES.filter(r=>{{
    if(filterFavs && !r.favorites) return false;
    if(filterCat && !r.categories.includes(filterCat)) return false;
    if(filterText){{
      const hay=(r.name+' '+r.categories.join(' ')+' '+r.description).toLowerCase();
      if(!hay.includes(filterText)) return false;
    }}
    return true;
  }});
}}

function render(){{
  const list=filtered();
  const grid=document.getElementById('grid');
  const empty=document.getElementById('empty');
  const counter=document.getElementById('counter');
  const stats=document.getElementById('stats-bar');

  counter.textContent='('+(list.length==={n_recipes}?{n_recipes}:list.length+' / '+{n_recipes})+' ricette)';
  stats.textContent=list.length==={n_recipes}
    ? `Tutte le ${{list.length}} ricette · aggiornato ${{UPDATED}}`
    : `${{list.length}} di {n_recipes} ricette`;

  if(!list.length){{ grid.innerHTML=''; empty.style.display=''; return; }}
  empty.style.display='none';

  grid.innerHTML=list.map(r=>{{
    const photo=r.has_photo
      ? `<img class="card-photo" src="photos/${{r.uid}}.jpg" alt="${{esc(r.name)}}" loading="lazy">`
      : `<div class="card-nophoto">🍽️</div>`;
    const tags=r.categories.slice(0,2).map(c=>`<span class="tag">${{esc(c)}}</span>`).join('');
    const fav=r.favorites?'<span class="fav-badge">⭐</span>':'';
    const strs=r.rating?`<div class="card-stars">${{stars(r.rating)}}</div>`:'';
    return `<div class="card" data-uid="${{r.uid}}" onclick="openModal('${{r.uid}}')" tabindex="0" role="button">
      ${{photo}}
      <div class="card-body">
        ${{strs}}<div class="card-name">${{fav}}${{esc(r.name)}}</div>
        <div class="card-tags">${{tags}}</div>
      </div>
    </div>`;
  }}).join('');
}}

const overlay=document.getElementById('overlay');
const modal=document.getElementById('modal');

function openModal(uid){{
  const r=RECIPES.find(x=>x.uid===uid);
  if(!r) return;

  const photo=r.has_photo
    ? `<img class="modal-photo" src="photos/${{r.uid}}.jpg" alt="${{esc(r.name)}}">`
    : `<div class="modal-nophoto">🍽️</div>`;

  const meta=[];
  if(r.servings) meta.push(`<span>👥 ${{esc(r.servings)}}</span>`);
  if(r.prep_time) meta.push(`<span>⏱ Prep: ${{esc(r.prep_time)}}</span>`);
  if(r.cook_time) meta.push(`<span>🔥 Cottura: ${{esc(r.cook_time)}}</span>`);
  if(r.total_time) meta.push(`<span>⏰ Totale: ${{esc(r.total_time)}}</span>`);
  if(r.rating) meta.push(`<span style="color:#d4a017">${{stars(r.rating)}}</span>`);

  const tags=r.categories.map(c=>`<span class="tag">${{esc(c)}}</span>`).join('');
  const fav=r.favorites?' ⭐':'';

  let ingHtml='';
  if(r.ingredients && r.ingredients.length){{
    ingHtml='<div class="modal-section"><h3>Ingredienti</h3><ul class="ing-list">';
    r.ingredients.forEach(item=>{{
      if(item.type==='header'){{
        ingHtml+=`</ul><div class="ing-header">${{esc(item.text)}}</div><ul class="ing-list">`;
      }} else {{
        const fb=item.text.match(/^\*\*(.+)\*\*$/);
        if(fb) ingHtml+=`</ul><div class="ing-header" style="color:var(--accent2)">${{esc(fb[1])}}</div><ul class="ing-list">`;
        else ingHtml+=`<li>${{renderIngText(item.text)}}</li>`;
      }}
    }});
    ingHtml+='</ul></div>';
  }}

  let dirHtml='';
  if(r.directions){{
    dirHtml=`<div class="modal-section"><h3>Procedimento</h3>
      <div class="directions-text">${{md(r.directions)}}</div></div>`;
  }}

  let notesHtml='';
  if(r.notes){{
    notesHtml=`<div class="modal-section"><h3>Note</h3>
      <div class="notes-text">${{esc(r.notes)}}</div></div>`;
  }}

  let srcHtml='';
  if(r.source_url){{
    srcHtml=`<a class="source-link" href="${{r.source_url}}" target="_blank" rel="noopener">
      🔗 ${{esc(r.source||r.source_url)}}</a>`;
  }} else if(r.source){{
    srcHtml=`<span class="source-link">📖 ${{esc(r.source)}}</span>`;
  }}

  document.getElementById('modal-inner').innerHTML=`
    ${{photo}}
    <div class="modal-content">
      <div class="modal-name">${{esc(r.name)}}${{fav}}</div>
      <div class="modal-meta">${{meta.join('')}}</div>
      <div class="modal-tags">${{tags}}</div>
      ${{r.description?`<div class="modal-desc">${{esc(r.description)}}</div>`:''}}
      ${{dirHtml}}${{ingHtml}}${{notesHtml}}${{srcHtml}}
    </div>`;

  overlay.classList.add('open');
  modal.scrollTop=0;
  document.body.style.overflow='hidden';
}}

function closeModal(){{
  overlay.classList.remove('open');
  document.body.style.overflow='';
}}

document.getElementById('btn-close').onclick=closeModal;
overlay.addEventListener('click',e=>{{ if(e.target===overlay) closeModal(); }});
document.addEventListener('keydown',e=>{{ if(e.key==='Escape') closeModal(); }});

function esc(s){{
  return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}}

// Render **bold** markdown
function md(text){{
  return esc(text).replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>');
}}

// Index recipes by name for [recipe:...] links
const recipeByName={{}};
RECIPES.forEach(r=>{{ recipeByName[r.name]=r.uid; }});

// Render ingredient text: handles [recipe:Name] links and **bold**
function renderIngText(text){{
  const rm=text.match(/^\[recipe:(.+?)\](.*)/);
  if(rm){{
    const name=rm[1].trim();
    const rest=(rm[2]||'').trim();
    const uid=recipeByName[name];
    const link=uid
      ?`<a href="#" class="recipe-link" onclick="openModal('${{uid}}');return false;">${{esc(name)}}</a>`
      :`<em>${{esc(name)}}</em>`;
    return rest?link+' '+esc(rest):link;
  }}
  return esc(text).replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>');
}}

render();
</script>
</body>
</html>
"""

(DOCS_DIR / "index.html").write_text(HTML, encoding='utf-8')
print(f"   ✅ {n_recipes} ricette, {len(all_cats)} categorie")

# ── 6. .nojekyll per GitHub Pages ─────────────────────────────────────────────
(DOCS_DIR / ".nojekyll").write_text("")

print(f"\n✅ Fatto! {n_recipes} ricette · backup in 'Backup Paprika/{backup_name}'")
