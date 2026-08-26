/** Point d'entrée : état de l'application, actions et navigation. */
import { $, alerter } from './dom.js';
import { api } from './api.js';
import { rendreAccueil } from './accueil.js';
import { cacherPassage, construirePave, reinitialiserPartie, rendrePartie } from './partie.js';
import { rendreHistorique, rendreJoueurs } from './stats.js';

const etat = {
  ecran: 'accueil',
  jeux: [],
  joueurs: [],
  jeuChoisi: null,
  options: {},
  selection: [],
  match: null,
  mult: 1,
};

// ────────────────────────────────── rendu ───────────────────────────────

const ECRANS = { accueil: '#ecran-accueil', partie: '#ecran-partie', stats: '#ecran-stats' };

function rendre() {
  for (const [nom, selecteur] of Object.entries(ECRANS)) {
    $(selecteur).hidden = nom !== etat.ecran;
  }
  if (etat.ecran === 'accueil') rendreAccueil(etat, actions);
  if (etat.ecran === 'partie') rendrePartie(etat, actions);
}

/**
 * Applique un état reçu du serveur, sauf s'il est plus ancien que l'affichage.
 * Deux écrans peuvent piloter la même partie (la borne et un téléphone) : les
 * réponses arrivent alors dans le désordre, la révision tranche.
 */
function appliquer(partie) {
  if (partie && etat.match && partie.revision < etat.match.revision) return false;
  etat.match = partie;
  return true;
}

/** Enrobe une action asynchrone : une erreur serveur devient un message. */
function proteger(fn) {
  return async (...args) => {
    try {
      await fn(...args);
    } catch (erreur) {
      alerter(erreur.message);
    }
  };
}

// ───────────────────────────────── actions ──────────────────────────────

const actions = {
  choisirJeu(slug) {
    etat.jeuChoisi = slug;
    const jeu = etat.jeux.find((j) => j.slug === slug);
    etat.options = Object.fromEntries(jeu.options.map((spec) => [spec.key, spec.default]));
    rendre();
  },

  definirOption(cle, valeur) {
    etat.options[cle] = valeur;
    rendre();
  },

  basculerJoueur(joueur) {
    const index = etat.selection.findIndex((choisi) => choisi.id === joueur.id);
    if (index >= 0) etat.selection.splice(index, 1);
    else etat.selection.push({ id: joueur.id, name: joueur.name });
    rendre();
  },

  retirerJoueur(index) {
    etat.selection.splice(index, 1);
    rendre();
  },

  deplacerJoueur(index, delta) {
    const cible = index + delta;
    if (cible < 0 || cible >= etat.selection.length) return;
    const [joueur] = etat.selection.splice(index, 1);
    etat.selection.splice(cible, 0, joueur);
    rendre();
  },

  ajouterInvite: proteger(async (nom) => {
    const joueur = await api.ajouterJoueur(nom);
    etat.joueurs = await api.joueurs();
    if (!etat.selection.some((choisi) => choisi.id === joueur.id)) etat.selection.push(joueur);
    rendre();
  }),

  supprimerJoueur: proteger(async (joueur) => {
    if (!confirm(`Supprimer ${joueur.name} et ses statistiques ?`)) return;
    await api.supprimerJoueur(joueur.id);
    etat.joueurs = await api.joueurs();
    etat.selection = etat.selection.filter((choisi) => choisi.id !== joueur.id);
    rendre();
  }),

  demarrer: proteger(async () => {
    etat.match = null;
    appliquer(await api.demarrer(etat.jeuChoisi, etat.selection, etat.options));
    etat.mult = 1;
    reinitialiserPartie();
    etat.ecran = 'partie';
    $('#voile-fin').hidden = true;
    cacherPassage();
    rendre();
    garderEcranAllume();
    suivreLaPartie();
  }),

  choisirMultiplicateur(mult) {
    etat.mult = etat.mult === mult ? 1 : mult;
    rendre();
  },

  lancer: proteger(async (secteur) => {
    const mult = secteur === 0 ? 1 : etat.mult;
    if (secteur === 25 && mult === 3) return;
    appliquer(await api.lancer(mult, secteur));
    etat.mult = 1; // le multiplicateur ne vaut que pour une fléchette
    rendre();
  }),

  annuler: proteger(async () => {
    appliquer(await api.annuler());
    cacherPassage();
    rendre();
  }),

  abandonner: proteger(async () => {
    if (!confirm('Abandonner la partie en cours ?')) return;
    await api.abandonner();
    await retourAccueil();
  }),

  revanche: proteger(async () => {
    $('#voile-fin').hidden = true;
    await actions.demarrer();
  }),

  afficher: proteger(async (onglet) => {
    if (onglet === 'accueil') return retourAccueil();
    etat.ecran = 'stats';
    rendre();
    if (onglet === 'joueurs') await rendreJoueurs(etat, actions);
    else await rendreHistorique();
  }),
};

async function retourAccueil() {
  clearInterval(synchronisation);
  etat.match = null;
  etat.ecran = 'accueil';
  etat.joueurs = await api.joueurs();
  $('#voile-fin').hidden = true;
  cacherPassage();
  rendre();
}

// ──────────────────────────── confort de borne ──────────────────────────

let synchronisation;

/**
 * Interroge le serveur pendant une partie pour refléter les fléchettes
 * saisies depuis un autre écran. Repos quand l'onglet est masqué.
 */
function suivreLaPartie() {
  clearInterval(synchronisation);
  synchronisation = setInterval(async () => {
    if (etat.ecran !== 'partie' || document.hidden) return;
    try {
      const partie = await api.partie();
      if (etat.ecran !== 'partie') return; // la partie a été quittée entre-temps
      if (!partie) return retourAccueil();
      if (partie.revision !== etat.match?.revision && appliquer(partie)) rendre();
    } catch {
      /* borne momentanément injoignable : la prochaine passe réessaiera */
    }
  }, 1500);
}

/** Empêche la mise en veille pendant une partie (ignoré si non supporté). */
async function garderEcranAllume() {
  try {
    await navigator.wakeLock?.request('screen');
  } catch {
    /* verrou refusé : sans conséquence */
  }
}

/**
 * Saisie au clavier, pratique avec le pavé numérique d'un portable :
 * les chiffres s'enchaînent (« 2 » puis « 0 » = 20) et partent après une
 * courte pause, s/d/t changent le multiplicateur.
 */
function brancherClavier() {
  let tampon = '';
  let minuteur;

  const envoyer = () => {
    const secteur = Number(tampon);
    tampon = '';
    if (secteur >= 1 && secteur <= 20) actions.lancer(secteur);
  };

  document.addEventListener('keydown', (evt) => {
    if (evt.target.tagName === 'INPUT' || etat.ecran !== 'partie') return;
    const voileOuvert = !$('#voile-tour').hidden;

    if (voileOuvert) {
      if (evt.key === ' ' || evt.key === 'Enter') cacherPassage();
      if (evt.key === 'Backspace') actions.annuler();
      return;
    }
    if (/^[0-9]$/.test(evt.key)) {
      tampon = (tampon + evt.key).slice(-2);
      clearTimeout(minuteur);
      minuteur = setTimeout(envoyer, Number(tampon) > 2 ? 120 : 450);
      return;
    }
    const raccourcis = {
      s: () => actions.choisirMultiplicateur(1),
      d: () => actions.choisirMultiplicateur(2),
      t: () => actions.choisirMultiplicateur(3),
      b: () => actions.lancer(25),
      m: () => actions.lancer(0),
      Backspace: () => actions.annuler(),
    };
    const action = raccourcis[evt.key];
    if (action) {
      evt.preventDefault();
      action();
    }
  });
}

function brancherInterface() {
  construirePave(actions);

  for (const bouton of document.querySelectorAll('[data-onglet]')) {
    bouton.addEventListener('click', () => actions.afficher(bouton.dataset.onglet));
  }
  $('#form-invite').addEventListener('submit', (evt) => {
    evt.preventDefault();
    const champ = $('#champ-invite');
    if (champ.value.trim()) actions.ajouterInvite(champ.value);
    champ.value = '';
  });
  $('#btn-demarrer').addEventListener('click', () => actions.demarrer());
  $('#btn-annuler').addEventListener('click', () => actions.annuler());
  $('#btn-manque').addEventListener('click', () => actions.lancer(0));
  $('#btn-quitter').addEventListener('click', () => actions.abandonner());

  $('#voile-tour').addEventListener('click', cacherPassage);
  $('#voile-annuler').addEventListener('click', (evt) => {
    evt.stopPropagation();
    actions.annuler();
  });
  $('#fin-revanche').addEventListener('click', () => actions.revanche());
  $('#fin-nouveau').addEventListener('click', () => retourAccueil());

  brancherClavier();
}

// ─────────────────────────────── démarrage ──────────────────────────────

(async function demarrage() {
  brancherInterface();
  try {
    const donnees = await api.bootstrap();
    etat.jeux = donnees.games;
    etat.joueurs = donnees.players;
    if (etat.jeux.length) actions.choisirJeu(etat.jeux[0].slug);

    if (donnees.match) {
      // partie interrompue (coupure, redémarrage) : on reprend où on en était
      etat.match = donnees.match;
      etat.selection = donnees.match.seats;
      etat.jeuChoisi = donnees.match.game;
      etat.options = donnees.match.options;
      etat.ecran = 'partie';
      garderEcranAllume();
      suivreLaPartie();
    }
    rendre();
  } catch (erreur) {
    alerter(`Serveur injoignable : ${erreur.message}`);
  }
})();
