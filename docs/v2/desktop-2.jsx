// Desktop screens: search, cook, shopping, profile

function DesktopSearch({ go, back }) {
  const store = useStore();
  const [q, setQ] = React.useState('');
  const [activeTags, setActiveTags] = React.useState(new Set());
  const allTags = Array.from(new Set(window.RECIPES.flatMap((r) => r.tag || []))).sort();
  const filtered = window.RECIPES.filter((r) => {
    if (q && !r.nome.toLowerCase().includes(q.toLowerCase()) && !r.ingredienti.some((i) => i.n.toLowerCase().includes(q.toLowerCase()))) return false;
    if (activeTags.size > 0 && !(r.tag || []).some((t) => activeTags.has(t))) return false;
    return true;
  });
  const toggle = (t) => setActiveTags((s) => { const n = new Set(s); n.has(t) ? n.delete(t) : n.add(t); return n; });

  return (
    <DesktopShell active="search" go={go} store={store}>
      <div className="rcp-scroll" style={{ height: '100%', padding: '28px 36px 48px' }}>
        <Eyebrow color={T.accent}>· Cerca</Eyebrow>
        <h1 style={{ fontFamily: T.serif, fontSize: 44, fontWeight: 500, letterSpacing: -1.2, margin: '4px 0 18px', lineHeight: 0.95 }}>
          Trova una <span style={{ fontStyle: 'italic' }}>ricetta.</span>
        </h1>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, background: T.card, border: `1px solid ${T.ruleSoft}`, borderRadius: 12, padding: '14px 16px', marginBottom: 22 }}>
          <II.search size={16} color={T.muted} />
          <input autoFocus value={q} onChange={(e) => setQ(e.target.value)} placeholder="Nome o ingrediente…"
            style={{ flex: 1, border: 'none', outline: 'none', background: 'transparent', fontFamily: T.serif, fontStyle: q ? 'normal' : 'italic', fontSize: 18, color: T.ink }} />
          {q && <button className="rcp-btn" onClick={() => setQ('')}><II.close size={14} color={T.muted} /></button>}
        </div>

        <Eyebrow>· Filtra per tag</Eyebrow>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, margin: '10px 0 22px' }}>
          {allTags.map((t) => {
            const a = activeTags.has(t);
            return (
              <button key={t} className="rcp-btn" onClick={() => toggle(t)}
                style={{ padding: '6px 14px', borderRadius: 999, fontSize: 12, fontWeight: 500,
                  background: a ? T.ink : 'transparent', color: a ? T.bg : T.inkSoft,
                  border: `1px solid ${a ? T.ink : T.ruleSoft}` }}>{t}</button>
            );
          })}
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', borderTop: `1px solid ${T.ink}`, paddingTop: 12, marginBottom: 8 }}>
          <Eyebrow>· {filtered.length} risultat{filtered.length === 1 ? 'o' : 'i'}</Eyebrow>
          <Eyebrow>min · pers</Eyebrow>
        </div>
        {filtered.map((r, i) => (
          <button key={r.id} onClick={() => go('detail', { recipeId: r.id })} className="rcp-btn"
            style={{ display: 'grid', gridTemplateColumns: '32px 60px 1fr 60px 30px', gap: 14, width: '100%', padding: '14px 0', borderBottom: `1px solid ${T.ruleSoft}`, alignItems: 'center', textAlign: 'left' }}>
            <span style={{ fontFamily: T.mono, fontSize: 11, color: T.muted, fontVariantNumeric: 'tabular-nums' }}>{(i + 1).toString().padStart(2, '0')}</span>
            <div style={{ width: 60, height: 60, borderRadius: 4, overflow: 'hidden' }}>
              <Photo src={r.photo} label={r.nome} tone="#d4c8a8" text="#3a2f15" />
            </div>
            <div>
              <Eyebrow size={8}>{r.categoria}{r.tag && r.tag.length ? ' · ' + r.tag.join(' · ') : ''}</Eyebrow>
              <div style={{ fontFamily: T.serif, fontSize: 22, fontWeight: 500, letterSpacing: -0.4, lineHeight: 1.05, marginTop: 2 }}>{r.nome}</div>
            </div>
            <div style={{ fontFamily: T.mono, fontSize: 12, color: T.inkSoft, fontVariantNumeric: 'tabular-nums', textAlign: 'right' }}>
              {r.tempo}<span style={{ color: T.faint }}> · </span>{r.porzioni}
            </div>
            <II.chevR size={14} color={T.muted} />
          </button>
        ))}
      </div>
    </DesktopShell>
  );
}

function DesktopCook({ recipe, back }) {
  const [step, setStep] = React.useState(0);
  const [timerSec, setTimerSec] = React.useState(0);
  const [timerRunning, setTimerRunning] = React.useState(false);
  React.useEffect(() => {
    if (!timerRunning) return;
    const t = setInterval(() => setTimerSec((s) => Math.max(0, s - 1)), 1000);
    return () => clearInterval(t);
  }, [timerRunning]);
  const fmt = (s) => `${Math.floor(s / 60).toString().padStart(2, '0')}:${(s % 60).toString().padStart(2, '0')}`;
  const total = recipe.passi.length;

  return (
    <Frame bg={T.ink} style={{ color: T.bg }}>
      {/* top bar */}
      <div style={{ padding: '20px 32px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <button onClick={back} className="rcp-btn" style={{ display: 'flex', alignItems: 'center', gap: 8, color: T.bg, opacity: 0.7, fontSize: 12, fontFamily: T.mono, letterSpacing: 1.5, textTransform: 'uppercase' }}>
          <II.close size={14} color={T.bg} /> Esci dalla cottura
        </button>
        <div style={{ fontFamily: T.serif, fontSize: 16, fontStyle: 'italic', opacity: 0.8 }}>{recipe.nome}</div>
        <div style={{ fontFamily: T.mono, fontSize: 12, fontVariantNumeric: 'tabular-nums', opacity: 0.7 }}>Passo {step + 1}/{total}</div>
      </div>
      <div style={{ padding: '0 32px', display: 'flex', gap: 4, marginBottom: 36 }}>
        {recipe.passi.map((_, i) => (
          <div key={i} style={{ flex: 1, height: 3, borderRadius: 2, background: i <= step ? T.accent : 'rgba(250,248,243,0.15)' }} />
        ))}
      </div>

      <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '1.6fr 1fr', gap: 48, padding: '0 48px 32px', minHeight: 0 }}>
        <div className="rcp-scroll" style={{ display: 'flex', flexDirection: 'column' }}>
          <div style={{ fontFamily: T.serif, fontSize: 200, fontWeight: 500, fontStyle: 'italic', lineHeight: 0.85, color: T.accent, letterSpacing: -6 }}>
            {step + 1}
          </div>
          <div style={{ fontFamily: T.serif, fontSize: 36, fontWeight: 500, lineHeight: 1.3, letterSpacing: -0.6, marginTop: 24, maxWidth: 540 }}>
            {recipe.passi[step]}
          </div>
        </div>
        <div className="rcp-scroll" style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {/* timer */}
          <div style={{ padding: 20, background: 'rgba(250,248,243,0.05)', border: '1px solid rgba(250,248,243,0.1)', borderRadius: 14 }}>
            <Eyebrow color="rgba(250,248,243,0.5)">· Timer</Eyebrow>
            <div style={{ fontFamily: T.mono, fontSize: 48, fontWeight: 500, fontVariantNumeric: 'tabular-nums', letterSpacing: -2, color: timerSec > 0 ? T.bg : 'rgba(250,248,243,0.4)', margin: '8px 0 14px' }}>{fmt(timerSec)}</div>
            <div style={{ display: 'flex', gap: 6, marginBottom: 8 }}>
              {[3, 5, 10, 15, 20].map((m) => (
                <button key={m} className="rcp-btn" onClick={() => { setTimerSec(m * 60); setTimerRunning(true); }}
                  style={{ flex: 1, padding: '8px', border: '1px solid rgba(250,248,243,0.15)', borderRadius: 8, fontSize: 12, fontWeight: 600, color: T.bg }}>{m}m</button>
              ))}
            </div>
            <button className="rcp-btn" onClick={() => setTimerRunning((r) => !r)}
              style={{ width: '100%', padding: '10px', background: T.accent, borderRadius: 8, color: T.bg, fontWeight: 600, fontSize: 13, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
              {timerRunning ? <><II.pause size={11} color={T.bg} /> Pausa</> : <><II.play size={11} color={T.bg} fill={T.bg} /> Avvia</>}
            </button>
          </div>
          {/* mini ingr list */}
          <div style={{ padding: 20, background: 'rgba(250,248,243,0.05)', border: '1px solid rgba(250,248,243,0.1)', borderRadius: 14, flex: 1, minHeight: 0, overflow: 'auto' }}>
            <Eyebrow color="rgba(250,248,243,0.5)">· Ingredienti a portata</Eyebrow>
            <div style={{ marginTop: 10 }}>
              {recipe.ingredienti.map((i, idx) => (
                <div key={idx} style={{ display: 'grid', gridTemplateColumns: '60px 1fr', gap: 10, padding: '6px 0', fontSize: 13, opacity: 0.85 }}>
                  <span style={{ fontFamily: T.mono, fontSize: 11, fontVariantNumeric: 'tabular-nums', opacity: 0.7 }}>{i.q} {i.u}</span>
                  <span>{i.n}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div style={{ padding: '20px 48px 28px', display: 'flex', gap: 12, justifyContent: 'space-between', alignItems: 'center' }}>
        <button onClick={() => setStep(Math.max(0, step - 1))} disabled={step === 0} className="rcp-btn"
          style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '14px 22px', borderRadius: 28, border: '1px solid rgba(250,248,243,0.15)', opacity: step === 0 ? 0.3 : 1, color: T.bg, fontSize: 13, fontWeight: 500 }}>
          <II.chevL size={14} color={T.bg} /> Precedente
        </button>
        <button onClick={() => step < total - 1 ? setStep(step + 1) : back()} className="rcp-btn rcp-press"
          style={{ padding: '14px 36px', borderRadius: 28, background: T.accent, color: T.bg, fontWeight: 600, fontSize: 14, display: 'flex', alignItems: 'center', gap: 10 }}>
          {step < total - 1 ? <>Successivo <II.chevR size={14} color={T.bg} /></> : <>Buon appetito <II.sparkle size={14} color={T.bg} /></>}
        </button>
      </div>
    </Frame>
  );
}

function DesktopShopping({ go }) {
  const store = useStore();
  const items = Array.from(store.shopping);
  const grouped = items.reduce((acc, it) => {
    const k = (it || '').toLowerCase();
    let cat = 'Altro';
    if (/farina|lievito|riso|pasta|savoiardi|sale|zucchero/.test(k)) cat = 'Dispensa';
    else if (/pomodor|melanzan|cipoll|sedano|carota|prezzemolo|limon|olive|capperi/.test(k)) cat = 'Frutta e verdura';
    else if (/pollo|pancetta|uova|mascarpone|panna|burro|parmigiano|pecorino/.test(k)) cat = 'Frigorifero';
    else if (/olio|aceto|pepe|vaniglia|zafferano|cacao|brodo|vino|gelatina|miele|malto/.test(k)) cat = 'Condimenti';
    else if (/fagioli/.test(k)) cat = 'Legumi';
    (acc[cat] = acc[cat] || []).push(it);
    return acc;
  }, {});
  const order = ['Frutta e verdura', 'Frigorifero', 'Dispensa', 'Legumi', 'Condimenti', 'Altro'];

  return (
    <DesktopShell active="shopping" go={go} store={store}>
      <div className="rcp-scroll" style={{ height: '100%', padding: '28px 36px 48px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', borderBottom: `1px solid ${T.ink}`, paddingBottom: 16, marginBottom: 24 }}>
          <div>
            <Eyebrow color={T.accent}>· La tua spesa</Eyebrow>
            <h1 style={{ fontFamily: T.serif, fontSize: 44, fontWeight: 500, letterSpacing: -1.2, margin: '4px 0 0', lineHeight: 0.95 }}>
              Lista <span style={{ fontStyle: 'italic' }}>spesa.</span>
            </h1>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <button className="rcp-btn" style={{ padding: '8px 14px', border: `1px solid ${T.ruleSoft}`, borderRadius: 999, fontSize: 12, display: 'flex', alignItems: 'center', gap: 6 }}>
              <II.printer size={12} /> Stampa
            </button>
            <button onClick={() => Store.clearShopping()} className="rcp-btn" style={{ padding: '8px 14px', border: `1px solid ${T.ruleSoft}`, borderRadius: 999, fontSize: 12, color: T.muted }}>Svuota</button>
          </div>
        </div>

        {items.length === 0 ? (
          <div style={{ marginTop: 80, textAlign: 'center', color: T.muted }}>
            <II.cart size={40} color={T.faint} />
            <div style={{ fontFamily: T.serif, fontSize: 22, fontStyle: 'italic', marginTop: 16 }}>Lista vuota</div>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 40px' }}>
            {order.filter((c) => grouped[c]).map((c) => (
              <div key={c} style={{ marginBottom: 24, breakInside: 'avoid' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', borderBottom: `1px solid ${T.ink}`, paddingBottom: 6, marginBottom: 4 }}>
                  <Eyebrow>· {c}</Eyebrow>
                  <Eyebrow>{grouped[c].length}</Eyebrow>
                </div>
                {grouped[c].map((it) => (
                  <button key={it} className="rcp-btn" onClick={() => Store.toggleShopping(it)}
                    style={{ display: 'flex', alignItems: 'center', gap: 12, width: '100%', padding: '10px 0', borderBottom: `1px dotted ${T.ruleSoft}`, textAlign: 'left' }}>
                    <span style={{ width: 16, height: 16, borderRadius: 8, border: `1.5px solid ${T.faint}` }} />
                    <span style={{ fontFamily: T.serif, fontSize: 16, flex: 1 }}>{it}</span>
                  </button>
                ))}
              </div>
            ))}
          </div>
        )}
      </div>
    </DesktopShell>
  );
}

function DesktopProfile({ go }) {
  const store = useStore();
  const [tab, setTab] = React.useState('fav');
  const fav = Array.from(store.favorites).map((id) => window.RECIPES.find((r) => r.id === id)).filter(Boolean);
  const hist = store.history.map((id) => window.RECIPES.find((r) => r.id === id)).filter(Boolean);
  const list = tab === 'fav' ? fav : hist;
  return (
    <DesktopShell active="profile" go={go} store={store}>
      <div className="rcp-scroll" style={{ height: '100%', padding: '28px 36px 48px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 18, marginBottom: 24 }}>
          <div style={{ width: 72, height: 72, borderRadius: 36, background: T.bgDeep, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: T.serif, fontSize: 32, fontStyle: 'italic', color: T.accent, fontWeight: 500 }}>S</div>
          <div>
            <Eyebrow color={T.accent}>· Profilo</Eyebrow>
            <h1 style={{ fontFamily: T.serif, fontSize: 36, fontWeight: 500, letterSpacing: -1, margin: '4px 0 0' }}>
              Simone <span style={{ fontStyle: 'italic', color: T.muted }}>Blaster</span>
            </h1>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 28 }}>
          {[['Cucinate', hist.length], ['Preferite', fav.length], ['Settimana', 4], ['Tot. ricette', window.RECIPES.length]].map(([l, v]) => (
            <div key={l} style={{ background: T.card, border: `1px solid ${T.ruleSoft}`, borderRadius: 12, padding: '16px' }}>
              <div style={{ fontFamily: T.serif, fontSize: 38, fontWeight: 500, fontStyle: 'italic', color: T.accent, lineHeight: 1 }}>{v}</div>
              <Eyebrow>{l}</Eyebrow>
            </div>
          ))}
        </div>

        <div style={{ display: 'flex', gap: 0, borderBottom: `1px solid ${T.ruleSoft}`, marginBottom: 18 }}>
          {[['fav', 'Preferite'], ['hist', 'Cronologia']].map(([k, l]) => (
            <button key={k} className="rcp-btn" onClick={() => setTab(k)}
              style={{ padding: '10px 18px', fontSize: 14, fontWeight: tab === k ? 600 : 500, color: tab === k ? T.ink : T.muted, borderBottom: tab === k ? `2px solid ${T.accent}` : '2px solid transparent', marginBottom: -1 }}>
              {l}
            </button>
          ))}
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px 24px' }}>
          {list.map((r) => (
            <button key={r.id} onClick={() => go('detail', { recipeId: r.id })} className="rcp-btn" style={{ textAlign: 'left' }}>
              <div style={{ borderRadius: 4, overflow: 'hidden', marginBottom: 8 }}>
                <Photo src={r.photo} label={r.nome} tone="#d4c8a8" text="#3a2f15" ratio="4/3" />
              </div>
              <Eyebrow size={8}>{r.categoria}</Eyebrow>
              <div style={{ fontFamily: T.serif, fontSize: 18, fontWeight: 500, letterSpacing: -0.3, marginTop: 2 }}>{r.nome}</div>
              <div style={{ fontFamily: T.mono, fontSize: 10, color: T.muted, marginTop: 4 }}>{fmtMin(r.tempo)} · {r.porzioni} pers</div>
            </button>
          ))}
        </div>
      </div>
    </DesktopShell>
  );
}

window.DesktopSearch = DesktopSearch;
window.DesktopCook = DesktopCook;
window.DesktopShopping = DesktopShopping;
window.DesktopProfile = DesktopProfile;
