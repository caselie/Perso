# Monter la borne

Comment transformer un vieux portable en borne de fléchettes, du mur au
démarrage automatique.

## 1. La cible et les cotes

Les mesures officielles, valables quelle que soit la borne :

| Repère | Pointes acier | Pointes plastique (soft-tip) |
| --- | --- | --- |
| Hauteur du centre du bull | **1,73 m** | **1,73 m** |
| Distance de jet (face de la cible → ligne) | **2,37 m** | **2,44 m** |
| Diagonale bull → ligne de jet | 2,93 m | 2,99 m |

La diagonale est le contrôle qui compte : tendez un mètre du centre du bull
jusqu'à la ligne, c'est elle qui rattrape un mur qui n'est pas d'aplomb ou un
sol en pente.

Trois détails qui changent tout à l'usage :

* **un panneau de protection** (liège, tapis fin, vieux plateau) de 60 cm autour
  de la cible : les fléchettes qui ricochent abîment le plâtre en une soirée ;
* **un éclairage venant du dessus et de l'avant**, pour ne pas projeter l'ombre
  du joueur sur la cible ;
* **un repère au sol** collé sur la ligne de jet (gaffer, baguette plate).

## 2. Le portable

### Quelle machine

Presque n'importe laquelle : le serveur est un petit Flask et l'interface est
du HTML sans dépendance. Le poste le plus gourmand, c'est le navigateur.
Comptez 2 Go de mémoire pour être tranquille.

Si le portable a un écran fatigué, branchez-le sur un téléviseur en HDMI et
refermez-le : voir plus bas comment garder la machine allumée capot fermé.

### Un système léger

Sur une machine ancienne, repartez d'une base minimale plutôt que de garder un
Windows d'origine :

```bash
# Debian « standard system utilities » seulement, puis :
sudo apt install --no-install-recommends \
     xserver-xorg xinit openbox chromium python3-venv unclutter
```

`openbox` suffit largement : pas de bureau, pas de barre des tâches, le
navigateur occupe tout l'écran.

### Installer la borne

```bash
sudo adduser borne
sudo -u borne git clone <ce dépôt> /home/borne/raspydarts
sudo -u borne /home/borne/raspydarts/scripts/run.sh --serveur   # crée le venv
```

### Démarrage automatique

Le serveur d'abord, en service système :

```bash
sudo cp /home/borne/raspydarts/scripts/raspydarts.service /etc/systemd/system/
sudo systemctl enable --now raspydarts
```

Puis l'affichage. Connexion automatique de l'utilisateur `borne` :

```bash
sudo mkdir -p /etc/systemd/system/getty@tty1.service.d
sudo tee /etc/systemd/system/getty@tty1.service.d/autologin.conf <<'EOF'
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin borne --noclear %I $TERM
EOF
```

Et le lancement de X à la connexion, dans `/home/borne/.bash_profile` :

```bash
[ "$(tty)" = "/dev/tty1" ] && exec startx
```

Enfin `/home/borne/.xinitrc` :

```bash
#!/bin/sh
xset s off -dpms          # pas d'économiseur, pas d'extinction d'écran
unclutter -idle 2 &       # curseur masqué après 2 secondes
openbox-session &
exec chromium --kiosk --noerrdialogs --disable-infobars \
     --disable-session-crashed-bubble --overscroll-history-navigation=0 \
     http://127.0.0.1:8080
```

### Garder l'écran allumé

Trois verrous, du plus proche du matériel au plus proche du navigateur :

```bash
# 1. le système ne se met pas en veille, même capot fermé
sudo sed -i 's/^#*HandleLidSwitch=.*/HandleLidSwitch=ignore/' /etc/systemd/logind.conf
sudo systemctl restart systemd-logind

# 2. X n'éteint pas l'écran     → xset s off -dpms (déjà dans .xinitrc)
# 3. la page demande un verrou d'écran pendant les parties (automatique)
```

## 3. Saisir les scores sans écran tactile

C'est la vraie question sur un portable. Par ordre de confort :

1. **Un pavé numérique sans fil** accroché près de la cible. Les raccourcis
   (`2` `0` pour le 20, `t` pour triple, `Retour arrière` pour annuler) rendent
   la saisie plus rapide qu'au doigt, pour une vingtaine d'euros.
2. **Un téléphone comme télécommande.** Ouvrez `http://<ip-du-pc>:8080` sur le
   wifi local : la même interface s'affiche, et les deux écrans restent
   synchronisés. Le portable devient un tableau d'affichage.
3. **Une souris sans fil** posée sur une tablette près de la ligne de jet.
4. **Un vrai écran tactile** : moniteur USB tactile d'occasion, ou surcouche
   tactile infrarouge à poser sur l'écran existant. C'est la solution la plus
   « borne de bar », et la plus chère.

Relevez l'adresse IP de la borne avec `hostname -I`. Si le réseau est instable,
fixez-la dans votre box par réservation DHCP.

## 4. Mise en place dans la pièce

* Placez l'écran **à côté** de la cible, pas dans l'axe : à hauteur d'yeux,
  décalé d'un mètre, hors de la trajectoire des fléchettes qui ricochent.
* Passez les câbles au-dessus ou le long de la plinthe, jamais en travers de la
  zone de jet.
* Sur batterie fatiguée, laissez le chargeur branché en permanence : la borne
  encaisse une coupure sans rien perdre, mais autant l'éviter en pleine partie.

## 5. Entretien

La base tient tout dans un seul fichier :

```bash
cp /home/borne/raspydarts/data/raspydarts.sqlite3 /media/cle/sauvegarde.sqlite3
```

Mettre à jour la borne :

```bash
cd /home/borne/raspydarts && git pull
sudo systemctl restart raspydarts
```

Repartir de zéro (efface joueurs et historique) : arrêtez le service, supprimez
`data/raspydarts.sqlite3`, redémarrez.

## Et ensuite ?

La saisie manuelle est volontairement simple et marche avec toutes les cibles.
Si vous passez plus tard à une cible électronique soft-tip, la matrice de
segments peut être câblée sur un Arduino ou un Pico qui enverrait les mêmes
`{"multiplier": …, "sector": …}` sur `/api/match/throw` : le moteur de jeu et
l'interface n'auraient pas une ligne à changer.
