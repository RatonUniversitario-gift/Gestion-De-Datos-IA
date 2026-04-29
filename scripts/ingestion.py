import os
import json
import requests
import pandas as pd
import logging
from datetime import datetime

# --- CONFIGURACIÓN DEL LOGGING ---
# Esto asegura que los logs se guarden en la carpeta correcta con fecha y hora
log_path = os.path.join("logs", "ingestion.log")
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8'
)

def consultar_chilecompra():
    # 1. Configuración de credenciales
    TICKET = os.getenv("CHILECOMPRA_TICKET", "token")
    fecha = datetime.now().strftime("%d%m%Y")
    
    # Endpoint de ordenes de Compra
    url = f"https://api.mercadopublico.cl/servicios/v1/publico/ordenesdecompra.json?estado=todos&ticket={TICKET}"
    
    try:
        logging.info(f"Iniciando proceso de ingesta para la fecha: {fecha}")
        
        res = requests.get(url, timeout=30)
        res.raise_for_status()  # Verifica si hubo error en la petición HTTP
        data = res.json()
        
        # Guardar Raw Data (JSON)
        raw_path = f"data/raw/compras_{fecha}.json"
        with open(raw_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        logging.info(f"Éxito: JSON crudo guardado en {raw_path}")
        
        # Procesamiento con Pandas
        if "Listado" in data and data["Listado"] is not None:
            df = pd.DataFrame(data["Listado"])
            
            # Selección de columnas relevantes para el modelo de IA
            df_final = df[['Codigo', 'Nombre', 'CodigoEstado']].copy()
            
            # Guardar Processed Data (CSV)
            output_path = f"data/processed/compras_{fecha}.csv"
            df_final.to_csv(output_path, index=False, encoding="utf-8-sig")
            
            logging.info(f"Éxito: Datos procesados guardados en {output_path}")
            logging.info(f"Registros procesados: {len(df_final)}")
        else:
            logging.warning("No se encontraron datos en el 'Listado' o el ticket de acceso es inválido.")
            
    except requests.exceptions.RequestException as e:
        logging.error(f"Error de conexión o timeout con la API de ChileCompra: {e}")
    except Exception as e:
        logging.error(f"Error crítico no esperado durante el proceso: {e}")

if __name__ == "__main__":
    consultar_chilecompra()