---
title: "EXP3: bandidos adversariales"
---

# 17.6 — EXP3: bandidos adversariales

> *"The art of war teaches us to rely not on the likelihood of the enemy's not coming, but on our own readiness to receive him."* — Sun Tzu

---

## 6.1 ¿Por qué cuestionar el supuesto estocástico?

Todos los algoritmos vistos hasta ahora — ε-greedy, UCB1, Thompson Sampling — comparten un supuesto fundamental: las recompensas de cada brazo provienen de una **distribución fija** (Bernoulli, Gaussiana, etc.). El entorno es estacionario y "honesto".

¿Cuándo falla este supuesto?

- **Publicidad competitiva**: si dos empresas usan bandidos para elegir anuncios, las recompensas de cada anuncio dependen de lo que muestra el competidor — un objetivo móvil
- **Oponentes adaptativos**: en seguridad informática, un atacante puede cambiar de estrategia al observar las defensas desplegadas
- **Preferencias cambiantes**: los usuarios de una plataforma cambian de gustos — lo que funcionaba en enero puede fallar en marzo
- **Mercados financieros**: los retornos de un activo no son i.i.d.; dependen de la dinámica global del mercado

En estos escenarios, modelar al entorno como un **adversario** que elige las recompensas (o pérdidas) de forma deliberada resulta más robusto que asumir estocasticidad.

---

## 6.2 El modelo adversarial

### Protocolo

En cada ronda $t = 1, \ldots, T$:

1. El **adversario** elige un vector de pérdidas $\ell_t = (\ell_{t,1}, \ldots, \ell_{t,K}) \in [0, 1]^K$ — una pérdida por brazo
2. El **agente** elige un brazo $A_t$ muestreando de una distribución $p_t$ sobre $\{1, \ldots, K\}$
3. El agente observa **solo** $\ell_{t, A_t}$ — la pérdida del brazo que eligió (feedback de bandidos, no la pérdida de los otros brazos)

El adversario puede ser **oblivious** (elige todas las pérdidas antes del juego) o **adaptativo** (elige $\ell_t$ después de ver las acciones pasadas $A_1, \ldots, A_{t-1}$, pero *antes* de ver $A_t$). El resultado de EXP3 cubre ambos casos.

### Regret adversarial

El regret se define contra el **mejor brazo fijo en retrospectiva**:

$$R_T = \sum_{t=1}^{T} \ell_{t, A_t} - \min_{i \in \{1,\ldots,K\}} \sum_{t=1}^{T} \ell_{t,i}$$

Notar que aquí usamos **pérdidas** (no recompensas). Minimizar pérdida = maximizar recompensa. El benchmark es el brazo que, *visto todo el juego*, acumula la menor pérdida total. El agente no sabe cuál es ese brazo hasta el final.

### Contraste con el modelo estocástico

| Aspecto | Estocástico | Adversarial |
|---------|-------------|-------------|
| Recompensas | $r_{t,i} \sim F_i$ (distribución fija) | $\ell_{t,i}$ elegida por adversario |
| Benchmark | Brazo con mayor $\mu_i$ | Mejor brazo fijo en retrospectiva |
| Información | Feedback de bandidos | Feedback de bandidos |
| Regret alcanzable | $O(K \log T / \Delta)$ | $O(\sqrt{KT \ln K})$ |

---

## 6.3 ¿Por qué fallan UCB1 y Thompson?

### UCB1 es determinista — el adversario lo predice

UCB1 selecciona $A_t = \arg\max_i \text{UCB}_i(t)$. Dado el historial, la selección es **completamente determinista**. Un adversario adaptativo puede calcular qué brazo elegirá UCB1 y asignarle la pérdida máxima:

**Ejemplo concreto** (3 brazos): Supongamos que UCB1 ha convergido a explotar el brazo C. El adversario hace:

$$\ell_{t,C} = 1, \quad \ell_{t,A} = 0, \quad \ell_{t,B} = 0$$

UCB1 sufre pérdida 1 en cada ronda. Eventualmente UCB1 cambia a otro brazo (digamos B), y el adversario simplemente reasigna $\ell_{t,B} = 1$. El adversario siempre castiga al brazo que UCB1 va a elegir.

### Thompson Sampling también concentra

Aunque Thompson es estocástico, su posterior se concentra con el tiempo. Después de muchas observaciones, $P(A_t = i^{∗}) \to 1$ para algún brazo $i^{∗}$. El adversario puede explotar esta concentración: basta observar qué brazo domina las elecciones y castigarlo.

### La defensa: aleatorización sostenida

La clave para sobrevivir a un adversario es **nunca volverse predecible**. El agente debe mantener una distribución sobre los brazos que no colapse a un solo brazo, pero que tampoco sea uniformemente aleatoria (eso sería no aprender nada).

![EXP3 vs UCB1]({{ '/17_multi_armed_bandits/images/22_exp3_vs_ucb1.png' | url }})

En el panel izquierdo (entorno estocástico), tanto UCB1 como EXP3 funcionan. En el panel derecho (entorno adversarial), UCB1 sufre regret lineal mientras EXP3 mantiene regret sublineal.

---

## 6.4 El algoritmo EXP3

**EXP3** (Exponential-weight algorithm for Exploration and Exploitation) fue propuesto por Auer et al. (2002). Sus tres ideas centrales son:

1. **Pesos multiplicativos**: cada brazo $i$ tiene un peso $w_i$ que refleja su rendimiento acumulado. Buenos brazos acumulan peso alto
2. **Mezcla con exploración uniforme**: las probabilidades de selección mezclan los pesos normalizados con una componente uniforme $\gamma / K$, garantizando que ningún brazo tenga probabilidad cero
3. **Estimación por importance weighting**: solo observamos la pérdida del brazo elegido. Para estimar las pérdidas de los demás brazos, usamos el estimador de **importance weighting** (Módulo 12): $\hat{\ell}_{t,i} = \ell_{t,i} / p_{t,i}$ cuando $A_t = i$

### Conexión con Módulo 12: importance weighting

En el Módulo 12 vimos que para estimar $\mathbb{E}_{x \sim p}[f(x)]$ usando muestras de otra distribución $q$, usamos $\frac{p(x)}{q(x)} f(x)$. Aquí la situación es análoga: queremos estimar la pérdida $\ell_{t,i}$ de *todos* los brazos, pero solo observamos la del brazo $A_t$ (muestreado con probabilidad $p_{t,i}$). El estimador:

$$\hat{\ell}_{t,i} = \frac{\ell_{t,i} \cdot \mathbb{1}[A_t = i]}{p_{t,i}}$$

es **insesgado**: $\mathbb{E}[\hat{\ell}_{t,i}] = \ell_{t,i}$. La división por $p_{t,i}$ corrige el sesgo de muestreo — si un brazo se elige con poca frecuencia, su pérdida observada se amplifica proporcionalmente.

### Pseudocódigo

```
función EXP3(K, T, γ):
    # ── Inicialización ────────────────────────────────────
    para i = 1, …, K:
        w[i] ← 1                                    # [E1] pesos iniciales iguales

    # ── Bucle principal ───────────────────────────────────
    para t = 1, …, T:

        # ── Calcular distribución de selección ───────────
        W ← Σ_i w[i]                                # suma total de pesos
        para i = 1, …, K:
            p[i] ← (1 − γ) · w[i] / W + γ / K      # [E2] mezcla: pesos + uniforme

        # ── Seleccionar brazo y observar ─────────────────
        A ← muestrear de Categorical(p)
        ℓ_A ← OBSERVAR_PÉRDIDA(A)                   # solo vemos ℓ_{t,A}

        # ── Estimar pérdidas por importance weighting ────
        para i = 1, …, K:
            si i == A:
                ℓ̂[i] ← ℓ_A / p[i]                   # [E3] importance weighting
            sino:
                ℓ̂[i] ← 0                             # no observamos los demás

        # ── Actualizar pesos multiplicativamente ─────────
        η ← γ / K                                    # tasa de aprendizaje
        para i = 1, …, K:
            w[i] ← w[i] · exp(−η · ℓ̂[i])            # [E4] penalizar brazos con alta pérdida

    retornar w
```

### Los cuatro pasos clave

| Paso | Marcador | Operación | Intuición |
|------|----------|-----------|-----------|
| Inicializar pesos | `[E1]` | $w_i = 1$ para todo $i$ | Sin preferencia inicial |
| Mezclar probabilidades | `[E2]` | $p_i = (1-\gamma)\frac{w_i}{\sum_j w_j} + \frac{\gamma}{K}$ | Explotar pesos pero garantizar exploración mínima |
| Importance weighting | `[E3]` | $\hat{\ell}_{t,i} = \frac{\ell_{t,i} \cdot \mathbb{1}[A_t = i]}{p_{t,i}}$ | Estimar pérdida corrigiendo sesgo de muestreo |
| Actualización multiplicativa | `[E4]` | $w_i \leftarrow w_i \cdot \exp(-\eta \hat{\ell}_{t,i})$ | Reducir peso de brazos con alta pérdida estimada |

### Parámetros

Con horizonte $T$ conocido, la elección óptima es:

$$\gamma = \eta = \sqrt{\frac{K \ln K}{T}}$$

Cuando $T$ es desconocido, se puede usar el truco del "doubling": ejecutar EXP3 con $T=1, 2, 4, 8, \ldots$ y reiniciar pesos en cada fase.

---

## 6.5 Traza manual: 3 brazos, adversario cíclico

Consideremos un adversario que **rota** cuál brazo es bueno (pérdida baja) en un patrón cíclico. Esto es algo que UCB1 no puede manejar.

**Patrón del adversario** (pérdidas):
- Rondas 1, 4: brazo A bueno → $\ell = (0.1, 0.9, 0.9)$
- Rondas 2, 5: brazo B bueno → $\ell = (0.9, 0.1, 0.9)$
- Rondas 3, 6: brazo C bueno → $\ell = (0.9, 0.9, 0.1)$

Usamos $\gamma = 0.3$, $\eta = \gamma / K = 0.1$, seed=42.

| $t$ | $\ell_t$ | $w_A$ | $w_B$ | $w_C$ | $p_A$ | $p_B$ | $p_C$ | $A_t$ | $\ell_{t,A_t}$ | $\hat{\ell}_{A_t}$ | Actualización |
|:---:|:--------:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:---------:|:----------:|:-------------:|
| 1 | (0.1, 0.9, 0.9) | 1.00 | 1.00 | 1.00 | 0.333 | 0.333 | 0.333 | C | 0.9 | 2.70 | $w_C \cdot e^{-0.27}$ |
| 2 | (0.9, 0.1, 0.9) | 1.00 | 1.00 | 0.76 | 0.353 | 0.353 | 0.294 | A | 0.9 | 2.55 | $w_A \cdot e^{-0.255}$ |
| 3 | (0.9, 0.9, 0.1) | 0.77 | 1.00 | 0.76 | 0.314 | 0.376 | 0.310 | B | 0.9 | 2.39 | $w_B \cdot e^{-0.239}$ |
| 4 | (0.1, 0.9, 0.9) | 0.77 | 0.79 | 0.76 | 0.332 | 0.338 | 0.330 | A | 0.1 | 0.30 | $w_A \cdot e^{-0.030}$ |
| 5 | (0.9, 0.1, 0.9) | 0.75 | 0.79 | 0.76 | 0.327 | 0.341 | 0.332 | B | 0.1 | 0.29 | $w_B \cdot e^{-0.029}$ |
| 6 | (0.9, 0.9, 0.1) | 0.75 | 0.77 | 0.76 | 0.330 | 0.337 | 0.334 | C | 0.1 | 0.30 | $w_C \cdot e^{-0.030}$ |

**Observaciones**:

- En $t=1$: pesos iguales → distribución uniforme. C es elegido (seed=42) y sufre pérdida 0.9. Su importance-weighted loss es $0.9 / 0.333 = 2.70$. El peso de C baja
- En $t=2$–$3$: el adversario castiga al brazo elegido, pero EXP3 distribuye sus elecciones — ningún brazo domina
- En $t=4$–$6$: los pesos se han estabilizado cerca de la uniformidad. Ahora el agente empieza a "atrapar" al brazo bueno de cada ronda
- Contraste con UCB1: UCB1 habría convergido a un solo brazo y el adversario lo castigaría ronda tras ronda con regret lineal

---

## 6.6 Garantía de regret

**Teorema (Auer et al., 2002).** EXP3 con parámetro $\gamma = \sqrt{K \ln K / T}$ satisface, para cualquier secuencia de pérdidas elegida por el adversario:

$$\mathbb{E}[R_T] \leq 2\sqrt{KT \ln K}$$

### Interpretación

- El regret es $O(\sqrt{KT \ln K})$ — **sublineal** en $T$. El regret promedio por ronda $R_T / T \to 0$ cuando $T \to \infty$
- Comparado con el $O(\log T)$ de UCB1 en el caso estocástico, esto es significativamente peor. Es el **precio de no asumir estocasticidad**
- La cota vale para **cualquier** adversario — incluso el peor posible. No hay supuesto sobre la estructura de las pérdidas
- La dependencia $\sqrt{K}$ en $K$ es inevitable: más brazos implica más pérdida de información (solo observamos uno por ronda)

### Optimalidad minimax

La cota inferior para bandidos adversariales es $\Omega(\sqrt{KT})$. EXP3 logra $O(\sqrt{KT \ln K})$ — óptimo salvo un factor $\sqrt{\ln K}$. El algoritmo **EXP3-IX** (Implicit eXploration) de Neu (2015) cierra esta brecha y logra $O(\sqrt{KT})$ exacto.

---

## 6.7 El espectro de supuestos

Los algoritmos de bandidos se ubican en un espectro según qué tan fuerte es su supuesto sobre el entorno:

| Supuesto | Algoritmos | Regret | Cuándo aplica |
|----------|-----------|--------|---------------|
| **Estocástico fuerte** (distribución conocida) | KL-UCB, Thompson | $O\left(\sum \frac{\Delta_i \log T}{\text{KL}(\mu_i, \mu^{∗})}\right)$ | Recompensas i.i.d., familia conocida |
| **Estocástico** (sub-Gaussiano) | UCB1, ε-greedy | $O(K \log T / \Delta)$ | Recompensas i.i.d., cotas de concentración |
| **Adversarial** | EXP3, EXP3-IX | $O(\sqrt{KT \ln K})$ | Sin supuestos sobre las pérdidas |

**Observación clave**: no hay almuerzo gratis. Los algoritmos estocásticos logran regret $O(\log T)$ — exponencialmente mejor que $O(\sqrt{T})$ — pero solo cuando su supuesto se cumple. Si el entorno es adversarial, su regret puede ser **lineal**. EXP3 es más conservador: garantiza $O(\sqrt{T})$ siempre, pero nunca logra $O(\log T)$ incluso si el entorno resulta ser estocástico.

Existe investigación activa en algoritmos **"best-of-both-worlds"** que logran $O(\log T)$ en entornos estocásticos y $O(\sqrt{T})$ en adversariales automáticamente — lo mejor de ambos mundos.

---

## 6.8 Guía práctica: ¿cuándo usar EXP3?

**Usar EXP3 cuando**:
- El entorno puede ser no estacionario o adversarial
- Hay competidores que reaccionan a tus decisiones
- Las recompensas dependen de factores externos impredecibles
- Necesitas garantías de peor caso sin supuestos distribucionales

**Usar algoritmos estocásticos (UCB1, Thompson) cuando**:
- Las recompensas son razonablemente estacionarias
- No hay adversario adaptativo
- Se necesita convergencia rápida ($O(\log T)$ vs $O(\sqrt{T})$)
- Hay información previa (prior bayesiano para Thompson)

**Regla general**: la mayoría de los problemas reales de A/B testing, recomendación y optimización de parámetros son **más cercanos al caso estocástico**. EXP3 es un seguro contra lo inesperado — su valor está en las garantías de peor caso, no en el rendimiento típico.

![Evolución de pesos y probabilidades de EXP3]({{ '/17_multi_armed_bandits/images/23_exp3_weights.png' | url }})

En la figura se observa cómo los pesos de EXP3 evolucionan: a diferencia de UCB1 o Thompson, las probabilidades **nunca colapsan** a un solo brazo. La componente uniforme $\gamma / K$ garantiza exploración perpetua.

---

## Resumen

| Propiedad | EXP3 |
|-----------|------|
| **Idea** | Pesos multiplicativos + exploración uniforme + importance weighting |
| **Fórmula** | $p_i = (1-\gamma)\frac{w_i}{\sum w_j} + \frac{\gamma}{K}$; $w_i \leftarrow w_i \exp(-\eta \hat{\ell}_i)$ |
| **Parámetros** | $\gamma = \sqrt{K \ln K / T}$ (requiere conocer $T$) |
| **Regret** | $O(\sqrt{KT \ln K})$ — sublineal, minimax-óptimo (salvo $\sqrt{\ln K}$) |
| **Ventaja** | Garantías contra **cualquier** adversario; no asume estocasticidad |
| **Desventaja** | Regret $O(\sqrt{T})$ incluso en entornos estocásticos (vs $O(\log T)$) |
| **Cuándo usar** | Entornos no estacionarios, adversariales, o cuando se necesitan garantías de peor caso |

En la sección 17.7 veremos aplicaciones concretas de bandidos — A/B testing, sistemas de recomendación, redes de comunicación — y variantes que extienden el framework básico a problemas del mundo real.
