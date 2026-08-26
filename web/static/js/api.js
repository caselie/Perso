/** Accès à l'API de la borne. Toute erreur serveur remonte en Error lisible. */
async function appeler(methode, url, corps) {
  const reponse = await fetch(url, {
    method: methode,
    headers: corps ? { 'Content-Type': 'application/json' } : {},
    body: corps ? JSON.stringify(corps) : undefined,
  });
  if (reponse.status === 204) return null;
  const donnees = await reponse.json().catch(() => null);
  if (!reponse.ok) {
    throw new Error((donnees && donnees.error) || `Erreur ${reponse.status}`);
  }
  return donnees;
}

export const api = {
  bootstrap: () => appeler('GET', '/api/bootstrap'),
  joueurs: () => appeler('GET', '/api/players'),
  ajouterJoueur: (name) => appeler('POST', '/api/players', { name }),
  supprimerJoueur: (id) => appeler('DELETE', `/api/players/${id}`),
  statsJoueur: (id) => appeler('GET', `/api/players/${id}/stats`),
  parties: (limit = 20) => appeler('GET', `/api/matches?limit=${limit}`),
  demarrer: (game, players, options) => appeler('POST', '/api/match', { game, players, options }),
  partie: () => appeler('GET', '/api/match'),
  abandonner: () => appeler('DELETE', '/api/match'),
  lancer: (multiplier, sector) => appeler('POST', '/api/match/throw', { multiplier, sector }),
  annuler: () => appeler('POST', '/api/match/undo'),
};
