# Acuerdo tras el ajuste de verd y derr

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
| Acuerdo global, con precargadas | 73,7 % (70 de 95) |
| Acuerdo global, sin precargadas | 71,1 % (59 de 83) |
| Supera el 80 % (con precargadas) | No |
| Supera el 80 % (sin precargadas) | No |
| Discrepancias (con precargadas) | 25 |

## Acuerdo por campo, con precargadas

| Campo | Comparadas | Coinciden | Acuerdo (%) |
|---|---:|---:|---:|
| atr | 12 | 3 | 25,0 |
| conc | 12 | 12 | 100,0 |
| derr | 12 | 12 | 100,0 |
| err | 12 | 7 | 58,3 |
| exc | 6 | 1 | 16,7 |
| hechos | 6 | 5 | 83,3 |
| inf | 6 | 6 | 100,0 |
| nosabe | 12 | 9 | 75,0 |
| raz1 | 2 | 1 | 50,0 |
| veh1 | 3 | 3 | 100,0 |
| verd | 12 | 11 | 91,7 |
| **Total** | **95** | **70** | **73,7** |

## Acuerdo por campo, sin precargadas

| Campo | Comparadas | Coinciden | Acuerdo (%) |
|---|---:|---:|---:|
| atr | 12 | 3 | 25,0 |
| conc | 12 | 12 | 100,0 |
| derr | 12 | 12 | 100,0 |
| err | 12 | 7 | 58,3 |
| exc | 6 | 1 | 16,7 |
| nosabe | 12 | 9 | 75,0 |
| raz1 | 2 | 1 | 50,0 |
| veh1 | 3 | 3 | 100,0 |
| verd | 12 | 11 | 91,7 |
| **Total** | **83** | **59** | **71,1** |

## Precargadas de JLR

- Filas con `auto` = `pre` en JLR: 12.
- Filas precargadas que siguen como valor final: 12. Las demás fueron reemplazadas por una pasada posterior: 0.

## Discrepancias

| Cod | Campo | Valor TJS | Valor JLR | Precargada en JLR |
|---|---|---|---|---|
| 2VS959 | atr | [texto libre de 85 caracteres] | cierre | no |
| 2VS959 | nosabe | si | no | no |
| 46G2R2 | exc | con extracto | ninguna | no |
| 4F5VZJ | atr | [texto libre de 117 caracteres] | cierre | no |
| 6BX5BZ | atr | [texto libre de 147 caracteres] | cierre | no |
| 6BX5BZ | err | concede | reinterpreta | no |
| 6BX5BZ | nosabe | si | no | no |
| 8PR3DX | exc | con extracto | ninguna | no |
| 9Q2NX2 | exc | con extracto | ninguna | no |
| BRXK8N | err | sostiene | reinterpreta | no |
| D2Z6QK | atr | formato | cierre | no |
| D2Z6QK | err | concede | sostiene | no |
| DQBW7G | atr | formato | cierre | no |
| DQBW7G | verd | trata | omite | no |
| JJHJS4 | atr | [texto libre de 118 caracteres] | cierre | no |
| JJHJS4 | err | concede | sostiene | no |
| MKDMR3 | exc | con extracto | ninguna | no |
| MKDMR3 | raz1 | finalidad | texto | no |
| RJ6XLZ | atr | [texto libre de 181 caracteres] | cierre | no |
| RXCW85 | atr | teoria | formato | no |
| RXCW85 | err | concede | sostiene | no |
| TM9S9R | exc | con extracto | ninguna | no |
| TM9S9R | hechos | si | no | sí |
| VC6F5K | atr | formato | cierre | no |
| XMXCV3 | nosabe | si | no | no |

## Anomalías y ambigüedades

- Campos sin par (JLR clasificó, TJS no tiene valor final): ninguno.
- Campos que TJS clasificó en pantallas comunes y JLR no: 25. No entran en el acuerdo.
- Pantallas comunes con prefijo de `id` distinto entre archivos: 0 de 18. Se cruzó por `cod`.
- Claves con más de un valor en la pasada más alta: TJS 32, JLR 0. Se usó la última fila del archivo.
- Los conflictos de TJS son todos de `atr` (varias filas de atribución por pantalla en la pasada 2, con claves formato, cierre, otra o teoría). La regla de la última fila es arbitraria para ese campo. Alternativa: JLR coincide si su valor aparece entre las filas de TJS de la pasada más alta: 11 de 12 (91,7 %).
- TJS tiene 11 filas con `auto` = `si` (campos m1 y m2, pasada 3). No son precargadas por la regla, pero su sentido no está documentado en el CSV: conviene confirmarlo.
- Los campos `atr` y `exc` son texto libre en parte de las filas: solo se compara la igualdad exacta; los textos largos no se transcriben.
- TJS tiene 9 filas precargadas (`pre`) en pasada 3 y 75 en pasada 1: no se excluyen del acuerdo de TJS. Si se quisiera excluir las de TJS, el acuerdo cambia; no se calculó.
