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

### Cota inferior: el regret es al menos lineal

Queremos demostrar que ε-greedy con $\varepsilon$ constante tiene regret **al menos** $\Omega(\varepsilon T)$. La prueba es corta y no requiere herramientas de concentración.

#### Paso 1: regret por ronda

El regret esperado en una ronda $t$ es:

$$\mathbb{E}[r_t] = \sum_{i=1}^{K} P(A_t = i) \cdot \Delta_i$$

donde $A_t$ es el brazo elegido en la ronda $t$, $\Delta_i = \mu^{∗} - \mu_i$ es la brecha del brazo $i$, y la suma pondera cada brecha por la probabilidad de elegir ese brazo.

#### Paso 2: cota inferior de la probabilidad de selección

En ε-greedy, la probabilidad de elegir el brazo $i$ tiene dos componentes:

$$P(A_t = i) = \underset{\text{exploración}}{\frac{\varepsilon}{K}} + \underset{\text{explotación}}{(1 - \varepsilon) \cdot \mathbf{1}[\hat\mu_i = \max_j \hat\mu_j]}$$

El segundo término es $0$ o $(1-\varepsilon)$ dependiendo de si el brazo $i$ tiene la estimación más alta en ese momento. Como este término es siempre $\geq 0$:

$$P(A_t = i) \geq \frac{\varepsilon}{K}$$

La desigualdad es estricta ($>$) para el brazo que la explotación elige, e igualdad ($=$) para los demás.

#### Paso 3: regret por ronda acotado inferiormente

Sustituyendo esta cota inferior en la expresión del regret por ronda:

$$\mathbb{E}[r_t] = \sum_{i=1}^{K} P(A_t = i) \cdot \Delta_i \geq \sum_{i=1}^{K} \frac{\varepsilon}{K} \cdot \Delta_i = \varepsilon \cdot \frac{1}{K}\sum_{i=1}^{K} \Delta_i = \varepsilon \cdot \bar\Delta$$

La desigualdad $\geq$ viene de reemplazar cada $P(A_t = i)$ por su cota inferior $\varepsilon/K$, descartando la probabilidad adicional que la explotación asigna a algún brazo. Definimos $\bar\Delta = \frac{1}{K}\sum_{i=1}^{K} \Delta_i$, la brecha promedio de todos los brazos (incluyendo el óptimo, que contribuye $\Delta_{i^{∗}} = 0$).

#### Paso 4: sumar sobre $T$ rondas

Como la cota vale para **toda** ronda $t$ (la exploración nunca se detiene), sumamos:

$$\mathbb{E}[R_T] = \sum_{t=1}^{T} \mathbb{E}[r_t] \geq \sum_{t=1}^{T} \varepsilon \cdot \bar\Delta = \varepsilon \cdot \bar\Delta \cdot T$$

Como $\varepsilon$ y $\bar\Delta$ son constantes independientes de $T$:

$$\boxed{\mathbb{E}[R_T] = \Omega(\varepsilon T)}$$

El regret crece **linealmente** con $T$. Esto es inevitable mientras $\varepsilon > 0$ sea constante: el algoritmo nunca deja de explorar, así que en cada ronda paga al menos $\varepsilon \cdot \bar\Delta$ de regret en expectativa. Para nuestro Problema Canónico A con $\varepsilon = 0.1$: $\bar\Delta = (0.4 + 0.2 + 0)/3 = 0.2$, así que $\mathbb{E}[R_T] \geq 0.02 \cdot T$.

> **Nota sobre cotas e igualdades.** Tanto la cota inferior como la superior parten de la misma expresión exacta $\mathbb{E}[R_T]$. La diferencia es la **dirección** en la que relajamos:
> - **Cota inferior**: reemplazamos términos por algo **menor** (descartamos la probabilidad de explotación) → obtenemos $\mathbb{E}[R_T] \geq f(T)$.
> - **Cota superior**: reemplazamos términos por algo **mayor** (acotamos los errores de explotación con Chebyshev) → obtenemos $\mathbb{E}[R_T] \leq g(T)$.
>
> Juntas, las dos cotas encierran el regret verdadero: $f(T) \leq \mathbb{E}[R_T] \leq g(T)$.

---

### Cota superior: el regret es $O(\varepsilon T)$

La cota inferior muestra que el regret es al menos lineal. Ahora queremos una **cota superior** que muestre que no crece más rápido que eso (salvo un término logarítmico despreciable). Esta cota requiere analizar cuántas veces el algoritmo explota un brazo subóptimo **por error**, lo que involucra una desigualdad de concentración.

#### Paso 1: descomposición del regret

Partimos de la descomposición por brazo (sección 17.1). Tanto $R_T$ como $N_i(T)$ son variables aleatorias (dependen de las recompensas y decisiones del algoritmo). Tomamos valor esperado:

$$\mathbb{E}[R_T] = \sum_{i=1}^{K} \Delta_i \cdot \mathbb{E}[N_i(T)]$$

donde $N_i(T)$ es el número de veces que jalamos el brazo $i$ en $T$ rondas (el mismo $N_i$ del pseudocódigo y la traza). El brazo óptimo tiene $\Delta_{i^{∗}} = 0$, así que solo contribuyen los subóptimos. Debemos acotar $\mathbb{E}[N_i(T)]$ para cada brazo con $\Delta_i > 0$.

#### Paso 2: dos fuentes de pulls subóptimos

En la ronda $t$, ε-greedy jala un brazo subóptimo $i$ por una de dos razones:

1. **Exploración**: con probabilidad $\varepsilon$, elige un brazo uniformemente en $\{1, \ldots, K\}$. Cae en $i$ con probabilidad $1/K$, independientemente del historial.

2. **Explotación errónea**: con probabilidad $1 - \varepsilon$, elige el brazo con mayor estimación. Si la estimación del brazo $i$ es incorrectamente más alta que la del óptimo, lo explotará por error.

Descomponemos $N_i(T)$ en estas dos contribuciones.

#### Paso 3: pulls por exploración

Definimos $X_t = 1$ si en la ronda $t$ el algoritmo explora y elige el brazo $i$, y $X_t = 0$ en caso contrario. Por la regla de ε-greedy:

$$P(X_t = 1) = \frac{\varepsilon}{K}$$

para toda ronda $t$, sin importar el historial. Por linealidad de la esperanza:

$$\mathbb{E}\left[\sum_{t=1}^{T} X_t\right] = \sum_{t=1}^{T} P(X_t = 1) = \frac{\varepsilon T}{K}$$

#### Paso 4: pulls por explotación errónea (Chebyshev)

Explotamos $i$ por error cuando su estimación supera la del brazo óptimo. ¿Cuántas veces puede ocurrir esto? Para responder necesitamos una herramienta de concentración.

**El estimador.** Después de jalar el brazo $i$ exactamente $n$ veces, observamos recompensas i.i.d. $r_1, \ldots, r_n$ con media $\mu_i$ y varianza $\sigma_i^2$. Para Bernoulli, $\sigma_i^2 = \mu_i(1-\mu_i)$. La media muestral es:

$$\hat\mu_i = \frac{1}{n}\sum_{j=1}^{n} r_j$$

Sus propiedades:

$$\mathbb{E}[\hat\mu_i] = \mu_i, \qquad \text{Var}(\hat\mu_i) = \frac{\sigma_i^2}{n}$$

El estimador es **insesgado** (en promedio da la media real) y su varianza decrece como $1/n$ (más observaciones → más precisión).

**Desigualdad de Chebyshev.** Para acotar la probabilidad de que el estimador se aleje de su media, usamos la desigualdad de Chebyshev. Esta es una cota universal que vale para **cualquier** variable aleatoria con varianza finita:

> **Chebyshev.** Sea $X$ una variable aleatoria con media $\mathbb{E}[X] = \mu$ y varianza $\text{Var}(X) = \sigma^2 < \infty$. Para todo $\delta > 0$:
>
> $$P(\lvert X - \mu \rvert \geq \delta) \leq \frac{\sigma^2}{\delta^2}$$

La intuición: si la varianza es pequeña relativa a $\delta^2$, es improbable que $X$ se aleje más de $\delta$ de su media. No asume nada sobre la forma de la distribución — solo necesita que la varianza exista.

**Aplicación a nuestro estimador.** Aplicamos Chebyshev al estimador $\hat\mu_i$ (que tiene varianza $\sigma_i^2/n$) con desviación $\delta = \Delta_i/2$:

$$P\left(\lvert \hat\mu_i - \mu_i \rvert \geq \frac{\Delta_i}{2}\right) \leq \frac{\sigma_i^2 / n}{(\Delta_i/2)^2} = \frac{4 \sigma_i^2}{n \cdot \Delta_i^2}$$

¿Por qué $\Delta_i/2$? Recordemos que $\mu^{∗} = \mu_i + \Delta_i$. Para que la explotación elija erróneamente el brazo $i$ sobre el óptimo, necesitamos $\hat\mu_i > \hat\mu^{∗}$. Esto puede ocurrir si **ambos** estimadores se desvían de sus medias reales: $\hat\mu_i$ sube y $\hat\mu^{∗}$ baja. Si cada uno se desvía a lo más $\Delta_i/2$, los estimadores se cruzan:

$$\hat\mu_i \leq \mu_i + \frac{\Delta_i}{2}, \quad \hat\mu^{∗} \geq \mu^{∗} - \frac{\Delta_i}{2} = \mu_i + \frac{\Delta_i}{2}$$

Entonces $\hat\mu_i \leq \hat\mu^{∗}$ y la explotación elige correctamente. Dicho al revés: para que haya error (es decir, que la explotación elija $i$ sobre el óptimo: $\hat\mu_i > \hat\mu^{∗}$), **al menos uno** de los estimadores debe desviarse en la dirección peligrosa — $\hat\mu_i$ hacia arriba o $\hat\mu^{∗}$ hacia abajo — por más de $\Delta_i/2$. Definimos $P(\text{error}) = P(\hat\mu_i > \hat\mu^{∗})$ y aplicamos la cota de la unión (union bound):

$$P(\hat\mu_i > \hat\mu^{∗}) \leq P\left(\hat\mu_i - \mu_i \geq \frac{\Delta_i}{2}\right) + P\left(\mu^{∗} - \hat\mu^{∗} \geq \frac{\Delta_i}{2}\right)$$

Cada probabilidad es **una cola** (one-tailed). Chebyshev es una cota de dos colas, pero como $P(X \geq \delta) \leq P(\lvert X \rvert \geq \delta)$, podemos aplicarlo para acotar cada término:

$$P(\text{error}) \leq \frac{4 \sigma_i^2}{n_i \cdot \Delta_i^2} + \frac{4 \sigma_{∗}^2}{n_{∗} \cdot \Delta_i^2}$$

donde $n_i$ y $n_{∗}$ son el número de observaciones de cada brazo. Ambos términos tienen la misma forma; para simplificar, usamos $\sigma^2 = \max_j \sigma_j^2$ y notamos que basta con que cada brazo tenga suficientes observaciones. El factor 2 de la unión no cambia el orden asintótico, así que trabajamos con un solo término.

**Conteo de explotaciones erróneas.** ¿Cuántas veces en total se explota erróneamente el brazo $i$? Llamemos $M_i$ a este número. Cada vez que explotamos $i$ por error, obtenemos una observación adicional de $i$, así que después de la $n$-ésima observación de $i$, la probabilidad de que la siguiente explotación elija $i$ es a lo más $\frac{4\sigma_i^2}{n \cdot \Delta_i^2}$ (por Chebyshev). Podemos acotar:

$$\mathbb{E}[M_i] \leq \sum_{n=1}^{\infty} P(\text{error tras } n \text{ observaciones}) \leq \sum_{n=1}^{n_i^{∗}} 1 + \sum_{n=n_i^{∗}+1}^{\infty} \frac{4\sigma_i^2}{n \cdot \Delta_i^2}$$

donde $n_i^{∗} = \left\lceil \frac{4\sigma_i^2}{\Delta_i^2} \right\rceil$ es el umbral donde la cota de Chebyshev baja de 1 (para $n \leq n_i^{∗}$, la cota excede 1 y no dice nada, así que acotamos trivialmente por 1). Para Bernoulli, $\sigma_i^2 \leq 1/4$, así que $n_i^{∗} \leq \lceil 1/\Delta_i^2 \rceil$.

El primer sumando es $n_i^{∗}$. Para el segundo, usamos $4\sigma_i^2/\Delta_i^2 \leq n_i^{∗}$:

$$\sum_{n=n_i^{∗}+1}^{\infty} \frac{n_i^{∗}}{n} \leq n_i^{∗} \int_{n_i^{∗}}^{\infty} \frac{dn}{n}$$

Esta integral diverge, pero en la práctica el brazo $i$ solo tiene a lo más $T$ observaciones, así que:

$$\sum_{n=n_i^{∗}+1}^{T} \frac{n_i^{∗}}{n} \leq n_i^{∗} \log\frac{T}{n_i^{∗}}$$

Entonces:

$$\mathbb{E}[M_i] \leq n_i^{∗} + n_i^{∗} \log\frac{T}{n_i^{∗}} = n_i^{∗}\left(1 + \log\frac{T}{n_i^{∗}}\right) = O\left(\frac{\log T}{\Delta_i^2}\right)$$

#### Paso 5: juntar las piezas

Sumando exploración y explotación errónea para cada brazo subóptimo $i$:

$$\mathbb{E}[N_i(T)] \leq \frac{\varepsilon T}{K} + \mathbb{E}[M_i] \leq \frac{\varepsilon T}{K} + O\left(\frac{\log T}{\Delta_i^2}\right)$$

Sustituyendo en la descomposición del regret:

$$\mathbb{E}[R_T] = \sum_{i:\Delta_i > 0} \Delta_i \cdot \mathbb{E}[N_i(T)] \leq \sum_{i:\Delta_i > 0} \Delta_i \left(\frac{\varepsilon T}{K} + O\left(\frac{\log T}{\Delta_i^2}\right)\right)$$

Distribuimos la suma. El primer término:

$$\frac{\varepsilon T}{K} \sum_{i:\Delta_i > 0} \Delta_i = \varepsilon \cdot \bar\Delta \cdot T$$

donde $\bar\Delta = \frac{1}{K}\sum_{i} \Delta_i$ es la brecha promedio. El segundo término usa $\Delta_i / \Delta_i^2 = 1/\Delta_i$:

$$O(\log T) \sum_{i:\Delta_i > 0} \frac{1}{\Delta_i} = O(H \log T)$$

donde $H = \sum_{i:\Delta_i > 0} 1/\Delta_i$ es la "dificultad" del problema (brazos con brecha pequeña contribuyen más). Entonces:

$$\mathbb{E}[R_T] \leq \varepsilon \cdot \bar\Delta \cdot T + O(H \log T)$$

Para $\varepsilon$ constante, el término $\varepsilon T$ es **lineal** y domina al término $O(\log T)$ conforme $T \to \infty$. Absorbiendo las constantes:

$$\boxed{\mathbb{E}[R_T] = O(\varepsilon T)}$$

El costo dominante es la **exploración perpetua**: en cada ronda, con probabilidad $\varepsilon$, el algoritmo elige un brazo al azar. Los errores de explotación (que crecen solo como $\log T$) son despreciables en comparación.

---

### Interpretación y ε óptimo

Juntando ambas cotas:

$$\varepsilon \cdot \bar\Delta \cdot T \leq \mathbb{E}[R_T] \leq \varepsilon \cdot \bar\Delta \cdot T + O(H \log T)$$

Para $\varepsilon$ **fijo** (por ejemplo, $\varepsilon = 0.1$), el término $\varepsilon T$ domina conforme $T \to \infty$ y el $O(\log T)$ es despreciable. El regret crece **linealmente** — $\Theta(\varepsilon T)$ — fundamentalmente peor que la cota de Lai-Robbins $\Omega(\log T)$.

¿Podemos mejorar eligiendo $\varepsilon$ como función de $T$? Si hacemos $\varepsilon = \varepsilon(T) \to 0$, el término de exploración $\varepsilon T$ disminuye, pero la exploración se vuelve más lenta y los errores de explotación tardan más en desaparecer. El esquema de decaimiento $\varepsilon_t = c/(c+t)$ (de la tabla anterior) logra $O(\sqrt{T})$, pero incluso esto es peor que $O(\log T)$ — ε-greedy, incluso optimizado, no alcanza la cota de Lai-Robbins.

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
