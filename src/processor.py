"""Módulo de procesamiento y comparación de presupuestos con Gemini."""

from ast import Import
import os
from dotenv import load_dotenv  # pyrefly: ignore[missing-import]
from google import genai  # pyrefly: ignore[missing-import]
from pydantic import BaseModel, Field  # pyrefly: ignore[missing-import]

# Carga variables de entorno (.env)
load_dotenv()


class OfertaProveedor(BaseModel):
    """Detalle de la oferta de un proveedor para un producto específico."""
    proveedor: str = Field(
        description="Nombre comercial o razón social real del proveedor (ej: 'Electropar', '7 Saltos S.A.')"
    )
    descripcion_cotizada: str = Field(
        description="Descripción textual del producto en la cotización, o 'No cotizado'"
    )
    cantidad: float = Field(
        default=0.0,
        description="Cantidad cotizada (0 si no cotizó)"
    )
    unidad_medida: str = Field(
        default="un",
        description="Unidad de medida (ej: 'm', 'un', 'kg', 'caja', 'global')"
    )
    precio_unitario: float = Field(
        default=0.0,
        description="Precio unitario numérico (0 si no cotizó)"
    )
    precio_total: float = Field(
        default=0.0,
        description="Precio total del ítem (cantidad * precio_unitario)"
    )
    moneda: str = Field(
        default="GS",
        description="Moneda cotizada detectada (ej: 'GS', 'USD', 'ARS')"
    )


class ItemComparado(BaseModel):
    """Producto normalizado comparado entre todos los proveedores."""
    producto_base: str = Field(
        description="Nombre genérico y representativo del producto comparado"
    )
    ofertas: list[OfertaProveedor] = Field(
        description="Oferta de cada proveedor participante para este producto"
    )
    diferencias_tecnicas: str = Field(
        description="Diferencias relevantes de especificaciones, marcas, potencias, medidas o normas técnicas"
    )
    mejor_opcion: str = Field(
        description="Proveedor recomendado con la mejor relación beneficio/costo para este ítem"
    )
    justificacion_mejor_opcion: str = Field(
        default="",
        description="Motivo conciso de la elección (ej: 'Menor precio unitario cumpliendo norma técnica')"
    )


class ResumenGeneral(BaseModel):
    """Resumen y conclusiones ejecutivas de la comparación."""
    proveedores_detectados: list[str] = Field(
        description="Lista de nombres comerciales reales de los proveedores analizados"
    )
    moneda_principal: str = Field(
        default="GS",
        description="Moneda principal predominante en los presupuestos"
    )
    observaciones_generales: str = Field(
        description="Observaciones globales sobre plazos de entrega, condiciones de pago, validez o garantías"
    )
    conclusion_recomendada: str = Field(
        description="Dictamen final y recomendación de adjudicación (ej: adjudicar todo a un proveedor o compra mixta)"
    )


class ResultadoComparacion(BaseModel):
    """Resultado completo del análisis comparativo."""
    resumen: ResumenGeneral = Field(
        description="Resumen ejecutivo y condiciones comerciales"
    )
    items: list[ItemComparado] = Field(
        description="Lista de todos los productos y sus ofertas comparadas"
    )


def comparar_presupuestos(presupuestos: dict[str, str]) -> ResultadoComparacion:
    """Envía los presupuestos a Gemini y devuelve la comparativa estructurada."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "No se encontró la variable GEMINI_API_KEY en el entorno o archivo .env. "
            "Por favor, agrégala en tu archivo .env: GEMINI_API_KEY=tu_clave_aqui"
        )

    client = genai.Client()

    texto_documentos = ""
    for identificador, contenido in presupuestos.items():
        texto_documentos += f"\n=== INICIO DOCUMENTO ({identificador}) ===\n{contenido}\n=== FIN DOCUMENTO ===\n"

    prompt = f"""
Actúa como un analista senior de compras, licitaciones y evaluación técnica de presupuestos.

OBJETIVO:
Analizar a profundidad, normalizar y comparar técnicamente los presupuestos contenidos en los documentos adjuntos.

INSTRUCCIONES CLAVE:
1. IDENTIFICACIÓN DE PROVEEDORES REALES:
   - Analiza el encabezado, RUC/NIT, correos electrónicos, membretes o firmas de cada documento para identificar la RAZÓN SOCIAL o NOMBRE COMERCIAL REAL de la empresa que cotiza.
   - NUNCA uses nombres de archivo genéricos (como "WhatsApp Image...") como nombre de proveedor si en el documento se lee el nombre real del comercio o vendedor.

2. NORMALIZACIÓN DE PRODUCTOS:
   - Agrupa los ítems equivalentes bajo un "producto_base" neutro y técnico.
   - Si un proveedor no cotizó un ítem, coloca descripcion_cotizada = "No cotizado", cantidad = 0, precio_unitario = 0, precio_total = 0.
   - Registra claramente la unidad de medida y la moneda de cada cotización.

3. EVALUACIÓN TÉCNICA Y MEJOR OPCIÓN:
   - En "diferencias_tecnicas", destaca marcas, calidades, potencias, medidas o advertencias si las especificaciones difieren.
   - Determina la "mejor_opcion" y proporciona una "justificacion_mejor_opcion" con criterio técnico-económico.

4. RESUMEN EJECUTIVO:
   - Completa el resumen con observaciones de plazos de entrega, condiciones de pago (contado/crédito) y tu recomendación final.

DOCUMENTOS A ANALIZAR:
{texto_documentos}
"""

    modelo_preferido = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    modelos_a_probar = [modelo_preferido]
    if modelo_preferido != "gemini-3.5-flash":
        modelos_a_probar.append("gemini-3.5-flash")

    ultimo_error = None
    for modelo in modelos_a_probar:
        try:
            print(
                f"Analizando y comparando presupuestos con Gemini ({modelo})...")
            interaction = client.interactions.create(
                model=modelo,
                input=prompt,
                response_format={
                    "type": "text",
                    "mime_type": "application/json",
                    "schema": ResultadoComparacion.model_json_schema(),
                },
                timeout=90,
            )
            return ResultadoComparacion.model_validate_json(interaction.output_text)
        except ImportError as e:
            print(f"  [Aviso] No se pudo completar con {modelo}: {e}")
            ultimo_error = e

    raise RuntimeError(
        f"Error al procesar los presupuestos con Gemini: {ultimo_error}")
