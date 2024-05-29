"""
Travaux MNT

Ensemble des méthodes de traitement des MNT

@author : boulze, schleich

ENSG, IGN, 2018

lorsque vous chargez un nouveau MNT rentrer ses coordonnées dans la fonction ecriture_fichier
(vous obtenez ces données en ouvrant le MNT.asc avec Notepad par exemple)

"""



# ----------------------------------------- IMPORTS -------------------------------------------------

import numpy as np
from skimage.morphology import erosion, dilation, opening, closing, disk, square, star
import cv2


# ---------------------------------------------------------------------------------------------------

   
"""

Determine un masque plaine/montagne sur le MNT


"""


def plaine_montagne(mnt, taille_maille, seuil):
    
    taille_mnt = len(mnt[0])
    mnt_masque = np.zeros((taille_mnt,taille_mnt), dtype=int)
    
    if taille_mnt%taille_maille !=0:                        #si le masque n'est pas un diviseur de la taille du mnt on arrete
        return "Taille du masque invalide"
    
    print("  \n\n     /!\ Taille du masque valide /!\      \n\n  ")
    
    print("--------- Création du maillage -----------  \n\n")
    for i in range(0,taille_mnt,taille_maille):
        for j in range(0,taille_mnt,taille_maille):
            maille = np.zeros((taille_maille,taille_maille), dtype=float)
            for k in range(0,taille_maille):
                for l in range(0,taille_maille):
                    maille[k][l] = mnt[i+k][j+l]    
                    
            z_max = np.max(maille)
            z_min = np.min(maille)
            z_moy = np.mean(maille)
            D = 2*z_max-z_moy-z_min
            if D <= seuil:
                for k in range(0,taille_maille):
                    for l in range(0,taille_maille):
                        mnt_masque[i+k][j+l] = 0
            elif D > seuil:
                for k in range(0,taille_maille):
                    for l in range(0,taille_maille):
                        mnt_masque[i+k][j+l] = 1
     
    
    print("     /!\ Maillage cree avec succes /!\      \n\n")
    
    ecriture_fichier(mnt_masque,"maillage_MNT"+"_"+str(taille_maille)+"_"+str(seuil)+".asc")

          

"""

Calcul l'index de position topographique d'un MNT (TPI) :

Fait la différence entre la valeur d'un pixel et la moyenne de la valeur de ses voisins proches


"""

def TPI(mnt):
    
   taille_mnt = len(mnt[0])
   mnt_TPI = np.zeros((taille_mnt,taille_mnt), dtype=float)
   
   print("----------- Creation du TPI ------------ \n\n")
   
   #gerer les effets de bords
    
   for i in range (1,taille_mnt):    # on parcourt les lignes
       for j in range(1,taille_mnt):    # on parcourt les colonnes
          
           voisins = voisinage(mnt,i,j)
           taille = len(voisins)
           somme_voisins = 0
           for k in range (taille):
               somme_voisins += voisins[k][0] 
           moyenne_voisins = somme_voisins/taille
           
           mnt_TPI[i][j] = mnt[i][j] - moyenne_voisins
          
    
   print("        /!\ TPI cree avec succes /!\      \n\n")
    
   ecriture_fichier(mnt_TPI,"TPI.asc")
    
   
 
"""
Calcul du MNT pour les courbes de niveau

"""

def cDEM(cTPI,DEM1,DEM2):
    taille_mnt = len(cTPI[0])
    
    
    cDEM =  np.zeros((taille_mnt,taille_mnt), dtype=float)
    
    for i in range (taille_mnt):
        
        for j in range (taille_mnt):
            
            cDEM[i][j] = cTPI[i][j]*DEM1[i][j]+(1-cTPI[i][j])*DEM2[i][j]
            
            
    cDEM_sans_bord =  np.zeros((taille_mnt-40,taille_mnt-40), dtype=float)
    print("sans bord")
    
    for i in range (20,taille_mnt-20):
        
        for j in range (20,taille_mnt-20):
            
            cDEM_sans_bord [i-20][j-20] = cDEM[i][j]
            
        
    ecriture_fichier(cDEM_sans_bord,"new_courbes/New_mnt/cDEM_effet_de_bord.asc")
   

        
# ----------------------------- Filtres morphologiques --------------------------------------------


def ouv_ferm(img,taille_disk):
    
    selem = disk(taille_disk)
    ouv = opening(img,selem)
    #ferm = closing(ouv, selem)
    
    ecriture_fichier(ouv,"ouv_ferm_disk"+str(taille_disk)+".asc")

        
# -------------------------------------- Fonctions ANNEXES ---------------------------------------------------
        
"""

Ecriture dans un fichier

"""

def ecriture_fichier(nom_fichier, adresse):
    
    fichier = open(adresse,'w')
   
    print("----------- Ecriture en cours ------------")
   
    fichier.write("ncols         4040 \n") 
    fichier.write("nrows         4040 \n")
    fichier.write("xllcorner     899900.000000 \n")
    fichier.write("yllcorner     6639900.000000 \n")
    fichier.write("cellsize      5.000000000000 \n")
    fichier.write("NODATA_value  -9999.90 \n")
   
    for ligne in nom_fichier:
        for element in ligne:
            fichier.write(str(round(element,3))+" ")
        fichier.write("\n")
    fichier.close()
        
    
    
"""

Determine les voisins d'un pixel pour une dalle carré de type a X a

"""
       
def voisinage(mnt,i,j):
    
    taille_mnt = len(mnt[0])-1
    voisin=[]

    # Coin Superieur gauche

    if i==0 and j==0:
        voisin.append([mnt[i][j+1],i,j+1])
        voisin.append([mnt[i+1][j],i+1,j])
        voisin.append([mnt[i+1][j+1],i+1,j+1])
        
    #coin inf droite
    
    elif i==taille_mnt and j==taille_mnt:
        voisin.append([mnt[i][j-1],i,j-1])
        voisin.append([mnt[i-1][j-1],i-1,j-1])
        voisin.append([mnt[i-1][j],i-1,j])
    
    # Coin superieur droit
    
    elif i==0 and j==taille_mnt:
        
        voisin.append([mnt[i+1][j],i+1,j])
        voisin.append([mnt[i][j-1],i,j-1])
        voisin.append([mnt[i+1][j-1],i+1,j-1])
    
    # Coin inferieur gauche
    
    elif i==taille_mnt and j==0:
        voisin.append([mnt[i-1][j+1],i-1,j+1])
        voisin.append([mnt[i-1][j],i-1,j])
        voisin.append([mnt[i][j+1],i,j+1])
        
    # Bord haut
    
    elif  (j>0 or j<taille_mnt) and i==0:
        
        voisin.append([mnt[i][j-1],i,j-1])
        voisin.append([mnt[i+1][j-1],i+1,j-1])
        voisin.append([mnt[i][j+1],i,j+1])
        voisin.append([mnt[i+1][j],i+1,j])
        voisin.append([mnt[i+1][j+1],i+1,j+1])
        
    #Bord bas
    
    elif  (j>0 or j<taille_mnt) and i==taille_mnt:
        
        voisin.append([mnt[i-1][j-1],i-1,j-1])
        voisin.append([mnt[i][j+1],i,j+1])
        voisin.append([mnt[i][j-1],i,j-1])
        voisin.append([mnt[i-1][j+1],i-1,j+1])
        voisin.append([mnt[i-1][j],i-1,j])

    # Bord gauche
    
    elif  j==0 and (i<taille_mnt or i>0):
                
        voisin.append([mnt[i-1][j+1],i-1,j+1])
        voisin.append([mnt[i-1][j],i-1,j])
        voisin.append([mnt[i+1][j+1],i+1,j+1])
        voisin.append([mnt[i][j+1],i,j+1])
        voisin.append([mnt[i+1][j],i+1,j])
    
    # Bord droit
    
    elif  j==taille_mnt and (i<taille_mnt or i>0):
        
        voisin.append([mnt[i][j-1],i,j-1])
        voisin.append([mnt[i+1][j-1],i+1,j-1])
        voisin.append([mnt[i+1][j],i+1,j])
        voisin.append([mnt[i-1][j],i-1,j])
        voisin.append([mnt[i-1][j-1],i-1,j-1]) 
    
    else:
        voisin.append([mnt[i+1][j],i+1,j])
        voisin.append([mnt[i+1][j+1],i+1,j+1])
        voisin.append([mnt[i+1][j-1],i+1,j-1])
        voisin.append([mnt[i-1][j],i-1,j])
        voisin.append([mnt[i-1][j+1],i-1,j+1])
        voisin.append([mnt[i-1][j-1],i-1,j-1])
        voisin.append([mnt[i][j+1],i,j+1])
        voisin.append([mnt[i][j-1],i,j-1])
        
    return voisin     
    

    
  
    
 # -------------------------------------- CONSOLE ----------------------------------------   
    
        

if __name__ == "__main__":
    
    print("----------- Chargement du MNT ----------- \n\n")
    
    mnt = np.genfromtxt("085_046.asc",skip_header=6)
    
    #Generation du maque plaine_montagne
    plaine_montagne(mnt,6,7)
    masque_6_7 = np.genfromtxt("maillage_MNT_6_7.asc",skip_header=6)  
    ouv_ferm(masque_6_7,12)
    
    #Traitement du MNT
    dem1 = cv2.GaussianBlur(mnt,(33,33),5)
    ecriture_fichier(dem1,"mnt_smooth_33_5.asc")
    
    dem2 = cv2.GaussianBlur(mnt,(133,133),15)
    ecriture_fichier(dem2,"mnt_smooth_133_15.asc")
    
    tpi = TPI(mnt)
    tpi_import = np.genfromtxt("TPI.asc",skip_header=6)
    
    tpismooth= cv2.GaussianBlur(tpi_import,(33,33),5)
    ecriture_fichier(tpismooth,"TPI_smooth_33_3.asc")
    
    tpi = np.genfromtxt("TPI_smooth_33_3.asc",skip_header=6)
    dem1 = np.genfromtxt("mnt_smooth_33_5.asc",skip_header=6)
    dem2 =  np.genfromtxt("mnt_smooth_133_15.asc",skip_header=6)
    
    cDEM(tpi,dem1,dem2)
    
    

    