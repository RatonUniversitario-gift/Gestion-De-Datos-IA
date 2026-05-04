# Gestión de Datos para IA - Pipeline de Ingesta

Este repositorio contiene un pipeline automatizado de ingesta y procesamiento de datos (ETL). El proyecto se encarga de extraer datos en formato JSON (potencialmente desde una API), transformarlos y estructurarlos utilizando Pandas, para finalmente almacenarlos como archivos CSV listos para ser consumidos por modelos de Inteligencia Artificial.

Tecnologías Utilizadas

*   **Python 3.x:** Lenguaje principal del script de ingesta.
*   **Pandas:** Para la limpieza, transformación y estructuración de los datos.
*   **Requests:** Para la extracción de datos desde fuentes externas/APIs.
*   **GitHub Actions:** Para la automatización y ejecución programada del pipeline (`ingesta.yml`).

Estructura del Proyecto

El repositorio sigue una arquitectura estándar para proyectos de datos:

├── .github/workflows/   # Configuraciones de CI/CD (Automatización de ingesta)
├── data/
│   ├── processed/       # Datos limpios y estructurados listos para usar (.csv)
│       ├── compras/     # CSV con listado general de órdenes
│       ├── detalle/     # CSV con detalle enriquecido (precios, productos)
│       └── limpio/      # CSV procesados y normalizados listos para IA  
│   └── raw/             # Datos crudos extraídos originalmente (.json)
├── docs/                # Documentación técnica del proyecto
├── logs/                # Registro de eventos y errores de la ejecución (ingestion.log)
├── scripts/
│   └── ingestion.py     # Script principal de extracción y transformación
├── README.md            # Documentación principal
└── requirements.txt     # Dependencias del proyecto

Instalación y Uso Local

Si deseas ejecutar este pipeline en tu propio entorno local, sigue estos pasos:

1.  Clona este repositorio:
    ```bash
    git clone [https://github.com/TU_USUARIO/Gestion-De-Datos-IA.git](https://github.com/TU_USUARIO/Gestion-De-Datos-IA.git)
    cd Gestion-De-Datos-IA
    ```

2.  Crea un entorno virtual e instala las dependencias:
    ```bash
    python -m venv venv
    source venv/Scripts/activate  # En Windows
    pip install -r requirements.txt
    ```

3. Configura tu ticket en un archivo .env en la raíz:
   CHILECOMPRA_TICKET=tu_ticket_aqui

4. Ejecuta la ingesta:
   python scripts/ingestion.py

5. Ejecuta la limpieza:
   python scripts/limpieza.py
   
El script leerá la configuración, extraerá los datos, registrará el proceso en `logs/ingestion.log` y guardará el resultado final en la carpeta `data/processed/`.

Documentación Adicional

Para entender en profundidad cómo los datos se transforman desde su estado crudo hasta el formato procesado, revisa el archivo [proceso.md](docs/proceso.md) en la carpeta de documentación.
