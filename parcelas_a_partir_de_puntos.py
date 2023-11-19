#### Variables de entrada #####

#nombre de la capa  de puntos
capa = 'puntos'
#nombre de la capa de poligono
capa_poligono_nombre = 'parcela_100'
# carpeta de salida
salida = r"C:\Users\user\Downloads\POLIGONO\SHAPEFILE"

############### script #########################
from qgis.core import QgsProject, QgsField, QgsFeature, QgsGeometry, QgsVectorLayer, QgsVectorFileWriter, QgsFeatureRequest, QgsPointXY

# Obtén la capa de puntos del lienzo por su nombre
capa_puntos = QgsProject.instance().mapLayersByName(capa)[0]

# Verifica que la capa se haya cargado correctamente
if not capa_puntos.isValid():
    print("Error al cargar la capa de puntos.")
else:
    # Obtén el índice del campo field_1
    indice_campo = capa_puntos.fields().indexFromName('field_1')

    # Crea una lista de IDs ordenados por el campo field_1
    ids_ordenados = [f.id() for f in sorted(capa_puntos.getFeatures(QgsFeatureRequest().setFlags(QgsFeatureRequest.NoGeometry)), key=lambda x: int(x.attributes()[indice_campo]))]

    # Crea una capa de polígonos vacía
    capa_poligonos = QgsVectorLayer("Polygon?crs=" + capa_puntos.crs().authid(), capa_poligono_nombre, "memory")

    # Agrega campos a la capa de polígonos
    provider = capa_poligonos.dataProvider()
    provider.addAttributes([QgsField("ID", QVariant.Int)])

    # Inicia la edición de la capa de polígonos
    capa_poligonos.startEditing()

    # Itera sobre los puntos ordenados y crea un polígono
    puntos = [capa_puntos.getFeature(id).geometry().asPoint() for id in ids_ordenados]

    # Crea un polígono cerrado conectando cada punto con el siguiente
    poligono = QgsGeometry.fromPolygonXY([[QgsPointXY(p) for p in puntos] + [QgsPointXY(puntos[0])]])  # Agrega el primer punto al final para cerrar el polígono
    feature = QgsFeature()
    feature.setGeometry(poligono)
    feature.setAttributes([1])  # Puedes ajustar este valor según tus necesidades

    # Agrega el polígono a la capa de polígonos
    provider.addFeature(feature)

    # Finaliza la edición y actualiza la capa
    capa_poligonos.commitChanges()
    capa_poligonos.updateExtents()

    # Guarda la capa de polígonos en un archivo
    ruta_poligonos = salida + '/' + capa_poligono_nombre + '.shp'
    QgsVectorFileWriter.writeAsVectorFormat(capa_poligonos, ruta_poligonos, 'utf-8', capa_puntos.crs(), 'ESRI Shapefile')
    # Carga la capa de polígonos desde el archivo
    capa_poligonos_cargada = QgsVectorLayer(ruta_poligonos, capa_poligono_nombre, 'ogr')

    # Verifica que la capa se haya cargado correctamente
    if not capa_poligonos_cargada.isValid():
        print("Error al cargar la capa de polígonos.")
    else:
        # Agrega la capa de polígonos al proyecto
        QgsProject.instance().addMapLayer(capa_poligonos_cargada)

        print("Polígono creado con éxito y cargado en el proyecto.")


    print("Polígono creado con éxito y guardado en:", ruta_poligonos)
