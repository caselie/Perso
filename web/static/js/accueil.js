/** Écran de configuration : choix du jeu, de ses options et des joueurs. */
import { $, el, remplir } from './dom.js';

export function rendreAccueil(etat, actions) {
  rendreJeux(etat, actions);
  rendreOptions(etat, actions);
  rendreSelection(etat, actions);
  rendrePastilles(etat, actions);
  rendrePied(etat);
}

function jeuCourant(etat) {
  return etat.jeux.find((jeu) => jeu.slug === etat.jeuChoisi) || null;
}

function rendreJeux(etat, actions) {
  remplir(
    $('#liste-jeux'),
    etat.jeux.map((jeu) =>
      el(
        'button',
        {
          class: 'carte-jeu',
          type: 'button',
          'aria-pressed': String(jeu.slug === etat.jeuChoisi),
          onclick: () => actions.choisirJeu(jeu.slug),
        },
        el('strong', {}, jeu.label),
        el('small', {}, jeu.description),
      ),
    ),
  );
}

function rendreOptions(etat, actions) {
  const jeu = jeuCourant(etat);
  const conteneur = $('#options-jeu');
  if (!jeu) return remplir(conteneur);

  const lignes = jeu.options
    .filter((spec) => !spec.hidden)
    .map((spec) => {
      const valeur = etat.options[spec.key];
      const definir = (v) => actions.definirOption(spec.key, v);
      let controle;

      if (spec.type === 'bool') {
        controle = el('button', {
          class: 'bascule',
          type: 'button',
          'aria-pressed': String(Boolean(valeur)),
          'aria-label': spec.label,
          onclick: () => definir(!valeur),
        });
      } else if (spec.type === 'choice') {
        controle = el(
          'div',
          { class: 'option-choix' },
          spec.choices.map((choix) =>
            el(
              'button',
              {
                type: 'button',
                'aria-pressed': String(choix === valeur),
                onclick: () => definir(choix),
              },
              (spec.labels && spec.labels[choix]) || String(choix),
            ),
          ),
        );
      } else if (spec.presets) {
        controle = el(
          'div',
          { class: 'option-choix' },
          spec.presets.map((choix) =>
            el(
              'button',
              {
                type: 'button',
                'aria-pressed': String(choix === valeur),
                onclick: () => definir(choix),
              },
              String(choix),
            ),
          ),
        );
      } else {
        controle = el('input', {
          type: 'number',
          value: valeur,
          min: spec.min,
          max: spec.max,
          onchange: (evt) => definir(Number(evt.target.value)),
        });
      }
      return el('label', { class: 'option' }, el('span', {}, spec.label), controle);
    });

  remplir(conteneur, lignes);
}

function rendreSelection(etat, actions) {
  const liste = $('#joueurs-selection');
  if (!etat.selection.length) {
    return remplir(liste, el('li', { class: 'vide' }, 'Aucun joueur sélectionné'));
  }
  remplir(
    liste,
    etat.selection.map((joueur, index) =>
      el(
        'li',
        {},
        el('span', { class: 'rang' }, `${index + 1}.`),
        el('span', { class: 'nom' }, joueur.name),
        el(
          'span',
          { class: 'fleches' },
          el(
            'button',
            {
              type: 'button',
              'aria-label': 'Monter',
              disabled: index === 0,
              onclick: () => actions.deplacerJoueur(index, -1),
            },
            '↑',
          ),
          el(
            'button',
            {
              type: 'button',
              'aria-label': 'Descendre',
              disabled: index === etat.selection.length - 1,
              onclick: () => actions.deplacerJoueur(index, 1),
            },
            '↓',
          ),
          el(
            'button',
            { type: 'button', 'aria-label': 'Retirer', onclick: () => actions.retirerJoueur(index) },
            '✕',
          ),
        ),
      ),
    ),
  );
}

function rendrePastilles(etat, actions) {
  const choisis = new Set(etat.selection.map((joueur) => joueur.id).filter(Boolean));
  remplir(
    $('#liste-joueurs'),
    etat.joueurs.map((joueur) =>
      el(
        'span',
        { class: 'pastille', 'aria-pressed': String(choisis.has(joueur.id)) },
        el(
          'button',
          {
            type: 'button',
            class: 'btn-fantome',
            style: 'background:none;border:none;padding:0',
            onclick: () => actions.basculerJoueur(joueur),
          },
          `${joueur.name}${joueur.matches ? ` · ${joueur.wins}/${joueur.matches}` : ''}`,
        ),
        el(
          'button',
          {
            class: 'sup',
            type: 'button',
            'aria-label': `Supprimer ${joueur.name}`,
            onclick: () => actions.supprimerJoueur(joueur),
          },
          '✕',
        ),
      ),
    ),
  );
}

function rendrePied(etat) {
  const jeu = jeuCourant(etat);
  const nombre = etat.selection.length;
  const message = $('#message-accueil');
  const bouton = $('#btn-demarrer');

  if (!jeu) {
    message.textContent = 'Choisissez un jeu.';
    bouton.disabled = true;
    return;
  }
  if (nombre < jeu.min_players) {
    message.textContent = `${jeu.label} : ${jeu.min_players} joueur(s) minimum.`;
    bouton.disabled = true;
    return;
  }
  if (nombre > jeu.max_players) {
    message.textContent = `${jeu.label} : ${jeu.max_players} joueurs au maximum.`;
    bouton.disabled = true;
    return;
  }
  message.textContent = `${jeu.label} — ${nombre} joueur(s)`;
  bouton.disabled = false;
}
