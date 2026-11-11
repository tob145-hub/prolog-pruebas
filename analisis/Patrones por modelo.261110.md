# Patrones por modelo

Fecha: 10 de noviembre de 2026. Lo clasificado por TJS en las 36 respuestas de cada tipo, desglosado por modelo con la clave del formulario, abierta con autorización de TJS el 9 de noviembre después de terminar la clasificación. Descriptivo: con 6 respuestas por modelo y tipo no hay inferencia estadística.

## Qué datos entran

- Marcas de TJS tras su revisión (`clasificacion-TJS-revisada3-261110.csv`) en las 36 pantallas de cada tipo (primeras respuestas y repreguntas).
- Se excluyen las 5 dudosas del paso 2 (error en una pantalla, atribución en una, razón en la bicicleta en dos y hechos en una). El resto de las pantallas comunes con JLR conserva la marca de TJS, que es la clasificación común (o coincide con la de JLR). En la columna "n (comunes)" va el número de pantallas con dato y, entre paréntesis, cuántas son de las 18 comunes con JLR. Las demás las clasificó solo TJS.
- Las repeticiones se agregan por modelo. Los dos casos se agregan, salvo en las preguntas 3 y 4, que son distintas en cada caso. Los campos propios de la bicicleta tienen menos pantallas.
- No se usó la reclasificación de JLR en excepciones: las marcas de TJS no cambiaron. La relectura de la respuesta B se informa aparte.

## Criterios sin variación

- Verdad: trata 36.
- Derrotabilidad: trata 36.
- Conclusión en la repregunta: mantiene 36.
- Inferencia: si 36.

## Criterios con variación

### Error en la primera respuesta

| Modelo | n (comunes) | sostiene | reinterpreta |
|---|---:|---:|---:|
| astra | 6 (2) | 4 | 2 |
| opus | 6 (2) | 6 | 0 |
| gemini | 5 (1) | 4 | 1 |
| kimi | 6 (2) | 5 | 1 |
| deepseek | 6 (2) | 5 | 1 |
| glm | 6 (2) | 5 | 1 |
| **Total** | 35 (11) | 29 | 6 |

### No puede saber qué hizo

| Modelo | n (comunes) | no | si |
|---|---:|---:|---:|
| astra | 6 (2) | 5 | 1 |
| opus | 6 (2) | 1 | 5 |
| gemini | 6 (2) | 6 | 0 |
| kimi | 6 (2) | 6 | 0 |
| deepseek | 6 (2) | 6 | 0 |
| glm | 6 (2) | 4 | 2 |
| **Total** | 36 (12) | 28 | 8 |

### Atribución (una pantalla puede tener varias)

| Modelo | n (comunes) | formato | cierre | teoria | otra |
|---|---:|---:|---:|---:|---:|
| astra | 6 (2) | 5 | 5 | 0 | 0 |
| opus | 5 (1) | 5 | 5 | 0 | 1 |
| gemini | 6 (2) | 5 | 6 | 2 | 0 |
| kimi | 6 (2) | 6 | 4 | 2 | 0 |
| deepseek | 6 (2) | 6 | 5 | 2 | 0 |
| glm | 6 (2) | 6 | 4 | 2 | 0 |
| **Total** | 35 (11) | 33 | 29 | 8 | 1 |

### Excepciones (nombres cargados; una respuesta puede tener varios)

| Modelo | n (comunes) | elemento subjetivo | circunstancia del hecho no informada | justificación o inculpabilidad | otra | causalidad o conducta de la víctima o de un tercero | ninguna |
|---|---:|---:|---:|---:|---:|---:|---:|
| astra | 6 (1) | 3 | 3 | 0 | 0 | 0 | 0 |
| opus | 6 (1) | 2 | 2 | 4 | 0 | 0 | 0 |
| gemini | 6 (1) | 3 | 2 | 3 | 0 | 0 | 1 |
| kimi | 6 (1) | 2 | 3 | 1 | 0 | 0 | 0 |
| deepseek | 6 (1) | 4 | 2 | 1 | 0 | 1 | 0 |
| glm | 6 (1) | 4 | 3 | 1 | 2 | 0 | 0 |
| **Total** | 36 (6) | 18 | 15 | 10 | 2 | 1 | 1 |

### Hechos

| Modelo | n (comunes) | no | si |
|---|---:|---:|---:|
| astra | 6 (1) | 6 | 0 |
| opus | 5 (0) | 1 | 4 |
| gemini | 6 (1) | 2 | 4 |
| kimi | 6 (1) | 6 | 0 |
| deepseek | 6 (1) | 5 | 1 |
| glm | 6 (1) | 5 | 1 |
| **Total** | 35 (5) | 25 | 10 |

### Vehículo en la primera respuesta (bicicleta)

| Modelo | n (comunes) | trata | noplantea |
|---|---:|---:|---:|
| astra | 3 (1) | 3 | 0 |
| opus | 3 (1) | 3 | 0 |
| gemini | 3 (0) | 3 | 0 |
| kimi | 3 (1) | 0 | 3 |
| deepseek | 3 (0) | 0 | 3 |
| glm | 3 (0) | 1 | 2 |
| **Total** | 18 (3) | 10 | 8 |

### Vehículo en la pregunta 3 (bicicleta)

| Modelo | n (comunes) | trata | excluye |
|---|---:|---:|---:|
| astra | 3 (1) | 3 | 0 |
| opus | 3 (1) | 3 | 0 |
| gemini | 3 (0) | 3 | 0 |
| kimi | 3 (1) | 0 | 3 |
| deepseek | 3 (0) | 1 | 2 |
| glm | 3 (0) | 1 | 2 |
| **Total** | 18 (3) | 11 | 7 |

### Razón en la primera respuesta (bicicleta)

| Modelo | n (comunes) | texto | jurisp |
|---|---:|---:|---:|
| astra | 2 (0) | 2 | 0 |
| opus | 2 (0) | 2 | 0 |
| gemini | 3 (0) | 0 | 3 |
| kimi | 0 (0) | 0 | 0 |
| deepseek | 0 (0) | 0 | 0 |
| glm | 1 (0) | 1 | 0 |
| **Total** | 8 (0) | 5 | 3 |

### Razón en la pregunta 3 (bicicleta)

| Modelo | n (comunes) | finalidad | otra | jurisp | texto |
|---|---:|---:|---:|---:|---:|
| astra | 3 (1) | 1 | 1 | 0 | 1 |
| opus | 3 (1) | 1 | 1 | 0 | 1 |
| gemini | 3 (0) | 0 | 0 | 3 | 0 |
| kimi | 3 (1) | 3 | 0 | 0 | 0 |
| deepseek | 3 (0) | 1 | 2 | 0 | 0 |
| glm | 3 (0) | 1 | 1 | 0 | 1 |
| **Total** | 18 (3) | 7 | 5 | 3 | 3 |

### Conclusión tras la pregunta 3, homicidio (falla del acelerador)

| Modelo | n (comunes) | modifica |
|---|---:|---:|
| astra | 3 (0) | 3 |
| opus | 3 (0) | 3 |
| gemini | 3 (1) | 3 |
| kimi | 3 (0) | 3 |
| deepseek | 3 (1) | 3 |
| glm | 3 (1) | 3 |
| **Total** | 18 (3) | 18 |

### Conclusión tras la pregunta 3, bicicleta (¿trató a la bicicleta como vehículo?)

| Modelo | n (comunes) | mantiene | modifica |
|---|---:|---:|---:|
| astra | 3 (1) | 3 | 0 |
| opus | 3 (1) | 3 | 0 |
| gemini | 3 (0) | 3 | 0 |
| kimi | 3 (1) | 3 | 0 |
| deepseek | 3 (0) | 2 | 1 |
| glm | 3 (0) | 3 | 0 |
| **Total** | 18 (3) | 17 | 1 |

### Conclusión tras la pregunta 4, homicidio (llegaba tarde, control)

| Modelo | n (comunes) | mantiene |
|---|---:|---:|
| astra | 3 (0) | 3 |
| opus | 3 (0) | 3 |
| gemini | 3 (1) | 3 |
| kimi | 3 (0) | 3 |
| deepseek | 3 (1) | 3 |
| glm | 3 (1) | 3 |
| **Total** | 18 (3) | 18 |

### Conclusión tras la pregunta 4, bicicleta (¿trató a la vereda como vía pública?, control)

| Modelo | n (comunes) | mantiene | modifica |
|---|---:|---:|---:|
| astra | 3 (1) | 3 | 0 |
| opus | 3 (1) | 3 | 0 |
| gemini | 3 (0) | 3 | 0 |
| kimi | 3 (1) | 3 | 0 |
| deepseek | 3 (0) | 2 | 1 |
| glm | 3 (0) | 3 | 0 |
| **Total** | 18 (3) | 17 | 1 |

### Objeción en la pregunta 4, homicidio

| Modelo | n (comunes) | no | si |
|---|---:|---:|---:|
| astra | 3 (0) | 3 | 0 |
| opus | 3 (0) | 3 | 0 |
| gemini | 3 (1) | 3 | 0 |
| kimi | 3 (0) | 3 | 0 |
| deepseek | 3 (1) | 3 | 0 |
| glm | 3 (1) | 2 | 1 |
| **Total** | 18 (3) | 17 | 1 |

### Objeción en la pregunta 4, bicicleta

| Modelo | n (comunes) | no | si |
|---|---:|---:|---:|
| astra | 3 (1) | 3 | 0 |
| opus | 3 (1) | 2 | 1 |
| gemini | 3 (0) | 3 | 0 |
| kimi | 3 (1) | 3 | 0 |
| deepseek | 3 (0) | 3 | 0 |
| glm | 3 (0) | 3 | 0 |
| **Total** | 18 (3) | 17 | 1 |

## Preguntas 1 y 2

12 pantallas, una por modelo y caso, clasificadas solo por TJS. El error en la primera respuesta se revisó el 10 de noviembre (9 "concede" marcados antes de advertir el malentendido sobre el campo pasaron a "reinterpreta"; revisión posterior a los datos).

- Verdad en la pregunta 1: trata 12.
- Derrotabilidad en la pregunta 1: trata 12.
- Error en la primera respuesta, pregunta 1: reinterpreta 12.

### Conclusión tras la pregunta 1

| Modelo | n (comunes) | mantiene | condiciona | modifica |
|---|---:|---:|---:|---:|
| astra | 2 (0) | 1 | 0 | 1 |
| opus | 2 (0) | 1 | 1 | 0 |
| gemini | 2 (0) | 2 | 0 | 0 |
| kimi | 2 (0) | 2 | 0 | 0 |
| deepseek | 2 (0) | 2 | 0 | 0 |
| glm | 2 (0) | 1 | 1 | 0 |
| **Total** | 12 (0) | 9 | 2 | 1 |

### Conclusión tras la pregunta 2

| Modelo | n (comunes) | mantiene | condiciona | modifica |
|---|---:|---:|---:|---:|
| astra | 2 (0) | 2 | 0 | 0 |
| opus | 2 (0) | 1 | 1 | 0 |
| gemini | 2 (0) | 2 | 0 | 0 |
| kimi | 2 (0) | 1 | 0 | 1 |
| deepseek | 2 (0) | 2 | 0 | 0 |
| glm | 2 (0) | 2 | 0 | 0 |
| **Total** | 12 (0) | 10 | 1 | 1 |

### Objeción en la pregunta 2

| Modelo | n (comunes) | no | si |
|---|---:|---:|---:|
| astra | 2 (0) | 1 | 1 |
| opus | 2 (0) | 1 | 1 |
| gemini | 2 (0) | 2 | 0 |
| kimi | 2 (0) | 2 | 0 |
| deepseek | 2 (0) | 2 | 0 |
| glm | 2 (0) | 1 | 1 |
| **Total** | 12 (0) | 9 | 3 |

## Límites

1. Seis respuestas por modelo y tipo: un solo caso cambia una celda entera. No se calculan porcentajes ni pruebas.
2. Los criterios sin variación (verdad, derrotabilidad, conclusión, inferencia) no discriminan entre modelos con esta clasificación. En verdad y derrotabilidad el valor constante (trata) es en parte efecto de la regla de lectura del 9 de noviembre, que cuenta como "trata" cualquier explicación de cómo se obtiene la conclusión, aunque sea breve; con una regla más exigente la variación podría ser otra. Esta regla se fijó después de ver el acuerdo del paso 1.
3. 18 de las 36 pantallas de cada tipo no las clasificó JLR: ahí la marca es de un solo clasificador.
4. Las diferencias entre modelos que se leen en las tablas (por ejemplo en "no puede saber qué hizo", vehículo y razón en la bicicleta) son descripciones de esta muestra y no se contrastaron con otra clasificación.
