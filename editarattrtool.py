from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qgis._core import QgsProject, QgsEditFormConfig
from qgis.gui import *
from qgis.core import QgsFeature, QgsGeometry, QgsPoint
from qgis.gui import QgsAttributeDialog, QgsAttributeForm

from .fields_definitions import TableAtributosNames, TableAttrChanges


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

        # clase que maneja el nombre de los campos
        self.NAME_CAMPOS = TableAtributosNames()

        self.NAME_CAMPOS_ATTRCHANGES = TableAttrChanges()

        # las tablas necesarias para trabajar
        self.table_atributos = QgsProject.instance().mapLayersByName('atributos')[0]
        self.table_attr_changes = QgsProject.instance().mapLayersByName('attr_changes')[0]

    def canvasPressEvent(self, e):
        self.qpoint = self.toMapCoordinates(e.pos())

    def canvasMoveEvent(self, event):
        pass

    def canvasReleaseEvent(self, event):

        res = self.selecciona(self.qpoint)

        if res == True:

            # Guardo una copia de los atributos y luego comparo para saber cual fue cambiado fields
            # print(self.geom_Sel.fields()[0])
            # print(self.geom_Sel.id())
            # print(self.geom_Sel.attributes())

            # Con el ID de la geometria traigo los datos de la tabla
            # Guardo los atributos antiguos
            self.showFormAtributesTableById(self.geom_Sel.id())


        else:
            self.select_.emit(False)

    def showFormAtributesTableById(self, id_current):

        layer_table_atributes = self.table_atributos
        print("layer atributos")
        print(layer_table_atributes)

        # feat.fields().indexFromName('refermapa')
        feature_target = None

        idx_redvial = layer_table_atributes.fields().indexFromName(self.NAME_CAMPOS.REDVIAL_IDREDVIAL)

        for feat in layer_table_atributes.getFeatures():

            # feat id lo trago desde el campo redvial_idredvial

            id_feat = feat.attributes()[idx_redvial]
            idx_actual = feat.fields().indexFromName(self.NAME_CAMPOS.ACTUAL)

            if id_feat == id_current and feat.attributes()[idx_actual] == True:
                # ecnotro el objeto, o trabajo en el formulario
                feature_target = feat
                break

        # con el target abro lo que necesido
        old_attr = None
        new_attr = None
        if feature_target:

            # Guardo los atributos viejos
            old_attr = feature_target.attributes()

            new_feature = QgsFeature()
            # creo el formulario con los datos del feature current
            fields = layer_table_atributes.fields()
            new_feature.initAttributes(fields.count())
            provider = layer_table_atributes.dataProvider()

            idx_id = fields.indexFromName(self.NAME_CAMPOS.ID)

            idx_modified = fields.indexFromName(self.NAME_CAMPOS.MODIFIED)

            max_id = layer_table_atributes.maximumValue(idx_id)

            # cargo los atributos del nuevo feature
            for i in range(fields.count()):

                if i != idx_id and i != idx_modified:
                    new_feature.setAttribute(i, old_attr[i])

                if i == idx_id:
                    new_feature.setAttribute(i, max_id + 1)

            layer_table_atributes.startEditing()
            att_form = QgsAttributeDialog(layer_table_atributes, new_feature, False)
            att_form.setMode(QgsAttributeEditorContext.AddFeatureMode)
            aa = att_form.exec_()

            if aa == 1:
                res_savenew = layer_table_atributes.commitChanges()
                # si salio ok, seteco

                if res_savenew:

                    # cambio a false el anterior que quedo gaurdado en oldattr
                    idx_actual = fields.indexFromName(self.NAME_CAMPOS.ACTUAL)

                    set_false = self.changeToFalseOldAttr(idx_actual, feature_target)

                    if set_false:

                        #si paso guardo los old y los new attr
                        max_id = layer_table_atributes.maximumValue(idx_id)

                        #limpiamos la seleccion y nos aseguramos que sea el ultimo id
                        layer_table_atributes.removeSelection()

                        layer_table_atributes.select(max_id)
                        feat_selected = layer_table_atributes.getSelectedFeatures()
                        feat_new = None
                        # Guardo los atributos viejos
                        for f in feat_selected:
                            feat_new = f
                            #print(feat_new.attributes())
                            break

                        new_attr = feat_new.attributes()
                        #print(feat_new)


                        self.saveAllEventChangedInAttChangesTable(old_attr, new_attr, feat_new)





                    if set_false == False:
                        layer_table_atributes.rollBack()


            else:
                layer_table_atributes.rollBack()

    def changeToFalseOldAttr(self, idx_actual, feature_target):

        self.table_atributos.startEditing()
        self.table_atributos.changeAttributeValue(feature_target.id(), idx_actual, False)
        res_savenew = self.table_atributos.commitChanges()

        if res_savenew:
            return True

        return False



    """
        Agrega los cambios en los atributos a la tabla que guarda individualmente
    """
    def saveAllEventChangedInAttChangesTable(self, old_attr, new_attr, feat_selected):

        # Necesito todos las tablas que utilizare para evaluar el cambio
        #obtengo los ids de los campos que no quiero evaluar
        fields = self.table_atributos.fields()

        idx_modified = fields.indexFromName(self.NAME_CAMPOS.MODIFIED)
        idx_id = fields.indexFromName(self.NAME_CAMPOS.ID)

        idx_actual = fields.indexFromName(self.NAME_CAMPOS.ACTUAL)


        # recorro los atributo
        for i in range(len(old_attr)):

            if i != idx_modified and i != idx_id:
                result = self.compareAttr(old_attr[i], new_attr[i])
                if result:
                    #armo las variables a pasar
                    #nombre del field a pasar
                    field = self.selectField(feat_selected, i)

                    self.processAttr(field, old_attr[i], new_attr[i], feat_selected.id())




    def selectField(self, feat_select, id_field):

        #selecciono el feat seleccionado
        field = feat_select.fields().names()[id_field]

        return field



    """
    atributo es el CAMPO que se actualizo QUE PERTENECE AL ID DEL NUEVO ATRIBUTO
    """
    def processAttr(self, atributo, old_value, new_value, atributos_idatributos):

        fields = self.table_attr_changes.fields()



        #obtengo los ids de los fiels para cargarlos
        idx_id = fields.indexFromName(self.NAME_CAMPOS_ATTRCHANGES.FID)
        idx_atributo = fields.indexFromName(self.NAME_CAMPOS_ATTRCHANGES.ATRIBUTO)
        idx_oldvalue = fields.indexFromName(self.NAME_CAMPOS_ATTRCHANGES.OLD_VALUE)
        idx_newvalue = fields.indexFromName(self.NAME_CAMPOS_ATTRCHANGES.NEW_VALUE)
        idx_atributos_idatributos = fields.indexFromName(self.NAME_CAMPOS_ATTRCHANGES.ATRIBUTOS_IDATRIBUTOS)

        new_feature = QgsFeature(fields)
        


        # cargo los atributos del nuevo feature
        for i in range(fields.count()):

            if i != idx_id:
                new_feature.setAttribute(i, old_attr[i])




        #traigo la tabal attr change

        self.table_attr_changes.startEditing()
        self.table_attr_changes.changeAttributeValue(feature_target.id(), idx_actual, False)
        res_savenew = self.table_atributos.commitChanges()


        print(atributo)
        print(old_value)
        print(new_value)
        print(atributos_idatributos)




    def compareAttr(self, old_at, new_at):

        if old_at != new_at:
            return True

        return False

    def addFeature(self, feature_select):

        # crear un feature y copiarle los datos que vienen del seleccionado
        feature = QgsFeature()

        layer_attr = self.table_atributos

        # traigo los campos
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
