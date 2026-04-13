---
title: "Algoritmo Forward"
---

# Algoritmo Forward

> *Problema 1 — Evaluación: ¿Con qué probabilidad generó este modelo la secuencia $O$?*

---

## 1. ¿Por qué no es trivial?

La pregunta parece simple: calcular $P(O \mid \lambda)$. Pero para obtenerla necesitamos sumar sobre **todas las posibles secuencias de estados ocultos**:

$$P(O \mid \lambda) = \sum_{q_1} \sum_{q_2} \cdots \sum_{q_T} P(O, q_1, \ldots, q_T \mid \lambda)$$

donde cada término de la suma es la probabilidad conjunta de la sección 20.1:

$$P(O, q \mid \lambda) = \pi_{q_1} \cdot B_{q_1, O_1} \cdot A_{q_1, q_2} \cdot B_{q_2, O_2} \cdots A_{q_{T-1}, q_T} \cdot B_{q_T, O_T}$$

Con $N$ estados y $T$ pasos de tiempo, hay $N^T$ secuencias posibles — una suma de $N^T$ términos, cada uno con $T$ factores. Para el ejemplo de Lain ($N=2$, $T=3$) son $2^3 = 8$ términos — manejable. Pero con $N=10$ estados y $T=100$ pasos hay $10^{100}$ términos. Es imposible enumerarlos.

El algoritmo Forward evita esta explosión usando **programación dinámica**: observa que muchos de esos $N^T$ términos comparten factores comunes, y reutiliza los cálculos previos en lugar de repetirlos.

---

## 2. La variable forward $\alpha_t(i)$

Definimos la **variable forward** como:

$$\alpha_t(i) = P(O_1, O_2, \ldots, O_t,\; q_t = i \mid \lambda)$$

En palabras: $\alpha_t(i)$ es la probabilidad de haber observado las primeras $t$ observaciones **y** de encontrarse en el estado $i$ en el instante $t$, dado el modelo $\lambda$.

Intuición: $\alpha_t(i)$ acumula toda la "evidencia" de las observaciones pasadas ($O_1$ hasta $O_t$) y la concentra en un único número por estado. No necesitamos recordar cada trayectoria — solo el resumen numérico en el tiempo $t$.

---

## 3. Inicialización, recursión y terminación

El algoritmo tiene tres fases:

**[P1] Inicialización** ($t = 1$):

$$\alpha_1(i) = \pi_i \cdot B_{i,O_1} \qquad \text{para todo } i = 1, \ldots, N$$

Interpretación: la probabilidad de estar en el estado $i$ al inicio es $\pi_i$; la probabilidad de haber observado $O_1$ desde ese estado es $B_{i,O_1}$. El producto da la probabilidad conjunta.

**[P2] Recursión** ($t = 2, 3, \ldots, T$):

$$\alpha_t(j) = \left[\sum_{i=1}^{N} \alpha_{t-1}(i) \cdot A_{ij}\right] \cdot B_{j,O_t} \qquad \text{para todo } j = 1, \ldots, N$$

Interpretación: para llegar al estado $j$ en el instante $t$, necesitamos:
1. Haber llegado a algún estado $i$ en $t-1$ (eso cuesta $\alpha_{t-1}(i)$)
2. Haber transitado de $i$ a $j$ (eso cuesta $A_{ij}$)
3. Haber emitido la observación $O_t$ desde el estado $j$ (eso cuesta $B_{j,O_t}$)

Sumamos sobre todos los estados $i$ posibles (venimos de cualquier estado anterior).

**[P3] Terminación**:

$$P(O \mid \lambda) = \sum_{i=1}^{N} \alpha_T(i)$$

La probabilidad total de la secuencia es la suma de las variables forward en el último instante.

---

## 4. Visualización: el trellis forward

La estructura de cómputo se llama **trellis** (cuadrícula de enrejado). Cada nodo es un par (estado, tiempo); cada arista representa una transición posible.

```
Estado │  t=1          t=2            t=3
───────┼──────────────────────────────────────────
  S    │  α₁(S)=0.540  α₂(S)=0.041   α₃(S)=0.00959
       │    ↘↗            ↘↗
  R    │  α₁(R)=0.080  α₂(R)=0.168   α₃(R)=0.09048
       
  O_t  │   O₁=0         O₂=1          O₃=1
        ────────────────────────────────→  tiempo
```

Las flechas en cada columna representan: desde cada nodo en $t$, se contribuye a todos los nodos en $t+1$ mediante la transición $A_{ij}$, y luego se multiplica por la emisión del nuevo estado.

![Forward Trellis]({{ '/20_hmm/images/03_forward_trellis.png' | url }})

---

## 5. Traza completa: el ejemplo de Lain

Parámetros: $\pi = (0.6, 0.4)$, $O = (0, 1, 1)$

$$A = \begin{pmatrix} 0.7 & 0.3 \\ 0.4 & 0.6 \end{pmatrix}, \qquad B = \begin{pmatrix} 0.9 & 0.1 \\ 0.2 & 0.8 \end{pmatrix}$$

**Paso 1 — Inicialización** (observación $O_1 = 0$):

$$\alpha_1(S) = \pi_S \cdot B_{S,0} = 0.6 \times 0.9 = 0.540$$

$$\alpha_1(R) = \pi_R \cdot B_{R,0} = 0.4 \times 0.2 = 0.080$$

Intuición: el día 1 no llueve (O=0). Lain asigna alta probabilidad a "Soleado" porque: (a) es el estado inicial más probable y (b) cuando es soleado la probabilidad de no paraguas es 0.9.

**Paso 2 — Recursión** (observación $O_2 = 1$):

$$\alpha_2(S) = [\alpha_1(S) \cdot A_{SS} + \alpha_1(R) \cdot A_{RS}] \cdot B_{S,1}$$
$$= [0.540 \times 0.7 + 0.080 \times 0.4] \times 0.1 = [0.378 + 0.032] \times 0.1 = 0.041$$

$$\alpha_2(R) = [\alpha_1(S) \cdot A_{SR} + \alpha_1(R) \cdot A_{RR}] \cdot B_{R,1}$$
$$= [0.540 \times 0.3 + 0.080 \times 0.6] \times 0.8 = [0.162 + 0.048] \times 0.8 = 0.168$$

Intuición: el día 2 hay paraguas (O=1). Ahora "Lluvioso" toma ventaja: $\alpha_2(R) \gg \alpha_2(S)$.

**Paso 3 — Recursión** (observación $O_3 = 1$):

$$\alpha_3(S) = [\alpha_2(S) \cdot A_{SS} + \alpha_2(R) \cdot A_{RS}] \cdot B_{S,1}$$
$$= [0.041 \times 0.7 + 0.168 \times 0.4] \times 0.1 = [0.0287 + 0.0672] \times 0.1 = 0.00959$$

$$\alpha_3(R) = [\alpha_2(S) \cdot A_{SR} + \alpha_2(R) \cdot A_{RR}] \cdot B_{R,1}$$
$$= [0.041 \times 0.3 + 0.168 \times 0.6] \times 0.8 = [0.0123 + 0.1008] \times 0.8 = 0.09048$$

**Terminación:**

$$P(O \mid \lambda) = \alpha_3(S) + \alpha_3(R) = 0.00959 + 0.09048 = \mathbf{0.10007}$$

**Tabla resumen:**

| $t$ | $O_t$ | $\alpha_t(S)$ | $\alpha_t(R)$ | $\alpha_t(S) + \alpha_t(R)$ |
|:---:|:-----:|:-------------:|:-------------:|:---------------------------:|
| 1 | 0 | 0.54000 | 0.08000 | 0.62000 |
| 2 | 1 | 0.04100 | 0.16800 | 0.20900 |
| 3 | 1 | 0.00959 | 0.09048 | **0.10007** |

La columna de suma no tiene por qué ser 1 — los $\alpha_t$ son probabilidades **conjuntas** (de observación + estado), no condicionales. Solo en $t=T$ la suma da $P(O \mid \lambda)$.

---

## 6. Pseudocódigo

```
función FORWARD(O, π, A, B):
    T ← longitud(O)
    N ← número de estados

    [P1] Inicialización:
        para i = 1 hasta N:
            α[1][i] ← π[i] × B[i][O[1]]

    [P2] Recursión:
        para t = 2 hasta T:
            para j = 1 hasta N:
                α[t][j] ← 0
                para i = 1 hasta N:
                    α[t][j] ← α[t][j] + α[t-1][i] × A[i][j]
                α[t][j] ← α[t][j] × B[j][O[t]]

    [P3] Terminación:
        P_obs ← 0
        para i = 1 hasta N:
            P_obs ← P_obs + α[T][i]

    retornar α, P_obs
```

---

## 7. Complejidad

| Algoritmo | Complejidad temporal | Complejidad espacial |
|-----------|:--------------------:|:--------------------:|
| Ingenuo (enumerar todas las secuencias) | $O(N^T \cdot T)$ | $O(N^T)$ |
| Forward (programación dinámica) | $O(N^2 T)$ | $O(N T)$ |

El ahorro es exponencial: para $N=10$, $T=100$, el método ingenuo requiere $10^{102}$ operaciones; Forward solo $100{,}000$.

El costo viene del doble bucle: para cada uno de los $T$ pasos de tiempo, para cada uno de los $N$ estados destino, sumamos sobre los $N$ estados origen. Eso es $N \times N$ operaciones por paso → $N^2 T$ en total.
