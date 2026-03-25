---
title: "ε-Greedy: la estrategia más simple"
---

# 17.2 — ε-Greedy: la estrategia más simple

> *"The simplest solution is almost always the best."* — Occam

---

## Intuición

La idea es directa: la mayor parte del tiempo, **explota** (jala el brazo con mejor estimación actual). Pero con probabilidad $\varepsilon$, **explora** (jala un brazo al azar, sin importar qué tan bueno o malo parezca).

Es como un chef que 90% del tiempo cocina su plato estrella, pero 10% del tiempo prueba una receta aleatoria del libro. Simple, fácil de implementar, y sorprendentemente efectivo como primera aproximación.

---

## Regla de selección

Tenemos $K$ brazos (en nuestro problema canónico, $K = 3$: los brazos A, B, C). En cada ronda, lanzamos una moneda con probabilidad $\varepsilon$:

- **Con probabilidad $\varepsilon$**: elegir un brazo al azar (explorar)
- **Con probabilidad $1 - \varepsilon$**: elegir el brazo con mejor media estimada (explotar)

$$A_t =
\begin{cases}
\text{brazo aleatorio en } 1, \ldots, K & \text{con prob. } \varepsilon \\
\arg\max_i \hat{\mu}_i & \text{con prob. } 1 - \varepsilon
\end{cases}$$

donde $\hat{\mu}_i$ es la **media muestral** del brazo $i$: el promedio de todas las recompensas que hemos observado al jalar ese brazo.

---

## Actualización incremental de la media

No necesitamos almacenar todas las recompensas pasadas. Podemos actualizar la media **incrementalmente**. Si acabamos de jalar el brazo $i$ y observamos una recompensa $r$ (un número: 0 o 1 en Bernoulli, un valor real en Gaussiano), actualizamos:

$$\hat{\mu}_i \leftarrow \hat{\mu}_i + \frac{1}{N_i}\left(r - \hat{\mu}_i\right)$$

Aquí $r$ es la recompensa que acabamos de observar en esta ronda, $\hat{\mu}_i$ es nuestra estimación actual de la media del brazo $i$, y $N_i$ es el número total de veces que hemos jalado ese brazo (incluyendo esta vez).

La fórmula dice: ajustar la estimación en la dirección del **error** $(r - \hat{\mu}_i)$, ponderado por $\frac{1}{N_i}$. Si $r > \hat{\mu}_i$, la estimación sube; si $r < \hat{\mu}_i$, baja. Conforme $N_i$ crece, los ajustes son más pequeños (la estimación se estabiliza).

**Derivación**: si la media de $n$ observaciones es $\hat{\mu}^{(n)} = \frac{1}{n}\sum_{j=1}^{n} r_j$, al agregar una nueva observación $r_{n+1}$:

$$\hat{\mu}^{(n+1)} = \frac{1}{n+1}\sum_{j=1}^{n+1} r_j = \frac{1}{n+1}\left(n \cdot \hat{\mu}^{(n)} + r_{n+1}\right) = \hat{\mu}^{(n)} + \frac{1}{n+1}(r_{n+1} - \hat{\mu}^{(n)})$$

Esta es exactamente la misma fórmula del **estimador Monte Carlo incremental** del Módulo 12. La diferencia: en Monte Carlo estimamos una sola cantidad; aquí mantenemos $K$ estimadores en paralelo, uno por brazo.

---

## Pseudocódigo

```
función EPSILON_GREEDY(K, T, ε):
    # ── Inicialización ────────────────────────────────────
    para i = 1, …, K:
        Q[i] ← 0              # [P1] media estimada del brazo i (sin datos aún)
        N[i] ← 0              # [P2] contador: cuántas veces se ha jalado el brazo i

    # ── Bucle principal ───────────────────────────────────
    para t = 1, …, T:

        # ── Decisión: explorar o explotar ─────────────────
        si random() < ε:                        # [P3] con probabilidad ε: explorar
            A ← brazo aleatorio uniforme en {1, …, K}
        sino:
            A ← argmax_i Q[i]                   # [P4] con probabilidad 1−ε: explotar

        # ── Observar y aprender ───────────────────────────
        r ← JALAR(A)                             # recibir recompensa del brazo A
        N[A] ← N[A] + 1
        Q[A] ← Q[A] + (r − Q[A]) / N[A]         # [P5] actualización incremental de la media

    retornar Q, N
```

Notar lo simple que es: solo 5 líneas esenciales (marcadas `[P1]`–`[P5]`). No hay hiperparámetros complicados, no hay distribuciones, no hay cálculos de confianza. Solo un coin flip y una media.

---

## Traza manual: Problema Canónico A (Bernoulli, seed=7, ε=0.1)

**¿Por qué $\hat{\mu}$ empieza en 0?** Inicializamos $Q[i] = 0$ porque no tenemos ninguna observación. La media de cero muestras no está definida, así que 0 es un valor convencional de "no sé nada". Podríamos inicializar en 0.5 (máxima entropía para Bernoulli) o en 1.0 (optimista), pero **no importa**: la primera vez que jalamos un brazo, la fórmula incremental da $Q[i] = 0 + (r - 0)/1 = r$, sobrescribiendo completamente la inicialización. Lo único que afecta $Q[i] = 0$ es el desempate en argmax antes de tener datos: con todos en 0, argmax siempre elige el primer brazo. Pero si la primera ronda es exploración (como aquí), la inicialización ni siquiera se usa.

Veamos exactamente qué hace ε-greedy en las primeras 10 rondas:

| $t$ | $\varepsilon$-flip | $A_t$ | $r_t$ | $\hat{\mu}_A$ | $\hat{\mu}_B$ | $\hat{\mu}_C$ | $N_A$ | $N_B$ | $N_C$ | $R_t$ |
|:---:|:---------:|:------:|:------:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:------:|
| 1 | **explore** | B | 1 | 0.000 | 1.000 | 0.000 | 0 | 1 | 0 | 0.2 |
| 2 | exploit | B | 1 | 0.000 | 1.000 | 0.000 | 0 | 2 | 0 | 0.4 |
| 3 | exploit | B | 1 | 0.000 | 1.000 | 0.000 | 0 | 3 | 0 | 0.6 |
| 4 | **explore** | C | 1 | 0.000 | 1.000 | 1.000 | 0 | 3 | 1 | 0.6 |
| 5 | exploit | B | 0 | 0.000 | 0.750 | 1.000 | 0 | 4 | 1 | 0.8 |
| 6 | exploit | C | 1 | 0.000 | 0.750 | 1.000 | 0 | 4 | 2 | 0.8 |
| 7 | **explore** | C | 1 | 0.000 | 0.750 | 1.000 | 0 | 4 | 3 | 0.8 |
| 8 | exploit | C | 1 | 0.000 | 0.750 | 1.000 | 0 | 4 | 4 | 0.8 |
| 9 | exploit | C | 1 | 0.000 | 0.750 | 1.000 | 0 | 4 | 5 | 0.8 |
| 10 | exploit | C | 1 | 0.000 | 0.750 | 1.000 | 0 | 4 | 6 | 0.8 |

**Observaciones**:
- En $t=1$: la moneda dice "explorar" y elige B al azar. B obtiene $r=1$ → $\hat{\mu}_B = 1.0$, así que ε-greedy se **fija** en B
- En $t=2{-}3$: B sigue siendo explotado ($\hat{\mu}_B = 1.0$) y sigue ganando. Aunque B no es el mejor brazo ($\mu_B = 0.5$), tiene suerte inicial
- En $t=4$: la moneda dice "explorar" y elige C al azar. C obtiene $r=1$ → ahora $\hat{\mu}_C = 1.0 = \hat{\mu}_B$, empatados
- En $t=5$: exploit elige B (desempate por índice). B fracasa ($r=0$) → $\hat{\mu}_B = 0.75 < \hat{\mu}_C = 1.0$, así que C toma el control
- En $t=6{-}10$: C domina la explotación. En $t=7$ cae otra exploración que por azar elige C — ¡exploración desperdiciada en el brazo que ya estaba explotando!
- El brazo A ($\mu_A = 0.3$, el peor) **nunca ha sido jalado** en 10 rondas — en este caso es bueno. Pero si A fuera el mejor, ε-greedy nunca lo descubriría
- Moraleja: la exploración es **ciega** — no se dirige hacia brazos con alta incertidumbre, sino que elige al azar. Incluso puede "explorar" un brazo que ya conoce bien ($t=7$)

---

## Esquemas de decaimiento de ε

El ε constante tiene un problema fundamental: **nunca deja de explorar**. Incluso en $t=10{,}000$, sigue jalando brazos malos con probabilidad $\varepsilon$. Existen tres estrategias comunes:

| Variante | Fórmula | Regret | Propiedad |
|----------|---------|--------|-----------|
| Constante | $\varepsilon_t = \varepsilon$ | $O(\varepsilon T)$ — lineal | Nunca converge; explora para siempre |
| Decaimiento lineal | $\varepsilon_t = \varepsilon_0 \left(1 - \frac{t}{T}\right)$ | Sublineal si se ajusta bien | Requiere conocer $T$ de antemano |
| Decaimiento $1/t$ | $\varepsilon_t = \frac{c}{c + t}$ | $O(\sqrt{T})$ | Automático; no necesita $T$; $c > 0$ controla qué tan rápido decae (e.g. $c = 10$) |

### Derivación del regret con ε constante

Queremos responder: ¿cuánto regret acumula ε-greedy después de $T$ rondas? La respuesta tiene dos partes: un costo que **nunca desaparece** (exploración perpetua) y un costo **transitorio** (errores iniciales). Vamos paso a paso.

#### Paso 1: punto de partida

Usamos la descomposición por brazo de la sección 17.1. El regret acumulado $R_T$ (el mismo que definimos antes: la suma de las brechas por cada pull subóptimo) se escribe como:

$$R_T = \sum_{i=1}^{K} \Delta_i \cdot N_i(T)$$

donde $\Delta_i = \mu^{∗} - \mu_i$ es la brecha del brazo $i$ y $N_i(T)$ es cuántas veces lo jalamos en $T$ rondas (el mismo $N_i$ del pseudocódigo y la traza). Tomando valor esperado $\mathbb{E}[\cdot]$ sobre la aleatoriedad de las recompensas y las decisiones del algoritmo:

$$\mathbb{E}[R_T] = \sum_{i=1}^{K} \Delta_i \cdot \mathbb{E}[N_i(T)]$$

El brazo óptimo $i^{∗}$ tiene $\Delta_{i^{∗}} = 0$, así que solo contribuyen los brazos subóptimos. Nuestro objetivo se reduce a acotar $\mathbb{E}[N_i(T)]$ para cada brazo subóptimo $i$.

#### Paso 2: ¿por qué jalamos un brazo subóptimo?

En cada ronda, hay exactamente dos razones por las que ε-greedy jala un brazo subóptimo $i$:

1. **Exploración**: con probabilidad $\varepsilon$, el algoritmo explora y elige un brazo uniformemente al azar. La probabilidad de caer en $i$ es $1/K$. Esto ocurre **sin importar** cuánto sepamos sobre $i$ — es exploración ciega.

2. **Explotación errónea**: con probabilidad $1-\varepsilon$, el algoritmo explota (elige el brazo con mayor estimación). Si nuestra estimación del brazo $i$ es incorrectamente más alta que la del brazo óptimo, explotará el brazo equivocado. Esto solo ocurre al inicio, cuando tenemos pocas observaciones.

Separamos el conteo en estas dos contribuciones. Llamamos "pulls por exploración" a los del caso 1 y "pulls por error" a los del caso 2.

#### Paso 3: contar los pulls por exploración

Esto es directo. En cada ronda, la probabilidad de explorar **y** caer en el brazo $i$ es:

$$P(\text{explorar y elegir } i) = \varepsilon \cdot \frac{1}{K} = \frac{\varepsilon}{K}$$

En $T$ rondas independientes, el número esperado de pulls por exploración es:

$$\mathbb{E}[\text{pulls exploración de } i] = \frac{\varepsilon}{K} \cdot T$$

Este término crece **linealmente** con $T$. No importa cuánto sepamos sobre $i$: aunque tengamos 10,000 observaciones confirmando que $i$ es pésimo, ε-greedy sigue jalándolo con probabilidad $\varepsilon/K$ cada ronda.

#### Paso 4: contar los pulls por explotación errónea

Explotamos el brazo $i$ erróneamente cuando su estimación supera la del brazo óptimo. ¿Cuándo puede pasar esto?

La media muestral $\hat\mu$ de un brazo fluctúa alrededor de su media real $\mu$. Cada recompensa individual tiene una desviación estándar $\sigma$ (para Bernoulli con parámetro $p$, es $\sigma = \sqrt{p(1-p)} \leq 1/2$). Después de $n$ observaciones, la desviación estándar del **estimador** $\hat\mu$ (no de cada recompensa, sino del promedio) es $\sigma / \sqrt{n}$ — se reduce con más datos. Para que la estimación del brazo $i$ supere la del óptimo, esta fluctuación del estimador debe cubrir la brecha $\Delta_i$:

$$\frac{\sigma}{\sqrt{n}} \gtrsim \Delta_i \implies n \lesssim \frac{\sigma^2}{\Delta_i^2}$$

Es decir, después de aproximadamente $n^{∗} \sim 1/\Delta_i^2$ observaciones del brazo $i$, la estimación es suficientemente precisa y la explotación errónea se detiene.

Pero las observaciones de $i$ no llegan en cada ronda — solo cuando lo jalamos. Lo jalamos por exploración con frecuencia $\varepsilon/K$ por ronda. Así que necesitamos del orden de:

$$\frac{n^{∗}}{\varepsilon / K} = \frac{K}{\varepsilon \,\Delta_i^2} \text{ rondas}$$

para acumular las $n^{∗}$ observaciones necesarias. Durante esas rondas, podemos estar explotando $i$ erróneamente, acumulando a lo más ese mismo número de pulls adicionales:

$$\mathbb{E}[\text{pulls error de } i] \leq \frac{K}{\varepsilon \,\Delta_i^2}$$

Este término es **constante** — no crece con $T$. Es un costo transitorio que se paga al inicio.

#### Paso 5: juntar las piezas

Sumando ambas contribuciones para el brazo $i$:

$$\mathbb{E}[N_i(T)] \leq \frac{\varepsilon T}{K} + \frac{K}{\varepsilon \,\Delta_i^2}$$

Sustituyendo en la descomposición del regret:

$$\mathbb{E}[R_T] = \sum_{i:\,\Delta_i > 0} \Delta_i \cdot \mathbb{E}[N_i(T)] \leq \sum_{i:\,\Delta_i > 0} \Delta_i \left(\frac{\varepsilon T}{K} + \frac{K}{\varepsilon \,\Delta_i^2}\right)$$

Distribuyendo la suma y simplificando ($\Delta_i \cdot 1/\Delta_i^2 = 1/\Delta_i$):

$$\mathbb{E}[R_T] \leq \frac{\varepsilon T}{K} \sum_{i:\,\Delta_i > 0} \Delta_i \;+\; \frac{K}{\varepsilon} \sum_{i:\,\Delta_i > 0} \frac{1}{\Delta_i}$$

El primer sumando (exploración perpetua) es proporcional a $T$ — crece para siempre. El segundo (errores iniciales) es constante respecto a $T$ — se paga una vez. Las sumas solo dependen del problema (los valores de $\Delta_i$), no de $T$ ni de $\varepsilon$, así que en notación asintótica:

$$\boxed{\mathbb{E}[R_T] = O\left(\varepsilon T + \frac{K}{\varepsilon}\right)}$$

#### Paso 6: ¿qué nos dice esta cota?

Para $\varepsilon$ **fijo** (por ejemplo, $\varepsilon = 0.1$), el término $\varepsilon T$ domina conforme $T \to \infty$. El regret crece **linealmente**: $\mathbb{E}[R_T] \sim 0.1 \cdot T$. Esto es fundamentalmente peor que la cota de Lai-Robbins $\Omega(\log T)$.

¿Podemos elegir $\varepsilon$ óptimamente? Sí, minimizando $\varepsilon T + K/\varepsilon$ respecto a $\varepsilon$. Derivando e igualando a cero: $T - K/\varepsilon^2 = 0$, lo que da:

$$\varepsilon^{∗} = \sqrt{\frac{K}{T}} \implies \mathbb{E}[R_T] = O(\sqrt{KT})$$

Pero esto requiere conocer $T$ de antemano. Y aún así, $O(\sqrt{T})$ es mucho peor que $O(\log T)$.

La siguiente gráfica muestra el regret empírico de ε-greedy **simulado en nuestro Problema Canónico A** (Bernoulli, $\mu = 0.3, 0.5, 0.7$) para distintos valores de $\varepsilon$, promediado sobre 200 ejecuciones. No es una curva teórica general — es el comportamiento concreto para este problema, pero la forma lineal del regret es universal para $\varepsilon$ constante.

![Regret para distintos valores de ε]({{ '/17_multi_armed_bandits/images/07_egreedy_regret_by_epsilon.png' | url }})

---

## El defecto fundamental: exploración ciega

El problema de ε-greedy no es que explore — es que explora **sin criterio**. Cuando decide explorar, elige un brazo uniformemente al azar, sin considerar:

- ¿Cuántas veces ya hemos jalado ese brazo? (tal vez ya sabemos que es malo)
- ¿Cuánta incertidumbre tenemos sobre su media? (tal vez necesitamos más datos)
- ¿Cuánto podría mejorar nuestra situación? (tal vez su potencial es bajo)

![Selección de brazos de ε-greedy]({{ '/17_multi_armed_bandits/images/06_egreedy_arm_selection.png' | url }})

Observa cómo el brazo A (rojo) sigue apareciendo incluso después de $t=800$. Con $\hat{\mu}_A \approx 0.3$ y decenas de observaciones, ya sabemos con alta confianza que A es inferior. Pero ε-greedy sigue desperdiciando pulls en él.

![Distribución de pulls]({{ '/17_multi_armed_bandits/images/08_egreedy_pull_count.png' | url }})

En la sección siguiente veremos cómo **UCB1** resuelve este problema: en lugar de explorar a ciegas, explora donde hay más **incertidumbre**, dirigiendo la exploración hacia donde puede ser útil.

---

## Resumen

| Propiedad | ε-Greedy |
|-----------|----------|
| **Idea** | Con probabilidad ε, explorar al azar; sino, explotar |
| **Parámetros** | ε (sensible al ajuste) |
| **Regret (ε constante)** | $O(\varepsilon T)$ — lineal |
| **Regret (ε decreciente)** | $O(\sqrt{T})$ — sublineal pero no logarítmico |
| **Ventaja** | Extremadamente simple de implementar |
| **Desventaja** | Exploración ciega: no usa la información acumulada |
| **Cuándo usar** | Prototipo rápido, baseline de comparación |
