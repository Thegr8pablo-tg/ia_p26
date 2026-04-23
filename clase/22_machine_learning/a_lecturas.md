---
title: "Lecturas"
---

# Lecturas: Machine Learning Basics

{% from "components/html_embed.njk" import render as html_embed %}

{{ html_embed(
  "https://www.deeplearningbook.org/contents/ml.html",
  "Deep Learning (Goodfellow, Bengio & Courville) — Capítulo 5: Machine Learning Basics",
  [
    {"page": 2,  "label": "Ir a p. 96 (Lectura 1)"},
    {"page": 57, "label": "Ir a p. 151 (Lectura 2)"}
  ]
) }}

---

## Instrucciones

Vas a leer **dos rangos de páginas** del Capítulo 5. Los números son **páginas del libro** (las que ves impresas arriba de cada página renderizada), no "página N del PDF".

| Lectura | Páginas del libro | Qué cubre (secciones aproximadas) |
|:-------:|:-----------------:|-----------------------------------|
| **1** | **96 – 132** | 5.1 Learning Algorithms; 5.2 Capacity, Overfitting, Underfitting; 5.3 Hyperparameters and Validation Sets; 5.4 Estimators, Bias, Variance; 5.5 Maximum Likelihood Estimation; 5.6 Bayesian Statistics; 5.7 Supervised Learning Algorithms; 5.8 Unsupervised Learning Algorithms; 5.9 Stochastic Gradient Descent |
| **2** | **151 – 161** | Final del capítulo — 5.11 Challenges Motivating Deep Learning: *the curse of dimensionality*, *local constancy and smoothness regularization*, *manifold learning* |

### ¿Por qué saltamos de la p. 132 a la 151?

No es accidente. Las páginas **133–150** (secciones 5.10 "Building a Machine Learning Algorithm" y parte de 5.11) son útiles pero **redundantes** con los conceptos que ya cubriste en el primer rango — retoman regularización, capacidad, y entrenamiento con otros ejemplos. En cambio, el final del capítulo (**151–161**) es el **puente directo a la siguiente clase**: las ideas que motivan por qué necesitamos redes neuronales profundas en lugar de modelos tradicionales.

Si después de clase te interesa, puedes leer las páginas intermedias — son complementarias, no contradictorias. Pero para esta clase, los dos rangos son suficientes.

---

## Cómo leer

- **Identifica** las ideas principales de cada sección; no te obsesiones con derivar cada fórmula.
- **Marca** los términos nuevos que no hayas visto (*capacidad*, *VC-dimension*, *MLE*, *MAP*, *manifold hypothesis*) — los definimos en clase.
- **Conecta** con lo que ya sabes: cuando leas "entropía cruzada" piensa en Módulo 6; cuando leas "gradiente estocástico" piensa en Módulo 7.
- Los **botones arriba del iframe** te llevan directo al inicio de cada rango. Úsalos.

---

## Fuente

Goodfellow, I., Bengio, Y., & Courville, A. (2016). *Deep Learning*. MIT Press.
Capítulo 5 — *Machine Learning Basics*. Disponible en línea en:
<https://www.deeplearningbook.org/contents/ml.html>

El libro está libremente disponible por capítulo en la página de los autores. Si te interesa leer el libro completo, puedes comprarlo en [MIT Press](https://mitpress.mit.edu/9780262035613/deep-learning/) o [Amazon](https://www.amazon.com/Deep-Learning-Adaptive-Computation-Machine/dp/0262035618/).
