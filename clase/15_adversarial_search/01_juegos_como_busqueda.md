---
title: "Juegos como búsqueda"
---

| Notebook | Colab |
|---------|:-----:|
| Notebook 01 — Juegos y árboles | <a href="COLAB_URL" target="_blank"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"></a> |

---

# Juegos como búsqueda

> *"Games are the most civilized form of warfare."*

---

La búsqueda de los módulos 13 y 14 asume un entorno inerte: el problema no cambia mientras buscas. En un juego, el entorno **te responde**. Un oponente toma decisiones activamente para frustrar las tuyas. Esta diferencia cambia todo: ya no buscas un *camino*, buscas una *estrategia* — una función que indica qué acción tomar en cada estado posible, sin importar cómo llegaste ahí.

---

## 1. Intuición: del camino a la estrategia

**¿Qué cambia?** Un agente de búsqueda controla cada acción del estado inicial al final. En un juego de dos jugadores, el agente controla la mitad de las acciones — la otra mitad las decide el oponente. No puedes planear el camino completo de antemano porque no controlas los movimientos del adversario.

| | Búsqueda (módulos 13–14) | Juego (módulo 15) |
|---|---|---|
| ¿Quién decide? | Un agente | Dos agentes con objetivos opuestos |
| ¿Cambia el entorno? | No | Sí — el oponente responde |
| ¿Qué buscamos? | Un **camino** óptimo | Una **estrategia**: acción óptima en cada estado posible |
| Resultado del éxito | Llegar a la meta | Ganar (o garantizar el mejor resultado posible) |
| Algoritmo base | `busqueda_generica` con frontera | Minimax: DFS con propagación de valores |

![Búsqueda vs juego]({{ '/15_adversarial_search/images/01_single_vs_adversarial.png' | url }})

---

## 2. Los 7 componentes formales

Todo juego de dos jugadores se puede describir con 7 elementos. La siguiente tabla los mapea contra los conceptos que ya conocemos:

| Componente del juego | Descripción | Análogo en búsqueda |
|---|---|---|
| $s_0$ — Estado inicial | Configuración al inicio del juego (tablero vacío, pilas de fichas) | `problema.inicio` |
| $S$ — Espacio de estados | Todos los tableros/configuraciones posibles | Nodos del grafo |
| $\text{Jugadores}(s)$ | ¿De quién es el turno en el estado $s$? (MAX o MIN) | — (nuevo) |
| $\text{Acciones}(s)$ | Movimientos legales desde $s$ | `problema.acciones(n)` |
| $\text{Resultado}(s, a)$ | Estado que resulta de aplicar acción $a$ en $s$ | `problema.resultado(n,a)` |
| $\text{Terminal}(s)$ | ¿Terminó el juego? (victoria, derrota, empate) | `problema.es_meta(n)` |
| $U(s, p)$ | Utilidad del jugador $p$ en estado terminal $s$ | `problema.costo(a)` (análogo) |

Los primeros cinco componentes son los mismos que en búsqueda — solo se añaden $\text{Jugadores}$ y $U$. Esta simetría no es coincidencia: minimax hereda toda la maquinaria de DFS y solo añade la lógica de alternancia y propagación de valores.

```python
# Interfaz de búsqueda (módulos 13-14)
class Problema:
    def inicio(self): ...
    def acciones(self, n): ...
    def resultado(self, n, a): ...
    def es_meta(self, n): ...
    def costo(self, a): ...

# Interfaz de juego (módulo 15)
class Juego:
    def estado_inicial(self): ...
    def jugador(self, s): ...      # nuevo: ¿de quién es el turno?
    def acciones(self, s): ...
    def resultado(self, s, a): ...
    def terminal(self, s): ...
    def utilidad(self, s, p): ...  # nuevo: considera quién gana
```

---

## 3. El árbol de juego

Un **árbol de juego** es el árbol de búsqueda donde los niveles alternan entre los dos jugadores. Los nodos MAX representan turnos donde el jugador que maximiza elige la acción; los nodos MIN representan turnos donde el oponente (que minimiza) elige.

Propiedades clave:
- **Factor de ramificación** $b$: número de movimientos legales en un estado típico.
- **Profundidad** $m$: longitud de la partida (número total de acciones hasta el estado terminal).
- **Nodos terminales**: hojas del árbol con valor de utilidad asignado.

![Un agente vs árbol de juego]({{ '/15_adversarial_search/images/01_single_vs_adversarial.png' | url }})

En profundidad 0 tenemos el turno de MAX; en profundidad 1 el turno de MIN; en profundidad 2 el turno de MAX otra vez, y así sucesivamente. Los nodos terminales son hojas con valores de utilidad conocidos: el juego terminó y sabemos quién ganó.

**Utilidad vs función de evaluación** — una distinción que volverá en la sección 15.5:
- $U(s)$: valor **exacto** en estados terminales. Lo conocemos con certeza — el juego terminó.
- $eval(s)$: estimación del valor en estados **no terminales**. Necesaria cuando el árbol es demasiado grande para llegar a las hojas.

Esta distinción es la misma que entre costo real $g(n)$ y heurística $h(n)$ en el módulo 14 — excepto que aquí estimamos el valor del juego, no el costo restante del camino.

---

## 4. Ejemplo: tic-tac-toe

Mapeamos los 7 componentes explícitamente:

- **Estado inicial** $s_0$: tablero 3×3 vacío, representado como lista de 9 posiciones (`['', '', '', '', '', '', '', '', '']`).
- **Jugadores**: X es MAX (quiere maximizar), O es MIN (quiere minimizar). $\text{Jugadores}(s)$ = MAX si hay número par de fichas en el tablero, MIN si hay número impar.
- **Acciones**: celdas vacías. Si el tablero tiene $k$ fichas, hay $9-k$ acciones disponibles.
- **Resultado**: colocar X u O en la celda elegida según de quién sea el turno.
- **Terminal**: tres en raya para algún jugador, o tablero lleno (empate).
- **Utilidad**: $U(s, \text{MAX}) = +1$ si X gana, $-1$ si O gana, $0$ si empate.

![Anatomía de tic-tac-toe]({{ '/15_adversarial_search/images/02_tictactoe_anatomy.png' | url }})

Factor de ramificación: empieza en $b=9$, decrece a medida que se llenan celdas. Profundidad máxima: $m=9$. Nodos terminales: $\leq 9! = 362{,}880$ (con poda por victorias anticipadas, en la práctica muchos menos).

```python
class TicTacToe:
    """Tic-tac-toe con los 7 componentes formales."""

    def estado_inicial(self):
        return tuple([''] * 9)   # tablero vacío, 9 posiciones

    def jugador(self, s):
        # X juega primero (turno par de fichas = MAX)
        fichas = sum(1 for c in s if c != '')
        return 'MAX' if fichas % 2 == 0 else 'MIN'

    def acciones(self, s):
        return [i for i, c in enumerate(s) if c == '']

    def resultado(self, s, a):
        ficha = 'X' if self.jugador(s) == 'MAX' else 'O'
        nuevo = list(s)
        nuevo[a] = ficha
        return tuple(nuevo)

    def terminal(self, s):
        return self._ganador(s) is not None or '' not in s

    def utilidad(self, s, p='MAX'):
        gan = self._ganador(s)
        if gan == 'X': return +1
        if gan == 'O': return -1
        return 0

    def _ganador(self, s):
        lineas = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
        for a, b, c in lineas:
            if s[a] == s[b] == s[c] != '':
                return s[a]
        return None
```

---

## 5. Ejemplo: Nim

Nim es el juego de ejemplo principal de este módulo porque su árbol cabe completamente en una figura, lo cual nos permite trazar minimax paso a paso.

**Reglas de Nim**: hay $k$ pilas de fichas con tamaños dados. Dos jugadores alternan turnos. En tu turno: **retira al menos 1 ficha de exactamente una pila**. El jugador que retire la última ficha **gana**.

```
Estado inicial: Nim(1,2) — pila A tiene 1 ficha, pila B tiene 2 fichas.

Turno 1 (MAX): Retira 1 de B → estado (1,1)
Turno 2 (MIN): Retira 1 de A → estado (0,1)
Turno 3 (MAX): Retira 1 de B → estado (0,0)
Turno 4 (MIN): No hay fichas. MIN no puede mover. MAX GANA.
```

Mapeamos los 7 componentes para Nim de $k$ pilas:

- **Estado inicial**: tupla de enteros, e.g. `(1, 2)` para dos pilas de tamaño 1 y 2.
- **Jugadores**: alterna MAX/MIN en cada turno; se controla con un parámetro booleano en la recursión.
- **Acciones**: `(pile_idx, amount)` — pila a modificar y cuántas fichas retirar. Desde estado $(a, b)$: acciones = $\{(0,1), \ldots, (0,a)\} \cup \{(1,1), \ldots, (1,b)\}$.
- **Resultado**: nuevo estado con la pila reducida en `amount`.
- **Terminal**: $(0, 0, \ldots, 0)$ — todas las pilas vacías.
- **Utilidad**: el jugador que **llega** a $(0,\ldots,0)$ habiendo tomado la última ficha **gana** (+1). El jugador cuyo turno es cuando el estado ya es terminal **pierde** (−1). Convención: utilidad desde la perspectiva de quien ACABA de mover al estado terminal.

![Reglas y árbol de Nim]({{ '/15_adversarial_search/images/03_nim_rules_and_tree.png' | url }})

```python
class Nim:
    """Juego de Nim para k pilas."""

    def estado_inicial(self, pilas):
        return tuple(pilas)

    def jugador(self, s, turno_max=True):
        # El turno se pasa como parámetro externo en la recursión
        return 'MAX' if turno_max else 'MIN'

    def acciones(self, s):
        acciones = []
        for i, pila in enumerate(s):
            for cant in range(1, pila + 1):
                acciones.append((i, cant))
        return acciones

    def resultado(self, s, a):
        pile_idx, amount = a
        nuevo = list(s)
        nuevo[pile_idx] -= amount
        return tuple(nuevo)

    def terminal(self, s):
        return all(p == 0 for p in s)

    def utilidad(self, s, es_max_turno):
        # Quien llega al estado terminal (todas pilas vacías) acaba de tomar la última ficha → gana
        # El jugador cuyo TURNO ES en el estado terminal no puede mover → pierde
        # Si es_max_turno es True, es el turno de MAX en el estado terminal → MAX pierde → valor = -1
        # Si es_max_turno es False, es el turno de MIN en el estado terminal → MIN pierde → valor = +1
        return -1 if es_max_turno else +1
```

**¿Por qué Nim es útil para aprender?** El árbol de juego de Nim(1,2) tiene exactamente **12 nodos** — cabe completamente en una figura y podemos trazar minimax paso a paso sin perder el hilo. Veremos también que Nim esconde una propiedad matemática profunda que minimax *descubrirá* en la sección 15.5: el nim-sum XOR.

---

## 6. ¿Y el ajedrez?

Los mismos 7 componentes aplican, pero los números hacen que minimax exacto sea inviable:

| Parámetro | Valor |
|---|---|
| Factor de ramificación $b$ | $\approx 35$ movimientos legales por posición |
| Profundidad $m$ | $\approx 80$ semi-movimientos en una partida típica |
| Partidas posibles | $\approx 10^{123}$ (número de Shannon) |
| Posiciones únicas | $\approx 10^{43}$ |

Incluso a 1 billón de nodos por segundo, explorar $10^{123}$ nodos tomaría más tiempo que la edad del universo ($\approx 4 \times 10^{17}$ segundos). La sección 15.5 muestra cómo resolver esto con límite de profundidad y funciones de evaluación.

---

**Siguiente:** [Tipos de juegos →](02_tipos_de_juegos.md)
