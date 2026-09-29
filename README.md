# Laboratorio 2: Amplificador BJT Multietapa con Espejo de Corriente NMOS

Repositorio del **Laboratorio 2** para la asignatura de Electrónica. El objetivo de este proyecto es diseñar, simular, implementar en PCB y caracterizar experimentalmente un amplificador en cascada basado en transistores BJT, junto con una red de polarización/generador de corriente por espejo NMOS con degeneración de fuente.

---

## 👥 Integrantes (Grupo N°)
- **[Nombre y Apellido 1]** - *[Legajo / Correo]*
- **[Nombre y Apellido 2]** - *[Legajo / Correo]*
- **[Nombre y Apellido 3]** - *[Legajo / Correo]*

---

## 🎯 Especificaciones de Diseño

| Parámetro | Valor Requerido |
| :--- | :--- |
| **Ganancia de Tensión de Transf. ($G_T$)** | $> 75$ |
| **Impedancia de Entrada ($Z_{in}$)** | $> 350\text{ k}\Omega$ |
| **Impedancia de Salida ($Z_o$)** | $8\Omega \pm 5\%$ |
| **Polarización** | Espejo de corriente NMOS con degeneración de fuente |
| **Excursión** | Máxima excursión simétrica prioritarias en el diseño |

---

## 🛠️ Estructura del Repositorio

```text
.
├── docs/                   # Guías, hojas de datos (datasheets) e informe final
│   └── Informe_Laboratorio_2.pdf
├── design/                 # Cálculos teóricos, hojas de cálculo o notebooks
├── simulation/             # Archivos de simulación (SPICE / LTspice / Altium)
│   ├── bias_point/         # Análisis del punto de operación (OP)
│   ├── ac_analysis/        # Respuestas en frecuencia (AC)
│   └── transient/          # Análisis temporal, ruido y THD (TRAN / NOISE / FFT)
├── pcb/                    # Archivos de diseño de circuito impreso (KiCad / Altium)
│   ├── schematics/
│   ├── layout/
│   └── gerbers/
└── README.md
