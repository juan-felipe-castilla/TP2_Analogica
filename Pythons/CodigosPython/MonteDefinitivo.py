import os
import subprocess
import re
import random

LTSPICE_EXE = os.path.expanduser("~/.wine/drive_c/Program Files/ADI/LTspice/LTspice.exe")
TEMPLATE_FILE = "template.net"
SIM_FILE = "simulacion.net"
LOG_FILE = "simulacion.log"

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
    
    # Cálculo MES adaptado
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

def test_montecarlo_rapido(params_nominales, corridas=30, tolerancia=0.05):
    """Somete una configuración ganadora a una prueba de fuego de tolerancias"""
    exitos = 0
    peor_mes = 999.0
    margen = tolerancia
    
    for _ in range(corridas):
        params_test = {}
        for r_name, r_val in params_nominales.items():
            variacion = random.uniform(1.0 - margen, 1.0 + margen)
            params_test[r_name] = r_val * variacion
            
        res = run_ltspice_doble(params_test)
        
        cond_ganancia = res['Ganancia'] > 75
        cond_mes = res['MES_Real'] > 0.8
        cond_zin = res['Zin'] > 350000
        cond_zout = 7.0 < res['Zout'] < 8.4
        
        if cond_ganancia and cond_mes and cond_zin and cond_zout:
            exitos += 1
            peor_mes = min(peor_mes, res['MES_Real'])
            
    yield_pct = (exitos / corridas) * 100
    return yield_pct, peor_mes

def optimizador_maestro(soluciones_robustas_deseadas=3, max_intentos=2000):
    candidatos_robustos = []
    intentos = 0
    
    print(f"\nIniciando Optimizador. Buscando {soluciones_robustas_deseadas} diseños de grado comercial...")
    
    while len(candidatos_robustos) < soluciones_robustas_deseadas and intentos < max_intentos:
        intentos += 1
        
        # Generamos valores aleatorios basados en tus ajustes anteriores
        params = {
            'RBD': 1000000, # Fijo por consigna
            'RED': random.choice([47, 68, 100]),
            'R1E': random.choice([120000, 150000, 180000]),
            'R2E': random.choice([22000, 27000, 33000, 39000]),
            'RCE': random.choice([6800, 8200, 10000]),
            'REE': random.choice([1000, 1200]),
            'R2S': random.choice([68000, 82000, 100000]),
            'R1S': random.choice([47000, 51000, 68000]),
            'RES': random.choice([10, 22, 47]),
            'RO': random.choice([6.8, 7.5, 8.2])
        }
        
        res = run_ltspice_doble(params)
        
        # Verificamos si pasa la prueba nominal
        if res['Ganancia'] > 75 and res['MES_Real'] > 0.8 and res['Zin'] > 350000 and 7.0 < res['Zout'] < 8.5:
            print(f"\n[Intento {intentos}] -> ¡Circuito Prometedor! G: {res['Ganancia']:.1f} | MES: {res['MES_Real']:.2f}V")
            print("Sometiendo a prueba de tolerancias Monte Carlo (30 iteraciones)...")
            
            yield_pct, peor_mes = test_montecarlo_rapido(params)
            
            if yield_pct >= 85.0: # Exigimos al menos 85% de supervivencia a las tolerancias
                print(f"-> APROBADO: Supervivencia del {yield_pct:.1f}%. Peor MES: {peor_mes:.2f}V")
                candidatos_robustos.append({
                    'params': params,
                    'nominal': res,
                    'yield': yield_pct,
                    'worst_mes': peor_mes if peor_mes != 999.0 else res['MES_Real']
                })
            else:
                print(f"-> DESCARTADO: Diseño inestable (Supervivencia {yield_pct:.1f}%). Colapsa en producción.")
        
        if intentos % 50 == 0:
            print(f"... {intentos} combinaciones evaluadas ...")

    return candidatos_robustos

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    resultados = optimizador_maestro(soluciones_robustas_deseadas=3)
    
    if not resultados:
        print("\nNo se encontraron soluciones robustas. Considera relajar los requisitos o ampliar los valores de resistencias.")
    else:
        # AQUÍ ESTÁ LA MAGIA: Ordenamos la lista priorizando el Peor MES (De mayor a menor)
        resultados_ordenados = sorted(resultados, key=lambda x: x['worst_mes'], reverse=True)
        
        print("\n" + "="*60)
        print(" TOP 3 MEJORES DISEÑOS ROBUSTOS (PRIORIZANDO MES)")
        print("="*60)
        
        for idx, diseño in enumerate(resultados_ordenados):
            p = diseño['params']
            nom = diseño['nominal']
            print(f"🥇 OPCIÓN {idx + 1} (La más robusta)" if idx == 0 else f"OPCIÓN {idx + 1}:")
            print(f"  Rendimiento Fabricación (Yield): {diseño['yield']:.1f}%")
            print(f"  Peor MES ante tolerancias:       {diseño['worst_mes']:.2f} V pico")
            print(f"  Ganancia Nominal:                {nom['Ganancia']:.1f}")
            print(f"  Impedancia Entrada Nominal:      {nom['Zin']:.0f} Ohms")
            print(f"  Impedancia Salida Nominal:       {nom['Zout']:.2f} Ohms")
            print(f"  Resistencias: {p}")
            
            if idx == 0:
                with open("valores_finales.txt", "w") as f:
                    linea_params = " ".join([f"{k}={v}" for k, v in p.items()])
                    f.write(f".param {linea_params}\n")
                print("  -> Guardado como 'valores_finales.txt' para llevar a LTspice.")
            print("-" * 60)