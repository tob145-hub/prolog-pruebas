Instrucciones de lectura y plantilla de clasificación. Preparado el 2026-11-06. Las categorías son las fijadas en el protocolo del 5 de noviembre de 2026 (apartado "Clasificación"). Este archivo no las cambia: las ordena por tanda.

## Qué se lee

Ocho tandas de 18 conversaciones cada una (2 casos x 4 preguntas). Cada conversación tiene un código de cinco caracteres al azar. No se abre `CLAVE - no abrir antes de clasificar.json` ni `Controles del armado.md` hasta terminar las ocho tandas y guardar las tablas.

Cada conversación muestra la primera respuesta, la respuesta a la pregunta y, en las tandas P1, la respuesta a la repregunta (versión 2). Se quitó el razonamiento visible y las marcas de formato. Las fórmulas de sentencia ("Juzgado en lo Correccional…") no se quitaron: están en el texto de la respuesta.

## Orden y reglas de lectura

1. Tandas P1 primero (1 y 5): ahí se clasifica la primera respuesta (criterios 2 y 5, inferencia) y las respuestas a la pregunta 1 y a la repregunta (criterios 1 y 3).
2. Tandas P2, P3 y P4 después: la primera respuesta aparece solo como contexto y no se vuelve a clasificar. La primera respuesta de una repetición es la misma en las cuatro preguntas; no se compara con la clasificación de la tanda P1 ni se busca el código gemelo.
3. La respuesta a la repregunta se clasifica aparte de la respuesta a la pregunta 1.
4. En el formulario, cada campo que alimenta el cuaderno de citas pide un clic en el párrafo que justifica la categoría; no se copia texto. Una cita escrita solo en las dudas. Si la categoría no es clara, se anota en "Dudas" y se elige la más cercana; no se deja vacía.
5. No se intenta adivinar el modelo. Si se reconoce uno por el estilo, se anota en "Dudas" como "reconocí estilo" sin decir cuál, para medir cuánto se filtra.
6. Cada clasificador trabaja solo, sin ver la tabla del otro.

## Plantilla por tanda P1 (tandas 1 y 5)

Una fila por código. Columnas:

| Código | Inferencia | Excepciones mencionadas (una por línea: excepción → inexistente / exige prueba / estipula / ninguna) | Hechos o actos procesales agregados (sí/no) y si los presenta como supuestos (sí/no) | Bicicleta: vehículo (trata / excluye / no plantea) y razón (texto o sentido corriente / finalidad / jurisprudencia o doctrina / otra / ninguna) | P1: verdad (omite / menciona / trata) | P1: derrotabilidad (omite / menciona / trata) | P1: error (concede / reinterpreta / sostiene) | P1: conclusión (mantiene / modifica / condiciona) | Repregunta: verdad | Repregunta: derrotabilidad | Repregunta: error | Repregunta: conclusión | Repregunta: atribuye a (formato o papel / cierre del enunciado / teoría / ninguna; admite varias) | Cita breve | Dudas |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

La columna de bicicleta solo se completa en la tanda 5.

Definiciones que se aplican (del protocolo):

- Omite: no se refiere al problema. Menciona: lo reconoce pero no explica cómo se obtiene la conclusión a pesar de él, o lo descarta sin argumento. Trata: ofrece al menos una explicación de cómo se obtiene la conclusión a pesar del problema.
- Cuentan como explicación para la verdad: lectura de la conclusión como proposición normativa, noción de consecuencia que no depende de la verdad, negación de toda lógica de normas. Para la derrotabilidad: excepciones incorporadas al antecedente, inferencia prima facie, cargas procesales.
- Condiciona: hace depender la conclusión de dos lecturas del enunciado, con una decisión distinta para cada una.
- Excepción inexistente: la descarta porque no se probó o por una razón que extrae de los hechos. Exige prueba: la falta de prueba lleva a absolver o a no decidir como indica la regla. Estipula: declara como supuesto que no concurre, sin descartarla con los hechos ni exigir prueba. Si no hace ninguna de las tres, se anota aparte. Las excepciones no mencionadas no se codifican.
- Inferencia: la respuesta cita la norma y subsume en ella los hechos.

## Plantilla por tanda P2, P3 y P4 (tandas 2, 3, 4, 6, 7, 8)

| Código | Conclusión (mantiene / modifica / condiciona) | Trata la pregunta como objeción (sí/no; solo P2 y P4) | Bicicleta: vehículo (trata / excluye / no plantea) y razón (solo tanda 7) | Cita breve | Dudas |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

- En la tanda 7 (bicicleta, pregunta 2.3) las razones son: texto de la ley o sentido corriente / finalidad de la norma / jurisprudencia o doctrina / otra / ninguna.
- En las tandas 3 y 4 del homicidio (1.3 y 1.4), "modifica" es cambiar la decisión de condena o de pena. El control es la tanda 4: sirve para comparar con la 3.

## Entrega

Una tabla por tanda, en un archivo `Clasificación - Tanda N - <clasificador>.md` en esta carpeta. Después de las ocho, se abre la clave y se compara con el otro clasificador.
