#!/bin/bash
echo  
echo Appuyez sur une touche pour effectuer la recherche...
read -n 1 ch
python3 parcours.py -w
echo  
echo Appuyez sur une touche pour afficher le CSV...
read -n 1 ch
cat parcours.csv
echo  
echo  
echo Appuyez sur une touche pour fermer la fenetre...
read -n 1 ch

