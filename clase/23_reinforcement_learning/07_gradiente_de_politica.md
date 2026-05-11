---
title: "07 · Gradiente de política"
summary: "REINFORCE, Actor-Critic, PPO y la conexión con RLHF: aprender π_θ directamente"
---

## Cuándo $\arg\max_a Q(s,a)$ se rompe

DQN aprende $Q_\theta(s,a)$ y actúa tomando $\arg\max_a Q_\theta(s,a)$.
Para CartPole (2 acciones discretas) esto funciona perfectamente.
Pero hay dos situaciones donde $\arg\max$ falla de raíz:

**Caso 1 — acciones continuas:**
Un robot con 30 articulaciones tiene $\mathbb{R}^{30}$ como espacio de acciones.
Calcular $\arg\max_a Q_\theta(s,a)$ sobre un espacio continuo requiere lanzar un optimizador numérico en cada paso de tiempo — costoso, lento e inestable.

**Caso 2 — políticas estocásticas óptimas:**
En piedra-papel-tijera, cualquier política determinista es explotable: si el oponente detecta que siempre juegas piedra, siempre jugará papel.
La única política óptima es elegir uniformemente al azar entre las tres opciones.
Un método basado en $\arg\max$ siempre devuelve una acción determinista — no puede representar esta solución.

**La solución:**
En lugar de aprender $Q$ y derivar la política después, aprender directamente la política como una distribución paramétrica:

$$\pi_\theta(a \mid s) \quad \text{— una distribución sobre acciones dado el estado}$$

Los parámetros $\theta$ son los pesos de una red neuronal que mapea estados a distribuciones de probabilidad sobre acciones.
En espacios discretos: un vector softmax.
En espacios continuos: los parámetros de una distribución gaussiana.

---

## REINFORCE

### El teorema del gradiente de política

¿Cómo subir por el gradiente del retorno esperado $J(\theta) = \mathbb{E}_{\pi_\theta}[G_0]$?
El teorema del gradiente de política (Williams, 1992) establece:

$$\boxed{\nabla_\theta J(\theta) \propto \mathbb{E}\bigl[G_t \nabla_\theta \log \pi_\theta(a_t \mid s_t)\bigr]}$$

> **Lectura:** El término $\nabla_\theta \log \pi_\theta(a_t \mid s_t)$ apunta en la dirección que aumenta la probabilidad de $a_t$ en $s_t$.
> Al multiplicarlo por $G_t$, escalamos ese empuje proporcionalmente al retorno obtenido:
> si el episodio fue bueno, aumentamos la probabilidad de las acciones tomadas; si fue malo, la disminuimos.

### La función de pérdida

Como hacemos descenso de gradiente (no ascenso), minimizamos el negativo:

$$\boxed{L(\theta) = -\mathbb{E}\bigl[G_t \log \pi_\theta(a_t \mid s_t)\bigr]}$$

| Símbolo | Significado |
|---------|-------------|
| $G_t$ | Retorno acumulado desde el paso $t$: suma de recompensas futuras con descuento |
| $\log \pi_\theta(a_t \mid s_t)$ | Log-probabilidad de la acción tomada en el estado actual |
| $\theta$ | Parámetros de la política (pesos de la red) |

### Pseudocódigo

```
REINFORCE(α, γ, num_episodios):
  Inicializa política π_θ
  Para cada episodio:
    Genera trayectoria τ = (s_0, a_0, r_1, s_1, ..., s_T) siguiendo π_θ
    Para cada paso t = 0, ..., T-1:
      G_t ← suma de r_{t+k+1} · γ^k para k = 0, 1, ...
      θ ← θ + α · G_t · ∇_θ log π_θ(a_t | s_t)
```

---

## El problema de la varianza

$G_t$ depende de **toda la trayectoria futura**: si en el paso 10 el agente tuvo mala suerte, $G_{10}$ será bajo aunque las acciones en los pasos 0-9 fueran excelentes.
Una sola muestra de trayectoria produce una estimación ruidosa del gradiente.

Dos ejecuciones de REINFORCE en el mismo problema pueden producir gradientes que apuntan en direcciones completamente distintas, simplemente por variación aleatoria en la exploración.

**Analogía:** calificar una decisión puntual de un estudiante por cómo le fue durante toda la semana, no por si esa decisión específica fue correcta.
El ruido de "toda la semana" enmascara la señal de "esta decisión".

**Solución: función de referencia (baseline)**

Si restamos una función $b(s_t)$ que depende solo del estado:

$$G_t \to G_t - b(s_t)$$

La esperanza del gradiente no cambia (los baselines no sesgan el gradiente), pero si $b(s_t) \approx \mathbb{E}[G_t \mid s_t]$, la varianza cae drásticamente.
¿Qué función estima $\mathbb{E}[G_t \mid s_t]$? La función de valor de estado: $V(s_t)$.
Esto nos lleva directamente al Actor-Critic.

---

## Actor-Critic

La idea es mantener dos redes simultáneamente: una aprende QUÉ hacer (el actor), la otra aprende cuánto vale cada estado (el crítico).

```
Estado s ──┬──▶ Actor  π_θ(a|s)   ──▶  acción a
           │
           └──▶ Crítico V_φ(s)    ──▶  valor de referencia
                     │
                     ▼
              δ_t = r + γV_φ(s') − V_φ(s)   (ventaja aproximada)
```

| Componente | Parámetros | Rol |
|------------|-----------|-----|
| Actor $\pi_\theta(a \mid s)$ | $\theta$ | Aprende QUÉ hacer — distribución sobre acciones |
| Crítico $V_\phi(s)$ | $\phi$ | Aprende cuánto vale cada estado — baseline aprendido |

### La estimación de ventaja

El error TD del crítico sirve como estimación de la ventaja:

$$\boxed{A(s,a) \approx \delta_t = r + \gamma V_\phi(s') - V_\phi(s)}$$

> **Lectura:** $\delta_t > 0$ significa que la acción tomada resultó mejor de lo esperado por el crítico — hay que aumentar su probabilidad.
> $\delta_t < 0$ significa que fue peor de lo esperado — hay que disminuirla.
> El crítico calibra el actor: no "qué tan bueno fue el episodio", sino "cuánto mejor o peor que lo esperado fue esta acción".

### Dos actualizaciones por transición

En cada transición $(s, a, r, s')$:

1. **Actor:** $\theta \leftarrow \theta + \alpha_\theta \cdot \delta_t \cdot \nabla_\theta \log \pi_\theta(a \mid s)$
2. **Crítico:** $\phi \leftarrow \phi - \alpha_\phi \cdot \delta_t \cdot \nabla_\phi V_\phi(s)$

El actor sube la probabilidad de acciones con $\delta_t > 0$ y la baja para $\delta_t < 0$.
El crítico minimiza su propio error de predicción.

---

## PPO: actualizaciones seguras

Actor-Critic funciona, pero hay un problema práctico: si el paso de gradiente es demasiado grande, la política nueva $\pi_\theta$ puede ser muy diferente de la anterior.
Esto puede destruir el aprendizaje previo — las políticas de RL son frágiles ante cambios bruscos.

### El ratio de probabilidad

Definimos el ratio entre la política nueva y la política con la que se recogieron los datos:

$$r_t(\theta) = \dfrac{\pi_\theta(a_t \mid s_t)}{\pi_{\theta_\text{old}}(a_t \mid s_t)}$$

Si $r_t = 1$, la política no cambió.
Si $r_t > 1$, la acción $a_t$ ahora es más probable que antes.
Si $r_t < 1$, es menos probable.

### El objetivo con clipping

PPO (Schulman et al., 2017) limita el cambio de política con un clipping simple:

$$\boxed{L^{\text{CLIP}}(\theta) = \mathbb{E}\Bigl[\min\bigl(r_t(\theta)\hat{A}_t,\; \text{clip}(r_t(\theta), 1-\varepsilon, 1+\varepsilon)\hat{A}_t\bigr)\Bigr]}$$

donde $\hat{A}_t$ es la estimación de ventaja y $\varepsilon \approx 0.2$ es el radio de confianza.

> **Intuición:** El ratio $r_t(\theta)$ mide cuánto cambió la política.
> Si $r_t > 1+\varepsilon$, la política nueva es mucho más probable que la anterior — probablemente demasiado.
> El clipping congela el gradiente cuando el cambio es excesivo.
> Resultado: actualizaciones limitadas por un factor de confianza, sin necesidad de líneas de búsqueda ni métodos de segundo orden.

:::exercise{title="¿Por qué tomar el mínimo?"}

El objetivo PPO toma el mínimo de dos expresiones: el objetivo sin clip y el objetivo con clip.

¿Por qué tomar el mínimo en lugar de simplemente clipear?

Piensa en dos casos separados: cuando la ventaja $\hat{A}_t > 0$ (la acción fue buena) y cuando $\hat{A}_t < 0$ (la acción fue mala).
¿Qué ocurre si solo se aplica clipping sin tomar el mínimo?
¿Podría el agente beneficiarse haciendo cambios grandes cuando la ventaja es negativa?

:::

---

## RLHF: el mismo PPO, distinta recompensa

El aprendizaje por refuerzo con retroalimentación humana (RLHF) es la técnica que convierte un modelo de lenguaje preentrenado en un asistente útil.
El algoritmo de fondo es exactamente PPO — solo cambia la fuente de la recompensa.

### El pipeline en tres pasos

**Paso 1 — Preentrenamiento:**
El modelo de lenguaje aprende a predecir el siguiente token sobre un corpus masivo de texto.
Al final de esta fase, el modelo puede generar texto coherente, pero no necesariamente útil o seguro.

**Paso 2 — Modelo de recompensa:**
Se presentan pares de respuestas (A vs B) a evaluadores humanos, quienes indican cuál prefieren.
Con estos datos de preferencia se entrena una red (el modelo de recompensa) para predecir qué respuestas preferirían los humanos.
Esta red es la función de recompensa $R$.

**Paso 3 — Fine-tuning con PPO:**
El LLM es el "agente"; cada respuesta generada es una "trayectoria".
El modelo de recompensa evalúa cada respuesta.
Se añade una penalización KL para evitar que el modelo se aleje demasiado del LLM original:

$$R_{\text{total}} = R_{\text{humano}}(s) - \beta \cdot D_{\text{KL}}(\pi_\theta \| \pi_{\text{ref}})$$

PPO actualiza los pesos del LLM para maximizar $R_{\text{total}}$.

### La conexión

La diferencia con RL estándar es solo la fuente de la recompensa: viene de preferencias humanas en vez de un simulador.
El algoritmo — PPO — es el mismo.
La teoría — gradiente de política, función de ventaja, ratio de probabilidad — es la misma.

ChatGPT (OpenAI), Claude (Anthropic) y Gemini (Google) usan variantes de este mismo pipeline.

---

## El arco completo

Empezamos con una escalera de seis estados y una tabla de 10 celdas.
Introdujimos Q-learning: aprender $Q^∗$ sin conocer $T$ ni $R$, solo interactuando.
DQN reemplazó la tabla por una red neuronal para escalar a estados continuos.
El gradiente de política aprendió $\pi_\theta$ directamente, evitando el $\arg\max$ en espacios continuos.
PPO añadió estabilidad con actualizaciones limitadas.
Y RLHF usó exactamente ese PPO para entrenar los modelos de lenguaje más avanzados del mundo.

La idea central no cambió en ningún paso: **encontrar una política que maximice la recompensa esperada**.
