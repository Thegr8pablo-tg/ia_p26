---
title: "Heurísticas para planificación"
---

| Notebook | Colab |
|---------|:-----:|
| Notebook 02 — Planificación forward | <a href="https://colab.research.google.com/github/sonder-art/ia_p26/blob/main/clase/16_planificacion_clasica/notebooks/02_planificacion_forward.ipynb" target="_blank"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"></a> |

---

# Heurísticas para planificación: el mismo truco del módulo 14

> *"Simplicity is the ultimate sophistication."*
> — Leonardo da Vinci

---

Forward planning con BFS funciona perfectamente para Blocks World con 3 bloques (13 estados). Pero con 20 bloques el espacio de estados tiene más de $10^{18}$ estados — BFS no alcanza. Necesitamos el mismo truco del módulo 14: una heurística que guíe la búsqueda hacia la meta sin explorar todo el espacio.

---

## 1. El problema: explosión del espacio de estados

![Explosión del espacio de estados]({{ '/16_planificacion_clasica/images/09_state_space_explosion.png' | url }})

| Bloques | Estados alcanzables (aprox.) | ¿BFS factible? |
|:---:|:---:|:---:|
| 3 | 13 | Sí |
| 5 | ~500 | Sí |
| 10 | ~$10^7$ | Apenas |
| 15 | ~$10^{12}$ | No |
| 20 | ~$10^{18}$ | No |

El crecimiento es factorial ($\approx e \cdot n!$) — mucho peor que exponencial. Con 20 bloques, incluso a 1 billón de estados por segundo, BFS tardaría ~30 años.

Esto es exactamente el mismo muro que encontramos en el módulo 14:
- **Módulo 14**: BFS en un grafo ponderado es demasiado lento → A* con heurística $h(n)$.
- **Módulo 16**: BFS en el espacio de estados de planificación es demasiado lento → Forward search con heurística $h(s)$.

La pregunta es: ¿de dónde sacamos una heurística para planificación?

---

## 2. La técnica de relajación: el mismo principio

En el módulo 14 aprendimos la técnica de relajación para diseñar heurísticas admisibles:

> **Relajar** = tomar el problema original, eliminar alguna restricción, y resolver el problema más fácil. La solución del problema relajado es siempre ≤ que la del original → heurística admisible.

Ejemplos del módulo 14:

| Problema | Relajación | Heurística resultante |
|---|---|---|
| 8-puzzle | Las fichas pueden pasar a través de otras | Distancia Manhattan |
| 8-puzzle | Las fichas pueden ir a cualquier posición | Fichas mal colocadas |
| Navegación | Las calles son rectas | Distancia euclidiana |

Para planificación, la relajación más natural es:

> **Ignorar las listas delete.** Las acciones siguen necesitando que sus precondiciones se cumplan, pero al aplicarlas solo agregan proposiciones — nunca eliminan nada.

---

## 3. Relajación por eliminación de deletes

### La idea

En planificación normal, cuando aplicas una acción:
- **Agregas** las proposiciones de la lista add (cosas nuevas que son ciertas).
- **Eliminas** las proposiciones de la lista delete (cosas que dejan de ser ciertas).

En la planificación **relajada**:
- **Agregas** las proposiciones de la lista add.
- **No eliminas nada** — las proposiciones de la lista delete se ignoran.

Esto significa que el estado **solo crece**: una vez que una proposición se vuelve verdadera, **nunca vuelve a ser falsa**. Las proposiciones se acumulan monótonamente.

### ¿Por qué funciona como heurística?

1. **El problema relajado es más fácil**: todo lo que puedes hacer en el problema real, también lo puedes hacer en el relajado (las precondiciones son las mismas). Pero además puedes hacer más cosas, porque las proposiciones no desaparecen.

2. **La solución relajada es más corta (o igual)**: nunca necesitas "deshacer" algo. Si necesitas $\text{Clear}(B)$ para una acción futura y $\text{Clear}(B)$ fue borrado en el plan real, el plan relajado no tiene ese problema — $\text{Clear}(B)$ sigue ahí.

3. **Admisibilidad**: como la solución relajada es siempre $\leq$ la real:

$$h_{\text{relajada}}(s) \leq h^*(s)$$

Esto es exactamente la definición de heurística admisible del módulo 14. Podemos usarla con A*.

### Ejemplo concreto

Veamos cómo difiere la planificación normal de la relajada en nuestro Blocks World:

![Relajación: normal vs sin deletes]({{ '/16_planificacion_clasica/images/10_relaxed_problem.png' | url }})

**Planificación normal** (con listas delete):

```
Paso 1: MoverDesdeMesa(B, C)
  Antes:  { On(A,M), On(B,M), On(C,M), Clear(A), Clear(B), Clear(C) }
  Delete: { On(B,M), Clear(C) }     ← estas proposiciones DESAPARECEN
  Add:    { On(B,C) }
  Después: { On(A,M), On(B,C), On(C,M), Clear(A), Clear(B) }

Paso 2: MoverDesdeMesa(A, B)
  Antes:  { On(A,M), On(B,C), On(C,M), Clear(A), Clear(B) }
  Delete: { On(A,M), Clear(B) }     ← estas proposiciones DESAPARECEN
  Add:    { On(A,B) }
  Después: { On(A,B), On(B,C), On(C,M), Clear(A) }
```

**Planificación relajada** (sin listas delete):

```
Paso 1: MoverDesdeMesa(B, C)
  Antes:  { On(A,M), On(B,M), On(C,M), Clear(A), Clear(B), Clear(C) }
  Delete: (ignorado)                 ← NO se elimina nada
  Add:    { On(B,C) }
  Después: { On(A,M), On(B,M), On(B,C), On(C,M), Clear(A), Clear(B), Clear(C) }
              ↑                                                          ↑
              B está en mesa Y sobre C    ← ¡"imposible" físicamente!    ↑
                                                     C sigue libre ← ¡B está encima!

Paso 2: MoverDesdeMesa(A, B)
  Pre:    { On(A,M) ✓, Clear(A) ✓, Clear(B) ✓ } ← ¡Clear(B) sigue ahí!
  Delete: (ignorado)
  Add:    { On(A,B) }
  Después: { On(A,M), On(A,B), On(B,M), On(B,C), On(C,M), Clear(A), Clear(B), Clear(C) }
```

En el mundo relajado, B está simultáneamente en la mesa Y sobre C. Esto es físicamente imposible, pero **matemáticamente útil**: el problema relajado se resuelve con los mismos 2 pasos, confirmando que $h_{\text{relajada}}(s_0) = 2 = h^*(s_0)$.

En problemas más complejos, el plan relajado puede ser **más corto** que el real (porque no necesita deshacer pasos), dando una heurística que subestima — exactamente lo que A* necesita.

### La heurística

$$h(s) = \text{longitud del plan relajado desde } s \text{ hasta la meta}$$

Para calcularla: resuelve el problema con las mismas acciones pero con listas delete vacías. El número de pasos del plan relajado es $h(s)$.

---

## 4. Conexión con A*

En el módulo 14, A* usa $f(n) = g(n) + h(n)$ para ordenar la frontera:
- $g(n)$ = costo acumulado desde el inicio
- $h(n)$ = estimación del costo restante (heurística admisible)

En planificación:
- $g(s)$ = número de acciones aplicadas desde $s_0$ hasta $s$
- $h(s)$ = longitud del plan relajado desde $s$ hasta la meta

```
Forward planning + Cola FIFO          = BFS      (módulo 13)
Forward planning + Cola de prioridad  = A*       (módulo 14)
  con f(s) = g(s) + h_relajada(s)     = planificador FF
```

El planificador **FF** (FastForward, 2001) usa exactamente esta estructura y fue uno de los planificadores más exitosos de la historia. Ganó la competencia internacional de planificación IPC y estableció el estándar para la década siguiente.

La intuición es la misma que en A*: en vez de explorar todos los estados ciegamente (BFS), **priorizamos** los estados que parecen más cercanos a la meta según la heurística relajada. Esto reduce drásticamente los nodos explorados.

---

## 5. El arco completo: módulos 13–16

| Algoritmo | Módulo | Tipo de estados | Transiciones | Heurística |
|---|:---:|---|---|---|
| BFS / DFS | 13 | Nodos explícitos | Aristas del grafo | Ninguna |
| A* | 14 | Nodos explícitos | Aristas del grafo | $h(n)$ — relajación del problema |
| Minimax | 15 | Configuraciones del juego | Turnos + acciones | Ninguna (exacto) |
| Alpha-beta | 15 | Configuraciones del juego | Turnos + acciones | Ninguna (poda, no heurística) |
| **Forward BFS** | **16** | **Proposiciones** | **Acciones STRIPS** | **Ninguna** |
| **Forward + A*** | **16** | **Proposiciones** | **Acciones STRIPS** | **$h_{\text{relajada}}$** — ignorar deletes |

El patrón es siempre el mismo:

1. **Definir** el espacio de estados y las transiciones.
2. **Buscar** con alguna variante de búsqueda genérica.
3. **Escalar** añadiendo heurísticas que guíen la búsqueda.

Lo que cambia es el **lenguaje de representación** (nodos vs proposiciones vs configuraciones de juego) y la **fuente de las heurísticas** (distancia geométrica vs relajación de restricciones vs evaluación de posición). El algoritmo subyacente es el mismo que aprendimos en el módulo 13.

---

**Siguiente:** [Volver al índice →](00_index.md)
