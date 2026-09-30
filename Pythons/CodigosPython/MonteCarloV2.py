import os
import subprocess
import re
import random

# VOLVEMOS A TU RUTA ORIGINAL (La que Wine entiende perfecto)
LTSPICE_EXE = os.path.expanduser("~/.wine/drive_c/Program Files/ADI/LTspice/LTspice.exe")
TEMPLATE_FILE = "template.net"
SIM_FILE = "simulacion_temp.net"
LOG_FILE = "simulacion_temp.log"

def generar_y_correr(params):
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        netlist = f.read()
    
    for key, val in params.items():
        netlist = netlist.replace(f"{{{key}}}", str(val))
        
    with open(SIM_FILE, 'w', encoding='utf-8') as f:
        f.write(netlist)
        
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
        
    # El comando original que no mareaba a Wine
    subprocess.run(["wine", LTSPICE_EXE, "-b", "-Run", SIM_FILE], capture_output=True)

def extraer_medicion(parametro_regex):
    if not os.path.exists(LOG_FILE): return 0.0
    
    # Intenta leer asumiendo UTF-16 (LTspice moderno) y si falla, UTF-8
    try:
        with open(LOG_FILE, 'r', encoding='utf-16') as f: log_data = f.read()
    except:
        with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f: log_data = f.read()
        
    match = re.search(parametro_regex, log_data, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return 0.0

def run_ltspice_doble(params):
    resultados = {'Ganancia': 0, 'Zin': 0, 'Zout': 0, 'MES_Real': 0}
    
    # --- CORRIDA 1: Medir Ganancia, Zin y extraer datos DC ---
    params_run1 = params.copy()
    params_run1['AMP_IN'] = "10m"
    params_run1['AMP_OUT'] = "0"
    params_run1['VAL_RL'] = "8" 
    generar_y_correr(params_run1)
    
    resultados['Ganancia'] = extraer_medicion(r"ganancia.*?=\s*([0-9\.eE\+\-]+)")
    resultados['Zin'] = extraer_medicion(r"zin.*?=\s*([0-9\.eE\+\-]+)")
    
    # Extraer tensiones DC
    vc_q3 = extraer_medicion(r"vc_q3.*?=\s*([0-9\.eE\+\-]+)")
    ve_q3 = extraer_medicion(r"ve_q3.*?=\s*([0-9\.eE\+\-]+)")
    vr5 = extraer_medicion(r"vr5.*?=\s*([0-9\.eE\+\-]+)")
    ve_q4 = extraer_medicion(r"ve_q4.*?=\s*([0-9\.eE\+\-]+)")
    
    # --- CÁLCULO MATEMÁTICO DE MES ---
    # 1. Límite de la Etapa 3 (Q3)
    R5, R8, R9, R10 = params['R5'], params['R8'], params['R9'], params['R10']
    
    Icq3 = vr5 / R5 if R5 > 0 else 0
    Vceq3 = vc_q3 - ve_q3
    Rac3 = 1 / (1/R5 + 1/R8 + 1/R9) # Resistencia dinámica vista por Q3
    
    mes_q3_pos = Vceq3 # Límite hacia el corte
    mes_q3_neg = Icq3 * Rac3 # Límite hacia saturación
    mes_q3 = min(mes_q3_pos, mes_q3_neg)
    
    # 2. Límite de la Etapa de Salida (Sziklai en Clase A)
    Ieq4 = ve_q4 / R10 if R10 > 0 else 0
    Rac_out = 1 / (1/R10 + 1/8) # Resistencia AC vista por el emisor
    
    mes_q4_pos = 12.0 - ve_q4 # Límite de subida (techo de la fuente)
    mes_q4_neg = Ieq4 * Rac_out # Límite de bajada (limitado por corriente de R10)
    mes_q4 = min(mes_q4_pos, mes_q4_neg)
    
    # La máxima excursión del amplificador es el peor caso entre las etapas
    resultados['MES_Real'] = min(mes_q3, mes_q4)
    
    # --- CORRIDA 2: Medir Zout (Carga desconectada) ---
    params_run2 = params.copy()
    params_run2['AMP_IN'] = "0"    
    params_run2['AMP_OUT'] = "10m" 
    params_run2['VAL_RL'] = "1Meg" 
    generar_y_correr(params_run2)
    
    resultados['Zout'] = extraer_medicion(r"zout.*?=\s*([0-9\.eE\+\-]+)")
    
    return resultados

def buscar_solucion(beta_npn, beta_pnp, soluciones_deseadas=3, max_intentos=5000):
    mejores_resultados = []
    intentos = 0
    
    print(f"\nBuscando {soluciones_deseadas} configuraciones que cumplan TODOS los requisitos...")
    print(f"Fijando parámetros físicos: NPN Beta={beta_npn} | PNP Beta={beta_pnp}")
    
    while len(mejores_resultados) < soluciones_deseadas and intentos < max_intentos:
        intentos += 1
        
        params = {
            'BETA_NPN': beta_npn,
            'BETA_PNP': beta_pnp,
            'REin': random.choice([47, 56, 68, 100]),
            'R1': random.choice([6.8, 7.5, 8.2, 10]), 
            'R3': random.choice([100000, 120000, 150000, 180000]),
            'R4': random.choice([22000, 27000, 33000, 39000]),
            'R5': random.choice([3300, 4700, 5600, 6800]), 
            'R6': random.choice([10, 22, 47]),       
            'R7': random.choice([1000, 1200, 1500]),
            'R8': random.choice([47000, 68000, 100000]),
            'R9': random.choice([47000, 51000, 68000]),
            'R10': random.choice([10, 22, 47])
        }
        
        res = run_ltspice_doble(params)

        print(f"Intento {intentos} -> G: {res['Ganancia']:.1f} | MES: {res['MES_Real']:.2f}V | Zin: {res['Zin']:.0f} | Zout: {res['Zout']:.2f}")
        
        cond_ganancia = res['Ganancia'] > 75
        cond_mes = res['MES_Real'] > 0.8 
        cond_zin = res['Zin'] > 350000
        cond_zout = 7.6 <= res['Zout'] <= 8.4
        
        if cond_ganancia and cond_mes and cond_zin and cond_zout:
            print(f"\n[{intentos}] ¡SOLUCIÓN ENCONTRADA! ({len(mejores_resultados) + 1}/{soluciones_deseadas})")
            mejores_resultados.append((params, res))
            
    return mejores_resultados

if __name__ == "__main__":
    # Aseguramos estar en el directorio correcto donde están los archivos para que Wine no se pierda
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("\n" + "="*50)
    print(" INGRESO DE DATOS DEL HARDWARE FÍSICO")
    print("="*50)
    
    try:
        val_npn = int(input("Ingresa el Beta (hFE) medido para los NPN (BC547C): "))
        val_pnp = int(input("Ingresa el Beta (hFE) medido para el PNP (BD140): "))
    except ValueError:
        print("\nError: Debes ingresar números enteros. Asignando valores por defecto (NPN: 500, PNP: 100).")
        val_npn = 500
        val_pnp = 100
        
    resultados = buscar_solucion(beta_npn=val_npn, beta_pnp=val_pnp, soluciones_deseadas=3)
    
    print("\n" + "="*50)
    print(f"RESUMEN FINAL: Se encontraron {len(resultados)} configuraciones exitosas")
    print("="*50)
    
    for idx, (params, res) in enumerate(resultados):
        print(f"Opción {idx + 1}:")
        print(f"  Ganancia: {float(res['Ganancia']):.2f}")
        print(f"  MES (Excursión Real): {float(res['MES_Real']):.2f} V pico")
        print(f"  Impedancia Entrada: {float(res['Zin']):.2f} Ohms")
        print(f"  Impedancia Salida: {float(res['Zout']):.2f} Ohms")
        print(f"  Resistencias: {params}")
        
        # Exportar automáticamente la primera opción encontrada para LTspice
        if idx == 0:
            with open("valores_finales.txt", "w") as f:
                linea_params = " ".join([f"{k}={v}" for k, v in params.items()])
                f.write(f".param {linea_params}\n")
            print("  -> Archivo 'valores_finales.txt' generado con éxito para LTspice.")
            
        print("-" * 50)