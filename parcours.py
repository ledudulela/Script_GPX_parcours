#!/usr/bin/python3
# -*- coding: UTF-8 -*-
SCRIPT_VERSION=20210422.1907
SCRIPT_AUTHOR="fdz, ctesc356"
# Le script accepte les paramètres optionnels de ligne de commande suivants:
#  -i fileName  : pour changer de fichier source (base de données de référence)
#  -w           : pour exports en waypoints
#  -t           : pour exports en trackpoints
#  -v           : pour connaitre la version du script
#  -d           : pour concaténer les fichiers CSV (données FGFS) en un seul fichier de données (.dat) au format GPX
#
# What's new in this version:
#  - Nouvelle fonction de concaténation de fichiers CSV provenant de FGFS en un seul fichier de données (.dat) au format GPX
#
# Infos:
# Si le fichier source a une extension .gpx, il sera dans un premier temps analysé et converti dans un fichier .dat .
# Si le fichier source a une extension .dat, il ne sera pas analysé.
# Dans les deux cas, le fichier .dat servira de fichier source à la fonction de recherche.
# Ce fichier .dat doit contenir des données au format gpx avec une ligne par waypoint, sans tabulation, sans quoi le script génèrera des erreurs.
# La fonction de recherche de waypoints nécessite ce formalisme pour rendre son exécution la rapide possible.
# Si le paramètre -i n'est pas spécifié, et qu'un fichier .dat ayant le même nom que le script est présent dans le répertoire, 
# alors ce fichier .dat servira par défaut de fichier source (si le fichier AIXM du tutoriel n'est pas également présent).
# Dans le fichier texte, les waypoints avec fréquence doivent être saisis avec leur fréquence pour éviter les doublons dans le résultat de la recherche.
# Attention au dernier 0 non significatif de la fréquence (le formalisme doit correspondre à celui du fichier source)
#
import os.path
import sys
import getopt
from datetime import date
from xml.etree import ElementTree as xmlDom

# ----------------------------------------------------------------------------------------------------------
class GPoint:
   "Définition d'un point géographique"

   def __init__(self,strType="W",strLat="0.0",strLon="0.0",strName="UNKNOWN",strEle="",strSym="Waypoint"):
      self.type=strType
      self.lat=strLat
      self.lon=strLon
      self.name=strName
      self.ele=strEle
      self.sym=strSym
      #print("type:"+self.type,"name:"+self.name,"lat:"+self.lat,"lon:"+self.lon,"sym:"+self.sym,"ele:"+self.ele)

   # conversion en GPX
   def toGpx(self):
      strReturn="<name>"+self.name+"</name>" + "<sym>"+self.sym+"</sym>"
      if self.ele != "": strReturn=strReturn+"<ele>"+self.ele+"</ele>"
      strType="wpt"
      if self.type=="T": strType="trkpt"
      strReturn="<"+strType+ ' lat="'+self.lat+'"'+' lon="'+self.lon+'"'+ ">" + strReturn + "</"+strType+">"
      return strReturn
   
   # conversion en CSV
   def toCsv(self):
      SEPAR=","
      return self.type + SEPAR + self.lat + SEPAR + self.lon + SEPAR + "\"" + self.sym + "\"" + SEPAR + self.name # self.ele

   # conversion en XML compatible FGFS Route Manager
   def toFgXml(self): 
      strReturn=""
      pt=self
      if not pt.sym.find("Airport")==-1: pt.sym="airport"
      if not pt.sym.find("Heliport")==-1: pt.sym="airport"
      if not pt.sym.find("Triangle")==-1: pt.sym="basic"
      if not pt.sym.find("Navaid")==-1:
         pt.sym="navaid" # offset-navaid
         pt.name=pt.name[0:3].rstrip()
      
      strOACI=""
      if pt.sym=="airport":
         i=pt.name.find("[")+1
         j=pt.name.find("]")
         strOACI=pt.name[i:j]
         pt.name=strOACI

      strReturn="<lat>"+pt.lat+"</lat>" + "<lon>"+pt.lon+"</lon>" + "<ident>"+pt.name+"</ident>" + "<type>"+pt.sym+"</type>"

      if pt.ele!="": strReturn=strReturn + "<altitude-ft>"+str(int(float(pt.ele)*3.31))+"</altitude-ft>"

      if len(strOACI)>0: strReturn=strReturn+"<oaci>"+strOACI+"</oaci>"

      strReturn="<wp>"+ strReturn +"</wp>"
      return strReturn


# ----------------------------------------------------------------------------------------------------------
# Conversion du XML en un objet de type GPoint
def XmlToPoint(strXML,strType):
   if len(strXML)>0:
      nodeXML=xmlDom.fromstring(strXML.replace("ns0:","")) # au cas ou, retire le namespace par defaut
      #print(nodeXML.tag,nodeXML.attrib)
      pt=GPoint()
      pt.type=strType
      pt.lat=nodeXML.get('lat')
      pt.lon=nodeXML.get('lon')

      # noeud enfant:
      #print(nodeXML[1].text) 

      if nodeXML.find('name') != None:
         if nodeXML.find('name').text != None: 
            pt.name=nodeXML.find('name').text

      if nodeXML.find('sym') != None:
         if nodeXML.find('sym').text != None: 
            pt.sym=nodeXML.find('sym').text

      if nodeXML.find('ele') != None:
         if nodeXML.find('ele').text != None:
            pt.ele=nodeXML.find('ele').text
   
      return pt
   else:
      return None

# ----------------------------------------------------------------------------------------------------------
def chercheWaypointDansGpxEtExporte(strGpxInputFileName,strTypePt="W",strElementTreeEncoding="unicode"):
   fileName=sys.argv[0]
   arrFileRootExt=os.path.splitext(fileName)
   fileName=fileName.replace(arrFileRootExt[1],"")
   fichierTxt=fileName+".txt"
   fichierGpx=fileName+".gpx"
   fichierCsv=fileName+".csv"
   fichierXml=fileName+".xml"
   fichierTmp=fileName+".dat"

   if os.path.exists(strGpxInputFileName) and os.path.exists(fichierTxt):
      print("In progress...")
      arrFileRootExt=os.path.splitext(strGpxInputFileName)
      if arrFileRootExt[1] != ".dat": # si le fichier en entrée n'a pas l'extention .dat alors analyse le fichier et le convertit en un .dat temporaire
         l=0
         print("Analyzing "+strGpxInputFileName+" ...")
         # cree un fichier temporaire gpx a partir du fichier GPX en entree en retirant tous les retour-charriots inutiles,
         # et en mettant les donnees en conformite
         objFicTmp=open(fichierTmp, "w")    # raz fichier Tmp
         objFicTmp=open(fichierTmp, "a")

         objFicTmp.write('﻿<?xml version="1.0" encoding="UTF-8"?>'+"\n")
         objFicTmp.write('<gpx version="1.0" creator="'+sys.argv[0]+'" xmlns="http://www.topografix.com/GPX/1/0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/0/gpx.xsd">'+"\n")

         xmlContent=xmlDom.parse(strGpxInputFileName)
         xmlRoot=xmlContent.getroot()
         strNamespace={'ns0':'http://www.topografix.com/GPX/1/0'}
         xmlWaypoints=xmlRoot.findall('ns0:wpt' ,strNamespace)
         if len(xmlWaypoints)==0: xmlWaypoints=xmlRoot.findall('wpt')
         for xmlWaypoint in xmlWaypoints:
            l=l+1
            strXml=xmlDom.tostring(xmlWaypoint,encoding=strElementTreeEncoding,method="xml")
            #print("DEBUG",l,strXml)
            pt=XmlToPoint(strXml,strTypePt)
            strXmlLine='<wpt'+' lat="'+pt.lat+'"'+' lon="'+pt.lon+'"'+'>'+'<name>'+pt.name+'</name>'+'<sym>'+pt.sym+'</sym>'+'<ele>'+pt.ele+'</ele>'+'</wpt>'
            objFicTmp.write(strXmlLine+"\n")
          
         objFicTmp.write("</gpx>")    #ligne de fin
         objFicTmp.close()
      else:
         fichierTmp=strGpxInputFileName

      # ouvre le fichier GPX en entree, en mode texte, car les methodes xmlDom.parse(GpxFile) et xmlRoot.findall('wpt') sont trop longues à l' exécution
      # en python, le parcours d'un tableau est bien plus rapide que le parcours d'une collection d'éléments XML (ElementTree)
      strGpxInputFileName=fichierTmp
      objFicGpxInput = open(strGpxInputFileName, "r") 
      arrGpxInputFileLines=objFicGpxInput.readlines() # charge le fichier bdd
      objFicGpxInput.close()

      objFicTxt = open(fichierTxt, "r")
      arrTxtFileLines=objFicTxt.readlines()   # charge le fichier texte
      objFicTxt.close()

      objFicGpx=open(fichierGpx, "w")    # raz fichier Gpx cible
      objFicGpx=open(fichierGpx, "a")
      
      objFicCsv=open(fichierCsv, "w")    # raz fichier Csv cible
      objFicCsv=open(fichierCsv, "a") 
   
      objFicXml=open(fichierXml, "w")    # raz fichier Xml cible
      objFicXml=open(fichierXml, "a") 
   
      i=0
      r=0
      t=0
      l=0
      boolTrouve=False
      for txt in arrTxtFileLines: # boucle sur chaque ligne du fichier texte
         txt=txt.rstrip("\n") # suppression des lf
         txt=txt.rstrip()
         if len(txt)==0: 
            txt="- ligne vide -"
            boolTrouve=True
         else:
            r=r+1
            boolTrouve=False
            print(str(r)+".",'"'+txt+'"',":")

         # pour la recherche des aéroports: "LFLC"
         xAp = "["+txt+"]"
         xSymAp="<sym>Airport"

         # pour recherche ILS <name>IPL 109.90 - 14 [FIMP] 186ft</name>
         xIls="<name>"+txt
         xSymIls="<sym>Pin"

         # pour une recherche (dans tous les cas) à l'identique
         xName = "<name>" + txt + "</name>"

         l=0
         for strXmlLine in arrGpxInputFileLines: # pour chaque ligne du fichier GPX
            l=l+1
            strXmlLine=strXmlLine.rstrip("\n")
            if i < 2:
               objFicGpx.write(strXmlLine)  # recopie des 2 lignes entête GPX
               objFicGpx.write("\n")
               i=i+1

               if i==2: 
                  objFicCsv.write("type,latitude,longitude,sym,name")  # écriture des entêtes
                  objFicCsv.write("\n")

                  objFicXml.write("<?xml version=\"1.0\"?><PropertyList><route>")  # écriture entête et noeud racine
                  objFicXml.write("\n")

                  if strTypePt=="T":
                     objFicGpx.write("<trk><trkseg>")  # écriture noeuds
                     objFicGpx.write("\n")

            elif (xName in strXmlLine) or (xAp in strXmlLine and xSymAp in strXmlLine) or (xIls in strXmlLine and xSymIls in strXmlLine):
               pt=XmlToPoint(strXmlLine,strTypePt)
               if pt != None: 
                  boolTrouve=True
                  print(strXmlLine)

                  line=pt.toGpx()
                  objFicGpx.write(line) # écriture ligne
                  objFicGpx.write("\n")

                  line=pt.toCsv()
                  objFicCsv.write(line) # écriture ligne
                  objFicCsv.write("\n")

                  line=pt.toFgXml()
                  objFicXml.write(line) # écriture ligne
                  objFicXml.write("\n")
	   
                  t=t+1
               # pas de break, pour ne pas s'arreter à la première valeur trouvée
         # fin du for txt
         if not boolTrouve: print("   not found.")

      if strTypePt=="T":
         objFicGpx.write("</trkseg></trk>")  # écriture fermeture noeuds
         objFicGpx.write("\n")
      objFicGpx.write("</gpx>")    # écriture fermeture noeud racine
      objFicGpx.close()

      objFicXml.write("</route></PropertyList>")    # écriture fermeture noeud racine
      objFicXml.close()

      objFicCsv.close()
   
      print("End: "+str(t)+"/"+str(r)+" waypoints.")

   else:
      print("Input-File(s) not found.")

# ----------------------------------------------------------------------------------------------   
# concatène des fichiers CSV en un gros fichier de données (.dat) au format GPX; ce fichier peut être très volumineux
def concatCsvFileToGpxFile():
   # Liste de fichiers créés à partir d'extractions de données du fichier FGFS_DATA.ods
   arrFileList=["FGFS_DATA_APT","FGFS_DATA_ILS-CAT","FGFS_DATA_DME-ILS","FGFS_DATA_FIXES","FGFS_DATA_NDB","FGFS_DATA_VOR-DME","FGFS_DATA_ILS"]
   # Le fichier "FGFS_DATA_ILS.csv" est créé à mla volée dans cette fonction. 
   # Il contient la liste des ILS provenant des fichiers ILS-CAT complétée par les DME-ILS et à laquelle on retire les doublons.
   # Il sera intégré au fichier GPX final.

   fileName=sys.argv[0]
   arrFileRootExt=os.path.splitext(fileName)
   strFicGpx=fileName.replace(arrFileRootExt[1],".dat") 
   objFicGpx=open(strFicGpx, "w") # raz fichier
   objFicGpx=open(strFicGpx, "a")

   # pour les ILS, sans doublon, dans un seul fichier CSV 
   strFicCsvILS="FGFS_DATA_ILS.csv"
   objFicCsvILS=open(strFicCsvILS, "w") # raz fichier
   objFicCsvILS=open(strFicCsvILS, "a")
   strFicCsvILS="lat,lon,sym,name" # entêtes

   objFicGpx.write('﻿<?xml version="1.0" encoding="UTF-8"?>'+"\n")
   objFicGpx.write('<gpx version="1.0" creator="' + fileName  +' - '+ str(date.today()) +'" xmlns="http://www.topografix.com/GPX/1/0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/0/gpx.xsd">'+"\n")

   for fileName in arrFileList:
      
      if fileName=="FGFS_DATA_ILS": # finalise la création de ce fichier
         objFicCsvILS.write(strFicCsvILS)
         objFicCsvILS.close()

      fileCSV=fileName+".csv"
      if os.path.exists(fileCSV):
         objFicCsv = open(fileCSV, "r")
         arrCsvFileLines=objFicCsv.readlines()   # charge le fichier texte
         objFicCsv.close()
         print(fileName)

         i=0
         c=0
         colLat=-1
         colLon=-1
         colName=-1
         colSym=-1
         colEle=-1

         for txt in arrCsvFileLines: # boucle sur chaque ligne du fichier texte
            strLat=""
            strLon=""
            strName=""
            strSym=""
            strEle=""

            strGpxLat=""
            strGpxLon=""
            strGpxName=""
            strGpxSym=""
            strGpxEle=""

            strIdentifiant=""
 
            i=i+1
            txt=txt.rstrip("\n") # suppression des lf
            txt=txt.rstrip()
            if len(txt)>0:
               txt=txt.replace(", ","||")
               txt=txt.replace("&","+")
               arrValues=txt.split(",") # format CSV attendu: lat,lon,sym,name(,ele)
               if i==1:
                  for col in arrValues:
                     if col=="lat" or col=="latitude": colLat=c
                     if col=="lon" or col=="longitude": colLon=c
                     if col=="name": colName=c
                     if col=="sym": colSym=c
                     if col=="ele" or col=="alt-ft" or col=="alt-m": colEle=c
                     c=c+1
               else:
                  strILSIdentifiant=""

                  if colLat!=-1:
                     strLat=arrValues[colLat]
                     strGpxLat="lat=\""+strLat+"\""

                  if colLon!=-1: 
                     strLon=arrValues[colLon]
                     strGpxLon="lon=\""+strLon+"\""

                  if colName!=-1: 
                     strName=arrValues[colName]
                     strGpxName="<name>"+strName+"</name>"

                     # pour la suppression de doublons des ILS, crée un identifiant unique
                     strIdentifiant=strName
                     p=strIdentifiant.find("]")
                     if p>0: 
                        strIdentifiant=strIdentifiant[0:p+1]
                        arrIdentifiant=strIdentifiant.split(' ')
                        p=len(arrIdentifiant)
                        if p>1: strIdentifiant=arrIdentifiant[0]+" "+arrIdentifiant[1] +" "+arrIdentifiant[p-1]

                  if colSym!=-1: 
                     strSym=arrValues[colSym]
                     strSym=strSym.replace("||",", ") # pour les symboles à virgule
                     strGpxSym="<sym>"+strSym.replace("\"","")+"</sym>" # retrait des double-quotes

                  if colEle!=-1:
                     strEle=arrValues[colEle]
                     strGpxEle="<ele>"+strEle+"</ele>"

                  # suppression de doublons des ILS
                  if fileName=="FGFS_DATA_DME-ILS" or fileName=="FGFS_DATA_ILS-CAT":
                     p=strFicCsvILS.find(strIdentifiant) # cherche l identifiant dans le contenu CSV des ILS
                     if not p>0: # si l'identifiant n'existe pas, ajoute la ligne au contenu CSV des ILS
                        strSym='"Pin, Red"' # unifie la couleur; mettre la ligne en commentaire pour deboguer
                        strFicCsvILS=strFicCsvILS+"\n"+ strLat+","+strLon+","+strSym+","+strIdentifiant
                     #else:
                     #   print("DEBUG",strIdentifiant," existe déjà")

                  else: 
                     strGpxLine="<wpt "+strGpxLat+" "+strGpxLon+">" + strGpxSym + strGpxName + strGpxEle + "</wpt>"+"\n"
                     objFicGpx.write(strGpxLine)

                  # fin du if fileName ILS*
  
         # fin du for txt in arrFileList

      # fin du if file exists

   # fin du for fileName in arrCsvFileLines

   objFicGpx.write("</gpx>")
   objFicGpx.close()


# ----------------------------------------------------------------------------------------------   
# fonction de test pour parser du XML au format GPX
def parseGPX():
   xmlContent=xmlDom.parse("AIXM_X_IFR_FR.gpx")
   xmlRoot=xmlContent.getroot()
   strNamespace={'ns0':'http://www.topografix.com/GPX/1/0'}
   xmlWaypoints=xmlRoot.findall('ns0:wpt')
   print(len(xmlWaypoints))
   i=0
   for xmlWaypoint in xmlWaypoints:
      i=i+1
      strElementTreeEncoding="unicode"
      if sys.version_info.major<3: strElementTreeEncoding="UTF-8"
      strXml=xmlDom.tostring(xmlWaypoint,encoding=strElementTreeEncoding,method="xml")
      pt=XmlToPoint(strXml,"W")
      print(i, pt.toCsv()) # xmlWaypoint

# ---------------------------------------------------------------------------------------------- 
# fonction principale récupérant les paramètres de ligne de commande
def main(strFileName,strType="W"):
   try:                                
      opts, args = getopt.getopt(sys.argv[1:], "i:twvd") # ["input", "trackpoint", "waypoint"]

   except getopt.GetoptError:
      print("Parametre(s) non valide(s).")
      sys.exit(2) 

   opt=""
   for opt, arg in opts:
      #print(opt)
      if opt == "-t": strType="T"
      if opt == "-w": strType="W"
      if opt == "-i": 
         strFileName=arg

   #print(sys.argv[0],sys.argv[1:])
   #print(strType,strFileName)
   strElementTreeEncoding="unicode"
   if sys.version_info.major<3: strElementTreeEncoding="UTF-8"
   if opt == "-v":
      print("version:",SCRIPT_VERSION)
   else:
      if opt == "-d":
         concatCsvFileToGpxFile()
      else:
         chercheWaypointDansGpxEtExporte(strFileName,strType,strElementTreeEncoding) # type=W (waypoint) ou T (trackpoint)

# ---------------------------------------------------------------------------------------------- 
# lance la procedure principale
if __name__ == "__main__":
    strInputFileName="AIXM_X_IFR_FR.gpx" # fichier par défaut historique (tuto)
    if not os.path.exists(strInputFileName): 
       strInputFileName=sys.argv[0].replace(".py",".dat") # le fichier par défaut est le fichier .dat
    main(strInputFileName)

