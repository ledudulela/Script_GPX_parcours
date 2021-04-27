#!/usr/bin/python3
# -*- coding: UTF-8 -*-
SCRIPT_VERSION=20210427.1845
SCRIPT_AUTHOR="fdz, ctesc356"
# Le script recherche dans la base de données (format GPX) les points spécifiés dans le fichier .txt 
# Le résultat de la recherche est stockée  sous forme de fichiers .csv et .gpx ( expérimental: .xml pour route manager FGFS )
# Le script accepte les paramètres optionnels de ligne de commande suivants:
#  -v           : pour connaitre la version du script
#  -i fileName  : pour spécifier le fichier source (base de données de référence à la recherche)
#  -w           : pour exports en waypoints
#  -t           : pour exports en trackpoints
#  -c fileName  : pour convertir un fichier GPX en fichier CSV ( option -w ou -t possible avant -c )
#  -x fileName  : pour extraire des données d'un fichier GPX en fonction de coordonnées géographiques et de types de points (nécessite un fichier de config)
#  -d           : pour concaténer les fichiers CSV (données FGFS) en un seul fichier de données (.dat) au format GPX
#
# What's new in this version:
#  - Adaptation pour une utilisation avec le script d'interface graphique (tkinter)
#  - Améliorations mineures du code
#
# Infos pratiques:
# Le fichier .txt (contenant les points à rechercher) doit avoir le même nom que le script. Ex: parcours.py -> parcours.txt
# Si le fichier source a une extension .gpx, il sera dans un premier temps analysé et converti dans un fichier .dat .
# Si le fichier source a une extension .dat, il ne sera pas analysé (exécution plus rapide; à utiliser uniquement si le fichier .dat est fiable(*) ).
# Dans les deux cas, le fichier .dat servira de fichier source à la fonction de recherche.
# (*) Ce fichier .dat doit contenir des données au format gpx avec une ligne par waypoint, sans tabulation, sans quoi le script génèrera des erreurs.
# La fonction de recherche de points nécessite ce formalisme pour rendre son exécution la rapide possible.
# Si le paramètre -i n'est pas spécifié, et qu'un fichier .dat ayant le même nom que le script est présent dans le répertoire, 
# alors ce fichier .dat servira par défaut de fichier source (si le fichier AIXM du tutoriel n'est pas également présent).
# Dans le fichier texte, les waypoints avec fréquence doivent être saisis avec leur fréquence pour éviter les doublons dans le résultat de la recherche.
# Attention au dernier 0 non significatif de la fréquence (le formatage doit correspondre à celui du fichier source)
#
# ----------------------------------------------------------------------------------------------------------
import os.path
import sys
import getopt
from datetime import date
from datetime import datetime
from xml.etree import ElementTree as xmlDom
# ----------------------------------------------------------------------------------------------------------
# constantes et variables globales
GPXNAMESPACE='http://www.topografix.com/GPX/1/0'
gkvNamespace={'ns0':GPXNAMESPACE}
XMLHEADER='<?xml version="1.0" encoding="UTF-8"?>'
GPXROOTNODE='<gpx version="1.0" creator="%s" xmlns="'+GPXNAMESPACE+'" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="'+GPXNAMESPACE+'/gpx.xsd">' # l'attribut "creator" est une chaine à contenu variable "%s"

# ----------------------------------------------------------------------------------------------------------
def scriptBaseName():
   return sys.argv[0].replace("_ui","")

def xmlEltTreeEncoding():
    strElementTreeEncoding="unicode" 
    if sys.version_info.major<3: strElementTreeEncoding="UTF-8"
    return strElementTreeEncoding

def remove_non_ascii(text):
    return ''.join([i if ord(i) < 128 else '_' for i in text])

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

      if nodeXML.get('lat') != None: pt.lat=nodeXML.get('lat')
      if nodeXML.get('lon') != None: pt.lon=nodeXML.get('lon')

      # noeud enfant:
      #print(nodeXML[1].text) 

      if nodeXML.find('name') != None:
         if nodeXML.find('name').text != None:
            pt.name=remove_non_ascii(nodeXML.find('name').text)

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
def chercheWaypointDansGpxEtExporte(strGpxInputFileName,strTypePt="W",strTxtInputFileName="",strElementTreeEncoding="unicode"):
   fileName=scriptBaseName()
   arrFileRootExt=os.path.splitext(fileName)
   fileName=arrFileRootExt[0] # fileName.replace(arrFileRootExt[1],"")
   fichierTxt=fileName+".txt"
   fichierLog=fileName+".log"
   fichierGpx=fileName+".gpx"
   fichierCsv=fileName+".csv"
   fichierXml=fileName+".xml"
   fichierTmp=fileName+".dat"
   if strTxtInputFileName!="": fichierTxt=strTxtInputFileName

   #print(strGpxInputFileName,fichierTxt)
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

         objFicTmp.write(XMLHEADER+"\n")
         objFicTmp.write(GPXROOTNODE%scriptBaseName()+"\n")

         xmlContent=xmlDom.parse(strGpxInputFileName)
         xmlRoot=xmlContent.getroot()

         xmlWaypoints=xmlRoot.findall('ns0:wpt' ,gkvNamespace)
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

      strTS=datetime.now()
      objFicLog=open(fichierLog, "w")    # raz fichier Log cible
      objFicLog=open(fichierLog, "a") 
      objFicLog.write(strTS.strftime("%Y%m%d%H%M%S"))  # 
      objFicLog.write("\n")

      objFicGpx=open(fichierGpx, "w")    # raz fichier Gpx cible
      objFicGpx=open(fichierGpx, "a")
      objFicGpx.write(XMLHEADER+"\n")
      objFicGpx.write(GPXROOTNODE%scriptBaseName()+"\n")

      if strTypePt=="T":
         objFicGpx.write("<trk><trkseg>")  # écriture noeuds
         objFicGpx.write("\n")
      
      objFicCsv=open(fichierCsv, "w")    # raz fichier Csv cible
      objFicCsv=open(fichierCsv, "a") 
      objFicCsv.write("type,latitude,longitude,sym,name")  # écriture des entêtes
      objFicCsv.write("\n")
   
      objFicXml=open(fichierXml, "w")    # raz fichier Xml cible
      objFicXml=open(fichierXml, "a") 
      objFicXml.write(XMLHEADER+"<PropertyList><route>")  # écriture entête et noeud racine
      objFicXml.write("\n")
   
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
            if (xName in strXmlLine) or (xAp in strXmlLine and xSymAp in strXmlLine) or (xIls in strXmlLine and xSymIls in strXmlLine):
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
         if not boolTrouve: 
            strLog=" not found."
            objFicLog.write(txt+strLog+"\n") 
            print("  "+strLog)

      if strTypePt=="T":
         objFicGpx.write("</trkseg></trk>")  # écriture fermeture noeuds
         objFicGpx.write("\n")
      objFicGpx.write("</gpx>")    # écriture fermeture noeud racine
      objFicGpx.close()

      objFicXml.write("</route></PropertyList>")    # écriture fermeture noeud racine
      objFicXml.close()

      objFicCsv.close()

      strLog="End: "+str(t)+"/"+str(r)+" waypoints."
      objFicLog.write(strLog)
      objFicLog.close()
      print(strLog)

   else:
      print("Input-File(s) not found.")

# ----------------------------------------------------------------------------------------------   
# concatène des fichiers CSV en un gros fichier de données (.dat) au format GPX; ce fichier peut être très volumineux
def concatCsvFilesToGpxDb(strFilePrefix):
   boolFileNotFound=False  # True si au moins un fichier csv n'a pas été trouvé
   
   # Liste de fichiers créés à partir d'extractions de données du fichier FGFS_DATA.ods
   arrFileList=["APT","ILS-CAT","DME-ILS","FIXES","NDB","VOR-DME","ILS"]
   # Le fichier "FGFS_DATA_ILS.csv" est créé à mla volée dans cette fonction. 
   # Il contient la liste des ILS provenant des fichiers ILS-CAT complétée par les DME-ILS et à laquelle on retire les doublons.
   # Il sera intégré au fichier GPX final.
   strCsvEntetes="lat,lon,sym,name"

   fileName=scriptBaseName()
   arrFileRootExt=os.path.splitext(fileName)
   strFicGpx=arrFileRootExt[0]+".dat" # fileName.replace(arrFileRootExt[1],".dat") 
   objFicGpx=open(strFicGpx, "w") # raz fichier
   objFicGpx=open(strFicGpx, "a")

   # pour les ILS, sans doublon, dans un seul fichier CSV 
   strFicCsvILS=strFilePrefix+"ILS"+".csv"
   objFicCsvILS=open(strFicCsvILS, "w") # raz fichier
   objFicCsvILS=open(strFicCsvILS, "a")
   strFicCsvILS=strCsvEntetes # entêtes

   objFicGpx.write(XMLHEADER+"\n")
   objFicGpx.write(GPXROOTNODE%(fileName  +' - '+ str(date.today())) + "\n")

   for fileName in arrFileList:
      
      if fileName=="ILS": # finalise la création de ce fichier
         objFicCsvILS.write(strFicCsvILS)
         objFicCsvILS.close()
         if not boolFileNotFound: print(fileName,"done")

      fileCSV=strFilePrefix+fileName+".csv"
      if os.path.exists(fileCSV):
         objFicCsv = open(fileCSV, "r")
         arrCsvFileLines=objFicCsv.readlines()   # charge le fichier texte
         objFicCsv.close()
         if not boolFileNotFound: print(fileName,"found,")

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
                  if fileName=="DME-ILS" or fileName=="ILS-CAT":
                     p=strFicCsvILS.find(strIdentifiant) # cherche l identifiant dans le contenu CSV des ILS
                     if not p>0: # si l'identifiant n'existe pas, ajoute la ligne au contenu CSV des ILS
                        strSym='"Pin, Red"' # unifie la couleur; mettre la ligne en commentaire pour deboguer
                        strFicCsvILS=strFicCsvILS+"\n"+ strLat+","+strLon+","+strSym+","+strIdentifiant
                     #else:
                     #   print("DEBUG",strIdentifiant," existe déjà")

                  else: 
                     # ecriture dans le fichier GPX
                     strGpxLine="<wpt "+strGpxLat+" "+strGpxLon+">" + strGpxSym + strGpxName + strGpxEle + "</wpt>"+"\n"
                     objFicGpx.write(strGpxLine)

                  # fin du if fileName ILS*
  
         # fin du for txt in arrFileList
      else:
         print(fileCSV,"not found.")
         boolFileNotFound=True # au moins un fichier n'a pas été trouvé
      # fin du if file exists

   # fin du for fileName in arrCsvFileLines


   objFicGpx.write("</gpx>")
   objFicGpx.close()

   if not boolFileNotFound: print(strFicGpx,"done")

# ----------------------------------------------------------------------------------------------   
# fonction de conversion de GPX vers CSV
def convertGpxFileToCsvFile(strFileName,strPtType,strElementTreeEncoding):
   strReturn=""
   if os.path.exists(strFileName):
      strFileCsv=strFileName+".csv"
      objFicCsv=open(strFileCsv, "w") # raz fichier
      objFicCsv=open(strFileCsv, "a")
      objFicCsv.write("type,lat,lon,sym,name")

      # waypoint <wpt> ou trackpoint <trk><trkseg><trkpt>
      xmlContent=xmlDom.parse(strFileName)
      xmlRoot=xmlContent.getroot()

      xmlTrackpoint=xmlRoot.find('ns0:trk',gkvNamespace)
      if xmlTrackpoint!=None:
         xmlWaypoints=xmlTrackpoint.findall('ns0:trkseg/ns0:trkpt',gkvNamespace)
      else:
         xmlWaypoints=xmlRoot.findall('ns0:wpt',gkvNamespace)

      for xmlWaypoint in xmlWaypoints:
         strXml=xmlDom.tostring(xmlWaypoint,encoding=strElementTreeEncoding,method="xml")
         pt=XmlToPoint(strXml,strPtType)
         objFicCsv.write("\n"+pt.toCsv())

      objFicCsv.close()  
      strReturn=strFileCsv

      strPtLibType="Waypoint"
      if strPtType=="T": strPtLibType="Trackpoint"
      print(len(xmlWaypoints),strPtLibType + "s in/to",strFileCsv)
  
   else:
      print(strFileName,"not found.")

   return strReturn
# ---------------------------------------------------------------------------------------------- 
# extraire de données
def extractFromGpxFile(strFileName,strElementTreeEncoding):
   strReturn=""
   fileName=scriptBaseName()
   arrFileRootExt=os.path.splitext(fileName)
   strConfigFile=arrFileRootExt[0]+".cfg"
   #print(strConfigFile,strElementTreeEncoding)
   boolExtractParameters=False
   floatLatMin=-90.0
   floatLatMax=90.0
   floatLonMin=180.0
   floatLonMax=-180.0
   arrSymWhiteList=[]
   arrSymBlackList=[]

   if os.path.exists(strConfigFile): # parse le fichier de config
      xmlConfigContent=xmlDom.parse(strConfigFile)
      xmlConfigRoot=xmlConfigContent.getroot()

      nodeExtract=xmlConfigRoot.find("extract")
      if nodeExtract != None: 
         boolExtractParameters=True

         # récupère les coordonnées géographiques
         nodeXML=nodeExtract.find("zone")
         if nodeXML != None:
            if nodeXML.find('lat_min') != None:
               if nodeXML.find('lat_min').text != None: floatLatMin=float(nodeXML.find('lat_min').text)

            if nodeXML.find('lat_max') != None:
               if nodeXML.find('lat_max').text != None: floatLatMax=float(nodeXML.find('lat_max').text)

            if nodeXML.find('lon_min') != None:
               if nodeXML.find('lon_min').text != None: floatLonMin=float(nodeXML.find('lon_min').text)

            if nodeXML.find('lon_max') != None:
               if nodeXML.find('lon_max').text != None: floatLonMax=float(nodeXML.find('lon_max').text)

         # constitue la liste des types de points à ne pas inclure dans le fichier final
         nodeXML=nodeExtract.find("types_pt")
         if nodeXML != None:
            nodesXML=nodeXML.findall("type_pt")
            for nodeXML in nodesXML:
               if nodeXML.get('sym') != None and nodeXML.text != None: 
                  if nodeXML.text[0:2]=="no": arrSymBlackList.append(nodeXML.get('sym'))

      if floatLatMin!=0 and floatLatMax!=0 and floatLonMin!=0 and floatLonMax!=0 and os.path.exists(strFileName):
         # vérifie que les valeurs des coordonnées sont réalistes et les rectifie si nécessaire
         if floatLatMin>floatLatMax: 
            floatVal=floatLatMin
            floatLatMin=floatLatMax
            floatLatMax=floatVal

         if floatLonMin>floatLonMax: 
            floatVal=floatLonMin
            floatLonMin=floatLonMax
            floatLonMax=floatVal

         if floatLatMin < -90: floatLatMin=-90
         if floatLatMin > 90: floatLatMin=90
         if floatLatMax < -90: floatLatMax=-90
         if floatLatMax > 90: floatLatMax=90
         if floatLonMin < -180: floatLonMin=-180
         if floatLonMin > 180: floatLonMin=180
         if floatLonMax < -180: floatLonMax=-180
         if floatLonMax > 180: floatLonMax=180

         strTS=datetime.now()
         strTS=strTS.strftime("%Y%m%d%H%M%S")
         strFicGpx=arrFileRootExt[0]+"_extract_"+ strTS +".gpx" # nom du fichier en sortie

         objFicGpx=open(strFicGpx, "w") # raz fichier
         objFicGpx=open(strFicGpx, "a")
         objFicGpx.write(XMLHEADER+"\n")
         objFicGpx.write(GPXROOTNODE%(fileName  +' - '+ str(date.today())))
        
         print("Extracting...") 

         strZone="lat["+str(floatLatMin)+","+str(floatLatMax)+"] ; lon["+str(floatLonMin)+","+str(floatLonMax)+"]"
         objFicGpx.write("\n"+"<metadata><desc>"+strZone+"</desc></metadata>")
                  
         xmlContent=xmlDom.parse(strFileName)
         xmlRoot=xmlContent.getroot()
         xmlWaypoints=xmlRoot.findall('ns0:wpt',gkvNamespace)
         n=len(xmlWaypoints)
         p=0
         i=0
         for xmlWaypoint in xmlWaypoints:
            strXml=xmlDom.tostring(xmlWaypoint,encoding=strElementTreeEncoding,method="xml")
            pt=XmlToPoint(strXml,"W")
            p=p+1
            if float(pt.lat) >= floatLatMin and float(pt.lat) <= floatLatMax and float(pt.lon) >= floatLonMin and float(pt.lon) <= floatLonMax:
               if pt.sym not in arrSymBlackList:
                  i=i+1
                  print(str(int(p/n*100))+"%", pt.toCsv())
                  objFicGpx.write("\n"+pt.toGpx())
                  if pt.sym not in arrSymWhiteList: arrSymWhiteList.append(pt.sym)

         objFicGpx.write("\n"+"</gpx>")
         objFicGpx.close()
         if not boolExtractParameters: print("No extract parameters found.")
         print("Zone:",strZone)
         if len(arrSymBlackList)>0 and len(arrSymWhiteList)>0: print("Sym:",arrSymWhiteList)
         print(i,"elements in/to",strFicGpx)
         strReturn=strFicGpx
      else:
         print("0.0 values or input-file not found.") 

   else:
      print(strConfigFile," not found.")

   return strReturn

def getDefaultConfigContent():
   strContent=XMLHEADER+"\n"
   strContent=strContent+'<config>'+"\n"
   strContent=strContent+'   <extract>'+"\n"
   strContent=strContent+'      <zone>'+"\n"
   strContent=strContent+'         <lat_min>-90.0</lat_min>'+"\n"
   strContent=strContent+'         <lat_max>90.0</lat_max>'+"\n"
   strContent=strContent+'         <lon_min>-180.0</lon_min>'+"\n"
   strContent=strContent+'         <lon_max>180.0</lon_max>'+"\n"
   strContent=strContent+'      </zone>'+"\n"
   strContent=strContent+'      <types_pt>'+"\n"
   strContent=strContent+'         <type_pt type="Airport" sym="Airport">yes</type_pt>'+"\n"
   strContent=strContent+'         <type_pt type="VOR-DME" sym="Navaid, Green">yes</type_pt>'+"\n"
   strContent=strContent+'         <type_pt type="NDB" sym="Navaid, Black">yes</type_pt>'+"\n"
   strContent=strContent+'         <type_pt type="ILS" sym="Pin, Red">yes</type_pt>'+"\n"
   strContent=strContent+'         <type_pt type="FixeA" sym="Triangle, Green">yes</type_pt>'+"\n"
   strContent=strContent+'         <type_pt type="FixeN" sym="Triangle, Blue">no</type_pt>'+"\n"
   strContent=strContent+'         <type_pt type="FixeO" sym="Triangle, Red">no</type_pt>'+"\n"
   strContent=strContent+'      </types_pt>'+"\n"
   strContent=strContent+'   </extract>'+"\n"
   strContent=strContent+'</config>'+"\n"
   return strContent
# ----------------------------------------------------------------------------------------------   
# fonction de test pour parser du XML au format GPX
def parseGPX():
   xmlContent=xmlDom.parse("AIXM_X_IFR_FR.gpx")
   xmlRoot=xmlContent.getroot()
   myNamespace={'ns0':'http://www.topografix.com/GPX/1/0'}
   xmlWaypoints=xmlRoot.findall('ns0:wpt',myNamespace)
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
def main(strFileName,strType="W",strTxtInputFileName=""):
   try:                                
      opts, args = getopt.getopt(sys.argv[1:], "i:c:x:twvd") # ["input", "trackpoint", "waypoint"]

   except getopt.GetoptError:
      print("Parametre(s) non valide(s).")
      sys.exit(2) 

   opt=""
   for opt, arg in opts:
      #print(opt)
      if opt == "-t": strType="T"
      if opt == "-w": strType="W"
      if opt == "-i" or opt == "-c" or opt == "-x": 
         strFileName=arg

   #print(sys.argv[0],sys.argv[1:])
   #print(strType,strFileName)
   strElementTreeEncoding=xmlEltTreeEncoding()

   if opt == "-v": # pour afficher la version du script
      print("version:",SCRIPT_VERSION)
   else:
      if opt == "-d": # pour générer la base de données de référence à partir d'une liste de fichiers CSV connus
         concatCsvFilesToGpxDb(strFilePrefix="FGFS_DATA_")
      elif opt == "-c": # pour convertir un fichier CSV en un fichier GPX
         convertGpxFileToCsvFile(strFileName,strType,strElementTreeEncoding)
      elif opt == "-x": # pour extraire en fonction de coordonnées specifiées dans le fichier de config
         extractFromGpxFile(strFileName,strElementTreeEncoding)
      else: # pour rechercher des points dans la bdd (fonction principale du script)
         chercheWaypointDansGpxEtExporte(strFileName,strType,strTxtInputFileName,strElementTreeEncoding) # type=W (waypoint) ou T (trackpoint)

# ---------------------------------------------------------------------------------------------- 
# lance la procedure principale
if __name__ == "__main__":
    strInputFileName="AIXM_X_IFR_FR.gpx" # fichier par défaut historique (tuto)
    if not os.path.exists(strInputFileName): 
       strInputFileName=scriptBaseName().replace(".py",".dat") # le fichier par défaut est le fichier .dat
    main(strInputFileName)

