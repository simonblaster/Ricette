// Design system unificato — "Recipees"
// Fusione di Editorial (tipografia + dettagli da rivista) + Smart (architettura
// app + micro-interazioni) + Typo Index (griglia rigorosa + monospace numeri).

const T = {
  // Colors — avorio caldo come fondo, ink scuro caldo, terracotta come accent
  bg: '#faf8f3',
  bgAlt: '#f3efe5',
  bgDeep: '#ebe4d3',
  ink: '#1a1714',
  inkSoft: '#3d342a',
  muted: '#857c6e',
  faint: '#c8bfae',
  rule: '#1a1714',
  ruleSoft: '#dad2bf',
  card: '#ffffff',
  accent: '#a83d20',         // terracotta — passi, stati attivi
  accentSoft: '#f4dccb',
  olive: 'oklch(0.45 0.08 130)',  // oliva — tag, categoria
  oliveSoft: 'oklch(0.94 0.04 130)',
  warn: '#c87a1e',
  // Type stacks
  serif: '"Source Serif 4", Georgia, serif',
  sans: '"Inter Tight", "Inter", -apple-system, sans-serif',
  mono: '"JetBrains Mono", ui-monospace, Menlo, monospace',
};

window.T = T;

// Format helpers — gestiscono valori mancanti / null / 0 graziosamente.
const fmtMin = (n) => (n && n > 0) ? `${n}m` : '—';        // per liste compatte
const fmtTime = (n) => (n && n > 0) ? `${n}'` : '—';       // per dettaglio (apostrofo)
const fmtTimeLong = (n) => (n && n > 0) ? `${n} min` : '—'; // per tag
window.fmtMin = fmtMin; window.fmtTime = fmtTime; window.fmtTimeLong = fmtTimeLong;

// Iconografia curata: stroke 1.5, line-cap round, geometry compatta.
// Tutte allineate a 16x16, scaling via prop size.
function makeIcon(viewBox, paths, opts = {}) {
  return function I({ size = 16, color = 'currentColor', fill = 'none', strokeWidth = opts.sw || 1.5 }) {
    return (
      <svg width={size} height={size} viewBox={viewBox} fill={fill} stroke={color}
        strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
        {paths}
      </svg>
    );
  };
}

const II = {
  search: makeIcon('0 0 16 16', <><circle cx="7" cy="7" r="4.5"/><path d="M10.5 10.5L13.5 13.5"/></>),
  back: makeIcon('0 0 16 16', <><path d="M9 3l-5 5 5 5"/><path d="M4 8h10"/></>),
  forward: makeIcon('0 0 16 16', <><path d="M7 3l5 5-5 5"/><path d="M12 8H2"/></>),
  chevR: makeIcon('0 0 16 16', <path d="M6 3l4 5-4 5"/>),
  chevL: makeIcon('0 0 16 16', <path d="M10 3l-4 5 4 5"/>),
  chevD: makeIcon('0 0 16 16', <path d="M3 6l5 4 5-4"/>),
  plus: makeIcon('0 0 16 16', <><path d="M8 3v10"/><path d="M3 8h10"/></>),
  minus: makeIcon('0 0 16 16', <path d="M3 8h10"/>),
  close: makeIcon('0 0 16 16', <><path d="M4 4l8 8"/><path d="M12 4l-8 8"/></>),
  check: makeIcon('0 0 16 16', <path d="M3 8.5l3 3 7-7"/>, { sw: 1.8 }),
  heart: makeIcon('0 0 16 16', <path d="M8 13.5s-5-3-5-7a3 3 0 015-2 3 3 0 015 2c0 4-5 7-5 7z"/>),
  bookmark: makeIcon('0 0 16 16', <path d="M4 2.5h8v11l-4-3-4 3z"/>),
  clock: makeIcon('0 0 16 16', <><circle cx="8" cy="8" r="6.4"/><path d="M8 4.5V8l2.5 1.6"/></>),
  users: makeIcon('0 0 16 16', <><circle cx="6" cy="6" r="2.4"/><path d="M2 13.5c.6-2.2 2-3.4 4-3.4s3.4 1.2 4 3.4"/><path d="M11 4.2a2.4 2.4 0 010 4M14.5 13c-.4-1.7-1.4-2.8-2.7-3.2"/></>),
  flame: makeIcon('0 0 16 16', <path d="M8 14c2.5 0 4.5-2 4.5-4.5 0-3-3-4-3-7 0 0-1.5 1.5-1.5 4 0 2-2 1.5-2 4 0 .8.5 1.5 1 2.2"/>),
  timer: makeIcon('0 0 16 16', <><path d="M8 14a5.5 5.5 0 100-11 5.5 5.5 0 000 11z"/><path d="M8 5.5V8M6 1.5h4"/></>),
  list: makeIcon('0 0 16 16', <><path d="M5 4h9M5 8h9M5 12h9"/><circle cx="2.5" cy="4" r=".5" fill="currentColor"/><circle cx="2.5" cy="8" r=".5" fill="currentColor"/><circle cx="2.5" cy="12" r=".5" fill="currentColor"/></>),
  cart: makeIcon('0 0 16 16', <><path d="M2 3h2l1.5 8h7l1.5-5H5"/><circle cx="6" cy="13.5" r=".8"/><circle cx="12" cy="13.5" r=".8"/></>),
  printer: makeIcon('0 0 16 16', <><path d="M4 5V2h8v3M4 11H2.5V5.5h11V11H12"/><path d="M4 9h8v5H4z"/></>),
  share: makeIcon('0 0 16 16', <><circle cx="12" cy="3.5" r="1.8"/><circle cx="4" cy="8" r="1.8"/><circle cx="12" cy="12.5" r="1.8"/><path d="M5.5 7l5-2.5M5.5 9l5 2.5"/></>),
  edit: makeIcon('0 0 16 16', <><path d="M11 2.5l2.5 2.5L6 12.5 3 13l.5-3z"/></>),
  user: makeIcon('0 0 16 16', <><circle cx="8" cy="6" r="2.6"/><path d="M3 13.5c.8-2.4 2.5-3.7 5-3.7s4.2 1.3 5 3.7"/></>),
  home: makeIcon('0 0 16 16', <><path d="M2.5 7L8 2.5 13.5 7v6.5h-3V10h-5v3.5h-3z"/></>),
  star: makeIcon('0 0 16 16', <path d="M8 1.5l2 4.4 4.8.5-3.6 3.3 1 4.7L8 12l-4.2 2.4 1-4.7L1.2 6.4 6 5.9z"/>),
  filter: makeIcon('0 0 16 16', <><path d="M2 3.5h12M4 8h8M6 12.5h4"/></>),
  tag: makeIcon('0 0 16 16', <><path d="M2 2.5h5L13.5 9 9 13.5 2.5 7z"/><circle cx="5" cy="5.5" r=".6" fill="currentColor"/></>),
  play: makeIcon('0 0 16 16', <path d="M5 3l8 5-8 5z"/>, { sw: 1.2 }),
  pause: makeIcon('0 0 16 16', <><path d="M5.5 3v10M10.5 3v10"/></>, { sw: 2 }),
  refresh: makeIcon('0 0 16 16', <><path d="M3 8a5 5 0 019-3l1 1M13 8a5 5 0 01-9 3l-1-1"/><path d="M13 2v3h-3M3 14v-3h3"/></>),
  sparkle: makeIcon('0 0 16 16', <><path d="M8 1.5v4M8 10.5v4M1.5 8h4M10.5 8h4"/></>),
};

window.II = II;

// ─────────────────────────────────────────────────────────────
// State condiviso: preferiti, cronologia, lista spesa, ricetta corrente.
// In un'app vera questo va in localStorage o backend; qui usiamo un
// simple store in-memory + listeners così tutte le viste reagiscono.
// ─────────────────────────────────────────────────────────────
const Store = (() => {
  // Init: prendi le prime ricette in elenco come seed dinamico per fav/storia
  const seedIds = (window.RECIPES || []).slice(0, 6).map(r => r.id);
  let state = {
    favorites: new Set(seedIds.slice(0, 3)),
    history: seedIds.slice(0, 4),
    shopping: new Set(),
  };
  const listeners = new Set();
  const notify = () => listeners.forEach((l) => l());
  return {
    get: () => state,
    subscribe(fn) { listeners.add(fn); return () => listeners.delete(fn); },
    toggleFav(id) {
      const s = new Set(state.favorites);
      if (s.has(id)) s.delete(id); else s.add(id);
      state = { ...state, favorites: s }; notify();
    },
    addToShopping(items) {
      const s = new Set(state.shopping);
      items.forEach((i) => s.add(i));
      state = { ...state, shopping: s }; notify();
    },
    toggleShopping(item) {
      const s = new Set(state.shopping);
      if (s.has(item)) s.delete(item); else s.add(item);
      state = { ...state, shopping: s }; notify();
    },
    clearShopping() { state = { ...state, shopping: new Set() }; notify(); },
    pushHistory(id) {
      const h = [id, ...state.history.filter((x) => x !== id)].slice(0, 8);
      state = { ...state, history: h }; notify();
    },
  };
})();

function useStore() {
  const [, force] = React.useReducer((x) => x + 1, 0);
  React.useEffect(() => Store.subscribe(force), []);
  return Store.get();
}

window.Store = Store;
window.useStore = useStore;

// Mini app router. Persistito per artboard tramite chiave.
function useApp(initial) {
  const [state, setState] = React.useState(initial || { screen: 'home', recipeId: null, query: '' });
  const navigate = (patch) => setState((s) => ({ ...s, ...patch }));
  const go = (screen, extra = {}) => navigate({ screen, ...extra });
  return { state, navigate, go };
}
window.useApp = useApp;

// Servings stepper (riusabile)
function useServings(base) {
  const [s, setS] = React.useState(base);
  const ratio = s / base;
  const fmtQ = (q) => {
    const v = q * ratio;
    if (Math.abs(v - Math.round(v)) < 0.05) return String(Math.round(v));
    if (v < 1) return v.toFixed(2).replace(/0+$/, '').replace(/\.$/, '');
    return v.toFixed(1).replace(/\.0$/, '');
  };
  // fmtIng: combina q + u in una stringa pulita; gestisce qb e quantità mancanti.
  // Ritorna {qty, hasQty}: qty è ciò che mostri (es. "200 g", "q.b.", "—"); hasQty è false per qb.
  const fmtIng = (ing) => {
    if (ing.qb) return { qty: 'q.b.', hasQty: false };
    const hasQ = ing.q !== '' && ing.q != null;
    const hasU = ing.u && ing.u !== '';
    if (!hasQ && !hasU) return { qty: 'q.b.', hasQty: false };
    if (!hasQ && hasU) return { qty: ing.u, hasQty: true };
    const qStr = fmtQ(parseFloat(ing.q));
    return { qty: hasU ? `${qStr} ${ing.u}` : qStr, hasQty: true };
  };
  return { servings: s, setS, ratio, fmtQ, fmtIng };
}
window.useServings = useServings;

// Foto: usa immagine reale se `src` viene passato; altrimenti placeholder striato.
function Photo({ src, label = 'foto', tone = T.bgDeep, text = T.inkSoft, radius = 0, ratio, style = {} }) {
  const wrap = ratio ? { aspectRatio: ratio, width: '100%' } : { width: '100%', height: '100%' };
  const [failed, setFailed] = React.useState(false);
  // Reset failed quando src cambia (es. cambio ricetta)
  React.useEffect(() => { setFailed(false); }, [src]);
  if (src && !failed) {
    return (
      <div style={{ ...wrap, overflow: 'hidden', borderRadius: radius, background: tone, ...style }}>
        <img src={src} alt={label} loading="lazy" decoding="async"
          onError={() => setFailed(true)}
          style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }} />
      </div>
    );
  }
  const stripe = `repeating-linear-gradient(135deg, ${tone} 0 10px, color-mix(in oklab, ${tone} 92%, black) 10px 20px)`;
  return (
    <div style={{
      ...wrap, background: stripe, display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontFamily: T.mono, fontSize: 9, color: text, letterSpacing: 1.5, textTransform: 'uppercase',
      borderRadius: radius, ...style,
    }}>· {label} ·</div>
  );
}
window.Photo = Photo;

// Tag pill — riusabile in tutta l'app
function Tag({ children, kind = 'default' }) {
  const styles = {
    default: { bg: T.bgAlt, color: T.inkSoft, border: T.ruleSoft },
    olive: { bg: T.oliveSoft, color: T.olive, border: 'transparent' },
    accent: { bg: T.accentSoft, color: T.accent, border: 'transparent' },
    ghost: { bg: 'transparent', color: T.muted, border: T.ruleSoft },
  }[kind];
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 4,
      padding: '3px 8px', borderRadius: 999, fontSize: 10,
      fontFamily: T.sans, fontWeight: 500, letterSpacing: 0.2,
      background: styles.bg, color: styles.color, border: `1px solid ${styles.border}`,
      whiteSpace: 'nowrap',
    }}>{children}</span>
  );
}
window.Tag = Tag;

// Eyebrow — letterspaced uppercase mono, usato ovunque per categorie/labels
function Eyebrow({ children, color = T.muted, size = 9 }) {
  return (
    <div style={{
      fontFamily: T.mono, fontSize: size, letterSpacing: 1.8,
      textTransform: 'uppercase', color, fontWeight: 500,
    }}>{children}</div>
  );
}
window.Eyebrow = Eyebrow;

// Frame: contenitore artboard
function Frame({ children, bg = T.bg, style = {} }) {
  return (
    <div style={{
      width: '100%', height: '100%', background: bg, color: T.ink,
      overflow: 'hidden', position: 'relative', display: 'flex', flexDirection: 'column',
      fontFamily: T.sans, ...style,
    }}>{children}</div>
  );
}
window.Frame = Frame;

// Hook: legge auth state Firebase e lo espone come valore React
function useFirebaseUser() {
  const [user, setUser] = React.useState(() =>
    window._firebaseAuth ? window._firebaseAuth.currentUser : null
  );
  React.useEffect(() => {
    const auth = window._firebaseAuth;
    if (!auth) return;
    return auth.onAuthStateChanged(setUser);
  }, []);
  return user;
}
window.useFirebaseUser = useFirebaseUser;

// CSS injection per scrollbar nascosta + scelte tipografiche
if (typeof document !== 'undefined' && !document.getElementById('recipees-styles')) {
  const s = document.createElement('style');
  s.id = 'recipees-styles';
  s.textContent = `
    .rcp-scroll{overflow:auto}
    .rcp-scroll::-webkit-scrollbar{display:none}
    .rcp-scroll{scrollbar-width:none}
    .rcp-btn{cursor:pointer;border:none;background:transparent;font-family:inherit;color:inherit;padding:0}
    .rcp-link{cursor:pointer;text-decoration:none;color:inherit}
    .rcp-link:hover{opacity:.85}
    .rcp-press{transition:transform .08s}
    .rcp-press:active{transform:scale(.97)}
  `;
  document.head.appendChild(s);
}
