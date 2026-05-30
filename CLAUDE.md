# Recipees — sessione coordinamento (Claude Code)

## Ruolo di questa sessione

La sessione **Recipees** è il supervisore cross-prodotto dell'ecosistema.
Non sviluppa codice direttamente: coordina le altre sessioni, verifica la
coerenza dei contratti tra i prodotti, mantiene i file condivisi, archivia
le decisioni che toccano più prodotti.

Le sessioni attive:

| Sessione | Prodotto / Ruolo | Directory di lavoro | Committa su |
|----------|------------------|---------------------|-------------|
| **Recipees** | Coordinamento + merge in `main` di Domus | `./` (root) | `main` (docs) + merge Domus |
| **Memoria** | iOS app (Heirloom) | `Heirloom/` | `main` Heirloom |
| **Domus-funzionalità** | Web app — feature | worktree su `feat/*` | branch `feat/*` |
| **Domus-debug** | Web app — bug-fix | worktree su `fix/*` | branch `fix/*` |

> **Una sessione = un prodotto = una verità.** Niente sessioni doppie sullo
> stesso prodotto: le vecchie sessioni Cowork pre-migrazione Claude Code vanno
> archiviate. Le due sessioni Domus lavorano lo stesso repo in **git worktree
> separati su branch dedicati** — il merge in `main` lo fa Recipees. Dettaglio:
> `RECIPEES_HUB.md` → CONVENZIONI, e `recipees-domus/CLAUDE.md` → Workflow git.
> Ogni sessione ha il proprio `CLAUDE.md` nella propria directory.

---

## Rituale fisso — ogni sessione senza eccezioni

1. **A inizio sessione:** leggi `RECIPEES_HUB.md` per intero.
2. **Durante la sessione:** aggiorna la sezione "Recipees" se prendi decisioni
   cross-prodotto o ricevi brief dalle altre sessioni.
3. **A fine sessione:** aggiorna "Ultimo aggiornamento" in cima a `RECIPEES_HUB.md`.
4. **Non riscrivere le sezioni di Memoria o Domus** — quelle le mantengono loro.
5. Se una decisione tocca più prodotti: aggiornala nel log
   "DECISIONI CROSS-PRODUCT" di `RECIPEES_HUB.md`.

---

## I tre prodotti

| Prodotto | Gesto | Cos'è |
|----------|-------|-------|
| **Memoria** | riscopri | App iOS, acquisizione ricette (foto, voce, video, PDF). Codename Xcode: Heirloom. iOS 17+, Swift 6, SwiftUI. |
| **Domus** | condividi | Web app, ricettario di famiglia online — `recipees.app`. Next.js 16 + Firebase. |
| **Folio** | tramanda | Libro stampato. Apre set 2026. Sessione non attiva. |

**Claim:** *Riscoperte. Condividi. Tramandate.*
**Voce brand:** memoir, sostantivi concreti, niente urgenza, niente tech-speak.

---

## File chiave (root)

| File | Scopo |
|------|-------|
| `RECIPEES_HUB.md` | Hub coordinamento — leggere a inizio, aggiornare a fine sessione |
| `ROADMAP_bug.md` | Bug tracker vivo per tutti e tre i prodotti |
| `ROADMAP_funzionalita.md` | Feature tracker |
| `GUIDA_PROCESSI.md` | Processi ricorrenti del vecchio sito Paprika/GitHub Pages |
| `beta-testers/` | Roster beta tester — non duplicare contatti in memoria |
| `test_exports/` | Fixture di test per il contratto Memoria→Domus (Pack v3) |

---

## Contratto Memoria → Domus (Pack v3)

Il contratto di export è definito in `RECIPEES_HUB.md` sezione
"CONTRATTO MEMORIA → DOMUS". È **stabile e additivo-only**: Memoria
produce uno ZIP, Domus lo importa. Campi nuovi solo opzionali, UUID
`book.id`/`recipe.id` stabili tra re-export.

Per verificare che il contratto regga: la sessione Recipees fa da arbitro
tra le due sessioni quando le spec divergono.

---

## Workflow git

Il repo è `simonblaster/Ricette` su GitHub (monorepo).
Il sito GitHub Pages legacy (Paprika) usa `aggiorna_sito.sh` / `aggiorna_sito.py`.

```bash
# Commit per i file di coordinamento
git add RECIPEES_HUB.md ROADMAP_bug.md ROADMAP_funzionalita.md
git commit -m "docs: aggiorna hub e roadmap — [descrizione breve]"
git push origin main
```

Per eseguire comandi git da questa sessione usare **Desktop Commander**
(`mcp__Desktop_Commander__start_process` con shell `zsh`): il bash sandbox
di Cowork non ha le credenziali SSH per GitHub.

---

## Regola inviolabile — dati utente

Attiva per Memoria e Domus dal momento del primo utente reale (14 mag 2026):

> I dati preesistenti dell'utente non si toccano. Restano intatti attraverso
> ogni nuova build, update o cambio di schema. Un update che cancella o
> corrompe dati preesistenti è un fallimento grave.

Conseguenze pratiche:
- Domus: soft delete (`deletedAt`), schema Firestore additivo-only, no deleteDoc su collezioni utente.
- Memoria: Codable con `decodeIfPresent` per ogni nuovo campo, BookStore fail-safe, no auto-save su load fallito.

Vedi i rispettivi `AGENTS.md` per i dettagli.

---

## Timeline lancio

| Data | Milestone |
|------|-----------|
| 14 mag 2026 | Domus online beta amici |
| **5 giu 2026** | Lancio beta amici unificato Memoria + Domus |
| set 2026 | Folio prevendita |
