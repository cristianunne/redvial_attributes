
from enum import Enum

class TableAtributosNames:


    def __init__(self):

        self.ID = 'id'
        self.TRAMO = 'tramo'
        self.REFERMAPA = 'refermapa'
        self.CREATED = 'created'
        self.ZONA = 'zona'
        self.CC = 'cc'
        self.NOMBRE = 'nombre'
        self.MANTEMIM = 'mantenim'
        self.JURISDIC = 'jurisdic'
        self.JERARQ = 'jerarq'
        self.MAT_CALZAD = 'mat_calzad'
        self.IDSUMA = 'idsuma'
        self.TIPO = 'tipo'
        self.OBSERVACION = 'observacion'
        self.JER_ABR = 'jer_abr'
        self.RULEID = 'ruleid'
        self.OVERRIDE = 'override'
        self.MODIFIED = 'modified'
        self.FECHAOBRA = 'fecha_obra'
        self.REDVIAL_IDREDVIAL = 'redvial_idredvial'
        self.ACTUAL = 'actual'
        self.AUTOVIA = 'autovia'



class TableAttrChanges:

    def __init__(self):
        self.FID = 'fid'
        self.ATRIBUTO = 'atributo'
        self.OLD_VALUE = 'old_value'
        self.NEW_VALUE = 'new_value'
        self.ATRIBUTOS_IDATRIBUTOS = 'atributos_idatributos'
        self.CREATED = 'created'


class TableRedVialHistory:

    def __init__(self):
        self.FID = 'FID'
        self.FECHA = 'fecha'
        self.ID_ORIGEN = 'id_origen'

class FieldsRedVialMap:
    def __init__(self):
        self.FID = 'fid'
        self.TRAMO = 'tramo'
        self.ZONA = 'Zona'
        self.CC = 'CC'
        self.NOMBRE = 'Nombre'
        self.MANTEMIM = 'Mantenim'
        self.JURISDIC = 'Jurisdic'
        self.JERARQ = 'Jerarq'
        self.MAT_CALZAD = 'Mat_Calzad'
        self.IDSUMA = 'IDsuma'
        self.TIPO = 'tipo'
        self.OBSERVACION = 'OBSERVACIO'
        self.REFERMAPA = 'refermapa'
        self.JER_ABR = 'JER_ABR'
        self.RULEID = 'RuleID'
        self.OVERRIDE = 'Override'
        self.CREATED = 'created'
        self.MODIFIED = 'modified'
        self.FECHAOBRA = 'fecha_obra'



class FieldsReferMapCategory(Enum):

    FID = 'fid'
    TIPO = 'tipo'
    JURISDICCION = 'jurisdiccion'
    JERARQUIA = 'jerarquia'
    MATERIAL = 'material'
    CATEGORIA = 'categoria'


