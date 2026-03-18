---
title: "Poda alfa-beta"
---

| Notebook | Colab |
|---------|:-----:|
| Notebook 02 — Minimax y alpha-beta | <a href="COLAB_URL" target="_blank"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"></a> |

---

# Poda alfa-beta: la misma respuesta, menos trabajo

> *"The art of being wise is the art of knowing what to overlook."*
> — William James

---

Alpha-beta es minimax con una poda inteligente: descarta ramas del árbol que no pueden cambiar la decisión final. La respuesta es **idéntica** a minimax — la acción que retorna es la misma. El trabajo se puede reducir hasta a la raíz cuadrada del de minimax.

---

## 1. Intuición: el detective que para cuando sabe suficiente

Antes de cualquier fórmula, un ejemplo en lenguaje natural:

> Eres MAX. Ya exploraste la acción A y encontraste que te garantiza un valor de **+1**.
>
> Ahora exploras la acción B. Bajas al nodo MIN de esa rama. MIN examina sus opciones y encuentra una que le da un valor de **−1** — MIN puede forzar que tú obtengas ≤ −1 por esa rama.
>
> ¿Necesitas seguir explorando el resto de la rama B?
>
> **No.** MIN puede forzar ≤ −1 en esa rama, y tú ya tienes **+1** garantizado en la acción A. Nunca elegirías B. Todo lo que quede por explorar en esa rama no puede mejorar tu situación — puedes ignorarlo.

Ese razonamiento es alpha-beta. La poda ocurre cuando sabemos que, sin importar lo que quede por explorar en una rama, la decisión en el nodo ancestro no puede cambiar.

---

## 2. Los valores $\alpha$ y $\beta$

- $\alpha$ = el **mejor valor** (el mayor) que MAX puede **garantizarse** en el camino actual desde la raíz hasta el nodo actual. Empieza en $-\infty$.
- $\beta$ = el **mejor valor** (el menor) que MIN puede **garantizarse** en el camino actual desde la raíz hasta el nodo actual. Empieza en $+\infty$.

Se pasan como parámetros **hacia abajo** en el árbol — cada nodo hijo hereda los valores de su padre. La invariante es:

$$\alpha \leq V(s) \leq \beta$$

Si en algún momento $\alpha \geq \beta$, sabemos que este nodo no puede influir en la decisión del ancestro — podamos todo lo que quede por explorar en este subárbol.

---

## 3. Condición de poda

```
Nodo MAX: si encontramos un hijo con valor v ≥ β → PODA (β-cutoff)
    ↑
    MIN ya tiene garantía ≤ β en otra parte del árbol.
    MAX puede forzar ≥ v ≥ β aquí.
    MIN nunca vendría a este subárbol — podamos el resto.

Nodo MIN: si encontramos un hijo con valor v ≤ α → PODA (α-cutoff)
    ↑
    MAX ya tiene garantía ≥ α en otra parte del árbol.
    MIN puede forzar ≤ v ≤ α aquí.
    MAX nunca vendría a este subárbol — podamos el resto.
```

Regla nemotécnica: **MAX poda cuando encontró algo demasiado bueno para que MIN lo permita** ($v \geq \beta$); **MIN poda cuando encontró algo demasiado malo para que MAX lo elija** ($v \leq \alpha$).

---

## 4. En lenguaje natural

El algoritmo en cuatro pasos — idéntico a minimax excepto por los parámetros $\alpha$ y $\beta$:

1. **Si el estado es terminal**: devuelve su utilidad. Igual que minimax.
2. **Si es el turno de MAX**: evalúa sucesores, actualiza $\alpha$ con el mejor encontrado. Si en cualquier momento $v \geq \beta$, **para** — el resto de esta rama no importa.
3. **Si es el turno de MIN**: evalúa sucesores, actualiza $\beta$ con el peor encontrado. Si en cualquier momento $v \leq \alpha$, **para** — el resto de esta rama no importa.
4. **En la raíz**: la decisión es idéntica a la de minimax. La diferencia es solo cuántos nodos se exploraron.

Los valores $\alpha$ y $\beta$ se pasan hacia abajo en cada llamada recursiva, acumulando la información de lo que ya se ha explorado en otras ramas del árbol.

---

## 5. Pseudocódigo

Los cambios respecto a minimax son exactamente **tres líneas** — marcadas con `[P1]`, `[P2]`, `[P3]`.

```
function ALPHA_BETA(juego, estado):

    # ── Punto de entrada ─────────────────────────────────────────────────────
    if juego.jugador(estado) == MAX:
        v, accion ← MAX_VALUE_AB(juego, estado, -∞, +∞)  # [P1] α=-∞, β=+∞ iniciales
    else:
        v, accion ← MIN_VALUE_AB(juego, estado, -∞, +∞)
    return accion


function MAX_VALUE_AB(juego, estado, α, β):

    # ── Caso base ────────────────────────────────────────────────────────────
    if juego.terminal(estado):
        return juego.utilidad(estado), None

    # ── Bucle con poda ───────────────────────────────────────────────────────
    v ← -∞
    mejor ← None
    for each accion in juego.acciones(estado):
        sucesor ← juego.resultado(estado, accion)
        v2, _ ← MIN_VALUE_AB(juego, sucesor, α, β)
        if v2 > v:
            v ← v2
            mejor ← accion
        α ← max(α, v)                           # [P2] actualizar α
        if v ≥ β:                                # [P3] poda β
            return v, mejor                      #      MIN no vendría aquí
    return v, mejor


function MIN_VALUE_AB(juego, estado, α, β):

    # ── Caso base ────────────────────────────────────────────────────────────
    if juego.terminal(estado):
        return juego.utilidad(estado), None

    # ── Bucle con poda ───────────────────────────────────────────────────────
    v ← +∞
    mejor ← None
    for each accion in juego.acciones(estado):
        sucesor ← juego.resultado(estado, accion)
        v2, _ ← MAX_VALUE_AB(juego, sucesor, α, β)
        if v2 < v:
            v ← v2
            mejor ← accion
        β ← min(β, v)                           # [P2] actualizar β
        if v ≤ α:                                # [P3] poda α
            return v, mejor                      #      MAX no vendría aquí
    return v, mejor
```

La estructura del algoritmo es idéntica a minimax. Los únicos cambios son:
- `[P1]`: pasar $\alpha = -\infty$, $\beta = +\infty$ al inicio.
- `[P2]`: actualizar $\alpha$ (en MAX) o $\beta$ (en MIN) con el mejor valor encontrado.
- `[P3]`: si $v \geq \beta$ (en MAX) o $v \leq \alpha$ (en MIN), retornar antes de terminar el bucle.

---

## 6. Implementación en Python

```python
def alpha_beta(estado, es_max, alpha=-float('inf'), beta=float('inf')):
    """
    Alpha-beta para Nim.

    Args:
        estado : tupla de enteros (tamaños de pilas)
        es_max : True si es turno de MAX, False si es turno de MIN
        alpha  : mejor valor que MAX puede garantizarse en el camino actual
        beta   : mejor valor que MIN puede garantizarse en el camino actual

    Returns:
        (valor, accion) donde accion = (pile_idx, amount) o None si terminal
    """
    # Caso base: estado terminal
    if all(p == 0 for p in estado):
        return (-1 if es_max else +1), None

    mejor_valor = -float('inf') if es_max else float('inf')
    mejor_accion = None

    for i, pila in enumerate(estado):
        for cant in range(1, pila + 1):
            nuevo = list(estado)
            nuevo[i] -= cant
            v, _ = alpha_beta(tuple(nuevo), not es_max, alpha, beta)

            if es_max:
                if v > mejor_valor:
                    mejor_valor = v
                    mejor_accion = (i, cant)
                alpha = max(alpha, mejor_valor)
                if mejor_valor >= beta:          # poda β
                    return mejor_valor, mejor_accion
            else:
                if v < mejor_valor:
                    mejor_valor = v
                    mejor_accion = (i, cant)
                beta = min(beta, mejor_valor)
                if mejor_valor <= alpha:         # poda α
                    return mejor_valor, mejor_accion

    return mejor_valor, mejor_accion


# Verificación: alpha-beta da la misma respuesta que minimax
if __name__ == '__main__':
    estado = (1, 2)
    v_mm, a_mm = minimax(estado, es_max=True)
    v_ab, a_ab = alpha_beta(estado, es_max=True)
    assert v_mm == v_ab, "Los valores deben coincidir"
    assert a_mm == a_ab, "Las acciones deben coincidir"
    print(f"Minimax:    valor={v_mm}, accion={a_mm}")
    print(f"Alpha-beta: valor={v_ab}, accion={a_ab}")
    # → Minimax:    valor=1, accion=(1, 1)
    # → Alpha-beta: valor=1, accion=(1, 1)
```

---

## 7. Traza: Nim(2,3) con poda

Para mostrar la poda de forma más visible, usamos Nim(2,3) — el árbol tiene más ramas desde la raíz, proporcionando más oportunidades de poda. La decisión final es la misma que daría minimax, pero alpha-beta abandona varias ramas antes de explorarlas completamente.

![Alpha-beta en Nim(2,3)]({{ '/15_adversarial_search/images/08_alphabeta_nim23.png' | url }})

La figura muestra el árbol de Nim(2,3) con las ramas podadas marcadas en gris. Los valores $\alpha$ y $\beta$ se actualizan a medida que sube la información de las hojas.

Traza parcial mostrando el momento de la primera poda:

| # | Estado | Jugador | $\alpha$ | $\beta$ | Retorna | Nota |
|:--:|:---:|:---:|:---:|:---:|---|---|
| 1 | (2,3) | MAX | $-\infty$ | $+\infty$ | — | inicio |
| 2 | (1,3) | MIN | $-\infty$ | $+\infty$ | — | acción A-1 |
| 3 | (0,3) | MAX | $-\infty$ | $+\infty$ | — | MIN→A-1 |
| 4 | (0,2) | MIN | $-\infty$ | $+\infty$ | — | MAX→B-1 |
| 5 | (0,1) | MAX | $-\infty$ | $+\infty$ | — | MIN→B-1 |
| 6 | (0,0) | MAX | $-\infty$ | $+\infty$ | **−1** ✓ | terminal |
| 7 | ← (0,1) | MAX | $-\infty$ | $+\infty$ | **+1** | única acción |
| 8 | ← (0,2) | MIN | $-\infty$ | **+1** | — | β ← +1 |
| 9 | (0,0) | MIN | $-\infty$ | **+1** | **+1** ✓ | terminal |
| 10 | ← (0,2) | MIN | $-\infty$ | **0** | — | min(+1,+1) sigue |
| 11 | ← (0,3) | MAX | **+1** | $+\infty$ | **+1** | α ← +1 |
| 12 | (1,2) | MIN | **+1** | $+\infty$ | — | MIN acción A-1 (pila A=1) |
| 13 | (0,2) | MAX | **+1** | $+\infty$ | — | MAX evalúa |
| 14 | (0,1) | MIN | **+1** | $+\infty$ | — | |
| 15 | (0,0) | MIN | **+1** | $+\infty$ | **+1** ✓ | terminal |
| 16 | ← (0,1) | MIN | **+1** | **+1** | **+1** | β ← +1; **+1 ≤ α=+1 → PODA** |
| 17 | (1,2) poda | MIN | **+1** | **+1** | **≤+1** | ramas restantes de (1,2) podadas |
| 18 | ← (1,3) | MIN | **+1** | $+\infty$ | min(+1, ≤+1) = | MIN no puede superar lo ya visto |
| 19 | ← (2,3) | MAX | **+1** | $+\infty$ | max(+1,…) = **+1** | acción A-1 confirmada óptima |

![Minimax vs alpha-beta]({{ '/15_adversarial_search/images/09_alphabeta_vs_minimax.png' | url }})

La figura compara el número de nodos expandidos por minimax y alpha-beta en el mismo árbol de Nim(2,3). Alpha-beta produce la misma decisión final con menos trabajo.

---

## 8. Análisis de eficiencia

| Ordenamiento | Complejidad | Equivalencia | Ejemplo: ajedrez a profundidad 4 |
|---|---|---|---|
| **Peor caso** | $O(b^m)$ | = minimax | Sin ahorro — poda nunca dispara |
| **Orden aleatorio** | $O(b^{3m/4})$ | ≈ 25% menos profundidad | Equivale a explorar hasta profundidad 3 |
| **Orden perfecto** | **$O(b^{m/2})$** | **dobla la profundidad efectiva** | **→ profundidad 8 con mismo cómputo** |

Con ordenamiento perfecto, alpha-beta puede buscar el **doble de profundidad** que minimax con el mismo tiempo de cómputo. Para ajedrez: pasar de profundidad 4 a profundidad 8 es una diferencia enorme en calidad de juego — la diferencia entre un programa que comete errores tácticos obvios y uno que planea combinaciones de varias jugadas.

La intuición del ordenamiento perfecto: si siempre exploramos primero el mejor movimiento (desde la perspectiva de quien elige), el valor de $\alpha$ sube (o $\beta$ baja) tan rápido como es posible, generando cortes en todos los hermanos restantes.

---

## 9. Ordenamiento de movimientos y módulo 14

El ordenamiento de movimientos es el análogo adversarial de las heurísticas $h(n)$ del módulo 14:

> En A\*, ordenar la frontera por $h(n)$ guía la búsqueda hacia la meta más rápidamente. En alpha-beta, explorar primero los movimientos más prometedores genera cortes $\alpha$/$\beta$ más pronto, reduciendo el trabajo total.

Estrategias comunes de ordenamiento:
- **Killer moves**: movimientos que causaron cortes en otras ramas del mismo nivel — es probable que también causen cortes aquí.
- **Evaluación rápida**: calcular un valor aproximado de cada movimiento antes de ordenarlos. Una función análoga a $h$ que mide el "atractivo" del movimiento.
- **Tabla de transposición**: recordar qué posiciones ya se evaluaron y su valor — si llegamos a la misma posición por otra secuencia, reutilizamos el resultado.

Todas estas técnicas hacen que alpha-beta se acerque al caso de ordenamiento perfecto — y nos llevan naturalmente a las funciones de evaluación de la sección 15.5.

---

## 10. Una posición real de tic-tac-toe

![Tic-tac-toe: decisión minimax]({{ '/15_adversarial_search/images/10_tictactoe_endgame.png' | url }})

La figura muestra una posición de tic-tac-toe donde O amenaza ganar en la siguiente jugada (tiene dos en raya con una celda libre). Minimax identifica el único movimiento correcto de X — bloquear la amenaza — y calcula que el juego termina en empate con juego perfecto de ambos lados. Alpha-beta llega a la misma conclusión expandiendo un subconjunto estrictamente menor de nodos: en cuanto encuentra el bloqueo obligatorio, poda todas las ramas alternativas.

---

## 11. ¿Y el ajedrez?

Alpha-beta con ordenamiento perfecto puede alcanzar profundidad 8 en lugar de profundidad 4 con el mismo cómputo. Eso es la diferencia entre un motor "principiante" y un motor de "jugador de club". Pero aun así, profundidad 8 con $b \approx 35$ significa $\approx 35^4 \approx 1.5 \times 10^6$ nodos — manejable. Profundidad 12, que es lo que logran los motores modernos, requiere técnicas adicionales que veremos en la siguiente sección.

---

**Siguiente:** [Juegos complejos →](05_juegos_complejos.md)
