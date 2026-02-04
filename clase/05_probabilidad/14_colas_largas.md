# Colas Largas (Fat Tails)

Cuando los teoremas clásicos fallan — y por qué esto importa más de lo que crees.

> "The central limit theorem has limitations... In fat-tailed domains, most of what you observe comes from the tails."
> — Nassim Nicholas Taleb

## El Problema Fundamental

Todo lo que vimos sobre LGN y TLC asume que la varianza es finita. Pero:

1. ¿Qué pasa si la varianza es infinita?
2. ¿Qué pasa si es finita pero tan grande que es *prácticamente* infinita?
3. ¿Cómo sabemos si estamos en esa situación?

**Spoiler:** Muchos fenómenos del mundo real tienen colas más pesadas de lo que asumimos — y tratarlos como normales puede ser catastrófico.

---

## Definición Formal de Fat Tails

### Clasificación de Colas

Una distribución tiene **colas pesadas** (fat tails) si su función de distribución de cola decrece más lentamente que exponencial.

**Thin-tailed (Colas ligeras):**
$$P(X > x) \sim e^{-\lambda x} \quad \text{(exponencial o más rápido)}$$

Ejemplos: Normal, Exponencial, Poisson

**Fat-tailed (Colas pesadas):**
$$P(X > x) \sim x^{-\alpha} \quad \text{(ley de potencias)}$$

Ejemplos: Pareto, Cauchy, Student-t con pocos grados de libertad

### El Exponente de Cola $\alpha$

Para una distribución Pareto-like:
$$P(X > x) \propto x^{-\alpha}$$

El exponente $\alpha$ determina qué momentos existen:

| $\alpha$ | Media | Varianza | Curtosis | Comportamiento |
|----------|-------|----------|----------|----------------|
| $\alpha \leq 1$ | ∞ | ∞ | ∞ | Extremadamente fat-tailed |
| $1 < \alpha \leq 2$ | Finita | ∞ | ∞ | Fat-tailed severo |
| $2 < \alpha \leq 3$ | Finita | Finita | ∞ | Fat-tailed moderado |
| $3 < \alpha \leq 4$ | Finita | Finita | Finita | Semi-fat-tailed |
| $\alpha > 4$ | Finita | Finita | Finita | Casi thin-tailed |

### Definición Intuitiva

> Una distribución es **fat-tailed** si un pequeño número de observaciones extremas domina la suma total.

En una distribución normal, eventos de 5 o 6 sigmas son prácticamente imposibles ($1$ en millones/billones).

En una distribución fat-tailed, eventos extremos ocurren con frecuencia "sorprendente".

---

## El Criterio de Taleb: Kappa

Nassim Taleb propone una métrica práctica para detectar fat tails:

$$\kappa = \frac{\max_{i \leq n} X_i}{\sum_{i=1}^n X_i}$$

**Interpretación:**
- Si $\kappa \approx 1/n$: distribución thin-tailed (cada observación contribuye igual)
- Si $\kappa \to 1$: distribución fat-tailed (una observación domina)

### Ejemplo Intuitivo

**Riqueza de 1000 personas:**
- Si la más rica tiene $1M y el promedio es $100K → $\kappa \approx 0.01$ (thin)
- Si la más rica tiene $1B y el promedio es $1M → $\kappa \approx 0.5$ (fat)

---

## Ejemplos del Mundo Real

![Extremos importan]({{ '/05_probabilidad/images/extremos_importan.png' | url }})

*En fat tails, el top 10% puede contribuir >50% del total. En thin tails, la contribución es más uniforme.*

### 1. Distribución de Riqueza

La riqueza sigue una distribución Pareto con $\alpha \approx 1.5$:
- El 1% más rico posee ~50% de la riqueza global
- Jeff Bezos solo tiene más que el PIB de muchos países

**Implicación:** El "promedio" de riqueza es engañoso. La mediana es mucho más representativa.

### 2. Tamaño de Ciudades (Ley de Zipf)

$$\text{Población de ciudad rank } r \propto r^{-1}$$

- Tokyo: ~38 millones
- Ciudad #100: ~3 millones
- Ciudad #1000: ~300 mil

### 3. Rendimientos Financieros

Los retornos de acciones NO son normales:
- Lunes Negro (1987): caída de 22.6% (un evento de ~20 sigmas si fuera normal)
- Flash Crash (2010): caída de 9% en minutos
- Eventos de "6 sigmas" ocurren varias veces por década

**Si los mercados fueran normales:**
- Un evento de 5σ ocurriría cada 14,000 años
- **En realidad:** ocurren cada pocos años

### 4. Terremotos

La magnitud de terremotos sigue ley de potencias (Gutenberg-Richter):
$$\log_{10} N = a - bM$$

Un terremoto de magnitud 8 no es "un poco peor" que uno de magnitud 7 — libera ~32 veces más energía.

### 5. Pandemias y Eventos de Mortalidad

La distribución de muertes por pandemias es fat-tailed:
- Gripe estacional: miles de muertes
- COVID-19: millones
- Gripe Española (1918): 50-100 millones
- Peste Negra: ~200 millones

### 6. Éxito de Libros/Películas/Apps

- La mayoría de libros venden pocas copias
- Unos pocos venden millones
- Harry Potter vs el libro promedio: factor de ~1 millón

### 7. Cyberataques y Fallas de Sistemas

- La mayoría de bugs son menores
- Unos pocos causan daños de billones (Equifax, SolarWinds)

---

## Por Qué el TLC Falla (y cuándo la LGN es lenta)

### Tres Regímenes según $\alpha$

Es crucial entender qué pasa según el exponente de cola $\alpha$:

| Régimen | Media | Varianza | LGN | TLC | Ejemplo |
|---------|-------|----------|-----|-----|---------|
| $\alpha > 2$ | Finita | Finita | ✓ Funciona | ✓ Funciona | Pareto α=3 |
| $1 < \alpha \leq 2$ | Finita | **Infinita** | ✓ Funciona (lento) | ✗ Falla | Pareto α=1.5 |
| $\alpha \leq 1$ | Infinita | Infinita | ✗ Falla | ✗ Falla | Cauchy |

### Caso Extremo: Cauchy (α = 1)

Sea $X_1, X_2, \ldots$ i.i.d. Cauchy estándar.

El promedio $\bar{X}_n = \frac{1}{n}\sum X_i$ es... ¡también Cauchy estándar!

No importa cuántos datos tengas, el promedio **no converge** porque la media **no existe**.

### Caso Intermedio: Pareto con $1 < \alpha \leq 2$

Este es el caso más engañoso. Para Pareto con α=1.5:
- La media **existe** y es finita: $\mu = \frac{\alpha}{\alpha-1} = 3$
- La varianza es **infinita**
- La LGN **sí aplica**: el promedio $\bar{X}_n \to 3$ eventualmente
- **PERO** la convergencia es extremadamente lenta

**¿Qué tan lenta?**

La velocidad de convergencia ya no es $1/\sqrt{n}$ sino aproximadamente $1/n^{1-1/\alpha}$. Para α=1.5, esto significa convergencia como $1/n^{1/3}$ — necesitarías **$n = 10^9$** para lograr lo que con variables normales logras con $n = 1000$.

### El TLC Falla Aunque la LGN Funcione

Cuando $1 < \alpha \leq 2$:
- El promedio SÍ converge a la media verdadera (LGN)
- Pero la **distribución** del promedio NO es normal (TLC falla)
- La distribución límite es una **distribución estable** asimétrica
- Los intervalos de confianza basados en normalidad son **incorrectos**

![Convergencia: Normal vs Pareto]({{ '/05_probabilidad/images/convergencia_fattail.png' | url }})

*Las gráficas muestran que Pareto α=3 (varianza finita) converge rápido y limpiamente, mientras que Pareto α=1.5 y α=2 (varianza infinita) convergen eventualmente pero con mucha más volatilidad y lentitud.*

---

## El Error del Pavo de Acción de Gracias

> "Consider a turkey that is fed every day. Every single feeding will firm up the bird's belief that it is the general rule of life to be fed every day by friendly members of the human race... On the Wednesday before Thanksgiving, something unexpected will happen to the turkey."
> — Taleb, *The Black Swan*

**El problema:** Usar datos históricos para estimar riesgos futuros asume que el futuro será como el pasado.

En dominios fat-tailed:
- La mayor pérdida futura será probablemente mayor que cualquier pérdida histórica
- El "peor caso" histórico subestima el verdadero peor caso

---

## Consecuencias Prácticas

### 1. El Promedio es Engañoso

En distribuciones fat-tailed, el promedio muestral:
- Es muy **volátil** (cambia drásticamente con nuevas observaciones)
- Converge tan **lentamente** que es prácticamente inútil en tamaños de muestra realistas
- Puede estar **dominado por una sola observación** extrema
- **No es representativo** del "caso típico" (la mediana puede ser muy diferente)

**Recomendación:** Usar la mediana o cuantiles en lugar del promedio.

### 2. Los Intervalos de Confianza Son Inútiles

Los intervalos de confianza estándar asumen normalidad.

Con fat tails:
- El intervalo del 95% puede excluir eventos que ocurren regularmente
- La cola "fuera del intervalo" contiene la mayor parte del riesgo

### 3. El Tamaño de Muestra "Suficiente" Es Enorme

Para distribuciones normales: $n=30$ suele bastar para que el TLC aplique.

Para distribuciones fat-tailed con $1 < \alpha \leq 2$:
- **Teóricamente** el promedio converge (la media existe)
- **Prácticamente** necesitarías $n > 10^6$ o más para convergencia estable
- La convergencia es tan lenta que en la práctica es como si no convergiera
- Y aún con millones de datos, una nueva observación extrema puede cambiar todo

![Una observación cambia todo]({{ '/05_probabilidad/images/una_observacion_cambia_todo.png' | url }})

*En fat tails, añadir UNA sola observación puede cambiar drásticamente el promedio. Este es el efecto de los "cisnes negros".*

### 4. Diversificación No Funciona Igual

En finanzas, la diversificación asume que los riesgos son independientes.

En eventos fat-tailed:
- Los eventos extremos tienden a ocurrir juntos (correlación en las colas)
- Cuando más necesitas diversificación, menos funciona

---

## Caso de Estudio: Value at Risk (VaR) y la Crisis de 2008

### ¿Qué es el VaR?

El **Value at Risk** (Valor en Riesgo) es LA medida estándar de riesgo financiero usada por bancos, fondos de inversión y reguladores.

**Definición:** El VaR al nivel de confianza $\alpha$ es la pérdida máxima que no se superará con probabilidad $\alpha$.

$$\text{VaR}_\alpha = -\inf\{x : P(R \leq x) \geq 1-\alpha\}$$

**En palabras simples:**
- VaR₉₉ = "El 99% de los días, no perderemos más que esta cantidad"
- VaR₉₅ = "El 95% de los días, no perderemos más que esta cantidad"

### Cómo se Calcula (Método Paramétrico)

Asumiendo que los retornos $R$ son normales:

$$R \sim \mathcal{N}(\mu, \sigma^2)$$

El VaR se calcula como:

$$\text{VaR}_\alpha = -(\mu + z_\alpha \cdot \sigma)$$

donde $z_\alpha$ es el cuantil de la normal estándar:
- Para VaR₉₉: $z_{0.01} \approx -2.33$
- Para VaR₉₅: $z_{0.05} \approx -1.65$

**Ejemplo:** Si $\mu = 0.05\%$ diario y $\sigma = 1\%$ diario:
$$\text{VaR}_{99} = -(0.05\% - 2.33 \times 1\%) \approx 2.28\%$$

"El 99% de los días, no perderemos más del 2.28%"

### El Problema: La Normalidad es Falsa

El VaR paramétrico asume normalidad. Pero los retornos financieros son **fat-tailed**.

**Consecuencias:**

1. **Subestima la frecuencia de pérdidas extremas**
   - El modelo dice: "violaciones del VaR₉₉ en 1% de los días"
   - La realidad: violaciones en 2-5% de los días

2. **Subestima la severidad de las pérdidas**
   - Cuando el VaR falla, falla catastróficamente
   - El modelo dice "máximo 2.3%", pero la pérdida real es 8%, 15%, 22%...

3. **Da falsa sensación de seguridad**
   - Los gestores creen que tienen el riesgo "controlado"
   - Hasta que llega un cisne negro

### La Crisis de 2008: VaR en Acción

Antes de la crisis, los bancos reportaban:
- "Nuestro VaR₉₉ diario es $50 millones"
- "Estamos bien capitalizados"

**Lo que pasó:**
- Días con pérdidas de $500M, $1B, $5B...
- Eventos que según el modelo eran de "una vez cada 10,000 años"
- Ocurrieron múltiples veces en semanas

**Cita de David Viniar (CFO de Goldman Sachs, agosto 2007):**
> "We were seeing things that were 25-standard deviation moves, several days in a row."

Un evento de 25σ en una distribución normal tiene probabilidad $\approx 10^{-135}$. Eso es menos probable que ganar la lotería todos los días durante un año. Pero "ocurrió" varios días seguidos.

**La realidad:** No fueron eventos de 25σ. Los retornos simplemente no son normales.

### Expected Shortfall (ES): Una Alternativa

El **Expected Shortfall** (también llamado CVaR o Tail VaR) responde:

> "Cuando las cosas van mal, ¿qué tan mal van?"

$$\text{ES}_\alpha = E[R | R < -\text{VaR}_\alpha]$$

Es el promedio de las pérdidas en los peores $(1-\alpha)\%$ de casos.

**Ventajas:**
- Considera la severidad, no solo la frecuencia
- Es una medida "coherente" de riesgo (tiene mejores propiedades matemáticas)
- Reguladores (Basilea III) ahora lo requieren

**Desventaja:** Sigue siendo sensible al modelo de distribución.

### Lección para Fat Tails

En dominios fat-tailed, las medidas de riesgo basadas en normalidad son **peligrosamente optimistas**.

**Soluciones:**
1. Usar distribuciones fat-tailed (Student-t, Pareto)
2. Usar métodos no paramétricos (simulación histórica)
3. Complementar con stress testing (escenarios extremos)
4. **Humildad epistemológica:** aceptar que no podemos cuantificar todos los riesgos

---

## Cómo Detectar Fat Tails

### 1. Gráfico Log-Log

Si $P(X > x) \propto x^{-\alpha}$, entonces:
$$\log P(X > x) = -\alpha \log x + c$$

Un gráfico log-log de la cola debería ser lineal.

### 2. QQ-Plot

Compara los cuantiles de tus datos con los cuantiles normales.

- Línea recta = datos normales
- Curvatura en los extremos = colas pesadas

### 3. Kappa de Taleb

Calcula $\kappa$ y observa cómo escala con $n$.

![Kappa de Taleb]({{ '/05_probabilidad/images/kappa_taleb.png' | url }})

*El criterio κ mide concentración: κ alto = una observación domina el total.*

### 4. Estimación de $\alpha$ (Hill Estimator)

$$\hat{\alpha} = \left(\frac{1}{k}\sum_{i=1}^k \log\frac{X_{(n-i+1)}}{X_{(n-k)}}\right)^{-1}$$

donde $X_{(i)}$ son las estadísticas de orden.

![Diagnósticos de fat tails]({{ '/05_probabilidad/images/fattail_diagnostics.png' | url }})

*Nota: Esta imagen se genera automáticamente al ejecutar `lab_probabilidad.py`*

---

## Qué Hacer con Fat Tails

### 1. Reconocer el Dominio

**Mediocristán** (thin-tailed):
- Alturas, pesos, temperaturas
- El promedio es informativo
- Los extremos no dominan

**Extremistán** (fat-tailed):
- Riqueza, ventas, catástrofes
- El promedio es engañoso
- Los extremos dominan

![Mediocristán vs Extremistán]({{ '/05_probabilidad/images/mediocristán_extremistan.png' | url }})

*Comparación de convergencia del promedio: en Mediocristán converge, en Extremistán es inestable.*

### 2. Usar Estadísticas Robustas

En lugar de:
- Media → usar **mediana**
- Varianza → usar **MAD** (median absolute deviation)
- Correlación → usar **correlación de rangos**

### 3. Aplicar el Principio de Precaución

En dominios fat-tailed:
- Asume que el peor caso será peor de lo observado
- Construye sistemas que sobrevivan a eventos extremos
- Evita exposición a "cola izquierda" (eventos catastróficos)

### 4. Entender la Asimetría

No todas las colas importan igual:
- **Cola derecha positiva** (ganancias): puede ser deseable (startups)
- **Cola izquierda negativa** (pérdidas): puede ser catastrófica (riesgos)

---

## El Mensaje de Taleb

> "In Extremistan, one single observation can disproportionately impact the aggregate."

Las herramientas estadísticas clásicas fueron diseñadas para Mediocristán. Aplicarlas en Extremistán es como usar un mapa de Kansas para navegar los Himalayas.

**La humildad epistemológica es clave:**
- No sabemos lo que no sabemos
- Los eventos raros son más importantes que los frecuentes
- La incertidumbre sobre la incertidumbre (meta-incertidumbre) importa

---

## Laboratorio de Simulación

Para explorar estos conceptos visualmente, ejecuta el laboratorio de simulación:

```bash
python lab_probabilidad.py
```

Esto generará imágenes comparando:
- Convergencia de promedios: Normal vs Cauchy vs Pareto
- Distribución de sumas: thin-tailed vs fat-tailed
- Diagnósticos de fat tails

---

## Referencias

1. **Taleb, N.N.** *Statistical Consequences of Fat Tails* (Technical Incerto, 2020)
2. **Taleb, N.N.** *The Black Swan* (2007)
3. **Mandelbrot, B.** *The Misbehavior of Markets* (2004)
4. **Clauset, Shalizi, Newman** "Power-law distributions in empirical data" (2009)

---

## Resumen

| Concepto | Thin-Tailed | Fat-Tailed |
|----------|-------------|------------|
| Colas | Decaen exponencialmente | Decaen como potencia |
| Varianza | Finita | Puede ser infinita |
| TLC | Aplica | No aplica o converge muy lento |
| Promedio | Estable | Volátil |
| Eventos extremos | Raros | Frecuentes |
| Ejemplo | Alturas | Riqueza |

**Mensaje final:** Antes de aplicar cualquier técnica estadística, pregúntate: ¿Estoy en Mediocristán o Extremistán?

---

**Siguiente:** [Laboratorio de Simulación](lab_probabilidad.py) | [← Volver al índice](00_index.md)
