# SinkholeContour
Code from the paper (https://doi.org/10.5194/ica-proc-2-133-2019) to generate contour lines on terrains with many sinkholes. The instructions below are in French.

## Génération du MNT

Méthode de Pyry Kettunen, Christian Koski & Juha Oksanen

1. On réalise 2 lissages gaussien du MNT :
	→ DEM1: (33x33) ; σ = 5
	→ DEM2: (133x133) ; σ = 15

2. On calcule le TPI du MNT
3. On lisse le TPI : (33x33) ; σ = 5

4. On calcule le cDEM de la manière suivante :
	→  cDEM[i][j] = cTPI[i][j]*DEM1[i][j]+(1-cTPI[i][j])*DEM2[i][j]

exécuter le script *masque_TraitementMNT.py* par exemple avec Spyder ou VS Code -> cela génère le fichier ouv_ferm_12.asc et le MNT pour tracer les courbes de niveau

_Sortie : le MNT pour tracer les courbes de niveau ainsi que le masque de plaine_montagne_

## Localisation des dépressions

il faut ouvrir QGIS et ouvrir la commande de pyQGIS et afficher l'éditeur
Placez le MNT.asc et le fichier ouv_ferm_12.asc dans le même dossier que le script pyQGIS ensuite charger le script *plugin.py* dans l'éditeur et exécuter

Dans le plugin.py vous pouvez changer les valeurs des seuils pour avoir différents résultats.

_Sortie : shapefile des dépressions_

## Ajustement des dépressions

- On dilate les dépressions sur une approche différente de celle proposée par les filtres morphologiques (algorithme d’inondation). *Remplissage_cuvettes.py*

- On calcule le max, min, et profondeur des dépressions à partir du cDEM, en utilisant l'outil de statistiques de zones de QGIS.

- On applique l’algorithme d’ajustement des dépressions (*representation_depressions.py*). On réalise l’opération pour 2 seuils :
	→ s = 3 (théorie)
	→ s = 1,2 (empirique)

_Sortie : 2 MNT avec 2 ajustements différents_

## Génération des courbes de niveau

- On trace ensuite les courbes de niveau des 2 MNT sur QGIS (à l’aide de l’outil contour)

_Sortie : 2 shapefile de courbes de niveau_

## Produit final

-  On enregistre les courbes maitresses d’un des shapefile (celui de 1,2 par exemple).
- On nettoie ensuite les deux shapefile de leur courbes maitresses
	→ Calculatrice Raster ( $length  > 700)

- On génère ensuite des polygones à partir des lignes pour les 2 shapefiles.
- Puis pour chaque shapefile, on supprime les bleus dans les rouges ou les rouges dans les bleus
