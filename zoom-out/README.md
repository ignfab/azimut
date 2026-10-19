# Zoom Out

On part de n'importe où en France, tout près du sol, et la vue aérienne s'éloigne
sans jamais s'arrêter. Le premier qui trouve où l'on est gagne.

Un seul fichier, `index.html`, sans dépendance, sans serveur, sans clé d'API. Il
réutilise les flux ouverts de la Géoplateforme IGN, comme Azimut.

## Jouer

- **Le dézoom du jour** : un seul lieu, le même pour tout le monde, renouvelé
  chaque jour à minuit, heure de Paris. Moins d'une minute de jeu. Une seule tentative : une partie
  commencée reprend là où elle en était si on recharge la page, et une partie
  finie affiche son résultat jusqu'au lendemain. Chaque jour porte un numéro
  (n° 1 le 19 octobre 2026), pour comparer ses scores.
- **Partie libre, seul** lance une partie de cinq manches tirées au hasard.
- **Créer une partie à plusieurs** fixe un départ dans 30 s, 1 min ou 2 min, et
  donne un lien à envoyer aux collègues.

À chaque manche, la vue s'éloigne pendant 45 s, d'une largeur de quelques
centaines de mètres jusqu'à la France entière, toujours en photo aérienne. Une
seule réponse par manche, de deux façons :

- **taper le nom de la commune** — l'orthographe est traitée avec indulgence :
  accents, tirets, « St » pour Saint, articles, et une à trois petites fautes
  selon la longueur du nom. Le bon nom donne la distance zéro ;
- **ou cliquer sur la petite carte** : le clic vaut réponse, sans confirmation.

Taper une autre commune que la bonne n'est pas perdu : elle compte comme un
point posé en son centre, et rapporte des points selon la distance.

Après le dézoom, la réponse apparaît et la vue redescend vers elle pendant 5 s,
puis le plan IGN se pose en transparence sur la photo pendant les 4 dernières
secondes, pour lire les noms autour.

Points : 1000 au maximum, érodés par la distance et par le temps.

| distance | réponse immédiate | à mi-dézoom | à la fin |
|---|---|---|---|
| 1 km | 975 | 610 | 244 |
| 5 km | 882 | 552 | 221 |
| 25 km | 535 | 335 | 134 |
| 100 km | 82 | 51 | 21 |

## Le multijoueur sans serveur

Le lien contient deux nombres : une graine aléatoire et une heure de départ.

```
https://…/zoom-out/#p=p1gr0n-tqo1c0
                      graine  départ
```

Chaque navigateur en déduit, seul, les mêmes cinq lieux dans le même ordre, et
cale le dézoom sur l'horloge. Tout le monde voit donc la même image au même
instant, sans qu'aucune donnée ne circule entre les joueurs. Un retardataire
rejoint la manche en cours. Les horloges des ordinateurs sont synchronisées à
la seconde près, ce qui suffit largement.

Pour comparer, chacun copie son résultat en fin de partie et le colle dans la
discussion d'équipe :

```
Zoom Out · partie P1GR0
🟩🟨🟩⬛🟧  2 914 pts
1. 2,1 km en 9 s
2. 18 km en 22 s
…
```

Le temps de chaque manche départage le « premier qui trouve ».

Le résultat du dézoom du jour tient en une ligne :

```
Zoom Out · dézoom du jour n° 12
🟩  3,2 km en 9 s — 800 pts
https://ignfab.github.io/azimut/zoom-out/
```

Son lien renvoie
simplement vers la page du jeu, puisque tout le monde a les mêmes lieux ce
jour-là. Le tirage du jour vient d'un hachage de la date, sans serveur. Le code
étant public, un curieux pourrait calculer les lieux à l'avance : c'est un jeu
entre collègues, pas un concours doté.

Une partie terminée peut être rejouée plus tard avec les mêmes lieux, pour qui
n'était pas là.

## Réglages

Tout est en tête de script : nombre de manches (`ROUNDS`, et `DAILY_ROUNDS` pour le dézoom du jour), durées du dézoom et de la
réponse, largeur de départ et d'arrivée, transparence du plan, écart minimal
entre deux lieux, et barème (`scoreOf`).

Attention : tous les joueurs doivent ouvrir la même version du fichier. Modifier
une durée ou le contour change ce que donne une graine.

## Lieux de départ

Tirage uniforme en surface, n'importe où en France métropolitaine, Corse
comprise. Le contour embarqué vient d'ADMIN EXPRESS (IGN), simplifié à 1 300
points et rentré de 1,5 km vers l'intérieur ; l'étang de Berre en est exclu.
Contrôle sur 10 000 tirages comparés au contour officiel non simplifié : aucun
départ en mer, dans l'étang ou à l'étranger, et une répartition conforme aux
surfaces (la Corse reçoit 1,8 % des départs pour 1,6 % du territoire).

Le nom de la commune vient de geo.api.gouv.fr, qui renvoie la commune contenant
le point d'après les contours officiels, avec repli sur le géocodeur de la
Géoplateforme. La même source sert aux suggestions pendant la saisie.

## Fonctionnement

Moteur de tuiles Web Mercator en WebGL, repris d'Azimut en version allégée :
fondu entre niveaux, conversion des coordonnées en double précision côté
JavaScript, repli sur la tuile parente en cas de trou. Au lieu de tout précharger,
le jeu charge en continu les huit secondes à venir, et le début de la manche
suivante pendant l'affichage de la réponse.

La photo aérienne est la seule couche affichée pendant le jeu. Les rares trous
qu'elle présente aux petites échelles sont comblés par la tuile parente, ou par
les quatre tuiles filles, jamais par le plan. Le plan n'apparaît qu'à la fin de
chaque manche, en transparence, comme une réponse ; la petite carte de réponse
reste un plan, pour pouvoir y placer un point.
