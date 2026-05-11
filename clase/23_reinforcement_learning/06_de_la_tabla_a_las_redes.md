---
title: "06 · De la tabla a las redes"
summary: "Por qué la tabla Q explota en CartPole; DQN como solución; repetición de experiencia y red objetivo"
---

## La escalera como puente

La escalera ya tiene su $Q^∗$ — la calculamos con programación dinámica en el módulo 21 y la recuperamos con Q-learning en las páginas anteriores.
Ahora podemos plantear la misma pregunta desde otro ángulo: ¿podría una red neuronal $Q_\theta(s,a)$ aprender la misma tabla?

La respuesta es sí — y el resultado es idéntico.
Para la escalera (5 estados, 2 acciones → 10 celdas), la tabla es claramente mejor: más simple, exacta, sin hiperparámetros de red.
El punto no es reemplazar algo que funciona.
El punto es entender **cuándo la tabla deja de funcionar** — porque ese momento llega muy rápido.

---

## CartPole: cuando la tabla explota

CartPole-v1 es el entorno de prueba estándar para RL continuo.
El objetivo es mantener un poste vertical empujando un carro hacia la izquierda o la derecha.

### El MDP de CartPole

| Símbolo | Nombre | Descripción |
|---------|--------|-------------|
| $S$ | Espacio de estados | Vector continuo 4D: $(x,\ \dot{x},\ \theta,\ \dot{\theta})$ |
| $x$ | Posición del carro | Metros, $[-4.8,\ 4.8]$ |
| $\dot{x}$ | Velocidad del carro | m/s, continuo |
| $\theta$ | Ángulo del poste | Radianes, $[-24°,\ 24°]$ |
| $\dot{\theta}$ | Velocidad angular | rad/s, continuo |
| $A(s)$ | Acciones | $\{0=\text{izquierda},\ 1=\text{derecha}\}$ |
| $R(s,a,s')$ | Recompensa | $+1$ por cada paso que el poste no cae |
| Terminal | Condición de fin | $\lvert\theta\rvert > 12°$ o $\lvert x \rvert > 2.4$ o $t > 500$ |
| Resuelto | Criterio oficial | Media $\geq 475$ sobre 100 episodios consecutivos |

### El problema de la discretización

Para usar una tabla $Q$, hay que discretizar el espacio continuo.
Si dividimos cada dimensión en 10 intervalos (bins):

$$10 \times 10 \times 10 \times 10 = 10{,}000 \text{ estados}$$

Parece manejable — pero los problemas aparecen rápido:

| Problema | Estados | Acciones | Celdas $Q$ |
|----------|---------|----------|------------|
| Escalera | 5 | 2 | 10 |
| CartPole (10 bins por dim.) | 10,000 | 2 | 20,000 |
| CartPole (20 bins por dim.) | 160,000 | 2 | 320,000 |
| Atari (píxeles) | $256^{33600}$ | 18 | imposible |

El problema más profundo no es el tamaño — es la **falta de generalización**.
En una tabla, dos celdas vecinas tienen valores completamente independientes.
Si el ángulo es $12.4°$ (un bin) y $12.6°$ (el bin siguiente), la tabla los trata como estados sin relación.
Una red neuronal, en cambio, puede interpolar: estados similares producen salidas similares porque comparten los mismos pesos $\theta$.

---

## La sustitución

El cambio fundamental es reemplazar la tabla por una red:

$$\boxed{Q[s,a] \to Q_\theta(s, a)}$$

![Arquitectura DQN]({{ '/23_reinforcement_learning/images/08_dqn_architecture.png' | url }})

La red recibe como entrada el vector de estado completo (los 4 valores continuos de CartPole) y produce como salida un valor $Q$ por cada acción posible.
No hay discretización: el espacio continuo se procesa directamente.

La política $\varepsilon$-greedy sigue siendo exactamente la misma:

$$a^∗ = \arg\max_a Q_\theta(s, a)$$

La única diferencia es que ahora $Q_\theta$ es una red neuronal en vez de una tabla.

---

## Problema 1: muestras correlacionadas

La idea más directa sería aplicar descenso de gradiente directamente sobre cada transición $(s_t, a_t, r_t, s_{t+1})$ a medida que ocurre.
El problema: las transiciones consecutivas dentro de un episodio son altamente correlacionadas — $s_{t+1}$ es el estado que sigue a $s_t$ en la misma trayectoria, no una muestra independiente del problema.

SGD asume que las muestras son i.i.d. (independientes e idénticamente distribuidas).
Si los gradientes consecutivos apuntan todos en la misma dirección (porque vienen del mismo episodio), la red puede sobreajustarse a esa trayectoria y "olvidar" experiencias anteriores.

**Solución: repetición de experiencia (experience replay)**

Se mantiene un buffer $D$ con las últimas $N$ transiciones (típicamente $N = 10{,}000$).
En cada paso, en lugar de usar solo la transición más reciente, se muestrea aleatoriamente un mini-lote de 64 transiciones del buffer.

![Repetición de experiencia]({{ '/23_reinforcement_learning/images/09_experience_replay.png' | url }})

El muestreo aleatorio rompe la correlación temporal: cada mini-lote mezcla transiciones de distintos momentos y distintos episodios.
Además, cada transición almacenada puede reutilizarse múltiples veces, mejorando la eficiencia de datos.

---

## Problema 2: el blanco se mueve

La función de pérdida de Q-learning tiene la forma:

$$L(\theta) = \mathbb{E}\bigl[(y_i - Q_\theta(s_i, a_i))^2\bigr]$$

donde el objetivo es:

$$y_i = r + \gamma \max_b Q_\theta(s', b)$$

Hay un problema oculto: $Q_\theta$ aparece en **ambos lados**.
En el lado derecho genera el objetivo $y_i$; en el lado izquierdo es lo que intentamos ajustar.
Cada vez que actualizamos $\theta$, el objetivo $y_i$ también cambia — es como intentar alcanzar un blanco que se mueve en cada paso.
El resultado es entrenamiento inestable: los gradientes oscilan y la red puede no converger.

**Solución: red objetivo (target network)**

Se mantiene una segunda copia de la red, $Q_{\theta^-}$, con parámetros **congelados**.
El objetivo se calcula con esta red congelada:

$$y_i = r + \gamma \max_b Q_{\theta^-}(s', b)$$

Los pesos $\theta^-$ solo se actualizan cada $C = 50$ pasos, copiando los pesos de la red online: $\theta^- \leftarrow \theta$.
Entre actualizaciones, el blanco se queda fijo — el entrenamiento es mucho más estable.

![Red objetivo]({{ '/23_reinforcement_learning/images/10_target_network.png' | url }})

---

## La función de pérdida

Reuniendo los dos elementos (experience replay + red objetivo):

$$\boxed{L(\theta) = \mathbb{E}\bigl[(y_i - Q_\theta(s_i, a_i))^2\bigr]}$$

| Símbolo | Significado |
|---------|-------------|
| $y_i = r + \gamma \max_b Q_{\theta^-}(s', b)$ | objetivo TD con red congelada |
| $Q_\theta(s_i, a_i)$ | predicción de la red online |
| $\theta$ | pesos de la red online (se actualizan en cada paso) |
| $\theta^-$ | pesos de la red objetivo (congelados, se copian cada $C$ pasos) |

> **Lectura:** Es una regresión MSE estándar — la predicción es $Q_\theta$, la etiqueta es $y_i$.
> La única novedad es que $y_i$ viene de otra red ($\theta^-$), no del ambiente directamente.
> Eso es todo lo que añade DQN sobre Q-learning: dos trucos de estabilización, misma idea de fondo.

---

## Pseudocódigo

Al inicio se crean dos redes con arquitectura idéntica e inicializadas con los mismos pesos.
En cada paso: el agente actúa con $\varepsilon$-greedy, almacena la transición $(s,a,r,s')$ en el buffer, muestrea un mini-lote aleatorio, calcula los objetivos con la red congelada, y hace un paso de gradiente sobre la red online.
Cada 50 pasos, los pesos de la red online se copian a la red objetivo.

```
DQN(α, γ, ε, C, num_episodios):
  Inicializa red online Q_θ y red objetivo Q_{θ^-} con pesos iguales
  Inicializa buffer D (capacidad 10 000)
  Para cada episodio:
    s ← estado_inicial()
    Mientras s no sea terminal:
      a ← ε-greedy(Q_θ, s)
      s', r, done ← ejecutar(a)
      Almacena (s, a, r, s', done) en D
      Si |D| ≥ 64:
        Muestrea mini-lote {(s_i, a_i, r_i, s'_i, done_i)} de D
        y_i ← r_i + γ · max_b Q_{θ^-}(s'_i, b) · (1 − done_i)
        θ ← θ − α · ∇_θ L(θ)    donde L = MSE(Q_θ(s_i, a_i), y_i)
      Cada C pasos: θ^- ← θ
      s ← s'
```

El factor `(1 − done_i)` en el cálculo del objetivo es un detalle importante: si el episodio terminó ($\text{done}=1$), no hay estado siguiente — el valor futuro es cero.

---

## Hacia adelante

La página 07 explora una familia de algoritmos distinta: en lugar de aprender $Q_\theta$ y derivar la política con $\arg\max$, ¿por qué no aprender la política $\pi_\theta$ directamente?
Esta idea — el gradiente de política — es la base de PPO y, en última instancia, del RLHF que entrena los modelos de lenguaje modernos.

La página 08 es el laboratorio aplicado: código ejecutable, demo en vivo y comparación de los cuatro métodos (Q-tabla, SARSA, Q-learning, DQN) sobre CartPole.
