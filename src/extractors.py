"""Comparador de compras"""

import os  # Manejar rutas de archivos
import pdfplumber  # Abrir archivos PDF y extraer su contenido
from PIL import Image  # Abrir imagenes y aplicar OCR para convertir foto en texto
import pytesseract  # Motor de reconocimiento optico de caracteres (OCR)


def extraer_texto_txt(ruta_archivo):
    """Lee un archivo .txt y devuelve su contenido"""
    with open(ruta_archivo, "r", encoding="utf-8") as f:
        return f.read().strip()


def extraer_texto_pdf(ruta_archivo):
    """Lee un archivo .pdf y devuelve el contenido"""
    texto = ""
    with pdfplumber.open(ruta_archivo) as pdf:
        for pagina in pdf.pages:
            texto_pagina = pagina.extract_text()
            if texto_pagina:
                texto += texto_pagina + "\n"
    return texto.strip()


def extraer_texto_imagen(ruta_archivo):
    """Extrae el texto de una imagen .png, .jpg usando OCR"""
    imagen = Image.open(ruta_archivo)
    texto = pytesseract.image_to_string(imagen)
    return texto.strip()


def extraer_texto_archivo(ruta_archivo):
    """Detecta la extension y usa el extractor correspondiente"""
    _, extension = os.path.slitext(
        ruta_archivo)  # _ la usamos cuando la funcion debe devolver cosas pero esta en si no la necesitamos de primera
    extension = extension.lower()

    if extension == ".txt":
        return extraer_texto_txt(ruta_archivo)
    elif extension == ".pdf":
        return extraer_texto_pdf(ruta_archivo)
    elif extension in [".png", ".jpg", ".jpeg"]:
        return extraer_texto_imagen(ruta_archivo)
    else:
        raise ValueError(f"Formato no soportado:{extension}")


def cargar_presupuestos(carpeta_input):
    """Leer todos los presupuestos de una carpeta y devolver un diccionario"""
    presupuestos = {}

    for archivo in os.listdir(carpeta_input):
        if archivo.startswith("."):  # Ignorar archivos ocultos de Mac
            continue

        ruta_completa = os.path.join(carpeta_input, archivo)
        nombre_proveedor, _ = os.path.splitext(archivo)

        print(f"Leyendo presupuesto de: {nombre_proveedor}...")
        texto = extraer_texto_archivo(ruta_completa)
        presupuestos[nombre_proveedor] = texto

    return presupuestos
