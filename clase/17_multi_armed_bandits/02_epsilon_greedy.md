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

Queremos acotar $\mathbb{E}[R_T]$: el regret esperado de ε-greedy después de $T$ rondas. La derivación tiene dos ingredientes: un costo **permanente** (exploración que nunca se detiene) y un costo **transitorio** (errores de estimación al inicio).

#### Paso 1: descomposición del regret

Partimos de la descomposición por brazo (sección 17.1):

$$R_T = \sum_{i=1}^{K} \Delta_i \cdot N_i(T)$$

donde $\Delta_i = \mu^{∗} - \mu_i$ es la brecha del brazo $i$ y $N_i(T)$ es el número de veces que jalamos el brazo $i$ en $T$ rondas (el mismo $N_i$ del pseudocódigo y la traza). Tanto $R_T$ como $N_i(T)$ son variables aleatorias — dependen de las recompensas observadas y de las decisiones del algoritmo. Tomamos valor esperado:

$$\mathbb{E}[R_T] = \sum_{i=1}^{K} \Delta_i \cdot \mathbb{E}[N_i(T)]$$

El brazo óptimo tiene $\Delta_{i^{∗}} = 0$, así que la suma se reduce a los brazos subóptimos ($\Delta_i > 0$). Nuestro problema se reduce a acotar $\mathbb{E}[N_i(T)]$ para cada uno de ellos.

#### Paso 2: dos fuentes de pulls subóptimos

Sea $i$ un brazo subóptimo. En la ronda $t$, ε-greedy lo jala por una de dos razones:

1. **Exploración**: con probabilidad $\varepsilon$, el algoritmo ignora sus estimaciones y elige un brazo uniformemente en $\{1, \ldots, K\}$. Cae en $i$ con probabilidad $1/K$, independientemente del historial.

2. **Explotación errónea**: con probabilidad $1 - \varepsilon$, el algoritmo elige $\arg\max_j \hat\mu_j$. Si la estimación del brazo $i$ es mayor que la del brazo óptimo, lo explotará por error. Esto solo puede ocurrir cuando las estimaciones son imprecisas.

Descomponemos $N_i(T)$ en estas dos contribuciones y acotamos cada una.

#### Paso 3: pulls por exploración

Definimos la variable indicadora $X_t = 1$ si en la ronda $t$ el algoritmo explora y elige el brazo $i$, y $X_t = 0$ en caso contrario. Por la regla de ε-greedy:

$$P(X_t = 1) = \varepsilon \cdot \frac{1}{K} = \frac{\varepsilon}{K}$$

para toda ronda $t$, sin importar el historial. El número total de pulls de $i$ por exploración en $T$ rondas es $\sum_{t=1}^{T} X_t$. Por linealidad de la esperanza:

$$\mathbb{E}\left[\sum_{t=1}^{T} X_t\right] = \sum_{t=1}^{T} P(X_t = 1) = \frac{\varepsilon T}{K}$$

Este término crece **linealmente** con $T$. No importa cuánto sepamos sobre $i$ — ε-greedy sigue jalándolo con probabilidad $\varepsilon/K$ en cada ronda, para siempre.

#### Paso 4: pulls por explotación errónea

Esta es la parte que requiere más cuidado. Explotamos $i$ erróneamente en la ronda $t$ cuando la estimación del brazo $i$ supera la del brazo óptimo. ¿Cuántas rondas puede durar esto?

**El estimador.** Después de jalar el brazo $i$ exactamente $n$ veces, nuestra estimación es la media muestral:

$$\hat\mu_i = \frac{1}{n}\sum_{j=1}^{n} r_j$$

donde $r_1, \ldots, r_n$ son las recompensas observadas del brazo $i$. Como las recompensas son i.i.d. con media $\mu_i$ y varianza $\sigma_i^2$ (para Bernoulli, $\sigma_i^2 = \mu_i(1-\mu_i)$), la esperanza y varianza del estimador son:

$$\mathbb{E}[\hat\mu_i] = \mu_i, \qquad \text{Var}(\hat\mu_i) = \frac{\sigma_i^2}{n}$$

La desviación estándar del estimador es $\sigma_i / \sqrt{n}$: esta es la escala típica de las fluctuaciones de $\hat\mu_i$ alrededor de $\mu_i$.

**Condición de error.** La explotación errónea de $i$ ocurre cuando $\hat\mu_i \geq \hat\mu_{i^{∗}}$, es decir, cuando la estimación del brazo subóptimo supera la del óptimo. ¿Cuándo es esto probable?

Escribimos la condición como:

$$\hat\mu_i - \mu_i \geq \hat\mu_{i^{∗}} - \mu_{i^{∗}} + \Delta_i$$

El lado izquierdo es la fluctuación del estimador de $i$ (escala $\sim \sigma_i/\sqrt{n_i}$). El lado derecho incluye la brecha $\Delta_i$ más la fluctuación del estimador del óptimo (escala $\sim \sigma_{i^{∗}}/\sqrt{n_{i^{∗}}}$). Para que la desigualdad se cumpla, las fluctuaciones deben **cubrir la brecha** $\Delta_i$.

**Concentración.** Por la desigualdad de Chebyshev, la probabilidad de que $\hat\mu_i$ se desvíe más de $\delta$ de su media real es:

$$P(\lvert \hat\mu_i - \mu_i \rvert \geq \delta) \leq \frac{\sigma_i^2}{n \,\delta^2}$$

Tomando $\delta = \Delta_i / 2$ (la mitad de la brecha), la probabilidad de que la estimación de $i$ sea engañosamente alta es:

$$P\!\left(\hat\mu_i - \mu_i \geq \frac{\Delta_i}{2}\right) \leq \frac{4\,\sigma_i^2}{n \,\Delta_i^2}$$

Esta probabilidad se vuelve pequeña cuando $n$ es grande. Concretamente, cuando:

$$n \geq \frac{4\,\sigma_i^2}{\Delta_i^2}$$

la probabilidad de error es menor que 1, y decae como $1/n$ conforme seguimos acumulando datos. Definimos el umbral:

$$n_i^{∗} = \left\lceil \frac{4\,\sigma_i^2}{\Delta_i^2} \right\rceil$$

Después de $n_i^{∗}$ observaciones de $i$, la explotación errónea se vuelve improbable. Para Bernoulli, $\sigma_i^2 \leq 1/4$, así que $n_i^{∗} \leq \lceil 1/\Delta_i^2 \rceil$.

**Velocidad de acumulación.** Pero las observaciones del brazo $i$ no llegan en cada ronda — solo cuando lo jalamos. En las rondas donde no explotamos $i$ erróneamente (que eventualmente son la mayoría), solo lo jalamos por exploración, con frecuencia $\varepsilon/K$ por ronda. Necesitamos del orden de:

$$\frac{n_i^{∗}}{\varepsilon/K} = \frac{K \,n_i^{∗}}{\varepsilon} \leq \frac{K}{\varepsilon\,\Delta_i^2}$$

rondas para acumular las $n_i^{∗}$ observaciones que extinguen el error. Cada una de esas rondas puede contribuir un pull erróneo de $i$, así que:

$$\mathbb{E}[\text{pulls por error de } i] \leq \frac{K}{\varepsilon\,\Delta_i^2}$$

Este término es **constante** respecto a $T$ — es un costo que se paga una vez al inicio y no vuelve a crecer.

#### Paso 5: juntar las piezas

Sumando las dos contribuciones para cada brazo subóptimo $i$:

$$\mathbb{E}[N_i(T)] \leq \frac{\varepsilon T}{K} + \frac{K}{\varepsilon\,\Delta_i^2}$$

Sustituyendo en la descomposición del regret:

$$\mathbb{E}[R_T] = \sum_{i:\,\Delta_i > 0} \Delta_i \cdot \mathbb{E}[N_i(T)] \leq \sum_{i:\,\Delta_i > 0} \Delta_i \left(\frac{\varepsilon T}{K} + \frac{K}{\varepsilon\,\Delta_i^2}\right)$$

Distribuimos la suma. El primer término da:

$$\frac{\varepsilon T}{K} \sum_{i:\,\Delta_i > 0} \Delta_i$$

El segundo término usa $\Delta_i \cdot 1/\Delta_i^2 = 1/\Delta_i$:

$$\frac{K}{\varepsilon} \sum_{i:\,\Delta_i > 0} \frac{1}{\Delta_i}$$

Ambas sumas solo dependen del problema (los valores de $\Delta_i$, que son constantes fijas), no de $T$ ni de $\varepsilon$. Definimos las constantes del problema:

$$\bar\Delta = \frac{1}{K}\sum_{i:\,\Delta_i > 0} \Delta_i, \qquad H = \sum_{i:\,\Delta_i > 0} \frac{1}{\Delta_i}$$

Entonces:

$$\mathbb{E}[R_T] \leq \varepsilon\,\bar\Delta\, T + \frac{K\,H}{\varepsilon}$$

En notación asintótica, absorbiendo las constantes del problema:

$$\boxed{\mathbb{E}[R_T] = O\!\left(\varepsilon T + \frac{K}{\varepsilon}\right)}$$

El primer término es el **costo de la exploración perpetua**: crece linealmente con $T$ porque ε-greedy nunca deja de explorar. El segundo es el **costo de los errores iniciales**: constante, se paga una vez mientras las estimaciones son imprecisas.

#### Paso 6: interpretación y ε óptimo

Para $\varepsilon$ **fijo** (por ejemplo, $\varepsilon = 0.1$), el término $\varepsilon T$ domina conforme $T \to \infty$. El regret crece **linealmente** — fundamentalmente peor que la cota de Lai-Robbins $\Omega(\log T)$.

¿Podemos optimizar $\varepsilon$? Sí. Minimizamos $f(\varepsilon) = \varepsilon T + K/\varepsilon$:

$$f'(\varepsilon) = T - \frac{K}{\varepsilon^2} = 0 \implies \varepsilon^{∗} = \sqrt{\frac{K}{T}}$$

Sustituyendo:

$$f(\varepsilon^{∗}) = \sqrt{KT} + \sqrt{KT} = 2\sqrt{KT}$$

$$\implies \mathbb{E}[R_T] = O(\sqrt{KT})$$

Pero esto requiere conocer $T$ de antemano. Y aun así, $O(\sqrt{T})$ es mucho peor que $O(\log T)$ — ε-greedy, incluso optimizado, no alcanza la cota de Lai-Robbins.

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
