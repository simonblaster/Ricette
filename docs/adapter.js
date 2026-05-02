// Adapter: trasforma RECIPES_RAW (formato sorgente del sito originale)
// nel formato consumato dal prototipo (window.RECIPES + window.CATEGORIES).
//
// Formato sorgente per ogni ricetta:
//   uid, name, categories[], servings, prep_time, cook_time, total_time,
//   description, ingredients[{type:'item'|'header', text}], directions,
//   notes, rating, source, source_url, has_photo, favorites
//
// Formato prototipo per ogni ricetta:
//   id, uid, nome, categoria (primaria), tag[], tempo (min), porzioni (n),
//   porzioniLabel, difficolta, descrizione, ingredienti[{q,u,n,qb,header}],
//   passi[], rating, source, photo, has_photo, favorites, source_url, notes
//
// Tutta la logica di conversione è qui — un solo punto da aggiornare se cambia
// il formato sorgente.

(function () {
  const raw = window.RECIPES_RAW || [];
  const cats = window.CATS_RAW || [];

  // Priorità categorie: la più specifica vince come "categoria primaria"
  const CAT_PRIORITY = ['Messinese', 'Manzo', 'Maiale', 'Pollo', 'Pasqua', 'Desserts',
    'Pizze, focacce & co.', 'Impasti per pizze, focacce & co.', 'Pane', 'Ricette base',
    'Aiutacuochi', '30 minuti'];

  // Estrae numero di porzioni da string tipo "6 persone", "Per 4", "4-6 persone"
  function parsePorzioni(s) {
    if (!s) return { n: 4, label: '' };
    const m = String(s).match(/(\d+)/);
    return { n: m ? parseInt(m[1], 10) : 4, label: s };
  }

  // Estrae minuti da string tipo "30 min", "1 h 30 min", "2 ore"
  function parseTime(s) {
    if (!s) return null;
    const str = String(s).toLowerCase();
    let total = 0;
    const h = str.match(/(\d+)\s*h|(\d+)\s*or[ae]/);
    if (h) total += parseInt(h[1] || h[2], 10) * 60;
    const m = str.match(/(\d+)\s*min/);
    if (m) total += parseInt(m[1], 10);
    if (!total) {
      const onlyN = str.match(/^\s*(\d+)\s*$/);
      if (onlyN) total = parseInt(onlyN[1], 10);
    }
    return total || null;
  }

  // Parser di un ingrediente "1 kg lacerto" / "500 g cipolle" / "olio evo" / "Sale q.b."
  // Gestisce anche formato invertito "Farina 00, 500 g" e senza spazio "50g cheddar"
  // Ritorna {q, u, n, qb}
  function parseIngredient(text) {
    const t = String(text || '').trim();
    if (!t) return { q: '', u: '', n: '', qb: true };

    // q.b. esplicito
    const qbMatch = t.match(/^(.+?)\s+q\.?\s*b\.?\s*$/i);
    if (qbMatch) return { q: '', u: '', n: qbMatch[1].trim(), qb: true };
    if (/^q\.?\s*b\.?$/i.test(t)) return { q: '', u: '', n: t, qb: true };

    // unità riconosciute (riusato in più regex)
    const U = 'kg|g|ml|cl|dl|l|mg|oz|lb|cucchiain[oi]|cucchia[ioy]|bicchier[ie]|tazz[ae]|pizzich[io]|mazzett[oi]|manciat[ae]|spicch[ioi]|fogli[ae]|fett[ae]|filett[oi]|panett[oi]';

    // "200 g cipolle" / "1.5 kg pasta" / "50g cheddar" (senza spazio tra numero e unità)
    const unitRe = new RegExp('^(\\d+(?:[\\.,]\\d+)?(?:\\s*/\\s*\\d+)?|\\d+\\s+\\d+/\\d+)\\s*(' + U + ')\\b\\.?\\s*(.*)$', 'i');
    const um = t.match(unitRe);
    if (um) return { q: um[1].replace(',', '.'), u: um[2], n: (um[3] || '').trim(), qb: false };

    // "1 cipolla" / "3 uova" — quantità senza unità
    const numRe = /^(\d+(?:[\.,]\d+)?|\d+\/\d+)\s+(.+)$/;
    const nm = t.match(numRe);
    if (nm) return { q: nm[1].replace(',', '.'), u: '', n: nm[2].trim(), qb: false };

    // "Farina 00 W350, 500 g" / "Sale, 22 g" — formato invertito Nome, quantità [unità]
    const revRe = new RegExp('^(.+?),\\s*(\\d+(?:[\\.,]\\d+)?(?:\\s*/\\s*\\d+)?)\\s*(' + U + ')?\\s*$', 'i');
    const rm = t.match(revRe);
    if (rm) return { q: rm[2].replace(',', '.'), u: (rm[3] || '').trim(), n: rm[1].trim(), qb: false };

    // "Olio evo" — solo nome → q.b.
    return { q: '', u: '', n: t, qb: true };
  }

  // Trasforma directions (testo libero con \n\n tra passi) in array passi.
  function parseDirections(s) {
    if (!s) return [];
    return String(s).split(/\n\s*\n/).map(p => p.trim()).filter(Boolean);
  }

  // Categoria primaria: prendi la più specifica (priorità) tra quelle assegnate.
  function pickPrimary(categories) {
    const cs = categories || [];
    for (const c of CAT_PRIORITY) if (cs.includes(c)) return c;
    return cs[0] || 'Altro';
  }

  // Difficoltà derivata: rating>=4 → "Provata", 1-3 → "Da provare", 0 → "Nuova"
  function difficolta(r) {
    if (r >= 4) return 'Provata';
    if (r >= 1) return 'Da provare';
    return 'Nuova';
  }

  const transformed = raw.map((r) => {
    const por = parsePorzioni(r.servings);
    const ingredienti = (r.ingredients || []).map(it => {
      if (it.type === 'header') return { header: true, n: it.text };
      // Bold-as-header: "**Header**"
      const bm = (it.text || '').match(/^\*\*(.+)\*\*$/);
      if (bm) return { header: true, n: bm[1] };
      return parseIngredient(it.text);
    });
    return {
      id: r.uid,
      uid: r.uid,
      nome: r.name,
      categoria: pickPrimary(r.categories),
      tag: r.categories || [],
      tempo: parseTime(r.total_time) || parseTime(r.cook_time) || parseTime(r.prep_time) || 0,
      porzioni: por.n,
      porzioniLabel: por.label,
      difficolta: difficolta(r.rating || 0),
      descrizione: r.description || '',
      ingredienti,
      passi: parseDirections(r.directions),
      rating: r.rating || 0,
      source: r.source || '',
      source_url: r.source_url || '',
      notes: r.notes || '',
      has_photo: !!(window.PHOTO_UIDS && window.PHOTO_UIDS.has(r.uid)),
      favorites: !!r.favorites,
      photo: (window.PHOTO_UIDS && window.PHOTO_UIDS.has(r.uid)) ? `photos/${r.uid}.jpg` : null,
    };
  });

  window.RECIPES = transformed;
  window.CATEGORIES = ['Tutte', ...cats];
})();
