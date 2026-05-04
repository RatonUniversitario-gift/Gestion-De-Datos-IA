import os
import glob
import logging
import pandas as pd
from datetime import datetime

# ── LOGGING (mismo archivo que ingestion.py) ─────────────────
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename=os.path.join("logs", "ingestion.log"),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8'
)

# ── MAPEO DE ESTADOS ─────────────────────────────────────────
ESTADOS = {
    4:  "Enviada a Proveedor",
    5:  "En Proceso",
    6:  "Aceptada",
    12: "Recepción Conforme",
    13: "Pendiente de Recepcionar",
    14: "Recepcionada Parcialmente",
    15: "Recepcion Conforme Incompleta"
}

# ─────────────────────────────────────────────────────────────

def limpiar_compras(ruta_csv: str) -> bool:
    """
    Limpia y transforma un archivo compras_DDMMYYYY.csv de data/processed/.
    Guarda el resultado en la misma carpeta con sufijo _limpio.

    Transformaciones aplicadas:
      1. Eliminar filas con valores nulos o incompletos
      2. Eliminar duplicados exactos
      3. Limpiar espacios en blanco en texto
      4. Normalizar nombres de productos (title case, sin espacios dobles)
      5. Convertir CodigoEstado a numérico
      6. Agregar columna EstadoDescripcion (texto legible del estado)
      7. Agregar columna FechaProcesamiento
    """
    nombre_archivo = os.path.basename(ruta_csv)
    logging.info(f"Iniciando limpieza: {nombre_archivo}")
    print(f"[INFO] Limpiando {nombre_archivo}...")

    try:
        df = pd.read_csv(ruta_csv, encoding="utf-8-sig")
        total_inicial = len(df)

        # 1. Eliminar filas con cualquier valor nulo
        df = df.dropna(subset=["Codigo", "Nombre", "PrecioNeto", "OrdenTotal"])
        nulos = total_inicial - len(df)
        if nulos:
            logging.info(f"Filas con nulos eliminadas: {nulos}")

        # 2. Eliminar duplicados exactos
        antes = len(df)
        df = df.drop_duplicates()
        duplicados = antes - len(df)
        if duplicados:
            logging.info(f"Duplicados eliminados: {duplicados}")

        # 3. Limpiar espacios en columnas de texto
        df["Codigo"] = df["Codigo"].astype(str).str.strip()
        df["Nombre"] = df["Nombre"].astype(str).str.strip()

        # 4. Normalizar nombres: title case + sin espacios dobles
        df["Nombre"] = df["Nombre"].str.title()
        df["Nombre"] = df["Nombre"].str.replace(r"\s+", " ", regex=True)

        # 5. Convertir CodigoEstado a numérico (elimina filas con valor inválido)
        df["CodigoEstado"] = pd.to_numeric(df["CodigoEstado"], errors="coerce")
        invalidos = df["CodigoEstado"].isna().sum()
        if invalidos:
            logging.info(f"Filas con CodigoEstado inválido eliminadas: {invalidos}")
        df = df.dropna(subset=["CodigoEstado"])
        df["CodigoEstado"] = df["CodigoEstado"].astype(int)

        # 6. Agregar descripción legible del estado
        df["EstadoDescripcion"] = df["CodigoEstado"].map(ESTADOS).fillna("Desconocido")

        # 7. Agregar fecha de procesamiento
        df["FechaProcesamiento"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # ── Ordenar columnas ──────────────────────────────────
        df = df[["Codigo", "Nombre", "CodigoEstado", "EstadoDescripcion",
         "TipoMoneda", "OrdenTotalNeto", "OrdenTotal",
         "Producto", "Cantidad", "PrecioNeto", "ItemTotal",
         "FechaCreacion",  "FechaProcesamiento"]]
        df = df.sort_values("Codigo").reset_index(drop=True)

        # ── Guardar con sufijo _limpio en la misma carpeta ───
        nombre_base = os.path.splitext(nombre_archivo)[0]
        ruta_salida = os.path.join("data/processed/limpio", f"{nombre_base}_limpio.csv")
        df.to_csv(ruta_salida, index=False, encoding="utf-8-sig")

        logging.info(f"Éxito: Archivo limpio guardado en {ruta_salida}")
        logging.info(f"Registros finales: {len(df)} (de {total_inicial} originales)")
        print(f"[INFO] Guardado en {ruta_salida} ({len(df)} registros)")
        return True

    except Exception as e:
        logging.error(f"Error al limpiar {nombre_archivo}: {e}")
        print(f"[ERROR] {nombre_archivo}: {e}")
        return False


def ejecutar_limpieza():
    """
    Busca todos los CSV de compras en data/processed/ que no tengan
    sufijo _limpio y aplica el proceso de limpieza a cada uno.
    """
    logging.info("=" * 50)
    logging.info("INICIO - Limpieza y transformación de datos")
    logging.info("=" * 50)

    archivos = [
        f for f in glob.glob("data/processed/detalle/detalleCompra_*.csv")
        if "_limpio" not in f
    ]

    if not archivos:
        msg = "No se encontraron archivos para limpiar. Ejecuta primero ingestion.py"
        logging.warning(msg)
        print(f"[ADVERTENCIA] {msg}")
        return

    print(f"[INFO] Archivos encontrados: {len(archivos)}")
    exitosos, fallidos = 0, 0

    for ruta in archivos:
        if limpiar_compras(ruta):
            exitosos += 1
        else:
            fallidos += 1

    logging.info(f"Limpieza completada — Exitosos: {exitosos} | Fallidos: {fallidos}")
    logging.info("=" * 50)
    print(f"\n[INFO] Limpieza finalizada: {exitosos} OK, {fallidos} con error.")


if __name__ == "__main__":
    ejecutar_limpieza()