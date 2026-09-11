# Azimut

Fabrique un travelling vertical vers n'importe quel point de France, sur les fonds
de la Géoplateforme IGN, et l'exporte en vidéo. Pensé pour le montage d'un sujet TV.

Tout tient dans `index.html` : pas de build, pas de dépendance, pas de clé d'API.
Ouvrez le fichier dans un navigateur, ou servez-le en statique.

## Utilisation

1. Saisissez une adresse, un lieu-dit, ou des coordonnées `48.8584, 2.2945`.
2. Réglez la durée, le cadre de départ et d'arrivée, le rythme.
3. **Lancer l'animation** précharge les tuiles puis joue le plan.
4. **Enregistrer la vidéo** rejoue le plan et télécharge un WebM.

Le WebM se convertit en master de montage avec :

```
ffmpeg -i zoom-mont-saint-michel.webm -c:v prores_ks -profile:v 3 plan.mov
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
  préférez « Plan IGN puis photo aérienne ».

## Logo

`logo/` contient le lockup en blanc, en encre, en version adaptative, et l'icône
carrée. Le mot est vectorisé, il n'y a aucune dépendance à une police.
