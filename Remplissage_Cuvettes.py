"""
Remplissage (inondations) des cuvettes


@author  : hugo boulze, schleich
@copyright : IGN, ENSG 2019
@version : 1.0
@email   : hugo.boulze@ensg.eu, anouk.schleich@ensg.eu


"""


# ----------------------------------------- IMPORTS -------------------------------------------------

import numpy as np

# ----------------------------------------- ALGOS ---------------------------------------------------


"""


    
    Pour vecteur :
        
    - 1ere colonne : id des dépressions
    - 2eme colonne : aire des dépressions
    - 3eme colonne : que des 0
    
    Pour vecteur_courant:
               
    - 1ere colonne : id des dépressions
    - 2eme colonne : que des 0
        


"""



def vecteur_id_aire(fichier_txt):

     identifiant = fichier_txt[:,9]
     aire = fichier_txt[:,10]
     
     # On crée un vecteur de deux colonnes et de len(fichier_txt) lignes
     vecteur = np.zeros((len(fichier_txt),3), dtype=int)
     vecteur_courant = np.zeros((len(fichier_txt),2), dtype=int)
     
     for i in range (len(fichier_txt)):
         vecteur[i][0] = identifiant [i]
         vecteur[i][1] = aire[i]
         vecteur_courant[i][0] = identifiant [i]

     return(vecteur,vecteur_courant)
     

"""

On compare l'altitude d'u pixel à celle de ses voisins. Si elle est plus haute que celle d'un pixel alors on inonde c pixel. (on rajoute 25m carré à l'aire 
de la dépression : un pixel représente un carré de 5m de côté)

"""
        
     
def iteration_voisinage(i,j,altitude,mnt,depression_id,identifiant,aire_depression,liste_pixel):
    
                #On récupère l'altitude sur l'ancien mnt des pixels voisins de celui que l'on vient d'incrémenter
                #On regarde si l'altitude du pixel est plus grande que celle de ces voisins
                # Si oui il y a écoulement de l'eau
                
              
                voisins = voisinage(mnt,i,j)
                
                for k in range(len( voisins)):
                    
                    
                    x = voisins[k][1]
                    y = voisins[k][2]
                    
                    
                    if altitude >  voisins[k][0]:
                        
                        #Si l'id de la case courante est différent de l'id de la dépression, alors c'est que le pixel n'appartient à aucune dépression
                        # A ce moment là, on l'ajoute à la dépression et l'aire de la dépression augmente
                        if depression_id[x,y] == 0: #!= identifiant:
                            aire_depression +=25
                            
                        liste_pixel.append([x,y])
#                        
                        
#                    
                    # Il faut ensuite réitérer sur l'ensemble du voisinage du voisinage etc ... jusqu'a arret
            
                return liste_pixel,aire_depression
            
            
        
"""

On parcourt les dépressions



"""      

                
def iteration(origine,vecteur_courant, mnt, identifiant_depression):
    
    
    taille_mnt = len(mnt)
    
    
    copie = np.zeros((taille_mnt,taille_mnt))
    
    for i in range (len(identifiant_depression)):
        for j in range (len(identifiant_depression)):
            copie[i][j]= identifiant_depression[i][j]
             
            
    new_mnt = np.zeros((taille_mnt,taille_mnt))
    
    for i in range (len(identifiant_depression)):
        for j in range (len(identifiant_depression)):
            new_mnt[i][j]= mnt[i][j]
            

   
    for i in range(0,taille_mnt):
        for j in range (0,taille_mnt):
            
            
                   
            #Si l'on se trouve sur une dépression
            if identifiant_depression[i][j] != 0:
              
                identifiant = int(identifiant_depression[i][j])
              
                if origine[identifiant-1][2] == 0:
                  
                  
                    # On ajoute 1 m à un pixel de la dépression courante
                    altitude = mnt[i][j] +1
                    
                    aireOrigine = origine[identifiant-1][1]
                  
                    
                    aireActuelle = vecteur_courant[identifiant-1][1]
                    
                   
                    liste_pixel = []
                   
                     
                    liste_pixel, aireActuelle = iteration_voisinage(i,j,altitude,mnt,identifiant_depression,identifiant,aireActuelle,liste_pixel)
                
                    if (aireActuelle - aireOrigine) < 2*aireOrigine:
                            
                        vecteur_courant[identifiant-1][1] = aireActuelle
                        
                        for pixel in liste_pixel:
                          
                        
                                x = pixel[0]
                                y = pixel[1]
                                
                                # Si le pixel ne fait pas deja parti de la depression, on le rajoute a la depression
                                
                                if identifiant_depression[x][y] != identifiant_depression[i][j]:
                                    
                                    if identifiant_depression[x][y] == 0 :
                                        
                                        copie[x][y] = identifiant_depression[i][j]
                                
                                new_mnt[x][y] +=  mnt[i][j] - mnt[x,y]
                
                    else:
                         origine[identifiant-1][2] = 1
                         
                    
                
            
    
    return origine, vecteur_courant, new_mnt, copie 



"""

Fonction qui permet de décider si le remplissage des dépressions doit continuer ou non


"""

def remplissage_depression(vecteur_origine,vecteur_courant,mnt,id_depression):
    
    taille_vecteur = len(vecteur_origine)
    
    somme = 0
    
    #Si la cellule vaut 1 cela veut dire que la dépression a atteint sa taille maximale
    for ligne in vecteur_origine:
        if ligne[2] == 1:
            somme +=1
        

    #Si toutes les cellules valent 1, toutes les dépressions ont leur taille finales: on arrête l'algorithme
    if somme == taille_vecteur:
        ecriture_fichier(id_depression,"NEW_depressions_id_2bis.asc")
    
    #Sinon on continue
    else:
        print("STEP")
        vecteur_origne, vecteur_courant, new_mnt, copie = iteration(vecteur_origine, vecteur_courant,mnt,id_depression)

        return remplissage_depression(vecteur_origine,vecteur_courant,new_mnt,copie)
        



"""

Algorithme d'inondation des dépressions ("launcher")


"""


def AlgoRemplissageDepression(fichier_txt,mnt,id_depression):
    
    vecteur, courant = vecteur_id_aire(fichier_txt)
    remplissage_depression(vecteur,courant,mnt,id_depression)


     
# -------------------------------------- Fonctions ANNEXES ---------------------------------------------------
        
"""

Ecriture dans un fichier


"""

def ecriture_fichier(nom_fichier, adresse):
    
    fichier = open(adresse,'w')
   
    print("----------- Ecriture en cours ------------")
   
    fichier.write("ncols         4080 \n") 
    fichier.write("nrows         4080 \n")
    fichier.write("xllcorner     899800.000000 \n")
    fichier.write("yllcorner     6639800.000000 \n")
    fichier.write("cellsize      5.000000000000 \n")
    fichier.write("NODATA_value  -9999.90 \n")
   
    for ligne in nom_fichier:
        for element in ligne:
            fichier.write(str(round(element,3))+" ")
        fichier.write("\n")
    fichier.close()
        
     
                    
                
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
    
   
   
     texte = np.genfromtxt("remplissage_cuvette/id_aire_aire_cuvette.txt", dtype=int, skip_header=1,delimiter=",")
    
     print(" /!\  ---------------CSV charge -------------------  /!\ \n")
     mnt =  np.genfromtxt("new_courbes/New_mnt/cDEM.asc", skip_header=6)
     print(" /!\  --------------- MNT charge -------------------  /!\ \n")
     identifiant =  np.genfromtxt("identifiant.asc", dtype=int, skip_header=6)
  
     print(" /!\  --------------- id charge et modifie -------------------  /!\ \n")
     
     
     AlgoRemplissageDepression(texte,mnt,identifiant)
     
     #iteration(vecteur,courant,mnt,identifiant)
    