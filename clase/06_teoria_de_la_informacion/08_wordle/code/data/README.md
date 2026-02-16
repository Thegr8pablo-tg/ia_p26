---
title: "Datos para el proyecto Wordle"
---

# Datos

## `mini_spanish_5.txt`

Lista mínima (~45 palabras) de 5 letras en español sin acentos. Sirve como fallback para correr el torneo sin dependencias externas.

## Listas más grandes

Para resultados más representativos, consigue una lista más grande (1,000–10,000 palabras). Opciones:

1. **OpenSLR** (Spanish word list): descarga de https://www.openslr.org/21/ y filtra a 5 letras.
2. **RAE** (Real Academia Española): extrae lemas del diccionario.
3. **wordfreq** (Python): `pip install wordfreq` y genera una lista con frecuencias.

Formato esperado: un archivo de texto con una palabra por línea (minúsculas, sin acentos).

```bash
# Ejemplo con el torneo:
python tournament.py --words data/mi_lista_grande.txt
```
