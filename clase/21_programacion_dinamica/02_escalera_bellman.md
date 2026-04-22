---
title: "La escalera y la ecuación de Bellman"
---

# 21.2 — La escalera y la ecuación de Bellman

> *"Tú no descubres la ecuación leyéndola. La descubres llenando la tabla."*

---

En esta página vas a hacer el trabajo. Al final vas a tener la ecuación de Bellman escrita — no porque yo te la haya dictado, sino porque la vas a haber *usado* cinco veces antes de que le pongamos nombre.

---

## El problema: una escalera con costos

Imagina una escalera de **6 escalones**, numerados del 0 al 5. Empiezas en el escalón **0**. Tu meta es llegar al escalón **5**. En cada turno puedes hacer **una** de dos cosas:

- **Subir 1** — avanzas al escalón siguiente.
- **Saltar 2** — avanzas dos escalones.

Cada escalón te cuesta algo en energía (cansancio, tiempo, lo que quieras imaginar). El costo del escalón $i$ es $c_i$. Aquí están los costos de nuestra escalera:

| Escalón $i$ | 0 | 1 | 2 | 3 | 4 | 5 |
|:-----------:|:-:|:-:|:-:|:-:|:-:|:-:|
| Costo $c_i$ | 3 | 2 | 7 | 1 | 4 | 0 |

El costo total que pagas es la suma de los costos de los escalones donde *aterrizas*. La pregunta es simple:

> ¿Cuál es la secuencia de movimientos que minimiza el costo total del escalón 0 al escalón 5?

![Setup de la escalera]({{ '/21_programacion_dinamica/images/01_escalera_setup.png' | url }})

---

## El intento codicioso — ¿funciona?

Antes de pensar en grande, probemos la estrategia codiciosa: **en cada paso, elige el escalón siguiente más barato**.

- Desde 0: puedes ir a 1 (costo 2) o a 2 (costo 7). Elige **1**.
- Desde 1: puedes ir a 2 (costo 7) o a 3 (costo 1). Elige **3**.
- Desde 3: puedes ir a 4 (costo 4) o a 5 (costo 0). Elige **5**.

Trayectoria codiciosa: **0 → 1 → 3 → 5**. Costo total: $3 + 2 + 1 + 0 = 6$.

![Codicioso vs. óptimo]({{ '/21_programacion_dinamica/images/02_greedy_vs_optimo.png' | url }})

En este vector de costos particular, el codicioso tuvo suerte: su trayectoria resultó ser la óptima. Pero eso no es porque la codicia sea buena estrategia — es porque los costos nos quedaron benignos. **Queremos un método que funcione sin depender de la suerte.**

Vamos a construirlo.

---

## La idea — pensar desde la meta hacia atrás

El principio de optimalidad nos dice algo muy específico: para saber qué hacer en el escalón 0, **primero necesitamos saber qué tan barato es llegar a la meta desde el escalón 1 y desde el escalón 2**. Entonces empezamos por la meta y vamos hacia atrás.

Definamos, para cada escalón $i$:

$$V(i) = \text{el costo mínimo total para llegar a la meta, empezando en } i.$$

Tu tarea: llenar la siguiente tabla, de derecha a izquierda.

| Escalón $i$ | 0 | 1 | 2 | 3 | 4 | 5 |
|:-----------:|:-:|:-:|:-:|:-:|:-:|:-:|
| Costo $c_i$ | 3 | 2 | 7 | 1 | 4 | 0 |
| Valor $V(i)$ | ? | ? | ? | ? | ? | ? |

Vamos a ir paso por paso.

### Paso 1 — ¿cuánto cuesta llegar a la meta desde la meta?

Si ya estás en el escalón 5, pagas 0 (ya llegaste). Entonces:

$$V(5) = 0.$$

### Paso 2 — desde el escalón 4

Desde 4 la única jugada es **subir 1** (saltar 2 te sacaría de la escalera). Pagas $c_4 = 4$ y llegas a 5, donde el costo restante es $V(5) = 0$:

$$V(4) = c_4 + V(5) = 4 + 0 = 4.$$

### Paso 3 — desde el escalón 3

Desde 3 tienes dos opciones:

- Subir 1 (vas a 4): pagas $c_3 + V(4) = 1 + 4 = 5$.
- Saltar 2 (vas a 5): pagas $c_3 + V(5) = 1 + 0 = 1$.

Elegimos la más barata:

$$V(3) = c_3 + \min\bigl(V(4),\; V(5)\bigr) = 1 + \min(4, 0) = 1. \quad [\text{acción: saltar 2}]$$

### Paso 4 — desde el escalón 2

- Subir 1 (vas a 3): $c_2 + V(3) = 7 + 1 = 8$.
- Saltar 2 (vas a 4): $c_2 + V(4) = 7 + 4 = 11$.

$$V(2) = c_2 + \min\bigl(V(3),\; V(4)\bigr) = 7 + \min(1, 4) = 8. \quad [\text{acción: subir 1}]$$

### Paso 5 — desde el escalón 1

- Subir 1 (vas a 2): $c_1 + V(2) = 2 + 8 = 10$.
- Saltar 2 (vas a 3): $c_1 + V(3) = 2 + 1 = 3$.

$$V(1) = c_1 + \min\bigl(V(2),\; V(3)\bigr) = 2 + \min(8, 1) = 3. \quad [\text{acción: saltar 2}]$$

---

### Una pausa — ¿qué patrón ves?

Para: antes de terminar la tabla, mira lo que llevas escrito. En cada renglón has calculado algo de la forma:

$$V(i) = c_i + \min\bigl(V(i+1),\; V(i+2)\bigr).$$

Eso es lo mismo tres veces — cambia solo el índice. Es una **fórmula recursiva**: el valor de cada escalón se expresa en términos de los valores de los escalones *posteriores*. Esto **es** el principio de optimalidad traducido a matemáticas.

No te preocupes, todavía no le ponemos nombre. Termina la tabla.

### Paso 6 — desde el escalón 0

- Subir 1 (vas a 1): $c_0 + V(1) = 3 + 3 = 6$.
- Saltar 2 (vas a 2): $c_0 + V(2) = 3 + 8 = 11$.

$$V(0) = c_0 + \min\bigl(V(1),\; V(2)\bigr) = 3 + \min(3, 8) = 6. \quad [\text{acción: subir 1}]$$

### La tabla, llena

| Escalón $i$ | 0 | 1 | 2 | 3 | 4 | 5 |
|:-----------:|:-:|:-:|:-:|:-:|:-:|:-:|
| Costo $c_i$ | 3 | 2 | 7 | 1 | 4 | 0 |
| Valor $V(i)$ | **6** | **3** | **8** | **1** | **4** | **0** |
| Acción óptima | subir 1 | saltar 2 | subir 1 | saltar 2 | subir 1 | — |

**Política óptima:** desde 0 sube 1, desde 1 salta 2, desde 3 salta 2. **Trayectoria:** $0 \to 1 \to 3 \to 5$. **Costo total:** $3 + 2 + 1 + 0 = 6$. Coincide con lo que calculamos con $V(0)$.

![Tabla de valores llena de derecha a izquierda]({{ '/21_programacion_dinamica/images/03_tabla_valores.png' | url }})

---

## Ahora sí, le ponemos nombre

Lo que acabas de escribir cinco veces es la fórmula más importante de la optimización dinámica. Se llama **la ecuación de Bellman**.

En su forma general, para un problema con acciones $a$ y función de transición $T(i, a)$ (la acción $a$ desde el estado $i$ te lleva al estado $T(i, a)$):

$$\boxed{\, V(i) = c_i + \min_{a}\; V\!\bigl(T(i, a)\bigr) \,}$$

Léela en palabras: *"el valor de estar en $i$ es el costo de estar en $i$ más el mejor valor que puedes obtener desde el estado al que te mueves".*

No es un algoritmo. Es una **condición**: nos dice qué propiedad satisface una función de valor óptima. El algoritmo que la resuelve (la programación dinámica, bottom-up) lo vamos a ver explícitamente en la sección 21.4 — aunque en realidad, acabas de aplicarlo a mano.

---

## Una vuelta de tuerca: ¿qué pasa si a veces resbalas?

Hasta ahora asumimos que cada acción hace exactamente lo que quieres. La realidad es menos cooperativa. Supón que la escalera está mojada y:

- La acción **subir 1** siempre funciona (pasas al escalón siguiente).
- La acción **saltar 2** **éxito** (llegas a $i+2$) con probabilidad $0.8$, pero **resbalas** (solo avanzas a $i+1$) con probabilidad $0.2$.

Tu trayectoria ya no es determinista. Aún así, el principio de optimalidad se aplica — solo que ahora el costo que esperas pagar desde cualquier estado depende de dónde **esperas** aterrizar, no de dónde aterrizas con certeza.

La versión estocástica de la función de valor:

$$V(i) = c_i + \min_{a}\; \mathbb{E}\bigl[\,V(\text{siguiente estado})\,\bigr]$$

donde la esperanza es sobre las posibles siguientes estados bajo la acción $a$. Escrito con probabilidades explícitas:

$$\boxed{\, V(s) = \min_{a}\; \Bigl\{\, c(s, a) + \sum_{s'} P(s' \mid s, a)\, V(s') \,\Bigr\} \,}$$

Esto **es** la ecuación de Bellman en su forma general. La suma es sobre todos los estados siguientes posibles, ponderada por la probabilidad de que efectivamente aterrices en cada uno.

### Rellenemos la tabla estocástica

Desde el escalón 4 solo hay una acción (subir 1), igual que antes: $V(4) = 4$.

Desde el escalón 3:

- Acción "subir 1" (determinista, va a 4): $c_3 + V(4) = 1 + 4 = 5$.
- Acción "saltar 2" (va a 5 con prob. 0.8, a 4 con prob. 0.2): $c_3 + 0.8 \cdot V(5) + 0.2 \cdot V(4) = 1 + 0 + 0.8 = 1.8$.

$$V(3) = \min(5,\, 1.8) = 1.8. \quad [\text{acción: saltar 2}]$$

Desde el escalón 2:

- "Subir 1" (va a 3): $c_2 + V(3) = 7 + 1.8 = 8.8$.
- "Saltar 2" (va a 4 con prob. 0.8, a 3 con prob. 0.2): $c_2 + 0.8 \cdot V(4) + 0.2 \cdot V(3) = 7 + 3.2 + 0.36 = 10.56$.

$$V(2) = \min(8.8,\, 10.56) = 8.8. \quad [\text{acción: subir 1}]$$

Desde el escalón 1:

- "Subir 1" (va a 2): $2 + V(2) = 2 + 8.8 = 10.8$.
- "Saltar 2" (va a 3 con prob. 0.8, a 2 con prob. 0.2): $2 + 0.8 \cdot V(3) + 0.2 \cdot V(2) = 2 + 1.44 + 1.76 = 5.2$.

$$V(1) = \min(10.8,\, 5.2) = 5.2. \quad [\text{acción: saltar 2}]$$

Desde el escalón 0:

- "Subir 1" (va a 1): $3 + V(1) = 3 + 5.2 = 8.2$.
- "Saltar 2" (va a 2 con prob. 0.8, a 1 con prob. 0.2): $3 + 0.8 \cdot V(2) + 0.2 \cdot V(1) = 3 + 7.04 + 1.04 = 11.08$.

$$V(0) = \min(8.2,\, 11.08) = 8.2. \quad [\text{acción: subir 1}]$$

### Tabla estocástica

| Escalón $i$ | 0 | 1 | 2 | 3 | 4 | 5 |
|:-----------:|:-:|:-:|:-:|:-:|:-:|:-:|
| $V$ determinista | 6 | 3 | 8 | 1 | 4 | 0 |
| $V$ estocástico | **8.2** | **5.2** | **8.8** | **1.8** | **4.0** | **0.0** |

![Escalera estocástica]({{ '/21_programacion_dinamica/images/04_escalera_estocastica.png' | url }})

**Observación clave.** El costo esperado desde el escalón 0 subió de **6** a **8.2**. La diferencia, **2.2**, es lo que te cuesta la incertidumbre. No estamos haciendo nada peor — estamos tomando las mismas decisiones inteligentes. Simplemente hay caminos donde el mundo no coopera. Ese 2.2 es **el precio de la incertidumbre**, y es un número que *ves*, no solo un concepto abstracto.

Fíjate que la política óptima cambió en un escalón: en el estado 1, ahora conviene saltar 2 en lugar de jugar seguro. Te arriesgas porque el salto vale la pena en esperanza, aun con el 20% de chance de no llegar.

---

## Otra vuelta: ¿y si el futuro vale menos que el presente?

Hasta aquí tratamos cada costo como igual de pesado, sin importar cuándo ocurra. Pero los humanos (y los mercados, y los agentes computacionales) rara vez piensan así. Un peso hoy no vale lo mismo que un peso dentro de un año. Un riesgo dentro de 10 turnos pesa menos que un riesgo dentro de 2.

Introducimos un **factor de descuento** $\gamma \in [0, 1]$ que pondera el futuro. Pero antes de ponerlo en la ecuación, hagámoslo sentir real — $\gamma$ no es un parámetro arbitrario, sale de una historia concreta.

### Historia 1 — "la escalera se puede interrumpir"

Supón que, en cada paso, hay una probabilidad $p$ de que algo te obligue a abandonar (se apaga la luz, llegan los exámenes, se acaba el día). Si $p = 0.05$, entonces la probabilidad de que sigas subiendo un paso más después es:

$$\gamma = 1 - p = 0.95.$$

El valor esperado desde un estado ya no es "todo lo que pasa adelante" — es "todo lo que pasa adelante, multiplicado por la probabilidad de que *realmente pase*". Y esa probabilidad se acumula: después de $t$ pasos, la probabilidad de seguir activo es $\gamma^t$.

![Descuento y probabilidad de terminación]({{ '/21_programacion_dinamica/images/05_gamma_decaimiento.png' | url }})

### Historia 2 — "un peso hoy vale más que un peso mañana"

Esta la conoces: si te ofrezco &#36;100 hoy o &#36;100 el año entrante, eliges hoy. Porque (a) puedes invertirlo, (b) la inflación lo erosiona, (c) podrías no estar aquí. Tu cerebro aplica un **factor de descuento subjetivo**. Si valoras &#36;100 de hoy igual que &#36;105 el año entrante, tu $\gamma$ (anual) es $\approx 0.95$.

Las dos historias llegan al mismo lugar: $\gamma = 0.95$. Es el mismo número, con dos razones posibles para creer en él.

### La ecuación de Bellman con descuento

Ahora sí, la ecuación en su forma más general:

$$\boxed{\, V(s) = \min_{a}\; \Bigl\{\, c(s, a) + \gamma \sum_{s'} P(s' \mid s, a)\, V(s') \,\Bigr\} \,}$$

Compárala con la forma anterior: solo apareció un $\gamma$ multiplicando a la esperanza. Toda la esperanza, todo el futuro, queda escalado por $\gamma$.

### Un paso concreto: $V(3)$ con $\gamma = 0.95$ (estocástico)

Desde el escalón 3, acción "saltar 2":

$$V(3) = c_3 + \gamma \cdot \bigl[\,0.8 \cdot V(5) + 0.2 \cdot V(4)\,\bigr] = 1 + 0.95 \cdot (0.8 \cdot 0 + 0.2 \cdot 4) = 1 + 0.95 \cdot 0.8 = 1.76.$$

El factor $\gamma = 0.95$ hace que aterrizar en el costoso $V(4) = 4$ se sienta *un poquito menos grave* — porque es un costo futuro. Si $\gamma = 1$ (sin descuento) volverías a obtener $V(3) = 1.8$.

---

## Resumen antes de seguir

Tres formas de la ecuación de Bellman, todas con la misma estructura:

| Caso | Ecuación |
|------|----------|
| Determinista | $V(i) = c_i + \min_a V(T(i, a))$ |
| Estocástico | $V(s) = \min_a \bigl\{ c(s, a) + \sum_{s'} P(s' \mid s, a)\, V(s') \bigr\}$ |
| Estocástico con descuento | $V(s) = \min_a \bigl\{ c(s, a) + \gamma \sum_{s'} P(s' \mid s, a)\, V(s') \bigr\}$ |

Cada versión dice *lo mismo*: **el valor de un estado es el costo inmediato más el mejor valor que puedes esperar desde el siguiente estado**. Lo único que cambia es qué tan exigentemente modelas la incertidumbre y el futuro.

Maximizar también es posible (para problemas de recompensa en lugar de costo): simplemente intercambia $\min$ por $\max$ y llama a $c$ "recompensa $r$". La estructura es idéntica.

---

**Siguiente:** [Formular problemas como MDP →](03_formular_problemas.md)
