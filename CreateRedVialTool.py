from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qgis._core import QgsProject, QgsEditFormConfig
from qgis.gui import *
from qgis.core import QgsFeature, QgsGeometry, QgsPoint, Qgis
from qgis.gui import QgsAttributeDialog, QgsAttributeForm


import datetime

from .fields_definitions import FieldsReferMapCategory


from .atributes_dialog import AtributesDialog

class CreateRedVialTool():

    def __init__(self, iface, toolbar):
        self.iface = iface
        self.toolbar = toolbar
        self.canvas = self.iface.mapCanvas()

        self.result = False

        # Create actions
        self.created_tool = QAction(QIcon(":/plugins/redvial_attributes/red_vial.png"),
                                  QCoreApplication.translate("RedVialAttributes", "Crear la Capa Red Vial Map"),
                                  self.iface.mainWindow())

        self.created_tool.setCheckable(True)

        # Connect to signals for button behaviour
        self.created_tool.triggered.connect(self.action_prueba)

        # Add actions to the toolbar
        self.toolbar.addAction(self.created_tool)



    def action_prueba(self):

        """layer_table_atributes = QgsProject.instance().mapLayersByName('atributos')[0]
        new_feature = QgsFeature()
        # creo el formulario con los datos del feature current
        fields = layer_table_atributes.fields()
        new_feature.initAttributes(fields.count())

        layer_table_atributes.startEditing()
        att_form = QgsAttributeDialog(layer_table_atributes, new_feature, False)
        att_form.setMode(QgsAttributeEditorContext.AddFeatureMode)

        print(att_form.attributeForm())

        aa = att_form.exec_()

        print(FieldsReferMapCategory.FID.value)
        print(FieldsReferMapCategory.TIPO.value)
        print(FieldsReferMapCategory.JERARQUIA.value)
        print(FieldsReferMapCategory.MATERIAL.value)
        print(FieldsReferMapCategory.CATEGORIA.value)"""
        self.redvial = QgsProject.instance().mapLayersByName('red_vial')[0]
        self.table_atributos = QgsProject.instance().mapLayersByName('atributos')[0]

        feature = self.redvial.selectedFeatures()[0]


        attr_dialog = AtributesDialog(self.iface)


        result_attrdialog = None

        if attr_dialog.initialize(feature):

                result_attrdialog = attr_dialog.exec()

        if result_attrdialog == 1:
            print(attr_dialog.feature_target.attributes())
            print(attr_dialog.feature_data.attributes())







    def act_created_tool(self):

        if self.showdialog():
            self.processRedVialMap()

    def processRedVialMap(self):

        cLayer = self.iface.mapCanvas().currentLayer()
        provider = cLayer.dataProvider()

        print(provider.fields().names())

        URI = "multilinestringZM?crs=epsg:" + str(22175) + "&index=yes"
        name = "memlayer"
        # create memory layer
        mem_layer = QgsVectorLayer(URI,
                                   name,
                                   "memory")

        mem_layer_provider = mem_layer.dataProvider()

        mem_layer.startEditing()

        f = QgsFields()
        f.append(QgsField("name", QVariant.String))
        f.append(QgsField("folders", QVariant.String))
        f.append(QgsField("description", QVariant.String))
        # add fields
        mem_layer_provider.addAttributes(f)

        #Recorro red vial y copio

        red_vial_layer = QgsProject.instance().mapLayersByName('red_vial')[0]


        features = []

        i = 0
        for feat in red_vial_layer.getFeatures():

            feat_ = QgsFeature(f)


            feat_.setGeometry(feat.geometry())
            feat_[0] = i

            print(feat_[0])

            features.append(feat_)
            i = i + 1
            if i == 5:
                break


        mem_layer_provider.addFeatures(features)
        mem_layer.commitChanges()

        QgsProject.instance().addMapLayer(mem_layer)


        #print(provider.crs())
        ###writer = QgsVectorFileWriter("output_path_and_name.shp", provider.encoding(), provider.fields(),
        ##                          Qgis.WKBMultiLineString, provider.crs())


    def showdialog(self):
        """msg = QMessageBox()
            msg.setIcon(QMessageBox.Question)

            msg.setText("Insertar CL_NODO?")
            msg.setWindowTitle("Insertar CL_NODOS")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            retval = msg.exec_()"""

        retval = QMessageBox.question(self.iface.mainWindow(),
                                          "Consulta", "Exportar a Red Vial Map?",
                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        val = None

        if retval == QMessageBox.Yes:

            val = True
        else:
            val = False

        return val
