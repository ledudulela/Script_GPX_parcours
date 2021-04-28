#!/usr/bin/python3
# -*- coding: UTF-8 -*-
SCRIPT_VERSION=20210428.1724
SCRIPT_AUTHOR="fdz"
# interface graphique du script. 
# Nécessite le package python3-tk si exécution avec python3 sinon python-tk 
#
# What's new in this version:
# Amélioration du responsive design de la fenêtre principale
# Renommages de menus
# Nouveau menu "BDD > Enregistrer sous"
# Nouveau menu "App > Ouvrir un fichier"
# Nouveau menu "App > Enregistrer le contenu

import os
import sys

#from functools import partial

if sys.version_info.major<3:
   import Tkinter as tk
   import tkMessageBox as msgbox
   import tkFileDialog
   # Messagebox
else:
   import tkinter as tk
   from tkinter import messagebox as msgbox
   import tkinter.filedialog as tkFileDialog
   
moduleCmd=sys.argv[0].replace("_ui","")
moduleCmd=moduleCmd.replace(".py","")
moduleCmd=moduleCmd.replace("./","")
cmd=__import__(moduleCmd)
#import moduleCmd as cmd

def cheminFichier(): # renvoie le nom du script "ligne de commandes" sans l'extension. exemple: "parcours"
   fileName=cmd.scriptBaseName()
   arrFileRootExt=os.path.splitext(fileName)
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
   if os.path.exists(strCheminFichier):
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

def setCurrentFichierDB(strFileName): # affiche le nom de fichier sélectionné dans le champ dédié
   lblSourceFilename['text']=strFileName

def lstFichiersOnSelect(event): # évènement de sélection d'un elt dans la liste des fichiers
   if event.widget.curselection():
      setCurrentFichierDB(event.widget.get(event.widget.curselection()))

def lstFichiersInit(strSelectedFile=""): # initialise la liste des fichiers
   arrFiles=os.listdir('.')
   arrExt=('.dat','.gpx')
   i=0
   s=0
   arrFiles.sort()
   for file in arrFiles:
      if os.path.splitext(file)[1] in arrExt:
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
   lblInfoLib2['text']="Veuillez patentier..."
   #msgbox.showinfo('Info',lblInfoLib2['text'])

def pleaseWaitOff():
   lblInfoLib2['text']=""

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
   strContent=txtDisplayContent.get("1.0", tk.END)
   setContenuFichierConfig(strContent)

def mnuAppResetConfigOnClick():
   strContent=cmd.getDefaultConfigContent()
   displayContent(strContent)

def mnuAppOpenFileOnClick():
   arrTypesFiles=[('csv file','.csv'),('gpx file','.gpx'),('data file','.dat'),('xml file','.xml'),('txt file','.txt')]
   strFilename=tkFileDialog.askopenfilename(title="Ouvrir un fichier",filetypes=arrTypesFiles)
   if strFilename!="":
      strContenu=getContenuFichier(strFilename)
      displayContent(strContenu)

def mnuAppSaveContentAsOnClick():
   arrTypesFiles=[('all files','.*'),('csv file','.csv'),('gpx file','.gpx'),('data file','.dat'),('xml file','.xml'),('txt file','.txt')]
   #strDefaultExt=".gpx"
   strFilename=tkFileDialog.asksaveasfilename(title="Enregistrer le contenu sous",filetypes=arrTypesFiles)
   if strFilename!="":
      strContenu=txtDisplayContent.get("1.0", tk.END)
      setContenuFichier(strFilename,strContenu)
      strFilename=os.path.split(strFilename)[1]
      lstFichiersRefresh(strFilename)


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
      msgbox.showinfo('Info',"Veuillez afficher, modifier et sauvegarder les paramètres de configuration avant de lancer une extraction.")

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
   strFilename=tkFileDialog.asksaveasfilename(title="Enregistrer la BDD sous",filetypes=arrTypesFiles,initialfile=cheminFichierDB())
   if strFilename!="":
      strContenu=getContenuFichier(cheminFichierDB())
      setContenuFichier(strFilename,strContenu)
      strFilename=os.path.split(strFilename)[1]
      lstFichiersRefresh(strFilename)

def mnuDataDeleteDBFileOnClick():
   strFileName=cheminFichierDB()
   if msgbox.askyesno("Question","Supprimer le fichier %s ?"%strFileName):
      os.remove(strFileName)
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


# ----------------------------------------------------------------------------
# initialisation de la fenêtre principale
mainWindow = tk.Tk()
mainWindow.title(cheminFichier())

# ----------------------------------------
# création des menus
# ----------------------------------------
menubar = tk.Menu(mainWindow)

mnuApp = tk.Menu(menubar, tearoff=0)
mnuApp.add_command(label="Afficher la configuration", command=mnuAppShowConfigOnClick)
mnuApp.add_command(label="Sauvegarder la configuration", command=mnuAppSaveConfigOnClick)
mnuApp.add_command(label="Réinitialiser la configuration", command=mnuAppResetConfigOnClick)
mnuApp.add_separator()
mnuApp.add_command(label="Ouvrir un fichier...", command=mnuAppOpenFileOnClick)
mnuApp.add_command(label="Enregistrer le contenu...", command=mnuAppSaveContentAsOnClick)
mnuApp.add_separator()
mnuApp.add_command(label="Quitter", command=mainWindow.quit)

mnuData = tk.Menu(menubar, tearoff=0)
mnuData.add_command(label="Ouvrir la sélection", command=mnuDataShowDBFileOnClick)
mnuData.add_command(label="Convertir en CSV", command=mnuDataConvertDBFileToCSVOnClick)
mnuData.add_command(label="Extraire une zone...", command=mnuDataExtractDBFileOnClick)
mnuData.add_separator()
mnuData.add_command(label="Enregistrer sous...", command=mnuDataSaveAsDBFileListOnClick)
mnuData.add_command(label="Supprimer...", command=mnuDataDeleteDBFileOnClick)
mnuData.add_separator()
mnuData.add_command(label="Actualiser la liste", command=mnuDataRefreshDBFileListOnClick)

mnuSearch = tk.Menu(menubar, tearoff=0)
mnuSearch.add_command(label="Rechercher les points", command=mnuSearchSearchOnClick)
mnuSearch.add_separator()
mnuSearch.add_command(label="Afficher en CSV", command=mnuSearchShowCSVOnClick)
mnuSearch.add_command(label="Afficher en GPX", command=mnuSearchShowGPXOnClick)
mnuSearch.add_command(label="Afficher en XML", command=mnuSearchShowXMLOnClick)
mnuSearch.add_separator()
mnuSearch.add_command(label="Afficher le Log", command=mnuSearchShowLogOnClick)

# instancie la menubar
menubar.add_cascade(label="Application",menu=mnuApp)
menubar.add_cascade(label="B.D.D.",menu=mnuData)
menubar.add_cascade(label="Recherche",menu=mnuSearch)
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
lblInfoLib1 = tk.Label(frmInfo, text="Base de données:") # anchor:W = text-align:left

# Label contenant le fichier source sélectionné par l'utilisateur
lblSourceFilename = tk.Label(frmInfo, text="()",font="-size 9 -weight bold") # anchor='w'

# Libellé 2
lblInfoLib2 = tk.Label(frmInfo, text=" ",fg="red")

# Positionnement des champs dans le Frame

lblInfoLib1.grid(row=0,column=0)
lblSourceFilename.grid(row=0,column=1)
lblInfoLib2.grid(row=0,column=2)

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
frmChoixType=tk.LabelFrame(panLeft,borderwidth=0,relief=tk.FLAT,text='Points à rechercher:')
frmChoixType.grid()
strRbtnTypeId=tk.StringVar()
rbtnTypeW=tk.Radiobutton(frmChoixType,text="Waypoint",variable=strRbtnTypeId,value="W")
rbtnTypeT=tk.Radiobutton(frmChoixType,text="Trackpoint",variable=strRbtnTypeId,value="T")
rbtnTypeW.select()
rbtnTypeW.grid(row=0,column=0)
rbtnTypeT.grid(row=0,column=1)

# champ texte contenant le fichier texte
txtContenuFichierTexte = tk.Text()

# disposition des champs dans le panel gauche
panLeft.add(lstFichiers)
panLeft.add(frmChoixType)
panLeft.add(txtContenuFichierTexte)

# panel droit
panRight = tk.PanedWindow(panData)

# champ texte principal pour afficher les données
txtDisplayContent = tk.Text()

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

