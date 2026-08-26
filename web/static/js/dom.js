/** Fabrique d'éléments — juste ce qu'il faut pour éviter le HTML en chaînes. */
export function el(tag, props = {}, ...enfants) {
  const noeud = document.createElement(tag);
  for (const [cle, valeur] of Object.entries(props)) {
    if (valeur === null || valeur === undefined || valeur === false) continue;
    if (cle === 'class') noeud.className = valeur;
    else if (cle === 'dataset') Object.assign(noeud.dataset, valeur);
    else if (cle.startsWith('on')) noeud.addEventListener(cle.slice(2), valeur);
    else if (cle in noeud && cle !== 'list') noeud[cle] = valeur;
    else noeud.setAttribute(cle, valeur);
  }
  for (const enfant of enfants.flat()) {
    if (enfant === null || enfant === undefined || enfant === false) continue;
    noeud.append(enfant.nodeType ? enfant : document.createTextNode(String(enfant)));
  }
  return noeud;
}

export const $ = (selecteur, racine = document) => racine.querySelector(selecteur);

/** Remplace le contenu d'un conteneur. */
export function remplir(conteneur, ...enfants) {
  conteneur.replaceChildren(...enfants.flat().filter(Boolean));
  return conteneur;
}

let minuteurAlerte;
export function alerter(message) {
  const boite = $('#alerte');
  boite.textContent = message;
  boite.hidden = false;
  clearTimeout(minuteurAlerte);
  minuteurAlerte = setTimeout(() => (boite.hidden = true), 3500);
}
