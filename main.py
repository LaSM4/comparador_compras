"""Archivo principal que ejecuta el comparador de presupuestos."""

import os
import sys
import argparse
from pathlib import Path
from src.extractors import cargar_presupuestos
from src.processor import comparar_presupuestos
from src.exporter import exportar_a_excel


def main():
    """Función para coordinar extracción, análisis y exportación."""
    base_dir = Path(__file__).resolve().parent

    parser = argparse.ArgumentParser(
        description="Comparador inteligente de presupuestos con IA (Gemini)."
    )
    parser.add_argument(
        "--input",
        "-i",
        default=str(base_dir / "data" / "input"),
        help="Ruta de la carpeta con presupuestos (default: data/input)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=str(base_dir / "data" / "output" / "cuadro_comparativo.xlsx"),
        help="Ruta del Excel de salida (default: data/output/cuadro.xlsx)",
    )
    parser.add_argument(
        "--model",
        "-m",
        default=os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
        help="Modelo de Gemini a utilizar (default: gemini-3.5-flash)",
    )

    args = parser.parse_args()

    # Configurar modelo en entorno si se especificó por CLI
    if args.model:
        os.environ["GEMINI_MODEL"] = args.model

    carpeta_entrada = args.input
    archivo_salida = args.output

    print("=== INICIANDO COMPARADOR DE PRESUPUESTOS ===")
    print(f"Carpeta de entrada : {carpeta_entrada}")
    print(f"Archivo de salida   : {archivo_salida}")

    try:
        presupuestos = cargar_presupuestos(carpeta_entrada)

        if len(presupuestos) < 2:
            print(
                f"\nSe encontraron {len(presupuestos)} presupuestos válidos "
                f"en '{carpeta_entrada}'."
            )
            print(
                "Por favor, agrega al menos 2 presupuestos (.pdf, .png, "
                ".jpg o .txt) para poder comparar."
            )
            return

        resultado = comparar_presupuestos(presupuestos)
        exportar_a_excel(resultado, archivo_salida)
        print("\n=== PROCESO FINALIZADO CON ÉXITO ===")

    except PermissionError:
        print(
            f"\n[Error de Permiso] No se pudo escribir en '{archivo_salida}'. "
            "Asegúrate de que el archivo no esté abierto en Microsoft Excel "
            "y vuelve a intentarlo."
        )
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[Cancelado] Operación cancelada por el usuario.")
        sys.exit(0)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"\n[Error en ejecución] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
