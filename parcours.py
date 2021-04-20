#!/usr/bin/python3
# -*- coding: UTF-8 -*-
SCRIPT_VERSION=20210420.2105
SCRIPT_AUTHOR="fdz, ctesc356"
# Le script accepte les paramètres optionnels suivants:
#  -i fileName  (pour changer de fichier source)
#  -w           (pour exports en waypoints)
#  -t           (pour exports en trackpoints)
#
# What's new in this version:
#  - Amélioration de la compatibilité GPX
#  - Résolution du bug lié aux namespaces XML
#  - Prise en charge de fichiers GPX en entrée autres que AIXM_FR
#  - Régression: les fréquences doivent être indiquées dans le fichier texte pour identifier les émetteurs radio (CBY 115.40)
import os.path
import sys
import getopt
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
      strReturn="<lat>"+self.lat+"</lat>" + "<lon>"+self.lon+"</lon>" + "<name>"+self.name+"</name>" + "<sym>"+self.sym+"</sym>"
      if self.ele != "": strReturn=strReturn+"<ele>"+self.ele+"</ele>"
      strType="wpt"
      if self.type=="T": strType="trkpt"
      strReturn="<"+strType+">" + strReturn + "</"+strType+">"
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
      # print(nodeXML[1].text) - noeud enfant

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
   fileName=fileName.replace(".py","")
   fichierTxt=fileName+".txt"
   fichierGpx=fileName+".gpx"
   fichierCsv=fileName+".csv"
   fichierXml=fileName+".xml"
   fichierTmp=fileName+".dat"

   if os.path.exists(strGpxInputFileName) and os.path.exists(fichierTxt):
      print("In progress...")

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
         strXml=xmlDom.tostring(xmlWaypoint,encoding=strElementTreeEncoding,method="xml")
         pt=XmlToPoint(strXml,strTypePt)
         strXmlLine='<wpt'+' lat="'+pt.lat+'"'+' lon="'+pt.lon+'"'+'>'+'<name>'+pt.name+'</name>'+'<sym>'+pt.sym+'</sym>'+'<ele>'+pt.ele+'</ele>'+'</wpt>'
         objFicTmp.write(strXmlLine+"\n")
      objFicTmp.write("</gpx>")    #ligne de fin
      objFicTmp.close()

      # ouvre le fichier GPX en entree
      strGpxInputFileName=fichierTmp
      objFicGpxInput = open(strGpxInputFileName, "r")
      arrGpxInputFileLines=objFicGpxInput.readlines()    # charge le fichier bdd
      objFicGpxInput.close()

      objFicTxt = open(fichierTxt, "r")
      arrTxtFileLines=objFicTxt.readlines()   # charge le fichier texte
      objFicTxt.close()

      objFicGpx=open(fichierGpx, "w")    # raz fichier Gpx
      objFicGpx=open(fichierGpx, "a")
      
      objFicCsv=open(fichierCsv, "w")    # raz fichier Csv
      objFicCsv=open(fichierCsv, "a") 
   
      objFicXml=open(fichierXml, "w")    # raz fichier Xml
      objFicXml=open(fichierXml, "a") 
   
      i=0
      r=0
      t=0
      for txt in arrTxtFileLines: # boucle sur chaque ligne du fichier texte
         txt=txt.rstrip("\n") # suppression des lf
         txt=txt.rstrip()
         if len(txt)==0: 
            txt="chaine vide"
         else:
            r=r+1

         xAp = "["+txt+"]" # pour la recherche des aéroports: "LFLC"
         xSym="<sym>Airport"

         #if len(txt) == 5:
         #   xSym="<sym>Triangle" # si 5 caractères, on considère que le pt recherché est un point de report: "ALBER"
   
         #xNa = txt # pour la recherche des navaids : "MEN"
         #if len(txt) == 3:
         #  xNa="<name>" + xNa + " "
         #   xSym="<sym>Navaid"
   
         #xNaf = txt # pour la recherche des navaids avec le début de la fréquence mais sans la décimale: "MEN 115"
         #if len(txt) == 7:
         #   xNaf="<name>" + xNaf
         #   xSym="<sym>Navaid"

         xIls = txt # pour recherche ILS <name>IPL 109.90 - 14 [FIMP] 186ft</name>
         if len(txt) > 7:
            xIls="<name>" + xIls
            xSym="<sym>Pin, Red"

         txt = "<name>" + txt + "</name>"  # pour une recherche (dans tous les cas) à l'identique
      
         for strXmlLine in arrGpxInputFileLines: # pour chaque ligne du fichier GPX
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

            #elif txt in strXmlLine or ( xSym in strXmlLine and (xAp in strXmlLine or xNa in strXmlLine or xNaf in strXmlLine or xIls in strXmlLine) ) :
            elif txt in strXmlLine or ( xSym in strXmlLine and (xAp in strXmlLine or xIls in strXmlLine) ) :
               pt=XmlToPoint(strXmlLine,strTypePt)
               if pt != None: 
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
               break

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
      opts, args = getopt.getopt(sys.argv[1:], "i:twv") # ["input", "trackpoint", "waypoint"]

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
      chercheWaypointDansGpxEtExporte(strFileName,strType,strElementTreeEncoding) # type=W (waypoint) ou T (trackpoint)

# ---------------------------------------------------------------------------------------------- 
# lance la procedure principale
if __name__ == "__main__":
    main("AIXM_X_IFR_FR.gpx")

