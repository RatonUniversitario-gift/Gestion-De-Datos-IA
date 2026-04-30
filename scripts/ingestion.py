import os
import json
import requests
import pandas as pd
import logging
import time
from datetime import datetime

# --- CONFIGURACIÓN DEL LOGGING ---
log_path = os.path.join("logs", "ingestion.log")
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8'
)

def consultar_chilecompra():
    TICKET = os.getenv("CHILECOMPRA_TICKET", "token")
    fecha = datetime.now().strftime("%d%m%Y")
    
    # Endpoint de ordenes de Compra
    url = f"https://api.mercadopublico.cl/servicios/v1/publico/ordenesdecompra.json?estado=todos&ticket={TICKET}"
    
    try:
        logging.info(f"Iniciando proceso de ingesta para la fecha: {fecha}")
        
        res = requests.get(url, timeout=30)
        res.raise_for_status()  
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
            
            # Extraer detalles de los primeros 10
            primeros_10 = df_final['Codigo'].head(10).tolist()
            if primeros_10:
                extraerDetalles(primeros_10)
        else:
            logging.warning("No se encontraron datos en el 'Listado' o el ticket de acceso es inválido.")
            
    except requests.exceptions.RequestException as e:
        logging.error(f"Error de conexión o timeout con la API de ChileCompra: {e}")
    except Exception as e:
        logging.error(f"Error crítico no esperado durante el proceso: {e}")


def extraerDetalles(codigos):
    TICKET = os.getenv("CHILECOMPRA_TICKET", "token")
    fecha = datetime.now().strftime("%d%m%Y")
    detalles_raw = []
    filas_csv = []
    
    for codigo in codigos:
        url = f"https://api.mercadopublico.cl/servicios/v1/publico/ordenesdecompra.json?codigo={codigo}&ticket={TICKET}"
        try:
            logging.info(f"Obteniendo detalle para: {codigo}")
            time.sleep(1.5)  # Esperar para no saturar la API (429 Too Many Requests)
            res = requests.get(url, timeout=30)
            res.raise_for_status()
            data = res.json()
            detalles_raw.append(data)
            
            if "Listado" in data and data["Listado"]:
                orden = data["Listado"][0]
                
                cod = orden.get("Codigo", "")
                nombre = orden.get("Nombre", "")
                cod_estado = orden.get("CodigoEstado", "")
                cod_tipo = orden.get("CodigoTipo", "")
                tipo = orden.get("Tipo", "")
                tipo_moneda = orden.get("TipoMoneda", "")
                
                tiene_items = orden.get("TieneItems", "")
                promedio_calificacion = orden.get("PromedioCalificacion", "")
                cantidad_evaluacion = orden.get("CantidadEvaluacion", "")
                orden_descuentos = orden.get("Descuentos", "")
                orden_cargos = orden.get("Cargos", "")
                orden_total_neto = orden.get("TotalNeto", "")
                orden_porcentaje_iva = orden.get("PorcentajeIva", "")
                orden_impuestos = orden.get("Impuestos", "")
                orden_total = orden.get("Total", "")
                
                fechas = orden.get("Fechas", {})
                f_creacion = fechas.get("FechaCreacion", "")
                f_envio = fechas.get("FechaEnvio", "")
                f_aceptacion = fechas.get("FechaAceptacion", "")
                f_cancelacion = fechas.get("FechaCancelacion", "")
                f_ultima_mod = fechas.get("FechaUltimaModificacion", "")
                
                items_obj = orden.get("Items", {})
                if not isinstance(items_obj, dict):
                    items_obj = {}
                    
                cantidad_items = items_obj.get("Cantidad", 0)
                listado_items = items_obj.get("Listado", [])
                
                if not listado_items:
                    filas_csv.append({
                        "Codigo": cod, "Nombre": nombre, "CodigoEstado": cod_estado,
                        "CodigoTipo": cod_tipo, "Tipo": tipo, "TipoMoneda": tipo_moneda,
                        "TieneItems": tiene_items, "PromedioCalificacion": promedio_calificacion, "CantidadEvaluacion": cantidad_evaluacion,
                        "OrdenDescuentos": orden_descuentos, "OrdenCargos": orden_cargos, "OrdenTotalNeto": orden_total_neto,
                        "OrdenPorcentajeIva": orden_porcentaje_iva, "OrdenImpuestos": orden_impuestos, "OrdenTotal": orden_total,
                        "FechaCreacion": f_creacion, "FechaEnvio": f_envio,
                        "FechaAceptacion": f_aceptacion, "FechaCancelacion": f_cancelacion,
                        "FechaUltimaModificacion": f_ultima_mod, "CantidadItems": cantidad_items,
                        "Producto": "", "Cantidad": "", "PrecioNeto": "",
                        "ItemTotalCargos": "", "ItemTotalDescuentos": "", "ItemTotalImpuestos": "", "ItemTotal": ""
                    })
                else:
                    for item in listado_items:
                        filas_csv.append({
                            "Codigo": cod, "Nombre": nombre, "CodigoEstado": cod_estado,
                            "CodigoTipo": cod_tipo, "Tipo": tipo, "TipoMoneda": tipo_moneda,
                            "TieneItems": tiene_items, "PromedioCalificacion": promedio_calificacion, "CantidadEvaluacion": cantidad_evaluacion,
                            "OrdenDescuentos": orden_descuentos, "OrdenCargos": orden_cargos, "OrdenTotalNeto": orden_total_neto,
                            "OrdenPorcentajeIva": orden_porcentaje_iva, "OrdenImpuestos": orden_impuestos, "OrdenTotal": orden_total,
                            "FechaCreacion": f_creacion, "FechaEnvio": f_envio,
                            "FechaAceptacion": f_aceptacion, "FechaCancelacion": f_cancelacion,
                            "FechaUltimaModificacion": f_ultima_mod, "CantidadItems": cantidad_items,
                            "Producto": item.get("Producto", ""),
                            "Cantidad": item.get("Cantidad", ""),
                            "PrecioNeto": item.get("PrecioNeto", ""),
                            "ItemTotalCargos": item.get("TotalCargos", ""),
                            "ItemTotalDescuentos": item.get("TotalDescuentos", ""),
                            "ItemTotalImpuestos": item.get("TotalImpuestos", ""),
                            "ItemTotal": item.get("Total", "")
                        })
                        
        except Exception as e:
            logging.error(f"Error al obtener detalle {codigo}: {e}")
            
    # Guardar raw JSON
    if detalles_raw:
        raw_path = f"data/raw/detalleCompra_{fecha}.json"
        with open(raw_path, "w", encoding="utf-8") as f:
            json.dump(detalles_raw, f, ensure_ascii=False, indent=4)
        logging.info(f"Éxito: Detalles raw guardados en {raw_path}")
        
    # Guardar processed CSV
    if filas_csv:
        df_detalles = pd.DataFrame(filas_csv)
        csv_path = f"data/processed/detalleCompra_{fecha}.csv"
        df_detalles.to_csv(csv_path, index=False, encoding="utf-8-sig")
        logging.info(f"Éxito: Detalles normalizados guardados en {csv_path}")

if __name__ == "__main__":
    consultar_chilecompra()