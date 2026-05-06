// Recipees — App glue
// Un componente <App> per dispositivo (mobile / desktop) che gestisce
// stato di navigazione e renderizza la schermata corrente.
//
// NB: Babel-standalone non risolve i bare identifier dal global scope —
// li leggiamo da window per sicurezza.

const { MobileHome, MobileDetail, MobileSearch, MobileCook, MobileShopping, MobileProfile,
        DesktopHome, DesktopDetail, DesktopSearch, DesktopCook, DesktopShopping, DesktopProfile,
        useApp } = window;

function MobileApp({ initialScreen = 'home', initialRecipeId = null }) {
  const { state, go, navigate } = useApp({
    screen: initialScreen, recipeId: initialRecipeId, contextIds: [], activeCats: [],
  });
  // Torna alla home ripristinando i filtri attivi
  const back = () => navigate({ screen: 'home', activeCats: state.activeCats || [] });
  const recipe = (state.recipeId && window.RECIPES.find((r) => r.id === state.recipeId)) || window.RECIPES[0] || {};
  if (!recipe || !recipe.id) return null;

  const contextIds = state.contextIds || [];

  switch (state.screen) {
    case 'detail':
      return <MobileDetail recipe={recipe} go={go} back={back} contextIds={contextIds} />;
    case 'search':
      return <MobileSearch go={go} back={back} />;
    case 'cook':
      return <MobileCook recipe={recipe}
        back={() => navigate({ screen: 'detail', recipeId: recipe.id, contextIds })} />;
    case 'shopping':
      return <MobileShopping go={go} />;
    case 'profile':
      return <MobileProfile go={go} />;
    default:
      return <MobileHome go={go} initialCats={state.activeCats || []} />;
  }
}

function DesktopApp({ initialScreen = 'home', initialRecipeId = null }) {
  const { state, go, navigate } = useApp({
    screen: initialScreen, recipeId: initialRecipeId, contextIds: [], activeCats: [],
  });
  // Torna alla home ripristinando i filtri attivi
  const back = () => navigate({ screen: 'home', activeCats: state.activeCats || [] });
  const recipe = (state.recipeId && window.RECIPES.find((r) => r.id === state.recipeId)) || window.RECIPES[0] || {};
  if (!recipe || !recipe.id) return null;

  const contextIds = state.contextIds || [];

  switch (state.screen) {
    case 'detail':
      return <DesktopDetail recipe={recipe} go={go} back={back} contextIds={contextIds} />;
    case 'search':
      return <DesktopSearch go={go} back={back} />;
    case 'cook':
      return <DesktopCook recipe={recipe}
        back={() => navigate({ screen: 'detail', recipeId: recipe.id, contextIds })} />;
    case 'shopping':
      return <DesktopShopping go={go} />;
    case 'profile':
      return <DesktopProfile go={go} />;
    default:
      return <DesktopHome go={go} initialCats={state.activeCats || []} />;
  }
}

window.MobileApp = MobileApp;
window.DesktopApp = DesktopApp;
