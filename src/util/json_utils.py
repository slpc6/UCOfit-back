"""Utilidades para conversión de datos"""

from datetime import datetime
from typing import Dict, List
from bson.objectid import ObjectId


def convertir_fechas_a_string(doc: Dict | List) -> Dict | List:
    """Convierte todas las fechas datetime a string en un documento

    Args:
        doc: diccionario o lista a convertir

    Returns:
        diccionario o lista con fechas convertidas a string

    """
    if isinstance(doc, dict):
        for key, value in doc.items():
            if isinstance(value, datetime):
                doc[key] = value.isoformat()
            elif isinstance(value, list):
                for item in value:
                    convertir_fechas_a_string(item)
            elif isinstance(value, dict):
                convertir_fechas_a_string(value)
    elif isinstance(doc, list):
        for item in doc:
            convertir_fechas_a_string(item)
    return doc


def convertir_objectid_a_string(doc: Dict | List) -> Dict | List:
    """Convierte todos los ObjectId a string en un documento

    Args:
        doc: diccionario o lista a convertir

    Returns:
        diccionario o lista con ObjectIds convertidos a string

    """

    if isinstance(doc, dict):
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                doc[key] = str(value)
            elif isinstance(value, list):
                for item in value:
                    convertir_objectid_a_string(item)
            elif isinstance(value, dict):
                convertir_objectid_a_string(value)
    elif isinstance(doc, list):
        for item in doc:
            convertir_objectid_a_string(item)
    return doc


def limpiar_datos_para_json(doc: Dict | List) -> Dict | List:
    """Limpia un documento para serialización JSON

    Convierte datetime a string y ObjectId a string

    Args:
        doc: diccionario o lista a limpiar

    Returns:
        diccionario o lista limpio para JSON

    """
    doc = convertir_fechas_a_string(doc)
    doc = convertir_objectid_a_string(doc)
    return doc
