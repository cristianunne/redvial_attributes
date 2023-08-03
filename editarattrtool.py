from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qgis._core import QgsProject, QgsEditFormConfig
from qgis.gui import *
from qgis.core import QgsFeature, QgsGeometry, QgsPoint
from qgis.gui import QgsAttributeDialog, QgsAttributeForm


from .fields_definitions import TableAtributosNames


class EditarAttrTool(QgsMapTool):
    select_ = pyqtSignal(object)

    def __init__(self, iface):
        QgsMapTool.__init__(self, iface.mapCanvas())

        self.iface = iface
        self.qpoint = None

        self.geom_Sel = None

        self.canvas = iface.mapCanvas()

        # our own fancy cursor
        self.cursor = QCursor(QPixmap(["16 16 3 1",
                                       "      c None",
                                       ".     c #FF0000",
                                       "+     c #FFFFFF",
                                       "                ",
                                       "       +.+      ",
                                       "      ++.++     ",
                                       "     +.....+    ",
                                       "    +.     .+   ",
                                       "   +.   .   .+  ",
                                       "  +.    .    .+ ",
                                       " ++.    .    .++",
                                       " ... ...+... ...",
                                       " ++.    .    .++",
                                       "  +.    .    .+ ",
                                       "   +.   .   .+  ",
                                       "   ++.     .+   ",
                                       "    ++.....+    ",
                                       "      ++.++     ",
                                       "       +.+      "]))


        #clase que maneja el nombre de los campos
        self.NAME_CAMPOS = TableAtributosNames()

        #las tablas necesarias para trabajar
        self.table_atributos = QgsProject.instance().mapLayersByName('atributos')[0]











    def canvasPressEvent(self, e):
        self.qpoint = self.toMapCoordinates(e.pos())

    def canvasMoveEvent(self, event):
        pass

    def canvasReleaseEvent(self, event):

        res = self.selecciona(self.qpoint)

        if res == True:

            #Guardo una copia de los atributos y luego comparo para saber cual fue cambiado fields
            #print(self.geom_Sel.fields()[0])
            #print(self.geom_Sel.id())
            #print(self.geom_Sel.attributes())

            #Con el ID de la geometria traigo los datos de la tabla
            #Guardo los atributos antiguos
            self.showFormAtributesTableById(self.geom_Sel.id())


        else:
            self.select_.emit(False)




    def showFormAtributesTableById(self, id_current):

        layer_table_atributes = self.table_atributos
        print("layer atributos")
        print(layer_table_atributes)


        #feat.fields().indexFromName('refermapa')
        feature_target = None

        idx_redvial = layer_table_atributes.fields().indexFromName(self.NAME_CAMPOS.REDVIAL_IDREDVIAL)

        for feat in layer_table_atributes.getFeatures():

            #feat id lo trago desde el campo redvial_idredvial

            id_feat = feat.attributes()[idx_redvial]
            idx_actual = feat.fields().indexFromName(self.NAME_CAMPOS.ACTUAL)

            if id_feat == id_current and feat.attributes()[idx_actual] == True:
                #ecnotro el objeto, o trabajo en el formulario
                feature_target = feat
                break

        #con el target abro lo que necesido
        old_attr = None
        new_attr = None
        if feature_target:

            #Guardo los atributos viejos
            old_attr = feature_target.attributes()

            new_feature = QgsFeature()
            #creo el formulario con los datos del feature current
            fields = layer_table_atributes.fields()
            new_feature.initAttributes(fields.count())
            provider = layer_table_atributes.dataProvider()

            idx_id = fields.indexFromName(self.NAME_CAMPOS.ID)

            max_id = layer_table_atributes.maximumValue(idx_id)

            #cargo los atributos del nuevo feature
            for i in range(fields.count()):

                if i != idx_id:
                    new_feature.setAttribute(i, old_attr[i])

                else:
                    new_feature.setAttribute(i, max_id + 1)


            layer_table_atributes.startEditing()
            att_form = QgsAttributeDialog(layer_table_atributes, new_feature, False)
            att_form.setMode(QgsAttributeEditorContext.AddFeatureMode)
            aa = att_form.exec_()

            if aa == 1:
                res_savenew = layer_table_atributes.commitChanges()
                #si salio ok, seteco

                if res_savenew:
                    layer_table_atributes.startEditing()

                    #cambio a false el anterior que quedo gaurdado en oldattr
                    idx_actual = fields.indexFromName(self.NAME_CAMPOS.ACTUAL)

                    #for del layer attr changed
                    max_id = layer_table_atributes.maximumValue(idx_id)
                    #print(max_id)
                    layer_table_atributes.changeAttributeValue(feature_target.id(), idx_actual, False)

                    res_savenew = layer_table_atributes.commitChanges()

                    if res_savenew == False:
                        layer_table_atributes.rollBack()


            else:
                layer_table_atributes.rollBack()







    def changeToFalseOldAttr(self, feature):
        pass


        #fsdfdsf


    def processChange(self, old_attr, new_attr):

        #Necesito todos las tablas que utilizare para evaluar el cambio

        #recorro los atributo
        for i in range(len(old_attr)):
            result = self.compareAttr(old_attr[i], new_attr[i])

            if result:
                self.processAttr()




    def processAttr(self):
        print(self.table_atributos)

    def compareAttr(self, old_at, new_at):

        if old_at != new_at:
            return True

        return False



    def addFeature(self, feature_select):

        #crear un feature y copiarle los datos que vienen del seleccionado
        feature = QgsFeature()



        layer_attr = self.table_atributos

        #traigo los campos
        fields = layer_attr.fields()
        feature.initAttributes(fields.count())
        provider = layer.dataProvider()

    

    def addFeatures_(self, feature, layer, field, pointValue):
        fields = layer.fields()
        feature.initAttributes(fields.count())
        provider = layer.dataProvider()
        for i in range(fields.count()):
            value = provider.defaultValue(i) if fields[i].name() != field else pointValue
            if value:
                feature.setAttribute(i, value)
                form = QgsAttributeDialog(layer, feature, False)
                form.setMode(QgsAttributeForm.AddFeatureMode)
                formSuppress = layer.editFormConfig().suppress()

                if formSuppress == QgsEditFormConfig.SuppressDefault:
                    if self.getSuppressOptions():  # this is calculated every time because user can switch options while using tool
                        layer.addFeature(feature, True)
                    else:
                        if not form.exec_():
                            feature.setAttributes(form.feature().attributes())
                elif formSuppress == QgsEditFormConfig.SuppressOff:
                    if not form.exec_():
                        feature.setAttributes(form.feature().attributes())
                else:
                    layer.addFeature(feature, True)


    def activate(self):
        self.canvas.setCursor(self.cursor)

    def deactivate(self):

        pass

    def selecciona(self, point):

        # Borro la seleccion actual
        mc = self.iface.mapCanvas()

        for layer in mc.layers():
            if layer.type() == layer.VectorLayer:
                layer.removeSelection()
            mc.refresh()

        pntGeom = QgsGeometry.fromPointXY(self.qpoint)
        pntBuffer = pntGeom.buffer((mc.mapUnitsPerPixel() * 2), 0)
        rectan = pntBuffer.boundingBox()
        cLayer = mc.currentLayer()
        cLayer.selectByRect(rectan)

        feats = cLayer.selectedFeatures()
        n = len(feats)

        # si n es mayor a 1 deselecciono todo los demas a expecion del primer elemento
        if n >= 1:
            if n > 1:
                i = 1

                while (i < n):
                    cLayer.deselect(feats[i].id())
                    i = i + 1

                self.geom_Sel = cLayer.selectedFeatures()[0]

            else:
                self.geom_Sel = cLayer.selectedFeatures()[0]

            mc.refresh()
            return True
        else:
            return False