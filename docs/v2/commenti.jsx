// commenti.jsx — Sezione commenti Firebase per ogni ricetta
// Dipende da: firebase-config.js (caricato prima in index.html)
// Usa: window._firebaseAuth, window._firebaseDb (inizializzati in firebase-config.js)

function CommentiSection({ recipeUid }) {
  const [user,      setUser]      = React.useState(null);
  const [commenti,  setCommenti]  = React.useState([]);
  const [testo,     setTesto]     = React.useState('');
  const [loading,   setLoading]   = React.useState(true);
  const [inviando,  setInviando]  = React.useState(false);
  const [errore,    setErrore]    = React.useState(null);

  const fbReady = !!(window._firebaseAuth && window._firebaseDb);

  React.useEffect(() => {
    if (!fbReady) { setLoading(false); return; }

    // Ascolta cambi autenticazione
    const unsubAuth = window._firebaseAuth.onAuthStateChanged(u => setUser(u));

    // Ascolta in real-time i commenti di questa ricetta
    let unsubDb = () => {};
    try {
      unsubDb = window._firebaseDb
        .collection('commenti')
        .where('recipeUid', '==', recipeUid)
        .orderBy('data', 'asc')
        .onSnapshot(
          snap => {
            setCommenti(snap.docs.map(d => ({ id: d.id, ...d.data() })));
            setLoading(false);
            setErrore(null);
          },
          err => {
            console.warn('[Commenti] Errore Firestore:', err);
            setLoading(false);
            // Se mancano gli indici Firestore mostra messaggio utile
            if (err.code === 'failed-precondition') {
              setErrore('Indice Firestore in costruzione — riprova tra qualche minuto.');
            }
          }
        );
    } catch (e) {
      setLoading(false);
    }

    return () => { unsubAuth(); unsubDb(); };
  }, [recipeUid, fbReady]);

  const login = () => {
    const provider = new firebase.auth.GoogleAuthProvider();
    window._firebaseAuth.signInWithPopup(provider).catch(e => {
      setErrore('Errore di accesso: ' + e.message);
    });
  };

  const logout = () => window._firebaseAuth.signOut();

  const invia = async () => {
    if (!testo.trim() || !user || inviando) return;
    setInviando(true);
    setErrore(null);
    try {
      await window._firebaseDb.collection('commenti').add({
        recipeUid,
        testo:       testo.trim(),
        authorName:  user.displayName || 'Utente',
        authorPhoto: user.photoURL    || null,
        authorUid:   user.uid,
        data:        firebase.firestore.FieldValue.serverTimestamp(),
        synced:      false,
      });
      setTesto('');
    } catch (e) {
      setErrore('Errore nell\'invio: ' + e.message);
    } finally {
      setInviando(false);
    }
  };

  // Se Firebase non è configurato, non renderizza nulla
  if (!fbReady) return null;

  const fmtData = (ts) => {
    if (!ts) return '';
    try {
      return new Date(ts.seconds * 1000).toLocaleDateString('it-IT', {
        day: '2-digit', month: 'long', year: 'numeric'
      });
    } catch { return ''; }
  };

  return (
    <div style={{ marginTop: 48, paddingTop: 24, borderTop: `2px solid ${T.ink}` }}>
      {/* Titolo sezione */}
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 10, marginBottom: 20 }}>
        <h2 style={{ fontFamily: T.serif, fontSize: 22, fontWeight: 500,
                     letterSpacing: -0.4, margin: 0, fontStyle: 'italic' }}>
          Commenti
        </h2>
        {commenti.length > 0 && (
          <span style={{ fontFamily: T.mono, fontSize: 11, color: T.muted }}>
            {commenti.length}
          </span>
        )}
      </div>

      {/* Errore */}
      {errore && (
        <div style={{ padding: '10px 14px', borderRadius: 8, background: '#fef2f2',
                      color: '#b91c1c', fontSize: 13, marginBottom: 16 }}>
          {errore}
        </div>
      )}

      {/* Lista commenti */}
      {loading ? (
        <p style={{ color: T.muted, fontSize: 13, fontStyle: 'italic' }}>
          Caricamento commenti…
        </p>
      ) : (
        <>
          {commenti.length === 0 && (
            <p style={{ color: T.muted, fontSize: 13, fontStyle: 'italic',
                        marginBottom: 24 }}>
              Nessun commento ancora. Hai provato questa ricetta?
            </p>
          )}

          {commenti.map(c => (
            <div key={c.id} style={{ display: 'flex', gap: 12, marginBottom: 20,
                                     paddingBottom: 20,
                                     borderBottom: `1px solid ${T.ruleSoft}` }}>
              {/* Avatar */}
              {c.authorPhoto ? (
                <img src={c.authorPhoto} alt=""
                     style={{ width: 36, height: 36, borderRadius: 18,
                              flexShrink: 0, objectFit: 'cover' }} />
              ) : (
                <div style={{ width: 36, height: 36, borderRadius: 18, flexShrink: 0,
                              background: T.card, border: `1px solid ${T.ruleSoft}`,
                              display: 'flex', alignItems: 'center',
                              justifyContent: 'center', fontSize: 14,
                              fontFamily: T.serif, color: T.accent }}>
                  {(c.authorName || '?')[0].toUpperCase()}
                </div>
              )}

              {/* Contenuto */}
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: 'flex', gap: 8, alignItems: 'baseline',
                              flexWrap: 'wrap', marginBottom: 6 }}>
                  <span style={{ fontWeight: 600, fontSize: 13 }}>
                    {c.authorName}
                  </span>
                  <span style={{ fontSize: 11, color: T.muted, fontFamily: T.mono }}>
                    {fmtData(c.data)}
                  </span>
                </div>
                <p style={{ margin: 0, fontSize: 14, lineHeight: 1.6,
                            color: T.inkSoft, whiteSpace: 'pre-wrap' }}>
                  {c.testo}
                </p>
              </div>
            </div>
          ))}

          {/* Form nuovo commento */}
          <div style={{ marginTop: commenti.length > 0 ? 8 : 0,
                        padding: '20px', borderRadius: 12,
                        background: T.card, border: `1px solid ${T.ruleSoft}` }}>
            {user ? (
              <>
                {/* Utente loggato */}
                <div style={{ display: 'flex', alignItems: 'center', gap: 8,
                              marginBottom: 12 }}>
                  {user.photoURL && (
                    <img src={user.photoURL} alt=""
                         style={{ width: 24, height: 24, borderRadius: 12 }} />
                  )}
                  <span style={{ fontSize: 13, color: T.inkSoft }}>
                    {user.displayName}
                  </span>
                  <button onClick={logout} className="rcp-btn"
                    style={{ marginLeft: 'auto', fontSize: 11, color: T.muted,
                             padding: '3px 8px', borderRadius: 6,
                             border: `1px solid ${T.ruleSoft}` }}>
                    Esci
                  </button>
                </div>

                <textarea
                  value={testo}
                  onChange={e => setTesto(e.target.value)}
                  onKeyDown={e => {
                    // Cmd/Ctrl+Enter per inviare
                    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') invia();
                  }}
                  placeholder="Hai provato questa ricetta? Come è andata? Hai modificato qualcosa?"
                  rows={3}
                  style={{ width: '100%', padding: '10px 12px', borderRadius: 8,
                           border: `1px solid ${T.ruleSoft}`, background: '#faf8f3',
                           fontFamily: 'inherit', fontSize: 14, resize: 'vertical',
                           color: T.ink, boxSizing: 'border-box', outline: 'none',
                           lineHeight: 1.55 }}
                />
                <div style={{ display: 'flex', justifyContent: 'flex-end',
                              alignItems: 'center', gap: 8, marginTop: 10 }}>
                  <span style={{ fontSize: 11, color: T.muted, fontFamily: T.mono }}>
                    ⌘↵ per inviare
                  </span>
                  <button onClick={invia}
                    disabled={inviando || !testo.trim()} className="rcp-btn rcp-press"
                    style={{ padding: '9px 20px', borderRadius: 8,
                             background: testo.trim() ? T.ink : T.ruleSoft,
                             color: testo.trim() ? T.bg : T.muted,
                             fontWeight: 600, fontSize: 13, transition: 'all .15s',
                             cursor: testo.trim() ? 'pointer' : 'default' }}>
                    {inviando ? 'Invio…' : 'Pubblica'}
                  </button>
                </div>
              </>
            ) : (
              /* Non loggato */
              <div style={{ textAlign: 'center', padding: '8px 0' }}>
                <p style={{ fontSize: 14, color: T.inkSoft, margin: '0 0 14px' }}>
                  Accedi con Google per lasciare un commento
                </p>
                <button onClick={login} className="rcp-btn rcp-press"
                  style={{ display: 'inline-flex', alignItems: 'center', gap: 10,
                           padding: '11px 20px', borderRadius: 10,
                           border: `1px solid ${T.ruleSoft}`, background: '#fff',
                           fontSize: 14, fontWeight: 500, color: '#3c4043',
                           boxShadow: '0 1px 3px rgba(0,0,0,.12)' }}>
                  <svg width="18" height="18" viewBox="0 0 24 24">
                    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05"/>
                    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                  </svg>
                  Accedi con Google
                </button>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

window.CommentiSection = CommentiSection;
