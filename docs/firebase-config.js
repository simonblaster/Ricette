// ── Configurazione Firebase ───────────────────────────────────────────────────
// Da compilare dopo aver creato il progetto Firebase.
// Vai su: https://console.firebase.google.com → tuo progetto → ⚙️ → Impostazioni progetto
//         → Le tue app → App web → Configurazione SDK
//
// NOTA: queste chiavi sono pubbliche (lato client) — la sicurezza è gestita
//       dalle Firestore Security Rules nel progetto Firebase.

window.FIREBASE_CONFIG = {
  apiKey:            "AIzaSyBUixFKA2UX1dCTXe7YGzuB0CA1BEmtQPs",
  authDomain:        "ricette-commenti.firebaseapp.com",
  projectId:         "ricette-commenti",
  storageBucket:     "ricette-commenti.firebasestorage.app",
  messagingSenderId: "650506832928",
  appId:             "1:650506832928:web:de1870ca7f81f6dfb90045",
  measurementId:     "G-N3PGW9E6SG"
};

// Inizializza Firebase solo se la config è stata compilata
(function () {
  const cfg = window.FIREBASE_CONFIG;
  if (!cfg || cfg.apiKey === 'DA_COMPILARE') {
    console.info('[Firebase] Config non ancora compilata — commenti disattivati.');
    return;
  }
  try {
    window._firebaseApp  = firebase.initializeApp(cfg);
    window._firebaseAuth = firebase.auth(window._firebaseApp);
    window._firebaseDb   = firebase.firestore(window._firebaseApp);
    // Abilita persistenza offline
    window._firebaseDb.enablePersistence({ synchronizeTabs: true })
      .catch(() => {/* ignorato */});
    console.info('[Firebase] Inizializzato correttamente.');
  } catch (e) {
    console.warn('[Firebase] Errore inizializzazione:', e);
  }
})();
