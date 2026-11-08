"""Exportador de resultados a Excel"""

import os
import pandas as pd


def exportar_a_excel(resultado, ruta_salida):
    """Convierte el resultado de la comparacion en un archivo Excel (.xlsx)"""
    filas = []

    for item in resultado.items:
        fila = {
            "Producto Base": item.producto_base,
        }

        for oferta in item.ofertas:
            nombre = oferta.proveedor
            fila[f"{nombre} - Cotizado"] = oferta.descripcion_cotizada
            fila[f"{nombre} - Cant."] = oferta.cantidad
            fila[f"{nombre} - P. Unitario"] = oferta.precio_unitario
            fila[f"{nombre} - Total"] = oferta.precio_total

        fila["Diferencias Técnicas"] = item.diferencias_tecnicas
        fila["Mejor Opción"] = item.mejor_opcion

        filas.append(fila)

    df = pd.DataFrame(filas)

    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)

    df.to_excel(ruta_salida, index=False)
    print(f"Cuadro comparativo guardado con exito en: {ruta_salida}")
