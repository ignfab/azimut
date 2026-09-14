# Azimut

Fabrique un travelling vertical vers n'importe quel point de France, sur les fonds
de la Géoplateforme IGN, et l'exporte en vidéo. Pensé pour le montage d'un sujet TV.

Tout tient dans `index.html` : pas de build, pas de dépendance, pas de clé d'API.
Ouvrez le fichier dans un navigateur, ou servez-le en statique.

## Deux mouvements

**Un point** — descente verticale depuis un cadre large jusqu'au point visé.

**D'un point à l'autre** — on décolle du départ, on monte, on traverse, on
redescend sur l'arrivée. La trajectoire suit van Wijk et Nuij (2003), l'unique
chemin où la vitesse perçue reste constante : sans lui, la traversée au sommet
paraît glisser trop vite et la descente traîne.

La largeur au sommet vaut `w0·cosh(r0)`, relation qui s'inverse — « cadre de
départ » fixe donc directement l'altitude du survol, et le paramètre ρ s'en
déduit. Il est borné à 3, si bien qu'un trajet court ne part pas dans l'espace :
deux quartiers de Lyon culminent à 9 km de large, Nantes–Rennes à 452 km.

### Rythme d'un trajet

Le rythme « Départ et arrivée doux » atteint trois fois la vitesse moyenne à
mi-parcours — exactement là où se fait la traversée. Le mode trajet bascule donc
sur « Survol régulier », qui monte en vitesse sur les premiers 22 % du temps, la
maintient constante, puis redescend : pointe à 1,28 fois la moyenne seulement.

La largeur des rampes se règle par la constante `EASE_ENDS` en tête de script.

| `EASE_ENDS` | vitesse à mi-parcours |
|---|---|
| 0.10 | ×1,11 — traversée très posée, départ plus sec |
| 0.22 | ×1,28 — réglage livré |
| 0.40 | ×1,67 — départ moelleux, traversée plus vive |

Deux autres leviers calment le mouvement : allonger la durée, ou augmenter
« cadre de départ ». Monter plus haut réduit la distance parcourue en nombre
d'écrans, donc la vitesse perçue.

Un trajet coûte environ 1,6 à 1,8 fois les tuiles d'un zoom simple sur longue
distance, et moins qu'un zoom simple en deçà de quelques kilomètres.

## Utilisation

À l'ouverture, la carte de France s'affiche. Cliquez dessus pour viser un point :
Azimut interroge le géocodage inverse pour en retrouver le nom.

1. Choisissez le mouvement en haut du panneau.
2. Cliquez sur la carte, ou saisissez une adresse, un lieu-dit, ou `48.8584, 2.2945`.
   En mode trajet, le clic renseigne le point encadré, et passe à l'arrivée
   une fois le départ posé.
2. Réglez la durée, le cadre de départ et d'arrivée, le rythme.
3. **Lancer l'animation** précharge les tuiles puis joue le plan.
4. **Enregistrer la vidéo** rejoue le plan et télécharge un WebM.

## Export

| Qualité | Débit en 1080p25 | Usage |
|---|---|---|
| Standard | ~8 Mb/s | diffusion web, repérage |
| Haute | ~18 Mb/s | montage courant |
| Maximale | ~34 Mb/s | plan large ou très détaillé |
| Images PNG | sans perte | master de diffusion |

Le débit est calculé à partir du format et de la cadence : un zoom plein cadre
n'offre aucune zone statique à l'encodeur, il lui faut bien plus de bits par pixel
qu'une scène ordinaire.

La cadence par défaut est 25 i/s, celle de la diffusion française. Elle compte
double : à débit égal, 25 i/s laisse deux fois plus de bits par image que 50,
et laisse à l'encodeur VP9 deux fois plus de temps, celui-ci travaillant en
temps réel dans `MediaRecorder`.

Pour un master sans aucune perte, choisissez « Images PNG » : le rendu devient
déterministe, image par image, sans contrainte de temps réel. L'archive s'importe
comme suite d'images dans n'importe quel logiciel de montage, ou se convertit :

```
ffmpeg -framerate 25 -i %05d.png -c:v prores_ks -profile:v 3 plan.mov
```

Pour convertir un WebM :

```
ffmpeg -i azimut-mont-saint-michel.webm -c:v prores_ks -profile:v 3 plan.mov
```

## Données

Flux WMTS ouverts de la Géoplateforme, sans clé :

| Couche | Identifiant | Zoom max |
|---|---|---|
| Photographies aériennes | `ORTHOIMAGERY.ORTHOPHOTOS` | 20 |
| Plan IGN v2 | `GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2` | 19 |

Géocodage via `data.geopf.fr/geocodage`, avec repli sur la Base Adresse Nationale.

Toute image produite doit porter la mention « © IGN — Géoplateforme ». Elle est
incrustée automatiquement et n'est pas désactivable.

## Fonctionnement

Le rendu est un pipeline WebGL de tuiles Web Mercator.

- **Préchargement intégral.** Avant lecture, la trajectoire complète est simulée et
  l'union exacte des tuiles nécessaires est téléchargée. Aucune requête réseau
  pendant l'animation, donc aucun à-coup à l'enregistrement.
- **Fondu entre niveaux.** Le niveau courant est dessiné opaque, le niveau suivant
  en fondu par-dessus. Le passage d'un niveau à l'autre est une opération neutre,
  ce qui rend le changement de résolution invisible.
- **Netteté à l'arrivée.** Sur les derniers 14 % du mouvement, le niveau affiché
  devient celui dont la résolution native est la plus proche de celle de l'écran,
  et non celui que dicte le réglage de finesse. Les tuiles concernées sont presque
  toujours déjà chargées, donc le gain est gratuit.
- **Chargement borné.** Chaque tuile est demandée par `fetch`, avec abandon à 5 s
  et deux nouvelles tentatives. Un code 4xx n'est jamais retenté : la donnée
  n'existe pas là, insister coûte trois requêtes pour rien. Huit requêtes en
  parallèle, au-delà HTTP/2 commence à réinitialiser des flux.
- **Couverture détectée, pas supposée.** Si la photo aérienne répond
  majoritairement 404 sur un niveau, ce niveau est rebasculé sur le plan IGN et
  rechargé. La bascule est constatée à l'exécution, donc elle suit l'évolution
  des pyramides IGN sans qu'on ait à coder une limite en dur.
- **Tolérance aux trous.** Une tuile qui n'a pas répondu est retentée deux fois,
  puis remplacée à l'affichage par le quartier correspondant de sa tuile parente.
  Un échec réseau se traduit par une zone légèrement floue, jamais par un carré vide.
- **Précision.** La conversion mercator vers coordonnées écran se fait en double
  précision côté JS ; seul le rectangle NDC est transmis au GPU. En float32 dans le
  shader, l'image se mettrait à cranter au-delà du zoom 15.
- **Composition 2D.** Le WebGL rend hors écran, un canvas 2D ajoute le vignettage,
  le repère, le cartouche et l'échelle. C'est ce canvas qui est capturé.

## Limites connues

- L'export sort en WebM (VP9). Safari n'enregistre pas ; utilisez Chrome, Edge ou Firefox.
- L'ortho plafonne au zoom 20. En deçà de ~150 m de large, l'image est agrandie.
- Les tuiles restent en VRAM sans éviction. Une longue session multiplie les lieux et
  peut dépasser 300 Mo ; recharger la page suffit.
- Aux zooms faibles, l'ortho ne couvre que la France. Pour un cadre de départ large,
  préférez « Photo aérienne puis plan IGN », qui bascule sur le plan à
  partir du niveau 16, soit environ 3 km de large.

## Arborescence

```
index.html              toute l'application, sans dépendance ni build
assets/ign_logo.png     logo incrusté dans le cartouche vidéo
assets/azimut-*.svg     identité Azimut : lockup blanc, encre, adaptatif, icône
tools/embed-logo.py     produit une version à fichier unique, logo en base64
```

## Servir la page

Le logo est chargé depuis `assets/`. Ouvrir `index.html` en double-cliquant place la
page en origine `file://`, ce qui altère le canvas et ferait échouer l'export vidéo :
l'application le détecte, prévient, et retombe sur un bloc IGN dessiné.

Passez donc par un serveur :

```
python -m http.server 8000
```

puis `http://localhost:8000/`. La version publiée sur GitHub Pages n'a pas ce problème.

Pour un fichier unique distribuable, qui fonctionne même en double-clic :

```
python tools/embed-logo.py      # ecrit azimut-autonome.html
```

## Polices

L'interface utilise **Public Sans** (SIL Open Font License), la police du US Web
Design System : même squelette dérivé du Franklin Gothic que Marianne, proportions
étroites et grande hauteur d'x, sans restriction d'usage.

Marianne est volontairement écartée : sa licence réserve son emploi à la
communication de l'État. Le mot « Azimut » du logo est en Barlow Condensed,
déjà vectorisé dans les SVG livrés, donc sans dépendance au chargement d'une police.
