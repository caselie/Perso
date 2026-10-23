# Nichoir connecté (ESP32-CAM)

Un nichoir à mésanges avec une caméra infrarouge au plafond. Tu regardes le nid
en direct depuis un navigateur ou Home Assistant, sans jamais ouvrir la boîte
ni déranger les oiseaux.

```
        ┌──────────── toit (charnière) ────────────┐
        │  compartiment technique  ~6 cm           │  ESP32-CAM, LED IR,
        │  [ESP32-CAM]  (IR)  (IR)   ◄── câble     │  régulateur, aérations
        ├────────── plafond, trou Ø15 ─────────────┤
        │                ▼ caméra                  │
   Ø32  ○  ← trou d'envol (centre à 19 cm)         │  chambre du nid
        │                                          │  12 × 12 cm, 22 cm de haut
        │   [ nid ]              DS18B20 ●         │
        └──────────── plancher percé ──────────────┘
```

**Principe :** la chambre du nid reste totalement noire pour l'oiseau. La caméra
voit grâce à des LED infrarouges à 850 nm, que les mésanges ne perçoivent pas
(leur vision s'étend vers l'ultraviolet, pas vers l'infrarouge). Toute
l'électronique est dans un compartiment séparé, au-dessus du nid.

## Ce qu'il faut savoir avant d'acheter

- **La caméra fournie avec l'ESP32-CAM ne voit pas l'infrarouge.** Elle a un
  filtre anti-IR : dans le nichoir, tu n'aurais qu'une image noire. Achète un
  module **OV2640 « NoIR » / « 850 nm » / « night vision »**, si possible grand
  angle (120 à 160°). Il coûte 3 à 5 €.
- **Il faut refaire la mise au point.** L'objectif est réglé sur l'infini, alors
  que le nid est à 10-15 cm. Tourne l'objectif dans le sens antihoraire (le
  point de colle cède) en regardant le flux jusqu'à ce qu'un texte posé à 15 cm
  soit net.
- **Oublie la batterie.** En streaming, l'ESP32-CAM tire environ 1 W, soit
  ~25 Wh par jour, LED IR en plus. Il faudrait un panneau de 20 W et une grosse
  batterie pour tenir en hiver. Un câble est la solution fiable.
- **L'alimentation est la cause n°1 des pannes d'ESP32-CAM** (redémarrages en
  boucle, « brownout detector »). Ne transporte pas du 5 V sur 15 m de câble
  USB : transporte du 12 V ou du PoE, et abaisse à 5 V *dans* le nichoir.

## Matériel

| Pièce | Rôle | Prix indicatif |
| --- | --- | --- |
| ESP32-CAM AI-Thinker + carte de programmation ESP32-CAM-MB | cerveau + caméra + Wi-Fi | 10 € |
| Module OV2640 NoIR grand angle (connecteur 24 broches) | voir dans le noir | 5 € |
| Antenne Wi-Fi externe IPEX/U.FL | le bois atténue le signal | 3 € |
| 4 LED IR 850 nm, 5 mm | éclairage invisible | 2 € |
| 2 résistances 39 Ω, 1 résistance 1 kΩ, 1 résistance 4,7 kΩ | | 1 € |
| Transistor NPN BC337 (ou 2N2222) | commande des LED | 0,5 € |
| Sonde DS18B20 | température du nid | 2 € |
| Condensateur 1000 µF 10 V | amortit les pics de courant | 0,5 € |
| **Alim. au choix :** séparateur PoE 802.3af → 5 V micro-USB *ou* bloc 12 V + convertisseur buck 12 → 5 V (type MP1584) | | 8-12 € |
| Presse-étoupe PG7 | entrée du câble étanche | 1 € |
| Planche de bois brut non traité, 18 mm × 150 mm × 1,2 m (sapin, mélèze, douglas) | la boîte | 10 € |

Le PoE est l'option la plus élégante : un seul câble Ethernet extérieur, un
injecteur PoE côté maison, et tu peux couper le courant à distance si ton
switch le permet.

## Câblage

Les broches GPIO13 et GPIO14 sont celles de la carte SD : on n'utilise pas de
carte SD, elles sont donc libres. Ne touche pas à GPIO12 (broche de démarrage).

```
 5V ───────┬────────────────┬──────────────────────── 5V de l'ESP32-CAM
           │                │
        1000 µF        LED IR ►| LED IR ►| 39 Ω ──┐
           │           LED IR ►| LED IR ►| 39 Ω ──┤      (2 branches de 2 LED,
 GND ──────┴───────┐                              │       ~50 mA chacune)
                   │                         C ───┘
                   │      GPIO13 ── 1 kΩ ──  B   BC337
                   └──────────────────────── E
                                             (E à GND)

 DS18B20 :  rouge → 3,3 V    noir → GND    jaune → GPIO14
            + résistance 4,7 kΩ entre GPIO14 et 3,3 V
```

Oriente les LED vers les parois et non vers le fond : la lumière réfléchie est
plus homogène et l'image n'a pas de point aveuglant au centre.

**Antenne :** sur l'ESP32-CAM, une petite résistance de 0 Ω à côté du connecteur
IPEX choisit entre l'antenne gravée et l'antenne externe. Dessoude-la et
ressoude-la sur la position « IPEX », puis fais sortir l'antenne sous le
débord du toit.

## Plan de coupe (planche de 18 mm × 150 mm)

Cotes pour une mésange charbonnière (trou de 32 mm). Pour la mésange bleue,
perce **28 mm** : les moineaux et les charbonnières ne pourront plus entrer.

| Pièce | Qté | Dimensions | Remarques |
| --- | --- | --- | --- |
| Plancher | 1 | 120 × 120 mm | 4 trous Ø6 pour l'écoulement |
| Côtés | 2 | 120 × 300 mm | 2 tasseaux à 220 mm du bas pour le plafond |
| Façade | 1 | 156 × 300 mm | trou Ø32, centre à 190 mm du bas du plancher ; pivote sur 2 clous pour le nettoyage |
| Dos | 1 | 156 × 400 mm | dépasse de 10 cm pour fixer le nichoir |
| Plafond intermédiaire | 1 | 120 × 120 mm, contreplaqué 10 mm | trou Ø15 au centre pour l'objectif, 4 trous Ø5 pour les LED |
| Toit | 1 | 200 × 220 mm | débord de 4-5 cm devant, charnière à l'arrière, crochet de fermeture |

- **Aération du compartiment technique :** 3 trous Ø8 en haut de chaque côté,
  cachés sous le débord du toit. L'électronique chauffe un peu ; en été c'est
  le soleil sur le toit qui pose problème, pas l'ESP32.
- **Rainure sous le trou d'envol :** quelques traits de scie à l'intérieur de
  la façade aident les oisillons à grimper pour sortir.
- **Pas de perchoir** sous le trou : il sert surtout aux prédateurs.
- **Aucun traitement à l'intérieur.** À l'extérieur, une huile de lin suffit.
- Fais passer le câble de la sonde DS18B20 par un petit trou du plafond et
  colle la sonde dans un coin de la chambre, à 3-4 cm du plancher.

## Logiciel

La carte tourne sous [ESPHome](https://esphome.io). La configuration est dans
[`esphome/nichoir.yaml`](esphome/nichoir.yaml).

```bash
cd nichoir/esphome
cp secrets.yaml.example secrets.yaml      # Wi-Fi, clés
pip install esphome
esphome run nichoir.yaml                  # 1re fois en USB via l'ESP32-CAM-MB
```

Ensuite, les mises à jour passent par le Wi-Fi (`esphome run nichoir.yaml`
propose l'OTA) : tu n'auras plus jamais à démonter le toit.

Une fois l'appareil allumé :

- **Flux vidéo :** `http://nichoir.local:8080`, dans n'importe quel navigateur,
  même sans Home Assistant.
- **Photo instantanée :** `http://nichoir.local:8081`
- **Page de contrôle :** `http://nichoir.local` (intensité IR, températures,
  redémarrage).
- **Home Assistant :** l'appareil est détecté automatiquement. Tu obtiens une
  caméra, une lumière « Infrarouge », la température du nid et celle de
  l'électronique, ainsi que le signal Wi-Fi.

Si le Wi-Fi tombe, la carte ouvre un point d'accès « Nichoir secours » pour
reconfigurer le réseau.

### Timelapse de la saison

[`homeassistant/automations.yaml`](homeassistant/automations.yaml) prend une
photo toutes les 10 minutes dans `/media/nichoir/` et t'alerte si le nid dépasse
35 °C. À la fin de la saison, assemble le film :

```bash
cd /media/nichoir
ffmpeg -framerate 24 -pattern_type glob -i '*/*.jpg' \
       -c:v libx264 -pix_fmt yuv420p nichoir-2027.mp4
```

Du premier brin de mousse à l'envol, ça donne 3 à 4 minutes de film.

## Installation

- **Quand :** maintenant. On est fin octobre : les mésanges visitent les
  nichoirs dès l'hiver et s'en servent comme dortoir par grand froid. Le nid se
  construit entre mars et avril. Un nichoir posé après février a peu de chances
  d'être occupé la première année.
- **Où :** entre 2 et 4 m de haut, trou orienté vers l'est ou le sud-est (à
  l'abri des vents dominants et du soleil de l'après-midi), légèrement penché
  vers l'avant pour que la pluie n'entre pas. Hors de portée des chats.
- **Règle d'or :** n'ouvre jamais le nichoir pendant la nidification. C'est
  tout l'intérêt de la caméra. Nettoyage une seule fois par an, en
  octobre-novembre, en pivotant la façade.

## Pour aller plus loin

- **Journal du nid automatique.** Envoie une photo par jour à un modèle de
  vision (intégration *AI Task* de Home Assistant) avec la question « combien
  d'œufs ou d'oisillons vois-tu ? », et stocke la réponse dans un capteur. Tu
  obtiens la courbe ponte → éclosion → envol sans rien noter à la main.
- **Compteur de passages.** Une barrière IR (LED 940 nm + phototransistor) en
  travers du trou d'envol, branchée sur GPIO15, compte les allers-retours de
  nourrissage. Au pic, un couple de mésanges en fait plus de 500 par jour.
- **Micro.** Un module I²S INMP441 permet d'entendre les oisillons quémander,
  bien avant de les voir.
