---
title: "03 · SARSA"
summary: "El quíntuple (S,A,R,S',A'), la regla de actualización on-policy, traza de 2 episodios sobre la escalera, convergencia"
---

## El nombre es el algoritmo

SARSA se llama así porque su actualización usa exactamente cinco elementos en orden:

$$(\underbrace{S}_{\text{estado}}, \underbrace{A}_{\text{acción}}, \underbrace{R}_{\text{recompensa}}, \underbrace{S'}_{\text{sig. estado}}, \underbrace{A'}_{\text{sig. acción}})$$

La diferencia clave respecto a Q-learning: la **siguiente acción $A'$ se elige *antes* de hacer la actualización**, usando la misma política $\varepsilon$-greedy que generó $A$.
El agente aprende el valor de la política que *realmente ejecuta*.

---

## Regla de actualización

$$\boxed{Q(s,a) \leftarrow Q(s,a) + \alpha\bigl[r + \gamma Q(s', a') - Q(s,a)\bigr]}$$

donde $a' \sim \pi_\varepsilon(s')$ — la siguiente acción está muestreada de la política $\varepsilon$-greedy.

Comparado con el esqueleto TD de la sección anterior, el `?` se llena con $Q(s', a')$.

---

## Pseudocódigo

```
SARSA(α, γ, ε, num_episodios):
  Inicializa Q[s, a] ← 0 para todo (s, a)
  Para cada episodio:
    s ← estado_inicial()
    a ← ε-greedy(Q, s)            ← elegimos a ANTES de entrar al bucle
    Mientras s no sea terminal:
      s', r ← ejecutar(a)          ← observamos (s', r)
      a' ← ε-greedy(Q, s')         ← elegimos a' AHORA (on-policy)
      Q[s, a] ← Q[s, a] + α · (r + γ · Q[s', a'] − Q[s, a])
      s ← s'                        ← avanzamos el estado
      a ← a'                        ← avanzamos la acción (5-tuple completo)
```

La firma estructural de SARSA: `a'` se selecciona *dentro del bucle*, antes de actualizar, y luego se usa como la acción del siguiente paso.
Esto es lo que lo hace **on-policy**.

---

## Traza completa: 2 episodios sobre la escalera

Parámetros: $\alpha = 0.5$, $\gamma = 1$, $\varepsilon = 0.4$.
La tabla $Q$ empieza en cero.

### Episodio 1: trayectoria $0 \to 1 \to 3 \to 5$

El agente elige las acciones con $\varepsilon$-greedy (con la tabla en cero, las acciones greedy son todas iguales, así que explorar o explotar es equivalente).
Fijamos esta trayectoria para el ejemplo:

| Paso | $s$ | $a$ | $r$ | $s'$ | $a'$ (on-policy) | $\delta$ | Actualización |
|------|-----|-----|-----|------|------------------|----------|---------------|
| 1 | 0 | $+1$ | $-2$ | 1 | $+2$ | $-2 + 0 - 0 = -2$ | $Q(0,+1) \mathrel{+}= 0.5 \cdot (-2) = -1.0$ |
| 2 | 1 | $+2$ | $-10$ | 3 | $+2$ | $-10 + 0 - 0 = -10$ | $Q(1,+2) \mathrel{+}= 0.5 \cdot (-10) = -5.0$ |
| 3 | 3 | $+2$ | $0$ | 5 (meta) | — | $0 + 0 - 0 = 0$ | $Q(3,+2)$ no cambia |

> **Recompensas:** $R(s'=1)=-2$ (costo de estado 1), $R(s'=3)=-10$ (costo de estado 3), $R(s'=5)=0$ (meta).

Tabla $Q$ después del episodio 1:

| Estado | $+1$ | $+2$ |
|--------|------|------|
| $s=0$ | **−1.0** | 0 |
| $s=1$ | 0 | **−5.0** |
| $s=2$ | 0 | 0 |
| $s=3$ | 0 | 0 |
| $s=4$ | 0 | — |

### Episodio 2: trayectoria $0 \to 2 \to 4 \to 5$

Ahora hay valores en la tabla.
En $s=0$: $Q(0,+1)=-1.0$ y $Q(0,+2)=0$.
La acción greedy es $+2$.
$\varepsilon$-greedy puede explorar: fijamos que elige $+2$ (greedy).

| Paso | $s$ | $a$ | $r$ | $s'$ | $a'$ (on-policy) | $\delta$ | Actualización |
|------|-----|-----|-----|------|------------------|----------|---------------|
| 1 | 0 | $+2$ | $-5$ | 2 | $+2$ (exploración) | $-5 + 1 \cdot 0 - 0 = -5$ | $Q(0,+2) \mathrel{+}= 0.5 \cdot (-5) = -2.5$ |
| 2 | 2 | $+2$ | $-1$ | 4 | $+1$ (única acción) | $-1 + 1 \cdot 0 - 0 = -1$ | $Q(2,+2) \mathrel{+}= 0.5 \cdot (-1) = -0.5$ |
| 3 | 4 | $+1$ | $0$ | 5 (meta) | — | $0 + 0 - 0 = 0$ | $Q(4,+1)$ no cambia |

> **Recompensas:** $R(s'=2)=-5$ (costo de estado 2), $R(s'=4)=-1$ (costo de estado 4), $R(s'=5)=0$ (meta).

Tabla $Q$ después del episodio 2 — **idéntica en SARSA y Q-learning hasta aquí**:

| Estado | $+1$ | $+2$ |
|--------|------|------|
| $s=0$ | −1.0 | **−2.5** |
| $s=1$ | 0 | −5.0 |
| $s=2$ | 0 | **−0.5** |
| $s=3$ | 0 | 0 |
| $s=4$ | 0 | — |

Esta es la tabla en la que vimos el momento de divergencia en la sección anterior.

![Evolución de la tabla Q]({{ '/23_reinforcement_learning/images/04_q_table_evolution.png' | url }})

---

## Convergencia de SARSA

:::exercise{title="¿A qué converge SARSA?"}

**Con $\varepsilon$ fijo:** SARSA converge a $Q^{\pi_\varepsilon}$ — el valor de la política $\varepsilon$-greedy, no la política greedy pura.
$Q^{\pi_\varepsilon}(s,a)$ es ligeramente peor que $Q^{∗}(s,a)$ porque el agente sigue explorando ocasionalmente con probabilidad $\varepsilon$.

**Con $\varepsilon \to 0$ (decrementando gradualmente):** SARSA converge a $Q^{∗}$ (bajo condiciones de convergencia estándar: visitas infinitas y tasa de aprendizaje decreciente).

:::

**¿Por qué SARSA con $\varepsilon$ fijo no converge a $Q^{∗}$?**
Porque la política $\pi_\varepsilon$ nunca es completamente greedy: siempre hay una probabilidad $\varepsilon$ de tomar una acción subóptima.
SARSA aprende fielmente el valor de esa política — incluyendo sus imperfecciones.

Esto no es un defecto; es una característica: SARSA es *honesto* sobre lo que el agente hará en el futuro.
En entornos peligrosos (como el problema del acantilado), esa honestidad puede ser preferible.
