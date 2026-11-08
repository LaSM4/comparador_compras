"""Módulo exportador de resultados a formato Excel (.xlsx) con diseño profesional."""

import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


def exportar_a_excel(resultado, ruta_salida: str):
    """Genera un archivo Excel (.xlsx) estilizado con la comparativa y el resumen ejecutivo."""
    wb = openpyxl.Workbook()

    # Estilos compartidos
    color_primario = "1F4E78"    # Azul corporativo
    color_total = "D9E1F2"       # Azul claro para totales
    color_resumen_hdr = "2F5597" # Azul secundario

    fuente_encabezado = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    fuente_negrita = Font(name="Calibri", size=11, bold=True)
    fuente_normal = Font(name="Calibri", size=10)
    fuente_titulo = Font(name="Calibri", size=14, bold=True, color="1F4E78")

    fill_encabezado = PatternFill(start_color=color_primario, end_color=color_primario, fill_type="solid")
    fill_total = PatternFill(start_color=color_total, end_color=color_total, fill_type="solid")
    fill_resumen_hdr = PatternFill(start_color=color_resumen_hdr, end_color=color_resumen_hdr, fill_type="solid")

    borde_fino = Border(
        left=Side(style="thin", color="D3D3D3"),
        right=Side(style="thin", color="D3D3D3"),
        top=Side(style="thin", color="D3D3D3"),
        bottom=Side(style="thin", color="D3D3D3"),
    )
    borde_total = Border(
        top=Side(style="thin", color="000000"),
        bottom=Side(style="double", color="000000"),
    )

    # ----------------------------------------------------
    # HOJA 1: Comparativa de Productos
    # ----------------------------------------------------
    ws_comp = wb.active
    ws_comp.title = "Comparativa de Productos"

    # Determinar lista ordenada de proveedores únicos
    proveedores_unicos = []
    if hasattr(resultado, "resumen") and resultado.resumen.proveedores_detectados:
        proveedores_unicos = list(resultado.resumen.proveedores_detectados)
    else:
        for item in resultado.items:
            for of in item.ofertas:
                if of.proveedor not in proveedores_unicos:
                    proveedores_unicos.append(of.proveedor)

    # Construir encabezados
    encabezados = ["Producto Base"]
    for prov in proveedores_unicos:
        encabezados.extend([
            f"{prov}\nCotizado",
            f"{prov}\nCant.",
            f"{prov}\nUnidad",
            f"{prov}\nP. Unit.",
            f"{prov}\nTotal",
        ])
    encabezados.extend([
        "Diferencias Técnicas",
        "Mejor Opción",
        "Justificación de Selección"
    ])

    ws_comp.append(encabezados)

    # Aplicar estilos a encabezados
    for col_idx in range(1, len(encabezados) + 1):
        celda = ws_comp.cell(row=1, column=col_idx)
        celda.font = fuente_encabezado
        celda.fill = fill_encabezado
        celda.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    # Cargar filas de datos
    filas_totales_cols = {}  # para acumular totales de cada proveedor
    for prov in proveedores_unicos:
        filas_totales_cols[prov] = 0.0

    for item in resultado.items:
        fila = [item.producto_base]

        # Mapa de ofertas por proveedor para este ítem
        ofertas_map = {of.proveedor: of for of in item.ofertas}

        for prov in proveedores_unicos:
            of = ofertas_map.get(prov)
            if of and of.descripcion_cotizada.lower() != "no cotizado":
                fila.extend([
                    of.descripcion_cotizada,
                    of.cantidad,
                    getattr(of, "unidad_medida", "un"),
                    of.precio_unitario,
                    of.precio_total,
                ])
                filas_totales_cols[prov] += of.precio_total
            else:
                fila.extend(["No cotizado", 0, "-", 0, 0])

        fila.append(item.diferencias_tecnicas)
        fila.append(item.mejor_opcion)
        fila.append(getattr(item, "justificacion_mejor_opcion", ""))

        ws_comp.append(fila)

    # Fila de Totales
    fila_total = ["TOTAL GENERAL"]
    for prov in proveedores_unicos:
        fila_total.extend(["-", "-", "-", "-", filas_totales_cols[prov]])
    fila_total.extend(["-", "-", "-"])
    ws_comp.append(fila_total)

    # Formateo de celdas de la hoja de comparativa
    max_row = ws_comp.max_row
    max_col = ws_comp.max_column

    formato_miles = "#,##0"

    for row in range(2, max_row + 1):
        es_ultima_fila = (row == max_row)
        for col in range(1, max_col + 1):
            celda = ws_comp.cell(row=row, column=col)
            celda.font = fuente_negrita if es_ultima_fila else fuente_normal
            celda.border = borde_total if es_ultima_fila else borde_fino
            if es_ultima_fila:
                celda.fill = fill_total

            # Formatear números
            if isinstance(celda.value, (int, float)):
                # Cantidades vs Precios
                encabezado_col = ws_comp.cell(row=1, column=col).value or ""
                if "Cant." in encabezado_col:
                    celda.alignment = Alignment(horizontal="center", vertical="center")
                    celda.number_format = "#,##0.##"
                else:
                    celda.alignment = Alignment(horizontal="right", vertical="center")
                    celda.number_format = formato_miles
            elif isinstance(celda.value, str):
                if celda.value in ["-", "No cotizado"]:
                    celda.alignment = Alignment(horizontal="center", vertical="center")
                elif "Diferencias" in (ws_comp.cell(row=1, column=col).value or ""):
                    celda.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
                else:
                    celda.alignment = Alignment(horizontal="left", vertical="center")

    # ----------------------------------------------------
    # HOJA 2: Resumen Ejecutivo
    # ----------------------------------------------------
    ws_resumen = wb.create_sheet(title="Resumen Ejecutivo")

    ws_resumen["B2"] = "CUADRO COMPARATIVO - RESUMEN EJECUTIVO"
    ws_resumen["B2"].font = fuente_titulo

    resumen = getattr(resultado, "resumen", None)

    filas_resumen = [
        ("Moneda Principal:", getattr(resumen, "moneda_principal", "GS")),
        ("Proveedores Evaluados:", ", ".join(proveedores_unicos)),
        ("Observaciones Generales:", getattr(resumen, "observaciones_generales", "Sin observaciones adicionales.")),
        ("Recomendación de Compra:", getattr(resumen, "conclusion_recomendada", "Ver detalle en hoja Comparativa.")),
    ]

    r_idx = 4
    for etiqueta, valor in filas_resumen:
        c_lbl = ws_resumen.cell(row=r_idx, column=2, value=etiqueta)
        c_lbl.font = fuente_negrita
        c_val = ws_resumen.cell(row=r_idx, column=3, value=valor)
        c_val.font = fuente_normal
        c_val.alignment = Alignment(wrap_text=True)
        r_idx += 2

    # Tabla de Totales por Proveedor en la hoja de resumen
    r_idx += 1
    hdr_prov = ws_resumen.cell(row=r_idx, column=2, value="Proveedor")
    hdr_prov.font = fuente_encabezado
    hdr_prov.fill = fill_resumen_hdr

    hdr_tot = ws_resumen.cell(row=r_idx, column=3, value=f"Total Presupuestado ({getattr(resumen, 'moneda_principal', 'GS')})")
    hdr_tot.font = fuente_encabezado
    hdr_tot.fill = fill_resumen_hdr

    for prov in proveedores_unicos:
        r_idx += 1
        c_p = ws_resumen.cell(row=r_idx, column=2, value=prov)
        c_p.font = fuente_normal
        c_p.border = borde_fino

        c_t = ws_resumen.cell(row=r_idx, column=3, value=filas_totales_cols[prov])
        c_t.font = fuente_negrita
        c_t.alignment = Alignment(horizontal="right")
        c_t.number_format = formato_miles
        c_t.border = borde_fino

    # Ajuste automático del ancho de columnas en ambas hojas
    for ws in [ws_comp, ws_resumen]:
        ws.row_dimensions[1].height = 28
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for celda in col:
                val_str = str(celda.value or "")
                lineas = val_str.split("\n")
                longitud_max_linea = max(len(l) for l in lineas) if lineas else 0
                if longitud_max_linea > max_len:
                    max_len = longitud_max_linea
            # Establecer un ancho razonable
            ws.column_dimensions[col_letter].width = max(min(max_len + 4, 45), 12)

    # Guardar archivo
    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    wb.save(ruta_salida)
    print(f"Cuadro comparativo guardado con éxito en: {ruta_salida}")
