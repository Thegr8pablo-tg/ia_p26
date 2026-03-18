---
title: "Minimax"
---

| Notebook | Colab |
|---------|:-----:|
| Notebook 02 — Minimax y alpha-beta | <a href="COLAB_URL" target="_blank"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"></a> |

---

# Minimax: el peor caso garantizado

> *"The essence of strategy: make sure you win even if the other player is perfect."*

---

Minimax es DFS con propagación de valores hacia atrás. Al igual que DFS explora ramas en profundidad antes de retroceder, minimax desciende hasta las hojas del árbol de juego y, al subir, propaga el mejor valor que cada jugador puede garantizarse. La estructura es idéntica — la diferencia está en qué hace cada llamada recursiva al retroceder.

---

## 1. Intuición

**Pregunta central de minimax**: *"Si mi oponente juega perfectamente contra mí, ¿cuál es la mejor decisión que puedo tomar?"*

No buscamos el mejor resultado *posible* — eso sería optimismo ingenuo. Buscamos el mejor resultado *garantizado*, asumiendo que el oponente es exactamente tan bueno como nosotros. Esta es la diferencia entre "espero que el oponente se equivoque" y "gano aunque el oponente no se equivoque".

La estrategia que minimax descubre se llama **estrategia minimax** u **óptima**: ningún agente racional puede hacer mejor contra un oponente que también juega óptimamente.

---

## 2. La conexión con DFS

Minimax usa DFS como motor de exploración. La estructura es idéntica — la diferencia está en qué hace cada llamada recursiva al retroceder:

| | DFS (módulo 13) | Minimax |
|---|---|---|
| Estructura | Recursión / pila | Recursión |
| Orden de visita | Profundidad primero | Profundidad primero |
| Complejidad tiempo | $O(b^m)$ | $O(b^m)$ |
| Complejidad espacio | $O(b \cdot m)$ | $O(b \cdot m)$ |
| Al visitar un nodo | Marca como explorado | Determina si es MAX o MIN |
| Al retroceder | Nada (solo desapila) | **Retorna un valor** (max o min de los hijos) |
| Se detiene | Al llegar al destino | Al llegar a estados terminales |

> DFS *visita* y *olvida*. Minimax *visita* y *recuerda un valor* que propaga hacia arriba.

Esta analogía es profunda: la complejidad de espacio de minimax es $O(b \cdot m)$ — igual que DFS, no $O(b^m)$. Solo necesita mantener el camino desde la raíz hasta el nodo actual, no todos los nodos explorados.

---

## 3. En lenguaje natural

El algoritmo en cuatro pasos:

1. **Si el estado es terminal**: devuelve su utilidad. El juego terminó — sabemos el resultado exacto.
2. **Si es el turno de MAX**: evalúa todos los estados sucesores recursivamente, devuelve el **máximo** de sus valores. MAX elige la mejor opción disponible.
3. **Si es el turno de MIN**: evalúa todos los estados sucesores recursivamente, devuelve el **mínimo** de sus valores. MIN elige la opción que peor le va a MAX.
4. **En la raíz**: la acción que lleva al sucesor con mayor valor minimax es la acción óptima de MAX.

La clave: para conocer el valor de un nodo MAX, necesitamos conocer el valor de **todos** sus hijos. Eso nos obliga a explorar cada rama hasta las hojas antes de poder comparar — exactamente el orden de DFS.

---

## 4. La función de valor

Definimos $V(s)$ como el valor minimax del estado $s$ — el resultado que ambos jugadores pueden garantizarse con juego perfecto desde $s$:

$$V(s) = \begin{cases}
U(s) & \text{si } \text{Terminal}(s) \\[6pt]
\displaystyle\max_{a \in \text{Acciones}(s)} V\!\left(\text{Resultado}(s,\,a)\right) & \text{si } \text{Jugadores}(s) = \text{MAX} \\[6pt]
\displaystyle\min_{a \in \text{Acciones}(s)} V\!\left(\text{Resultado}(s,\,a)\right) & \text{si } \text{Jugadores}(s) = \text{MIN}
\end{cases}$$

Cada caso tiene una interpretación directa:
- **Terminal**: el valor es conocido — la partida terminó y hay un resultado definido.
- **MAX**: elige el sucesor de mayor valor — maximiza su resultado garantizado.
- **MIN**: elige el sucesor de menor valor — minimiza el resultado garantizado de MAX.

La recursión es bien fundada porque cada llamada opera sobre un estado estrictamente más profundo en el árbol, y los árboles de juegos finitos tienen profundidad acotada.

---

## 5. Pseudocódigo

```
function MINIMAX(juego, estado):

    # ── Punto de entrada ────────────────────────────────────────────────────
    if juego.jugador(estado) == MAX:
        valor, accion ← MAX_VALUE(juego, estado)
    else:
        valor, accion ← MIN_VALUE(juego, estado)
    return accion                            # [P1] devolvemos ACCIÓN, no valor


function MAX_VALUE(juego, estado):

    # ── Caso base: estado terminal ──────────────────────────────────────────
    if juego.terminal(estado):
        return juego.utilidad(estado), None  # [P2] hoja: utilidad conocida

    # ── Bucle: MAX elige la acción que MAXIMIZA ─────────────────────────────
    v ← -∞
    mejor ← None
    for each accion in juego.acciones(estado):
        sucesor ← juego.resultado(estado, accion)
        v2, _ ← MIN_VALUE(juego, sucesor)   # [P3] alterna a MIN en el hijo
        if v2 > v:
            v ← v2
            mejor ← accion
    return v, mejor


function MIN_VALUE(juego, estado):

    # ── Caso base: estado terminal ──────────────────────────────────────────
    if juego.terminal(estado):
        return juego.utilidad(estado), None

    # ── Bucle: MIN elige la acción que MINIMIZA ─────────────────────────────
    v ← +∞
    mejor ← None
    for each accion in juego.acciones(estado):
        sucesor ← juego.resultado(estado, accion)
        v2, _ ← MAX_VALUE(juego, sucesor)   # [P4] alterna a MAX en el hijo
        if v2 < v:
            v ← v2
            mejor ← accion
    return v, mejor
```

La alternancia `MAX_VALUE` ↔ `MIN_VALUE` implementa la alternancia de turnos. Cada llamada profundiza un nivel en el árbol — exactamente DFS. La única adición sobre DFS puro es que al retroceder se retorna un valor numérico en lugar de simplemente desapilar.

---

## 6. Implementación en Python

```python
def minimax(estado, es_max):
    """
    Minimax para Nim.

    Args:
        estado  : tupla de enteros (tamaños de pilas)
        es_max  : True si es turno de MAX, False si es turno de MIN

    Returns:
        (valor, accion) donde accion = (pile_idx, amount) o None si terminal
    """
    # Caso base: estado terminal
    if all(p == 0 for p in estado):
        # El jugador cuyo turno ES (es_max) no puede mover → pierde
        # Si es_max = True  → MAX pierde  → valor = -1
        # Si es_max = False → MIN pierde  → valor = +1 (bueno para MAX)
        return (-1 if es_max else +1), None

    # Generar acciones y evaluar recursivamente
    mejor_valor = -float('inf') if es_max else float('inf')
    mejor_accion = None

    for i, pila in enumerate(estado):
        for cant in range(1, pila + 1):
            nuevo = list(estado)
            nuevo[i] -= cant
            v, _ = minimax(tuple(nuevo), not es_max)   # alterna el turno

            if es_max and v > mejor_valor:
                mejor_valor = v
                mejor_accion = (i, cant)
            elif not es_max and v < mejor_valor:
                mejor_valor = v
                mejor_accion = (i, cant)

    return mejor_valor, mejor_accion


# Ejemplo de uso
if __name__ == '__main__':
    estado = (1, 2)
    valor, accion = minimax(estado, es_max=True)
    print(f"Estado: {estado}")
    print(f"Valor garantizado para MAX: {valor}")
    print(f"Mejor acción (pila, cantidad): {accion}")
    # → Valor garantizado para MAX: 1
    # → Mejor acción (pila, cantidad): (1, 1)   [retirar 1 de la pila B]
```

---

## 7. Traza paso a paso: Nim(1,2)

El árbol de Nim(1,2) tiene exactamente 12 nodos — lo suficientemente pequeño para trazar cada llamada.

![Árbol completo de Nim(1,2)]({{ '/15_adversarial_search/images/06_nim_complete_tree.png' | url }})

La figura muestra el árbol de juego **completo** de Nim(1,2) con 12 nodos. Los círculos azules son nodos MAX, los rojos son nodos MIN. Los cuadrados verdes son estados terminales con su utilidad anotada. La arista verde gruesa señala el camino óptimo de MAX.

| # | Llamada | Estado | Jugador | Retorna |
|:--:|---|:---:|:---:|---|
| 1 | `max_value` | (1,2) | MAX | — (inicia exploración) |
| 2 | `min_value` | (0,2) | MIN | — (acción A-1: retirar 1 de pila A) |
| 3 | `max_value` | (0,1) | MAX | — |
| 4 | `min_value` | (0,0) | MIN | **+1** ✓ terminal |
| 5 | ← `max_value` | (0,1) | MAX | max(+1) = **+1** |
| 6 | `max_value` | (0,0) | MAX | **−1** ✓ terminal |
| 7 | ← `min_value` | (0,2) | MIN | min(+1, −1) = **−1** |
| 8 | `min_value` | (1,1) | MIN | — (acción B-1: retirar 1 de pila B) |
| 9 | `max_value` | (0,1) | MAX | — |
| 10 | `min_value` | (0,0) | MIN | **+1** ✓ terminal |
| 11 | ← `max_value` | (0,1) | MAX | max(+1) = **+1** |
| 12 | `max_value` | (1,0) | MAX | — |
| 13 | `min_value` | (0,0) | MIN | **+1** ✓ terminal |
| 14 | ← `max_value` | (1,0) | MAX | max(+1) = **+1** |
| 15 | ← `min_value` | (1,1) | MIN | min(+1, +1) = **+1** |
| 16 | `min_value` | (1,0) | MIN | — (acción B-2: retirar 2 de pila B) |
| 17 | `max_value` | (1,0) | MAX | — |
| 18 | `min_value` | (0,0) | MIN | **+1** ✓ terminal |
| 19 | ← `max_value` | (1,0) | MAX | max(+1) = **+1** |
| 20 | ← `min_value` | (1,0) | MIN | min(+1) = **−1** ✗ (estado (1,0): MAX tiene turno, MIN no puede forzar −1) |

Corrección de la traza — el estado (1,0) con turno de MIN: MIN retira 1 de la pila de tamaño 1, llegando a (0,0) donde MAX tiene turno y pierde → valor +1 para MAX. Entonces `min_value`(1,0) = min(+1) = **−1** no aplica. Retraza limpia:

| # | Llamada | Estado | Jugador | Retorna | Nota |
|:--:|---|:---:|:---:|---|---|
| 16 | `min_value` | (1,0) | MIN | — | acción B-2: retirar 2 de B |
| 17 | `max_value` | (0,0) | MAX | **−1** ✓ terminal | MAX no puede mover → pierde |
| 18 | ← `min_value` | (1,0) | MIN | min(−1) = **−1** | MIN fuerza derrota de MAX |
| 19 | ← `max_value` | (1,2) | MAX | max(−1, **+1**, −1) = **+1** | **B-1 → (1,1) es la acción óptima** |

![Traza paso a paso]({{ '/15_adversarial_search/images/07_minimax_step_by_step.png' | url }})

**Análisis**: MAX elige la acción B-1 (retirar 1 ficha de la pila B), llegando al estado (1,1). Desde (1,1), MIN está en posición perdedora — cualquier movimiento que haga coloca a MAX en posición de ganar. La acción A-1 lleva a (0,2) con valor −1 para MAX; la acción B-2 lleva a (1,0) con valor −1 para MAX; solo B-1 lleva a (1,1) con valor +1.

**Verificación por nim-sum** (anticipando la sección 15.5): $1 \oplus 2 = 3 \neq 0$ confirma que (1,2) es posición ganadora para MAX. $1 \oplus 1 = 0$ confirma que (1,1) es posición perdedora para el jugador en turno (MIN). ✓

---

## 8. Propiedades

| Propiedad | Valor | Condición |
|---|---|---|
| **Completo** | Sí | En árboles de juego finitos |
| **Óptimo** | Sí\* | \*Contra un oponente que también juega óptimamente |
| **Tiempo** | $O(b^m)$ | $b$ = factor de ramificación, $m$ = profundidad máxima |
| **Espacio** | $O(b \cdot m)$ | Igual que DFS — solo mantiene el camino actual |

Comparación con los algoritmos de módulos anteriores:

| Algoritmo | Tiempo | Espacio | Completo | Óptimo |
|---|---|---|:---:|:---:|
| DFS | $O(b^m)$ | $O(b \cdot m)$ | No | No |
| BFS | $O(b^d)$ | $O(b^d)$ | Sí | Sí (sin pesos) |
| A\* | $O(b^d)$ | $O(b^d)$ | Sí | Sí |
| **Minimax** | $O(b^m)$ | **$O(b \cdot m)$** | Sí | Sí\* |

El espacio lineal de minimax ($O(b \cdot m)$) es una ventaja importante: igual que DFS, solo necesita mantener el camino desde la raíz hasta el nodo actual en la pila de recursión.

---

## 9. Los números reales

| Juego | $b$ | $m$ | Nodos aprox. | ¿Minimax exacto? |
|---|:---:|:---:|---|:---:|
| Nim(1,2) | 3 | 4 | 12 | Sí |
| Tic-tac-toe | 9 | 9 | $\leq 9! = 362{,}880$ | Sí (con simetría) |
| Ajedrez | 35 | 80 | $\approx 10^{123}$ | No |
| Go | 250 | 150 | $\approx 10^{360}$ | No |

Para ajedrez, incluso a 1 billón de nodos por segundo, explorar $10^{123}$ nodos tomaría más tiempo que la edad del universo ($\approx 4 \times 10^{17}$ segundos). La siguiente sección muestra cómo reducir este costo hasta a la raíz cuadrada manteniendo la misma respuesta.

---

**Siguiente:** [Poda alfa-beta →](04_poda_alfa_beta.md)
