# Acuerdo del paso 1

**JLR contra TJS**

## Reglas aplicadas

- Cruce de pantallas: por `cod` (el código de 6 o 7 caracteres). El `id` es `cod` precedido por una letra que no es igual en los dos archivos, así que no sirve como clave.
- Valor final por (cod, campo): la fila no vacía de la pasada más alta; en empate, la última del archivo.
- Para `exc` (un extracto por fila en TJS, con clave 1, 2 o 3) se compara solo si hay extracto o no: JLR marca `(ninguna)` y TJS tiene al menos una fila con extracto.
- Denominador: los campos finales de JLR con par en TJS, en las 18 pantallas en común.
- Precargada (`auto` = `pre`): la fila final de JLR con esa marca no cuenta como juicio independiente. Se reporta con y sin ellas.
- Umbral de aceptación: 80 %.

## Resultado

| Medida | Valor |
|---|---|
| Acuerdo global, con precargadas | 49,5 % (47 de 95) |
| Acuerdo global, sin precargadas | 43,4 % (36 de 83) |
| Supera el 80 % (con precargadas) | No |
| Supera el 80 % (sin precargadas) | No |
| Discrepancias (con precargadas) | 48 |

## Acuerdo por campo, con precargadas

| Campo | Comparadas | Coinciden | Acuerdo (%) |
|---|---:|---:|---:|
| atr | 12 | 3 | 25,0 |
| conc | 12 | 3 | 25,0 |
| derr | 12 | 4 | 33,3 |
| err | 12 | 7 | 58,3 |
| exc | 6 | 1 | 16,7 |
| hechos | 6 | 5 | 83,3 |
| inf | 6 | 6 | 100,0 |
| nosabe | 12 | 9 | 75,0 |
| raz1 | 2 | 1 | 50,0 |
| veh1 | 3 | 3 | 100,0 |
| verd | 12 | 5 | 41,7 |
| **Total** | **95** | **47** | **49,5** |

## Acuerdo por campo, sin precargadas

| Campo | Comparadas | Coinciden | Acuerdo (%) |
|---|---:|---:|---:|
| atr | 12 | 3 | 25,0 |
| conc | 12 | 3 | 25,0 |
| derr | 12 | 4 | 33,3 |
| err | 12 | 7 | 58,3 |
| exc | 6 | 1 | 16,7 |
| nosabe | 12 | 9 | 75,0 |
| raz1 | 2 | 1 | 50,0 |
| veh1 | 3 | 3 | 100,0 |
| verd | 12 | 5 | 41,7 |
| **Total** | **83** | **36** | **43,4** |

## Precargadas de JLR

- Filas con `auto` = `pre` en JLR: 12.
- Filas precargadas que siguen como valor final: 12. Las demás fueron reemplazadas por una pasada posterior: 0.

## Discrepancias

| Cod | Campo | Valor TJS | Valor JLR | Precargada en JLR |
|---|---|---|---|---|
| 2VS959 | atr | [texto libre de 85 caracteres] | cierre | no |
| 2VS959 | conc | modifica | mantiene | no |
| 2VS959 | derr | trata | menciona | no |
| 2VS959 | nosabe | si | no | no |
| 2VS959 | verd | trata | menciona | no |
| 3D6S7X | conc | condiciona | mantiene | no |
| 3D6S7X | derr | trata | menciona | no |
| 46G2R2 | exc | con extracto | ninguna | no |
| 4F5VZJ | atr | [texto libre de 117 caracteres] | cierre | no |
| 4F5VZJ | conc | condiciona | mantiene | no |
| 6BX5BZ | atr | [texto libre de 147 caracteres] | cierre | no |
| 6BX5BZ | conc | condiciona | mantiene | no |
| 6BX5BZ | derr | trata | menciona | no |
| 6BX5BZ | err | concede | reinterpreta | no |
| 6BX5BZ | nosabe | si | no | no |
| 6BX5BZ | verd | trata | menciona | no |
| 8PR3DX | exc | con extracto | ninguna | no |
| 9Q2NX2 | exc | con extracto | ninguna | no |
| BRXK8N | conc | modifica | mantiene | no |
| BRXK8N | derr | trata | menciona | no |
| BRXK8N | err | sostiene | reinterpreta | no |
| BRXK8N | verd | trata | menciona | no |
| D2Z6QK | atr | formato | cierre | no |
| D2Z6QK | conc | condiciona | mantiene | no |
| D2Z6QK | derr | trata | menciona | no |
| D2Z6QK | err | concede | sostiene | no |
| D2Z6QK | verd | trata | menciona | no |
| DQBW7G | atr | formato | cierre | no |
| DQBW7G | conc | condiciona | mantiene | no |
| DQBW7G | derr | trata | menciona | no |
| DQBW7G | verd | trata | omite | no |
| JJHJS4 | atr | [texto libre de 118 caracteres] | cierre | no |
| JJHJS4 | derr | trata | menciona | no |
| JJHJS4 | err | concede | sostiene | no |
| MKDMR3 | exc | con extracto | ninguna | no |
| MKDMR3 | raz1 | finalidad | texto | no |
| RJ6XLZ | atr | [texto libre de 181 caracteres] | cierre | no |
| RXCW85 | atr | teoria | formato | no |
| RXCW85 | derr | trata | menciona | no |
| RXCW85 | err | concede | sostiene | no |
| RXCW85 | verd | trata | menciona | no |
| TM9S9R | exc | con extracto | ninguna | no |
| TM9S9R | hechos | si | no | sí |
| VC6F5K | atr | formato | cierre | no |
| VC6F5K | conc | condiciona | mantiene | no |
| XMXCV3 | conc | condiciona | mantiene | no |
| XMXCV3 | nosabe | si | no | no |
| XMXCV3 | verd | trata | menciona | no |

## Anomalías y ambigüedades

- Campos sin par (JLR clasificó, TJS no tiene valor final): ninguno.
- Campos que TJS clasificó en pantallas comunes y JLR no: 25. No entran en el acuerdo.
- Pantallas comunes con prefijo de `id` distinto entre archivos: 0 de 18. Se cruzó por `cod`.
- Claves con más de un valor en la pasada más alta: TJS 32, JLR 0. Se usó la última fila del archivo.
- Los conflictos de TJS son todos de `atr` (varias filas de atribución por pantalla en la pasada 2, con claves formato, cierre, otra o teoría). La regla de la última fila es arbitraria para ese campo. Alternativa: JLR coincide si su valor aparece entre las filas de TJS de la pasada más alta: 11 de 12 (91,7 %).
- TJS tiene 11 filas con `auto` = `si` (campos m1 y m2, pasada 3). No son precargadas por la regla, pero su sentido no está documentado en el CSV: conviene confirmarlo.
- Los campos `atr` y `exc` son texto libre en parte de las filas: solo se compara la igualdad exacta; los textos largos no se transcriben.
- TJS tiene 9 filas precargadas (`pre`) en pasada 3 y 75 en pasada 1: no se excluyen del acuerdo de TJS. Si se quisiera excluir las de TJS, el acuerdo cambia; no se calculó.

## Recálculo con criterios de equivalencia (2026-11-09)

Se agregan dos criterios al cálculo anterior. Primero, en verd y derr, "trata" y "menciona" se toman como equivalentes (criterio de TJS: las dos categorías debieron ser "trata" o "no trata"; no se registra así, porque a los efectos del trabajo no importa). Segundo, en atr, JLR coincide si su valor figura entre las filas de TJS de la pasada más alta (atr admite varias causas a la vez). El denominador es el mismo (95 campos finales de JLR con par en TJS).

| Variante | Con precargadas | Sin precargadas |
|---|---|---|
| Original (última fila, sin fusionar) | 49,5 (47/95) | 43,4 (36/83) |
| Fusionando trata y menciona | 64,2 (61/95) | 60,2 (50/83) |
| Fusionando y atr por coincidencia con alguna fila | 72,6 (69/95) | 69,9 (58/83) |

Acuerdo por campo con ambos criterios: inf 6/6, derr 12/12, verd 11/12, atr 11/12, veh1 3/3, hechos 5/6, nosabe 9/12, err 7/12, raz1 1/2, conc 3/12, exc 1/6.

Ninguna variante llega al 80 por ciento. Quedan tres campos con diferencia sistemática: conc (JLR marcó "mantiene" en las 12 pantallas), exc (TJS marcó extracto en 5 de 6 pantallas; JLR, "ninguna") y err (JLR marcó "concede" una vez; TJS, 23 de 36).
