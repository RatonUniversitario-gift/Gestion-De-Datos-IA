import os
import json
import requests
import pandas as pd
from datetime import datetime

def consultar_chilecompra():
    # 1. Configuración de credenciales
    # Usamos os.getenv para que en GitHub Actions lea el "Secret"
    TICKET = os.getenv("CHILECOMPRA_TICKET", "token")
    fecha = datetime.now().strftime("%d%m%Y")
    
    # Endpoint de Órdenes de Compra
    url = f"https://api.mercadopublico.cl/servicios/v1/publico/ordenesdecompra.json?estado=todos&ticket={TICKET}"
    
    try:
        print(f"Iniciando ingesta para la fecha: {fecha}")
        res = requests.get(url, timeout=30)
        data = res.json()
        
        raw_path = f"data/raw/compras_{fecha}.json"
        with open(raw_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Exito: Json crudo guardado en {raw_path}")
        
        if "Listado" in data and data["Listado"] is not None:
            df = pd.DataFrame(data["Listado"])
            
            
            df_final = df[['Codigo', 'Nombre', 'CodigoEstado']].copy()
            
            
            output_path = f"data/processed/compras_{fecha}.csv"
            df_final.to_csv(output_path, index=False, encoding="utf-8-sig")
            
            print(f"Exito: Guardado en {output_path}")
        else:
            print("Advertencia: No se encontraron datos o el ticket es invalido.")
            
    except Exception as e:
        print(f"Error critico: {e}")

if __name__ == "__main__":
    consultar_chilecompra()