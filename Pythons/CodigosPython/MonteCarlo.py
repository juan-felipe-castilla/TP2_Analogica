import os
import subprocess
import re
import random

LTSPICE_EXE = os.path.expanduser("~/.wine/drive_c/Program Files/ADI/LTspice/LTspice.exe")
TEMPLATE_FILE = "template_100.net"
SIM_FILE = "simulacion_mc.net"
LOG_FILE = "simulacion_mc.log"

def generar_y_correr(params):
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        netlist = f.read()
    for key, val in params.items():
        netlist = netlist.replace(f"{{{key}}}", str(val))
    with open(SIM_FILE, 'w', encoding='utf-8') as f:
        f.write(netlist)
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    subprocess.run(["wine", LTSPICE_EXE, "-b", "-Run", SIM_FILE], capture_output=True)

def extraer_medicion(parametro_regex):
    if not os.path.exists(LOG_FILE): return 0.0
    try:
        with open(LOG_FILE, 'r', encoding='utf-16') as f: log_data = f.read()
    except:
        with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f: log_data = f.read()
    match = re.search(parametro_regex, log_data, re.IGNORECASE)
    if match: return float(match.group(1))
    return 0.0

def run_ltspice_doble(params):
    resultados = {'Ganancia': 0, 'Zin': 0, 'Zout': 0, 'MES_Real': 0}
    
    # CORRIDA 1: Ganancia y DC (10mV in)
    params_run1 = params.copy()
    params_run1['AMP_IN'] = "10m"
    params_run1['AMP_OUT'] = "0"
    params_run1['VAL_RL'] = "8" 
    generar_y_correr(params_run1)
    
    resultados['Ganancia'] = extraer_medicion(r"ganancia.*?=\s*([0-9\.eE\+\-]+)")
    resultados['Zin'] = extraer_medicion(r"zin.*?=\s*([0-9\.eE\+\-]+)")
    
    vc_q3 = extraer_medicion(r"vc_q3.*?=\s*([0-9\.eE\+\-]+)")
    ve_q3 = extraer_medicion(r"ve_q3.*?=\s*([0-9\.eE\+\-]+)")
    vrce = extraer_medicion(r"vrce.*?=\s*([0-9\.eE\+\-]+)")
    ve_q4 = extraer_medicion(r"ve_q4.*?=\s*([0-9\.eE\+\-]+)")
    
    # Cálculo MES adaptado a los nodos
    RCE, R1S, R2S, RES = params['RCE'], params['R1S'], params['R2S'], params['RES']
    
    Icq3 = vrce / RCE if RCE > 0 else 0
    Vceq3 = vc_q3 - ve_q3
    Rac3 = 1 / (1/RCE + 1/R1S + 1/R2S)
    mes_q3 = min(Vceq3, Icq3 * Rac3)
    
    Ieq4 = ve_q4 / RES if RES > 0 else 0
    Rac_out = 1 / (1/RES + 1/8)
    mes_q4 = min(12.0 - ve_q4, Ieq4 * Rac_out)
    
    resultados['MES_Real'] = min(mes_q3, mes_q4)
    
    # CORRIDA 2: Zout
    params_run2 = params.copy()
    params_run2['AMP_IN'] = "0"    
    params_run2['AMP_OUT'] = "10m" 
    params_run2['VAL_RL'] = "1Meg" 
    generar_y_correr(params_run2)
    
    resultados['Zout'] = extraer_medicion(r"zout.*?=\s*([0-9\.eE\+\-]+)")
    return resultados

def analisis_montecarlo_final(tolerancia_porcentaje=5, corridas=100):
    # Valores extraídos exactamente de tu netlist elegida
    nominales = {
        'RBD': 1000000,
        'RED': 47,
        'R1E': 180000,
        'R2E': 27000,
        'RCE': 6800,
        'REE': 1200,
        'R2S': 100000,
        'R1S': 47000,
        'RES': 10,
        'RO': 7.5
    }
    
    exitos = 0
    fallos_ganancia = 0
    fallos_mes = 0
    fallos_zin = 0
    fallos_zout = 0
    
    margen = tolerancia_porcentaje / 100.0
    
    print(f"\nIniciando Análisis de Tolerancias al {tolerancia_porcentaje}% con {corridas} corridas...")
    
    for i in range(corridas):
        params_test = {}
        for r_name, r_val in nominales.items():
            variacion = random.uniform(1.0 - margen, 1.0 + margen)
            params_test[r_name] = r_val * variacion
            
        res = run_ltspice_doble(params_test)
        
        # Filtros exigidos por tu cátedra
        cond_ganancia = res['Ganancia'] > 75
        cond_mes = res['MES_Real'] > 0.8
        cond_zin = res['Zin'] > 350000
        cond_zout = 7.0 < res['Zout'] < 8.5
        
        if cond_ganancia and cond_mes and cond_zin and cond_zout:
            exitos += 1
        else:
            if not cond_ganancia: fallos_ganancia += 1
            if not cond_mes: fallos_mes += 1
            if not cond_zin: fallos_zin += 1
            if not cond_zout: fallos_zout += 1
            
        print(f"[{i+1:03d}/100] G: {res['Ganancia']:05.1f} | Zin: {res['Zin']:06.0f} | MES: {res['MES_Real']:.2f}V | Zout: {res['Zout']:.2f}")

    rendimiento = (exitos / corridas) * 100
    
    print("\n" + "="*50)
    print(" REPORTE DE PRODUCCIÓN - CONFIGURACIÓN ELEGIDA")
    print("="*50)
    print(f"Tasa de éxito (Yield): {rendimiento:.1f}% ({exitos} de {corridas} sobrevivieron)")
    print("\nDesglose de los que fallaron:")
    print(f"- Ganancia (< 75)       : {fallos_ganancia}")
    print(f"- MES (< 0.8V)          : {fallos_mes}")
    print(f"- Zin (< 350k)          : {fallos_zin}")
    print(f"- Zout (Fuera de rango) : {fallos_zout}")
    print("="*50)
    
    if rendimiento >= 85.0:
        print("DISEÑO ROBUSTO: Listo para armar en hardware físico.")
    else:
        print("ADVERTENCIA: Alto riesgo por tolerancias físicas. Revisa los fallos.")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    analisis_montecarlo_final(tolerancia_porcentaje=5, corridas=100)