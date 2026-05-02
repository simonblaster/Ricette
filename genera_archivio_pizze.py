#!/usr/bin/env python3
"""
Genera docs/pizze-che-raccontano-una-storia.html da menu_pizzerie.json.
Uso: python3 genera_archivio_pizze.py
"""

import json, os
from pathlib import Path
from datetime import datetime

BASE     = Path(__file__).parent
DB       = BASE / "menu_pizzerie.json"
OUT      = BASE / "docs" / "pizze-che-raccontano-una-storia.html"
UPDATED  = datetime.now().strftime("%d/%m/%Y")

with open(DB, encoding="utf-8") as f:
    db = json.load(f)

pizzerie = db["pizzerie"]
all_pizze = []
for piz in pizzerie:
    for p in piz["pizze"]:
        all_pizze.append({**p, "_pizzeria": piz["nome"], "_citta": piz["citta"], "_maestro": piz["maestro"]})

n_pizze    = len(all_pizze)
n_pizzerie = len(pizzerie)

# Valori unici per filtri
all_tipi      = sorted(set(p["tipo"] for p in all_pizze))
all_pizzerie  = [p["nome"] for p in pizzerie]
all_tags      = sorted(set(t for p in all_pizze for t in p.get("tags", [])))

TIPO_EMOJI = {"rossa": "🍅", "bianca": "🤍", "calzone": "🥙", "fritta": "🔥"}

data_js = json.dumps(all_pizze, ensure_ascii=False)
pizzerie_js = json.dumps([
    {"nome": p["nome"], "citta": p["citta"], "maestro": p["maestro"], "stile": p["stile"], "note_menu": p.get("note_menu", "")}
    for p in pizzerie
], ensure_ascii=False)

tipi_btns = "\n".join(
    f'<button class="btn tipo-btn" data-tipo="{t}" onclick="toggleFilter(this,\'tipo\')">{TIPO_EMOJI.get(t,"")} {t}</button>'
    for t in all_tipi
)
pizzerie_btns = "\n".join(
    f'<button class="btn piz-btn" data-piz="{p["nome"]}" onclick="toggleFilter(this,\'piz\')">{p["nome"]}</button>'
    for p in pizzerie
)
tag_btns = "\n".join(
    f'<button class="btn tag-btn" data-tag="{t}" onclick="toggleFilter(this,\'tag\')">{t}</button>'
    for t in all_tags
)

HTML = f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Pizze che raccontano una storia</title>
<style>
  :root {{
    --bg: #f5f3ef; --surface: #fff; --surface2: #f0ede8;
    --border: #ddd; --accent: #c0392b; --accent-light: #fdf0ef;
    --text: #1a1a1a; --muted: #777; --radius: 10px;
    --shadow: 0 1px 4px rgba(0,0,0,0.08);
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; min-height: 100vh; }}

  header {{ background: var(--surface); border-bottom: 1px solid var(--border); padding: 14px 16px; position: sticky; top: 0; z-index: 100; box-shadow: var(--shadow); }}
  .header-top {{ display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }}
  h1 {{ font-size: 1.2rem; font-weight: 700; flex: 1; min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  h1 span {{ color: var(--accent); }}
  #count {{ color: var(--muted); font-size: 0.78rem; white-space: nowrap; }}

  .toolbar {{ display: flex; gap: 8px; margin-top: 10px; align-items: center; }}
  .search-wrap {{ position: relative; flex: 1; }}
  .search-wrap input {{ background: var(--surface2); border: 1px solid var(--border); border-radius: 20px; color: var(--text); font-size: 0.85rem; padding: 7px 12px 7px 32px; width: 100%; outline: none; -webkit-appearance: none; }}
  .search-wrap input:focus {{ border-color: var(--accent); background: #fff; }}
  .search-icon {{ position: absolute; left: 10px; top: 50%; transform: translateY(-50%); font-size: 0.75rem; pointer-events: none; }}
  .btn-filter-toggle {{ background: var(--surface2); border: 1px solid var(--border); border-radius: 20px; color: var(--text); font-size: 0.82rem; padding: 7px 14px; cursor: pointer; white-space: nowrap; display: flex; align-items: center; gap: 5px; }}
  .btn-filter-toggle.has-active {{ background: var(--accent); border-color: var(--accent); color: #fff; }}
  .btn-clear {{ background: transparent; border: 1px solid #ccc; border-radius: 20px; color: var(--muted); font-size: 0.82rem; padding: 7px 12px; cursor: pointer; white-space: nowrap; }}

  .filter-panel {{ overflow: hidden; max-height: 0; transition: max-height 0.25s ease; }}
  .filter-panel.open {{ max-height: 600px; }}
  .filters {{ padding-top: 10px; display: flex; flex-direction: column; gap: 8px; }}
  .filter-row {{ display: flex; flex-wrap: wrap; gap: 5px; align-items: center; }}
  .filter-label {{ font-size: 0.65rem; text-transform: uppercase; letter-spacing: 1px; color: var(--muted); min-width: 52px; }}
  .btn {{ display: inline-flex; align-items: center; gap: 3px; padding: 4px 10px; border-radius: 20px; border: 1px solid var(--border); background: var(--surface); color: #444; font-size: 0.78rem; cursor: pointer; transition: all 0.12s; user-select: none; white-space: nowrap; -webkit-tap-highlight-color: transparent; }}
  .btn:active, .btn:hover {{ border-color: var(--accent); color: var(--accent); background: var(--accent-light); }}
  .btn.active {{ background: var(--accent); border-color: var(--accent); color: #fff; font-weight: 600; }}

  .main {{ padding: 14px 16px; max-width: 1600px; margin: 0 auto; }}
  .section-header {{ font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1.5px; color: var(--muted); margin: 20px 0 10px; border-bottom: 1px solid var(--border); padding-bottom: 5px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(270px, 1fr)); gap: 10px; }}

  .card {{ background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 14px 16px; box-shadow: var(--shadow); }}
  .card-header {{ display: flex; align-items: flex-start; justify-content: space-between; gap: 6px; margin-bottom: 5px; }}
  .card-name {{ font-size: 0.95rem; font-weight: 600; line-height: 1.3; }}
  .tipo-badge {{ font-size: 1.1rem; flex-shrink: 0; }}
  .card-meta {{ font-size: 0.67rem; color: var(--muted); margin-bottom: 7px; display: flex; gap: 5px; flex-wrap: wrap; align-items: center; }}
  .cat-badge {{ background: var(--surface2); border-radius: 4px; padding: 1px 5px; border: 1px solid var(--border); }}
  .ingredienti {{ font-size: 0.8rem; color: #555; line-height: 1.55; }}
  .note {{ font-size: 0.71rem; color: var(--muted); font-style: italic; border-top: 1px solid var(--border); padding-top: 6px; margin-top: 8px; }}
  .empty {{ text-align: center; padding: 60px 20px; color: var(--muted); font-size: 1rem; }}
  .tag-chip {{ display: inline-block; font-size: 0.65rem; background: var(--accent-light); color: var(--accent); border-radius: 4px; padding: 1px 5px; margin: 1px; }}

  @media (min-width: 640px) {{
    header {{ padding: 16px 24px; }}
    h1 {{ font-size: 1.4rem; }}
    .filter-panel {{ max-height: none !important; overflow: visible; }}
    .btn-filter-toggle, .btn-clear {{ display: none; }}
    .toolbar {{ margin-top: 0; }}
    .filters {{ padding-top: 0; margin-top: 10px; }}
    .main {{ padding: 18px 24px; }}
  }}
</style>
</head>
<body>
<header>
  <div class="header-top">
    <h1>🍕 <span>Pizze che raccontano</span> una storia</h1>
    <span id="count">{n_pizze} pizze &middot; {n_pizzerie} pizzerie</span>
  </div>
  <div class="toolbar">
    <div class="search-wrap">
      <span class="search-icon">🔍</span>
      <input type="text" id="search" placeholder="cerca nome, ingrediente…" oninput="applyFilters()">
    </div>
    <button class="btn-filter-toggle" id="btn-toggle" onclick="togglePanel()">⚙️ Filtri</button>
    <button class="btn-clear" onclick="clearAll()">✕ Reset</button>
  </div>
  <div class="filter-panel" id="filter-panel">
    <div class="filters">
      <div class="filter-row">
        <span class="filter-label">Tipo</span>
        {tipi_btns}
      </div>
      <div class="filter-row">
        <span class="filter-label">Pizzeria</span>
        {pizzerie_btns}
      </div>
      <div class="filter-row">
        <span class="filter-label">Tag</span>
        {tag_btns}
      </div>
    </div>
  </div>
</header>

<div class="main">
  <div id="output"></div>
</div>

<script>
const PIZZE = {data_js};
const PIZZERIE = {pizzerie_js};
const TIPO_EMOJI = {{"rossa":"🍅","bianca":"🤍","calzone":"🥙","fritta":"🔥"}};

let filters = {{ tipo: null, piz: null, tag: null }};

function togglePanel() {{
  const p = document.getElementById('filter-panel');
  p.classList.toggle('open');
}}

function toggleFilter(btn, key) {{
  const val = btn.dataset[key] || btn.dataset.tipo || btn.dataset.piz || btn.dataset.tag;
  const active = btn.classList.contains('active');
  document.querySelectorAll('.' + key + '-btn, .tipo-btn, .piz-btn, .tag-btn').forEach(b => {{
    if (b.dataset[key] !== undefined || b.dataset.tipo !== undefined || b.dataset.piz !== undefined || b.dataset.tag !== undefined) {{
      if (b === btn) return;
    }}
  }});
  // deactivate all in group
  const groupClass = key === 'tipo' ? 'tipo-btn' : key === 'piz' ? 'piz-btn' : 'tag-btn';
  document.querySelectorAll('.' + groupClass).forEach(b => b.classList.remove('active'));
  if (!active) {{ btn.classList.add('active'); filters[key] = val; }}
  else {{ filters[key] = null; }}
  updateToggleStyle();
  applyFilters();
}}

function updateToggleStyle() {{
  const hasActive = Object.values(filters).some(v => v);
  document.getElementById('btn-toggle').classList.toggle('has-active', hasActive);
}}

function clearAll() {{
  filters = {{ tipo: null, piz: null, tag: null }};
  document.querySelectorAll('.btn').forEach(b => b.classList.remove('active'));
  document.getElementById('search').value = '';
  updateToggleStyle();
  applyFilters();
}}

function esc(s) {{
  return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}}

function applyFilters() {{
  const q = document.getElementById('search').value.toLowerCase().trim();
  let risultati = PIZZE.filter(p => {{
    if (filters.tipo && p.tipo !== filters.tipo) return false;
    if (filters.piz && p._pizzeria !== filters.piz) return false;
    if (filters.tag && !(p.tags||[]).includes(filters.tag)) return false;
    if (q) {{
      const hay = (p.nome + ' ' + (p.ingredienti||[]).join(' ') + ' ' + p._pizzeria + ' ' + (p.tags||[]).join(' ')).toLowerCase();
      if (!hay.includes(q)) return false;
    }}
    return true;
  }});

  document.getElementById('count').textContent = risultati.length + ' pizze · {n_pizzerie} pizzerie';

  if (!risultati.length) {{
    document.getElementById('output').innerHTML = '<div class="empty">Nessuna pizza trovata 🍕</div>';
    return;
  }}

  // Raggruppa per pizzeria
  const byPizzeria = {{}};
  risultati.forEach(p => {{
    if (!byPizzeria[p._pizzeria]) byPizzeria[p._pizzeria] = [];
    byPizzeria[p._pizzeria].push(p);
  }});

  let html = '';
  PIZZERIE.forEach(piz => {{
    const lista = byPizzeria[piz.nome];
    if (!lista || !lista.length) return;
    html += `<div class="section-header">${{esc(piz.nome)}} — ${{esc(piz.maestro)}}, ${{esc(piz.citta)}} (${{lista.length}})</div>`;
    html += '<div class="grid">';
    lista.forEach(p => {{
      const emoji = TIPO_EMOJI[p.tipo] || '🍕';
      const tags = (p.tags||[]).map(t => `<span class="tag-chip">${{esc(t)}}</span>`).join('');
      const ing = (p.ingredienti||[]).map(i => esc(i)).join(', ');
      const nota = p.note ? `<div class="note">${{esc(p.note)}}</div>` : '';
      html += `
        <div class="card">
          <div class="card-header">
            <div class="card-name">${{esc(p.nome)}}</div>
            <span class="tipo-badge">${{emoji}}</span>
          </div>
          <div class="card-meta">
            <span class="cat-badge">${{esc(p.categoria||'')}}</span>
          </div>
          <div class="ingredienti">${{ing}}</div>
          ${{tags ? '<div style="margin-top:6px">' + tags + '</div>' : ''}}
          ${{nota}}
        </div>`;
    }});
    html += '</div>';
  }});

  document.getElementById('output').innerHTML = html;
}}

applyFilters();
</script>
</body>
</html>
"""

OUT.write_text(HTML, encoding="utf-8")
print(f"✅ Generato: {OUT}")
print(f"   {n_pizze} pizze · {n_pizzerie} pizzerie · aggiornato {UPDATED}")
