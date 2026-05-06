// Mobile screens — Recipees
// 6 schermate: Home, Detail, Search, Cook (step), Shopping, Profile
// Usano il design system da v2/system.jsx + dati da data.jsx (window.RECIPES)

// ─── Helper: converte [recipe:Nome] → pulsante React navigabile ────────────
function renderWithLinks(text, goFn) {
  if (!text) return null;
  // Normalizza apostrofi per il lookup (dritto ↔ curvo)
  const na = s => s.replace(/['']/g, "'");
  const findR = n => window.RECIPES.find(r => na(r.nome) === na(n));
  // Renderizza i tag [recipe:…] inline su una riga
  const inline = (line, k) => {
    if (!line.includes('[recipe:')) return <span key={k}>{line}</span>;
    const segs = line.split(/(\[recipe:[^\]]+\])/);
    return <span key={k}>{segs.map((s, i) => {
      const m = s.match(/^\[recipe:(.+)\]$/);
      if (!m) return s;
      const linked = findR(m[1]);
      if (linked) return (
        <button key={i} onClick={e => { e.stopPropagation(); goFn(linked.id); }}
          className="rcp-btn"
          style={{ color: T.accent, fontStyle: 'italic', fontWeight: 600,
            textDecoration: 'underline', textDecorationStyle: 'dotted',
            display: 'inline', padding: 0, fontSize: 'inherit',
            lineHeight: 'inherit', verticalAlign: 'baseline' }}>
          {linked.nome}
        </button>
      );
      return <em key={i} style={{ color: T.accent }}>{m[1]}</em>;
    })}</span>;
  };
  // Se non ci sono header di sezione, renderizza inline (descrizione / passi)
  if (!text.includes('== ')) {
    if (!text.includes('[recipe:')) return text;
    return inline(text, 0);
  }
  // Rendering a blocchi per le note con sezioni == Header ==
  return text.split('\n').map((line, i) => {
    const hm = line.match(/^== (.+) ==$/);
    if (hm) return (
      <div key={i} style={{ fontFamily: T.serif, fontWeight: 600, fontStyle: 'normal',
        fontSize: 11, letterSpacing: 0.7, textTransform: 'uppercase',
        color: T.ink, marginTop: 10, marginBottom: 2 }}>
        {hm[1]}
      </div>
    );
    if (!line.trim()) return <div key={i} style={{ height: 4 }} />;
    return <div key={i}>{inline(line, i)}</div>;
  });
}

// ─── Bottom nav riusabile ───────────────────────────────────
function BottomNav({ active, go }) {
  const items = [
    { k: 'home', l: 'Casa', I: II.home },
    { k: 'search', l: 'Cerca', I: II.search },
    { k: 'shopping', l: 'Spesa', I: II.cart },
    { k: 'profile', l: 'Tu', I: II.user },
  ];
  return (
    <div style={{
      position: 'absolute', bottom: 0, left: 0, right: 0,
      background: 'color-mix(in oklab, ' + T.bg + ' 96%, transparent)',
      backdropFilter: 'blur(14px)', borderTop: `1px solid ${T.ruleSoft}`,
      display: 'flex', justifyContent: 'space-around', padding: '8px 8px 14px',
      zIndex: 5,
    }}>
      {items.map((it) => {
        const a = active === it.k;
        return (
          <button key={it.k} className="rcp-btn rcp-press" onClick={() => go(it.k)}
            style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 3, padding: '4px 12px', color: a ? T.ink : T.muted }}>
            <it.I size={18} strokeWidth={a ? 1.8 : 1.4} />
            <span style={{ fontSize: 10, fontWeight: a ? 600 : 500, letterSpacing: 0.2 }}>{it.l}</span>
          </button>
        );
      })}
    </div>
  );
}

// ─── HOME ───────────────────────────────────────────────────
function MobileHome({ go }) {
  const store = useStore();
  const fbUser = window.useFirebaseUser ? window.useFirebaseUser() : null;
  const featured = (window.RECIPES.find(r => r.rating >= 4 && (r.passi?.length ?? 0) > 2) || window.RECIPES[0]) || {};
  const featNome = featured.nome || 'Senza titolo';
  const featDescr = featured.descrizione || '';
  const recents = (store?.history || []).map((id) => window.RECIPES.find((r) => r.id === id)).filter(Boolean);
  const all = window.RECIPES;
  const firstName = fbUser ? (fbUser.displayName || 'chef').split(' ')[0] : 'Simone';
  // Tutti gli ID nell'ordine dell'indice (usato per navigazione prev/next)
  const allIds = all.map(r => r.id);
  return (
    <Frame>
      <div className="rcp-scroll" style={{ flex: 1, padding: '18px 18px 90px' }}>
        {/* masthead */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 18 }}>
          <div>
            <Eyebrow color={T.accent}>Cosa cuciniamo,</Eyebrow>
            <h1 style={{ fontFamily: T.serif, fontSize: 30, fontWeight: 500, letterSpacing: -0.8, margin: '4px 0 0', lineHeight: 0.95 }}>
              <span style={{ fontStyle: 'italic' }}>{firstName}?</span>
            </h1>
          </div>
          {/* Avatar — cliccabile: profilo se loggato, login se no */}
          <button className="rcp-btn rcp-press"
            onClick={() => { if (fbUser) { go('profile'); } else if (window._firebaseAuth) { window.loginGoogle && window.loginGoogle(); } }}
            style={{ width: 36, height: 36, borderRadius: 18, background: T.card, border: `1px solid ${T.ruleSoft}`, overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
            {fbUser && fbUser.photoURL
              ? <img src={fbUser.photoURL} style={{ width: 36, height: 36, objectFit: 'cover' }} alt="" />
              : <II.user size={16} />}
          </button>
        </div>

        {/* search bar */}
        <button onClick={() => go('search')} className="rcp-btn"
          style={{ display: 'flex', alignItems: 'center', gap: 10, width: '100%',
            background: T.card, border: `1px solid ${T.ruleSoft}`, borderRadius: 14,
            padding: '12px 14px', marginBottom: 22, color: T.muted, fontSize: 13 }}>
          <II.search size={14} />
          <span style={{ flex: 1, textAlign: 'left' }}>Cerca tra le ricette o per ingrediente</span>
          <Tag kind="ghost">⌘K</Tag>
        </button>

        {/* featured editorial card */}
        <button onClick={() => go('detail', { recipeId: featured.id, contextIds: allIds })} className="rcp-btn rcp-press"
          style={{ display: 'block', width: '100%', textAlign: 'left', marginBottom: 26 }}>
          <Eyebrow color={T.accent}>Della settimana · №27</Eyebrow>
          <div style={{ marginTop: 8, position: 'relative', borderRadius: 4, overflow: 'hidden' }}>
            <Photo src={featured.photo} label={featured.nome} tone="#d4c8a8" text="#3a2f15" ratio="16/9" />
          </div>
          <h2 style={{ fontFamily: T.serif, fontSize: 26, fontWeight: 500, letterSpacing: -0.6, margin: '12px 0 4px', lineHeight: 1 }}>
            <span style={{ fontStyle: 'italic' }}>{featNome.split(' ')[0]}</span> {featNome.split(' ').slice(1).join(' ')}
          </h2>
          <p style={{ margin: 0, fontSize: 13, color: T.muted, lineHeight: 1.5, fontFamily: T.serif, fontStyle: 'italic' }}>
            {featDescr}
          </p>
          <div style={{ display: 'flex', gap: 6, marginTop: 10 }}>
            <Tag>{fmtTimeLong(featured.tempo)}</Tag>
            <Tag kind="olive">{featured.categoria}</Tag>
            <Tag>{featured.difficolta}</Tag>
          </div>
        </button>

        {/* recents — horizontal scroll */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 10 }}>
          <Eyebrow>· Cucinato di recente</Eyebrow>
          <button className="rcp-btn" style={{ fontSize: 11, color: T.accent, fontWeight: 600 }}>Tutto →</button>
        </div>
        <div className="rcp-scroll" style={{ display: 'flex', gap: 10, overflowX: 'auto', marginBottom: 22, marginLeft: -18, marginRight: -18, padding: '0 18px' }}>
          {recents.map((r) => (
            <button key={r.id} onClick={() => go('detail', { recipeId: r.id, contextIds: recents.map(x => x.id) })} className="rcp-btn rcp-press"
              style={{ flexShrink: 0, width: 130, textAlign: 'left' }}>
              <div style={{ width: 130, height: 130, borderRadius: 4, overflow: 'hidden', marginBottom: 8 }}>
                <Photo src={r.photo} label={r.nome} tone="#d4c8a8" text="#3a2f15" />
              </div>
              <div style={{ fontFamily: T.serif, fontSize: 15, fontWeight: 500, lineHeight: 1.1, letterSpacing: -0.2 }}>{r.nome}</div>
              <div style={{ fontFamily: T.mono, fontSize: 9, color: T.muted, letterSpacing: 1.2, textTransform: 'uppercase', marginTop: 3 }}>{fmtMin(r.tempo)} · {r.categoria}</div>
            </button>
          ))}
        </div>

        {/* full index — typo-style */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', borderTop: `1px solid ${T.ink}`, paddingTop: 12, marginBottom: 6 }}>
          <Eyebrow>· Indice · {all.length} ricette</Eyebrow>
          <Eyebrow>min · pers</Eyebrow>
        </div>
        {all.map((r, i) => (
          <button key={r.id} onClick={() => go('detail', { recipeId: r.id, contextIds: allIds })} className="rcp-btn"
            style={{ display: 'grid', gridTemplateColumns: '22px 1fr auto', gap: 10, width: '100%',
              padding: '11px 0', borderBottom: `1px solid ${T.ruleSoft}`, alignItems: 'baseline', textAlign: 'left' }}>
            <span style={{ fontFamily: T.mono, fontSize: 10, color: T.muted, fontVariantNumeric: 'tabular-nums' }}>{(i + 1).toString().padStart(2, '0')}</span>
            <div>
              <div style={{ fontFamily: T.serif, fontSize: 16, fontWeight: 500, letterSpacing: -0.3, lineHeight: 1.1 }}>
                {r.nome}
                {store.favorites.has(r.id) && <span style={{ color: T.accent, marginLeft: 6, fontSize: 11 }}>♥</span>}
              </div>
              <div style={{ fontFamily: T.mono, fontSize: 9, color: T.muted, letterSpacing: 1.2, textTransform: 'uppercase', marginTop: 2 }}>{r.categoria} · {r.difficolta}</div>
            </div>
            <div style={{ fontFamily: T.mono, fontSize: 11, color: T.inkSoft, fontVariantNumeric: 'tabular-nums', textAlign: 'right' }}>
              {r.tempo}<span style={{ color: T.faint }}> · </span>{r.porzioni}
            </div>
          </button>
        ))}
      </div>
      <BottomNav active="home" go={(s) => go(s)} />
    </Frame>
  );
}

// ─── DETAIL ─────────────────────────────────────────────────
function MobileDetail({ recipe, go, back, contextIds = [] }) {
  const { servings, setS, fmtIng } = useServings(recipe.porzioni);
  const [checked, setChecked] = React.useState(() => recipe.ingredienti.map(() => false));
  const [addedToCart, setAddedToCart] = React.useState(false);
  const store = useStore();
  const isFav = store.favorites.has(recipe.id);

  // Navigazione contestuale prev/next
  const ctxIdx  = contextIds.indexOf(recipe.id);
  const prevId  = ctxIdx > 0 ? contextIds[ctxIdx - 1] : null;
  const nextId  = ctxIdx >= 0 && ctxIdx < contextIds.length - 1 ? contextIds[ctxIdx + 1] : null;
  const prevR   = prevId ? window.RECIPES.find(r => r.id === prevId) : null;
  const nextR   = nextId ? window.RECIPES.find(r => r.id === nextId) : null;
  const goCtx   = (id) => go('detail', { recipeId: id, contextIds });

  // Ricette correlate (da RECIPE_LINKS)
  const links     = (window.RECIPE_LINKS || {})[recipe.id] || {};
  const usesIds   = links.uses    || [];
  const usedInIds = links.used_in || [];
  const usesR     = usesIds.map(id => window.RECIPES.find(r => r.id === id)).filter(Boolean);
  const usedInR   = usedInIds.map(id => window.RECIPES.find(r => r.id === id)).filter(Boolean);

  const addToShopping = () => {
    const items = recipe.ingredienti
      .filter((ing, i) => !checked[i] && !ing.header)
      .map(ing => {
        if (ing.qb) return ing.n;
        return [ing.q, ing.u, ing.n].filter(Boolean).join(' ').trim();
      });
    Store.addToShopping(items);
    setAddedToCart(true);
    setTimeout(() => setAddedToCart(false), 2000);
  };

  // Mini card per ricetta correlata
  const LinkedCard = ({ r, label }) => (
    <button onClick={() => goCtx(r.id)} className="rcp-btn rcp-press"
      style={{ display: 'flex', alignItems: 'center', gap: 10, width: '100%',
        padding: '10px 12px', borderRadius: 10, background: T.card,
        border: `1px solid ${T.ruleSoft}`, textAlign: 'left' }}>
      <div style={{ width: 44, height: 44, borderRadius: 6, overflow: 'hidden', flexShrink: 0 }}>
        <Photo src={r.photo} label={r.nome} tone="#d4c8a8" text="#3a2f15" />
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontFamily: T.mono, fontSize: 8, color: T.accent, letterSpacing: 1.5,
          textTransform: 'uppercase', marginBottom: 2 }}>{label}</div>
        <div style={{ fontFamily: T.serif, fontSize: 14, fontWeight: 500, lineHeight: 1.2,
          overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{r.nome}</div>
      </div>
      <II.chevR size={12} color={T.muted} />
    </button>
  );

  return (
    <Frame>
      <div className="rcp-scroll" style={{ flex: 1, paddingBottom: 100 }}>
        {/* hero */}
        <div style={{ height: 240, position: 'relative' }}>
          <Photo src={recipe.photo} label={recipe.nome} tone="#cbb88f" text="#2c1f10" />
          <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(180deg, rgba(26,23,20,.0) 50%, rgba(26,23,20,.4))' }} />
          <button onClick={back} className="rcp-btn"
            style={{ position: 'absolute', top: 14, left: 14, width: 36, height: 36, borderRadius: 18, background: 'rgba(250,248,243,.92)', backdropFilter: 'blur(8px)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <II.back size={14} />
          </button>
          <div style={{ position: 'absolute', top: 14, right: 14, display: 'flex', gap: 8 }}>
            <button onClick={() => Store.toggleFav(recipe.id)} className="rcp-btn"
              style={{ width: 36, height: 36, borderRadius: 18, background: 'rgba(250,248,243,.92)', backdropFilter: 'blur(8px)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: isFav ? T.accent : T.ink }}>
              <II.heart size={14} fill={isFav ? T.accent : 'none'} />
            </button>
            <button onClick={() => {
                const url = window.location.href;
                if (navigator.share) { navigator.share({ title: recipe.nome, url }); }
                else { navigator.clipboard.writeText(url).then(() => alert('Link copiato!')); }
              }} className="rcp-btn"
              style={{ width: 36, height: 36, borderRadius: 18, background: 'rgba(250,248,243,.92)', backdropFilter: 'blur(8px)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <II.share size={14} />
            </button>
          </div>
        </div>

        {/* Barra navigazione contestuale prev/next */}
        {contextIds.length > 1 && (
          <div style={{ display: 'flex', alignItems: 'center', background: T.bgAlt,
            borderBottom: `1px solid ${T.ruleSoft}`, padding: '8px 14px', gap: 6 }}>
            <button onClick={back} className="rcp-btn"
              style={{ fontFamily: T.mono, fontSize: 8, letterSpacing: 1.5, textTransform: 'uppercase',
                color: T.muted, display: 'flex', alignItems: 'center', gap: 3, flexShrink: 0 }}>
              <II.back size={10} color={T.muted} /> Indice
            </button>
            <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}>
              <button onClick={() => prevId && goCtx(prevId)} className="rcp-btn"
                style={{ display: 'flex', alignItems: 'center', gap: 3, opacity: prevId ? 1 : 0.25,
                  pointerEvents: prevId ? 'auto' : 'none', maxWidth: 100, overflow: 'hidden' }}>
                <II.chevL size={11} />
                {prevR && <span style={{ fontFamily: T.serif, fontSize: 11, fontStyle: 'italic',
                  overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{prevR.nome}</span>}
              </button>
              <span style={{ fontFamily: T.mono, fontSize: 9, color: T.faint, flexShrink: 0 }}>
                {ctxIdx + 1}/{contextIds.length}
              </span>
              <button onClick={() => nextId && goCtx(nextId)} className="rcp-btn"
                style={{ display: 'flex', alignItems: 'center', gap: 3, opacity: nextId ? 1 : 0.25,
                  pointerEvents: nextId ? 'auto' : 'none', maxWidth: 100, overflow: 'hidden',
                  flexDirection: 'row-reverse' }}>
                <II.chevR size={11} />
                {nextR && <span style={{ fontFamily: T.serif, fontSize: 11, fontStyle: 'italic',
                  overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{nextR.nome}</span>}
              </button>
            </div>
          </div>
        )}

        <div style={{ padding: '20px 18px 0' }}>
          <Eyebrow color={T.accent}>{recipe.categoria} · №{(window.RECIPES.indexOf(recipe) + 1).toString().padStart(2, '0')}</Eyebrow>
          <h1 style={{ fontFamily: T.serif, fontSize: 32, fontWeight: 500, letterSpacing: -1, margin: '6px 0 0', lineHeight: 0.95 }}>
            <span style={{ fontStyle: 'italic' }}>{recipe.nome.split(' ')[0]}</span>{recipe.nome.split(' ').length > 1 ? ' ' + recipe.nome.split(' ').slice(1).join(' ') : ''}
          </h1>
          <p style={{ fontFamily: T.serif, fontStyle: 'italic', fontSize: 14, lineHeight: 1.55, color: T.inkSoft, margin: '12px 0 0' }}>
            {renderWithLinks(recipe.descrizione, goCtx)}
          </p>
          <div style={{ display: 'flex', gap: 6, marginTop: 14, flexWrap: 'wrap' }}>
            {(recipe.tag || []).map((t) => <Tag key={t} kind="olive">{t}</Tag>)}
          </div>

          {/* meta strip — 3 col, monospace */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', borderTop: `1px solid ${T.ink}`, borderBottom: `1px solid ${T.ink}`, marginTop: 18 }}>
            {[
              { l: 'Tempo', v: fmtTime(recipe.tempo), I: II.clock },
              { l: 'Porzioni', v: recipe.porzioni, I: II.users },
              { l: 'Livello', v: recipe.difficolta, I: II.flame },
            ].map((m, i) => (
              <div key={m.l} style={{ padding: '12px 6px', borderLeft: i === 0 ? 'none' : `1px solid ${T.ruleSoft}`, textAlign: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 4, color: T.muted, marginBottom: 4 }}>
                  <m.I size={10} />
                  <Eyebrow size={8}>{m.l}</Eyebrow>
                </div>
                <div style={{ fontFamily: T.serif, fontSize: 18, fontWeight: 500, letterSpacing: -0.3 }}>{m.v}</div>
              </div>
            ))}
          </div>

          {/* action row */}
          <div style={{ display: 'flex', gap: 8, marginTop: 18 }}>
            <button onClick={() => go('cook', { recipeId: recipe.id })} className="rcp-btn rcp-press"
              style={{ flex: 1, background: T.ink, color: T.bg, padding: '13px 14px', borderRadius: 12, fontWeight: 600, fontSize: 13, letterSpacing: -0.1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
              <II.play size={12} fill={T.bg} color={T.bg} /> Inizia a cucinare
            </button>
            <button onClick={addToShopping} className="rcp-btn"
              style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 3, padding: '6px 12px', minWidth: 56, borderRadius: 12, border: `1px solid ${addedToCart ? T.accent : T.ruleSoft}`, background: addedToCart ? T.accentSoft : T.card, transition: 'all .2s' }}>
              <II.cart size={14} color={addedToCart ? T.accent : T.ink} />
              <span style={{ fontFamily: T.mono, fontSize: 9, letterSpacing: 0.5, color: addedToCart ? T.accent : T.muted }}>{addedToCart ? 'OK!' : 'Spesa'}</span>
            </button>
            <button onClick={() => window.print()} className="rcp-btn"
              style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 3, padding: '6px 12px', minWidth: 56, borderRadius: 12, border: `1px solid ${T.ruleSoft}`, background: T.card }}>
              <II.printer size={14} />
              <span style={{ fontFamily: T.mono, fontSize: 9, letterSpacing: 0.5, color: T.muted }}>Stampa</span>
            </button>
          </div>

          {/* INGREDIENTI */}
          <div style={{ marginTop: 28, display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
            <h2 style={{ fontFamily: T.serif, fontSize: 22, fontWeight: 500, letterSpacing: -0.4, margin: 0, fontStyle: 'italic' }}>Ingredienti</h2>
            <div style={{ display: 'flex', alignItems: 'center', gap: 4, background: T.card, border: `1px solid ${T.ruleSoft}`, borderRadius: 999, padding: 2 }}>
              <button onClick={() => setS(Math.max(1, servings - 1))} className="rcp-btn" style={{ width: 26, height: 26, borderRadius: 13, display: 'flex', alignItems: 'center', justifyContent: 'center' }}><II.minus size={11} /></button>
              <span style={{ fontFamily: T.mono, fontSize: 11, fontWeight: 600, minWidth: 56, textAlign: 'center' }}>{servings} pers</span>
              <button onClick={() => setS(servings + 1)} className="rcp-btn" style={{ width: 26, height: 26, borderRadius: 13, display: 'flex', alignItems: 'center', justifyContent: 'center' }}><II.plus size={11} /></button>
            </div>
          </div>

          <div style={{ marginTop: 12 }}>
            {recipe.ingredienti.map((ing, i) => {
              // Ingrediente che è un link a un'altra ricetta
              if (ing.recipeLink) {
                const linked = window.RECIPES.find(r => r.id === ing.recipeLink);
                if (linked) return (
                  <button key={i} onClick={() => goCtx(linked.id)} className="rcp-btn rcp-press"
                    style={{ display: 'flex', alignItems: 'center', gap: 8, width: '100%',
                      padding: '8px 10px', borderBottom: `1px dotted ${T.ruleSoft}`,
                      color: T.accent, textAlign: 'left' }}>
                    <II.tag size={11} color={T.accent} />
                    <span style={{ fontFamily: T.serif, fontSize: 14, fontStyle: 'italic' }}>{linked.nome}</span>
                    <II.chevR size={10} color={T.faint} style={{ marginLeft: 'auto' }} />
                  </button>
                );
              }
              if (ing.header) return (
                <div key={i} style={{ fontFamily: T.serif, fontSize: 13, fontWeight: 600, fontStyle: 'italic', color: T.ink, padding: '10px 0 4px', marginTop: 4 }}>{ing.n}</div>
              );
              const f = fmtIng(ing);
              return (
                <button key={i} onClick={() => setChecked((c) => c.map((v, j) => j === i ? !v : v))} className="rcp-btn"
                  style={{ display: 'grid', gridTemplateColumns: '20px 64px 1fr', gap: 10, width: '100%', padding: '10px 0', borderBottom: `1px dotted ${T.ruleSoft}`, alignItems: 'center', textAlign: 'left',
                    opacity: checked[i] ? 0.4 : 1, textDecoration: checked[i] ? 'line-through' : 'none' }}>
                  <span style={{ width: 18, height: 18, borderRadius: 9, border: checked[i] ? 'none' : `1.5px solid ${T.faint}`, background: checked[i] ? T.accent : 'transparent', color: T.bg, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    {checked[i] && <II.check size={11} color={T.bg} strokeWidth={2} />}
                  </span>
                  <span style={{ fontFamily: T.mono, fontSize: 11, fontVariantNumeric: 'tabular-nums', color: f.hasQty ? T.inkSoft : T.muted, fontStyle: f.hasQty ? 'normal' : 'italic' }}>{f.qty}</span>
                  <span style={{ fontSize: 14 }}>{ing.n}</span>
                </button>
              );
            })}
          </div>

          {/* PREPARAZIONE */}
          <h2 style={{ fontFamily: T.serif, fontSize: 22, fontWeight: 500, letterSpacing: -0.4, margin: '32px 0 14px', fontStyle: 'italic' }}>Preparazione</h2>
          {recipe.passi.map((p, i) => (
            <div key={i} style={{ display: 'grid', gridTemplateColumns: '40px 1fr', gap: 10, padding: '12px 0', borderTop: i === 0 ? `1px solid ${T.ink}` : `1px solid ${T.ruleSoft}` }}>
              <div style={{ fontFamily: T.serif, fontSize: 36, fontWeight: 500, color: T.accent, fontStyle: 'italic', lineHeight: 0.9 }}>{i + 1}</div>
              <div style={{ fontSize: 14, lineHeight: 1.6, color: T.inkSoft, paddingTop: 4 }}>{renderWithLinks(p, goCtx)}</div>
            </div>
          ))}

          {/* RICETTE CORRELATE — Basi usate / Usata in */}
          {(usesR.length > 0 || usedInR.length > 0) && (
            <div style={{ marginTop: 28 }}>
              <div style={{ borderTop: `1px solid ${T.ink}`, paddingTop: 14, marginBottom: 12 }}>
                <Eyebrow>· Ricette correlate</Eyebrow>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {usesR.map(r => <LinkedCard key={r.id} r={r} label="Base usata" />)}
                {usedInR.map(r => <LinkedCard key={r.id} r={r} label="Usata in" />)}
              </div>
            </div>
          )}

          {/* note della ricetta (da Paprika ZNOTES) */}
          {recipe.notes && (
            <div style={{ marginTop: 28, padding: '14px 16px', borderRadius: 10,
                          background: T.card, border: `1px solid ${T.ruleSoft}` }}>
              <Eyebrow style={{ marginBottom: 6 }}>Note</Eyebrow>
              <div style={{ margin: 0, fontFamily: T.serif, fontStyle: 'italic',
                           fontSize: 14, lineHeight: 1.65, color: T.inkSoft }}>
                {renderWithLinks(recipe.notes, goCtx)}
              </div>
            </div>
          )}

          {/* commenti Firebase */}
          <div style={{ padding: '0 0 24px' }}>
            {window.CommentiSection && (
              <window.CommentiSection recipeUid={recipe.id} />
            )}
          </div>
        </div>
      </div>
    </Frame>
  );
}

window.MobileHome = MobileHome;
window.MobileDetail = MobileDetail;
window.BottomNav = BottomNav;
