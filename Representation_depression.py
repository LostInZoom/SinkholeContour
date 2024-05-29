"""

Travaux MNT


Ensemble des méthodes de traitement des MNT



@author : boulze, schleich


ENSG, IGN, 2018


"""


# ----------------------------------------- IMPORTS -------------------------------------------------

import numpy as np
import math as mp

# ----------------------------------------- ALGOS ---------------------------------------------------



def exageration_depressions(equidistance, mnt, profondeur, max_depression, min_depression,median):
    
    print("Algo exageration")
    taille_mnt = len(mnt)+40
    new_mnt = np.zeros((taille_mnt-40,taille_mnt-40), dtype=float)
    
    for i in range(20,taille_mnt-20):
        for j in range (20,taille_mnt-20):
            
            
            #Cas des petites dépressions
          
            if str(profondeur[i][j])!= "nan" and profondeur[i][j] <  equidistance  :
                
                
                maxi = max_depression[i][j]
                mini = min_depression[i][j]
                
                courbe_inf = mp.floor(mini)-mp.floor(mini)%equidistance
                courbe_sup = mp.floor(maxi+equidistance)-mp.floor(maxi)%equidistance
                
                
                #Si la depression n'intersecte pas dejà la courbe de niveau
                
#                if courbe_sup - courbe_inf == equidistance:
                  
                tiers =  maxi - profondeur[i][j]/3
                
                
                
                #On regarde si la depression est plus proche de courbe inf que de courbe_sup
                #Si elle est plus proche de courbe sup, on la réhausse
                
                if courbe_sup - maxi < mini-courbe_inf:
                    
                    
                    epsilon = courbe_sup - tiers
                    
                    new_mnt[i-20][j-20] = mnt[i-20][j-20]+ epsilon
                    
                
                #Sinon elle est plus proche de la courbe inf, on l'abaisse
                
                else:
                
                    
                    epsilon = tiers - courbe_inf
                 
                    new_mnt[i-20][j-20] = mnt[i-20][j-20] - epsilon
                        
                        
                # Si la depression intersecte dejà la courbe de niveau
                
#                else:
#                    
#                    tiers = maxi - profondeur[i][j]/3
#                    courbe_sup_min = mp.floor(mini+equidistance)-mp.floor(mini)%equidistance
#                    
#                    #On regarde si le tiers supérieur est au dessus ou au dessous de la courbe sup du MIN 
#                    #Si le tiers est au dessus du sup du MIN, on l'abaisse
#                    
#                    if tiers > courbe_sup_min:
#                        
#                        epsilon = tiers - courbe_sup_min
#                        
#                        new_mnt[i][j] = mnt[i][j] - epsilon
#                      
#                    #Sinon elle est plus proche de la courbe inf, on l'abaisse
#                    
#                    else:
#                        
#                        epsilon = courbe_sup_min - tiers
#                        
#                        new_mnt[i][j] = mnt[i][j] + epsilon
#                    
#                
        
        # Les dépressions ou profondeur[i][j] >= E n'ont pas besoin de retouches car elles intersectent 2 fois les courbes de niveaux
        
            else:
            
                  new_mnt[i-20][j-20] = mnt[i-20][j-20]
        
           
           
               
               
    ecriture_fichier(new_mnt,"new_courbes/New_mnt/mnt_tiers.asc")

     
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
    
    
  
 # -------------------------------------- CONSOLE ----------------------------------------   
    
        

if __name__ == "__main__":
    
    print("----------- Chargement du MNT ----------- \n\n")
  
    mnt = np.genfromtxt("new_courbes/New_mnt/cDEM_effet_de_bord.asc",skip_header=6)
    
    print("----------- Chargement profondeur  ----------- \n\n")
    
    profondeur = np.genfromtxt("new_courbes/newRaster/profondeur.asc",skip_header=6)
    
    print("----------- Chargement min  ----------- \n\n")
    
    mini = np.genfromtxt("new_courbes/newRaster/min.asc",skip_header=6)
    
    print("----------- Chargement max  ----------- \n\n")
    
    maxi = np.genfromtxt("new_courbes/newRaster/max.asc",skip_header=6)
    
    print("----------- Chargement median  ----------- \n\n")
    
    #median = np.genfromtxt("new_courbes/newRaster/median.asc",skip_header=6)
    
    
    exageration_depressions(10,mnt,profondeur,maxi,mini,2)
    
    
    
    
   