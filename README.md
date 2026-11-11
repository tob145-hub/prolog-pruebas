# Pruebas por API: premisa normativa y derrotabilidad

Código, consignas, transcripciones, clasificación y documentos de las pruebas del trabajo presentado en el Seminario Trasandino (Valdivia). El método completo está en `metodo/` (anexo en PDF); el trabajo resume ese método en su anexo.

## Contenido

- `metodo/`: método completo de las pruebas (PDF).
- `protocolo/`: protocolo del 5 de noviembre de 2026, enmienda del 6 de noviembre, reglas de lectura, guía de criterios y manual del formulario. Los documentos fijos tienen versión en PDF.
- `seleccion-de-modelos/`: estimación de la variación del índice y las fuentes consultadas el 5 de noviembre (tabla del índice, páginas de cada modelo, metodología, catálogo de OpenRouter).
- `consignas.json`, `consignas-repregunta-v2.json`, `modelos.json`: casos (homicidio y bicicleta), preguntas P1 a P4, repreguntas, y los seis modelos con esfuerzo y proveedor fijo en OpenRouter.
- `datos/pruebas/`: tres repeticiones por modelo y caso (respuestas completas en `.json`, con el texto intermedio en el campo de razonamiento de cada respuesta; texto en `.md`; `manifiesto.json` por ejecución; registros de cada lanzamiento). El turno 3 de P1 de Opus 5.5 figura como `-ERROR-` en las seis ejecuciones (bloqueo `content_filter` del proveedor); no se reemplazó.
- `datos/repregunta-v2/`: turno 3 de P1 con la repregunta v2, 36 llamadas. Reemplaza al turno 3 original en el análisis.
- `datos/texto-intermedio/`: el texto intermedio ("razonamiento") de cada respuesta, separado y rotulado, extraído de los `.json` (unas 740.000 palabras). Cinco de los seis modelos lo devuelven como texto; GPT-6 Astra lo devuelve cifrado, y solo hay resúmenes en algunas respuestas.
- `bloqueo-de-opus/`: consulta a soporte de Anthropic sobre el bloqueo de Opus 5.5 y su respuesta literal.
- `codigo/`: programa que ejecutó las consultas (`correr.py`), lanzadores, programas que armaron las fichas, las lecturas y los formularios, y los que calcularon el acuerdo, el alfa y los patrones. Algunos leen rutas del proyecto desde la variable `RAIZ_PROYECTO`.
- `transcripciones-numeradas/` y `lectura-por-tandas/`: material de lectura de los autores, con códigos en lugar del nombre del modelo; la clave está en `clasificacion/`.
- `formularios/`: formularios de clasificación (HTML) de cada autor.
- `clasificacion/`: marcas de cada autor, sus ajustes y revisiones, clasificación común, y las claves que asocian cada código con su modelo.
- `analisis/`: acuerdo entre clasificadores, patrones por modelo y lectura del marco procesal con los indicios buscados.

Los pilotos (no forman parte de los resultados) no se publican aquí; están a disposición.

## Uso

La clave de OpenRouter se lee de la variable de entorno `OPENROUTER_API_KEY`. Cada programa tiene `--help`.

## Licencias

- Código (`codigo/`): licencia MIT (`LICENSE-codigo`).
- Todo lo demás (transcripciones, texto intermedio, clasificación, análisis, protocolo y documentos): CC BY 4.0 (`LICENSE-datos`).

## Siglas

TJS y JLR son las iniciales de los dos autores del trabajo. Aparecen así en `clasificacion/`, `analisis/` y en los programas que calculan el acuerdo.

## Gasto

El costo de cada consulta a la API figura en el `manifiesto.json` de cada ejecución (`gastado_respuestas_usd`). Las pruebas se pagaron con saldo prepago de OpenRouter, sin recarga automática.

## Cita

DOI de la versión congelada (Zenodo): [Falta: DOI].
