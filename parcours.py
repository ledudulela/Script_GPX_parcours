#!/usr/bin/python3
SCRIPT_VERSION=20210416.1700
SCRIPT_AUTHOR="fdz, ctesc356"
# Le script accepte les parametres optionnels suivants:
#  -i fileName  (pour changer de fichier source)
#  -w           (pour exports en waypoints)
#  -t           (pour exports en trackpoints)
import os.path
import sys
import getopt
from xml.etree import ElementTree as xmlDom

# ----------------------------------------------------------------------------------------------------------
class GPoint:
   "Definition d'un point geographique"

   def __init__(self,strType="W",strLat="0.0",strLon="0.0",strName="UNKNOWN",strEle="",strSym="Waypoint"):
      self.type=strType
      self.lat=strLat
      self.lon=strLon
      self.name=strName
      self.ele=strEle
      self.sym=strSym
      #print("type:"+self.type,"name:"+self.name,"lat:"+self.lat,"lon:"+self.lon,"sym:"+self.sym,"ele:"+self.ele)

   def toGpx(self):
      strReturn="<lat>"+self.lat+"</lat>" + "<lon>"+self.lon+"</lon>" + "<name>"+self.name+"</name>" + "<sym>"+self.sym+"</sym>"
      if self.ele != "": strReturn=strReturn+"<ele>"+self.ele+"</ele>"
      strType="wpt"
      if self.type=="T": strType="trkpt"
      strReturn="<"+strType+">" + strReturn + "</"+strType+">"
      return strReturn

   def toCsv(self):
      SEPAR=","
      return self.type + SEPAR + self.lat + SEPAR + self.lon + SEPAR + "\"" + self.sym + "\"" + SEPAR + self.name # self.ele

   def toFgXml(self):
      strReturn=""
      pt=self
      if not pt.sym.find("Airport")==-1: pt.sym="airport"
      if not pt.sym.find("Heliport")==-1: pt.sym="airport"
      if not pt.sym.find("Navaid")==-1: pt.sym="navaid"
      if not pt.sym.find("Triangle")==-1: pt.sym="basic"
      
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
def XmlToPoint(strXML,strType):
   if len(strXML)>0:
      nodeXML=xmlDom.fromstring(strXML)
      #print(nodeXML.tag,nodeXML.attrib)
      pt=GPoint()
      pt.type=strType
      pt.lat=nodeXML.get('lat')
      pt.lon=nodeXML.get('lon')

      if nodeXML.find('name') != None:
         if nodeXML.find('name').text != None: pt.name=nodeXML.find('name').text

      if nodeXML.find('sym') != None:
         if nodeXML.find('sym').text != None: pt.sym=nodeXML.find('sym').text

      if nodeXML.find('ele') != None:
         if nodeXML.find('ele').text != None: pt.ele=nodeXML.find('ele').text
   
      return pt
   else:
      return None

# ----------------------------------------------------------------------------------------------------------
def chercheWaypointDansAixmEtExporte(AixmFileName,strTypePt="W"):
   fileName="parcours"
   fichierTxt=fileName+".txt"
   fichierGpx=fileName+".gpx"
   fichierCsv=fileName+".csv"
   fichierXml=fileName+".xml"

   if os.path.exists(AixmFileName) and os.path.exists(fichierTxt):
      objFicAixm = open(AixmFileName, "r")
      arrAixmFileLines=objFicAixm.readlines()    # charge le fichier bdd
      objFicAixm.close()

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
      for wp in arrTxtFileLines:
         wp=wp.rstrip('\n')   # suppression des lf
         wp=wp.rstrip()
         if len(wp)==0: wp="chainevide"

         r=r+1
      
         ap = wp # pour la recherche des aeroports: "LFLC"
         sym="<sym>Airport"
         if len(wp) == 5:sym="<sym>Triangle" # si 5 car on considere que le pt recherche est un point de report: "ALBER"
   
         na = wp # pour la recherche des navaids : "MEN"
         if len(wp) == 3:
            na="<name>" + na + " "
            sym="<sym>Navaid"
   
         naf = wp # pour la recherche des navaids avec le debut de la frequence mais sans la decimale: "MEN 115"
         if len(wp) == 7:
            naf="<name>" + naf
            sym="<sym>Navaid"

         wp = "<name>" + wp + "</name>"  # pour une recherche a l'identique
      
         for line in arrAixmFileLines: # pour chaque ligne de la bdd XML
            line=line.rstrip('\n')
            if i < 2:
               objFicGpx.write(line)  # recopie des 2 lignes entete GPX
               objFicGpx.write("\n")
               i=i+1

               if i==2: 
                  objFicCsv.write("type,latitude,longitude,sym,name")  #ecriture des entetes
                  objFicCsv.write("\n")

                  objFicXml.write("<?xml version=\"1.0\"?><PropertyList><route>")  #ecriture entete
                  objFicXml.write("\n")

                  if strTypePt=="T":
                     objFicGpx.write("<trk><trkseg>")  #ecriture entete
                     objFicGpx.write("\n")


            elif wp in line or (ap in line and sym in line) or (na in line and sym in line) or (naf in line and sym in line) :
               print(line)
               pt=XmlToPoint(line,strTypePt)
               if pt != None: 
                  line=pt.toGpx()
                  objFicGpx.write(line) #ecriture ligne
                  objFicGpx.write("\n")

                  line=pt.toCsv()
                  objFicCsv.write(line) # ecriture ligne
                  objFicCsv.write("\n")

                  line=pt.toFgXml()
                  objFicXml.write(line) # ecriture ligne
                  objFicXml.write("\n")
	   
               t=t+1
               break

      if strTypePt=="T":
         objFicGpx.write("</trkseg></trk>")  #ecriture fermeture entete
         objFicGpx.write("\n")
      objFicGpx.write("</gpx>")    #ligne fin
      objFicGpx.close()

      objFicXml.write("</route></PropertyList>")    #ligne fin
      objFicXml.close()

      objFicCsv.close()
   
      print("End: "+str(t)+"/"+str(r)+" waypoints.")

# ----------------------------------------------------------------------------------------------   
def parseAIXM():
   xmlContent=xmlDom.parse("AIXM_X_IFR_FR.gpx")
   xmlRoot=xmlContent.getroot()
   xmlWaypoints=xmlRoot.findall('wpt') #  xmlns:gpx= {http://www.topografix.com/GPX/1/0}
   print(len(xmlWaypoints))
   i=0
   for xmlWaypoint in xmlWaypoints:
      i=i+1
      strXml=xmlDom.tostring(xmlWaypoint,encoding="unicode",method="xml")
      pt=XmlToPoint(strXml,"W")
      print(i, pt.toCsv()) # xmlWaypoint

# ---------------------------------------------------------------------------------------------- 
def main(strFileName,strType="W"):
   try:                                
      opts, args = getopt.getopt(sys.argv[1:], "i:tw") # ["input", "trackpoint", "waypoint"]

   except getopt.GetoptError:
      print("Parametre(s) non valide(s).")
      sys.exit(2) 

   for opt, arg in opts:
      #print(opt)
      if opt == "-t": strType="T"
      if opt == "-w": strType="W"
      if opt == "-i": 
         strFileName=arg

   #print(sys.argv[0],sys.argv[1:])
   #print(strType,strFileName)
   chercheWaypointDansAixmEtExporte(strFileName,strType) # type=W (waypoint) ou T (trackpoint)

# ---------------------------------------------------------------------------------------------- 
# lance la procedure principale
if __name__ == "__main__":
    main("AIXM_X_IFR_FR.gpx")


