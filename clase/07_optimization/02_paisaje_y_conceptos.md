---
title: "Paisaje de optimización: mínimos, máximos, sillas y convexidad"
---

# Paisaje de optimización

Imagina la función objetivo como un **terreno montañoso**. Optimizar es buscar el punto más bajo (minimización) o más alto (maximización) de ese terreno. La "forma" de ese terreno determina qué tan fácil o difícil es encontrar la solución.

---

## Mínimos y máximos

Un punto $x^*$ es un **mínimo local** si $f(x^*) \leq f(x)$ para todo $x$ en una vecindad de $x^*$.

Un punto $x^*$ es un **mínimo global** si $f(x^*) \leq f(x)$ para **todo** $x$ en el dominio.

**Condición necesaria** (para funciones diferenciables): en un mínimo o máximo, el gradiente se anula:

$$\nabla f(x^*) = 0$$

Pero cuidado: $\nabla f = 0$ es necesario, no suficiente. Puede ser un mínimo, un máximo, o un punto silla.

---

## Local vs global

La diferencia entre mínimos locales y globales es crucial en la práctica:

![Mínimos locales vs mínimo global]({{ '/07_optimization/images/local_vs_global.png' | url }})

Un algoritmo como descenso de gradiente puede **quedarse atrapado** en un mínimo local sin encontrar el global. Esta es una de las dificultades fundamentales de la optimización no convexa.

> **Notebook — Abre NB1, Sección 3: Paisajes 1D**
> [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sonder-art/ia_p26/blob/main/clase/07_optimization/notebooks/01_formulacion_y_paisaje.ipynb)
>
> 1. Ejecuta las celdas de la Sección 3 para ver una función con múltiples mínimos.
> 2. Cambia `f_custom` a `lambda x: x**4 - 8*x**2`. ¿Cuántos mínimos locales tiene?
> 3. Prueba `lambda x: np.abs(x - 2)` — ¿es diferenciable en el mínimo?

---

## Puntos silla

Un **punto silla** es un punto crítico ($\nabla f = 0$) que no es ni mínimo ni máximo: es mínimo en una dirección y máximo en otra.

![Punto silla]({{ '/07_optimization/images/saddle_point_3d.png' | url }})

El ejemplo clásico es $f(x,y) = x^2 - y^2$: en $(0,0)$ el gradiente es cero, pero es un mínimo a lo largo de $x$ y un máximo a lo largo de $y$.

**¿Por qué importa?** En dimensiones altas (como el entrenamiento de redes neuronales con millones de parámetros), los puntos silla son **mucho más comunes** que los mínimos locales. Intuitivamente: para que un punto crítico sea un mínimo local, *todas* las direcciones deben curvar hacia arriba. En alta dimensión, es muy probable que al menos una dirección curve hacia abajo.

> **Notebook — Abre NB1, Sección 4: Superficies 2D**
> [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sonder-art/ia_p26/blob/main/clase/07_optimization/notebooks/01_formulacion_y_paisaje.ipynb)
>
> 1. Compara los contornos del punto silla ($x^2 - y^2$) con el bowl ($x^2 + y^2$).
> 2. Cambia `f_custom_2d` a `lambda x, y: x**2*y**2 - x**2 - y**2`. ¿Tiene puntos silla?
> 3. Prueba `lambda x, y: np.sin(x) + np.sin(y)` — ¿cuántos mínimos locales ves?

---

## Convexidad

Una función $f$ es **convexa** si para cualesquiera dos puntos $x, y$ y cualquier $\lambda \in [0, 1]$:

$$f(\lambda x + (1-\lambda) y) \leq \lambda f(x) + (1-\lambda) f(y)$$

Geométricamente: **la cuerda entre dos puntos de la curva siempre queda por arriba de la curva**.

![Convexa vs no convexa]({{ '/07_optimization/images/convex_vs_nonconvex.png' | url }})

### ¿Por qué convexidad es tan importante?

> **En una función convexa, todo mínimo local es global.**

Esto significa que si un algoritmo encuentra un punto donde $\nabla f = 0$, puedes estar seguro de que es **la** solución óptima. No hay trampas de mínimos locales.

Ejemplos de funciones convexas:
- $f(x) = x^2$ (y cualquier forma cuadrática positiva definida)
- $f(x) = |x|$
- $f(x) = e^x$
- $f(x) = \max(0, x)$ (ReLU)

Ejemplos de funciones **no** convexas:
- $f(x) = \sin(x)$
- $f(x) = x^4 - 4x^2$ (tiene dos mínimos locales)
- Cualquier red neuronal con más de una capa

> **Notebook — Abre NB1, Secciones 5-6: Convexidad**
> [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sonder-art/ia_p26/blob/main/clase/07_optimization/notebooks/01_formulacion_y_paisaje.ipynb)
>
> 1. Ejecuta las pruebas de cuerdas para $x^2$, $\sin(x)$, $e^x$, $\cos(x)$.
> 2. Clasifica cada función como convexa o no convexa.
> 3. Inventa una función propia y verifica visualmente si es convexa.
> 4. ¿Qué operaciones preservan convexidad? Prueba $f(x) = x^2 + |x|$ y $f(x) = \max(x^2, 2x+1)$.

---

## Taxonomía de problemas

| Tipo | Objetivo | Restricciones | Ejemplo | ¿Convexo? |
|------|----------|---------------|---------|-----------|
| **Programación lineal (LP)** | Lineal | Lineales | Asignación de recursos | Sí |
| **Programación cuadrática (QP)** | Cuadrática | Lineales | SVM, portafolio | Sí (si $Q \succeq 0$) |
| **Optimización convexa** | Convexa | Convexas | Regresión logística | Sí |
| **Optimización no convexa** | Cualquiera | Cualquiera | Redes neuronales | No |
| **Programación entera (IP/MIP)** | Lineal/Cuadrática | Variables enteras | Knapsack, scheduling | No (NP-hard en general) |

A medida que bajas en la tabla, los problemas se vuelven **más difíciles** pero también **más expresivos**.

La buena noticia: muchos problemas de ML son convexos (regresión lineal, logística, SVM) o "casi convexos" (en la práctica, los mínimos locales de redes neuronales suelen tener valores similares).

### Optimización entera y discreta

Cuando las variables de decisión deben ser **enteras** (¿cuántos camiones enviar?, ¿qué proyectos financiar?), el problema cambia fundamentalmente. No puedes simplemente resolver la versión continua y redondear — el resultado redondeado puede ser **infactible** o muy lejos del óptimo.

¿Por qué es más difícil? La región factible ya no es continua — son puntos aislados. No hay gradientes, y no puedes "caminar" suavemente hacia la solución.

**Ejemplo clásico — knapsack (mochila):** Tienes una mochila con capacidad $W$ y $n$ objetos, cada uno con peso $w_i$ y valor $v_i$. ¿Cuáles llevas para maximizar el valor total sin exceder la capacidad?

$$\max \sum_i v_i x_i \quad \text{s.t.} \quad \sum_i w_i x_i \leq W, \quad x_i \in \{0, 1\}$$

En Python, `scipy.optimize.milp` resuelve problemas de programación entera mixta (MIP). Para problemas más serios, bibliotecas como PuLP o Google OR-Tools son el estándar industrial.

---

:::exercise{title="Ejercicio: Clasifica los problemas" difficulty="1"}

Para cada problema, indica si es LP, QP, convexo (no lineal), o no convexo:

1. $\min_{x} \quad 3x_1 + 2x_2$ sujeto a $x_1 + x_2 \leq 10$, $x_1, x_2 \geq 0$
2. $\min_{x} \quad x_1^2 + x_2^2$ sujeto a $x_1 + x_2 = 1$
3. $\min_{x} \quad \sin(x_1) + x_2^2$
4. $\min_{w} \quad \sum_i \log(1 + e^{-y_i w^T x_i})$ (log-loss)

<details>
<summary><strong>Ver Solución</strong></summary>

1. **LP** — Objetivo lineal, restricciones lineales.
2. **QP** — Objetivo cuadrático (con $Q = I$, positiva definida → convexo), restricción lineal de igualdad.
3. **No convexo** — $\sin(x_1)$ no es convexa.
4. **Convexo** — La función log-loss es convexa (composición de funciones convexas). Este es el problema de regresión logística.

</details>

:::

---

**Siguiente:** [Algoritmos →](03_algoritmos.md)
