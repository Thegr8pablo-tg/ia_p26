---
title: "02 · On-policy vs Off-policy"
summary: "La tabla Q como objeto concreto, el error TD, las dos ecuaciones de Bellman y la bifurcación SARSA / Q-learning"
---

## La tabla $Q$ como objeto concreto

Antes de hablar de algoritmos, construyamos el objeto central: la **tabla $Q$**.

Es una matriz con un estado por fila y una acción por columna.
Cada celda responde: *"si estoy en $s$ y tomo $a$, ¿qué retorno total espero acumular hasta la meta?"*

Al principio no sabemos nada, así que inicializamos todo en cero:

![Tabla Q vacía]({{ '/23_reinforcement_learning/images/03_q_table_empty.png' | url }})

Para la escalera: 5 filas (estados 0–4; el estado 5 es terminal y no necesita acciones) y 2 columnas ($+1$ y $+2$).
La celda $(s=4, +2)$ está marcada como no disponible porque desde $s=4$ la única acción posible es $+1$.

Con cada episodio que juega el agente, algunas celdas se actualizan.
Después de suficientes episodios, la tabla converge a $Q^{∗}$.

---

## El esqueleto de la actualización TD

La idea central de TD es simple: **compara lo que esperabas con lo que realmente pasó, y ajusta**.

Formalmente, la actualización tiene esta estructura:

$$Q(s,a) \leftarrow Q(s,a) + \alpha \cdot \underbrace{\bigl[r + \gamma \cdot \textbf{?} - Q(s,a)\bigr]}_{\delta_t \text{ — error TD}}$$

Piezas de la fórmula:

| Símbolo | Nombre | Intuición |
|---------|--------|-----------|
| $Q(s,a)$ | Estimación actual | "Antes de ejecutar $a$, creía que valía $Q(s,a)$" |
| $r$ | Recompensa observada | Lo que el ambiente devolvió al hacer $a$ en $s$ |
| $\gamma \cdot \textbf{?}$ | Estimación del futuro | Cuánto más se puede ganar desde $s'$ en adelante |
| $r + \gamma \cdot \textbf{?}$ | Target TD | Nueva estimación del retorno total — con un paso real |
| $\alpha$ | Tasa de aprendizaje | Cuánto actualizamos: 0 = no aprendes, 1 = reemplazas todo |
| $\delta_t$ | Error TD | Diferencia entre lo nuevo y lo viejo: la "sorpresa" |

**`?`** es la pieza que falta: estimación del valor en $s'$. **Esta elección distingue SARSA de Q-learning.**

### El error TD $\delta_t$: intuición

$$\boxed{\delta_t = \underbrace{r + \gamma \cdot \textbf{?}}_{\text{nueva estimación}} - \underbrace{Q(s,a)}_{\text{estimación anterior}}}$$

Piénsalo como un sistema de aprendizaje por retroalimentación:

| Caso | Lectura | Efecto |
|------|---------|--------|
| $\delta_t > 0$ | "La acción fue **mejor** de lo que pensaba" — el target supera a $Q(s,a)$ | Subimos $Q(s,a)$ |
| $\delta_t < 0$ | "La acción fue **peor** de lo que pensaba" — el target está por debajo de $Q(s,a)$ | Bajamos $Q(s,a)$ |
| $\delta_t = 0$ | "Exactamente lo que esperaba" — no hay nueva información | $Q(s,a)$ no cambia |

El algoritmo empuja $Q(s,a)$ hacia el target `r + γ·?` en pequeños pasos de tamaño $\alpha$.
Con suficientes episodios, $Q$ converge al punto donde $\delta_t = 0$ para todos los pares $(s,a)$ — que es exactamente la ecuación de Bellman.

La pregunta que queda abierta: ¿qué ponemos en el `?`?

---

## Las dos ecuaciones de Bellman

Del módulo 21 y de la página anterior, recordamos:

$$Q^\pi(s,a) = \mathbb{E}_{\substack{s' \sim T \\ a' \sim \pi}}\bigl[r + \gamma Q^\pi(s', a')\bigr] \tag{Eq. 1}$$

$$Q^{∗}(s,a) = \mathbb{E}_{s' \sim T}\bigl[r + \gamma \max_{a'} Q^{∗}(s', a')\bigr] \tag{Eq. 2}$$

Colocadas juntas, la diferencia salta a la vista:

| | Eq. 1 — valor de $\pi$ | Eq. 2 — valor óptimo |
|--|------------------------|----------------------|
| Valor futuro en $s'$ | $Q^\pi(s', a')$ con $a' \sim \pi$ | $\max_{a'} Q^{∗}(s', a')$ |
| Pregunta que responde | ¿Cuánto vale seguir mi política actual? | ¿Cuánto vale hacer lo mejor posible? |
| Converge a | $Q^\pi$ — depende de $\pi$ | $Q^{∗}$ — óptimo global |

Ambas ecuaciones son **exactas** cuando $Q$ es la función correcta.
Las actualizaciones TD son versiones *aproximadas* que usan una muestra $(s, a, r, s')$ en lugar de la esperanza completa.

---

## La bifurcación: ¿qué va en el `?`?

Dos opciones naturales para rellenar el `?`:

**Opción A — usa la acción que *realmente* tomaremos en $s'$** (muestreada de $\pi$):

$$\textbf{?} = Q(s', a') \quad \text{donde } a' \sim \pi \qquad \Longrightarrow \quad \text{SARSA}$$

Apunta a la ecuación (1): aprende el valor de la política que se está ejecutando.

**Opción B — usa el máximo sobre todas las acciones de $s'$**:

$$\textbf{?} = \max_{a'} Q(s', a') \qquad \Longrightarrow \quad \text{Q-learning}$$

Apunta a la ecuación (2): aprende el valor óptimo, sin importar qué acción ejecuta el agente.

```
Actualización TD: Q(s,a) ← Q(s,a) + α [r + γ · ? − Q(s,a)]
                                              |
                  ┌───────────────────────────┴─────────────────────────┐
                  │                                                     │
         ? = Q(s', a'),  a'∼π                           ? = max Q(s', a')
                                                               a'
         ┌───────────────────┐                       ┌───────────────────┐
         │      SARSA        │                       │    Q-learning     │
         │   (on-policy)     │                       │  (off-policy)     │
         └───────────────────┘                       └───────────────────┘
```

---

## Política de comportamiento y política objetivo

:::exercise{title="Definiciones — on-policy vs off-policy"}

**Política de comportamiento** $\mu$: la política que usa el agente para **explorar** el ambiente — las acciones que *realmente* ejecuta.

**Política objetivo** $\pi$: la política que el agente está **aprendiendo** — hacia la cual converge $Q$.

**On-policy** ($\mu = \pi$): el agente aprende el valor de la política que está ejecutando.

**Off-policy** ($\mu \neq \pi$): el agente puede explorar con una política diferente a la que está aprendiendo.

:::

En ambos algoritmos usamos $\varepsilon$-greedy como política de comportamiento $\mu$ para garantizar exploración.
La diferencia está en $\pi$:

| | SARSA | Q-learning |
|--|-------|------------|
| $\mu$ (comportamiento) | $\varepsilon$-greedy | $\varepsilon$-greedy |
| $\pi$ (objetivo) | $\varepsilon$-greedy ($\mu = \pi$) | greedy pura ($\mu \neq \pi$) |
| Clasificación | **on-policy** | **off-policy** |

---

## ¿A qué converge cada uno?

:::exercise{title="Garantías de convergencia"}

**SARSA** con $\varepsilon$ fijo: converge a $Q^{\pi_\varepsilon}$ — el valor de la política $\varepsilon$-greedy, no el óptimo exacto.

**SARSA** decrementando $\varepsilon \to 0$ (con condiciones de convergencia estándar): converge a $Q^{∗}$.

**Q-learning**: converge a $Q^{∗}$ *independientemente de la política de comportamiento*, siempre que cada par $(s,a)$ sea visitado un número suficiente de veces.

:::

La diferencia práctica: Q-learning siempre aprende la política óptima aunque explore agresivamente; SARSA aprende el valor de la política con la que realmente opera.

---

## Un momento de divergencia concreto

Veamos exactamente cuándo y por qué los dos algoritmos producen resultados distintos.

Después de dos episodios sobre la escalera ($\alpha=0.5$, $\gamma=1$, $\varepsilon=0.4$), ambos tienen la misma tabla $Q$:

| Estado | $+1$ | $+2$ |
|--------|------|------|
| $s=0$ | $-1.0$ | $-2.5$ |
| $s=1$ | $0$ | $-5.0$ |
| $s=2$ | $0$ | $-0.5$ |
| $s=3$ | $0$ | $0$ |
| $s=4$ | $0$ | — |

Ahora empieza el **episodio 3**.
Desde $s=0$, la acción greedy es $+1$ (pues $Q(0,+1)=-1.0 > Q(0,+2)=-2.5$), pero $\varepsilon$-greedy *explora* y elige $a=+2$.
El ambiente devuelve $s'=2$ y $r=R(s'=2)=-5$.

**Situación:** ambos algoritmos están en $s=0$, tomaron $a=+2$, llegaron a $s'=2$ con $r=-5$.
En $s'=2$: $Q(2,+1)=0$ y $Q(2,+2)=-0.5$.

Ahora viene la bifurcación:

**Q-learning** toma el máximo — no importa qué acción se ejecutará realmente:

$$\textbf{?} = \max_{a'} Q(2, a') = \max(0, -0.5) = 0$$

$$\delta_{\text{QL}} = -5 + 1 \cdot 0 - (-2.5) = \mathbf{-2.5}$$

**SARSA** muestrea la acción que *ejecutará* según $\varepsilon$-greedy en $s'=2$.
La acción greedy sería $+1$ (valor $0 > -0.5$), pero $\varepsilon$-greedy *explora* y elige $a'=+2$:

$$\textbf{?} = Q(2, a'=+2) = -0.5$$

$$\delta_{\text{SARSA}} = -5 + 1 \cdot (-0.5) - (-2.5) = \mathbf{-3.0}$$

La tabla se actualiza de forma diferente:

| Algoritmo | $\delta$ | Nuevo $Q(0,+2)$ |
|-----------|----------|-----------------|
| Q-learning | $-2.5$ | $-2.5 + 0.5 \cdot (-2.5) = -3.75$ |
| SARSA | $-3.0$ | $-2.5 + 0.5 \cdot (-3.0) = -4.00$ |

A partir de aquí, las tablas divergen.

**¿Por qué ocurre esto?**
SARSA sufrió la penalización de una *exploración* en $s'=2$ — la acción $+2$ tiene valor $-0.5$, peor que el greedy $+1$.
Q-learning no la sufrió: siempre considera el mejor escenario posible en $s'$, aunque luego explore.

Este es exactamente el precio de ser on-policy: si tu política explora estados malos, aprendes que son malos.
Si eres off-policy, aprendes el valor óptimo aunque explores.

---

## Evolución de la tabla $Q$ en los dos primeros episodios

Para ver cómo se van llenando las celdas antes del punto de divergencia:

![Evolución de la tabla Q]({{ '/23_reinforcement_learning/images/04_q_table_evolution.png' | url }})

Los episodios 1 y 2 producen la misma tabla para SARSA y Q-learning porque en esos pasos el greedy coincide con lo que ε-greedy elige (o las celdas consultadas son cero de todas formas).
El divergence empieza cuando la tabla tiene valores suficientemente distintos de cero para que la diferencia entre $a' \sim \pi$ y $\max_{a'}$ importe.
