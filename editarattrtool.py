from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qgis._core import QgsProject, QgsEditFormConfig
from qgis.gui import *
from qgis.core import QgsFeature, QgsGeometry, QgsPoint, Qgis
from qgis.gui import QgsAttributeDialog, QgsAttributeForm


import datetime

from .atributes_dialog import AtributesDialog
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

        self.table_atributos = None
        self.table_attr_changes = None

        self.initialize()



    def initialize(self):

        # controlo aca la existencia de las capas
        try:
            # las tablas necesarias para trabajar
            self.table_atributos = QgsProject.instance().mapLayersByName('atributos')[0]
            self.table_attr_changes = QgsProject.instance().mapLayersByName('attr_changes')[0]
            self.refermapa_category = QgsProject.instance().mapLayersByName('refermapa_category')[0]


        except (IndexError):

            self.iface.messageBar().pushMessage("Error",
                                                "Debe cargar la capa 'atributos', 'attr_changes' y 'refermapa_category'",
                                                Qgis.Critical, 5)



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
            #print(self.geom_Sel.attributes())

            # Con el ID de la geometria traigo los datos de la tabla
            # Guardo los atributos antiguos

            self.shoFormAttrTableById(self.geom_Sel)


        else:
            self.select_.emit(False)


    def shoFormAttrTableById(self, geom_Sel):
        id_current = geom_Sel.id()
        layer_table_atributes = self.table_atributos

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
            #hago una copia los fields
            fields = layer_table_atributes.fields()
            new_feature.initAttributes(fields.count())
            provider = layer_table_atributes.dataProvider()

            idx_id = fields.indexFromName(self.NAME_CAMPOS.ID)

            idx_modified = fields.indexFromName(self.NAME_CAMPOS.MODIFIED)

            max_id = layer_table_atributes.maximumValue(idx_id)

            tblattr_dp = layer_table_atributes.dataProvider()
            layer_table_atributes.startEditing()

            att_form = AtributesDialog(self.iface)

            result_attrdialog = None

            if att_form.initialize(geom_Sel, self.refermapa_category):
                result_attrdialog = att_form.exec()

            if result_attrdialog == 1:

                if self.compareData(att_form.feature_target, att_form.feature_data):

                    # si son diferentes hayq eu guardar en attributes

                    max_id = layer_table_atributes.maximumValue(idx_id)

                    att_form.feature_data[idx_id] = max_id + 1

                    tblattr_dp.addFeatures([att_form.feature_data])

                    res_savenew = layer_table_atributes.commitChanges()

                    if res_savenew:
                        # cambio a false el anterior que quedo gaurdado en oldattr
                        idx_actual = fields.indexFromName(self.NAME_CAMPOS.ACTUAL)
                        set_false = self.changeToFalseOldAttr(idx_actual, feature_target)


                        if set_false:
                            # si paso guardo los old y los new attr
                            max_id = layer_table_atributes.maximumValue(idx_id)
                            # limpiamos la seleccion y nos aseguramos que sea el ultimo id
                            layer_table_atributes.removeSelection()

                            layer_table_atributes.select(max_id)
                            feat_selected = layer_table_atributes.getSelectedFeatures()

                            feat_new = None

                            # Guardo los atributos viejos
                            for f in feat_selected:
                                feat_new = f
                                # print(feat_new.attributes())
                                break

                            new_attr = att_form.feature_data.attributes()



                            self.saveAllEventChangedInAttChangesTable(old_attr, new_attr, feat_new)

                        if set_false == False:
                            layer_table_atributes.rollBack()

                else:
                    print('sin cambios')

            else:
                layer_table_atributes.rollBack()




    def showFormAtributesTableById(self, geom_Sel):

        id_current = geom_Sel.id()
        layer_table_atributes = self.table_atributos


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

            tblattr_dp = layer_table_atributes.dataProvider()
            layer_table_atributes.startEditing()
            #att_form = QgsAttributeDialog(layer_table_atributes, new_feature, False)
            #att_form.setMode(QgsAttributeEditorContext.AddFeatureMode)


            att_form = AtributesDialog(self.iface)

            result_attrdialog = None

            if att_form.initialize(geom_Sel):

                result_attrdialog = att_form.exec()

            if result_attrdialog == 1:
                print(att_form.feature_target.attributes())
                print(att_form.feature_data.attributes())

                if self.compareData(att_form.feature_target, att_form.feature_data):

                    #si son diferentes hayq eu guardar en attributes

                    max_id = layer_table_atributes.maximumValue(idx_id)
                    att_form.feature_data[idx_id] = max_id

                    tblattr_dp.addFeatures([att_form.feature_data])

                    

                    res_savenew = layer_table_atributes.commitChanges()


                else:
                    print('sin cambios')

            else:
                layer_table_atributes.rollBack()





    def compareData(self, fselect, fdata):

        #utilizare la tabla attributes
        tabla_atributes_fields = TableAtributosNames()
        fields = fselect.fields()

        idx_tramo = fields.indexFromName(self.NAME_CAMPOS.TRAMO)
        idx_created = fields.indexFromName(self.NAME_CAMPOS.CREATED)

        idx_zona = fields.indexFromName(self.NAME_CAMPOS.ZONA)
        idx_cc = fields.indexFromName(self.NAME_CAMPOS.CC)
        idx_nombre = fields.indexFromName(self.NAME_CAMPOS.NOMBRE)
        idx_mantenim = fields.indexFromName(self.NAME_CAMPOS.MANTEMIM)
        idx_jurisdic = fields.indexFromName(self.NAME_CAMPOS.JURISDIC)
        idx_jerarq = fields.indexFromName(self.NAME_CAMPOS.JERARQ)
        idx_mat_calzad = fields.indexFromName(self.NAME_CAMPOS.MAT_CALZAD)
        idx_refermapa = fields.indexFromName(self.NAME_CAMPOS.REFERMAPA)
        idx_idsuma = fields.indexFromName(self.NAME_CAMPOS.IDSUMA)

        idx_tipo = fields.indexFromName(self.NAME_CAMPOS.TIPO)
        idx_observacion = fields.indexFromName(self.NAME_CAMPOS.OBSERVACION)
        idx_jerabr = fields.indexFromName(self.NAME_CAMPOS.JER_ABR)
        idx_ruleid = fields.indexFromName(self.NAME_CAMPOS.RULEID)

        idx_modified = fields.indexFromName(self.NAME_CAMPOS.MODIFIED)
        idx_fechaobra = fields.indexFromName(self.NAME_CAMPOS.FECHAOBRA)
        idx_autovia = fields.indexFromName(self.NAME_CAMPOS.AUTOVIA)


        if fselect[idx_tramo] != fdata[idx_tramo]:
            return True

        if fselect[idx_created] != fdata[idx_created]:
            return True

        if fselect[idx_zona] != fdata[idx_zona]:
            return True

        if fselect[idx_cc] != fdata[idx_cc]:
            return True

        if fselect[idx_nombre] != fdata[idx_nombre]:
            return True

        if fselect[idx_mantenim] != fdata[idx_mantenim]:
            return True

        if fselect[idx_jurisdic] != fdata[idx_jurisdic]:
            return True

        if fselect[idx_jerarq] != fdata[idx_jerarq]:
            return True

        if fselect[idx_mat_calzad] != fdata[idx_mat_calzad]:
            return True

        if fselect[idx_refermapa] != fdata[idx_refermapa]:
            return True

        if fselect[idx_idsuma] != fdata[idx_idsuma]:
            return True

        if fselect[idx_tipo] != fdata[idx_tipo]:
            return True

        if fselect[idx_observacion] != fdata[idx_observacion]:
            return True

        if fselect[idx_jerabr] != fdata[idx_jerabr]:
            return True

        if fselect[idx_ruleid] != fdata[idx_ruleid]:
            return True

        if fselect[idx_modified] != fdata[idx_modified]:
            return True

        if fselect[idx_fechaobra] != fdata[idx_fechaobra]:
            return True

        if fselect[idx_autovia] != fdata[idx_autovia]:
            return True

        return False



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

        new_feaures = []

        # recorro los atributo
        for i in range(len(old_attr)):

            if i != idx_modified and i != idx_id:
                result = self.compareAttr(old_attr[i], new_attr[i])
                if result:
                    #armo las variables a pasar
                    #nombre del field a pasar
                    field = self.selectField(feat_selected, i)

                    new_feat = self.processAttr(field, old_attr[i], new_attr[i], feat_selected.id())
                    new_feaures.append(new_feat)


        #guardo los cambios aqui

        # traigo la tabal attr change

        table_attrch = self.table_attr_changes.dataProvider()


        self.table_attr_changes.startEditing()

        res_add_feat = table_attrch.addFeatures(new_feaures)
        res_savenew = self.table_attr_changes.commitChanges()

        if res_savenew == False:
            self.table_attr_changes.rollBack()



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
        idx_created = fields.indexFromName(self.NAME_CAMPOS_ATTRCHANGES.CREATED)
        idx_atributos_idatributos = fields.indexFromName(self.NAME_CAMPOS_ATTRCHANGES.ATRIBUTOS_IDATRIBUTOS)

        new_feature = QgsFeature(fields)

        #proceso los campos individualmete
        new_feature[idx_atributo] = atributo
        new_feature[idx_oldvalue] = old_value
        new_feature[idx_newvalue] = new_value
        new_feature[idx_created] = str(datetime.datetime.now())

        new_feature[idx_atributos_idatributos] = atributos_idatributos

        return new_feature




    def compareAttr(self, old_at, new_at):

        if old_at != new_at:
            return True

        return False


    def activate(self):
        self.canvas.setCursor(self.cursor)

        #controlo el error


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


    def changeReferMapa(self, jurisd, jerar, mat_calzad, tipo):


        #Primero cargo



        if tipo == 'ACCESO':

            if mat_calzad == 'PAVIMENTO':
                return 'ACCESO PAVIMENTADO'

            elif mat_calzad == 'CONSOLIDADO':
                return 'ACCESO CONSOLIDADO'

            elif mat_calzad == 'TIERRA':
                return 'ACCESO DE TIERRA'

        if tipo == 'AUTOVIA':
            return 'AUTOVIA'

        elif tipo == 'CAMINO':
            if jurisd == 'PROVINCIAL' and jerar == 'TERCIARIA' and mat_calzad == 'TIERRA':
                return 'PROVINCIAL TERCIARIA DE TIERRA'

            elif jurisd == 'PROVINCIAL' and jerar == 'TERCIARIA' and mat_calzad == 'CONSOLIDADO':
                return 'PROVINCIAL TERCIARIA CONSOLIDADO'

            elif jurisd == 'PROVINCIAL' and jerar == 'TERCIARIA' and mat_calzad == 'PAVIMENTO':
                return 'PROVINCIAL TERCIARIA PAVIMENTADO'

        elif tipo == 'RUTA':
            if jurisd == 'PROVINCIAL' and jerar == 'PRIMARIA' and mat_calzad == 'TIERRA':
                return 'PROVINCIAL PRIMARIA DE TIERRA'

            elif jurisd == 'PROVINCIAL' and jerar == 'PRIMARIA' and mat_calzad == 'CONSOLIDADO':
                return 'PROVINCIAL PRIMARIA CONSOLIDADA'

            elif jurisd == 'PROVINCIAL' and jerar == 'PRIMARIA' and mat_calzad == 'PAVIMENTO':
                return 'PROVINCIAL PRIMARIA PAVIMENTADA'



            if jurisd == 'PROVINCIAL' and jerar == 'SECUNDARIA' and mat_calzad == 'CONSOLIDADO':
                return 'PROVINCIAL SECUNDARIA CONSOLIDADA'

            elif jurisd == 'PROVINCIAL' and jerar == 'SECUNDARIA' and mat_calzad == 'PAVIMENTO':
                return 'PROVINCIAL SECUNDARIA PAVIMENTADA'

            elif jurisd == 'PROVINCIAL' and jerar == 'SECUNDARIA' and mat_calzad == 'TIERRA':
                return 'PROVINCIAL SECUNDARIA DE TIERRA'

            if jurisd == 'NACIONAL' and jerar == 'TRONCAL' and mat_calzad == 'PAVIMENTO':
                return 'NACIONAL PAVIMENTADA'


        elif tipo == 'VINCULACION':

            if jurisd == 'PROVINCIAL' and jerar == 'TERCIARIA' and mat_calzad == 'TIERRA':
                return 'PROVINCIAL TERCIARIA DE TIERRA'

            elif jurisd == 'NACIONAL' and jerar == 'TRONCAL' and mat_calzad == 'PAVIMENTO':
                return 'NACIONAL PAVIMENTADA'

            elif jurisd == 'PROVINCIAL' and jerar == 'PRIMARIA' and mat_calzad == 'PAVIMENTO':
                return 'PROVINCIAL PRIMARIA PAVIMENTADA'










