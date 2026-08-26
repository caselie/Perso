/** Écran de jeu : tableau des scores, pavé de saisie, passages de main. */
import { $, el, remplir } from './dom.js';

const NUMEROS = Array.from({ length: 20 }, (_, i) => i + 1);
/** Notation de bar : une barre, une croix, une croix cerclée. */
const SYMBOLES_MARQUES = ['·', '/', '✕', '⊗'];
let precedent = null;

export function reinitialiserPartie() {
  precedent = null;
}

/** Construit le pavé une seule fois ; le rendu ne fait ensuite que l'habiller. */
export function construirePave(actions) {
  const touches = NUMEROS.map((n) =>
    el('button', { class: 'touche', type: 'button', dataset: { secteur: n } }, String(n)),
  );
  touches.push(
    el(
      'button',
      {
        class: 'touche bull',
        type: 'button',
        dataset: { secteur: 25 },
        style: 'grid-column: span 4',
      },
      'BULL',
    ),
  );
  remplir($('#pave'), touches);

  $('#pave').addEventListener('click', (evt) => {
    const touche = evt.target.closest('.touche');
    if (!touche || touche.classList.contains('eteinte')) return;
    actions.lancer(Number(touche.dataset.secteur));
  });

  for (const bouton of document.querySelectorAll('.mult')) {
    bouton.addEventListener('click', () => actions.choisirMultiplicateur(Number(bouton.dataset.mult)));
  }
}

export function rendrePartie(etat, actions) {
  const partie = etat.match;
  if (!partie) return;

  const avance = precedent !== null && partie.history_length > precedent.history_length;
  const changeDeMain = precedent !== null && partie.current !== precedent.current;

  rendreEntete(partie);
  rendreScores(partie);
  rendreVolee(partie);
  rendreMultiplicateurs(etat);
  rendrePave(etat, partie);

  $('#btn-annuler').disabled = partie.history_length === 0 || partie.saved;

  if (partie.finished) {
    $('#voile-tour').hidden = true;
    montrerFin(partie);
  } else if (avance && changeDeMain) {
    $('#voile-fin').hidden = true;
    montrerPassage(partie);
  }
  precedent = partie;
}

// ─────────────────────────────────── tableau ────────────────────────────

function rendreEntete(partie) {
  $('#titre-jeu').textContent = partie.label;
  $('#info-tour').textContent = `Tour ${partie.round}`;
}

function rendreScores(partie) {
  remplir(
    $('#scores'),
    partie.scoreboard.map((ligne) =>
      el(
        'li',
        {
          class: `score-ligne${ligne.active ? ' actif' : ''}${ligne.eliminated ? ' hors-jeu' : ''}`,
        },
        el('span', { class: 'nom' }, ligne.name),
        el('span', { class: 'valeur' }, String(ligne.score)),
        detailLigne(partie.game, ligne),
      ),
    ),
  );
}

function detailLigne(jeu, ligne) {
  if (jeu === 'cricket') {
    return el(
      'span',
      { class: 'marques' },
      ligne.marks.map(({ target, marks, dead }) =>
        el(
          'span',
          { class: `marque${dead ? ' morte' : ''}`, dataset: { m: marks } },
          `${target === 25 ? 'B' : target} ${SYMBOLES_MARQUES[marks]}`,
        ),
      ),
    );
  }

  const morceaux = [];
  if (jeu === 'x01') {
    if (ligne.legs) morceaux.push(`${ligne.legs} manche(s)`);
    if (!ligne.opened) morceaux.push('entrée au double');
    morceaux.push(`moy. ${ligne.stats.average3}`);
    if (ligne.checkout) {
      return el(
        'span',
        { class: 'sous' },
        morceaux.join(' · '),
        el('span', { class: 'finish' }, ligne.checkout),
      );
    }
  } else if (jeu === 'killer') {
    morceaux.push(`n°${ligne.number}`);
    morceaux.push('♥'.repeat(ligne.lives) || 'aucune vie');
    if (ligne.killer) morceaux.push('KILLER');
  } else if (jeu === 'atc') {
    morceaux.push(`${ligne.score}/${ligne.total}`, ligne.detail);
  } else {
    morceaux.push(`moy. ${ligne.stats.average3}`);
  }
  return el('span', { class: 'sous' }, morceaux.join(' · '));
}

// ──────────────────────────────────── saisie ────────────────────────────

function rendreVolee(partie) {
  $('#consigne').textContent = partie.prompt;
  const creneaux = [0, 1, 2].map((i) => {
    const dart = partie.turn_throws[i];
    return el('li', { class: `creneau${dart ? ' rempli' : ''}` }, dart ? dart.label : '·');
  });
  remplir($('#flechettes'), creneaux);
  $('#total-volee').textContent = String(
    partie.turn_throws.reduce((somme, dart) => somme + dart.value, 0),
  );
}

function rendreMultiplicateurs(etat) {
  for (const bouton of document.querySelectorAll('.mult')) {
    bouton.setAttribute('aria-pressed', String(Number(bouton.dataset.mult) === etat.mult));
  }
}

function rendrePave(etat, partie) {
  const cibles = new Set(partie.highlights || []);
  for (const touche of document.querySelectorAll('.touche')) {
    const secteur = Number(touche.dataset.secteur);
    touche.classList.toggle('cible', cibles.has(secteur));
    if (secteur === 25) {
      // le bull n'a pas de triple
      touche.classList.toggle('eteinte', etat.mult === 3);
      touche.textContent = etat.mult === 2 ? '50' : etat.mult === 3 ? 'BULL ✕' : 'BULL 25';
    }
  }
}

// ──────────────────────────────────── voiles ────────────────────────────

function montrerPassage(partie) {
  const tour = partie.last_turn;
  const voile = $('#voile-tour');
  if (!tour) return;

  $('#voile-resume').replaceChildren(
    document.createTextNode(`${tour.name} — ${tour.points} point(s) `),
    tour.note ? el('span', { class: 'note' }, tour.note) : document.createTextNode(''),
  );
  remplir(
    $('#voile-flechettes'),
    tour.throws.map((dart) => el('li', { class: 'creneau rempli' }, dart.label)),
  );
  $('#voile-joueur').textContent = partie.players[partie.current];
  voile.hidden = false;
}

export function cacherPassage() {
  $('#voile-tour').hidden = true;
}

function montrerFin(partie) {
  $('#fin-titre').textContent =
    partie.winner !== null ? `🎯 ${partie.players[partie.winner]} l'emporte !` : 'Partie terminée';
  remplir($('#fin-stats'), tableauStats(partie));
  $('#voile-fin').hidden = false;
}

const COLONNES = {
  x01: [
    ['Moyenne /3', (l) => l.stats.average3],
    ['Fléchettes', (l) => l.stats.darts],
    ['Manches', (l) => l.legs],
    ['Meilleure manche', (l) => l.stats.best_leg ?? '—'],
    ['100+', (l) => l.stats.tons],
    ['180', (l) => l.stats.count_180],
    ['Meilleur finish', (l) => l.stats.best_checkout || '—'],
    ['% finish', (l) => `${l.stats.checkout_pct}%`],
  ],
  cricket: [
    ['Points', (l) => l.score],
    ['Marques', (l) => l.stats.marks],
    ['MPR', (l) => l.stats.mpr],
    ['Fléchettes', (l) => l.stats.darts],
  ],
  atc: [
    ['Progression', (l) => `${l.score}/${l.total}`],
    ['Touches', (l) => l.stats.hits],
    ['% réussite', (l) => `${l.stats.hit_pct}%`],
    ['Fléchettes', (l) => l.stats.darts],
  ],
  shanghai: [
    ['Points', (l) => l.score],
    ['Moyenne /3', (l) => l.stats.average3],
    ['Fléchettes', (l) => l.stats.darts],
  ],
  killer: [
    ['Numéro', (l) => l.number],
    ['Vies', (l) => l.lives],
    ['Vies retirées', (l) => l.stats.kills],
    ['Fléchettes', (l) => l.stats.darts],
  ],
};

function tableauStats(partie) {
  const colonnes = COLONNES[partie.game] || COLONNES.shanghai;
  return el(
    'table',
    {},
    el(
      'thead',
      {},
      el('tr', {}, el('th', {}, 'Joueur'), colonnes.map(([titre]) => el('th', {}, titre))),
    ),
    el(
      'tbody',
      {},
      partie.scoreboard.map((ligne) =>
        el(
          'tr',
          { class: ligne.index === partie.winner ? 'gagnant' : '' },
          el('td', {}, ligne.name),
          colonnes.map(([, lire]) => el('td', {}, String(lire(ligne) ?? '—'))),
        ),
      ),
    ),
  );
}
