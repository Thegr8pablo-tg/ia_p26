---
title: "El principio de optimalidad"
---

# 21.1 — El principio de optimalidad

> *"Lo que hagas ahora no solo te cuesta ahora: cambia el menú de mañana."*

---

## Un viaje que no se puede planear a pasos

Imagina que estás en la Ciudad de México y quieres llegar a Guadalajara en coche, al **menor costo total** (gasolina + tiempo + peajes). Miras el GPS y ves las primeras opciones:

- **Opción A** — tomar una salida rápida y barata en los primeros 20 km.
- **Opción B** — tomar una salida un poco más cara que te pone en una autopista directa.

Si decides **solo mirando el costo inmediato**, eliges A. Es más barata *ahora*.

Pero la opción A te lleva por un camino donde, 100 km más adelante, la única ruta viable pasa por una zona sin servicios y con cuotas altísimas. La opción B te cuesta un poco más al salir, pero te deja en una autopista que atraviesa todo el país con paradas económicas.

Al final del viaje, A te costó 2,400 pesos. B te habría costado 1,800.

¿Qué pasó? **La decisión de hoy cambió el menú de mañana.** Elegir A no fue solo pagar 150 pesos en lugar de 200 ahora: fue *inscribirte* en una secuencia de decisiones peores que no estaban disponibles cuando elegiste B.

Este es el rasgo distintivo de las **decisiones secuenciales**. A diferencia de los problemas de un solo tiro que vimos en el Módulo 9, aquí:

> La calidad de una decisión depende de lo que vas a poder decidir *después* de tomarla.

Optimizar paso a paso — "en cada momento hago lo que parece mejor" — no funciona. Se llama **estrategia codiciosa** (o *greedy*) y puede salir muy mal.

---

## Entonces, ¿por dónde empezamos a pensar?

Si no puedes optimizar paso a paso, ¿qué puedes hacer? Una opción es enumerar todas las secuencias posibles de decisiones, calcular el costo de cada una, y elegir la mejor. Pero eso **explota**: con 20 decisiones y 3 opciones cada una, son $3^{20} \approx 3.5 \times 10^9$ secuencias. Inviable.

Aquí es donde, en 1953, Richard Bellman notó algo aparentemente inocente — y que resultó ser una de las ideas más útiles del siglo XX.

---

## El principio de optimalidad

En *Dynamic Programming* (1957), Bellman enunció lo siguiente:

> *"An optimal policy has the property that whatever the initial state and initial decision are, the remaining decisions must constitute an optimal policy with respect to the state resulting from the first decision."*

Dicho en español, sin tecnicismos:

> **Cualquiera que sea tu primer paso, desde el estado al que llegaste el resto de tus pasos debe ser también óptimo.**

Léelo dos veces. Es sencillo y es fuerte.

**¿Por qué es fuerte?** Porque convierte un problema de **muchas decisiones** en una serie anidada de problemas de **una decisión + un subproblema**. En lugar de enumerar secuencias, solo tienes que contestar, recursivamente:

> *"Desde donde estoy ahora, ¿cuál es el costo mínimo total para llegar a la meta, asumiendo que de ahí en adelante sigo siendo óptimo?"*

Si puedes contestar esa pregunta para todos los estados posibles, **ya resolviste el problema**.

---

## La analogía del viaje

Volvamos al viaje CDMX → Guadalajara. Supón que sabes que la ruta óptima pasa por Querétaro en algún punto. El principio de optimalidad te dice algo muy concreto sobre esa ruta:

> **Si la mejor ruta CDMX → GDL pasa por Querétaro, entonces la subruta Querétaro → GDL tiene que ser, por sí sola, la mejor ruta Querétaro → GDL.**

¿Por qué? Supón que no lo fuera: supón que hay otra forma de ir de Querétaro a Guadalajara que cuesta menos. Entonces podrías construir una ruta nueva CDMX → Querétaro → (esa otra ruta) → GDL que costaría menos que la "óptima" original. Contradicción.

```
                          CDMX
                            │
                            │  (parte del viaje óptimo)
                            ▼
                        Querétaro ──┐
                            │       │
             ruta "óptima"  │       │  ¿otra ruta más barata?
             original  ◄────┤       │
                            ▼       ▼
                    Guadalajara  Guadalajara

  Si existiera una subruta Querétaro → GDL más barata, entonces la
  ruta original NO era la óptima. Contradicción: la subruta Querétaro → GDL
  debe ser óptima también.
```

Este argumento — "si el total es óptimo, cada subtramo también lo es" — es **la estructura recursiva** que Bellman descubrió. Funciona para rutas, funciona para planes de inversión, funciona para secuencias de decisiones de un agente, y funciona para cualquier problema donde las decisiones se apilan en el tiempo.

---

## Lo que viene

Todavía no tenemos una ecuación. Tenemos un principio: *el resto de una solución óptima es, en sí mismo, óptimo*. En la siguiente página vamos a escribir este principio como una ecuación — pero **no** te la voy a dictar. Vamos a llenar una tabla a mano para un problema muy pequeño (una escalera), y la ecuación va a aparecer sola, renglón por renglón. Cuando ya la hayas escrito cinco veces sin darte cuenta, le ponemos nombre.

Se llama **la ecuación de Bellman**.

---

**Siguiente:** [La escalera y la ecuación de Bellman →](02_escalera_bellman.md)
