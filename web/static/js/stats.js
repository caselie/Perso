/** Écrans « statistiques joueurs » et « historique des parties ». */
import { $, el, remplir } from './dom.js';
import { api } from './api.js';

const NOMS_JEUX = {
  x01: '501 / 301',
  cricket: 'Cricket',
  atc: 'Around the Clock',
  shanghai: 'Shanghai',
  killer: 'Killer',
};

export async function rendreJoueurs(etat, actions) {
  $('#stats-titre').textContent = 'Statistiques';
  if (!etat.joueurs.length) {
    return remplir($('#stats-contenu'), el('p', { class: 'message' }, 'Aucun joueur enregistré.'));
  }
  const fiches = await Promise.all(etat.joueurs.map((joueur) => api.statsJoueur(joueur.id)));
  remplir(
    $('#stats-contenu'),
    el('div', { class: 'fiches' }, fiches.map((fiche) => carteJoueur(fiche, actions))),
  );
}

function carteJoueur(fiche, actions) {
  const r = fiche.records;
  const lignes = [
    ['Parties', fiche.matches],
    ['Victoires', `${fiche.wins} (${fiche.win_pct}%)`],
    ['Meilleure moyenne /3', r.average3 || '—'],
    ['Meilleur MPR', r.mpr || '—'],
    ['Meilleur finish', r.best_checkout || '—'],
    ['Meilleure manche', r.best_leg ? `${r.best_leg} fléchettes` : '—'],
    ['180', r.count_180],
  ];
  const parJeu = Object.entries(fiche.by_game).map(([slug, bloc]) =>
    el('li', {}, `${NOMS_JEUX[slug] || slug} : ${bloc.wins}/${bloc.matches}`),
  );

  return el(
    'div',
    { class: 'fiche' },
    el('h3', {}, fiche.name),
    el(
      'dl',
      {},
      lignes.flatMap(([titre, valeur]) => [el('dt', {}, titre), el('dd', {}, String(valeur))]),
    ),
    parJeu.length
      ? el('ul', { style: 'margin-top:.6rem;font-size:.8rem;color:var(--texte-doux);list-style:none' }, parJeu)
      : null,
  );
}

export async function rendreHistorique() {
  $('#stats-titre').textContent = 'Historique';
  const parties = await api.parties(40);
  if (!parties.length) {
    return remplir($('#stats-contenu'), el('p', { class: 'message' }, 'Aucune partie terminée.'));
  }
  remplir(
    $('#stats-contenu'),
    el(
      'div',
      { class: 'table-stats' },
      el(
        'table',
        {},
        el('thead', {}, el('tr', {}, ['Date', 'Jeu', 'Joueurs', 'Vainqueur'].map((t) => el('th', {}, t)))),
        el(
          'tbody',
          {},
          parties.map((partie) =>
            el(
              'tr',
              {},
              el('td', {}, dateCourte(partie.finished_at)),
              el('td', {}, NOMS_JEUX[partie.game] || partie.game),
              el('td', {}, partie.players.join(', ')),
              el('td', {}, partie.winner || '—'),
            ),
          ),
        ),
      ),
    ),
  );
}

function dateCourte(iso) {
  const date = new Date(iso);
  return Number.isNaN(date.getTime())
    ? iso
    : date.toLocaleString('fr-FR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
}
