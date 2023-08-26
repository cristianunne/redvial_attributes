
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qgis.core import *
from qgis.core import QgsFeature, QgsGeometry, QgsPoint
from qgis.gui import QgsAttributeDialog
from qgis.gui import QgsMessageBar
import datetime

from .fields_definitions import TableRedVialHistory



class HistorySegmentTool():

    def __init__(self, iface, toolbar):
        self.iface = iface
        self.toolbar = toolbar
        self.canvas = self.iface.mapCanvas()

        self.result = False

        # Create actions
        self.histo_tool = QAction(QIcon(":/plugins/redvial_attributes/history_line.png"),
                               QCoreApplication.translate("RedVialAttributes", "Copiar Segmento a Red Vial History"),
                               self.iface.mainWindow())

        self.histo_tool.setCheckable(True)

        # Connect to signals for button behaviour
        self.histo_tool.triggered.connect(self.act_history_tool)

        # Add actions to the toolbar
        self.toolbar.addAction(self.histo_tool)



    def act_history_tool(self):
        if self.histo_tool.isChecked():
            try:
                #tengo que tener seleccionado un elemento de RED VIAL
                self.redvial = QgsProject.instance().mapLayersByName('red_vial')[0]
                self.redvial_history = QgsProject.instance().mapLayersByName('red_vial_history')[0]

                self.proccessHistorySegment()


            except (IndexError):

                self.iface.messageBar().pushMessage("Error",
                                                    "Debe cargar la capa 'Red Vial' y 'Red Vial History'",
                                                    Qgis.Critical, 5)

                self.histo_tool.setChecked(False)


    def proccessHistorySegment(self):

        # verifico que haya al menos un elemento seleccionado
        redvial_segment_select = self.redvial.selectedFeatures()

        if (len(redvial_segment_select) >= 1):

            segment_select = redvial_segment_select[0]

            #Ahora hago una copia a la tabla history
            #utilizo un formulario para consultar si ejecutar o no

            if self.showdialog():
                self.saveSegmentToHistory(segment_select)
                self.histo_tool.setChecked(False)

            else:
                self.histo_tool.setChecked(False)





        else:
            self.iface.messageBar().pushMessage("Error",
                                                "Debe seleccionar un Segmento de la Red Vial",
                                                Qgis.Critical, 5)

            self.histo_tool.setChecked(False)


    def saveSegmentToHistory(self, segment_select):


        red_vial_fields = TableRedVialHistory()

        fields = self.redvial_history.fields()

        idx_fecha = fields.indexFromName(red_vial_fields.FECHA)
        idx_idrigen = fields.indexFromName(red_vial_fields.ID_ORIGEN)


        segment_history = QgsFeature(fields)
        segment_history.setGeometry(segment_select.geometry())

        # proceso los campos individualmete
        segment_history[idx_fecha] = str(datetime.datetime.now())
        segment_history[idx_idrigen] = segment_select.id()

        table_redvial_history = self.redvial_history.dataProvider()
        self.redvial_history.startEditing()

        res_add_feat = table_redvial_history.addFeature(segment_history)

        res_savenew = self.redvial_history.commitChanges()

        if res_savenew == False:
            self.table_redvial_history.rollBack()

    def showdialog(self):
        """msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)

        msg.setText("Insertar CL_NODO?")
        msg.setWindowTitle("Insertar CL_NODOS")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        retval = msg.exec_()"""

        retval = QMessageBox.question(self.iface.mainWindow(),
                                      "Question", "Agregar el Segmento a Red Vial History?",
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        val = None

        if retval == QMessageBox.Yes:

            val = True
        else:
            val = False

        return val


