"""
Fonctions codées mais finalement non utilisées pour le projet


@author  : hugo boulze, schleich
@copyright : IGN, ENSG 2019
@version : 1.0
@email   : hugo.boulze@ensg.eu, anouk.schleich@ensg.eu


"""


# ----------------------------------------- IMPORTS -------------------------------------------------

import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------------------------------


"""

Trace le profil du terrain sur une certaine direction (codé uniquement pour la direction "est")

Entrées :
    - mnt             : MNT
    - direction       : direction de la coupe (est,nord,sud,ouest)
    - ligne_origine   : abcisse du point de départ de la coupe
    - colonne_origine : ordonnée du point de départ de la coupe
    
Sortie :
    - un graphe de l'évolution de l'altitude en fonction du pixel
    

"""

def morpho_terrain(mnt, direction, ligne_origine, colonne_origine):
    
    taille_mnt = len(mnt[0])
    altitude_y = []
    valeur_pixel= []
    
    if direction == "est":
        accu=colonne_origine
        while accu < taille_mnt:
            altitude_y.append(mnt[ligne_origine][accu])
            valeur_pixel.append(accu)        
            accu+=1
    plt.plot(valeur_pixel, altitude_y)
    plt.show()
    
  
"""

Défini le chemin d'un thalweg à partir d'un pixel origine (foncion récursive)

Entrées :
    - mnt         : MNT
    - ligne       : abcisse du pixel origine
    - colonne     : ordonnée du pixel origine
    - masque      : grille dans laquelle pour chaque pixel est indiqué le nombre de thalweg passant par lui
    - max_courant : défini la longueur actuelle du thalweg
    - max_points  : définir la longueur maximale du thalweg
    
Sortie :
    - un graphe de l'évolution de l'altitude en fonction du pixel
    

    
"""
    
def masque_thalweg(mnt,ligne,colonne,masque,max_courant,max_points):
    if max_courant == max_points+1:
        return masque
    else:
        voisins = voisinage(mnt,ligne,colonne)
        min_voisin = min(voisins)
        
        #si altitude min sup au pixel, pas de possiilit de continuer le twalvhg o retounre donc l'ancien masque
        if min_voisin[0] > mnt[ligne][colonne]:
            return masque
        
        
        ligne_voisin = min_voisin[1]
        colonne_voisin = min_voisin[2]
        
        #on incrémente le passage de 1 au passage
        masque[ligne_voisin][colonne_voisin] +=1
        
        #on augmente le max courant et on réaaplique sur les voisins du min des voisins
        max_courant +=1
    
        #J'ai rajouté le return
        return masque_thalweg(mnt,ligne_voisin,colonne_voisin,masque,max_courant,max_points)
    
    
 
    
"""

Défini les thalwegs du mnt


"""

def thalweg_MNT(mnt,max_points):
    
    taille_mnt = len(mnt[0])
    masque = np.zeros((taille_mnt,taille_mnt), dtype=int)
    
    
    print("---------- Creation du masque -------      \n\n")
    
    
    for i in range (0,taille_mnt):    # on parcourt les lignes
        for j in range(0,taille_mnt):  
            masque[i][j] +=1
            #cf return modifie masque_thalweg
            masque = masque_thalweg(mnt,i,j,masque,1,max_points)
     
    
    
    print("     /!\ Masque cree avec succes /!\      \n\n")
    
    ecriture_fichier(masque,"thalweg/dalle_2040_2720/thalweg_pas_50.asc")
    

    
"""


Lisse le MNT en attribuant à un mixel la moyenne de l'ensemble de ses voisins et de lui meme



"""  
    

def smoothing(mnt, sigma):
    taille_mnt = len(mnt[0])
    mnt_smoothing = np.zeros((taille_mnt,taille_mnt), dtype=float)
 
    print("--------------  Smoothing  -------------      \n\n")
    
    for i in range (0,taille_mnt):    # on parcourt les lignes
        for j in range(0,taille_mnt):  
          
           voisins = voisinage(mnt,i,j)
           taille = len(voisins)
           somme_voisins = 0
           for k in range (taille):
               somme_voisins += voisins[k][0] 
           moyenne = (somme_voisins+mnt[i][j])/(taille+1)
           
           mnt_smoothing[i][j] = moyenne
    
    print("        /!\ smoothing effectue avec succes /!\      \n\n")
    
    ecriture_fichier(mnt_smoothing,"smoothing_MNT.asc")
    
 
"""


Decoupe le MNT en plusieurs dalles afin de diminuer les temps de calculs



"""


                
def decoupage_MNT(mnt, taille_maille):
    
    taille_mnt = len(mnt[0])

    if taille_mnt%taille_maille !=0:                        #si le masque n'est pas un diviseur de la taille du mnt on arrete
        return "Taille de maille invalide"
    
    print("  \n\n     /!\ Taille de maille valide /!\      \n\n  ")
    
    print("--------- Création du maillage -----------  \n\n")
    
    accu_Y = 0
    
    for i in range(0,taille_mnt,taille_maille):
        
        accu_X = 0 #compte le nombre de mailles sur X
        
        for j in range(0,taille_mnt,taille_maille):
            maille = np.zeros((taille_maille,taille_maille), dtype=float)
            for k in range(0,taille_maille):
                for l in range(0,taille_maille):
                    maille[k][l] = mnt[i+k][j+l]    
                    
                    
            xll_corner =  899800.000000 +accu_X*taille_maille*5
            yll_corner =  6639800.000000 + (4080-taille_maille)*5  -accu_Y*taille_maille*5      
                
                    
            print("     /!\ Maillage cree avec succes /!\      \n\n")
    
            fichier = open("dalles_diff_sup/dalle"+str(i)+"_"+str(j)+".asc",'w')
   
            print("----------- Ecriture en cours ------------  \n\n")
    
            fichier.write("ncols         " + str(taille_maille) +"\n")
            fichier.write("nrows         " + str(taille_maille) +" \n")
            fichier.write("xllcorner     "+ str(xll_corner)+" \n") 
            fichier.write("yllcorner     "+ str(yll_corner)+" \n") 
            fichier.write("cellsize      5.000000000000 \n")
            fichier.write("NODATA_value  -9999.90 \n")
        
            for ligne in maille:
                for element in ligne:
                    fichier.write(str(element)+" ")
                fichier.write("\n")
            fichier.close()
            
            accu_X +=1
            
        accu_Y +=1
        

        

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
        