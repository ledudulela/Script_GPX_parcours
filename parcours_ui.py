#!/usr/bin/python3
# -*- coding: UTF-8 -*-
SCRIPT_VERSION=20210501.2113
SCRIPT_AUTHOR="ledudulela"
L_FR="FR"
L_EN="EN"
LOCALE=L_FR # choose your LOCALE
# interface graphique du script de même nom en ligne de commandes. 
# Nécessite le package python3-tk si exécution avec python3 sinon python-tk 
#
# What's new in this version:
# Pour du contenu CSV: 
#  - nouveau menu Tools > Coord. à lat,lon,dist,bearing: coordonnées du point se trouvant à une distance & bearing d'un point donné
#   saisir lat,lon,dist,bearing (avec ou sans entêtes de colonnes CSV en première ligne)
#   Le résultat sera affiché sur la dernière ligne
#
from sys import argv as argv
import math
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
else:
   import tkinter as tk
   from tkinter import messagebox as msgbox
   import tkinter.filedialog as tkFileDialog
   
def i18n(strKey):
   if not(LOCALE==L_FR or LOCALE==L_EN): LOCALE==L_EN
   mapping={
      "mnuApp":{L_FR:"Application",L_EN:"Application"},
      "mnuAppShowConfig":{L_FR:"Afficher la configuration", L_EN:"Display configuration"},
      "mnuAppSaveConfig":{L_FR:"Sauvegarder la configuration", L_EN:"Save configuration"},
      "mnuAppResetConfig":{L_FR:"Réinitialiser la configuration", L_EN:"Reset configuration"},
      "mnuAppOpenFile":{L_FR:"Ouvrir un fichier...", L_EN:"Open file..."},
      "mnuAppSaveContentAs":{L_FR:"Enregistrer le contenu...", L_EN:"Save content..."},
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
      "mnuToolsDist2Points":{L_FR:"Distance & Bearing (CSV)", L_EN:"Distance & Bearing (CSV)"},
      "mnuToolsCoordByBearingDist":{L_FR:"Coord. à lat,lon,dist,bearing (CSV)", L_EN:"Coord. at lat,lon,dist,bearing (CSV)"},
      "mnuToolsReplaceBlankRowsByHeader":{L_FR:"Remplacer les lignes vierges par l'entête", L_EN:"Replace blank rows by header"},
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
      "mnuDataExtractDBFile_msg_info_extract":{L_FR:"Veuillez afficher, modifier et sauvegarder les paramètres de configuration avant de lancer une extraction.",L_EN:"Please open, modify and save configuration parameters before extraction."},
      "mnuToolsDist2Points_msg_info_err":{L_FR:"Format de données non valide.\nCSV sans entêtes lat,lon ou distance déjà présente.",L_EN:"Bad data format\nCSV without lat,lon header or distance already exists."},
      "mnuToolsCoordByBearingDist_msg_info_err":{L_FR:"Format de données non valide.\nCSV sans entêtes lat,lon,dist,bearing.",L_EN:"Bad data format\nCSV without lat,lon,dist,bearing header."},
      "os_msg_open_file":{L_FR:"Ouvrir un fichier",L_EN:"Open file"},
      "os_msg_delete_file":{L_FR:"Supprimer le fichier",L_EN:"Delete file"},
      "os_msg_save_db_as":{L_FR:"Enregistrer la BDD sous",L_EN:"Save DB as"}, 
      "os_msg_save_content_as":{L_FR:"Enregistrer le contenu sous",L_EN:"Save content as"},
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

    def curPos(self):
       # current Cursor Position
       return self.index(tk.INSERT)

    def curPosRowStartEnd(self):
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

    def close(self):
       pass # ferme le popup-menu

    def copy(self):
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
       intNbrLignes=self.index('end-1c').split('.')[0]
       strChaine="Nbr de lignes: "+str(intNbrLignes)
       msg(strChaine)

# -------------------------------------------------------------------------------
def msg(strTexte):
      msgbox.showinfo(moduleCmd, strTexte)

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
      setContenuFichier(strFilename,strContenu)
      strFilename=cmd.os.path.split(strFilename)[1]
      lstFichiersRefresh(strFilename)

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
   strEntetesCSV=""
   strContenu=getDisplayContent()+"\n"
   arrContenu=strContenu.split("\n")
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
   intLOF=0
   strEOL='1.end'

   NEWCOLS="dist,bearing"   

   # recherche la position des colonnes lat et lon
   # if txtDisplayContent.get('1.0','1.end').find(NEWCOLS)==-1:
   if len(arrContenu[0])>0:
      if not arrContenu[0].find("lat")==-1 and arrContenu[0].find("dist")==-1:
         strEntetesCSV=arrContenu[0]
         arrValues=strEntetesCSV.split(",")
         for value in arrValues:
            if value[0:3]=="lat": colLat=p
            if value[0:3]=="lon": colLon=p
            p=p+1

   if colLon==0: # avertissement si la col Lon n'a pas été trouvée
      msgbox.showinfo('Info', i18n("mnuToolsDist2Points_msg_info_err"))
   else:   
      for strLine in arrContenu:
         i=i+1
         strLine=strLine.strip()
         intLOF=len(strLine) # longueur de la ligne
         if intLOF>0:
            strLine=strLine+","
            strEOL=str(i)+'.end' # ou alors str(i)+"."+str(intLOF) pour la posi de fin de ligne
            if not strLine.find(strEntetesCSV)==-1: # si les entêtes de colonnes attendues sont dans la ligne...
               strValue=NEWCOLS
            else:
               arrValues=strLine.split(",")
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
            txtDisplayContent.insert(strEOL,","+strValue)

def mnuToolsCoordByBearingDistOnClick():
   # Calculating coordinates given a bearing and a distance
   l=0
   iLat=0
   iLon=1
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

   strContenu=getDisplayContent()+"\n"
   arrContenu=strContenu.split("\n")
   if len(arrContenu)>0:
      strLine=arrContenu[0]
      if strLine.find("lon")>0: # dans ce cas, les entêtes existent
         l=1
         if strLine.find("name")>0:
            iLat=1
            iLon=2
            iDist=5
            iBear=6
            strSym=',"Waypoint"'
            strName=',PointX'
 
      if len(arrContenu)>l:
         strLine=arrContenu[l] # ligne de valeurs
         if strLine.find(",")>0: # la confiance n'exclut pas le contrôle
            strLine=strLine.replace(", ","||") # pour les sym contenant une virgule
            arrCols=strLine.split(",")
            
            if l==1: strType=strLine[0:2] # si entetes alors type en debut de ligne
            lat1=float(arrCols[iLat].strip())
            lon1=float(arrCols[iLon].strip())
            dist=float(arrCols[iDist].strip())
            bear=float(arrCols[iBear].strip())
            (lat,lon) = pointRadialDistance(lat1,lon1,bear,dist)

            # affiche le résultat sur la dernière ligne
            strResult=strType + str(lat) + "," + str(lon) + strSym + strName + "," + str(dist) + "," + str(bear)
            txtDisplayContent.insert(tk.END,"\n" + strResult)

   if strResult=="":
      msg(i18n("mnuToolsCoordByBearingDist_msg_info_err"))


def mnuToolsReplaceBlankRowsByHeaderOnClick():
   # remplace les lignes vierges par le contenu de la ligne 1 (entêtes CSV)
   strEntetesCSV=""
   strContenu=getDisplayContent()+"\n"
   arrContenu=strContenu.split("\n")
   n=len(arrContenu)-1
   i=0
   p=0
   l=0
   boolWrite=False
   if n>0: strEntetesCSV=arrContenu[0].strip()
   if len(strEntetesCSV):
      for i in range(n, -1, -1):
         strLine=arrContenu[i].strip()
         p=str(i+1)
         l=len(strLine)
         if boolWrite and l==0:
            txtDisplayContent.delete(p+".0",p+".0")
            txtDisplayContent.insert(p+".0",strEntetesCSV)

         boolWrite=(l>0)

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
   # panel top
   windowWidth=1270
   if windowWidth>mainWindow.winfo_screenwidth(): windowWidth=mainWindow.winfo_screenwidth()

   windowHeight=660
   if windowHeight>mainWindow.winfo_screenheight(): windowHeight=mainWindow.winfo_screenheight()
   
   #panMain=windowWidth-4
   panMain= tk.PanedWindow(mainWindow, orient=tk.VERTICAL,bg="darkgray") # ,bg="red"

   # panel Top/info
   panInfo = tk.PanedWindow(panMain, orient=tk.HORIZONTAL) #  ,bg="blue"

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
   panInfo.pack(fill=tk.BOTH,padx=1, pady=1) # expand=tk.Y


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
   panData.pack(expand=tk.Y,fill=tk.BOTH,padx=2, pady=2)

   # pack panMain
   panMain.pack(expand=tk.Y,fill=tk.BOTH)

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

