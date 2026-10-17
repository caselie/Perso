"""Découpe la photo en calques pour la parallaxe.

premier-plan.png : le couple détouré (RGBA, bord adouci)
fond.png         : la scène sans le couple, trou rebouché par inpainting
ciel.png         : masque du ciel (pour l'éclairage et la brume)
"""
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import new_session, remove

d = sys.argv[1]
src = Image.open(f"{d}/source.jpg").convert("RGB")
rgb = np.array(src)

masque = np.array(remove(src, session=new_session("u2net_human_seg"), only_mask=True, post_process_mask=True))
print("premier plan :", round((masque > 128).mean() * 100, 1), "%")

# Premier plan : alpha légèrement adouci pour éviter un détourage « collé ».
alpha = cv2.GaussianBlur(masque, (0, 0), 1.6)
Image.fromarray(np.dstack([rgb, alpha])).save(f"{d}/premier-plan.png")

# Fond : on retire le couple (masque dilaté) puis on rebouche. L'inpainting se
# fait en basse résolution (rapide, et seules les lisières seront visibles).
trou = cv2.dilate((masque > 40).astype(np.uint8) * 255, np.ones((41, 41), np.uint8))
petit = 0.25
r_small = cv2.resize(rgb, None, fx=petit, fy=petit, interpolation=cv2.INTER_AREA)
t_small = cv2.resize(trou, (r_small.shape[1], r_small.shape[0]), interpolation=cv2.INTER_NEAREST)
rebouche = cv2.inpaint(cv2.cvtColor(r_small, cv2.COLOR_RGB2BGR), t_small, 12, cv2.INPAINT_TELEA)
rebouche = cv2.cvtColor(cv2.resize(rebouche, (rgb.shape[1], rgb.shape[0]), interpolation=cv2.INTER_CUBIC), cv2.COLOR_BGR2RGB)
rebouche = cv2.GaussianBlur(rebouche, (0, 0), 3)
# Hors du sujet, le décor garde ses pixels d'origine : aucun halo quand les
# calques sont alignés, la reconstruction n'apparaît qu'en lisière.
poids = (cv2.GaussianBlur(cv2.dilate(masque, np.ones((7, 7), np.uint8)), (0, 0), 2) / 255.0)[..., None]
fond = (rgb * (1 - poids) + rebouche * poids).astype(np.uint8)
Image.fromarray(fond).save(f"{d}/fond.png")

# Ciel : bleu dominant dans la moitié haute.
hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
ciel = ((hsv[..., 0] > 95) & (hsv[..., 0] < 125) & (hsv[..., 1] > 60)).astype(np.uint8) * 255
ciel[rgb.shape[0] // 2 :] = 0
ciel = cv2.GaussianBlur(ciel, (0, 0), 4)
Image.fromarray(ciel).save(f"{d}/ciel.png")
print("ok")
