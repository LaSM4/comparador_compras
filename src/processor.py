"""Clases que configuran los prompts para Gemini"""
import json
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field

# Carga las variables del archivo .env (como GEMINI_API_KEY)
load_dotenv()


class OfertaProveedor(BaseModel):
    """Clase donde se lee la oferta del proveedor"""
    proveedor: str = Field(description="Nombre del proveedor")
    descripcion_cotizada: str = Field(
        description="Producto tal cual figura en su presupuesto, o 'No cotizado'")
    cantidad: float = Field(description="Cantidad cotizada (0 si no cotizó)")
    precio_unitario: float = Field(
        description="Precio unitario en números (0 si no cotizó)")
    precio_total: float = Field(
        description="Precio total para este item (cantidad * precio_unitario)")


class ItemComparado(BaseModel):
    """Clase donde se lee el item especifico del producto"""
    producto_base: str = Field(
        description="Nombre genérico del producto que se está comparando")
    ofertas: list[OfertaProveedor] = Field(
        description="Lista con la oferta de cada proveedor con este producto")
    diferencias_tecnicas: str = Field(
        description="""
        Explicacion breve si hay diferencias de especificaciones, marcas, cantidades, medidas, tamaños, potencia, 
        y todo lo relacionado en la característica del producto""")
    mejor_opcion: str = Field(
        description="Proveedor con la mejor ecuacion beneficio/costo para este item")


class ResultadoComparacion(BaseModel):
    """Tiramos el resultado de la comparacion"""
    items: list[ItemComparado] = Field(
        description="Lista de todos los productos comparados")


def comparar_presupuestos(presupuestos: dict) -> ResultadoComparacion:
    """Envia todos los presupuestos a Gemini y devuelve la comparacion estructurada"""
    client = genai.Client()

    texto_proveedores = ""
    lista_nombres = list(presupuestos.keys())

    for proveedor, contenido in presupuestos.items():
        texto_proveedores += f"\n--- PROVEEDOR: {proveedor} ---\n{contenido}\n"

    prompt = f"""
Actúa como un analista senior de compras, licitaciones y evaluación técnica de presupuestos.

OBJETIVO
Analizar, normalizar y comparar los presupuestos de los siguientes proveedores:

{', '.join(lista_nombres)}

CRITERIOS DE ANÁLISIS

1. NORMALIZACIÓN DE PRODUCTOS
- Identifica productos iguales, similares o comparables.
- Genera un nombre común denominado "producto_base".
- El nombre debe ser técnico, neutro y representativo.
- Elimina diferencias puramente comerciales o de redacción.

2. AGRUPACIÓN Y ALERTA TÉCNICA
- Si un proveedor cotiza una alternativa o sustituto con leve diferencia de capacidad, medida o cantidad para el mismo ítem pedido (ej: Proveedor A cotiza 1 Disyuntor de 32A y Proveedor B cotiza 2 Disyuntores de 16A, o distinta marca/potencia), AGRÚPALOS en la misma fila bajo el mismo "producto_base" para poder compararlos lado a lado.
- Sin embargo, NUNCA asumas que son técnicamente iguales sin advertirlo: explica con rigor en "diferencias_tecnicas" si la diferencia altera la seguridad, capacidad o norma técnica, y tenlo en cuenta al elegir "mejor_opcion".

3. INTERPRETACIÓN INTELIGENTE
- Comprende sinónimos, abreviaturas y distintas formas de descripción.
- Considera marcas, modelos, formatos y unidades.
- Detecta equivalencias únicamente cuando mantengan la misma función y especificación técnica esencial.

4. OFERTAS POR PROVEEDOR
Para cada producto_base debe existir una oferta de TODOS los proveedores:

{', '.join(lista_nombres)}

Si un proveedor no cotizó:

descripcion_cotizada = "No cotizado"
cantidad = 0
precio_unitario = 0
precio_total = 0

5. CÁLCULOS
- precio_total = cantidad × precio_unitario
- Verifica todos los cálculos.
- No inventes valores faltantes.
- Utiliza únicamente los datos presentes en los presupuestos.

6. DIFERENCIAS TÉCNICAS
Registrar de forma detallada únicamente las diferencias relevantes:
- marca
- modelo
- capacidad
- amperaje
- potencia
- dimensiones
- material
- presentación
- cantidad
- norma técnica
- características funcionales

7. CONTROL DE CALIDAD
Antes de responder valida que:

- No existan productos duplicados.
- No falte ningún proveedor.
- Todos los cálculos sean correctos.
- No haya equivalencias inseguras o técnicamente incorrectas.
- Las diferencias técnicas estén claramente documentadas.

8. PRINCIPIO GENERAL
Prioriza siempre la precisión técnica sobre la agrupación.
Ante cualquier duda técnica o de seguridad, NO asumir equivalencia.

RESPUESTA
Devuelve exclusivamente JSON válido.

PRESUPUESTOS A COMPARAR:

{texto_proveedores}
"""
    print("Analizando y comparando presupuesstos con Gemini...")
    interaction = client.interactions.create(
        model="gemini-3.8-flash",
        input=prompt,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema":
            ResultadoComparacion.model_json_schema(),
        },
    )

    return ResultadoComparacion.model_validate_json(interaction.output_text)
