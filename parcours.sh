#!/bin/bash
python parcours.py -w
echo  
echo Appuyez sur une touche pour afficher le CSV...
read -n 1 ch
cat parcours.csv
echo  
echo Appuyez sur une touche pour afficher le GPX...
read -n 1 ch
cat parcours.gpx
echo  
echo  
echo Appuyez sur une touche pour fermer la fenetre...
read -n 1 ch

