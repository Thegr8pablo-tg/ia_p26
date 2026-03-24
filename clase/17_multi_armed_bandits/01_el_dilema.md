---
title: "El dilema: exploración vs. explotación"
---

# 17.1 — El dilema: exploración vs. explotación

> *"You have to learn the rules of the game. And then you have to play better than anyone else."* — Albert Einstein

---

## Tres escenarios, un mismo problema

Imagina las siguientes situaciones:

| Escenario | Opciones | Recompensa | Costo de explorar |
|-----------|----------|------------|-------------------|
| **Máquinas tragamonedas** | 3 máquinas con probabilidades desconocidas | Dinero ganado | Dinero perdido en máquinas malas |
| **Prueba A/B** | 2 diseños de página web | Tasa de conversión (clics → compras) | Usuarios expuestos al peor diseño |
| **Ensayo clínico** | 3 tratamientos experimentales | Recuperación del paciente | Pacientes que reciben tratamiento inferior |

Las tres comparten una estructura: en cada ronda, debes **elegir** entre opciones con efectos desconocidos. Cada elección te da una **recompensa** (posiblemente aleatoria) y, al mismo tiempo, **información** sobre esa opción. El dilema: ¿aprovechas lo mejor que has visto hasta ahora (*explotación*) o pruebas algo menos conocido que podría ser mejor (*exploración*)?

![Espectro exploración-explotación]({{ '/17_multi_armed_bandits/images/03_explore_exploit_spectrum.png' | url }})

---

## Del MEU al bandido: ¿qué cambia?

En el Módulo 09 (Teoría de la Decisión) aprendimos el **principio de máxima utilidad esperada (MEU)**:

$$a^{∗} = \arg\max_a \sum_s P(s) \cdot U(o(a, s))$$

Este principio asume que **conocemos** $P(s)$ — la distribución de los estados. Si supiéramos que la máquina A paga con probabilidad 0.3, la B con 0.5 y la C con 0.7, la respuesta sería trivial: siempre jalar C.

Pero en el problema del bandido multibrazo **no conocemos las distribuciones**. Debemos **aprender** $P(s)$ al mismo tiempo que **maximizamos** la utilidad acumulada. Cada acción produce dos cosas:

1. Una **recompensa** inmediata
2. **Información** sobre la calidad de esa opción

Y aquí está la tensión: una acción que nos da buena información (explorar un brazo poco conocido) puede darnos mala recompensa. Una acción que explota el mejor brazo conocido no nos enseña nada nuevo — y tal vez estamos explotando el brazo equivocado.

---

## Definición formal

El **problema del bandido multibrazo** (multi-armed bandit, MAB) se define con 5 componentes:

| Componente | Símbolo | Descripción |
|------------|---------|-------------|
| Número de brazos | $K$ | Cantidad de opciones disponibles |
| Distribuciones de recompensa | $\nu_1, \ldots, \nu_K$ | Cada brazo $i$ tiene una distribución $\nu_i$ con media $\mu_i$ (desconocida para el agente) |
| Horizonte | $T$ | Número total de rondas |
| Política | $\pi$ | Regla de decisión: dado el historial, ¿qué brazo jalar? |
| Regret acumulado | $R_T$ | Medida de rendimiento (definida abajo) |

En cada ronda $t = 1, 2, \ldots, T$:

1. El agente elige un brazo $A_t \in \{1, \ldots, K\}$ (según su política $\pi$)
2. El entorno genera una recompensa $r_t \sim \nu_{A_t}$
3. El agente observa **solo** $r_t$ (no las recompensas de los otros brazos)
4. El agente actualiza sus estimaciones y repite

El brazo **óptimo** es $i^{∗} = \arg\max_i \mu_i$, con media $\mu^{∗} = \mu_{i^{∗}}$.

---

## Distribuciones de recompensa

La definición dice que cada brazo tiene una distribución $\nu_i$, pero no dice **qué tipo** de distribución. Este es un punto clave: la teoría de bandidos funciona con cualquier distribución, y la elección afecta tanto la naturaleza de las recompensas como la dificultad del problema.

![Distribuciones de recompensa comunes]({{ '/17_multi_armed_bandits/images/26_reward_distributions.png' | url }})

### Bernoulli: éxito o fracaso

La distribución más simple para bandidos. Cada pull da $r \in \{0, 1\}$:

$$r \sim \text{Bernoulli}(p) \implies P(r=1) = p, \quad P(r=0) = 1-p$$

La media es $\mu_i = p_i$. Este es el modelo natural para situaciones de **sí/no**: ¿hizo clic el usuario?, ¿se curó el paciente?, ¿ganó la máquina tragamonedas?

Bernoulli tiene una propiedad especial: la media $p$ determina completamente la distribución. Esto hace que la cota de Lai-Robbins se exprese directamente en términos de las medias (ver más abajo).

### Normal: recompensas continuas

Cada pull da un valor real $r \in (-\infty, \infty)$:

$$r \sim \mathcal{N}(\mu, \sigma^2)$$

Aquí la media $\mu_i$ es lo que queremos estimar, pero la varianza $\sigma^2$ controla cuánto **ruido** hay. Con $\sigma$ grande, las distribuciones de brazos distintos se solapan mucho → se necesitan más muestras para distinguirlos.

Este modelo es natural para recompensas como ingresos, tiempos de respuesta o puntuaciones.

### Otras distribuciones

El marco de bandidos funciona con cualquier distribución paramétrica con media finita:

| Distribución | Soporte | Parámetro(s) | Ejemplo de uso |
|:---:|:---:|:---:|:---:|
| Bernoulli | $\{0, 1\}$ | $p$ | Clics, conversiones, diagnósticos |
| Normal | $(-\infty, \infty)$ | $\mu, \sigma^2$ | Ingresos, ratings, señales |
| Poisson | $\{0, 1, 2, \ldots\}$ | $\lambda$ | Conteos de eventos (visitas, fallos) |
| Exponencial | $[0, \infty)$ | $\lambda$ | Tiempos de espera, duración de sesión |

La elección de distribución importa por dos razones:

1. **Algoritmos paramétricos** como Thompson Sampling requieren un modelo conjugado específico para cada familia (veremos Beta-Bernoulli y Normal-Normal en la sección 4)
2. **La cota inferior de Lai-Robbins** depende de la divergencia KL entre distribuciones, que cambia según la familia. Bernoulli y Normal con misma diferencia de medias $\Delta$ tienen KL distintas → la dificultad del problema cambia

En este módulo usamos Bernoulli y Normal como problemas canónicos porque cubren los dos casos fundamentales (discreto binario y continuo) y porque tienen conjugados analíticos. Los algoritmos no-paramétricos como ε-greedy y UCB1 funcionan igual sin importar la distribución.

---

## Dos problemas canónicos

Usaremos dos problemas estándar a lo largo de todo el módulo, jugando el mismo papel que Nim(1,2) en el Módulo 15:

### Problema canónico A: Bernoulli

![Tres máquinas tragamonedas]({{ '/17_multi_armed_bandits/images/01_slot_machines.png' | url }})

- **3 brazos** con recompensas Bernoulli: $r \in \{0, 1\}$ (éxito o fracaso)
- Probabilidades de éxito: $\mu_A = 0.3$, $\mu_B = 0.5$, $\mu_C = 0.7$
- Brazo óptimo: C ($\mu^{∗} = 0.7$)
- Brechas (gaps): $\Delta_A = 0.7 - 0.3 = 0.4$, $\Delta_B = 0.7 - 0.5 = 0.2$, $\Delta_C = 0$

¿Por qué estos valores? La brecha entre B y C ($\Delta_B = 0.2$) es más difícil de detectar que la de A ($\Delta_A = 0.4$). Un buen algoritmo debe dejar de explorar A rápidamente, pero necesitará más muestras para distinguir B de C.

### Problema canónico B: Gaussiano

![Distribuciones gaussianas]({{ '/17_multi_armed_bandits/images/02_gaussian_densities.png' | url }})

- **3 brazos** con recompensas normales: $r \sim \mathcal{N}(\mu_i, \sigma^2)$
- Medias: $\mu_A = 1.0$, $\mu_B = 2.0$, $\mu_C = 3.0$, con $\sigma = 1.5$ compartida
- Brazo óptimo: C ($\mu^{∗} = 3.0$)
- Brechas: $\Delta_A = 2.0$, $\Delta_B = 1.0$

La diferencia clave con el caso Bernoulli: las recompensas son continuas y las distribuciones se **solapan significativamente** (un pull de A puede dar más que uno de C). Esto hace que se necesiten más muestras para identificar al mejor brazo.

---

## Regret: la medida del arrepentimiento

¿Cómo evaluamos una política de bandidos? No por la recompensa total (que depende de las distribuciones), sino por cuánto **peor** lo hicimos comparado con el oráculo que siempre jala el brazo óptimo.

### Regret por ronda

$$r_t = \mu^{∗} - \mu_{A_t}$$

Es la diferencia entre la media del mejor brazo y la del brazo que efectivamente jalamos. Notar que $r_t \geq 0$ siempre.

### Regret acumulado

$$R_T = \sum_{t=1}^{T} (\mu^{∗} - \mu_{A_t}) = T \cdot \mu^{∗} - \sum_{t=1}^{T} \mu_{A_t}$$

### Descomposición por brazo

Esta forma es clave para entender **de dónde viene** el regret:

$$R_T = \sum_{i=1}^{K} \Delta_i \cdot N_i(T)$$

donde $\Delta_i = \mu^{∗} - \mu_i$ es la brecha del brazo $i$ y $N_i(T)$ es el número de veces que se jaló el brazo $i$.

**Interpretación**: el regret crece cuando jalamos brazos subóptimos ($\Delta_i > 0$) muchas veces ($N_i$ grande). Un buen algoritmo mantiene $N_i(T)$ pequeño para brazos con $\Delta_i$ grande.

![Descomposición del regret por brazo]({{ '/17_multi_armed_bandits/images/05_regret_decomposition.png' | url }})

---

## ¿Cuánto regret es inevitable?

### Estrategias puras: ningún extremo funciona

![Estrategias puras]({{ '/17_multi_armed_bandits/images/04_pure_strategies.png' | url }})

- **Explotación pura** (siempre jalar un brazo fijo sin explorar): si por suerte eliges C, excelente. Pero si caes en A (el peor), el regret crece linealmente como $\Delta_A \cdot T = 0.4T$.
- **Exploración pura** (round-robin): recompensa promedio $\bar{\mu} = \frac{1}{K}\sum_i \mu_i$, siempre peor que $\mu^{∗}$. Regret lineal de $(\mu^{∗} - \bar{\mu})T$.
- **Oráculo** (siempre el mejor brazo): regret = 0. Pero requiere saber las distribuciones de antemano.

Necesitamos algo entre los dos extremos: explorar lo suficiente para identificar al mejor brazo, y explotar lo aprendido.

### La cota inferior de Lai-Robbins

¿Existe un límite fundamental de cuánto regret es inevitable? Sí. Lai y Robbins (1985) demostraron que **ningún** algoritmo "uniformemente bueno" puede tener regret menor que:

$$\liminf_{T \to \infty} \frac{R_T}{\log T} \geq \sum_{i: \mu_i < \mu^{∗}} \frac{\Delta_i}{\text{KL}(\nu_i, \nu_{i^{∗}})}$$

donde $\text{KL}(\nu_i, \nu_{i^{∗}})$ es la divergencia KL (Módulo 06) entre las distribuciones de los brazos $i$ e $i^{∗}$.

**Interpretación**: el mejor regret posible crece **logarítmicamente** con $T$ — es decir, $R_T = \Omega(\log T)$. Un algoritmo que logra $R_T = O(\log T)$ es asintóticamente óptimo. Brazos con distribuciones más "parecidas" al óptimo (KL pequeña) contribuyen más al regret inevitable, porque son más difíciles de distinguir.

Para el caso Bernoulli, la divergencia KL es:

$$\text{KL}(\mu_i, \mu^{∗}) = \mu_i \ln \frac{\mu_i}{\mu^{∗}} + (1 - \mu_i) \ln \frac{1 - \mu_i}{1 - \mu^{∗}}$$

Esta cota será nuestro benchmark: en las siguientes secciones veremos que ε-greedy no la alcanza, UCB1 se acerca, y Thompson Sampling la iguala asintóticamente.

---

## Lo que viene

Ahora que tenemos el problema y la métrica, estamos listos para el primer algoritmo. La siguiente sección presenta **ε-greedy**: la estrategia más simple para balancear exploración y explotación. Veremos por qué funciona razonablemente bien — y exactamente dónde falla.
