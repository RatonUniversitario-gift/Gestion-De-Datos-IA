# Pipeline de Ingesta - ChileCompra
Este proyecto automatiza la recolección diaria de órdenes de compra desde la API de mercado publico(ChileCompra) para su posterior analisis y predicción de precios.

## Estructura del Proyecto
- `scripts/`: Contiene `ingestion.py`, el script principal de extracción, transformación y carga (ETL).
- `data/raw/`: Archivos JSON crudos por fecha.
- `data/processed/`: Archivos CSV resultantes por fecha.
- `logs/`: Registros históricos de ejecución del pipeline.
- `docs/`: Documentación técnica detallada del proceso.

## Tecnologías Utilizadas
- **Python 3.x**: Lógica de ingesta.
- **Pandas**: Procesamiento y limpieza de datos.
- **GitHub Actions**: Automatización de la tarea programada (cron diario).
- **Logging**: Sistema de trazabilidad de errores y eventos.

## Requisitos e Instalación
Para ejecutar este proyecto localmente:
1. Clonar el repositorio.
2. Instalar dependencias: `pip install -r requirements.txt`
3. Ejecutar: `python scripts/ingestion.py`

## Gestión de Errores
El sistema implementa un robusto manejo de excepciones y logging. Cualquier fallo en la conexión o en la estructura de los datos queda registrado en `logs/ingestion.log`, asegurando que el flujo de datos para la IA sea confiable y auditable.