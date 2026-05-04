# Proceso de Ingesta y Transformación de Datos

Este documento detalla el flujo de trabajo (Pipeline ETL) implementado en el script `scripts/ingestion.py`. El objetivo principal es garantizar que los datos crudos se conviertan en información estructurada y de alta calidad para futuros desarrollos en Inteligencia Artificial.

## 1. Extracción (Extract)
El proceso comienza obteniendo la API pública de Mercado Público (ChileCompra) mediante dos endpoints:
*   **Listado general:** Se obtienen todas las órdenes de compra del día, guardadas en `data/raw/compras_DDMMAAAA.json` y `data/processed/compras/`.
*   **Detalle enriquecido:** Se consultan las primeras 10 órdenes con información completa (precios, productos, impuestos), guardadas en `data/raw/detalleCompra_DDMMAAAA.json` y `data/processed/detalle/`.
*   El ticket de acceso se gestiona como variable de entorno (`CHILECOMPRA_TICKET`) mediante un archivo `.env` local, sin exponerlo en el código.

## 2. Transformación (Transform)
Una vez que los datos crudos están asegurados, se inicia la limpieza y estructuración:
*   Se utiliza `pandas` para cargar los archivos JSON y convertirlos en DataFrames.
*   **Limpieza:** Se manejan valores nulos, se normalizan los tipos de datos (por ejemplo, asegurar que las fechas sean objetos *datetime* y los montos sean numéricos) y se eliminan duplicados si los hubiera.
*   **Estructuración:** Las estructuras anidadas que suelen venir en los JSON (como detalles de compra dentro de una orden general) se "aplanan" para que encajen en un formato tabular.

## 2.5 Limpieza (script: limpieza.py)
- Lee los archivos de data/processed/detalle/
- Elimina filas donde faltan campos críticos: Codigo, Nombre, PrecioNeto, OrdenTotal
- Normaliza nombres de productos a title case y elimina espacios dobles
- Convierte CodigoEstado numérico a texto legible (EstadoDescripcion)
- Guarda el resultado en data/processed/limpio/ con sufijo _limpio.csv

## 3. Carga (Load)
El último paso del script en Python es guardar los datos procesados.
*   El DataFrame resultante se exporta como un archivo separado por comas dentro del directorio `data/processed/` (ej. `compras_DDMMAAAA.csv`).
*   Todo el proceso, incluyendo posibles errores de conexión o datos corruptos, queda registrado en `logs/ingestion.log` para facilitar la depuración y el monitoreo.

## 4. Automatización (CI/CD)
Para mantener el flujo de datos actualizado sin intervención manual, el proyecto utiliza **GitHub Actions**.
*   El archivo `.github/workflows/ingesta.yml` define un *cron job* que ejecuta el script `ingestion.py` de forma automática según la periodicidad configurada (diaria, semanal, etc.).
*   Una vez que el runner de GitHub termina de procesar los datos, hace un *commit* y un *push* automático de los nuevos archivos CSV a la rama principal del repositorio, manteniendo la carpeta `data/processed/` siempre al día.
