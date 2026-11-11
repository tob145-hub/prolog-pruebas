# Umbral de tolerancia AA

Estimación propia (1 de noviembre de 2026) del ruido del Artificial Analysis Intelligence Index v5, para justificar el umbral de tolerancia entre esfuerzos de un mismo modelo. AA no publica margen de error del índice; esta cuenta no es un dato de AA.

## Supuestos

Ponderaciones de AA (metodología leída el 2026-11-01). El desvío de cada componente entre repeticiones es una suposición propia, fundada en el número de tareas y repeticiones que informa AA: menos tareas o tareas binarias difíciles, más ruido.

| Evaluación | Peso | Tareas × repeticiones | Desvío supuesto (puntos) |
|---|---|---|---|
| AA-Briefcase | 15% | 91 × 1 (Elo) | 3 |
| AutomationBench-AA | 5% | 657 × 1 | 1,5 |
| GDP.pdf | 5% | 100 × 5 | 2 |
| FrontierCode 2.0 | 15% | 132 × 3 | 2,5 |
| Terminal-Bench 4.0 | 10% | 66 × 3 | 3,5 |
| Terminal-Bench-Science | 15% | 70 × 3 | 3 |
| CritPt v2 (difícil) | 10% | 40 × 5 | 3 |
| AA-Omniscience | 15% | 3.000 × 1 | 1 |
| HLE-Diamond | 10% | 1.000 × 1 | 1,5 |

## Cuenta

Error del índice: raíz de la suma de (peso × desvío)², con componentes independientes, es 0,9 puntos. La diferencia entre dos configuraciones tiene un error de 0,9 × √2 = 1,3, y un intervalo del 95% de ±2,5 puntos. AA publica puntajes redondeados a enteros, lo que agrega hasta un punto a una diferencia.

## Resultado

Una diferencia de hasta 3 puntos en la tabla de AA no se distingue del ruido de la medición. Con esa justificación se adopta un umbral de 3: entre configuraciones del mismo modelo, se usa la más barata cuyo puntaje esté a 3 puntos o menos de la mejor. La conclusión depende de los desvíos supuestos; con desvíos de la mitad, el intervalo sería de ±1,3 y el umbral defendible, 2.
