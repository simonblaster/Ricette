// Desktop layout — Recipees
// Single-window app per artboard. Sidebar persistente, content area che cambia.

function DesktopShell({ children, active, go, store, activeCat = null, onCat = () => {} }) {
  const navItems = [
    { k: 'home', l: 'Indice', I: II.list },
    { k: 'search', l: 'Cerca', I: II.search },
    { k: 'shopping', l: 'Lista spesa', I: II.cart, badge: store.shopping.size },
    { k: 'profile', l: 'Profilo', I: II.user },
  ];
  return (
    <Frame>
      <div style={{ display: 'flex', height: '100%' }}>
        {/* sidebar */}
        <div style={{ width: 220, background: T.bgAlt, borderRight: `1px solid ${T.ruleSoft}`, display: 'flex', flexDirection: 'column', padding: '24px 16px' }}>
          <div style={{ marginBottom: 28, paddingLeft: 6 }}>
            <Eyebrow color={T.accent}>vol. III · ’26</Eyebrow>
            <div style={{ fontFamily: T.serif, fontSize: 22, fontWeight: 500, letterSpacing: -0.5, marginTop: 4, lineHeight: 1 }}>
              Recip<span style={{ fontStyle: 'italic', color: T.accent }}>ees</span>.
            </div>
          </div>
          <Eyebrow size={8}>· Naviga</Eyebrow>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 2, marginTop: 8, marginBottom: 24 }}>
            {navItems.map((n) => {
              const a = active === n.k;
              return (
                <button key={n.k} className="rcp-btn" onClick={() => go(n.k)}
                  style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '8px 10px', borderRadius: 8, background: a ? T.bg : 'transparent', color: a ? T.ink : T.inkSoft, fontSize: 13, fontWeight: a ? 600 : 500, textAlign: 'left', border: a ? `1px solid ${T.ruleSoft}` : '1px solid transparent' }}>
                  <n.I size={14} />
                  <span style={{ flex: 1 }}>{n.l}</span>
                  {n.badge > 0 && <span style={{ fontFamily: T.mono, fontSize: 10, padding: '1px 6px', borderRadius: 999, background: T.accent, color: T.bg }}>{n.badge}</span>}
                </button>
              );
            })}
          </div>
          <Eyebrow size={8}>· Categorie</Eyebrow>
          <div style={{ display: 'flex', flexDirection: 'column', marginTop: 6, flex: 1, overflowY: 'auto', minHeight: 0 }}>
            {window.CATEGORIES.slice(1).map((c) => (
              <button key={c} className="rcp-btn" onClick={() => onCat(activeCat === c ? null : c)}
                style={{ padding: '6px 10px', borderRadius: 6, fontFamily: T.serif, fontSize: 13, fontStyle: 'italic', textAlign: 'left',
                  color: activeCat === c ? T.accent : T.inkSoft,
                  background: activeCat === c ? T.accentSoft : 'transparent',
                  fontWeight: activeCat === c ? 600 : 400,
                  flexShrink: 0,
                }}>{c}</button>
            ))}
          </div>
          <div style={{ paddingTop: 12, marginTop: 8, display: 'flex', alignItems: 'center', gap: 10, borderTop: `1px solid ${T.ruleSoft}` }}>
            <div style={{ width: 28, height: 28, borderRadius: 14, background: T.bgDeep, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: T.serif, fontSize: 14, fontStyle: 'italic', color: T.accent, fontWeight: 500 }}>S</div>
            <div>
              <div style={{ fontSize: 12, fontWeight: 600 }}>Simone</div>
              <div style={{ fontFamily: T.mono, fontSize: 9, color: T.muted, letterSpacing: 1 }}>{store.favorites.size} ♥ · {store.history.length} cucinate</div>
            </div>
          </div>
        </div>
        {/* content */}
        <div style={{ flex: 1, minWidth: 0 }}>{children}</div>
      </div>
    </Frame>
  );
}

// HOME desktop — editorial 3-col grid
function DesktopHome({ go }) {
  const store = useStore();
  const [activeCat, setActiveCat] = React.useState(null);
  const featured = window.RECIPES[2];
  const all = activeCat ? window.RECIPES.filter(r => r.tag.includes(activeCat)) : window.RECIPES;
  return (
    <DesktopShell active="home" go={go} store={store} activeCat={activeCat} onCat={setActiveCat}>
      <div className="rcp-scroll" style={{ height: '100%', padding: '28px 36px 48px' }}>
        {/* masthead */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', borderBottom: `1px solid ${T.ink}`, paddingBottom: 18, marginBottom: 24 }}>
          <div>
            <Eyebrow color={T.accent}>Mer · 2 maggio</Eyebrow>
            <h1 style={{ fontFamily: T.serif, fontSize: 56, fontWeight: 500, letterSpacing: -1.6, margin: '4px 0 0', lineHeight: 0.9 }}>
              Le mie <span style={{ fontStyle: 'italic' }}>ricette.</span>
            </h1>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <button onClick={() => go('search')} className="rcp-btn" style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 14px', background: T.card, border: `1px solid ${T.ruleSoft}`, borderRadius: 999, fontSize: 12, color: T.muted }}>
              <II.search size={12} /> Cerca <span style={{ fontFamily: T.mono, fontSize: 10, padding: '1px 5px', background: T.bgAlt, borderRadius: 4, marginLeft: 6 }}>⌘K</span>
            </button>
            <button className="rcp-btn" style={{ padding: '8px 14px', background: T.ink, color: T.bg, borderRadius: 999, fontSize: 12, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 6 }}>
              <II.plus size={12} color={T.bg} /> Aggiungi
            </button>
          </div>
        </div>

        {/* featured */}
        <button onClick={() => go('detail', { recipeId: featured.id })} className="rcp-btn"
          style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: 32, width: '100%', padding: '8px 0 28px', textAlign: 'left', borderBottom: `1px solid ${T.ruleSoft}` }}>
          <div style={{ borderRadius: 4, overflow: 'hidden' }}>
            <Photo src={featured.photo} label={featured.nome} tone="#d4c8a8" text="#3a2f15" ratio="3/2" />
          </div>
          <div>
            <Eyebrow color={T.accent}>· Della settimana · №27</Eyebrow>
            <h2 style={{ fontFamily: T.serif, fontSize: 42, fontWeight: 500, letterSpacing: -1.2, margin: '8px 0 12px', lineHeight: 0.95 }}>
              <span style={{ fontStyle: 'italic' }}>{featured.nome}</span>.
            </h2>
            <p style={{ fontFamily: T.serif, fontSize: 16, fontStyle: 'italic', lineHeight: 1.5, color: T.inkSoft, margin: 0 }}>
              {featured.descrizione}
            </p>
            <div style={{ display: 'flex', gap: 6, marginTop: 18 }}>
              <Tag>{fmtTimeLong(featured.tempo)}</Tag>
              <Tag kind="olive">{featured.categoria}</Tag>
              <Tag>{featured.difficolta}</Tag>
              <Tag kind="accent">⭐ Preferita</Tag>
            </div>
          </div>
        </button>

        {/* index 3-col */}
        <div style={{ marginTop: 28, display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 16 }}>
          <Eyebrow>· {activeCat ? activeCat : 'Indice'} — {all.length} ricette</Eyebrow>
          <div style={{ display: 'flex', gap: 12 }}>
            <Eyebrow>ordine: a-z</Eyebrow>
            <Eyebrow color={T.accent}>griglia</Eyebrow>
          </div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '24px 28px' }}>
          {all.map((r, i) => (
            <button key={r.id} onClick={() => go('detail', { recipeId: r.id })} className="rcp-btn"
              style={{ textAlign: 'left', display: 'block' }}>
              <div style={{ borderRadius: 4, overflow: 'hidden', marginBottom: 10 }}>
                <Photo src={r.photo} label={r.nome} tone="#d4c8a8" text="#3a2f15" ratio="4/3" />
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 4 }}>
                <Eyebrow size={8}>№{(i + 1).toString().padStart(2, '0')} · {r.categoria}</Eyebrow>
                {store.favorites.has(r.id) && <span style={{ color: T.accent, fontSize: 11 }}>♥</span>}
              </div>
              <div style={{ fontFamily: T.serif, fontSize: 22, fontWeight: 500, letterSpacing: -0.5, lineHeight: 1.05 }}>{r.nome}</div>
              <div style={{ fontFamily: T.mono, fontSize: 10, color: T.muted, marginTop: 6, letterSpacing: 1, textTransform: 'uppercase' }}>{fmtMin(r.tempo)} · {r.porzioni} pers · {r.difficolta}</div>
            </button>
          ))}
        </div>
      </div>
    </DesktopShell>
  );
}

// DETAIL desktop — 2-col layout: hero + actions left, ingredienti+passi right
function DesktopDetail({ recipe, go, back }) {
  const store = useStore();
  const { servings, setS, fmtIng } = useServings(recipe.porzioni);
  const [checked, setChecked] = React.useState(() => recipe.ingredienti.map(() => false));
  const [addedToCart, setAddedToCart] = React.useState(false);
  const addToShopping = () => {
    const items = recipe.ingredienti
      .filter(ing => !ing.header)
      .map(ing => {
        if (ing.qb) return ing.n;
        const parts = [ing.q, ing.u, ing.n].filter(Boolean);
        return parts.join(' ').trim();
      });
    Store.addToShopping(items);
    setAddedToCart(true);
    setTimeout(() => setAddedToCart(false), 2000);
  };
  const isFav = store.favorites.has(recipe.id);

  return (
    <DesktopShell active="home" go={go} store={store}>
      <div className="rcp-scroll" style={{ height: '100%', padding: '24px 36px 48px' }}>
        <button onClick={back} className="rcp-btn" style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, color: T.muted, marginBottom: 18, textTransform: 'uppercase', letterSpacing: 1.5, fontFamily: T.mono }}>
          <II.back size={11} color={T.muted} /> Indice
        </button>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.2fr', gap: 40 }}>
          {/* LEFT — hero + meta */}
          <div>
            <div style={{ borderRadius: 4, overflow: 'hidden', marginBottom: 18 }}>
              <Photo src={recipe.photo} label={recipe.nome} tone="#cbb88f" text="#2c1f10" ratio="4/5" />
            </div>
            <div style={{ display: 'flex', gap: 8 }}>
              <button onClick={() => go('cook', { recipeId: recipe.id })} className="rcp-btn rcp-press"
                style={{ flex: 1, background: T.ink, color: T.bg, padding: '12px 14px', borderRadius: 10, fontWeight: 600, fontSize: 13, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
                <II.play size={11} fill={T.bg} color={T.bg} /> Cucina ora
              </button>
              <button onClick={() => Store.toggleFav(recipe.id)} className="rcp-btn"
                style={{ width: 44, height: 44, borderRadius: 10, border: `1px solid ${T.ruleSoft}`, background: T.card, color: isFav ? T.accent : T.ink, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <II.heart size={14} fill={isFav ? T.accent : 'none'} />
              </button>
              <button onClick={() => window.print()} className="rcp-btn"
                style={{ width: 44, height: 44, borderRadius: 10, border: `1px solid ${T.ruleSoft}`, background: T.card, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <II.printer size={14} />
              </button>
              <button onClick={() => {
                  const url = window.location.href;
                  if (navigator.share) { navigator.share({ title: recipe.nome, url }); }
                  else { navigator.clipboard.writeText(url).then(() => alert('Link copiato negli appunti!')); }
                }} className="rcp-btn"
                style={{ width: 44, height: 44, borderRadius: 10, border: `1px solid ${T.ruleSoft}`, background: T.card, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <II.share size={14} />
              </button>
            </div>
            {/* meta strip */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', borderTop: `1px solid ${T.ink}`, borderBottom: `1px solid ${T.ink}`, marginTop: 18 }}>
              {[
                { l: 'Tempo', v: fmtTime(recipe.tempo), I: II.clock },
                { l: 'Porzioni', v: recipe.porzioni, I: II.users },
                { l: 'Livello', v: recipe.difficolta, I: II.flame },
              ].map((m, i) => (
                <div key={m.l} style={{ padding: '14px 8px', borderLeft: i === 0 ? 'none' : `1px solid ${T.ruleSoft}`, textAlign: 'center' }}>
                  <Eyebrow size={8}>{m.l}</Eyebrow>
                  <div style={{ fontFamily: T.serif, fontSize: 22, fontWeight: 500, letterSpacing: -0.4, marginTop: 4 }}>{m.v}</div>
                </div>
              ))}
            </div>
          </div>

          {/* RIGHT — content */}
          <div>
            <Eyebrow color={T.accent}>{recipe.categoria} · №{(window.RECIPES.indexOf(recipe) + 1).toString().padStart(2, '0')}</Eyebrow>
            <h1 style={{ fontFamily: T.serif, fontSize: 52, fontWeight: 500, letterSpacing: -1.6, margin: '6px 0 0', lineHeight: 0.92 }}>
              <span style={{ fontStyle: 'italic' }}>{recipe.nome.split(' ')[0]}</span>{recipe.nome.split(' ').length > 1 ? ' ' + recipe.nome.split(' ').slice(1).join(' ') : ''}.
            </h1>
            <p style={{ fontFamily: T.serif, fontStyle: 'italic', fontSize: 16, lineHeight: 1.55, color: T.inkSoft, margin: '14px 0 0', maxWidth: 460 }}>
              {recipe.descrizione}
            </p>
            <div style={{ display: 'flex', gap: 6, marginTop: 14 }}>
              {(recipe.tag || []).map((t) => <Tag key={t} kind="olive">{t}</Tag>)}
            </div>

            {/* ingredienti */}
            <div style={{ marginTop: 28, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2 style={{ fontFamily: T.serif, fontSize: 22, fontWeight: 500, letterSpacing: -0.4, margin: 0, fontStyle: 'italic' }}>Ingredienti</h2>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <button onClick={addToShopping} className="rcp-btn"
                  style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '6px 11px', border: `1px solid ${addedToCart ? T.accent : T.ruleSoft}`, borderRadius: 999, fontSize: 11, color: addedToCart ? T.accent : T.inkSoft, background: addedToCart ? T.accentSoft : 'transparent', transition: 'all .2s' }}>
                  <II.cart size={11} color={addedToCart ? T.accent : T.inkSoft} />{addedToCart ? 'Aggiunto!' : 'Lista spesa'}
                </button>
                <div style={{ display: 'flex', alignItems: 'center', gap: 4, background: T.card, border: `1px solid ${T.ruleSoft}`, borderRadius: 999, padding: 2 }}>
                  <button onClick={() => setS(Math.max(1, servings - 1))} className="rcp-btn" style={{ width: 24, height: 24, borderRadius: 12, display: 'flex', alignItems: 'center', justifyContent: 'center' }}><II.minus size={11} /></button>
                  <span style={{ fontFamily: T.mono, fontSize: 11, fontWeight: 600, minWidth: 56, textAlign: 'center' }}>{servings} pers</span>
                  <button onClick={() => setS(servings + 1)} className="rcp-btn" style={{ width: 24, height: 24, borderRadius: 12, display: 'flex', alignItems: 'center', justifyContent: 'center' }}><II.plus size={11} /></button>
                </div>
              </div>
            </div>
            <div style={{ marginTop: 10 }}>
              {recipe.ingredienti.map((ing, i) => {
                if (ing.header) return (
                  <div key={i} style={{ fontFamily: T.serif, fontSize: 13, fontWeight: 600, fontStyle: 'italic', color: T.ink, padding: '10px 0 4px', marginTop: 4 }}>{ing.n}</div>
                );
                const f = fmtIng(ing);
                return (
                  <button key={i} onClick={() => setChecked((c) => c.map((v, j) => j === i ? !v : v))} className="rcp-btn"
                    style={{ display: 'grid', gridTemplateColumns: '20px 70px 1fr', gap: 12, width: '100%', padding: '8px 0', borderBottom: `1px dotted ${T.ruleSoft}`, alignItems: 'center', textAlign: 'left',
                      opacity: checked[i] ? 0.4 : 1, textDecoration: checked[i] ? 'line-through' : 'none' }}>
                    <span style={{ width: 16, height: 16, borderRadius: 8, border: checked[i] ? 'none' : `1.5px solid ${T.faint}`, background: checked[i] ? T.accent : 'transparent', color: T.bg, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      {checked[i] && <II.check size={9} color={T.bg} strokeWidth={2} />}
                    </span>
                    <span style={{ fontFamily: T.mono, fontSize: 11, fontVariantNumeric: 'tabular-nums', color: f.hasQty ? T.inkSoft : T.muted, fontStyle: f.hasQty ? 'normal' : 'italic' }}>{f.qty}</span>
                    <span style={{ fontSize: 13 }}>{ing.n}</span>
                  </button>
                );
              })}
            </div>

            {/* passi */}
            <h2 style={{ fontFamily: T.serif, fontSize: 22, fontWeight: 500, letterSpacing: -0.4, margin: '32px 0 14px', fontStyle: 'italic' }}>Preparazione</h2>
            {recipe.passi.map((p, i) => (
              <div key={i} style={{ display: 'grid', gridTemplateColumns: '50px 1fr', gap: 14, padding: '14px 0', borderTop: i === 0 ? `1px solid ${T.ink}` : `1px solid ${T.ruleSoft}` }}>
                <div style={{ fontFamily: T.serif, fontSize: 44, fontWeight: 500, color: T.accent, fontStyle: 'italic', lineHeight: 0.85 }}>{i + 1}</div>
                <div style={{ fontFamily: T.serif, fontSize: 16, lineHeight: 1.55, color: T.inkSoft, paddingTop: 4 }}>{p}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </DesktopShell>
  );
}

window.DesktopHome = DesktopHome;
window.DesktopDetail = DesktopDetail;
window.DesktopShell = DesktopShell;
