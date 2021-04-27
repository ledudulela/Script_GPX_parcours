#!/usr/bin/python3
# -*- coding: UTF-8 -*-
SCRIPT_VERSION=20210427.1847
SCRIPT_AUTHOR="fdz"
# interface graphique du script. 
# Nécessite le package python3-tk si exécution avec python3 sinon python-tk 
import os
import sys
from functools import partial

if sys.version_info.major<3:
   import Tkinter as tk
   import tkMessageBox as msgbox
   import tkFileDialog
   # Messagebox
else:
   import tkinter as tk
   from tkinter import messagebox as msgbox

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
   lstFichiers.select_set(s)
   lstFichiers.event_generate("<<ListboxSelect>>")

def lstFichiersRefresh(strSelectedFile=""): # rafrachit la liste des fichiers
   lstFichiers.delete(0,tk.END)
   lstFichiersInit(strSelectedFile)

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


def mnuDataShowDBFileOnClick():
   strContent=getContenuFichierDB()
   displayContent(strContent)

def mnuDataExtractDBFileOnClick():
   if txtDisplayContent.search("<extract>","1.0",stopindex=tk.END):
      strElementTreeEncoding=cmd.xmlEltTreeEncoding()
      strFileName=cheminFichierDB()

      strNewFileName=cmd.extractFromGpxFile(strFileName,strElementTreeEncoding)
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
      strFileName=cmd.convertGpxFileToCsvFile(strFileName,strPtType,strElementTreeEncoding)
      if strFileName!="":
         strContent=getContenuFichier(strFileName)
         displayContent(strContent)

def mnuDataRefreshDBFileListOnClick():
   lstFichiersRefresh()

def mnuDataDeleteDBFileOnClick():
   strFileName=cheminFichierDB()
   if msgbox.askyesno("Question","Supprimer le fichier %s ?"%strFileName):
      os.remove(strFileName)
      lstFichiersRefresh()
      displayContent("")


def mnuSearchSearchOnClick():
    #msgbox.showinfo('Info', 'Effacement du champ résultat')
    txtDisplayContent.delete("1.0", tk.END)

    #msgbox.showinfo('Info', 'Enregistrement du fichier texte')
    strContent=txtContenuFichierTexte.get("1.0", tk.END)
    setContenuFichierTexte(strContent)

    #msgbox.showinfo('Info', 'Recherche en cours...')
    strType=strRbtnTypeId.get()
    strCheminFichierSource=cheminFichierDB()
    cmd.main(strCheminFichierSource,strType,strTxtInputFileName=cheminFichierTexte())

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
mnuApp.add_command(label="Quitter", command=mainWindow.quit)

mnuSearch = tk.Menu(menubar, tearoff=0)
mnuSearch.add_command(label="Rechercher...", command=mnuSearchSearchOnClick)
mnuSearch.add_separator()
mnuSearch.add_command(label="Afficher en CSV", command=mnuSearchShowCSVOnClick)
mnuSearch.add_command(label="Afficher en GPX", command=mnuSearchShowGPXOnClick)
mnuSearch.add_command(label="Afficher en XML", command=mnuSearchShowXMLOnClick)
mnuSearch.add_separator()
mnuSearch.add_command(label="Afficher le Log", command=mnuSearchShowLogOnClick)

mnuData = tk.Menu(menubar, tearoff=0)
mnuData.add_command(label="Afficher", command=mnuDataShowDBFileOnClick)
mnuData.add_command(label="Afficher en CSV", command=mnuDataConvertDBFileToCSVOnClick)
mnuData.add_command(label="Extraire...", command=mnuDataExtractDBFileOnClick)
mnuData.add_separator()
mnuData.add_command(label="Actualiser", command=mnuDataRefreshDBFileListOnClick)
mnuData.add_command(label="Supprimer...", command=mnuDataDeleteDBFileOnClick)

# instancie la menubar
menubar.add_cascade(label="Application",menu=mnuApp)
menubar.add_cascade(label="Données",menu=mnuData)
menubar.add_cascade(label="Recherche",menu=mnuSearch)
mainWindow.config(menu=menubar)

# ----------------------------------------
# disposition des champs dans des panels
# ----------------------------------------
# panel top
panTop = tk.PanedWindow(mainWindow, orient=tk.HORIZONTAL,width=1266) 

# panel top/gauche
panLeft = tk.PanedWindow(panTop, orient=tk.VERTICAL,width=300)

# liste des fichiers sources de données 
lstFichiers = tk.Listbox()
lstFichiers.pack(side=tk.TOP)

 # champ texte contenant le fichier texte (15 caracteres de large)
txtContenuFichierTexte = tk.Text(width=15)
txtContenuFichierTexte.pack(side=tk.LEFT)

 # radiobuttons pour choix de type de points
frmChoixType=tk.Frame(panLeft,borderwidth=2,relief=tk.GROOVE)
frmChoixType.grid()
strRbtnTypeId=tk.StringVar()
rbtnTypeW=tk.Radiobutton(frmChoixType,text="Waypoint",variable=strRbtnTypeId,value="W")
rbtnTypeT=tk.Radiobutton(frmChoixType,text="Trackpoint",variable=strRbtnTypeId,value="T")
rbtnTypeW.select()
rbtnTypeW.grid(row=0,column=0)
rbtnTypeT.grid(row=0,column=1)
frmChoixType.pack()

# disposition des champs dans le panel top/gauche
panLeft.add(lstFichiers)
panLeft.add(txtContenuFichierTexte)
panLeft.add(frmChoixType)
panLeft.pack(expand=tk.Y, fill=tk.BOTH, pady=2, padx=2)

# panel top/droit
panRight = tk.PanedWindow(panTop)

# champ texte principal pour afficher les données
txtDisplayContent = tk.Text()
txtDisplayContent.pack() 

# disposition des champs dans le panel top/droit
panRight.add(txtDisplayContent)
panRight.pack(expand=tk.Y, fill=tk.BOTH, pady=2, padx=2)

# disposition des sous-panels dans le panel top
panTop.add(panLeft)
panTop.add(panRight)
panTop.pack()

# panel bas
panBottom = tk.PanedWindow(mainWindow, orient=tk.HORIZONTAL,height=30)

# Label de barre d'état
lblStatebarLib1 = tk.Label(mainWindow, text="Fichier source de données:", width=60, anchor='e')
lblStatebarLib1.pack(side=tk.LEFT)

# Label contenant le fichier source sélectionné par l'utilisateur
lblSourceFilename = tk.Label(mainWindow, text="()", width=128, anchor='w') 
lblSourceFilename.pack()

# disposition des champs dans le panel bas
panBottom.add(lblSourceFilename)
panBottom.add(lblSourceFilename)
panBottom.pack()

# init et bind events des champs (en fin en raison d''interactions évènementielles entre champs)
lstFichiers.bind("<<ListboxSelect>>", lstFichiersOnSelect)
lstFichiersInit()
txtContenuFichierTexte.insert("1.0",getContenuFichierTexte())

# affichage de la fenêtre principale
#mainWindow.attributes("-fullscreen",False)
mainWindow.geometry("1270x660")
mainWindow.mainloop()

