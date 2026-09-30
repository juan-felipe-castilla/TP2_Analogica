import os
import subprocess
import re
import pandas as pd
import glob

# Rutas
LTSPICE_EXE = os.path.expanduser("~/.wine/drive_c/Program Files/ADI/LTspice/LTspice.exe")
NETLIST_ENTRADA = "template_Vceq.net"      
NETLIST_TEMP = "simulacion_dc.net"
LOG_TEMP = "simulacion_dc.log"
EXCEL_SALIDA = "Telemetria_Total.xlsx"

# TUS VALORES GANADORES FÍSICOS
VALORES_FISICOS = {
    'RBD': 1000000, 'RED': 47, 'R1E': 120000, 'R2E': 27000,
    'RCE': 6800, 'REE': 1200, 'R2S': 100000, 'R1S': 47000,
    'RES': 10, 'RO': 7.5, 'AMP_IN': "0", 'AMP_OUT': "0", 'VAL_RL': "8"
}

def parsear_valor_spice(val_str):
    val_str = val_str.lower().strip()
    multiplicadores = {'meg': 1e6, 'k': 1e3, 'm': 1e-3, 'u': 1e-6, 'µ': 1e-6}
    for sufijo, mult in multiplicadores.items():
        if val_str.endswith(sufijo):
            try: return float(val_str[:-len(sufijo)]) * mult
            except ValueError: pass
    try: return float(val_str)
    except ValueError: return 0.0

def extraer_componentes(archivo_net, params):
    resistencias, transistores = [], []
    with open(archivo_net, 'r', encoding='utf-8', errors='ignore') as f:
        for linea in f:
            linea_limpia = linea.strip()
            if not linea_limpia or linea_limpia.startswith(('*', '.', ';')): continue
            
            for key, val in params.items():
                linea_limpia = linea_limpia.replace(f"{{{key}}}", str(val))
                
            tokens = linea_limpia.split()
            prefijo = tokens[0][0].upper()

            if prefijo == 'R' and len(tokens) >= 4:
                resistencias.append({
                    'Nombre': tokens[0].upper(), 'Nodo1': tokens[1].upper(), 'Nodo2': tokens[2].upper(),
                    'Valor_Str': tokens[3], 'Valor_Ohm': parsear_valor_spice(tokens[3])
                })
            elif prefijo == 'Q' and len(tokens) >= 5:
                modelo = tokens[5].upper() if len(tokens) >= 6 and tokens[4] in ['0', 'N001', 'GND'] else tokens[4].upper()
                transistores.append({
                    'Nombre': tokens[0].upper(), 'Colector': tokens[1].upper(),
                    'Base': tokens[2].upper(), 'Emisor': tokens[3].upper(), 'Modelo': modelo
                })
    return resistencias, transistores

def inyectar_valores_y_sondas(origen, destino, params, resistencias, transistores):
    with open(origen, 'r', encoding='utf-8', errors='ignore') as f:
        netlist = f.read()
        
    for key, val in params.items():
        netlist = netlist.replace(f"{{{key}}}", str(val))
        
    lineas_filtradas = []
    for l in netlist.splitlines():
        l_strip = l.strip().lower()
        if l_strip.startswith(('.tran', '.ac', '.meas', '.backanno', '.end', '.options', '.op')):
            continue
        lineas_filtradas.append(l)

    nodos = set()
    for r in resistencias: nodos.update([r['Nodo1'], r['Nodo2']])
    for q in transistores: nodos.update([q['Colector'], q['Base'], q['Emisor']])
        
    if '0' in nodos: nodos.remove('0')
    if 'GND' in nodos: nodos.remove('GND')

    for nodo in nodos:
        lineas_filtradas.append(f".meas TRAN V_{nodo} AVG V({nodo})")
    for r in resistencias:
        lineas_filtradas.append(f".meas TRAN I_{r['Nombre']} AVG I({r['Nombre']})")
    
    # Sondas de asalto directo a los pines del transistor
    for q in transistores:
        lineas_filtradas.append(f".meas TRAN I_C_{q['Nombre']} AVG Ic({q['Nombre']})")
        lineas_filtradas.append(f".meas TRAN I_B_{q['Nombre']} AVG Ib({q['Nombre']})")

    lineas_filtradas.append(".tran 0 1m 0")
    lineas_filtradas.append(".end")
        
    with open(destino, 'w', encoding='utf-8') as f:
        f.write("\n".join(lineas_filtradas) + "\n")

def extraer_datos_log_seguro(archivo_log):
    if not os.path.exists(archivo_log): return {}, {}
    try:
        with open(archivo_log, 'r', encoding='utf-16') as f: contenido = f.read()
    except:
        with open(archivo_log, 'r', encoding='utf-8', errors='ignore') as f: contenido = f.read()

    tensiones, corrientes = {}, {}
    for linea in contenido.splitlines():
        match_v = re.search(r"v_([\w\-]+).*?=\s*([0-9\.eE\+\-]+)", linea, re.IGNORECASE)
        if match_v: tensiones[match_v.group(1).upper()] = float(match_v.group(2))
            
        match_i = re.search(r"i_([\w\-]+).*?=\s*([0-9\.eE\+\-]+)", linea, re.IGNORECASE)
        if match_i: corrientes[match_i.group(1).upper()] = float(match_i.group(2))
            
    return tensiones, corrientes

def procesar_circuito():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    for arch in glob.glob("simulacion_dc*"):
        try: os.remove(arch)
        except: pass

    if not os.path.exists(NETLIST_ENTRADA):
        print(f"Error: No se encontró '{NETLIST_ENTRADA}'.")
        return

    resistencias, transistores = extraer_componentes(NETLIST_ENTRADA, VALORES_FISICOS)
    print("Inyectando sondas de potencia e impedancia...")
    inyectar_valores_y_sondas(NETLIST_ENTRADA, NETLIST_TEMP, VALORES_FISICOS, resistencias, transistores)
    subprocess.run(["wine", LTSPICE_EXE, "-b", "-Run", NETLIST_TEMP], capture_output=True)

    tensiones, corrientes = extraer_datos_log_seguro(LOG_TEMP)
    if not tensiones: return
    tensiones['0'] = 0.0 

    datos_r = []
    for r in resistencias:
        v1 = tensiones.get(r['Nodo1'], 0.0)
        v2 = tensiones.get(r['Nodo2'], 0.0)
        v_drop = abs(v1 - v2)
        i_dc = abs(corrientes.get(r['Nombre'], v_drop / r['Valor_Ohm'] if r['Valor_Ohm'] > 0 else 0.0))
        datos_r.append({
            'Resistencia': r['Nombre'], 'Valor [Ω]': r['Valor_Ohm'], 
            'Caída Vdc [V]': round(v_drop, 4), 'Corriente [mA]': round(i_dc * 1000, 4), 
            'Potencia [mW]': round((i_dc ** 2) * r['Valor_Ohm'] * 1000, 3)
        })

    datos_q = []
    for q in transistores:
        vc = tensiones.get(q['Colector'], 0.0)
        vb = tensiones.get(q['Base'], 0.0)
        ve = tensiones.get(q['Emisor'], 0.0)
        es_pnp = 'PNP' in q['Modelo'] or q['Nombre'] == 'Q5'

        vceq = (ve - vc) if es_pnp else (vc - ve)
        vbeq = (vb - ve) if es_pnp else (vb - ve)
        estado = "Activa" if (vceq > 0.3 and abs(vbeq) > 0.5) else ("Saturación" if vceq <= 0.3 else "Corte")
        
        # Telemetría de Fuego (Potencia Térmica)
        ic = abs(corrientes.get(f"C_{q['Nombre']}", 0.0))
        ib = abs(corrientes.get(f"B_{q['Nombre']}", 0.0))
        potencia_mw = (abs(vceq) * ic * 1000) + (abs(vbeq) * ib * 1000)

        datos_q.append({
            'Transistor': q['Nombre'], 'Tipo': 'PNP' if es_pnp else 'NPN',
            'Vc [V]': round(vc, 4), 'Vb [V]': round(vb, 4), 'Ve [V]': round(ve, 4),
            'Vceq [V]': round(vceq, 4), 'Potencia [mW]': round(potencia_mw, 3), 'Región DC': estado
        })

    df_r = pd.DataFrame(datos_r)
    df_q = pd.DataFrame(datos_q)

    with pd.ExcelWriter(EXCEL_SALIDA, engine='openpyxl') as writer:
        df_q.to_excel(writer, sheet_name='Transistores (V & Potencia)', index=False)
        df_r.to_excel(writer, sheet_name='Resistencias (Potencia)', index=False)
        for sheetname in writer.sheets:
            ws = writer.sheets[sheetname]
            for col in ws.columns:
                ws.column_dimensions[col[0].column_letter].width = max(max(len(str(cell.value or '')) for cell in col) + 3, 12)

    print("\n" + "="*75)
    print("   TELEMETRÍA TÉRMICA DE TRANSISTORES")
    print("="*75)
    print(df_q[['Transistor', 'Vb [V]', 'Ve [V]', 'Vc [V]', 'Vceq [V]', 'Potencia [mW]']].to_string(index=False))
    print(f"\n-> Archivo Excel de inteligencia generado: '{EXCEL_SALIDA}'")

    for temp in glob.glob("simulacion_dc*"):
        try: os.remove(temp)
        except: pass

if __name__ == "__main__":
    procesar_circuito()