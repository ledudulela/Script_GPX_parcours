#!/usr/bin/python3
# -*- coding: UTF-8 -*-
SCRIPT_VERSION=20210507.2247
SCRIPT_AUTHOR="ledudulela"
L_FR="FR"
L_EN="EN"
LOCALE=L_FR # choose your LOCALE
# interface graphique du script de même nom en ligne de commandes. 
# Nécessite le package python3-tk si exécution avec python3 sinon python-tk 
#
# What's new in this version:
#  - Ajout du menu Application > Aide...
#  - Sauvegarde du contenu dans un fichier systématiquement en UTF-8
#  - Ajout du menu Tools > Convertir du CSV en GPX
#  - amélioration du Tool > Correction du bearing géographique / magnétique
#   avec les paramètres [w o e - + t]  pris en charge ( remplace E par le signe - )
#   e correspond à -
#   w, o correspondent à +
#   t donnera les coordonnées des points aux extrémités de la tangente du segment, idéal pour arc-dme
#     s'utilise sur les radiales, en ajoutant la lettre t, par exemple: w20t
#   longueur de la demi-tangente redéfinie à L*sin(5)
#
from sys import argv as argv
import math
import re
#from functools import partial

# importe le script de commandes
moduleCmd=argv[0].replace("_ui","")
moduleCmd=moduleCmd.replace(".py","")
moduleCmd=moduleCmd.replace("./","")
cmd=__import__(moduleCmd) # import moduleCmd as cmd

if cmd.sys.version_info.major<3:
   import Tkinter as tk
   import tkMessageBox as msgbox
   import tkFileDialog
   import tkSimpleDialog as inputbox
else:
   import tkinter as tk
   from tkinter import messagebox as msgbox
   import tkinter.filedialog as tkFileDialog
   from tkinter import simpledialog as inputbox


REGEXCSV='(?!\B"[^"]*),(?![^"]*"\B)'
   
def i18n(strKey):
   if not(LOCALE==L_FR or LOCALE==L_EN): LOCALE==L_EN
   mapping={
      "mnuApp":{L_FR:"Application",L_EN:"Application"},
      "mnuAppShowConfig":{L_FR:"Afficher la configuration", L_EN:"Display configuration"},
      "mnuAppSaveConfig":{L_FR:"Sauvegarder la configuration", L_EN:"Save configuration"},
      "mnuAppResetConfig":{L_FR:"Réinitialiser la configuration", L_EN:"Reset configuration"},
      "mnuAppOpenFile":{L_FR:"Ouvrir un fichier...", L_EN:"Open file..."},
      "mnuAppSaveContentAs":{L_FR:"Enregistrer le contenu...", L_EN:"Save content..."},
      "mnuAppHelp":{L_FR:"Aide...", L_EN:"Help..."}, 
      "mnuAppAbout":{L_FR:"À propos...", L_EN:"About..."}, 
      "mnuAppExit":{L_FR:"Quitter", L_EN:"Exit"}, 
      "mnuData":{L_FR:"B.D.D",L_EN:"D.B"},
      "mnuDataShowDBFile":{L_FR:"Ouvrir la sélection", L_EN:"Open selection"},
      "mnuDataConvertDBFileToCSV":{L_FR:"Convertir en CSV",L_EN:"Convert in CSV"},
      "mnuDataExtractDBFile":{L_FR:"Extraire une zone...",L_EN:"Extract a zone..."}, 
      "mnuDataSaveAsDBFileList":{L_FR:"Enregistrer sous...", L_EN:"Save as..."},
      "mnuDataDeleteDBFile":{L_FR:"Supprimer...", L_EN:"Delete..."},
      "mnuDataRefreshDBFileList":{L_FR:"Actualiser la liste", L_EN:"Refresh list"},
      "mnuSearch":{L_FR:"Recherche",L_EN:"Search"},
      "mnuSearchSearch":{L_FR:"Rechercher les points", L_EN:"Search points"},
      "mnuSearchShowCSV":{L_FR:"Afficher en CSV", L_EN:"Show in CSV"},
      "mnuSearchShowGPX":{L_FR:"Afficher en GPX", L_EN:"Show in GPX"},
      "mnuSearchShowXML":{L_FR:"Afficher en XML", L_EN:"Show in XML"},
      "mnuSearchShowLog":{L_FR:"Afficher le Log", L_EN:"Show Log"},
      "mnuTools":{L_FR:"Outils",L_EN:"Tools"},
      "mnuToolsDist2Points":{L_FR:"Ajouter Distance & Bearing", L_EN:"Add Distance & Bearing"},
      "mnuToolsCoordByBearingDist":{L_FR:"Coord. à partir de: lat,lon, dist,bearing", L_EN:"Coord. from: lat,lon, dist,bearing"},
      "mnuToolsMagnetDeclin":{L_FR:"Correction du bearing géo./magnét.", L_EN:"Geo./Magnet. bearing correction"},
      "mnuToolsConvertCsvToGpx":{L_FR:"Convertir le CSV en GPX", L_EN:"Convert CSV to GPX"},
      "mnuToolsReplaceBlankRowsByHeader":{L_FR:"Remplacer les lignes vierges par l'entête", L_EN:"Replace blank rows by header"},
      "btnAppQuit":{L_FR:"Quitter",L_EN:"Quit"},
      "btnSearchSearch":{L_FR:"Rechercher",L_EN:"Search"},
      "btnToolsDist2Points":{L_FR:"+ Dist. & Bear.",L_EN:"+ Dist. & Bear."},
      "btnToolsCoordByBearingDist":{L_FR:"Coord. Pt dist.",L_EN:"Coord. dist. Pt"},
      "btnToolsMagnetDeclin":{L_FR:"Géo. / Magnét.",L_EN:"Geo. / Magnet."},
      "PopText_close":{L_FR:"[x]",L_EN:"[x]"},
      "PopText_copy":{L_FR:"Copier",L_EN:"Copy"},
      "PopText_cut":{L_FR:"Couper",L_EN:"Cut"},
      "PopText_past":{L_FR:"Coller",L_EN:"Past"},
      "PopText_select_row":{L_FR:"Sélectionner la ligne",L_EN:"Select row"},
      "PopText_insert_row":{L_FR:"Insérer une ligne",L_EN:"Insert row"},
      "PopText_select_all":{L_FR:"Tout sélectionner",L_EN:"Select all"},
      "PopText_rows_count":{L_FR:"Nbr de lignes...",L_EN:"Nb rows..."},
      "lblInfoLib1":{L_FR:"Base de données",L_EN:"Database"},
      "frmChoixType":{L_FR:"Points à rechercher",L_EN:"Points to search"},
      "lblInfoLib2":{L_FR:"Veuillez patentier",L_EN:"Please wait"},
      "mnuAppHelp_msg_filenotfound":{L_FR:"Fichier introuvable.",L_EN:"File not found."},
      "mnuDataExtractDBFile_msg_info_extract":{L_FR:"Veuillez afficher, modifier et sauvegarder les paramètres de configuration avant de lancer une extraction.",L_EN:"Please open, modify and save configuration parameters before extraction."},
      "mnuToolsDist2Points_msg_info_err":{L_FR:"Format de données non valide.\nCSV sans entêtes lat,lon ou dist,bearing déjà présents.",L_EN:"Bad data format\nCSV without lat,lon header or dist,bearing already exist."},
      "mnuToolsCoordByBearingDist_msg_info_err":{L_FR:"Format de données non valide.\nCSV sans entêtes lat,lon,dist,bearing.",L_EN:"Bad data format\nCSV without lat,lon,dist,bearing header."},
      "mnuToolsMagnetDeclin_msg_info_err":{L_FR:"Format de données non valide.\nCSV sans entêtes lat,lon,dist,bearing.",L_EN:"Bad data format\nCSV without lat,lon,dist,bearing header."},
      "os_msg_open_file":{L_FR:"Ouvrir un fichier",L_EN:"Open file"},
      "os_msg_delete_file":{L_FR:"Supprimer le fichier",L_EN:"Delete file"},
      "os_msg_save_db_as":{L_FR:"Enregistrer la BDD sous",L_EN:"Save DB as"}, 
      "os_msg_save_content_as":{L_FR:"Enregistrer le contenu sous",L_EN:"Save content as"},
      "inputboxMagnetDeclinValue":{L_FR:"Valeur à ajouter",L_EN:"Value to add"},
      "dummy":{L_FR:"In French", L_EN:"In English"}
   }
   return mapping[strKey][LOCALE]

class PopText(tk.Text,tk.Tk): # classe surchargée pour afficher un popup-menu sur un tk.Text
    # source https://stackoverflow.com/questions/12014210/tkinter-app-adding-a-right-click-context-menu
    # Comportement particulier, il faut maintenir le clic-droit pour sélectionner une option du sous-menu
    
    def __init__(self,parentTkWindow):
        tk.Text.__init__(self)
        TAB="  "
        self.parentWindow=parentTkWindow # permet de connaitre la fenetre parent pour l'utilisation du clipboard
        self.popup_menu = tk.Menu(self, tearoff=0)   
        self.popup_menu.add_command(label=i18n("PopText_close"), command=self.close)
        #self.popup_menu.add_separator()
        self.popup_menu.add_command(label=TAB+i18n("PopText_copy"), command=self.copy)
        self.popup_menu.add_command(label=TAB+i18n("PopText_cut"), command=self.cut)
        self.popup_menu.add_command(label=TAB+i18n("PopText_past"), command=self.past)
        self.popup_menu.add_separator()
        self.popup_menu.add_command(label=TAB+i18n("PopText_select_row"), command=self.select_row)
        self.popup_menu.add_command(label=TAB+i18n("PopText_insert_row"), command=self.insert_row)
        self.popup_menu.add_separator()
        self.popup_menu.add_command(label=TAB+i18n("PopText_select_all"), command=self.select_all)
        self.popup_menu.add_separator()
        self.popup_menu.add_command(label=TAB+i18n("PopText_rows_count"), command=self.rows_count)
        # bind event on right_click
        self.bind("<Button-3>", self.popup) # Button-2 on Aqua
        self.bind("<KeyRelease-KP_Enter>",self.kp_enter_release) # <KeyRelease> -KP_Enter

    def curPos(self):
       # current Cursor Position
       return self.index(tk.INSERT)

    def curPosRowStartEnd(self):
       # renvoie start,end de ligne de la sélection
       index=self.curPos()
       strRow=index.split(".")[0]
       start=strRow+".0"
       end=strRow+".end"
       return start,end
    
    def hasSelection(self):
       return self.tag_ranges("sel")

    def popup(self, event):
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.popup_menu.grab_release()

    def kp_enter_release(self, event):
       # insère une ligne vierge après la position courante
       try:
          self.insert(self.curPos(), "\n")        
       finally:
          pass

    def close(self):
       # ferme le popup-menu
       pass

    def copy(self):
       # copie la sélection dans le clipboard
       if self.hasSelection(): # selection exists
          self.parentWindow.clipboard_clear()  # clear clipboard-contents
          self.parentWindow.clipboard_append(self.selection_get()) # copy selection in clipboard

    def past(self):
       # colle le clipboard-contents à la currentCursorPosition
       self.insert(self.curPos(), self.parentWindow.clipboard_get())

    def cut(self):
       # si la sélection est une chaine, copie la chaine dans le clipboard et coupe la chaine.
       # si la sélection est une ligne vierge, supprime la ligne
       if self.hasSelection(): # si selection existe alors coupe la chaine
          strContent=self.get(tk.SEL_FIRST,tk.SEL_LAST)
          if len(strContent)>0:
             self.copy() 
             self.delete(tk.SEL_FIRST,tk.SEL_LAST)
       else: # la sélection est une ligne vierge, supprime la ligne
          start,end=self.curPosRowStartEnd()
          strRowContent=self.get(start,end)
          if len(strRowContent)==0: self.delete_row()

    def select_all(self):
       # sélectionne toutes les lignes
       self.tag_add(tk.SEL, "1.0", tk.END)
       self.mark_set(tk.INSERT, "1.0")
       self.see(tk.INSERT)
       return 'break'

    def insert_row(self):
       # insère une ligne vierge avant la ligne courante
       self.insert('current linestart', "\n")

    def delete_row(self):
       # supprime la ligne
       self.delete('current linestart', 'current lineend+1c')
       #return "break" uncomment if you want to disable selection by double-clicking

    def select_row(self):
       # sélectionne le texte de la ligne
       start,end=self.curPosRowStartEnd()
       self.tag_add(tk.SEL,start,end)

    def rows_count(self):
       # comptabilise le nbr de lignes
       intNbrLignes=self.index('end-1c').split('.')[0]
       strChaine="Nbr de lignes: "+str(intNbrLignes)
       msg(strChaine)

    def delete_last_blank_rows(self):
      # supprime les lignes vierges en fin
      intNbrLignes=int(self.index('end-1c').split('.')[0])
      if intNbrLignes>1:
         for i in range(intNbrLignes-1, -1, -1):
            strRow=str(i)
            start=strRow+".0"
            end=strRow+".end+1c"
            strContent=self.get(start,end)
            #print(start,end,strContent,str(len(strContent)))
            if len(strContent)==1: 
               self.delete(start,end)
            else:
               break

# -------------------------------------------------------------------------------
def msg(strTexte):
      msgbox.showinfo(moduleCmd, strTexte)

def isNumeric(strValue):
   return re.match('^[0-9\.\-]*$',strValue)

def loopBearing(bearing):
   newBear=bearing
   if newBear>=360: newBear=newBear-360
   if newBear<0: newBear=360+newBear
   return newBear
# -------------------------------------------------------------------------------
def csvCommaIsInString(strString):
   # renvoie True si la chaine contient une virgule
   boolReturn=(strString.find(',')>0)
   return boolReturn

def csvLineToArray(strCsvLine):
   # renvoie un tableau de valeurs de la chaine CSV.
   # renvoie None si la chaine ne contient pas de virgule.
   arrCols=None
   if csvCommaIsInString(strCsvLine): 
      arrCols=re.split(r'(?!\B"[^"]*),(?![^"]*"\B)',strCsvLine,flags=re.IGNORECASE)
   return arrCols

def csvIndexOfCol(strCsvHeader,strSearchColName):
   # renvoie l'index de la colonne recherchée dans l'entête CSV.
   # renvoie None si le nom de la colonne recherchée ne s'y trouve pas.
   p=None
   i=0
   arrCols=csvLineToArray(strCsvHeader)
   strSearchValue=strSearchColName
   if not arrCols is None:
      for strCol in arrCols:
         if strCol[0:3]==strSearchValue[0:3]: # prend que la partie gauche pour palier à lat/latitude et lon/longitude
            p=i
         i=i+1         
   return p

def csvIsGpxHeader(strHeader,strSearchTerm=""):
   # renvoie True si trouve la chaine "lat,lon" dans strHeader,
   # si strSearchTerm est spécifié, recherchera, en plus, la présence de ce terme dans strHeader
   boolReturn=False
   if not strHeader.find('lat,lon')==-1 or not strHeader.find('latitude,lon')==-1:
      if strSearchTerm=="":
         boolReturn=True
      else:
         if not strHeader.find(strSearchTerm+",")==-1 or not strHeader.find(","+strSearchTerm)==-1 :
            boolReturn=True
   return boolReturn

def csvIsGpxRowOfValues(strLine):
   # renvoie True si strLine ne contient pas d'entêtes et donc, 
   # dans ce cas, strLine contient des valeurs séparées par une virgule
   boolReturn=False
   if csvCommaIsInString(strLine) and not csvIsGpxHeader(strLine):
      boolReturn=True
   return boolReturn

def csvJoinStdValues(strType,lat,lon,strSym,strName):
   strCSV=strType+","+str(lat)+","+str(lon)+","+strSym+","+strName
   return strCSV

def csvJoinValues(strType,lat,lon,strSym,strName,dist,bearing):
   strCSV=csvJoinStdValues(strType,lat,lon,strSym,strName)+","+str("%.2f"%dist)+","+str("%.2f"%bearing)
   return strCSV

def csvJoinStrings(strType,strLat,strLon,strSym,strName,strDist="",strBearing=""):
   if len(strDist)>0: strDist=","+strDist
   if len(strBearing)>0: strBearing=","+strBearing
   strCSV=strType+","+strLat+","+strLon+","+strSym+","+strName + strDist + strBearing
   return strCSV
# -------------------------------------------------------------------------------
def distNmBetween2Points(floatLat1,floatLon1,floatLat2,floatLon2):
   lat1 = floatLat1 * math.pi/180
   lat2 = floatLat2 * math.pi/180
   dlon = (floatLon2-floatLon1) * math.pi/180
   R = 6371010/1852
   dNm = math.acos(math.sin(lat1)*math.sin(lat2) + math.cos(lat1)*math.cos(lat2) * math.cos(dlon)) * R;
   return dNm

def distNmBetween2PointsBis(floatLat1,floatLon1,floatLat2,floatLon2):
   # autre methode de calcul
   distance=0
   if floatLat1==floatLat2:
      distance=60 * math.fabs(floatLon1-floatLon2) * math.cos(math.radians(floatLat1))
   else:
      tempo=math.atan( math.fabs(floatLon1-floatLon2) / math.fabs(floatLat1-floatLat2) * math.cos(math.radians(math.fabs(floatLat1+floatLat2))/2) )
      distance=math.fabs(floatLat1-floatLat2) / math.cos(tempo) *60
   return distance

def bearingBetween2Points(floatLat1,floatLon1,floatLat2,floatLon2):
   lat1=math.radians(floatLat1)
   lon1=math.radians(floatLon1)
   lat2=math.radians(floatLat2)
   lon2=math.radians(floatLon2)
   dLon=lon2-lon1
   Y=math.sin(dLon) * math.cos(lat2)
   X=math.cos(lat1)*math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dLon)
   bearing=math.degrees(math.atan2(Y,X))
   if bearing<0: bearing=bearing+360
   return bearing


def pointRadialDistance(lat1, lon1, bearing, distance):
    """
    Return final coordinates (lat2,lon2) [in degrees] given initial coordinates
    (lat1,lon1) [in degrees] and a bearing [in degrees] and distance [in NM]
    """
    rEarth = 6371.010 # Earth's average radius in km
    epsilon = 0.000001 # threshold for floating-point equality

    rlat1 = math.radians(lat1)
    rlon1 = math.radians(lon1)
    rbearing = math.radians(bearing)
    rdistance = distance *1.852 / rEarth # normalize linear distance to radian angle  / 1.852 

    rlat2 = math.asin( math.sin(rlat1) * math.cos(rdistance) + math.cos(rlat1) * math.sin(rdistance) * math.cos(rbearing) )

    #if math.cos(rlat1) == 0 or math.fabs(math.cos(rlat1)) < epsilon: # Endpoint a pole
    #    rlon2=rlon1
    #else:
    #    rlon2 = ((rlon1 - math.asin( math.sin(rbearing)* math.sin(rdistance) / math.cos(rlat1) ) + math.pi ) % (2*math.pi) ) - math.pi

    if ((math.cos(rlat2) == 0) and (math.fabs(math.cos(rlat2)) < epsilon)):
       rlon2 = rlon1;
    else:
       rlon2 = rlon1 + math.atan2(math.sin(rbearing) * math.sin(rdistance) * math.cos(rlat1), math.cos(rdistance) - math.sin(rlat1) * math.sin(rlat2));

    lat = math.degrees(rlat2)
    lon = math.degrees(rlon2)
    return (lat, lon)

def cheminFichier(): # renvoie le nom du script "ligne de commandes" sans l'extension. exemple: "parcours"
   fileName=cmd.scriptBaseName()
   arrFileRootExt=cmd.os.path.splitext(fileName)
   fileName=arrFileRootExt[0] 
   return fileName

def cheminFichierTexte():
   return cheminFichier()+".txt"

def cheminFichierCSV():
   return cheminFichier()+".csv"

def cheminFichierGPX():
   return cheminFichier()+".gpx"

def cheminFichierXML():
   return cheminFichier()+".xml"

def cheminFichierLOG():
   return cheminFichier()+".log"

def cheminFichierConfig():
   return cheminFichier()+".cfg"


def cheminFichierDB(): # renvoie le nom du fichier sélectionné et stocké dans le champ dédié
   fichier=lblSourceFilename['text']
   return fichier


def setContenuFichier(cheminFichier,strContenu): # fonction générique, écrit le contenu dans le fichier
   objFic = open(cheminFichier, "w")
   objFic = open(cheminFichier, "a")
   objFic.write(strContenu.rstrip("\n"))   # sauvegarde le fichier
   objFic.close()


def setContenuFichierTexte(strContenu): # écrit le contenu dans le fichier texte
   fichier=cheminFichierTexte()
   setContenuFichier(fichier,strContenu)


def setContenuFichierConfig(strContenu): # écrit le contenu dans le fichier de config
   fichier=cheminFichierConfig()
   setContenuFichier(fichier,strContenu)


def getContenuFichier(strCheminFichier): # fonction générique, renvoie le contenu du fichier
   strReturn=""
   if strCheminFichier!="":
      if cmd.os.path.exists(strCheminFichier):
         objFic = open(strCheminFichier, "r")
         strReturn=objFic.read()   # charge le fichier 
         objFic.close()
   return strReturn


def getContenuFichierTexte(): # renvoie le contenu du fichier texte
   strReturn=getContenuFichier(cheminFichierTexte())
   return strReturn 


def getContenuFichierCSV(): # renvoie le contenu du fichier CSV
   strReturn=getContenuFichier(cheminFichierCSV())
   return strReturn


def getContenuFichierGPX(): # renvoie le contenu du fichier GPX
   strReturn=getContenuFichier(cheminFichierGPX())
   return strReturn

def getContenuFichierXML(): # renvoie le contenu du fichier XML
   strReturn=getContenuFichier(cheminFichierXML())
   return strReturn


def getContenuFichierLOG(): # renvoie le contenu du fichier LOG
   strReturn=getContenuFichier(cheminFichierLOG())
   return strReturn


def getContenuFichierConfig():  # renvoie le contenu du fichier Config
   strReturn=getContenuFichier(cheminFichierConfig())
   return strReturn


def getContenuFichierDB():  # renvoie le contenu du fichier DB
   strReturn=getContenuFichier(cheminFichierDB())
   return strReturn


def displayContent(strContent): # affiche la chaine dans le champ dédié
   txtDisplayContent.delete("1.0", tk.END)
   txtDisplayContent.insert("1.0",strContent)

def getDisplayContent():
   return txtDisplayContent.get("1.0", tk.END)

def getTrimDisplayContentArray():
   txtDisplayContent.delete_last_blank_rows()
   strContenu=getDisplayContent()+"\n"
   arrContenu=strContenu.split("\n")
   return arrContenu

def setCurrentFichierDB(strFileName): # affiche le nom de fichier sélectionné dans le champ dédié
   lblSourceFilename['text']=strFileName

def lstFichiersOnSelect(event): # évènement de sélection d'un elt dans la liste des fichiers
   if event.widget.curselection():
      setCurrentFichierDB(event.widget.get(event.widget.curselection()))

def lstFichiersInit(strSelectedFile=""): # initialise la liste des fichiers
   arrFiles=cmd.os.listdir('.')
   arrExt=('.dat','.gpx')
   i=0
   s=0
   arrFiles.sort()
   for file in arrFiles:
      if cmd.os.path.splitext(file)[1] in arrExt:
         lstFichiers.insert(i, file)
         if strSelectedFile!="":
            if strSelectedFile == file: s=i
         i=i+1
   #lstFichiers.config(yscrollcommand=scrollVFichiers.set)
   lstFichiers.select_set(s)
   lstFichiers.event_generate("<<ListboxSelect>>")

def lstFichiersRefresh(strSelectedFile=""): # rafrachit la liste des fichiers
   lstFichiers.delete(0,tk.END)
   lstFichiersInit(strSelectedFile)

def pleaseWaitOn():
   lblInfoLib2['text']=i18n("lblInfoLib2")+"..."
   lblInfoLib2.master.update()
   #msgbox.showinfo('Info',lblInfoLib2['text'])

def pleaseWaitOff():
   lblInfoLib2['text']=""

def rbtnTypeOnChange():
   # si le contenu est en CSV, change le type de point pour chaque ligne du CSV en fonction du choix utilisateur 
   strNewType=strRbtnTypeId.get()

   strFoundType="T"
   if strNewType=="T": strFoundType="W"
   strNewType=strNewType+","
   strFoundType=strFoundType+","

   strContenu=getDisplayContent()+"\n"
   arrContenu=strContenu.split("\n")
   strContenu=""

   i=0
   for strLine in arrContenu:
      i=i+1
      if len(strLine)>2: 
         if strLine[0:2]==strFoundType:
            txtDisplayContent.delete(str(i)+".0",str(i)+".2")
            txtDisplayContent.insert(str(i)+".0",strNewType)

#-----------------------------------
# fonctions de la barre de menus
#-----------------------------------
def mnuAppShowConfigOnClick():
   strContent=getContenuFichierConfig()
   if strContent=="":
      strContent=cmd.getDefaultConfigContent()
      setContenuFichierConfig(strContent)
      strContent=getContenuFichierConfig() # recharge le fic pour s'assurer de la bonne prise en compte
   displayContent(strContent)

def mnuAppSaveConfigOnClick():
   strContent=getDisplayContent()
   setContenuFichierConfig(strContent)

def mnuAppResetConfigOnClick():
   strContent=cmd.getDefaultConfigContent()
   displayContent(strContent)

def mnuAppOpenFileOnClick():
   arrTypesFiles=[('csv file','.csv'),('gpx file','.gpx'),('data file','.dat'),('xml file','.xml'),('txt file','.txt')]
   strFilename=tkFileDialog.askopenfilename(title=i18n("os_msg_open_file"),filetypes=arrTypesFiles)
   if strFilename:
      strContenu=getContenuFichier(strFilename)
      displayContent(strContenu)

def mnuAppSaveContentAsOnClick():
   arrTypesFiles=[('all files','.*'),('csv file','.csv'),('gpx file','.gpx'),('data file','.dat'),('xml file','.xml'),('txt file','.txt')]
   #strDefaultExt=".gpx"
   strFilename=tkFileDialog.asksaveasfilename(title=i18n("os_msg_save_content_as"),filetypes=arrTypesFiles)
   if strFilename:
      strContenu=getDisplayContent()
      if cmd.sys.version_info.major<3: strContenu=strContenu.encode("utf-8")
      setContenuFichier(strFilename,strContenu)
      strFilename=cmd.os.path.split(strFilename)[1]
      lstFichiersRefresh(strFilename)

def mnuAppHelpOnClick():
   strFilename=argv[0].replace(".py","")  + "_help_" + LOCALE.lower()+".txt"
   if cmd.os.path.exists(strFilename):
      strContenu=getContenuFichier(strFilename)
      displayContent(strContenu)
   else:
      msg(i18n("mnuAppHelp_msg_filenotfound") + "\n"+strFilename )

def mnuAppAboutOnClick():
   msg("Version: "+str(SCRIPT_VERSION))


def mnuDataShowDBFileOnClick():
   strContent=getContenuFichierDB()
   displayContent(strContent)

def mnuDataExtractDBFileOnClick():
   if txtDisplayContent.search("<extract>","1.0",stopindex=tk.END):
      strElementTreeEncoding=cmd.xmlEltTreeEncoding()
      strFileName=cheminFichierDB()
      pleaseWaitOn()
      strNewFileName=cmd.extractFromGpxFile(strFileName,strElementTreeEncoding)
      pleaseWaitOff()
      if strNewFileName!="":
         # refresh liste fichiers
         lstFichiersRefresh(strNewFileName)
         mnuDataShowDBFileOnClick()
   else:
      msgbox.showinfo('Info',i18n("mnuDataExtractDBFile_msg_info_extract"))

def mnuDataConvertDBFileToCSVOnClick():
      strElementTreeEncoding=cmd.xmlEltTreeEncoding()
      strFileName=cheminFichierDB()
      strPtType=strRbtnTypeId.get()
      pleaseWaitOn()
      strFileName=cmd.convertGpxFileToCsvFile(strFileName,strPtType,strElementTreeEncoding)
      pleaseWaitOff()
      if strFileName!="":
         strContent=getContenuFichier(strFileName)
         displayContent(strContent)

def mnuDataRefreshDBFileListOnClick():
   lstFichiersRefresh()

def mnuDataSaveAsDBFileListOnClick():
   arrTypesFiles=[('all files','.*'),('csv file','.csv'),('gpx file','.gpx'),('data file','.dat'),('xml file','.xml'),('txt file','.txt')]
   #strDefaultExt=".gpx"
   strFilename=tkFileDialog.asksaveasfilename(title=i18n("os_msg_save_db_as"),filetypes=arrTypesFiles,initialfile=cheminFichierDB())
   if strFilename:
      strContenu=getContenuFichier(cheminFichierDB())
      setContenuFichier(strFilename,strContenu)
      strFilename=cmd.os.path.split(strFilename)[1]
      lstFichiersRefresh(strFilename)

def mnuDataDeleteDBFileOnClick():
   strFileName=cheminFichierDB()
   if msgbox.askyesno("Question",i18n("os_msg_delete_file")+" %s ?"%strFileName):
      if cmd.os.path.exists(strFileName):
         cmd.os.remove(strFileName)
         lstFichiersRefresh()
         displayContent(" ")


def mnuSearchSearchOnClick():
    #msgbox.showinfo('Info', 'Effacement du champ résultat')
    txtDisplayContent.delete("1.0", tk.END)

    #msgbox.showinfo('Info', 'Enregistrement du fichier texte')
    strContent=txtContenuFichierTexte.get("1.0", tk.END)
    setContenuFichierTexte(strContent)

    #msgbox.showinfo('Info', 'Recherche en cours...')
    pleaseWaitOn()
    strType=strRbtnTypeId.get()
    strCheminFichierSource=cheminFichierDB()
    cmd.main(strCheminFichierSource,strType,strTxtInputFileName=cheminFichierTexte())
    pleaseWaitOff()

    #msgbox.showinfo('Info', 'Afficher le résultat')
    strContent=getContenuFichierCSV()
    displayContent(strContent)

def mnuSearchShowCSVOnClick():
   strContent=getContenuFichierCSV()
   displayContent(strContent)

def mnuSearchShowGPXOnClick():
   strContent=getContenuFichierGPX()
   displayContent(strContent)

def mnuSearchShowXMLOnClick():
   strContent=getContenuFichierXML()
   displayContent(strContent)

def mnuSearchShowLogOnClick():
   strContent=getContenuFichierLOG()
   displayContent(strContent)


def mnuToolsDist2PointsOnClick():
   # calcule la distance entre deux points consécutifs
   strEntetesCSV=""
   colLat=0
   colLon=0
   i=0
   p=0

   floatPreviousLat=0.0
   floatPreviousLon=0.0
   floatLat=0.0
   floatLon=0.0

   floatDistance=0.0
   floatBearing=0.0
   boolPrevious=False
   intLOL=0
   strEOL='1.end'

   NEWCOLS="dist,bearing"   

   arrContenu=getTrimDisplayContentArray()

   # recherche la position des colonnes lat et lon
   if len(arrContenu[0])>0:
      strLine=arrContenu[0].strip()
      if csvIsGpxHeader(strLine) and not (csvIsGpxHeader(strLine,"dist") or csvIsGpxHeader(strLine,"bearing")):
         colLat=csvIndexOfCol(strLine,"lat")
         colLon=csvIndexOfCol(strLine,"lon")

   if colLon==0: # avertissement si la col Lon n'a pas été trouvée
      msg(i18n("mnuToolsDist2Points_msg_info_err"))
   else:
      txtDisplayContent.insert(tk.END,"\n"+"\n") # ajoute 2 lignes vierges en fin avant d'afficher le résultat
      for strLine in arrContenu:
         i=i+1
         strLine=strLine.strip()
         intLOL=len(strLine) # longueur de la ligne
         if intLOL>0:
            strValue=""
            strEOL=str(i)+'.end' # ou alors str(i)+"."+str(intLOL) pour la posi de fin de ligne
            
            if csvIsGpxHeader(strLine): # si les noms de colonnes obligatoires se trouvent dans la ligne...
               strValue=NEWCOLS
               boolPrevious=False

            else: 
               arrValues=csvLineToArray(strLine)
               floatLat=float(arrValues[colLat])
               floatLon=float(arrValues[colLon])
               
               if boolPrevious:
                  # calculs distance et bearing
                  floatDistance=distNmBetween2Points(floatPreviousLat,floatPreviousLon,floatLat,floatLon) 
                  floatBearing=bearingBetween2Points(floatPreviousLat,floatPreviousLon,floatLat,floatLon)
               else:
                  # pas de calcul, valeurs à 0
                  floatDistance=0.0
                  floatBearing=0.0

               boolPrevious=True
               floatPreviousLat=floatLat
               floatPreviousLon=floatLon

               # concat les valeurs dans la chaine à afficher
               strValue=str("%.2f"%floatDistance)+","+str("%.2f"%floatBearing)
            
            # ajoute la chaine en fin de ligne
            #txtDisplayContent.insert(strEOL,","+strValue)

            txtDisplayContent.insert(tk.END,"\n"+strLine+","+strValue)

      txtDisplayContent.delete_last_blank_rows()

def mnuToolsCoordByBearingDistOnClick():
   # calcule les coordonnées d'un point à partir d'un point existant, d'une distance et d'un bearing
   # Calculating coordinates given a bearing and a distance
   l=0
   i=0
   n=0
   p=0
   boolContinue=True
   boolTrouve=False
   iType=None
   iLat=0
   iLon=1
   iSym=None
   iName=None
   iDist=2
   iBear=3
   strType=""
   strSym=""
   strName=""
   strResult=""
# soit il n'y a pas l'entête CSV et dans ce cas on attent uniquement les valeurs sur la première ligne:
#   lat,lon,dist,bearing
# soit il y a les entêtes et on attend deux lignes ordonnées ainsi avec les valeurs sur la 2ème ligne:
#   lat,lon,dist,bearing
#   -21.31,55.41,15.00,270.00
# ou
#   type,latitude,longitude,sym,name,dist,bearing
#   T,-21.31,55.41,"Airport",[FMEP],15.00,270.00


   arrContenu=getTrimDisplayContentArray()
   if len(arrContenu)>0:
      strLine=arrContenu[0]

      if csvIsGpxHeader(strLine):
         if csvIsGpxHeader(strLine,"dist") and csvIsGpxHeader(strLine,"bearing"): 
            l=1 # il y a une ligne d'entêtes avec les noms de colonnes obligatoires
            iType=csvIndexOfCol(strLine,"type")
            iLat=csvIndexOfCol(strLine,"lat")
            iLon=csvIndexOfCol(strLine,"lon")
            iSym=csvIndexOfCol(strLine,"sym")
            iName=csvIndexOfCol(strLine,"name")
            iDist=csvIndexOfCol(strLine,"dist")
            iBear=csvIndexOfCol(strLine,"bearing")
            txtDisplayContent.insert(tk.END,"\n")
         else:
            boolContinue=False
      else:
         if strLine[0:1] in ('W','T','<') or len(strLine)<3: boolContinue=False

      if boolContinue:
         txtDisplayContent.insert(tk.END,"\n"+"\n") # ajoute 2 lignes vierges en fin avant d'afficher le résultat

         for strLine in arrContenu:
            strResult=""
            if len(arrContenu)>l: 
               strLine=arrContenu[i].strip()
               if csvIsGpxRowOfValues(strLine):
                  arrColValues=csvLineToArray(strLine)
                  p=p+1
                  if not iType==None:strType=arrColValues[iType]+","
                  if not iLat==None: lat1=float(arrColValues[iLat])
                  if not iLon==None: lon1=float(arrColValues[iLon])
                  if not iSym==None: strSym=',"Waypoint"'
                  if not iName==None: strName=',Point'+str(p)
                  if not iDist==None: dist=float(arrColValues[iDist])
                  if not iBear==None: bear=float(arrColValues[iBear])

                  (lat,lon) = pointRadialDistance(lat1,lon1,bear,dist)

                   # affiche le résultat sur la dernière ligne
                  boolTrouve=True
                  # concatène en fonction des champs présents (on utilisera donc pas la fonction csvJoinValues)
                  strResult=strType + str(lat) + "," + str(lon) + strSym + strName + "," + str(dist) + "," + str(bear)
                  
                  txtDisplayContent.insert(tk.END,"\n"+strResult)
               else:
                  txtDisplayContent.insert(tk.END,"\n"+strLine)
            i=i+1
         txtDisplayContent.delete_last_blank_rows()

   if not boolTrouve: msg(i18n("mnuToolsCoordByBearingDist_msg_info_err"))


def mnuToolsMagnetDeclinOnClick():
   # demande à l'utilisateur une valeur de bearing puis si le champ bearing existe dans l'entête CSV, 
   # remplace le bearing de chaque ligne par cette valeur
   # le résultat est écrit dans une nouvelle ligne en fin de la zone de texte
   # accepte les paramètres o,w,e,-,+ pour le choix du signe (W=plus E=moins)
   # accepte le paramètre m pour calculer les coordonnées du point magnétique correspondant
   # accepte le paramètre t pour calculer la tangente du segment

   strInputOffsetBearing=""
   bearingOffset=0
   l=0
   c=0
   t=0
   boolMagn=False
   boolTan=False
   strEntetes=""
   strPtSym='"Waypoint"'
   arrTan=[90,-90]

   arrContenu=getTrimDisplayContentArray()
   if len(arrContenu)>0:
      if not csvIsGpxHeader(arrContenu[0],"bearing"): # recherche le terme dans la première ligne du tableau
         msg(i18n("mnuToolsMagnetDeclin_msg_info_err"))
      else:
         # demande à l'utilisateur la valeur du OffSet
         strInputOffsetBearing=inputbox.askstring(
            i18n("mnuToolsMagnetDeclin"), 
            prompt=i18n("inputboxMagnetDeclinValue")+":",
            initialvalue=0)

         if not strInputOffsetBearing is None:
            strInputOffsetBearing=strInputOffsetBearing.upper()
            if not (strInputOffsetBearing.find("M")==-1): boolMagn=True
            if not (strInputOffsetBearing.find("T")==-1): boolTan=True

            if not (strInputOffsetBearing.find("E")==-1): 
               strInputOffsetBearing=strInputOffsetBearing.replace("E","")
               strInputOffsetBearing=strInputOffsetBearing.replace("-","")
               strInputOffsetBearing="-"+strInputOffsetBearing

            strInputOffsetBearing=strInputOffsetBearing.replace(" ","")
            strInputOffsetBearing=strInputOffsetBearing.replace("+","")
            strInputOffsetBearing=strInputOffsetBearing.replace("O","")
            strInputOffsetBearing=strInputOffsetBearing.replace("W","")
            strInputOffsetBearing=strInputOffsetBearing.replace("T","")

            if isNumeric(strInputOffsetBearing):
               bearingOffset=float(strInputOffsetBearing)
            else:
               bearingOffset=999 # sera ainsi hors plage

            if bearingOffset>-360 and bearingOffset<360:

               for strLine in arrContenu:
                  strLine=strLine.strip()
                  boolIsHeader=False
                  boolIsData=False
                  l=l+1
                  if l==1: 
                     txtDisplayContent.insert(tk.END,"\n"+"\n") # ajoute lignes vierges en fin avant afficher résultat

                  if csvIsGpxHeader(strLine,"bearing"):
                     strEntetes=strLine
                     strResult=strLine

                  else:
                     if csvCommaIsInString(strLine):
                        arrValues=csvLineToArray(strLine)

                        c=csvIndexOfCol(strEntetes,"type")
                        type1=arrValues[c]

                        c=csvIndexOfCol(strEntetes,"lat")
                        lat1=float(arrValues[c])

                        c=csvIndexOfCol(strEntetes,"lon")
                        lon1=float(arrValues[c])

                        c=csvIndexOfCol(strEntetes,"sym")
                        sym1=arrValues[c]

                        c=csvIndexOfCol(strEntetes,"name")
                        name1=arrValues[c]
                        if name1[-2:]!="-V":name1=name1+"-V" # ajoute un car pour identifier le pt "variant"

                        c=csvIndexOfCol(strEntetes,"dist")
                        dist1=float(arrValues[c])

                        c=csvIndexOfCol(strEntetes,"bearing") 
                        bear1=float(arrValues[c])

                        newBear=loopBearing(float(bear1) + bearingOffset)
                        
                        # le même point "géographique" avec le nouveau bearing
                        strPtGM=csvJoinValues(type1,lat1,lon1,sym1,name1,dist1,newBear)

                        # csv final à afficher
                        strResult=strPtGM

                        # calcul de tangente ( = 2 demi-tangentes ) perpendiculaire à la radiale
                        if boolTan: 
                           symTan='"Dot, White"'
                           t=0
                           lenTan=dist1*math.sin(math.radians(5)) # longueur de la demi-tangente
                           if lenTan<1: lenTan=1 # NM

                           for bearTanOffset in arrTan: # 2 valeurs: 90 et -90
                              t=t+1
                              bearTan=bear1+bearTanOffset
                              nameTan=name1+"-T"

                              # le point calculé à l'extrémité de la demi-tangente
                              (latTan,lonTan)=pointRadialDistance(lat1,lon1,bearTan,lenTan)

                              # ajoute le csv au résultat final
                              strPtTan=csvJoinValues("T",latTan,lonTan,symTan,(nameTan+str(t)),lenTan,loopBearing(bearTan+bearingOffset))

                              if t==1: strResult=strResult + "\n" + strEntetes + "\n"
                              strResult=strResult + strPtTan + "\n"


                     else:
                        strResult=strLine

                  # affiche le résultat sur la dernière ligne
                  txtDisplayContent.insert(tk.END,"\n" + strResult)

               txtDisplayContent.delete_last_blank_rows()

def mnuToolsConvertCsvToGpxOnClick():
   strResult=""
   strEntetes=""
   boolTrackpoints=""

   arrContenu=getTrimDisplayContentArray()
   if len(arrContenu)>0:
      strLine=arrContenu[0]
      if csvIsGpxHeader(strLine):
         strEntetes=strLine
         iType=csvIndexOfCol(strLine,"type")
         iLat=csvIndexOfCol(strLine,"lat")
         iLon=csvIndexOfCol(strLine,"lon")
         iSym=csvIndexOfCol(strLine,"sym")
         iName=csvIndexOfCol(strLine,"name")
         iDist=csvIndexOfCol(strLine,"dist")
         iBear=csvIndexOfCol(strLine,"bearing")
      if strEntetes!="":
         for strLine in arrContenu:
            #if csvCommaIsInString(strLine):
            if csvIsGpxRowOfValues(strLine):
               arrColValues=csvLineToArray(strLine)
               strType="wpt"
               strLat="0.0"
               strLon="0.0"
               strSym="Waypoint"
               strName="Point"
               strDist=""
               strBear=""
            
               if not iType==None:  
                  if arrColValues[iType]=="T": strType="trkpt"
               if not iLat==None: 
                  strLat=arrColValues[iLat]
               if not iLon==None: 
                  strLon=arrColValues[iLon]
               if not iSym==None: 
                  strSym=arrColValues[iSym]
               if not iName==None: 
                  strName=arrColValues[iName]
               if not iDist==None: 
                  strDist=arrColValues[iDist]
               if not iBear==None: 
                  strBear=arrColValues[iBear]
               
               strGpxRow='<' + strType + ' lat="'+strLat+'"'+' lon="' +strLon + '">'  
               strGpxRow=strGpxRow + "<name>" + strName.replace('"','') + "</name>" + "<sym>" + strSym.replace('"','') + "</sym>"
               if len(strBear)>0: strGpxRow=strGpxRow + "<course>" + strBear + "</course>"
               if len(strDist)>0: strGpxRow=strGpxRow + "<extensions><distance_nm>" + strDist + "</distance_nm></extensions>"
               
               strGpxRow=strGpxRow + "</"+strType+">"
               strResult=strResult+"\n"+strGpxRow

   if len(strResult)>0:
      if strType=="trkpt": strResult="\n" + "<trk><trkseg>" + strResult + "\n" + "</trkseg></trk>" # <name>track</name>
      GPXNAMESPACE=cmd.GPXNAMESPACE
      strResult=cmd.XMLHEADER + "\n" + cmd.GPXROOTNODE%argv[0] + strResult + "\n" + "</gpx>"
      displayContent(strResult)


def mnuToolsReplaceBlankRowsByHeaderOnClick():
   # remplace les lignes vierges par le contenu de la ligne 1 (entêtes CSV)
   strEntetesCSV=""
   i=0
   p=0
   l=0
   boolWrite=False
   arrContenu=getTrimDisplayContentArray()
   n=len(arrContenu)-1
   if n>0: strEntetesCSV=arrContenu[0].strip() # copie la première ligne
   if len(strEntetesCSV):
      for i in range(n, -1, -1):
         strLine=arrContenu[i].strip()
         p=str(i+1)
         l=len(strLine)
         if boolWrite and l==0:
               txtDisplayContent.delete(p+".0",p+".0")
               txtDisplayContent.insert(p+".0",strEntetesCSV)
         boolWrite=(l>0) and (strLine!=strEntetesCSV)

# ----------------------------------------------------------------------------
if __name__ == '__main__':
   # initialisation de la fenêtre principale
   mainWindow = tk.Tk()
   mainWindow.title(cheminFichier())

   # ----------------------------------------
   # création des menus
   # ----------------------------------------
   menubar = tk.Menu(mainWindow)

   mnuApp = tk.Menu(menubar, tearoff=0)
   mnuApp.add_command(label=i18n("mnuAppShowConfig"), command=mnuAppShowConfigOnClick)
   mnuApp.add_command(label=i18n("mnuAppSaveConfig"), command=mnuAppSaveConfigOnClick)
   mnuApp.add_command(label=i18n("mnuAppResetConfig"), command=mnuAppResetConfigOnClick)
   mnuApp.add_separator()
   mnuApp.add_command(label=i18n("mnuAppOpenFile"), command=mnuAppOpenFileOnClick)
   mnuApp.add_command(label=i18n("mnuAppSaveContentAs"), command=mnuAppSaveContentAsOnClick)
   mnuApp.add_separator()
   mnuApp.add_command(label=i18n("mnuAppHelp"), command=mnuAppHelpOnClick)
   mnuApp.add_command(label=i18n("mnuAppAbout"), command=mnuAppAboutOnClick)
   mnuApp.add_separator()
   mnuApp.add_command(label=i18n("mnuAppExit"), command=mainWindow.quit)

   mnuData = tk.Menu(menubar, tearoff=0)
   mnuData.add_command(label=i18n("mnuDataShowDBFile"), command=mnuDataShowDBFileOnClick)
   mnuData.add_command(label=i18n("mnuDataConvertDBFileToCSV"), command=mnuDataConvertDBFileToCSVOnClick)
   mnuData.add_command(label=i18n("mnuDataExtractDBFile"), command=mnuDataExtractDBFileOnClick)
   mnuData.add_separator()
   mnuData.add_command(label=i18n("mnuDataSaveAsDBFileList"), command=mnuDataSaveAsDBFileListOnClick)
   mnuData.add_command(label=i18n("mnuDataDeleteDBFile"), command=mnuDataDeleteDBFileOnClick)
   mnuData.add_separator()
   mnuData.add_command(label=i18n("mnuDataRefreshDBFileList"), command=mnuDataRefreshDBFileListOnClick)
   
   mnuSearch = tk.Menu(menubar, tearoff=0)
   mnuSearch.add_command(label=i18n("mnuSearchSearch"), command=mnuSearchSearchOnClick)
   mnuSearch.add_separator()
   mnuSearch.add_command(label=i18n("mnuSearchShowCSV"), command=mnuSearchShowCSVOnClick)
   mnuSearch.add_command(label=i18n("mnuSearchShowGPX"), command=mnuSearchShowGPXOnClick)
   mnuSearch.add_command(label=i18n("mnuSearchShowXML"), command=mnuSearchShowXMLOnClick)
   mnuSearch.add_separator()
   mnuSearch.add_command(label=i18n("mnuSearchShowLog"), command=mnuSearchShowLogOnClick)
   
   mnuTools = tk.Menu(menubar, tearoff=0)
   mnuTools.add_command(label=i18n("mnuToolsDist2Points"), command=mnuToolsDist2PointsOnClick)
   mnuTools.add_command(label=i18n("mnuToolsCoordByBearingDist"), command=mnuToolsCoordByBearingDistOnClick)
   mnuTools.add_command(label=i18n("mnuToolsMagnetDeclin"), command=mnuToolsMagnetDeclinOnClick)
   mnuTools.add_separator()
   mnuTools.add_command(label=i18n("mnuToolsConvertCsvToGpx"), command=mnuToolsConvertCsvToGpxOnClick)
   mnuTools.add_separator()
   mnuTools.add_command(label=i18n("mnuToolsReplaceBlankRowsByHeader"), command=mnuToolsReplaceBlankRowsByHeaderOnClick)

   # instancie la menubar
   menubar.add_cascade(label=i18n("mnuApp"),menu=mnuApp)
   menubar.add_cascade(label=i18n("mnuData"),menu=mnuData)
   menubar.add_cascade(label=i18n("mnuSearch"),menu=mnuSearch)
   menubar.add_cascade(label=i18n("mnuTools"),menu=mnuTools)
   mainWindow.config(menu=menubar)

   # ----------------------------------------
   # disposition des champs dans des panels
   # ----------------------------------------
   # dimensionnement de la fenêtre
   windowWidth=1270
   if windowWidth>mainWindow.winfo_screenwidth(): windowWidth=mainWindow.winfo_screenwidth()

   windowHeight=660
   if windowHeight>mainWindow.winfo_screenheight(): windowHeight=mainWindow.winfo_screenheight()

   # ----------------------------------------
   # panel top
   PANBG="darkgray" # couleur de fond par défaut
   panMain= tk.PanedWindow(mainWindow, orient=tk.VERTICAL,bg=PANBG)

   # panel Top / barre de boutons
   WB=10 # largeur par défaut des boutons
   RLF=tk.FLAT
   panButtons = tk.PanedWindow(panMain, orient=tk.HORIZONTAL,bg=PANBG)

   frmButtons=tk.Frame(panButtons,bg=PANBG) # ,borderwidth=1,relief=tk.GROOVE
   frmButtons.grid()

   btnAppQuit=tk.Button(frmButtons,text=i18n("btnAppQuit"), width=WB, relief=RLF,command=mainWindow.quit)
   btnSearchSearch=tk.Button(frmButtons,text=i18n("btnSearchSearch"), width=WB, relief=RLF,command=mnuSearchSearchOnClick)
   btnToolsDist2Points=tk.Button(frmButtons,text=i18n("btnToolsDist2Points"), width=WB, relief=RLF,command=mnuToolsDist2PointsOnClick)
   btnToolsCoordByBearingDist=tk.Button(frmButtons,text=i18n("btnToolsCoordByBearingDist"), width=WB, relief=RLF,command=mnuToolsCoordByBearingDistOnClick)
   btnToolsMagnetDeclin=tk.Button(frmButtons,text=i18n("btnToolsMagnetDeclin"), width=WB, relief=RLF,command=mnuToolsMagnetDeclinOnClick)

   btnAppQuit.grid(row=0,column=0,padx=4)
   btnSearchSearch.grid(row=0,column=1,padx=10)
   btnToolsDist2Points.grid(row=0,column=2,padx=4)
   btnToolsCoordByBearingDist.grid(row=0,column=3)
   btnToolsMagnetDeclin.grid(row=0,column=4,padx=4)

   panButtons.add(frmButtons)
   panButtons.pack(fill=tk.BOTH,padx=3, pady=5)

   # panel Top/info
   panInfo = tk.PanedWindow(panMain, orient=tk.HORIZONTAL)

   frmInfo=tk.Frame(panInfo) # ,borderwidth=1,relief=tk.GROOVE
   frmInfo.grid() #frmInfo.columnconfigure(0,weight=1)

   # Libellé 1
   lblInfoLib1 = tk.Label(frmInfo, text=i18n("lblInfoLib1")+":") # anchor:W = text-align:left

   # Label contenant le fichier source sélectionné par l'utilisateur
   lblSourceFilename = tk.Label(frmInfo, text="()",font="-size 9 -weight bold") # anchor='w'

   # Libellé 2 contiendra par exemple le "please wait" pour les longs traitements
   lblInfoLib2 = tk.Label(frmInfo, text=" ",fg="red")

   # Positionnement des champs dans le Frame

   lblInfoLib1.grid(row=0,column=0)
   lblSourceFilename.grid(row=0,column=1)
   lblInfoLib2.grid(row=0,column=2)

   frmInfo.columnconfigure(2,weight=3) # attribution de l'espace de la dernière colonne 

   # disposition des champs dans le panel 
   panInfo.add(frmInfo)
   panInfo.pack(fill=tk.BOTH,padx=2, pady=0) # expand=tk.Y


   # --- panel 2 ---
   panData = tk.PanedWindow(panMain, orient=tk.HORIZONTAL)

   # panel gauche
   panLeft = tk.PanedWindow(panData, orient=tk.VERTICAL,width=270)

   # liste des fichiers sources de données 
   lstFichiers = tk.Listbox(panLeft,height=20) # ,width=30

   # radiobuttons pour choix de type de points
   frmChoixType=tk.LabelFrame(panLeft,borderwidth=0,relief=tk.FLAT,text=i18n("frmChoixType")+':')
   frmChoixType.grid()
   strRbtnTypeId=tk.StringVar()
   rbtnTypeW=tk.Radiobutton(frmChoixType,text="Waypoint",variable=strRbtnTypeId,value="W",command=rbtnTypeOnChange)
   rbtnTypeT=tk.Radiobutton(frmChoixType,text="Trackpoint",variable=strRbtnTypeId,value="T",command=rbtnTypeOnChange)
   rbtnTypeW.select()
   rbtnTypeW.grid(row=0,column=0)
   rbtnTypeT.grid(row=0,column=1)

   # champ texte contenant le fichier texte
   txtContenuFichierTexte = PopText(mainWindow) # tk.Text()

   # disposition des champs dans le panel gauche
   panLeft.add(lstFichiers)
   panLeft.add(frmChoixType)
   panLeft.add(txtContenuFichierTexte)

   # panel droit
   panRight = tk.PanedWindow(panData)

   # champ texte principal pour afficher les données
   txtDisplayContent = PopText(mainWindow) #tk.Text()

   # disposition des champs dans le panel droit
   panRight.add(txtDisplayContent)


   # disposition des sous-panels dans le panel 
   panData.add(panLeft)
   panData.add(panRight)
   panData.pack(expand=tk.Y,fill=tk.BOTH,padx=2, pady=0)

   # pack panMain
   panMain.pack(expand=tk.Y,fill=tk.BOTH,pady=1)

   # init et bind events des champs (en fin en raison d''interactions évènementielles entre champs)
   lstFichiers.bind("<<ListboxSelect>>", lstFichiersOnSelect)
   lstFichiersInit()
   txtContenuFichierTexte.insert("1.0",getContenuFichierTexte())
   

   # affichage de la fenêtre principale
   mainWindow.attributes("-fullscreen",False)
   #strWindowGeometry=str(windowWidth)+"x"+str(windowHeight)
   #print(strWindowGeometry)
   #mainWindow.geometry(strWindowGeometry)
   mainWindow.mainloop()

