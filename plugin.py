import numpy as np
import matplotlib.pyplot as plt
import os
from osgeo import gdal
import processing
import qgis
from qgis.analysis import QgsRasterCalculatorEntry, QgsRasterCalculator
from PyQt4.QtCore import QVariant
from qgis.core import QgsField, QgsExpression, QgsFeature
import math as m
from qgis.analysis import QgsZonalStatistics


###-------------------------------------Generation du MNT---------------------------------------------
#Executer le script python fourni

Charger le MNT existant
mnt= QgsRasterLayer("\\Users\\Anouk\\Documents\\Plugin2\\085_046.asc", "MNT")
if not mnt.isValid():
  print("Layer failed to load!")
mnt.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(mnt)

#Chargement du Masque
masque= QgsRasterLayer("\\Users\\Anouk\\Documents\\Plugin2\\ouv_ferm_12.asc", "masque")
if not masque.isValid():
  print("Layer failed to load!")
masque.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(masque)


#Smoothing du MNT
processing.runalg("saga:gaussianfilter",mnt,5,0,33,"\\Users\\Anouk\\Documents\\Plugin2\\smooth33.asc")
smooth33= QgsRasterLayer("\\Users\\Anouk\\Documents\\Plugin2\\smooth33.asc", "smooth33")
if not smooth33.isValid():
  print("Layer failed to load!")
smooth33.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(smooth33)

mnt_c=QgsRasterCalculatorEntry()
mnt_c.raster = mnt
mnt_c.bandNumber = 1
mnt_c.ref = 'mnt@1'

smooth_c=QgsRasterCalculatorEntry()
smooth_c.raster = smooth33
smooth_c.bandNumber = 1
smooth_c.ref = 'smooth33@1'

entries = [ mnt_c , smooth_c ]

final_output = '\\Users\\Anouk\\Documents\\Plugin2\\dif_smooth.tif' 
calc=QgsRasterCalculator ('%s - %s'%(smooth_c.ref, mnt_c.ref), final_output , 'GTiff', mnt.extent(), mnt.width(), mnt.height(), entries )
calc.processCalculation()

dif_smooth=QgsRasterLayer(final_output, "dif_smooth")
if not dif_smooth.isValid():
  print("Layer failed to load!")
dif_smooth.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(dif_smooth)

processing.runalg('gdalogr:rastercalculator', dif_smooth,'1',None,'1',None,'1',None,'1',None,'1',None,'1','A>1.5','0',1,None,'\\Users\\Anouk\\Documents\\Plugin2\\dif_sup_avt_masque.tif')
dif_sup=QgsRasterLayer('\\Users\\Anouk\\Documents\\Plugin2\\dif_sup_avt_masque.tif', "dif_sup_avt_masque")
if not dif_sup.isValid():
  print("Layer failed to load!")
dif_sup.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(dif_sup)

processing.runalg('gdalogr:rastercalculator', masque,'1',dif_sup,'1',None,'1',None,'1',None,'1',None,'1','B*(1-A)','0',5,None,'\\Users\\Anouk\\Documents\\Plugin2\\dif_sup_apres_masque.tif')
dif_sup2=QgsRasterLayer('\\Users\\Anouk\\Documents\\Plugin2\\dif_sup_apres_masque.tif', "dif_sup_apres_masque")
if not dif_sup2.isValid():
  print("Layer failed to load!")
dif_sup2.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(dif_sup2)

#Creation Shapefile
processing.runalg('gdalogr:polygonize', dif_sup2,'id','\\Users\\Anouk\\Documents\\Plugin2\\dep_pot.shp')
dep_pot=QgsVectorLayer('\\Users\\Anouk\\Documents\\Plugin2\\dep_pot.shp', "dep_pot", "ogr")
if not dep_pot.isValid():
  print("Layer failed to load!")
dep_pot.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(dep_pot)

#----------------- Tri depression

#ajout colonne de geometrie
processing.runalg('qgis:exportaddgeometrycolumns', dep_pot,0,'\\Users\\Anouk\\Documents\\Plugin2\\dep_pot_geom.shp')
dep_pot_geom=QgsVectorLayer('\\Users\\Anouk\\Documents\\Plugin2\\dep_pot_geom.shp', "dep_pot_geom", "ogr")
if not dep_pot_geom.isValid():
  print("Layer failed to load!")
dep_pot_geom.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(dep_pot_geom)

#supprimer entites area<300
processing.runalg('qgis:extractbyattribute', dep_pot_geom,'area',2,'300','\\Users\\Anouk\\Documents\\Plugin2\\dep_pot_area_300.shp')
dep_pot_area_300=QgsVectorLayer('\\Users\\Anouk\\Documents\\Plugin2\\dep_pot_area_300.shp', "dep_pot_area_300", "ogr")
if not dep_pot_area_300.isValid():
  print("Layer failed to load!")
dep_pot_area_300.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(dep_pot_area_300)


# Add a new attribute compacite in the output layer
provider = dep_pot_area_300.dataProvider()
provider.addAttributes([QgsField('comp', QVariant.Double)])
dep_pot_area_300.updateFields()

# Set the value of the 'comp' field for each feature
dep_pot_area_300.startEditing()
new_field_index = dep_pot_area_300.fieldNameIndex('comp')
for f in processing.features(dep_pot_area_300):
  dep_pot_area_300.changeAttributeValue(f.id(), new_field_index, (4*np.pi*f['area'])/(f['perimeter']*f['perimeter']))
dep_pot_area_300.commitChanges()

if not dep_pot_area_300.isValid():
  print("Layer failed to load!")
dep_pot_area_300.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(dep_pot_area_300)

processing.runalg('qgis:extractbyattribute', dep_pot_area_300,'comp',3,'0.33','\\Users\\Anouk\\Documents\\Plugin2\\dep_tri1.shp')
processing.runalg('qgis:extractbyattribute', dep_pot_area_300,'comp',4,'0.33','\\Users\\Anouk\\Documents\\Plugin2\\dep_pot_longues.shp')

dep_tri1=QgsVectorLayer('\\Users\\Anouk\\Documents\\Plugin2\\dep_tri1.shp', "dep_tri1", "ogr")
if not dep_tri1.isValid():
  print("Layer failed to load!")
dep_tri1.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(dep_tri1)

dep_pot_longues=QgsVectorLayer('\\Users\\Anouk\\Documents\\Plugin2\\dep_pot_longues.shp', "dep_pot_longues", "ogr")
if not dep_pot_longues.isValid():
  print("Layer failed to load!")
dep_pot_longues.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(dep_pot_longues)

##Etape de Triangulation - Tri sur les depressions longues
processing.runalg('qgis:polygoncentroids', dep_tri1,'\\Users\\Anouk\\Documents\\Plugin2\\centroide.shp')
centroide=QgsVectorLayer('\\Users\\Anouk\\Documents\\Plugin2\\centroide.shp', "centroide", "ogr")
if not centroide.isValid():
  print("Layer failed to load!")
centroide.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(centroide)

processing.runalg('qgis:voronoipolygons', centroide,0.0,'\\Users\\Anouk\\Documents\\Plugin2\\voronoi.shp')
voronoi=QgsVectorLayer('\\Users\\Anouk\\Documents\\Plugin2\\voronoi.shp', "voronoi", "ogr")
if not voronoi.isValid():
  print("Layer failed to load!")
voronoi.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(voronoi)


#ajout colonne de geometrie
processing.runalg('qgis:exportaddgeometrycolumns', voronoi,0,'\\Users\\Anouk\\Documents\\Plugin2\\voronoi_geom.shp')
voronoi_geom=QgsVectorLayer('\\Users\\Anouk\\Documents\\Plugin2\\voronoi_geom.shp', "voronoi_geom", "ogr")
if not voronoi_geom.isValid():
  print("Layer failed to load!")
voronoi_geom.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(voronoi_geom)

#supprimer entites area<60 000
processing.runalg('qgis:extractbyattribute', voronoi_geom,'area_1',4,'60000','\\Users\\Anouk\\Documents\\Plugin2\\voronoi_select60000.shp')
voronoi_select60000=QgsVectorLayer('\\Users\\Anouk\\Documents\\Plugin2\\voronoi_select60000.shp', "voronoi_select60000", "ogr")
if not voronoi_select60000.isValid():
  print("Layer failed to load!")
voronoi_select60000.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(voronoi_select60000)

processing.runalg('qgis:dissolve', voronoi_select60000,True,None,'\\Users\\Anouk\\Documents\\Plugin2\\voronoi_fusion.shp')
voronoi_fusion=QgsVectorLayer('\\Users\\Anouk\\Documents\\Plugin2\\voronoi_fusion.shp', "voronoi_fusion", "ogr")
if not voronoi_fusion.isValid():
  print("Layer failed to load!")
voronoi_fusion.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(voronoi_fusion)

processing.runalg('qgis:multiparttosingleparts', voronoi_fusion,'\\Users\\Anouk\\Documents\\Plugin2\\voronoi_fusion2.shp')
voronoi_fusion2=QgsVectorLayer('\\Users\\Anouk\\Documents\\Plugin2\\voronoi_fusion2.shp', "voronoi_fusion2", "ogr")
if not voronoi_fusion2.isValid():
  print("Layer failed to load!")
voronoi_fusion2.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(voronoi_fusion2)

#ajout colonne de geometrie
processing.runalg('qgis:exportaddgeometrycolumns', voronoi_fusion2,0,'\\Users\\Anouk\\Documents\\Plugin2\\voronoi_fusion2_geom.shp')
voronoi_fusion2_geom=QgsVectorLayer('\\Users\\Anouk\\Documents\\Plugin2\\voronoi_fusion2_geom.shp', "voronoi_fusion2_geom", "ogr")
if not voronoi_fusion2_geom.isValid():
  print("Layer failed to load!")
voronoi_fusion2_geom.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(voronoi_fusion2_geom)

#supprimer entites area<200 000
processing.runalg('qgis:extractbyattribute', voronoi_fusion2_geom,'area_2',2,'200000','\\Users\\Anouk\\Documents\\Plugin2\\voronoi_fusion3.shp')
voronoi_fusion3=QgsVectorLayer('\\Users\\Anouk\\Documents\\Plugin2\\voronoi_fusion3.shp', "voronoi_fusion3", "ogr")
if not voronoi_fusion3.isValid():
  print("Layer failed to load!")
voronoi_fusion3.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(voronoi_fusion3)

processing.runalg('qgis:fixeddistancebuffer', voronoi_fusion3,100.0,5.0,False,'\\Users\\Anouk\\Documents\\Plugin2\\voronoi_buffer.shp')
voronoi_buffer=QgsVectorLayer('\\Users\\Anouk\\Documents\\Plugin2\\voronoi_buffer.shp', "voronoi_buffer", "ogr")
if not voronoi_buffer.isValid():
  print("Layer failed to load!")
voronoi_buffer.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(voronoi_buffer)

processing.runalg('qgis:selectbylocation', dep_pot_longues,voronoi_buffer,['within'],0.0,0)

processing.runalg('qgis:saveselectedfeatures', dep_pot_longues,'\\Users\\Anouk\\Documents\\Plugin2\\dep_long_inside_buffer.shp')
dep_long_inside_buffer=QgsVectorLayer('\\Users\\Anouk\\Documents\\Plugin2\\dep_long_inside_buffer.shp', "dep_long_inside_buffer", "ogr")
if not dep_long_inside_buffer.isValid():
  print("Layer failed to load!")
dep_long_inside_buffer.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(dep_long_inside_buffer)

#supprimer certaines depressions longues
processing.runalg('qgis:extractbyattribute', dep_long_inside_buffer,'area',2,'700','\\Users\\Anouk\\Documents\\Plugin2\\dep_long_1.shp')
dep_long_1=QgsVectorLayer('\\Users\\Anouk\\Documents\\Plugin2\\dep_long_1.shp', "dep_long_1", "ogr")
if not dep_long_1.isValid():
  print("Layer failed to load!")
dep_long_1.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(dep_long_1)

processing.runalg('qgis:extractbyattribute', dep_long_1,'area',4,'9500','\\Users\\Anouk\\Documents\\Plugin2\\dep_long_2.shp')
dep_long_2=QgsVectorLayer('\\Users\\Anouk\\Documents\\Plugin2\\dep_long_2.shp', "dep_long_2", "ogr")
if not dep_long_2.isValid():
  print("Layer failed to load!")
dep_long_2.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(dep_long_2)

processing.runalg('qgis:extractbyattribute', dep_long_2,'comp',2,'0.11','\\Users\\Anouk\\Documents\\Plugin2\\dep_longues_finales.shp')
dep_longues_finales=QgsVectorLayer('\\Users\\Anouk\\Documents\\Plugin2\\dep_longues_finales.shp', "dep_longues_finales", "ogr")
if not dep_longues_finales.isValid():
  print("Layer failed to load!")
dep_longues_finales.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(dep_longues_finales)

#Tri depression ronde
processing.runalg('qgis:selectbylocation', dep_tri1,voronoi_buffer,['within'],0.0,0)

processing.runalg('qgis:saveselectedfeatures', dep_tri1,'\\Users\\Anouk\\Documents\\Plugin2\\dep_tri1_inside_final.shp')
dep_tri1_inside_final=QgsVectorLayer('\\Users\\Anouk\\Documents\\Plugin2\\dep_tri1_inside_final.shp', "dep_tri1_inside_final", "ogr")
if not dep_tri1_inside_final.isValid():
  print("Layer failed to load!")
dep_tri1_inside_final.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(dep_tri1_inside_final)

dep_tri1.invertSelection()

processing.runalg('qgis:saveselectedfeatures', dep_tri1,'\\Users\\Anouk\\Documents\\Plugin2\\dep_tri1_outside_buffer.shp')
dep_tri1_outside_buffer=QgsVectorLayer('\\Users\\Anouk\\Documents\\Plugin2\\dep_tri1_outside_buffer.shp', "dep_tri1_outside_buffer", "ogr")
if not dep_tri1_outside_buffer.isValid():
  print("Layer failed to load!")
dep_tri1_outside_buffer.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(dep_tri1_outside_buffer)

processing.runalg('qgis:extractbyattribute', dep_tri1_outside_buffer,'comp',2,'0.38','\\Users\\Anouk\\Documents\\Plugin2\\dep_tri1_outside_buffer1.shp')
dep_tri1_outside_buffer1=QgsVectorLayer('\\Users\\Anouk\\Documents\\Plugin2\\dep_tri1_outside_buffer1.shp', "dep_tri1_outside_buffer1", "ogr")
if not dep_tri1_outside_buffer1.isValid():
  print("Layer failed to load!")
dep_tri1_outside_buffer1.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(dep_tri1_outside_buffer1)

processing.runalg('qgis:extractbyattribute', dep_tri1_outside_buffer1,'area',2,'1000','\\Users\\Anouk\\Documents\\Plugin2\\dep_tri1_outside_final.shp')
dep_tri1_outside_final=QgsVectorLayer('\\Users\\Anouk\\Documents\\Plugin2\\dep_tri1_outside_final.shp', "dep_tri1_outside_final", "ogr")
if not dep_tri1_outside_final.isValid():
  print("Layer failed to load!")
dep_tri1_outside_final.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(dep_tri1_outside_final)

#Fusion des 3 couches de depressions
processing.runalg('qgis:mergevectorlayers', [dep_longues_finales,dep_tri1_inside_final,dep_tri1_outside_final],'\\Users\\Anouk\\Documents\\Plugin2\\dep_finales_avt_algo.shp')
dep_finales_avt_algo=QgsVectorLayer('\\Users\\Anouk\\Documents\\Plugin2\\dep_finales_avt_algo.shp', "dep_finales_avt_algo", "ogr")
if not dep_finales_avt_algo.isValid():
  print("Layer failed to load!")
dep_finales_avt_algo.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(dep_finales_avt_algo)

#Champ Id
fieldindex = dep_finales_avt_algo.fieldNameIndex("id")
i = 1
dep_finales_avt_algo.startEditing()
for feature in dep_finales_avt_algo.getFeatures():
    dep_finales_avt_algo.changeAttributeValue(feature.id(), dep_finales_avt_algo.fieldNameIndex("id"), i)
    i +=1
dep_finales_avt_algo.commitChanges()

QgsMapLayerRegistry.instance().addMapLayer(dep_finales_avt_algo)

#Statistique de zone
processing.runalg('qgis:zonalstatistics', mnt,1.0,dep_finales_avt_algo,'_',False,'\\Users\\Anouk\\Documents\\Plugin2\\dep_finales_avt_algo2.shp')
dep_finales_avt_algo2=QgsVectorLayer('\\Users\\Anouk\\Documents\\Plugin2\\dep_finales_avt_algo2.shp', "dep_finales_avt_algo2", "ogr")
if not dep_finales_avt_algo2.isValid():
  print("Layer failed to load!")
dep_finales_avt_algo2.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(dep_finales_avt_algo2)


processing.runalg('qgis:fixeddistancebuffer', dep_finales_avt_algo2,15.0,5.0,False,'\\Users\\Anouk\\Documents\\Plugin2\\buffer_dep_finales.shp')
buffer_dep_finales=QgsVectorLayer('\\Users\\Anouk\\Documents\\Plugin2\\buffer_dep_finales.shp', "buffer_dep_finales", "ogr")
if not buffer_dep_finales.isValid():
  print("Layer failed to load!")
buffer_dep_finales.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(buffer_dep_finales)


#Statistique de zone sur buffer
processing.runalg('qgis:zonalstatistics', mnt,1.0,buffer_dep_finales,'_b',False,'\\Users\\Anouk\\Documents\\Plugin2\\buffer_dep_finales2.shp')
buffer_dep_finales2=QgsVectorLayer('\\Users\\Anouk\\Documents\\Plugin2\\buffer_dep_finales2.shp', "buffer_dep_finales2", "ogr")
if not buffer_dep_finales2.isValid():
  print("Layer failed to load!")
buffer_dep_finales2.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(buffer_dep_finales2)


# Add a new attribute profondeur in the output layer
provider = buffer_dep_finales2.dataProvider()
provider.addAttributes([QgsField('prof', QVariant.Double)])
buffer_dep_finales2.updateFields()

# Set the value of the 'comp' field for each feature
buffer_dep_finales2.startEditing()
new_field_index = buffer_dep_finales2.fieldNameIndex('prof')
for f in processing.features(buffer_dep_finales2):
  buffer_dep_finales2.changeAttributeValue(f.id(), new_field_index, (f['_bmax']-f['_bmin']))
buffer_dep_finales2.commitChanges()


#Jointure
processing.runalg("qgis:joinattributestable",dep_finales_avt_algo2,buffer_dep_finales2,"id","id","\\Users\\Anouk\\Documents\\Plugin2\\dep_finales_avt_algo3.shp")
dep_finales_avt_algo3=QgsVectorLayer('\\Users\\Anouk\\Documents\\Plugin2\\dep_finales_avt_algo3.shp', "dep_finales_avt_algo3", "ogr")
if not dep_finales_avt_algo3.isValid():
  print("Layer failed to load!")
dep_finales_avt_algo3.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(dep_finales_avt_algo3)


#Contour autour des buffers
processing.runalg('qgis:polygonstolines', buffer_dep_finales2,'\\Users\\Anouk\\Documents\\Plugin2\\contour.shp')
contour=QgsVectorLayer('\\Users\\Anouk\\Documents\\Plugin2\\contour.shp', "contour", "ogr")
if not contour.isValid():
  print("Layer failed to load!")
contour.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(contour)

Buffer autour des contour
processing.runalg('qgis:fixeddistancebuffer', contour,1.0,5.0,False,'\\Users\\Anouk\\Documents\\Plugin2\\buffer_contour.shp')
buffer_contour=QgsVectorLayer('\\Users\\Anouk\\Documents\\Plugin2\\buffer_contour.shp', "buffer_contour", "ogr")
if not buffer_contour.isValid():
  print("Layer failed to load!")
buffer_contour.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(buffer_contour)


#Statistique de zone sur contour
processing.runalg('qgis:zonalstatistics', mnt,1.0,buffer_contour,'_c',False,'\\Users\\Anouk\\Documents\\Plugin2\\buffer_contour2.shp')
buffer_contour2=QgsVectorLayer('\\Users\\Anouk\\Documents\\Plugin2\\buffer_contour2.shp', "buffer_contour2", "ogr")
if not buffer_contour2.isValid():
  print("Layer failed to load!")
buffer_contour2.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(buffer_contour2)



# Add a new attribute max_moy in the output layer
provider = buffer_contour2.dataProvider()
provider.addAttributes([QgsField('max_moy', QVariant.Double)])
buffer_contour2.updateFields()

# Set the value of the 'max_moy' field for each feature
buffer_contour2.startEditing()
new_field_index = buffer_contour2.fieldNameIndex('max_moy')
for f in processing.features(buffer_contour2):
  buffer_contour2.changeAttributeValue(f.id(), new_field_index, (f['_cmax']-f['_cmean']))
buffer_contour2.commitChanges()



# Add a new attribute min_moy in the output layer
provider = buffer_contour2.dataProvider()
provider.addAttributes([QgsField('min_moy', QVariant.Double)])
buffer_contour2.updateFields()

# Set the value of the 'min_moy' field for each feature
buffer_contour2.startEditing()
new_field_index = buffer_contour2.fieldNameIndex('min_moy')
for f in processing.features(buffer_contour2):
  buffer_contour2.changeAttributeValue(f.id(), new_field_index, (f['_cmin']-f['_cmean']))
buffer_contour2.commitChanges()


# Add a new attribute min_dedep in the output layer
provider = buffer_contour2.dataProvider()
provider.addAttributes([QgsField('mincdep', QVariant.Double)])
buffer_contour2.updateFields()

# Set the value of the 'min c dep' field for each feature
buffer_contour2.startEditing()
new_field_index = buffer_contour2.fieldNameIndex('mincdep')
for f in processing.features(buffer_contour2):
  buffer_contour2.changeAttributeValue(f.id(), new_field_index, (f['_cmin']-f['_min']))
buffer_contour2.commitChanges()
#


Jointure
processing.runalg("qgis:joinattributestable",dep_finales_avt_algo3,buffer_contour2,"id","id","\\Users\\Anouk\\Documents\\Plugin2\\dep_finales_avt_algo4.shp")
dep_finales_avt_algo4=QgsVectorLayer('\\Users\\Anouk\\Documents\\Plugin2\\dep_finales_avt_algo4.shp', "dep_finales_avt_algo4", "ogr")
if not dep_finales_avt_algo4.isValid():
  print("Layer failed to load!")
dep_finales_avt_algo4.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(dep_finales_avt_algo4)


processing.runalg('qgis:extractbyattribute', dep_finales_avt_algo4,'mincdep',3,'0.8','\\Users\\Anouk\\Documents\\Plugin2\\dep_finales.shp')
dep_finales=QgsVectorLayer('\\Users\\Anouk\\Documents\\Plugin2\\dep_finales.shp', "dep_finales", "ogr")
if not dep_finales.isValid():
  print("Layer failed to load!")
dep_finales.setCrs(QgsCoordinateReferenceSystem(2154))
QgsMapLayerRegistry.instance().addMapLayer(dep_finales)

field_ids = []
# Fieldnames to keep
fieldnames = set(['id','area','comp','_min','_max','_count','_mean','_std','_unique','_range','_var','_median','_mode','perimeter_','_bmin','_bmax','_bcount','_bmean','_bstd','_bunique','_brange','_bvar','_bmedian','_bmode','prof','_cmin','_cmax','_ccount','_cmean','_cstd','_cunique','_crange','_cvar','_cmedian','_cmode','max_moy','min_moy','mincdep'])
for field in dep_finales.fields():
    if field.name() not in fieldnames:
      field_ids.append(dep_finales.fieldNameIndex(field.name()))

# Delete the fields in the attribute table through their corresponding index in the list.
dep_finales.dataProvider().deleteAttributes(field_ids)
dep_finales.updateFields()



