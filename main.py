"""Archivo principal que ejecuta el sistema"""

from src.extractors import cargar_presupuestos
from src.processor import comparar_presupuestos
from src.exporter import exportar_a_excel


def main():
    """Funcion para inicirar el sistema, si no encuentra mas de 1 presupuesto da un mensaje"""
    carpeta_entrada = "data/input"
    archivo_salida = "data/output/cuadro_comparativo.xlsx"

    print("=== INICIANDO COMPARADOR DE PRESUPUESTOS ===")

    presupuestos = cargar_presupuestos(carpeta_entrada)

    if len(presupuestos) < 2:
        print(
            f"Se encontraron{len(presupuestos)} presupuestos en '{carpeta_entrada}'.")
        print("Por favor, agrega al menos 2 presupuestos (.pdf, .png, .jpg o .txt para comparar.)")
        return

    resultado = comparar_presupuestos(presupuestos)
    exportar_a_excel(resultado, archivo_salida)
    print("=== PROCESO FINALIZADO ===")


if __name__ == "__main__":
    main()
