// Géométrie d'une cible réglementaire (cotes en mm), projetée sur un rayon
// de 530 unités SVG pour la couronne extérieure des numéros.
export const ORDRE = [
  20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5,
];
export const VIEWBOX = "-540 -540 1080 1080";
const K = 530 / 225;

export type Zone = "S" | "D" | "T";

const angleSecteur = (secteur: number) => -90 + ORDRE.indexOf(secteur) * 18;

export const polaire = (rayonMm: number, degres: number): [number, number] => {
  const a = (degres * Math.PI) / 180;
  return [Math.cos(a) * rayonMm * K, Math.sin(a) * rayonMm * K];
};

export const rayon = (rayonMm: number) => rayonMm * K;

export const quartier = (r1: number, r2: number, a1: number, a2: number) => {
  const [x1, y1] = polaire(r2, a1);
  const [x2, y2] = polaire(r2, a2);
  const [x3, y3] = polaire(r1, a2);
  const [x4, y4] = polaire(r1, a1);
  return `M${x1} ${y1}A${rayon(r2)} ${rayon(r2)} 0 0 1 ${x2} ${y2}L${x3} ${y3}A${rayon(r1)} ${rayon(r1)} 0 0 0 ${x4} ${y4}Z`;
};

export const ANNEAUX: { zone: Zone; r1: number; r2: number }[] = [
  { zone: "S", r1: 15.9, r2: 99 },
  { zone: "T", r1: 99, r2: 107 },
  { zone: "S", r1: 107, r2: 162 },
  { zone: "D", r1: 162, r2: 170 },
];

export const bornesSecteur = (secteur: number): [number, number] => {
  const a = angleSecteur(secteur);
  return [a - 9, a + 9];
};

const RAYON_IMPACT: Record<Zone, number> = { S: 135, D: 166, T: 103 };

// Point d'impact au centre de la zone visée, en coordonnées SVG.
export const pointImpact = (cible: string): [number, number] => {
  const zone = cible[0] as Zone;
  const secteur = Number(cible.slice(1));
  return polaire(RAYON_IMPACT[zone], angleSecteur(secteur));
};
