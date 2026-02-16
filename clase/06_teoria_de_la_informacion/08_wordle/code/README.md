---
title: "Código del Proyecto Wordle"
---

# Proyecto Wordle — Código

Esqueleto auto-contenido para implementar, comparar y competir con estrategias de Wordle basadas en teoría de la información.

## Estructura

```
code/
├── wordle_env.py       # Entorno del juego (feedback, filtrado, cualquier longitud)
├── lexicon.py          # Carga de palabras + dos modos de probabilidad
├── strategy.py         # Clase base abstracta para estrategias
├── download_words.py   # Descarga lista grande desde OpenSLR (~5000+ palabras)
├── strategies/         # Estrategias built-in (baselines)
│   ├── __init__.py     # Auto-descubrimiento (built-in + estudiantes)
│   ├── random_strat.py # Baseline: aleatorio
│   └── max_prob_strat.py # Baseline: primera candidata alfabética
├── tournament.py       # Torneo: todas las estrategias en paralelo
├── experiment.py       # Experimento: una estrategia en detalle
├── data/
│   └── mini_spanish_5.txt  # Lista mínima (~44 palabras, fallback offline)
└── results/            # Salida (CSVs, gráficas)
```

---

## Setup

### 1. Instalar dependencias

```bash
cd clase/06_teoria_de_la_informacion/wordle/code
pip install -r requirements.txt
```

### 2. Descargar lista grande de palabras (recomendado)

```bash
python3 download_words.py
```

Esto descarga el corpus OpenSLR SLR21 (español) y genera:
- `data/spanish_5letter.csv` — ~5000 palabras con frecuencias
- `data/spanish_5letter.txt` — mismas palabras, una por línea

Sin este paso, el torneo usa `data/mini_spanish_5.txt` (44 palabras).

---

## Dos modos de probabilidad

El torneo soporta dos modos que cambian cómo se elige la palabra secreta y cómo se evalúa el rendimiento:

| Modo | Descripción | Cuándo usarlo |
|------|-------------|---------------|
| `uniform` | Todas las palabras tienen la misma probabilidad | Evaluar la lógica de información pura |
| `frequency` | Probabilidad ponderada por frecuencia (sigmoide) | Simular un Wordle realista con palabras comunes |

```bash
python3 tournament.py --mode uniform     # default
python3 tournament.py --mode frequency   # ponderado
python3 tournament.py --mode both        # corre ambos y compara
```

---

## Correr el torneo

```bash
# Mini léxico, uniforme (rápido, para probar)
python3 tournament.py

# Lista grande, ambos modos
python3 tournament.py --mode both

# Subsample de 200 palabras para iterar rápido
python3 tournament.py --num-games 200

# Palabras de 6 letras (necesita download_words.py --length 6)
python3 tournament.py --length 6 --max-guesses 8
```

El torneo corre cada estrategia **en paralelo** (un proceso por estrategia) y genera:
- Tabla de resultados ordenada por rendimiento
- CSV en `results/`
- Histograma de distribución de intentos

### Experimentar con una estrategia

```bash
python3 experiment.py --strategy random --num-games 20 --verbose
python3 experiment.py --strategy maxprob --num-games 50 --mode frequency --verbose
```

---

## Cómo subir tu estrategia (estudiantes)

### Ubicación

Tu estrategia va en tu carpeta de estudiante, **no** en `code/strategies/`:

```
estudiantes/<tu-usuario>/wordle/<nombre>.py
```

Por ejemplo:
```
estudiantes/gabonavarroo/wordle/mi_entropia.py
estudiantes/KarolCisneros/wordle/entropy_strat.py
```

### Qué debe contener tu archivo

Un archivo `.py` con una clase que herede de `Strategy`:

```python
import sys
from pathlib import Path

# Hacer importable el código del proyecto
_CODE_DIR = str(Path(__file__).resolve().parents[3]
                / "clase" / "06_teoria_de_la_informacion" / "wordle" / "code")
if _CODE_DIR not in sys.path:
    sys.path.insert(0, _CODE_DIR)

from strategy import Strategy
from wordle_env import feedback, filter_candidates


class MiEstrategia(Strategy):
    @property
    def name(self) -> str:
        # Usa un nombre ÚNICO (incluye tu usuario para evitar colisiones)
        return "Entropy_gabonavarroo"

    def begin_game(self, word_length: int, vocabulary: list[str]) -> None:
        self._vocab = list(vocabulary)

    def guess(self, history: list[tuple[str, tuple[int, ...]]]) -> str:
        candidates = self._vocab
        for g, pat in history:
            candidates = filter_candidates(candidates, g, pat)
        # --- Tu lógica aquí ---
        return candidates[0]
```

### Reglas

1. **Un archivo, una clase.** Puedes tener varios archivos (varias estrategias).
2. **Nombre único.** Incluye tu usuario en `name` para evitar colisiones en el torneo.
3. **Sin dependencias extra.** Solo `numpy` y la librería estándar. No instales paquetes adicionales.
4. **Auto-contenido.** Tu archivo debe importar solo de `strategy`, `wordle_env`, y `lexicon`. No importes de `it_code/` ni de otros estudiantes.
5. **No hagas trampa.** Tu estrategia NO debe acceder al secreto directamente (solo al historial de feedback).

### Verificar que funciona

Desde `code/`:

```bash
# Debe detectar tu estrategia automáticamente
python3 tournament.py --num-games 10

# O probar solo la tuya
python3 experiment.py --strategy "Entropy_gabonavarroo" --num-games 10 --verbose
```

### Workflow de Git

```bash
# Desde la raíz del repo
./clase/flow.sh start wordle-mi-estrategia
# ... crea tu archivo en estudiantes/<tu-usuario>/wordle/
./clase/flow.sh save "add my wordle strategy"
./clase/flow.sh upload
# Abre PR al upstream
```

---

## Utilidades disponibles para tu estrategia

```python
from wordle_env import feedback, filter_candidates

# Calcular feedback (simulación)
pat = feedback("canto", "arcos")  # -> (1, 0, 1, 1, 0)

# Filtrar candidatos consistentes con un guess+feedback
remaining = filter_candidates(candidates, "arcos", (1, 0, 1, 1, 0))
```

```python
from lexicon import load_lexicon

# Cargar léxico con probabilidades (para estrategias que usan frecuencia)
lex = load_lexicon(mode="frequency")
# lex.words -> lista de palabras
# lex.probs -> dict {palabra: probabilidad}
```

---

## Docker

```bash
docker compose up tournament
docker compose up experiment
```
