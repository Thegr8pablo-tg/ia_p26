---
title: "Proyecto Wordle: Teoría de la Información en Acción"
---

# Proyecto Wordle: Teoría de la Información en Acción

:::project{id="PROJ-WORDLE" title="Proyecto Wordle" due="TBD" points="TBD"}
Diseña, implementa y compara estrategias de Wordle usando herramientas de teoría de la información (entropía, ganancia de información, score esperado). Trabaja con el [código esqueleto](code/README.md) y participa en el torneo del curso.
:::

## Contenido

| Sección | Tema | Idea clave |
|:------:|------|-----------|
| W.1 | [El juego de Wordle](01_el_juego.md) | Reglas, feedback y estructura de información |
| W.2 | [Estrategia aleatoria](02_estrategia_aleatoria.md) | Baseline: adivinar al azar |
| W.3 | [Máxima probabilidad](03_maxima_probabilidad.md) | Greedy: siempre la más probable |
| W.4 | [Entropía ingenua](04_entropia_ingenua.md) | Maximizar bits esperados (3B1B S1) |
| W.5 | [Entropía ponderada](05_entropia_ponderada.md) | Incorporar frecuencia con sigmoide (3B1B S2) |
| W.6 | [Score esperado](06_score_esperado.md) | Minimizar intentos totales (3B1B S3) |
| W.7 | [Look-ahead](07_look_ahead.md) | Mirar dos pasos al futuro (3B1B S4) |
| W.8 | [Preguntas abiertas](08_preguntas_abiertas.md) | Direcciones creativas y extensiones |

## Código esqueleto

El directorio [`code/`](code/README.md) contiene un esqueleto auto-contenido con:

- Entorno de juego (`WordleEnv`) que soporta cualquier longitud de palabra
- Clase base `Strategy` para implementar estrategias
- Torneo automático que descubre y compara todas las estrategias
- Dos estrategias de ejemplo (aleatoria y máxima probabilidad)

```bash
cd code
pip install -r requirements.txt
python tournament.py
```

## Referencia

- [3Blue1Brown: Solving Wordle using information theory](https://www.3blue1brown.com/lessons/wordle) — el video que inspira la progresión de estrategias de este proyecto.

---

**Volver:** [← Índice del módulo](../00_index.md)
