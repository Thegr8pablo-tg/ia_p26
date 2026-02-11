---
title: "Código del Proyecto Wordle"
---

# Proyecto Wordle — Código

Esqueleto auto-contenido para implementar, comparar y competir con estrategias de Wordle basadas en teoría de la información.

## Estructura

```
code/
├── wordle_env.py       # Entorno del juego (feedback, filtrado, cualquier longitud)
├── lexicon.py          # Carga de listas de palabras
├── strategy.py         # Clase base abstracta para estrategias
├── strategies/         # Implementaciones de estrategias
│   ├── __init__.py     # Auto-descubrimiento de estrategias
│   ├── random_strat.py # Estrategia aleatoria (baseline)
│   └── max_prob_strat.py # Siempre adivinar la primera candidata
├── tournament.py       # Torneo: correr todas las estrategias y comparar
├── experiment.py       # Experimento: analizar una estrategia en detalle
├── data/
│   └── mini_spanish_5.txt  # Lista mínima de palabras (fallback)
└── results/            # Salida (CSVs, gráficas)
```

## Setup rápido

```bash
pip install -r requirements.txt
```

## Uso

### Torneo (todas las estrategias)

```bash
python tournament.py                                # léxico mini, todas las estrategias
python tournament.py --words data/lista_grande.txt  # léxico personalizado
python tournament.py --length 6 --max-guesses 8     # palabras de 6 letras
python tournament.py --allow-non-words               # permitir "sondas" no-palabra
```

### Experimento (una estrategia)

```bash
python experiment.py --strategy random --num-games 20 --verbose
python experiment.py --strategy maxprob --num-games 50 --verbose
```

### Docker

```bash
docker compose up tournament
docker compose up experiment
```

## Cómo agregar tu estrategia

1. Crea un archivo en `strategies/`, por ejemplo `strategies/mi_estrategia.py`.
2. Implementa una clase que herede de `Strategy`:

```python
from strategy import Strategy
from wordle_env import filter_candidates

class MiEstrategia(Strategy):
    @property
    def name(self) -> str:
        return "MiEstrategia"

    def begin_game(self, word_length: int, vocabulary: list[str]) -> None:
        self._candidates = list(vocabulary)

    def guess(self, history: list[tuple[str, tuple[int, ...]]]) -> str:
        candidates = self._candidates
        for g, pat in history:
            candidates = filter_candidates(candidates, g, pat)
        # Tu lógica aquí
        return candidates[0]
```

3. Corre el torneo — tu estrategia se descubre automáticamente:

```bash
python tournament.py
```

## Utilidades disponibles

- `wordle_env.feedback(secret, guess)` — calcula el patrón de feedback (tupla de 0/1/2)
- `wordle_env.filter_candidates(candidates, guess, pattern)` — filtra candidatos consistentes
- `WordleEnv` — entorno completo del juego con estado, historial, y validación

## Notas

- El código es **auto-contenido**: no importa nada de `it_code/` ni `datasets/`.
- Soporta **cualquier longitud de palabra** (no solo 5).
- `allow_non_words=True` permite adivinar secuencias de letras que no son palabras reales (para explorar la pregunta abierta de "sondas de información pura").
