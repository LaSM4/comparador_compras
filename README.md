# Comparador Inteligente de Compras y Presupuestos

Herramienta de análisis técnico y económico de presupuestos de compras y licitaciones impulsada por Inteligencia Artificial (**Google Gemini**).

Permite cargar múltiples cotizaciones en formatos PDF (vectoriales o escaneados), imágenes (fotos de WhatsApp, escaneos) o texto plano, extraer y normalizar los productos, detectar equivalencias técnicas y exportar un cuadro comparativo profesional en Excel.

---

## 🚀 Características

- **Soporte multiformato:** Procesa archivos `.pdf` (con OCR automático para páginas escaneadas), imágenes (`.png`, `.jpg`, `.jpeg`) y archivos de texto (`.txt`).
- **OCR inteligente con Tesseract:** Detección automática del binario en macOS, Linux y Windows, con soporte en español (`spa+eng`).
- **Normalización con IA (Gemini):**
  - Identifica la razón social / nombre comercial real de los proveedores desde los membretes y firmas (sin depender del nombre del archivo).
  - Agrupa productos similares bajo un nombre técnico estándar (*producto base*).
  - Detecta diferencias técnicas en marcas, potencias, medidas y normas de seguridad.
  - Elige la mejor opción costo/beneficio con justificación técnica.
- **Exportación en Excel con diseño profesional:**
  - Hoja 1: Matriz comparativa lado a lado con separadores de miles y suma total de cada proveedor.
  - Hoja 2: Resumen ejecutivo con observaciones generales, condiciones comerciales y recomendación de adjudicación.

---

## 📋 Requisitos Previos

### 1. Python
Se recomienda Python 3.10 o superior (compatible con Python 3.11, 3.12 y 3.14).

### 2. Tesseract OCR (Requisito del sistema)
Para extraer texto de imágenes y PDFs escaneados es necesario tener instalado Tesseract con el paquete de idioma español:

- **macOS (Homebrew):**
  ```bash
  brew install tesseract tesseract-lang
  ```
- **Ubuntu / Debian:**
  ```bash
  sudo apt-get update
  sudo apt-get install -y tesseract-ocr tesseract-ocr-spa
  ```
- **Windows:**
  Descargar e instalar el instalador desde [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki) marcando la opción de idioma "Spanish".

---

## ⚙️ Configuración

1. **Crear entorno virtual e instalar dependencias:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configurar la API Key de Gemini:**
   Crea un archivo `.env` en la raíz del proyecto (o edita el existente):
   ```env
   GEMINI_API_KEY=tu_clave_de_gemini_aqui
   GEMINI_MODEL=gemini-3.5-flash
   ```
   > Obtén tu API Key gratuita en [Google AI Studio](https://aistudio.google.com/).

---

## 💻 Uso

1. Coloca al menos 2 presupuestos a comparar en la carpeta:
   ```
   data/input/
   ```
2. Ejecuta el sistema:
   ```bash
   python main.py
   ```
3. Opciones avanzadas de línea de comandos:
   ```bash
   # Especificar carpetas personalizadas o modelo
   python main.py --input mis_presupuestos/ --output comparativa.xlsx --model gemini-3.5-flash
   ```
4. El cuadro comparativo resultante se guardará en:
   ```
   data/output/cuadro_comparativo.xlsx
   ```

---

## 📁 Estructura del Proyecto

```
comparador_compras/
├── data/
│   ├── input/                # Presupuestos a analizar (.pdf, .jpg, .png, .txt)
│   └── output/               # Cuadros comparativos generados (.xlsx)
├── src/
│   ├── __init__.py
│   ├── extractors.py         # Extracción de texto y OCR resiliente
│   ├── processor.py          # Prompt y estructuración Pydantic con Gemini
│   └── exporter.py           # Generación y formateo avanzado en Excel
├── main.py                   # Punto de entrada de la aplicación
├── requirements.txt          # Dependencias de Python
└── .env                      # Claves de acceso y configuración (ignorado por Git)
```
