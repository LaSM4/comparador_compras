"""Módulo extractor de texto para presupuestos (PDF, Imágenes, TXT)."""

import os
import shutil
import pdfplumber  # pyrefly: ignore[missing-import]
from PIL import Image  # pyrefly: ignore[missing-import]
import pytesseract  # pyrefly: ignore[missing-import]


def _configurar_tesseract():
    """Detecta y configura la ruta de Tesseract si no está en PATH."""
    cmd = pytesseract.pytesseract.tesseract_cmd
    if not shutil.which(cmd):
        posibles_rutas = [
            "/opt/homebrew/bin/tesseract",       # macOS Apple Silicon
            "/usr/local/bin/tesseract",          # macOS Intel / Linux
            "/usr/bin/tesseract",                # Linux estándar
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",  # Windows
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]
        for ruta in posibles_rutas:
            if os.path.exists(ruta):
                pytesseract.pytesseract.tesseract_cmd = ruta
                break


def _obtener_idioma_ocr():
    """Determina si el paquete de español está disponible para Tesseract."""
    _configurar_tesseract()
    try:
        langs = pytesseract.get_languages()
        if "spa" in langs:
            return "spa+eng"
        return "eng"
    except Exception:
        return "eng"


def extraer_texto_txt(ruta_archivo: str) -> str:
    """Lee un archivo .txt con soporte para múltiples codificaciones."""
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            return f.read().strip()
    except UnicodeDecodeError:
        with open(
            ruta_archivo, "r", encoding="latin-1", errors="replace"
        ) as f:
            return f.read().strip()


def extraer_texto_imagen(ruta_archivo: str) -> str:
    """Extrae texto de una imagen (.png, .jpg, .jpeg) usando OCR."""
    _configurar_tesseract()
    idioma = _obtener_idioma_ocr()
    try:
        with Image.open(ruta_archivo) as imagen:
            texto = pytesseract.image_to_string(imagen, lang=idioma)
            return texto.strip()
    except Exception as e:
        print(
            f"  [Aviso OCR] No se procesó la imagen {ruta_archivo}: {e}"
        )
        return ""


def extraer_texto_pdf(ruta_archivo: str) -> str:
    """Lee un archivo .pdf con fallback a OCR para páginas escaneadas."""
    texto_total = []
    _configurar_tesseract()
    idioma = _obtener_idioma_ocr()

    try:
        with pdfplumber.open(ruta_archivo) as pdf:
            for num_pag, pagina in enumerate(pdf.pages, start=1):
                texto_pagina = pagina.extract_text()
                # Si la página contiene texto vectorial suficiente, usarlo
                if texto_pagina and len(texto_pagina.strip()) > 30:
                    texto_total.append(texto_pagina.strip())
                else:
                    # PDF escaneado: aplicar OCR a la página renderizada
                    try:
                        img = pagina.to_image(resolution=200).original
                        texto_ocr = pytesseract.image_to_string(
                            img, lang=idioma
                        )
                        if texto_ocr.strip():
                            texto_total.append(texto_ocr.strip())
                    except Exception as e_ocr:
                        print(
                            f"  [Aviso PDF OCR] Pág {num_pag} "
                            f"en {ruta_archivo}: {e_ocr}"
                        )
                        if texto_pagina:
                            texto_total.append(texto_pagina.strip())

        return "\n\n".join(texto_total).strip()
    except Exception as e:
        print(f"  [Error PDF] No se pudo leer {ruta_archivo}: {e}")
        return ""


def extraer_texto_archivo(ruta_archivo: str) -> str:
    """Detecta la extensión y utiliza el extractor correspondiente."""
    _, extension = os.path.splitext(ruta_archivo)
    extension = extension.lower()

    if extension == ".txt":
        return extraer_texto_txt(ruta_archivo)
    elif extension == ".pdf":
        return extraer_texto_pdf(ruta_archivo)
    elif extension in [".png", ".jpg", ".jpeg"]:
        return extraer_texto_imagen(ruta_archivo)
    else:
        raise ValueError(f"Formato no soportado: {extension}")


def cargar_presupuestos(carpeta_input: str) -> dict[str, str]:
    """Lee todos los presupuestos de una carpeta y retorna un dict."""
    if not os.path.exists(carpeta_input):
        os.makedirs(carpeta_input, exist_ok=True)
        print(
            f"Carpeta '{carpeta_input}' creada. Agrega presupuestos allí."
        )
        return {}

    presupuestos = {}
    formatos_soportados = {".pdf", ".png", ".jpg", ".jpeg", ".txt"}

    archivos = sorted(os.listdir(carpeta_input))
    for archivo in archivos:
        if archivo.startswith("."):
            continue

        ruta_completa = os.path.join(carpeta_input, archivo)
        if not os.path.isfile(ruta_completa):
            continue

        _, extension = os.path.splitext(archivo)
        if extension.lower() not in formatos_soportados:
            print(
                f"  [Omitido] '{archivo}': Formato ({extension}) no soportado."
            )
            continue

        nombre_base, _ = os.path.splitext(archivo)
        print(f"Leyendo presupuesto de: {archivo}...")
        texto = extraer_texto_archivo(ruta_completa)

        if not texto:
            print(
                f"  [Advertencia] No se extrajo texto de '{archivo}' (vacío)."
            )
            continue

        # Se guarda con el identificador del archivo para referencia
        presupuestos[nombre_base] = texto

    return presupuestos
