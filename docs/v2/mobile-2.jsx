// Mobile screens part 2 — Search, Cook, Shopping, Profile

// ─── SEARCH ─────────────────────────────────────────────────
function MobileSearch({ go, back }) {
  const [q, setQ] = React.useState('');
  const [activeTags, setActiveTags] = React.useState(new Set());
  const allTags = Array.from(new Set(window.RECIPES.flatMap((r) => r.tag || []))).sort();
  const filtered = window.RECIPES.filter((r) => {
    if (q && !r.nome.toLowerCase().includes(q.toLowerCase()) && !r.ingredienti.some((i) => i.n.toLowerCase().includes(q.toLowerCase()))) return false;
    if (activeTags.size > 0 && !(r.tag || []).some((t) => activeTags.has(t))) return false;
    return true;
  });
  const toggle = (t) => setActiveTags((s) => { const n = new Set(s); n.has(t) ? n.delete(t) : n.add(t); return n; });
  const suggestions = ['veloce', 'vegan', 'classico', 'inverno', 'lievitazione lunga'];

  return (
    <Frame>
      <div style={{ padding: '18px 18px 12px', borderBottom: `1px solid ${T.ruleSoft}` }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <button onClick={back} className="rcp-btn"><II.back size={16} /></button>
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: 8, background: T.card, border: `1px solid ${T.ruleSoft}`, borderRadius: 12, padding: '10px 12px' }}>
            <II.search size={14} color={T.muted} />
            <input autoFocus value={q} onChange={(e) => setQ(e.target.value)} placeholder="Nome o ingrediente…"
              style={{ flex: 1, border: 'none', outline: 'none', background: 'transparent', fontFamily: T.sans, fontSize: 13, color: T.ink }} />
            {q && <button className="rcp-btn" onClick={() => setQ('')}><II.close size={12} color={T.muted} /></button>}
          </div>
        </div>
      </div>
      <div className="rcp-scroll" style={{ flex: 1, padding: '14px 18px 90px' }}>
        <Eyebrow>· Filtra per tag</Eyebrow>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, margin: '10px 0 18px' }}>
          {allTags.map((t) => {
            const a = activeTags.has(t);
            return (
              <button key={t} className="rcp-btn" onClick={() => toggle(t)} style={{
                padding: '6px 12px', borderRadius: 999, fontSize: 11, fontWeight: 500,
                background: a ? T.ink : 'transparent', color: a ? T.bg : T.inkSoft,
                border: `1px solid ${a ? T.ink : T.ruleSoft}`,
              }}>{t}</button>
            );
          })}
        </div>

        {q === '' && activeTags.size === 0 && (
          <>
            <Eyebrow>· Suggerimenti</Eyebrow>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 2, margin: '8px 0 18px' }}>
              {suggestions.map((s) => (
                <button key={s} className="rcp-btn" onClick={() => setQ(s)}
                  style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '11px 0', textAlign: 'left', borderBottom: `1px dotted ${T.ruleSoft}` }}>
                  <II.search size={11} color={T.muted} />
                  <span style={{ fontFamily: T.serif, fontSize: 15, fontStyle: 'italic' }}>{s}</span>
                  <span style={{ flex: 1 }} />
                  <II.forward size={12} color={T.muted} />
                </button>
              ))}
            </div>
          </>
        )}

        <Eyebrow>· {filtered.length} risultat{filtered.length === 1 ? 'o' : 'i'}</Eyebrow>
        <div style={{ marginTop: 10 }}>
          {filtered.map((r, i) => (
            <button key={r.id} onClick={() => go('detail', { recipeId: r.id })} className="rcp-btn"
              style={{ display: 'flex', gap: 12, width: '100%', padding: '12px 0', borderBottom: `1px solid ${T.ruleSoft}`, alignItems: 'center', textAlign: 'left' }}>
              <div style={{ width: 56, height: 56, borderRadius: 4, overflow: 'hidden', flexShrink: 0 }}>
                <Photo src={r.photo} label={r.nome} tone="#d4c8a8" text="#3a2f15" />
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <Eyebrow size={8}>{r.categoria}</Eyebrow>
                <div style={{ fontFamily: T.serif, fontSize: 17, fontWeight: 500, letterSpacing: -0.3, lineHeight: 1.1, marginTop: 2 }}>{r.nome}</div>
                <div style={{ fontFamily: T.mono, fontSize: 10, color: T.muted, marginTop: 4 }}>{fmtMin(r.tempo)} · {r.porzioni} pers · {r.difficolta}</div>
              </div>
              <II.chevR size={14} color={T.muted} />
            </button>
          ))}
        </div>
      </div>
      <BottomNav active="search" go={go} />
    </Frame>
  );
}

// ─── COOK MODE step-by-step ─────────────────────────────────
function MobileCook({ recipe, back }) {
  const [step, setStep] = React.useState(0);
  const total = recipe.passi.length;
  const [timerSec, setTimerSec] = React.useState(0);
  const [timerRunning, setTimerRunning] = React.useState(false);

  React.useEffect(() => {
    if (!timerRunning) return;
    const t = setInterval(() => setTimerSec((s) => Math.max(0, s - 1)), 1000);
    return () => clearInterval(t);
  }, [timerRunning]);

  const fmt = (s) => `${Math.floor(s / 60).toString().padStart(2, '0')}:${(s % 60).toString().padStart(2, '0')}`;
  const presets = [3, 5, 10, 15];

  return (
    <Frame bg={T.ink} style={{ color: T.bg }}>
      {/* top bar */}
      <div style={{ padding: '18px 18px 12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <button onClick={back} className="rcp-btn" style={{ color: T.bg, opacity: 0.7 }}><II.close size={18} color={T.bg} /></button>
        <div style={{ fontFamily: T.mono, fontSize: 10, letterSpacing: 2, textTransform: 'uppercase', opacity: 0.6 }}>{recipe.nome}</div>
        <div style={{ fontFamily: T.mono, fontSize: 11, fontVariantNumeric: 'tabular-nums', opacity: 0.8 }}>{step + 1}/{total}</div>
      </div>

      {/* progress dots */}
      <div style={{ padding: '0 18px', display: 'flex', gap: 4 }}>
        {recipe.passi.map((_, i) => (
          <div key={i} style={{ flex: 1, height: 3, borderRadius: 2, background: i <= step ? T.accent : 'rgba(250,248,243,0.15)' }} />
        ))}
      </div>

      {/* step content */}
      <div className="rcp-scroll" style={{ flex: 1, padding: '40px 24px 24px', display: 'flex', flexDirection: 'column' }}>
        <div style={{ fontFamily: T.serif, fontSize: 96, fontWeight: 500, fontStyle: 'italic', lineHeight: 0.85, color: T.accent, letterSpacing: -2 }}>
          {step + 1}
        </div>
        <div style={{ fontFamily: T.serif, fontSize: 24, fontWeight: 500, lineHeight: 1.35, letterSpacing: -0.4, marginTop: 18 }}>
          {recipe.passi[step]}
        </div>

        {/* timer */}
        <div style={{ marginTop: 32, padding: 16, background: 'rgba(250,248,243,0.06)', border: '1px solid rgba(250,248,243,0.1)', borderRadius: 14 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <Eyebrow color="rgba(250,248,243,0.6)">Timer</Eyebrow>
            <div style={{ fontFamily: T.mono, fontSize: 28, fontWeight: 500, fontVariantNumeric: 'tabular-nums', letterSpacing: -1, color: timerSec > 0 ? T.bg : 'rgba(250,248,243,0.4)' }}>{fmt(timerSec)}</div>
          </div>
          <div style={{ display: 'flex', gap: 6 }}>
            {presets.map((m) => (
              <button key={m} className="rcp-btn" onClick={() => { setTimerSec(m * 60); setTimerRunning(true); }}
                style={{ flex: 1, padding: '8px', border: '1px solid rgba(250,248,243,0.15)', borderRadius: 8, fontSize: 12, fontWeight: 600, color: T.bg }}>{m}m</button>
            ))}
            <button className="rcp-btn" onClick={() => setTimerRunning((r) => !r)}
              style={{ width: 40, padding: '8px', background: T.accent, borderRadius: 8, color: T.bg, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {timerRunning ? <II.pause size={12} color={T.bg} /> : <II.play size={12} color={T.bg} fill={T.bg} />}
            </button>
          </div>
        </div>
      </div>

      {/* bottom nav step */}
      <div style={{ padding: '14px 18px 20px', display: 'flex', gap: 10 }}>
        <button onClick={() => setStep(Math.max(0, step - 1))} disabled={step === 0} className="rcp-btn"
          style={{ width: 56, height: 56, borderRadius: 28, border: '1px solid rgba(250,248,243,0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: step === 0 ? 0.3 : 1, color: T.bg }}>
          <II.chevL size={16} color={T.bg} />
        </button>
        <button onClick={() => step < total - 1 ? setStep(step + 1) : back()} className="rcp-btn rcp-press"
          style={{ flex: 1, height: 56, borderRadius: 28, background: T.accent, color: T.bg, fontWeight: 600, fontSize: 14, letterSpacing: -0.1 }}>
          {step < total - 1 ? 'Passo successivo' : 'Buon appetito ✦'}
        </button>
      </div>
    </Frame>
  );
}

// ─── SHOPPING ───────────────────────────────────────────────
function MobileShopping({ go }) {
  const store = useStore();
  const items = Array.from(store.shopping);
  // raggruppa euristicamente
  const grouped = items.reduce((acc, it) => {
    const k = (it || '').toLowerCase();
    let cat = 'Altro';
    if (/farina|lievito|riso|pasta|savoiardi|sale|zucchero/.test(k)) cat = 'Dispensa';
    else if (/pomodor|melanzan|cipoll|sedano|carota|prezzemolo|limon|olive|capperi/.test(k)) cat = 'Frutta e verdura';
    else if (/pollo|pancetta|uova|mascarpone|panna|burro|parmigiano|pecorino/.test(k)) cat = 'Frigorifero';
    else if (/olio|aceto|pepe|vaniglia|zafferano|cacao|brodo|vino|gelatina|miele|malto/.test(k)) cat = 'Condimenti';
    else if (/fagioli/.test(k)) cat = 'Legumi e cereali';
    (acc[cat] = acc[cat] || []).push(it);
    return acc;
  }, {});
  const order = ['Frutta e verdura', 'Frigorifero', 'Dispensa', 'Legumi e cereali', 'Condimenti', 'Altro'];

  return (
    <Frame>
      <div className="rcp-scroll" style={{ flex: 1, padding: '20px 18px 100px' }}>
        <Eyebrow color={T.accent}>· La tua spesa</Eyebrow>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginTop: 4, marginBottom: 18 }}>
          <h1 style={{ fontFamily: T.serif, fontSize: 28, fontWeight: 500, letterSpacing: -0.6, margin: 0, lineHeight: 1 }}>
            Lista <span style={{ fontStyle: 'italic' }}>spesa</span>
          </h1>
          <div style={{ fontFamily: T.mono, fontSize: 11, color: T.muted }}>{items.length} voci</div>
        </div>

        {items.length === 0 ? (
          <div style={{ marginTop: 60, textAlign: 'center', color: T.muted }}>
            <II.cart size={32} color={T.faint} />
            <div style={{ fontFamily: T.serif, fontSize: 17, fontStyle: 'italic', marginTop: 12 }}>Lista vuota</div>
            <div style={{ fontSize: 12, marginTop: 6, lineHeight: 1.5, maxWidth: 220, margin: '6px auto 0' }}>
              Apri una ricetta e tocca <II.cart size={11} color={T.muted} /> per aggiungere gli ingredienti.
            </div>
          </div>
        ) : (
          order.filter((c) => grouped[c]).map((c) => (
            <div key={c} style={{ marginBottom: 22 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', borderBottom: `1px solid ${T.ink}`, paddingBottom: 6, marginBottom: 4 }}>
                <Eyebrow>· {c}</Eyebrow>
                <div style={{ fontFamily: T.mono, fontSize: 10, color: T.muted }}>{grouped[c].length}</div>
              </div>
              {grouped[c].map((it) => (
                <button key={it} className="rcp-btn" onClick={() => Store.toggleShopping(it)}
                  style={{ display: 'flex', alignItems: 'center', gap: 12, width: '100%', padding: '11px 0', borderBottom: `1px dotted ${T.ruleSoft}`, textAlign: 'left' }}>
                  <span style={{ width: 18, height: 18, borderRadius: 9, border: `1.5px solid ${T.faint}` }} />
                  <span style={{ fontSize: 14, flex: 1 }}>{it}</span>
                </button>
              ))}
            </div>
          ))
        )}
        {items.length > 0 && (
          <button onClick={() => Store.clearShopping()} className="rcp-btn"
            style={{ marginTop: 20, fontSize: 12, color: T.muted, textDecoration: 'underline' }}>Svuota la lista</button>
        )}
      </div>
      <BottomNav active="shopping" go={go} />
    </Frame>
  );
}

// ─── PROFILE / FAVORITES ────────────────────────────────────
function MobileProfile({ go }) {
  const store = useStore();
  const fbUser = window.useFirebaseUser ? window.useFirebaseUser() : null;
  const [tab, setTab] = React.useState('fav');
  const fav = Array.from(store.favorites).map((id) => window.RECIPES.find((r) => r.id === id)).filter(Boolean);
  const hist = store.history.map((id) => window.RECIPES.find((r) => r.id === id)).filter(Boolean);
  const list = tab === 'fav' ? fav : hist;

  const displayName = fbUser ? (fbUser.displayName || 'Utente') : 'Simone';
  const firstName = displayName.split(' ')[0];
  const initial = firstName[0].toUpperCase();

  return (
    <Frame>
      <div className="rcp-scroll" style={{ flex: 1, padding: '20px 18px 100px' }}>

        {/* Header utente */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 22 }}>
          {fbUser && fbUser.photoURL
            ? <img src={fbUser.photoURL} alt="" style={{ width: 56, height: 56, borderRadius: 28, objectFit: 'cover', flexShrink: 0 }} />
            : <div style={{ width: 56, height: 56, borderRadius: 28, background: T.bgDeep, flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: T.serif, fontSize: 22, fontStyle: 'italic', color: T.accent, fontWeight: 500 }}>{initial}</div>
          }
          <div style={{ minWidth: 0 }}>
            <Eyebrow>· Profilo</Eyebrow>
            <div style={{ fontFamily: T.serif, fontSize: 22, fontWeight: 500, letterSpacing: -0.4, marginTop: 2 }}>{firstName}</div>
            <div style={{ fontFamily: T.mono, fontSize: 10, color: T.muted, marginTop: 2 }}>{fav.length} preferite · {hist.length} cucinate</div>
          </div>
          {/* Login / Logout */}
          {fbUser
            ? <button className="rcp-btn" onClick={() => window._firebaseAuth && window._firebaseAuth.signOut()}
                style={{ marginLeft: 'auto', fontFamily: T.mono, fontSize: 9, color: T.muted, letterSpacing: 1,
                  textTransform: 'uppercase', padding: '5px 8px', border: `1px solid ${T.ruleSoft}`, borderRadius: 6, flexShrink: 0 }}>
                Esci
              </button>
            : <button className="rcp-btn" onClick={() => window.loginGoogle && window.loginGoogle()}
                style={{ marginLeft: 'auto', fontFamily: T.mono, fontSize: 9, color: T.accent, letterSpacing: 1,
                  textTransform: 'uppercase', padding: '5px 8px', border: `1px solid ${T.accentSoft}`, borderRadius: 6, flexShrink: 0 }}>
                Accedi
              </button>
          }
        </div>

        {/* Stats */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 8, marginBottom: 22 }}>
          {[['Cucinate', hist.length], ['Preferite', fav.length], ['Settimana', 4]].map(([l, v]) => (
            <div key={l} style={{ background: T.card, border: `1px solid ${T.ruleSoft}`, borderRadius: 12, padding: '12px 10px', textAlign: 'center' }}>
              <div style={{ fontFamily: T.serif, fontSize: 24, fontWeight: 500, fontStyle: 'italic', color: T.accent, lineHeight: 1 }}>{v}</div>
              <Eyebrow size={8}>{l}</Eyebrow>
            </div>
          ))}
        </div>

        {/* Tabs */}
        <div style={{ display: 'flex', gap: 0, borderBottom: `1px solid ${T.ruleSoft}`, marginBottom: 14 }}>
          {[['fav', '♥ Preferite'], ['hist', 'Cronologia']].map(([k, l]) => (
            <button key={k} className="rcp-btn" onClick={() => setTab(k)}
              style={{ padding: '10px 16px', fontSize: 13, fontWeight: tab === k ? 600 : 500, color: tab === k ? T.ink : T.muted, borderBottom: tab === k ? `2px solid ${T.accent}` : '2px solid transparent', marginBottom: -1 }}>
              {l}
            </button>
          ))}
        </div>

        {list.length === 0 && tab === 'fav' && (
          <div style={{ textAlign: 'center', padding: '40px 0', color: T.muted }}>
            <II.heart size={28} color={T.faint} />
            <div style={{ fontFamily: T.serif, fontSize: 16, fontStyle: 'italic', marginTop: 10 }}>Nessuna ricetta preferita.</div>
            <div style={{ fontSize: 12, marginTop: 6 }}>Tocca ♥ nelle ricette per aggiungerle qui.</div>
          </div>
        )}

        {list.map((r, i) => (
          <div key={r.id + i} style={{ display: 'flex', gap: 12, width: '100%', padding: '11px 0', borderBottom: `1px dotted ${T.ruleSoft}`, alignItems: 'center' }}>
            <button onClick={() => go('detail', { recipeId: r.id })} className="rcp-btn"
              style={{ display: 'flex', gap: 12, flex: 1, alignItems: 'center', textAlign: 'left', minWidth: 0 }}>
              <div style={{ width: 48, height: 48, borderRadius: 4, overflow: 'hidden', flexShrink: 0 }}>
                <Photo src={r.photo} label={r.nome} tone="#d4c8a8" text="#3a2f15" />
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontFamily: T.serif, fontSize: 16, fontWeight: 500, letterSpacing: -0.3 }}>{r.nome}</div>
                <div style={{ fontFamily: T.mono, fontSize: 10, color: T.muted, marginTop: 2 }}>{fmtMin(r.tempo)} · {r.categoria}</div>
              </div>
            </button>
            {/* ♥ cliccabile per rimuovere dai preferiti */}
            {tab === 'fav' && (
              <button className="rcp-btn rcp-press" onClick={() => Store.toggleFav(r.id)}
                style={{ padding: 8, flexShrink: 0 }}>
                <II.heart size={16} color={T.accent} fill={T.accent} />
              </button>
            )}
          </div>
        ))}
      </div>
      <BottomNav active="profile" go={go} />
    </Frame>
  );
}

window.MobileSearch = MobileSearch;
window.MobileCook = MobileCook;
window.MobileShopping = MobileShopping;
window.MobileProfile = MobileProfile;
