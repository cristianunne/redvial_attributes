import os

from PyQt5 import uic, QtGui, QtWidgets, QtCore
from PyQt5.QtCore import QDateTime
from qgis._core import QgsProject
from qgis.core import *

from .fields_definitions import FieldsReferMapCategory, TableAtributosNames

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'atributes_dialog_base.ui'))


class AtributesDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, iface, parent=None):
        """Constructor."""
        super(AtributesDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.iface = iface

        # agrego los validadores
        self.le_ruleid.setValidator(QtGui.QIntValidator())

        self.feature_data = QgsFeature()
        self.is_changed = False

    # https://wiki.qt.io/Qt_for_Python_Signals_and_Slots

    def initialize(self, feature, refermapa_category):
        if feature:

            self.refermapa_category = refermapa_category

            if self.setFeatureData(feature):
                if self.setDataToForms():
                    self._loadSingalsForms()
                    return True
           #self.loadAllData():

        return False

    def _loadSingalsForms(self):
        self.le_tramo.textChanged.connect(self._signalLeTramo)
        self.dt_created.valueChanged.connect(self._signalDtCreated)
        self.le_zona.textChanged.connect(self._signalLeZona)
        self.le_cc.textChanged.connect(self._signalLeCC)
        self.le_nombre.textChanged.connect(self._signalLe_nombre)
        self.le_manten.textChanged.connect(self._signalLe_manten)
        self.cb_jurisd.currentTextChanged.connect(self._signalCb_jurisd)
        self.cb_jerarq.currentTextChanged.connect(self._signalCb_jerarq)
        self.cb_mat_calz.currentTextChanged.connect(self._signalCb_mat_calz)
        self.le_refermapa.textChanged.connect(self._signalLe_refermapa)
        self.le_idsuma.textChanged.connect(self._signalLe_idsuma)
        self.cb_tipo.currentTextChanged.connect(self._signalCb_tipo)
        self.te_observacion.textChanged.connect(self._signalTe_observacion)
        self.le_jer_abr.textChanged.connect(self._signalLe_jer_abr)
        self.le_ruleid.textChanged.connect(self._signalLe_ruleid)

        self.dt_modified.valueChanged.connect(self._signalDt_modified)

        self.dt_fecha_obra.valueChanged.connect(self._signalDt_fecha_obra)

        self.checkb_autovia.toggled.connect(self._signalCheckb_autovia)  # checkBoxChecked

    def setReferMapa2(self):
        text_tipo = str(self.cb_tipo.currentText())
        text_mat_calz = str(self.cb_mat_calz.currentText())

        fields = self.refermapa_category.fields()
        idx_categoria = fields.indexFromName(FieldsReferMapCategory.CATEGORIA.value)
        idx_tipo = fields.indexFromName(FieldsReferMapCategory.TIPO.value)
        idx_material = fields.indexFromName(FieldsReferMapCategory.MATERIAL.value)

        # traigo la clase que maneja los id de los fiels
        attributes_fields = TableAtributosNames()

        """idx_tipo = self.feature_data.fields().indexFromName(attributes_fields.TIPO)
        idx_jurisdiccion = self.feature_data.fields().indexFromName(attributes_fields.JURISDIC)
        idx_jerarquia = self.feature_data.fields().indexFromName(attributes_fields.JERARQ)
        idx_material = self.feature_data.fields().indexFromName(attributes_fields.MAT_CALZAD)"""

        for feat in self.refermapa_category.getFeatures():
            pass

        print(self.feature_data.attributes())

    def setReferMapa(self):

        text_tipo = str(self.cb_tipo.currentText())
        text_mat_calz = str(self.cb_mat_calz.currentText())
        text_jurisdiccion = str(self.cb_jurisd.currentText())
        text_jerarquia = str(self.cb_jerarq.currentText())

        fields = self.refermapa_category.fields()
        idx_categoria = fields.indexFromName(FieldsReferMapCategory.CATEGORIA.value)
        idx_tipo = fields.indexFromName(FieldsReferMapCategory.TIPO.value)
        idx_material = fields.indexFromName(FieldsReferMapCategory.MATERIAL.value)
        idx_jurisdiccion = fields.indexFromName(FieldsReferMapCategory.JURISDICCION.value)
        idx_jerarquia = fields.indexFromName(FieldsReferMapCategory.JERARQUIA.value)

        if text_tipo == "ACCESO":

            if str(text_mat_calz) == "PAVIMENTO":

                for feat in self.refermapa_category.getFeatures():
                    if str(feat.attributes()[idx_material]) == "PAVIMENTO" and str(
                            feat.attributes()[idx_tipo]) == "ACCESO":
                        self.le_refermapa.setText('')
                        self.le_refermapa.setText(str(feat.attributes()[idx_categoria]))
                        print(feat.attributes()[idx_material])

                # self.le_refermapa.setText()

            elif str(text_mat_calz) == "CONSOLIDADO":

                for feat in self.refermapa_category.getFeatures():
                    if str(feat.attributes()[idx_material]) == "CONSOLIDADO" and str(
                            feat.attributes()[idx_tipo]) == "ACCESO":
                        print(feat.attributes()[idx_material])
                        self.le_refermapa.setText(str(feat.attributes()[idx_categoria]))



            elif str(text_mat_calz) == "TIERRA":

                for feat in self.refermapa_category.getFeatures():
                    if str(feat.attributes()[idx_material]) == "TIERRA" and str(
                            feat.attributes()[idx_tipo]) == "ACCESO":
                        print(feat.attributes()[idx_categoria])
                        self.le_refermapa.setText(str(feat.attributes()[idx_categoria]))

            elif str(text_mat_calz) == "NULL":
                self.le_refermapa.setText(str(''))

        elif text_tipo == "AUTOVIA":
            self.le_refermapa.setText(str('AUTOVIA'))
            # seteo el texto de los otros inputs tmb
            self.cb_tipo.setCurrentText(str('AUTOVIA'))
            self.cb_jurisd.setCurrentText(str('NACIONAL'))
            self.cb_jerarq.setCurrentText(str('TRONCAL'))
            self.cb_mat_calz.setCurrentText(str('PAVIMENTO'))
            self.checkb_autovia.setChecked(True)

        elif self.checkb_autovia.isChecked():
            self.le_refermapa.setText(str('AUTOVIA'))
            # seteo el texto de los otros inputs tmb
            self.cb_tipo.setCurrentText(str('AUTOVIA'))
            self.cb_jurisd.setCurrentText(str('NACIONAL'))
            self.cb_jerarq.setCurrentText(str('TRONCAL'))
            self.cb_mat_calz.setCurrentText(str('PAVIMENTO'))

        else:
            # tengo un feat con los datos
            for feat in self.refermapa_category.getFeatures():

                # compurebo por la autovia
                if (text_jurisdiccion == 'NACIONAL' and text_jerarquia == 'TRONCAL'
                        and text_mat_calz == 'PAVIMENTO' and self.checkb_autovia.isChecked()):
                    self.le_refermapa.setText(str('AUTOVIA'))

                elif (text_jurisdiccion == 'NACIONAL' and text_jerarquia == 'TRONCAL'
                      and text_mat_calz == 'PAVIMENTO' and self.checkb_autovia.isChecked() == False):

                    if (text_jurisdiccion == str(feat.attributes()[idx_jurisdiccion]) and
                            text_jerarquia == str(feat.attributes()[idx_jerarquia]) and
                            text_mat_calz == str(feat.attributes()[idx_material]) and
                            str(feat.attributes()[idx_tipo]) == 'RUTA'):
                        self.le_refermapa.setText(str(feat.attributes()[idx_categoria]))

                else:

                    if (text_jurisdiccion == str(feat.attributes()[idx_jurisdiccion]) and
                            text_jerarquia == str(feat.attributes()[idx_jerarquia]) and
                            text_mat_calz == str(feat.attributes()[idx_material]) and str(feat.attributes()[idx_tipo]) == text_tipo):
                        # consulto si autovia esta activo

                        print("atributossss")
                        print(text_jurisdiccion)
                        print(text_jerarquia)
                        print(text_mat_calz)
                        self.le_refermapa.setText(str(feat.attributes()[idx_categoria]))

    def _signalLeTramo(self):

        attr_names = TableAtributosNames()

        if self.feature_target:
            tramo_attr = self.feature_target[attr_names.TRAMO]

            if tramo_attr == self.le_tramo.text():
                self.feature_data[attr_names.TRAMO] = tramo_attr
                self.le_tramo.setStyleSheet("")

            else:
                self.feature_data[attr_names.TRAMO] = self.le_tramo.text()
                self.le_tramo.setStyleSheet(
                    """QLineEdit { background-color: #e89db0; }""")

    def _signalDtCreated(self):

        attr_names = TableAtributosNames()

        if self.feature_target:
            created = self.feature_target[attr_names.CREATED]

            if created != self.dt_created.dateTime():
                self.feature_data[attr_names.CREATED] = self.dt_created.dateTime()
                self.dt_created.setStyleSheet(
                    """QDateTimeEdit { background-color: #e89db0; }""")
            else:
                self.feature_data[attr_names.CREATED] = created
                self.dt_created.setStyleSheet("")

    def _signalLeZona(self):
        attr_names = TableAtributosNames()

        if self.feature_target:
            zona_attr = self.feature_target[attr_names.ZONA]

            if zona_attr == self.le_zona.text():
                self.feature_data[attr_names.ZONA] = zona_attr
                self.le_zona.setStyleSheet("")

            else:
                self.feature_data[attr_names.ZONA] = self.le_zona.text()
                self.le_zona.setStyleSheet(
                    """QLineEdit { background-color: #e89db0; }""")

    def _signalLeCC(self):
        attr_names = TableAtributosNames()

        if self.feature_target:
            cc_attr = self.feature_target[attr_names.CC]

            if cc_attr == self.le_cc.text():
                self.feature_data[attr_names.CC] = cc_attr
                self.le_cc.setStyleSheet("")

            else:
                self.feature_data[attr_names.CC] = self.le_cc.text()
                self.le_cc.setStyleSheet(
                    """QLineEdit { background-color: #e89db0; }""")

    def _signalLe_nombre(self):

        attr_names = TableAtributosNames()

        if self.feature_target:
            nombre_attr = self.feature_target[attr_names.NOMBRE]

            if nombre_attr == self.le_nombre.text():
                self.feature_data[attr_names.NOMBRE] = nombre_attr
                self.le_nombre.setStyleSheet("")

            else:
                self.feature_data[attr_names.NOMBRE] = self.le_nombre.text()
                self.le_nombre.setStyleSheet(
                    """QLineEdit { background-color: #e89db0; }""")

    def _signalLe_manten(self):

        attr_names = TableAtributosNames()

        if self.feature_target:
            nombre_attr = self.feature_target[attr_names.MANTEMIM]

            if nombre_attr == self.le_manten.text():
                self.feature_data[attr_names.MANTEMIM] = nombre_attr
                self.le_manten.setStyleSheet("")

            else:
                self.feature_data[attr_names.MANTEMIM] = self.le_manten.text()
                self.le_manten.setStyleSheet(
                    """QLineEdit { background-color: #e89db0; }""")

    def _signalCb_jurisd(self):

        attr_names = TableAtributosNames()

        if self.feature_target:
            nombre_attr = self.feature_target[attr_names.JURISDIC]

            if nombre_attr == self.cb_jurisd.currentText():
                self.feature_data[attr_names.JURISDIC] = nombre_attr
                self.cb_jurisd.setStyleSheet("")

            else:
                self.feature_data[attr_names.JURISDIC] = self.cb_jurisd.currentText()
                self.cb_jurisd.setStyleSheet(
                    """QComboBox { background-color: #e89db0; }""")

                # Cargo la Jurisdiccion
        self._loadJerarquia(str(self.cb_jurisd.currentText()))
        self.cb_jerarq.setCurrentText(str('NULL'))



    def _signalCb_jerarq(self):

        attr_names = TableAtributosNames()

        if self.feature_target:
            nombre_attr = self.feature_target[attr_names.JERARQ]

            if nombre_attr == self.cb_jerarq.currentText():
                self.feature_data[attr_names.JERARQ] = nombre_attr
                self.cb_jerarq.setStyleSheet("")

            else:
                self.feature_data[attr_names.JERARQ] = self.cb_jerarq.currentText()
                self.cb_jerarq.setStyleSheet(
                    """QComboBox { background-color: #e89db0; }""")
                # Cargo la Jurisdiccion
        self._loadMaterialCalzada(str(self.cb_jerarq.currentText()))
        self.cb_mat_calz.setCurrentText(str('NULL'))

    def _signalCb_mat_calz(self):

        attr_names = TableAtributosNames()

        if self.feature_target:
            nombre_attr = self.feature_target[attr_names.MAT_CALZAD]


            if nombre_attr == self.cb_mat_calz.currentText():
                self.feature_data[attr_names.MAT_CALZAD] = nombre_attr
                self.cb_mat_calz.setStyleSheet("")
                self.cb_mat_calz.setCurrentText(str(self.feature_data[attr_names.MAT_CALZAD]))

            else:
                self.feature_data[attr_names.MAT_CALZAD] = self.cb_mat_calz.currentText()
                self.cb_mat_calz.setStyleSheet(
                    """QComboBox { background-color: #e89db0; }""")
                #self.cb_mat_calz.setCurrentText(str(self.feature_data[attr_names.MAT_CALZAD]))
                # Cargo la Jurisdiccion


        self.setReferMapa()

    def _signalLe_refermapa(self):

        attr_names = TableAtributosNames()

        if self.feature_target:
            nombre_attr = self.feature_target[attr_names.REFERMAPA]

            if nombre_attr == self.le_refermapa.text():
                self.feature_data[attr_names.REFERMAPA] = nombre_attr
                self.le_refermapa.setStyleSheet("")

            else:
                self.feature_data[attr_names.REFERMAPA] = self.le_refermapa.text()
                self.le_refermapa.setStyleSheet(
                    """QLineEdit { background-color: #e89db0; }""")

    def _signalLe_idsuma(self):

        attr_names = TableAtributosNames()

        if self.feature_target:
            nombre_attr = self.feature_target[attr_names.IDSUMA]

            if nombre_attr == self.le_idsuma.text():
                self.feature_data[attr_names.IDSUMA] = nombre_attr
                self.le_idsuma.setStyleSheet("")

            else:
                self.feature_data[attr_names.IDSUMA] = self.le_idsuma.text()
                self.le_idsuma.setStyleSheet(
                    """QLineEdit { background-color: #e89db0; }""")

    def _signalCb_tipo(self):

        #tengo que modificar jurisdiccion, jerarquia y material de calzada
        attr_names = TableAtributosNames()

        if self.feature_target:
            if self.cb_tipo.currentText() != 'AUTOVIA':
                self.checkb_autovia.setChecked(False)
            nombre_attr = self.feature_target[attr_names.TIPO]

            if nombre_attr == self.cb_tipo.currentText():
                self.feature_data[attr_names.TIPO] = nombre_attr
                self.cb_tipo.setStyleSheet("")


            else:
                self.feature_data[attr_names.TIPO] = self.cb_tipo.currentText()
                self.cb_tipo.setStyleSheet(
                    """QComboBox { background-color: #e89db0; }""")


        # Cargo la Jurisdiccion
        self._loadJurisdiccion(str(self.cb_tipo.currentText()))
        self.cb_jurisd.setCurrentText(str('NULL'))
        #self.setReferMapa()


    def setComboBoxByTipo(self, tipo):

        fields = self.refermapa_category.fields()
        idx_categoria = fields.indexFromName(FieldsReferMapCategory.CATEGORIA.value)
        idx_tipo = fields.indexFromName(FieldsReferMapCategory.TIPO.value)
        idx_material = fields.indexFromName(FieldsReferMapCategory.MATERIAL.value)
        idx_jurisdiccion = fields.indexFromName(FieldsReferMapCategory.JURISDICCION.value)
        idx_jerarquia = fields.indexFromName(FieldsReferMapCategory.JERARQUIA.value)

        for feat in self.refermapa_category.getFeatures():
            if str(feat.attributes()[idx_tipo]) == tipo:
                self.le_refermapa.setText('')





    def _signalTe_observacion(self):

        attr_names = TableAtributosNames()

        if self.feature_target:
            nombre_attr = self.feature_target[attr_names.OBSERVACION]

            if nombre_attr == self.te_observacion.toPlainText():
                self.feature_data[attr_names.OBSERVACION] = nombre_attr
                self.te_observacion.setStyleSheet("")

            else:
                self.feature_data[attr_names.OBSERVACION] = self.te_observacion.toPlainText()
                self.te_observacion.setStyleSheet(
                    """QTextEdit { background-color: #e89db0; }""")

    def _signalLe_jer_abr(self):

        attr_names = TableAtributosNames()

        if self.feature_target:
            nombre_attr = self.feature_target[attr_names.JER_ABR]

            if nombre_attr == self.le_jer_abr.text():
                self.feature_data[attr_names.JER_ABR] = nombre_attr
                self.le_jer_abr.setStyleSheet("")

            else:
                self.feature_data[attr_names.JER_ABR] = self.le_jer_abr.text()
                self.le_jer_abr.setStyleSheet(
                    """QLineEdit { background-color: #e89db0; }""")

    def _signalLe_ruleid(self):

        attr_names = TableAtributosNames()

        if self.feature_target:
            nombre_attr = self.feature_target[attr_names.RULEID]

            if nombre_attr == self.le_ruleid.text():
                self.feature_data[attr_names.RULEID] = nombre_attr
                self.le_ruleid.setStyleSheet("")

            else:
                self.feature_data[attr_names.RULEID] = self.le_ruleid.text()
                self.le_ruleid.setStyleSheet(
                    """QLineEdit { background-color: #e89db0; }""")

    def _signalDt_modified(self):

        attr_names = TableAtributosNames()

        if self.feature_target:
            created = self.feature_target[attr_names.MODIFIED]

            if created != self.dt_modified.dateTime():
                self.feature_data[attr_names.MODIFIED] = self.dt_modified.dateTime()
                self.dt_modified.setStyleSheet(
                    """QDateTimeEdit { background-color: #e89db0; }""")
            else:
                self.feature_data[attr_names.MODIFIED] = created
                self.dt_modified.setStyleSheet("")

    def _signalDt_fecha_obra(self):

        attr_names = TableAtributosNames()

        if self.feature_target:
            created = self.feature_target[attr_names.FECHAOBRA]

            if created != self.dt_fecha_obra.dateTime():
                self.feature_data[attr_names.FECHAOBRA] = self.dt_fecha_obra.dateTime()
                self.dt_fecha_obra.setStyleSheet(
                    """QDateTimeEdit { background-color: #e89db0; }""")
            else:
                self.feature_data[attr_names.FECHAOBRA] = created
                self.dt_fecha_obra.setStyleSheet("")

    def _signalCheckb_autovia(self):

        attr_names = TableAtributosNames()

        if self.feature_target:
            created = self.feature_target[attr_names.AUTOVIA]

            if self.checkb_autovia.isChecked():
                self.feature_data[attr_names.AUTOVIA] = True
                self.checkb_autovia.setStyleSheet(
                    """QCheckBox { background-color: #e89db0; }""")
            else:
                self.cb_tipo.setCurrentText(str('RUTA'))

                self.feature_data[attr_names.AUTOVIA] = False
                self.checkb_autovia.setStyleSheet("")
        self.setReferMapa()

    def loadAllData(self):

        if self._loadJurisdiccion() and self._loadJerarquia() and self._loadMaterialCalzada() and self._loadTipo():
            return True

        return False

    def setFeatureData(self, feature):
        # recibe el feature de la RED VIAL y con el id me encargo de traer lo de la tabla atributos
        attr_names_table = TableAtributosNames()

        try:

            layer_table_atributes = QgsProject.instance().mapLayersByName('atributos')[0]

            fields = layer_table_atributes.fields()
            self.feature_data.setFields(fields)

            if feature:
                id_current = feature.id()
                self.feature_target = None

                idx_redvial = layer_table_atributes.fields().indexFromName(attr_names_table.REDVIAL_IDREDVIAL)

                for feat in layer_table_atributes.getFeatures():

                    # feat id lo trago desde el campo redvial_idredvial

                    id_feat = feat.attributes()[idx_redvial]
                    idx_actual = feat.fields().indexFromName(attr_names_table.ACTUAL)

                    if id_feat == id_current and feat.attributes()[idx_actual] == True:
                        # ecnotro el objeto, o trabajo en el formulario
                        self.feature_target = feat
                        self.feature_data.setAttributes(feat.attributes())
                        break

                return True

            return False

        except(IndexError):
            self.iface.messageBar().pushMessage("Error",
                                                "Debe cargar la capa 'atributos'",
                                                Qgis.Critical, 5)
            return False

    def setDataToForms(self):

        attr_names_table = TableAtributosNames()

        if self.feature_target:
            # seteo los valores de los campos
            self.le_tramo.setText(self.feature_target[attr_names_table.TRAMO])
            time_format = "dd-MM-yyyy  HH:mm:ss"

            if self.feature_target[attr_names_table.CREATED] != NULL:

                created = QDateTime.fromString(self.feature_target[attr_names_table.CREATED].toString(time_format),
                                               time_format)

                if created.isValid():
                    self.dt_created.setDateTime(created)
            else:

                created = QDateTime.fromString("00-00-0000 00:00:00",
                                               time_format)

                self.dt_created.setDateTime(created)

            # Cargo la Zona
            self.le_zona.setText(str(self.feature_target[attr_names_table.ZONA]))

            # Cargo la CC
            self.le_cc.setText(str(self.feature_target[attr_names_table.CC]))

            # Cargo la NOMBRE
            self.le_nombre.setText(str(self.feature_target[attr_names_table.NOMBRE]))

            # Cargo la MANTENIMIENTO
            self.le_manten.setText(str(self.feature_target[attr_names_table.MANTEMIM]))

            # Cargo la TIPO

            self._loadTipo()
            self.cb_tipo.setCurrentText(str(self.feature_target[attr_names_table.TIPO]))


            # Cargo la Jurisdiccion
            self._loadJurisdiccion(str(self.feature_target[attr_names_table.TIPO]))
            self.cb_jurisd.setCurrentText(str(self.feature_target[attr_names_table.JURISDIC]))

            # Cargo la JERARQUIA
            self._loadJerarquia(str(self.feature_target[attr_names_table.JURISDIC]))
            self.cb_jerarq.setCurrentText(str(self.feature_target[attr_names_table.JERARQ]))

            # Cargo la MATERIAL
            self._loadMaterialCalzada(str(self.feature_target[attr_names_table.JERARQ]))
            self.cb_mat_calz.setCurrentText(str(self.feature_target[attr_names_table.MAT_CALZAD]))

            # Cargo la REFERMAPA
            self.le_refermapa.setText(str(self.feature_target[attr_names_table.REFERMAPA]))

            # Cargo la REFERMAPA
            self.le_refermapa.setText(str(self.feature_target[attr_names_table.REFERMAPA]))

            # Cargo la ID SUMA
            self.le_idsuma.setText(str(self.feature_target[attr_names_table.IDSUMA]))



            # Cargo la OBSERVACION
            self.te_observacion.setText(str(self.feature_target[attr_names_table.OBSERVACION]))

            # Cargo la JER ABR
            self.le_jer_abr.setText(str(self.feature_target[attr_names_table.JER_ABR]))

            # Cargo RULE ID
            self.le_ruleid.setText(str(self.feature_target[attr_names_table.RULEID]))

            # Cargo MODIFICADO

            if self.feature_target[attr_names_table.MODIFIED] != NULL:

                modif = QDateTime.fromString(self.feature_target[attr_names_table.MODIFIED].toString(time_format),
                                             time_format)

                if modif.isValid():
                    self.dt_modified.setDateTime(modif)

            else:

                modif = QDateTime.fromString("00-00-0000 00:00:00",
                                             time_format)

                self.dt_modified.setDateTime(modif)

            # Cargo Fecha de OBRA

            if self.feature_target[attr_names_table.FECHAOBRA] != NULL:

                fecha_obra = QDateTime.fromString(self.feature_target[attr_names_table.FECHAOBRA].toString(time_format),
                                                  time_format)

                if fecha_obra.isValid():
                    self.dt_fecha_obra.setDateTime(fecha_obra)

            else:

                fecha_obra = QDateTime.fromString("00-00-0000 00:00:00",
                                                  time_format)

                self.dt_fecha_obra.setDateTime(fecha_obra)

            # Cargo RULE ID
            self.le_redvial_idredvial.setText(str(self.feature_target[attr_names_table.REDVIAL_IDREDVIAL]))

            # Cargo Actual
            if self.feature_target[attr_names_table.ACTUAL] != NULL:
                self.checkb_actual.setChecked(self.feature_target[attr_names_table.ACTUAL])

            if self.feature_target[attr_names_table.AUTOVIA] != NULL:
                self.checkb_autovia.setChecked(self.feature_target[attr_names_table.AUTOVIA])

            return True

        return False

    def _loadJerarquia(self, jurisdiccion):
        # recupero la tabla refermapa_category
        try:
            refermapa_category_table = QgsProject.instance().mapLayersByName('refermapa_category')[0]
            self.cb_jerarq.clear()

            jurisd_array = []

            i = 0
            for feat in refermapa_category_table.getFeatures():

                if jurisdiccion == str(feat[FieldsReferMapCategory.JURISDICCION.value]):
                    jurisd_array.append(feat[FieldsReferMapCategory.JERARQUIA.value])

            array_unicos = []
            for obj in set(jurisd_array):
                if obj == NULL:
                    pass

                else:
                    array_unicos.append(obj)

            array_unicos.sort()
            array_unicos.append('NULL')
            # agrego los elementos al combobox
            self.cb_jerarq.addItems(array_unicos)

            return True



        except(IndexError):
            self.iface.messageBar().pushMessage("Error",
                                                "Debe cargar la capa 'refermapa_category'",
                                                Qgis.Critical, 5)
            return False

    def _loadJurisdiccion(self, tipo):

        # recupero la tabla refermapa_category
        try:
            refermapa_category_table = QgsProject.instance().mapLayersByName('refermapa_category')[0]

            self.cb_jurisd.clear()

            jurisd_array = []

            i = 0
            for feat in refermapa_category_table.getFeatures():
                if tipo == str(feat[FieldsReferMapCategory.TIPO.value]):
                    jurisd_array.append(feat[FieldsReferMapCategory.JURISDICCION.value])


            array_unicos = []
            for obj in set(jurisd_array):
                if obj == NULL:
                    pass

                else:
                    array_unicos.append(obj)

            # agrego los elementos al combobox

            array_unicos.sort()
            array_unicos.append('NULL')
            self.cb_jurisd.addItems(array_unicos)

            return True



        except(IndexError):
            self.iface.messageBar().pushMessage("Error",
                                                "Debe cargar la capa 'refermapa_category'",
                                                Qgis.Critical, 5)
            return False

    def _loadMaterialCalzada(self, jerarquia):

        # recupero la tabla refermapa_category
        try:
            refermapa_category_table = QgsProject.instance().mapLayersByName('refermapa_category')[0]
            self.cb_mat_calz.clear()
            jurisd_array = []

            i = 0
            for feat in refermapa_category_table.getFeatures():
                if jerarquia == str(feat[FieldsReferMapCategory.JERARQUIA.value]):
                    jurisd_array.append(feat[FieldsReferMapCategory.MATERIAL.value])

            array_unicos = []
            for obj in set(jurisd_array):
                if obj == NULL:
                    pass

                else:
                    array_unicos.append(obj)

            # agrego los elementos al combobox

            array_unicos.sort()
            array_unicos.append('NULL')
            self.cb_mat_calz.addItems(array_unicos)

            return True



        except(IndexError):
            self.iface.messageBar().pushMessage("Error",
                                                "Debe cargar la capa 'refermapa_category'",
                                                Qgis.Critical, 5)
            return False

    def _loadTipo(self):
        # recupero la tabla refermapa_category
        try:
            refermapa_category_table = QgsProject.instance().mapLayersByName('refermapa_category')[0]

            jurisd_array = []

            i = 0
            for feat in refermapa_category_table.getFeatures():
                jurisd_array.append(feat[FieldsReferMapCategory.TIPO.value])

            array_unicos = []
            for obj in set(jurisd_array):
                if obj == NULL:
                    pass

                else:
                    array_unicos.append(obj)

            # agrego los elementos al combobox

            array_unicos.sort()
            array_unicos.append('NULL')
            self.cb_tipo.addItems(array_unicos)

            # print(self.cb_tipo.currentText())

            # self.cb_tipo.setCurrentText('PROVINCIAL')

            return True



        except(IndexError):
            self.iface.messageBar().pushMessage("Error",
                                                "Debe cargar la capa 'refermapa_category'",
                                                Qgis.Critical, 5)
            return False
