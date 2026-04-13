---
title: "Algoritmo Backward"
---

# Algoritmo Backward

> *Si Forward mira al pasado, Backward mira al futuro. Juntos, ven todo.*

---

## 1. Motivación: ¿qué le falta al algoritmo Forward?

El algoritmo Forward calcula $\alpha_t(i) = P(O_1, \ldots, O_t, q_t = i \mid \lambda)$: la probabilidad de haber visto las observaciones **hasta** el instante $t$ y de estar en el estado $i$.

Pero hay preguntas que Forward no puede responder eficientemente por sí solo. Por ejemplo: dado el modelo y **toda** la secuencia observada, ¿cuál es la probabilidad de estar en el estado $i$ en el instante $t$? Esa pregunta requiere información de las observaciones **futuras** ($O_{t+1}, \ldots, O_T$), que Forward no tiene.

El algoritmo Backward calcula exactamente esa información futura.

---

## 2. La variable backward $\beta_t(i)$

Definimos la **variable backward** como:

$$\beta_t(i) = P(O_{t+1}, O_{t+2}, \ldots, O_T \mid q_t = i,\; \lambda)$$

En palabras: $\beta_t(i)$ es la probabilidad de observar el **resto** de la secuencia ($O_{t+1}$ en adelante), dado que en el instante $t$ estamos en el estado $i$.

Mientras $\alpha_t(i)$ acumula información **desde el pasado hacia $t$**, $\beta_t(i)$ acumula información **desde el futuro hacia $t$**. Se procesan en sentido contrario: de derecha a izquierda en el trellis.

---

## 3. Inicialización, recursión y terminación

**[P1] Inicialización** ($t = T$):

$$\beta_T(i) = 1 \qquad \text{para todo } i = 1, \ldots, N$$

Interpretación: en el último instante no hay observaciones futuras que considerar — la probabilidad de "la secuencia vacía de observaciones futuras" es 1.

**[P2] Recursión** ($t = T-1, T-2, \ldots, 1$):

$$\beta_t(i) = \sum_{j=1}^{N} A_{ij} \cdot B_{j,O_{t+1}} \cdot \beta_{t+1}(j) \qquad \text{para todo } i = 1, \ldots, N$$

Interpretación: para que el futuro sea consistente estando en el estado $i$ en $t$, necesitamos:
1. Transitar de $i$ a algún estado $j$ en $t+1$ (cuesta $A_{ij}$)
2. Emitir la observación $O_{t+1}$ desde el estado $j$ (cuesta $B_{j,O_{t+1}}$)
3. Que el futuro restante sea consistente desde $j$ en $t+1$ (eso es $\beta_{t+1}(j)$)

Sumamos sobre todos los estados $j$ posibles.

**[P3] Terminación** — verificación cruzada:

$$P(O \mid \lambda) = \sum_{i=1}^{N} \pi_i \cdot B_{i,O_1} \cdot \beta_1(i)$$

Esta fórmula debe dar el mismo resultado que el algoritmo Forward. Si coincide, ambos están correctos.

---

## 4. Visualización: el trellis backward

```
Estado │  t=1          t=2          t=3
───────┼──────────────────────────────────────
  S    │  β₁(S)=0.1465  β₂(S)=0.31  β₃(S)=1.0
       │              ↖↗
  R    │  β₁(R)=0.2620  β₂(R)=0.52  β₃(R)=1.0

  O_t  │   O₁=0         O₂=1         O₃=1
        ──────────────────────────────────→  tiempo
        ←────────────────────────────── sentido del cómputo
```

Las flechas van de derecha a izquierda. Empezamos en $t=T$ (todos los $\beta$ son 1) y propagamos hacia $t=1$.

![Backward Trellis]({{ '/20_hmm/images/04_backward_trellis.png' | url }})

---

## 5. Traza completa: el ejemplo de Lain

Parámetros: $O = (0, 1, 1)$

$$A = \begin{pmatrix}
0.7 & 0.3 \\
0.4 & 0.6
\end{pmatrix}, \qquad B = \begin{pmatrix}
0.9 & 0.1 \\
0.2 & 0.8
\end{pmatrix}$$

**Paso 1 — Inicialización** ($t=3$):

$$\beta_3(S) = 1.0, \qquad \beta_3(R) = 1.0$$

**Paso 2 — Recursión** ($t=2$, observación futura $O_3 = 1$):

$$\beta_2(S) = A_{SS} \cdot B_{S,1} \cdot \beta_3(S) + A_{SR} \cdot B_{R,1} \cdot \beta_3(R)$$
$$= 0.7 \times 0.1 \times 1.0 + 0.3 \times 0.8 \times 1.0 = 0.07 + 0.24 = 0.310$$

$$\beta_2(R) = A_{RS} \cdot B_{S,1} \cdot \beta_3(S) + A_{RR} \cdot B_{R,1} \cdot \beta_3(R)$$
$$= 0.4 \times 0.1 \times 1.0 + 0.6 \times 0.8 \times 1.0 = 0.04 + 0.48 = 0.520$$

**Paso 3 — Recursión** ($t=1$, observación futura $O_2 = 1$):

$$\beta_1(S) = A_{SS} \cdot B_{S,1} \cdot \beta_2(S) + A_{SR} \cdot B_{R,1} \cdot \beta_2(R)$$
$$= 0.7 \times 0.1 \times 0.31 + 0.3 \times 0.8 \times 0.52 = 0.0217 + 0.1248 = 0.1465$$

$$\beta_1(R) = A_{RS} \cdot B_{S,1} \cdot \beta_2(S) + A_{RR} \cdot B_{R,1} \cdot \beta_2(R)$$
$$= 0.4 \times 0.1 \times 0.31 + 0.6 \times 0.8 \times 0.52 = 0.0124 + 0.2496 = 0.2620$$

**Verificación cruzada** (debe coincidir con Forward):

$$P(O \mid \lambda) = \pi_S \cdot B_{S,0} \cdot \beta_1(S) + \pi_R \cdot B_{R,0} \cdot \beta_1(R)$$
$$= 0.6 \times 0.9 \times 0.1465 + 0.4 \times 0.2 \times 0.2620$$
$$= 0.07911 + 0.02096 = \mathbf{0.10007} \checkmark$$

El resultado coincide exactamente con el Forward. Ambos algoritmos son correctos.

**Tabla resumen de $\beta$:**

| $t$ | $O_t$ | $\beta_t(S)$ | $\beta_t(R)$ |
|:---:|:-----:|:------------:|:------------:|
| 1 | 0 | 0.1465 | 0.2620 |
| 2 | 1 | 0.3100 | 0.5200 |
| 3 | 1 | 1.0000 | 1.0000 |

---

## 6. Pseudocódigo

```
función BACKWARD(O, A, B):
    T ← longitud(O)
    N ← número de estados

    [P1] Inicialización:
        para i = 1 hasta N:
            β[T][i] ← 1

    [P2] Recursión (de derecha a izquierda):
        para t = T-1 hasta 1:
            para i = 1 hasta N:
                β[t][i] ← 0
                para j = 1 hasta N:
                    β[t][i] ← β[t][i] + A[i][j] × B[j][O[t+1]] × β[t+1][j]

    [P3] Terminación (verificación):
        P_obs ← 0
        para i = 1 hasta N:
            P_obs ← P_obs + π[i] × B[i][O[1]] × β[1][i]

    retornar β, P_obs
```

---

## 7. Combinando Forward y Backward: la posterior $\gamma_t(i)$

La razón principal de calcular $\beta$ es poder combinarla con $\alpha$ para obtener la **probabilidad posterior** de cada estado:

$$\gamma_t(i) = P(q_t = i \mid O,\; \lambda) = \frac{\alpha_t(i) \cdot \beta_t(i)}{P(O \mid \lambda)}$$

En palabras: la probabilidad de estar en el estado $i$ en el instante $t$, dado que **hemos observado toda la secuencia** $O$, es proporcional al producto de la información pasada ($\alpha$) y la información futura ($\beta$). Dividimos por $P(O \mid \lambda)$ para normalizar.

Para el ejemplo de Lain:

| $t$ | $\gamma_t(S)$ | $\gamma_t(R)$ | Interpretación |
|:---:|:-------------:|:-------------:|----------------|
| 1 | $\frac{0.540 \times 0.1465}{0.10007} = 0.791$ | 0.209 | Día 1: probablemente soleado (O=0 confirma) |
| 2 | $\frac{0.041 \times 0.310}{0.10007} = 0.127$ | 0.873 | Día 2: probablemente lluvioso (O=1 confirma) |
| 3 | $\frac{0.00959 \times 1.0}{0.10007} = 0.096$ | 0.904 | Día 3: muy probablemente lluvioso (O=1 confirma) |

Notar que $\gamma_t(S) + \gamma_t(R) = 1$ para todo $t$ — son probabilidades condicionales correctamente normalizadas.

![Forward vs Backward]({{ '/20_hmm/images/05_forward_vs_backward.png' | url }})

![Posteriors Gamma]({{ '/20_hmm/images/06_gamma_posteriors.png' | url }})

---

## 8. Forward vs Backward: comparación

| Aspecto | Forward $\alpha_t(i)$ | Backward $\beta_t(i)$ |
|---------|:--------------------:|:--------------------:|
| Define | $P(O_1 \ldots O_t,\; q_t=i \mid \lambda)$ | $P(O_{t+1} \ldots O_T \mid q_t=i,\; \lambda)$ |
| Dirección | Izquierda → derecha | Derecha → izquierda |
| Inicialización | $\alpha_1(i) = \pi_i \cdot B_{i,O_1}$ | $\beta_T(i) = 1$ |
| ¿Solo bastante? | Sí, para $P(O \mid \lambda)$ | No solo (necesita $\pi$ y $B$ para terminar) |
| Uso principal | Evaluación | Posteriors $\gamma$ (con Forward) |
| ¿Cuándo usar los dos? | Para Baum-Welch y para calcular $\gamma_t(i)$ | Siempre junto con Forward |
| Complejidad | $O(N^2 T)$ | $O(N^2 T)$ |

**Regla práctica:** Si solo necesitas $P(O \mid \lambda)$, usa Forward solo. Si necesitas los posteriors $\gamma_t(i)$ (para saber cuándo es más probable cada estado), necesitas ambos.
