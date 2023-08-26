

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qgis.core import *
from qgis.gui import QgsAttributeDialog
from qgis.gui import QgsMessageBar

#Traigo la herramienta de seleccion
from .editarattrtool import EditarAttrTool


class ModifiedAtributeTool():

    def __init__(self, iface, toolbar):
        self.iface = iface
        self.toolbar = toolbar
        self.canvas = self.iface.mapCanvas()

        self.table_atributos = None
        self.table_attr_changes = None


        self.result = False

        # Create actions
        self.md_attr = QAction(QIcon(":/plugins/redvial_attributes/editar_attr.png"),
                               QCoreApplication.translate("RedVialAttributes", "Modificar Atributos"), self.iface.mainWindow())

        self.md_attr.setCheckable(True)

        # Connect to signals for button behaviour
        self.md_attr.triggered.connect(self.act_modified_attr)

        # Add actions to the toolbar
        self.toolbar.addAction(self.md_attr)

        #self.iface.addPluginToMenu(self.tr('&Modificar Atributos'), self.md_attr)


        #self.iface.addToolBarIcon(self.md_attr)


        # Get the tool
        self.tool = EditarAttrTool(self.iface)

    def act_modified_attr(self):

        if self.md_attr.isChecked():

            #controlo aca la existencia de las capas
            try:

                # las tablas necesarias para trabajar
                self.table_atributos = QgsProject.instance().mapLayersByName('atributos')[0]
                self.table_attr_changes = QgsProject.instance().mapLayersByName('attr_changes')[0]

                self.canvas.setMapTool(self.tool)
                self.tool.select_.connect(self.alm_res)
                self.activate()

                if self.result != False:
                    print(self.result)

                else:
                    pass


            except (IndexError):

                self.iface.messageBar().pushMessage("Error", "Debe cargar la capa 'atributos', 'atributos' y 'attr_changes'", Qgis.Critical, 5)

                self.md_attr.setChecked(False)



        else:
            self.deactivate()
            self.unsetTool()

    def alm_res(self, result):

        self.result = result

    def unsetTool(self):
        mc = self.canvas
        mc.unsetMapTool(self.tool)

    def activate(self):

        print("Activo la herramienta Modificar Atributos")


        #compruebo que las capas esten presentes sino desactivo e informo



    def deactivate(self):

        mc = self.canvas

        layer = self.canvas.currentLayer()

        for la in mc.layers():
            if layer.type() == layer.VectorLayer:
                layer.removeSelection()
            mc.refresh()
        print("Desactivo la Herramienta de Modificar Atributos")

    def tr(self, message):
        return QCoreApplication.translate('RedVialAttributes', message)