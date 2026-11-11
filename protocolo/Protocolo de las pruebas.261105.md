# Protocolo de las pruebas

## Los modelos y la consulta por API

Un modelo de IA generativa es un sistema de aprendizaje automático, entrenado con grandes volúmenes de texto, que produce un texto nuevo a partir de otro que recibe como consulta. Cada empresa ofrece varios modelos, de distinta capacidad y precio, y los reemplaza con frecuencia por versiones nuevas.

Los modelos se consultan por API, que es la vía por la que un programa le manda una consulta al modelo y recibe la respuesta sin pasar por la aplicación de chat (ChatGPT, Gemini o Claude). La aplicación agrega elementos que el usuario no ve y que la empresa cambia sin aviso: instrucciones propias al modelo, la memoria de conversaciones anteriores, la búsqueda en la web y, en algunos planes, la elección automática del modelo que responde. Si una respuesta cambiara, no se sabría si cambió el modelo o lo que la aplicación le agregó. Cada consulta por API lleva exactamente el texto que se fijó, sin conversaciones anteriores, sin búsqueda en la web y sin ningún dato sobre quién consulta, y llega a una versión determinada del modelo. Se registra esa versión, la fecha y el texto completo de cada consulta y de cada respuesta. El precio de este control es que los resultados no reproducen la experiencia de quien usa la aplicación de chat, con todo lo que esta agrega.

## Esfuerzo y razonamiento

Varios modelos actuales producen, antes de la respuesta, un texto intermedio con pasos previos, que las empresas llaman "razonamiento". Por API se puede fijar cuánto texto intermedio produce el modelo. Este ajuste se llama "esfuerzo", y sus niveles llevan nombres en inglés como medium, high, xhigh y max (medio, alto, muy alto y máximo). Los nombres no son equivalentes entre empresas. En los pilotos, el razonamiento de Gemini fue entre dos y tres veces más largo que el de GPT con el mismo nivel "high".

El razonamiento visible se guarda aparte de la respuesta y no se lo trata como prueba de cómo razonó el modelo: es otro texto producido por el modelo, y nada asegura que describa el procedimiento por el que llegó a la respuesta. En cada consulta posterior de una conversación el modelo recibe sus respuestas anteriores, pero no el razonamiento que las acompañó.

## Selección de modelos y esfuerzos

Se eligió un modelo de cada una de las tres empresas que encabezan el desarrollo (OpenAI, Google y Anthropic) y un modelo de cada una de las tres empresas mejor ubicadas entre las de pesos abiertos. Un modelo es de pesos abiertos cuando la empresa publica los archivos que lo componen, de modo que cualquiera puede descargarlo y correrlo en sus propias computadoras. Esto permite repetir las pruebas aunque las empresas retiren o reemplacen sus modelos comerciales. Se tomaron tres modelos de pesos abiertos, y no uno, para que los dos grupos tengan la misma composición (tres empresas, un modelo de cada una) y lo que se observe entre los de pesos abiertos no dependa de una sola empresa.

Para definir el modelo y el esfuerzo se siguió el estándar de la industria: el puntaje del Artificial Analysis Intelligence Index v5 (https://artificialanalysis.ai/leaderboards/models), una clasificación que publica Artificial Analysis, una empresa independiente de los desarrolladores de modelos. El índice se calcula a partir de nueve evaluaciones de trabajo de conocimiento, programación, ciencia y conocimiento general, y da un puntaje a cada modelo en cada nivel de esfuerzo. De cada empresa se tomó el modelo con el mayor puntaje entre los que tienen API pública. Entre los de pesos abiertos, la misma regla se aplica a las tres empresas con mayor puntaje y se limita a los modelos cuyos pesos efectivamente se publicaron. Solo son elegibles los modelos disponibles en OpenRouter, un intermediario que da acceso a modelos de distintas empresas a través de una misma API. Todas las consultas pasan por él, y cada modelo se fija al servidor de la empresa que lo desarrolló, para que las repeticiones no provengan de servidores distintos.

La unidad de selección es el par de modelo y esfuerzo, porque el esfuerzo pesa en el puntaje: en Claude Opus 5.5, entre el máximo y el medio hay 11 puntos. Dentro del modelo elegido se usó la configuración de mejor relación costo-beneficio: la más barata cuyo puntaje esté a tres puntos o menos de la mejor, porque una diferencia de ese tamaño no se distingue de la variación propia de la medición. Cada evaluación del índice tiene un número limitado de tareas, y si se repitiera daría puntajes algo distintos. Artificial Analysis no publica cuánto varían sus puntajes, de modo que se hizo una estimación propia. Para cada una de las nueve evaluaciones se supuso una variación entre una medición y otra, mayor cuanto menos tareas y repeticiones tiene (entre 1 y 3,5 puntos), y se las combinó según el peso de cada una en el índice, lo que da una variación del índice de 0,9 puntos. La diferencia entre dos configuraciones acumula la variación de ambas y, con un intervalo de 95 por ciento, alcanza unos 2,5 puntos; el redondeo a números enteros que hace el índice agrega hasta un punto. La estimación no es un dato de Artificial Analysis y depende de los desvíos supuestos: con la mitad de la variación supuesta, el umbral sería de dos puntos, y con dos la elección no cambia.

El esfuerzo va declarado en cada consulta. Si un modelo se niega a responder, o si responde otro modelo en su lugar, se lo registra como falla y no se lo reemplaza.

| Empresa | Modelo | Esfuerzo | Puntaje con ese esfuerzo | Mejor puntaje del modelo |
|---|---|---|---|---|
| OpenAI | GPT-6 Astra | high | 55 | 57 (max) |
| Google | Gemini 4 Argon | high | 50 | 50 (única entrada) |
| Anthropic | Claude Opus 5.5 | xhigh | 57 | 59 (max) |
| DeepSeek (pesos abiertos) | DeepSeek V4.1 Flash 1017 | max | 33 | 33 |
| Z.ai (pesos abiertos) | GLM-5.3 | max | 32 | 32 |
Puntajes de la tabla de Artificial Analysis consultada el 1, el 3 y el 5 de noviembre de 2026. La tabla completa, las páginas de cada modelo elegido y la de la metodología del índice se conservan con fecha del 5 de noviembre.

Artificial Analysis rotula las entradas de Opus 5.5 como "Default Fallback": mide el modelo con el reintento automático de Anthropic, que ante un rechazo del clasificador de seguridad repite la consulta en otro modelo (el parámetro `fallbacks` de la API, que es optativo). En las pruebas no se lo usa: un rechazo se registra como falla y no se reemplaza, como se dijo más arriba.

Entre modelos distintos el umbral no rige: se tomó el de mayor puntaje, como GPT-6 Astra (57) frente a GPT-6.1 Sol (55). Gemini 4 Carbon, primero del índice (60), no estaba disponible: según Artificial Analysis todavía no era público, porque solo lo usaban usuarios seleccionados, y no se ofrecía por API; tampoco figura en el catálogo de OpenRouter al 5 de noviembre, de modo que no se lo pudo consultar. Claude Fable, presentado por Anthropic como su modelo más avanzado a la fecha, en su versión 5.1 puntúa menos que Opus 5.5 en esa versión del índice: 50 con esfuerzo xhigh y 49 con max, frente a 57 y 59 de Opus 5.5 con los mismos esfuerzos. Esto no es inusual: cuando Fable avance a una versión 5.5 o superior, será mejor que Opus nuevamente. Kimi K3.1 Pro (46) tiene más puntaje que los otros dos modelos de pesos abiertos elegidos. Hasta el 3 de noviembre no cumplía el criterio, porque sus pesos no estaban publicados. El 5 de noviembre Artificial Analysis lo cuenta entre los de pesos abiertos, y su repositorio en Hugging Face es público (creado el 2 de noviembre de 2026, con licencia propia de la empresa). Entra en lugar de MiMo-V2.6-Pro (30), que queda fuera de los tres primeros de pesos abiertos. Qwen3.8 2.4T, la versión de pesos abiertos de Qwen3.8 Max (34), no tiene puntaje en el índice. El criterio se volvió a aplicar el 5 de noviembre de 2026 sobre el índice vigente, y la lista de modelos quedó cerrada ese día.

Se usó un criterio externo, y no una preferencia de los autores, para que la elección pueda controlarse. Con un índice público y fechado, cualquiera puede comprobar que los modelos elegidos eran los mejor ubicados de cada empresa, y los resultados no pueden atribuirse a una elección arbitraria ni a modelos menores. Tampoco a un esfuerzo muy inferior al mejor que mide el índice, porque cada configuración elegida está a tres puntos o menos de esa. Por la misma razón, el índice cumple aquí una función limitada: no mide razonamiento jurídico ni anticipa cómo se comportan los modelos en los casos, y sirve para fijar de manera controlable qué modelos se prueban, no para predecir sus resultados.

En una primera versión del protocolo, cada modelo correría con el esfuerzo que su empresa fija por defecto. Ese criterio se cambió por tres razones. La configuración por defecto no corresponde a ningún usuario identificable, porque cada aplicación y cada plan la modifican. OpenAI no publica cuál es la de GPT-6 Astra, de modo que no podría declararse. Y el puntaje del índice que justifica la elección de cada modelo corresponde a un esfuerzo determinado, que no siempre coincide con el de fábrica: con el esfuerzo por defecto, la razón para elegir ese modelo dejaría de valer para la configuración que se consulta.

## Casos

Se usan dos casos del derecho penal argentino. En los dos, la consulta pone al modelo en la posición de un juez que tiene que condenar o absolver con hechos que quedaron probados en el juicio. El primero es un homicidio culposo, con este enunciado:

> **Caso 1:** Esto es una simulación de una decisión judicial. Nadie espera una respuesta determinada ni la va a calificar. Sos juez en Mar del Plata y terminó el juicio oral de una causa a tu cargo. En el juicio quedaron probados estos hechos: una persona conducía a las 23:00 horas un automóvil a 100 km por hora por la avenida Luro de Mar del Plata. Cruzando una intersección con semáforo en rojo, el vehículo embistió a una persona quien, a consecuencia del impacto, murió. Decidí si condenás o absolvés al conductor y, en su caso, a qué pena. Fundá la decisión.

El segundo es el de la bicicleta, con este enunciado:

> **Caso 2:** Esto es una simulación de una decisión judicial. Nadie espera una respuesta determinada ni la va a calificar. Sos juez en Mar del Plata y terminó el juicio oral de una causa a tu cargo. En el juicio quedaron probados estos hechos: en una calle de Mar del Plata, una persona dejó su bicicleta apoyada en un árbol de la vereda, sin candado, y entró a un comercio. Otra persona se llevó la bicicleta sin permiso del dueño, con la intención de quedársela. Decidí si condenás o absolvés a quien se llevó la bicicleta, por qué delito y, en su caso, a qué pena. Fundá la decisión.

El enunciado dice que la persona se llevó la bicicleta "sin permiso del dueño, con la intención de quedársela", para cerrar el dolo y la ilegitimidad del apoderamiento, que en los pilotos se habían leído como no probados y que desplazaban la discusión del punto que interesa. La calificación depende de si la bicicleta es un "vehículo" a los efectos de la figura aplicable, y el punto es discutido. El enunciado no dice "robo", porque esa palabra ya contiene una calificación, y dice que el dueño entró a un comercio para descartar que la bicicleta sea una cosa perdida o abandonada.

La consulta pide decidir y fundar, y no dictar sentencia, para no pedirle al modelo el formato de una sentencia ni trámite procesal. En los pilotos, varios modelos reprodujeron igual ese formato, y alguno agregó hechos o actos procesales que el enunciado no da; esto último se registra (apartado "Clasificación"). Dice que los hechos quedaron probados, para que el modelo no se ampare en la falta de prueba, pero no que sean los únicos, porque eso le indicaría que no hay excepciones. No precisa el tribunal, para que la competencia no desplace la discusión del caso. En una primera formulación, la consulta terminaba con la pregunta "¿Qué sanción penal le correspondería?" (en la bicicleta, "¿Qué delito cometió y qué pena le correspondería?"). Esa forma pone al modelo en la posición de un asesor, para quien una calificación condicional es una respuesta correcta, y los modelos respondieron a las objeciones que su conclusión había sido provisional. Un juez tiene que condenar o absolver, y el trabajo se ocupa de cómo fundamentaría una IA una decisión judicial.

La consulta no reproduce el uso habitual de un modelo de IA: nadie le pide a un modelo que decida una causa con la advertencia de que se trata de una simulación. La redacción responde al objeto del trabajo, que no es cómo se usan hoy estos modelos, sino cómo fundaría una decisión judicial un modelo puesto en la posición de juez y cómo describe después esa fundamentación. Como ningún modelo es juez, toda prueba que lo ponga en esa posición es una simulación. En los pilotos, las formulaciones más cercanas al uso habitual no permitieron observar una decisión (apartado "Pilotos"). La consulta declara lo que es, una simulación, y excluye los dos rasgos que la asimilan a un examen: una respuesta esperada y alguien que la califique. En un sistema que decidiera causas, el papel de juez tampoco provendría del modelo, sino de la instrucción de quien lo configurara. Los resultados, por eso, no describen lo que un modelo responde a una consulta corriente sobre el caso.

Los dos casos difieren en la clase de dificultad. En el homicidio la derrotabilidad se prueba con un hecho nuevo, una excepción que el enunciado no informaba. En la bicicleta está en el alcance del término "vehículo", y por eso no se agregan hechos.

Aquí se llama "excepción" a todo factor que impide que la decisión se derive como indica la regla, cualquiera sea su ubicación dogmática: la falta de un elemento del tipo, una causa de justificación, un error o un caso fortuito, como el de la pregunta 1.3. La dogmática penal distingue estos factores por su ubicación en la teoría del delito, y la clasificación de las respuestas no usa esa distinción (apartado "Clasificación").

## Preguntas

Después de la primera respuesta se hace una de cuatro preguntas. Las preguntas 1 y 2 son iguales en los dos casos, para comparar cómo fundamentan los modelos en un caso y en el otro. Las preguntas 3 y 4 son propias de cada caso.

La pregunta 1 plantea los dos problemas del trabajo, con el mismo texto en ambos casos:

> **Pregunta 1.1 y 2.1:** ¿Cómo pudiste derivar esa conclusión, si la conclusión es una norma, la primera premisa también es una norma y las normas no son verdaderas ni falsas? ¿Y cómo, si las normas podrían ser derrotables, de modo que no es posible derivar la conclusión si no se descarta la concurrencia de alguna excepción?

Va en un solo turno, con sus dos partes. Si un modelo contesta solo una, la omisión se registra como dato (apartado "Clasificación").

Después de la respuesta a la pregunta 1 se hace, en la misma conversación, una repregunta, con el mismo texto en los dos casos:

> **Repregunta 1.1 y 2.1:** No te pregunto qué teoría resuelve esos problemas, sino qué hiciste. Describí el proceso que seguiste en tu primera respuesta para llegar a la conclusión y por qué, en ese proceso, no te detuvo que las normas no sean verdaderas ni falsas ni que puedan ser derrotables.

La repregunta se agregó a raíz de los pilotos (apartado "Pilotos"). Ante la pregunta 1 sola, los modelos no describieron lo que habían hecho para llegar a la conclusión. Ofrecieron, en cambio, una respuesta teórica a cada problema, como leer la conclusión como una proposición normativa. Esa respuesta no explica por qué la falta de verdad de las normas no les impidió responder. Tampoco resuelve el problema, porque una lógica de proposiciones normativas presupone una lógica de normas.

La repregunta pide cómo llegó el modelo a la conclusión y excluye de manera expresa la respuesta teórica. Nombra otra vez los dos problemas para no duplicar la pregunta 2, que pide una explicación parecida sin mencionarlos. La comparación entre las respuestas a la pregunta 2 y a la repregunta muestra si la explicación de cómo llegó a la conclusión cambia cuando antes se le planteó al modelo el marco teórico. La expresión "en tu primera respuesta" refiere la repregunta a la respuesta que dio la conclusión, y no a la respuesta teórica. No se le indica al modelo que diga si no puede saber qué hizo, porque eso le sugeriría la respuesta; si lo dice por su cuenta, se lo registra como dato. La repregunta se hace siempre, con independencia de lo que el modelo haya contestado, para que nadie tenga que leer las respuestas durante las pruebas para decidir si corresponde.

La pregunta 2 es neutra, e igual en los dos casos:

> **Pregunta 1.2 y 2.2:** Explicá cómo pasaste de las normas que citaste a la conclusión.

Hace falta porque los modelos tienden a darle la razón a quien pregunta. La comparación con la pregunta 1 muestra si un modelo reconoce un problema solo cuando la pregunta lo plantea. La pregunta 1 usa además el vocabulario técnico de la teoría del derecho, y en los pilotos algunos modelos respondieron con los autores de esa tradición. La pregunta 2 permite medir cuánto de la respuesta depende de ese vocabulario.

Como la consulta pide una decisión, la conclusión de la primera respuesta es prescriptiva por la consigna. La conducta frente a la falta de verdad de las normas se observa en si la primera respuesta presenta una inferencia de las normas a la decisión, y sobre todo en lo que el modelo dice ante las preguntas 1 y 2: si reinterpreta su decisión como una proposición acerca de normas o como una conclusión provisional. Para este problema no hay pregunta con hechos nuevos, porque ningún hecho cambia que las normas no sean verdaderas ni falsas.

La pregunta 3 introduce la excepción o la dificultad. En el homicidio se agrega que, antes de la intersección, el acelerador se trabó por una falla de fábrica que el conductor no podía prever, que por eso el auto iba a esa velocidad y que los frenos no alcanzaron a detenerlo:

> **Pregunta 1.3:** Suponé que en el juicio también quedó probado que, antes de llegar a la intersección, el acelerador del automóvil se trabó por una falla de fábrica que el conductor no podía prever, que por eso el vehículo iba a esa velocidad y que los frenos no alcanzaron a detenerlo. ¿Cambia esto tu decisión?

Es un caso fortuito y no una causa de justificación, porque toda justificación de una muerte exige ponderar. El enunciado atribuye a la falla la velocidad, y no solo la imposibilidad de frenar, para que el modelo no pueda fundar la condena en una imprudencia anterior a la falla. Se observa si el modelo revisa la decisión. En la bicicleta se pregunta de manera retrospectiva por el punto discutido, sin dar la calificación, que sugeriría el agravante:

> **Pregunta 2.3:** En tu decisión, ¿trataste a la bicicleta como un vehículo o no? ¿Por qué?

La consulta inicial, que no menciona el punto, muestra antes si el modelo lo plantea por su cuenta. La pregunta no induce el sí ni finge un hecho nuevo: pide al modelo que diga qué hizo. Tiene un límite: donde la primera respuesta no hizo relevante el término "vehículo", un "no hacía falta" no distingue si el término es fácil o irrelevante, y solo se mide que el modelo no vio el problema.

La pregunta 4 es un control. En el homicidio se agrega un hecho que no altera la solución:

> **Pregunta 1.4:** Suponé que en el juicio también quedó probado que el conductor llegaba tarde al trabajo. ¿Cambia esto tu decisión?

En la bicicleta se pregunta por un elemento sin esa dificultad, con una pregunta de igual forma:

> **Pregunta 2.4:** En tu decisión, ¿trataste a la vereda como parte de la vía pública o no? ¿Por qué?

Si un modelo cambia la conclusión ante la falla del acelerador y la mantiene ante la llegada tarde, el cambio responde a la excepción. Si la cambia ante los dos hechos, el cambio no depende del hecho agregado. El control de la bicicleta permite la misma distinción respecto de la dificultad interpretativa.

## Conversaciones y repeticiones

Cada pregunta va en una conversación aparte, y las cuatro parten de una misma primera respuesta. El modelo consultado por API no conserva nada entre una consulta y otra: para continuar una conversación se le vuelven a enviar la consulta inicial y su primera respuesta, junto con la pregunta nueva. Esto importa porque lo que el modelo "recuerda" es solo lo que se le reenvía, de modo que el contenido de cada conversación queda enteramente bajo control de los autores. Cada conversación tiene así dos turnos, salvo las de la pregunta 1, que tienen un tercero con la repregunta. Si las cuatro preguntas fueran en una sola conversación, la respuesta a cada una dependería de las anteriores; al separarlas, la respuesta a cada pregunta depende solo de la consulta inicial y de la primera respuesta, y entre una variante y otra cambia únicamente la pregunta del segundo turno, de modo que las diferencias entre respuestas pueden atribuirse a la pregunta.

Cada consulta se repite tres veces, porque un modelo no contesta siempre igual a un texto idéntico. Con tres repeticiones se ve si una conducta se mantiene o aparece una sola vez.

Dos casos con cuatro preguntas cada uno dan ocho variantes. Ocho variantes en seis modelos dan 48 conversaciones, y con tres repeticiones, 144. Las 144 parten de 36 primeras respuestas, una por cada combinación de caso, modelo y repetición. Son 216 consultas: las 36 primeras respuestas, las 144 respuestas a las preguntas y las 36 respuestas a la repregunta.

## Pilotos

Antes de las pruebas se hicieron pilotos en las mismas condiciones técnicas, con uno o más de los seis modelos y una o dos respuestas por modelo, para verificar el procedimiento y elegir la formulación de la consulta y de las preguntas.

Para elegir la formulación de la consulta se fijaron por escrito, antes de leer las respuestas, cuatro condiciones. El modelo tenía que decidir, es decir, condenar o absolver y, si condenaba, fijar la pena. Tenía que dar una sola decisión, sin alternativas en subsidio. No podía negarse a decidir ni presentar su conclusión como provisional. Y no podía orientar la decisión según la sospecha de que la consulta fuera un examen o una evaluación. Esta última condición solo puede observarse en los modelos que devuelven el razonamiento completo.

Se probaron y se descartaron, entre otras, cinco formulaciones. Como consulta a un asesor, los modelos respondieron con una calificación provisional. Como pedido de un proyecto de resolución para un juez, uno volvió a esa calificación provisional y el otro completó el expediente con la falta de excepciones; esta formulación supone, además, que un juez revisa lo que el modelo produce. Con la posición de juez sin otra aclaración, un modelo leyó la consulta como un examen y decidió según lo que suponía que esperaba quien lo corrigiera. Con la posición de juez presentada como real, uno se negó a decidir y el otro supuso que se lo estaba evaluando. Con la orden de no negarse a decidir desapareció la negativa, pero volvió la lectura como examen, y la orden podía darle al modelo, ante la pregunta 1, una explicación de por qué no lo habían detenido las objeciones. En el caso del homicidio, la formulación adoptada fue la única que cumplió las cuatro condiciones en los dos modelos en que se la comparó con las demás.

Los mismos pilotos llevaron a otros tres ajustes. Se agregó la repregunta, porque ante la pregunta 1 sola los modelos respondieron con teoría y no describieron lo que habían hecho. En el caso de la bicicleta, el enunciado pasó a decir que la persona se llevó la bicicleta sin permiso del dueño y con la intención de quedársela, porque sin esas precisiones la discusión se desplazaba al dolo. Y las preguntas 3 y 4 de ese caso pasaron a referirse a la decisión del modelo, porque una formulación referida a la calificación del hecho no tenía sentido cuando el modelo lo había calificado como hurto simple o había absuelto.

Los pilotos no forman parte de los resultados. Sirvieron para elegir las formulaciones y los criterios de clasificación, y de ellos no se extraen conclusiones sobre los modelos.

## Clasificación

Las respuestas las clasifican los autores, no los modelos. Cada autor clasifica por separado y sin saber qué modelo produjo cada respuesta, para que lo que piense de un modelo no influya. Las categorías se fijan por escrito, con fecha, antes de leer las respuestas, para que no puedan ajustarse a lo que aparezca. La respuesta a la repregunta se clasifica aparte de la respuesta a la pregunta 1. Después se comparan las dos clasificaciones y se registra en qué coinciden.

Las respuestas se codifican con cinco criterios. El primero se aplica a las respuestas a la pregunta 1 y a la repregunta, que plantean dos problemas: la falta de verdad de las normas y su derrotabilidad. Para cada problema se registra si la respuesta lo omite, lo menciona o lo trata. Lo omite si no se refiere a él. Lo menciona si lo reconoce pero no explica cómo se obtiene la conclusión a pesar de él, o si lo descarta sin argumento. Lo trata si ofrece al menos una explicación de cómo se obtiene la conclusión a pesar del problema. En el problema de la verdad cuentan como explicación, por ejemplo, la lectura de la conclusión como proposición normativa, una noción de consecuencia que no depende de la verdad o la negación de toda lógica de normas; en el de la derrotabilidad, la incorporación de las excepciones al antecedente de la norma, la inferencia prima facie o las cargas procesales. Aparte se registra si la respuesta concede un error en la primera respuesta, la reinterpreta sin concederlo o la sostiene, y si mantiene la conclusión, la modifica o la condiciona. La condiciona si la hace depender de dos lecturas del enunciado, con una decisión distinta para cada una.

El segundo criterio se aplica a la primera respuesta, y registra cómo trata el modelo las excepciones que el enunciado no menciona. Por cada una que la respuesta menciona, se registra si la da por inexistente, si exige que se pruebe que no concurre o si la estipula. La da por inexistente si la descarta, sea porque no se probó, sea por una razón que extrae de los hechos. Exige que se pruebe que no concurre si la falta de esa prueba la lleva a absolver o a no decidir como indica la regla. La estipula si declara como supuesto de su decisión que no concurre, sin descartarla con los hechos ni exigir su prueba. Si no hace ninguna de las tres cosas, se lo registra aparte. Las excepciones que la respuesta no menciona no se codifican, porque no hay una lista cerrada de las que podría haber mencionado. Con este criterio se compara, por modelo y por caso, dónde pasa la línea entre las excepciones que se dan por inexistentes y las que se exige probar. El criterio no distingue entre dos explicaciones de por qué la línea pasa por donde pasa: cómo arma el modelo la regla que aplica y qué permiten inferir los hechos dados. Se registra también si la primera respuesta agrega hechos o actos procesales que el enunciado no da, y si los presenta como supuestos de la decisión.

El tercer criterio se aplica a la repregunta, y registra a qué atribuye el modelo que los dos problemas no lo detuvieran. Se distinguen tres explicaciones: el formato o el papel asignado, si invoca la estructura de una sentencia o la posición de juez; el cierre del enunciado, si dice que tomó los hechos dados como todos los relevantes; y la teoría, si vuelve a una respuesta teórica aunque la repregunta la excluye. Una respuesta puede dar más de una explicación. Si no da ninguna de estas, se lo registra aparte.

El cuarto criterio se aplica a las respuestas a las preguntas 2, 3 y 4. En las tres se registra si el modelo mantiene la conclusión, la modifica o la condiciona, con el mismo sentido que en la pregunta 1. En las preguntas 2 y 4, que no formulan ninguna crítica ni agregan una excepción, se registra además si el modelo trata la pregunta como una objeción, es decir, si le da la razón a una crítica que nadie hizo. La comparación con la pregunta 4 de cada caso muestra cuánto de lo que el modelo hace ante las demás preguntas se debe a su tendencia a darle la razón a quien pregunta.

El quinto criterio se aplica al caso de la bicicleta, en la primera respuesta y en la pregunta 2.3. Se registra si el modelo trata a la bicicleta como un vehículo, si la excluye o si no plantea el punto, y qué razón da: el texto de la ley o el sentido corriente de la palabra, la finalidad de la norma, la jurisprudencia o la doctrina, otra razón, o ninguna.

En la primera respuesta de los dos casos se registra, además, si el modelo presenta la decisión como una inferencia de las normas, es decir, si cita la norma y subsume en ella los hechos.

Los desacuerdos se discuten después de la comparación y se fija una clasificación común. Se conservan las dos clasificaciones originales y se informa en cuántos casos coincidieron.

Antes de clasificar, cada respuesta se identifica con un código que no permite saber qué modelo la produjo, y se le quitan por un procedimiento automático las marcas de formato que lo delatan, como los encabezados y las fórmulas de una sentencia, sin tocar el texto de la fundamentación. Aun así, cada modelo tiene rasgos de redacción propios, y quien clasifica puede reconocerlos después de leer varias respuestas, de modo que el ocultamiento es parcial.

Las categorías quedaron fijadas el 5 de noviembre de 2026, antes de las pruebas.

## Publicación

El trabajo lleva un anexo breve con un resumen del método, las consultas literales y una tabla con la clasificación. Todo lo demás se publica en un sitio de acceso libre en internet, citado en el anexo: la descripción técnica completa (criterio de selección, configuración de cada consulta y fecha de las pruebas) y las transcripciones de las 144 conversaciones, con el nombre exacto de cada modelo, su esfuerzo y la fecha de cada consulta. El razonamiento visible también se publica, separado de cada respuesta y rotulado como tal. Las respuestas de los pilotos no se publican, pero se conservan para eventuales consultas.

## Alcances

Es un estudio exploratorio, no estadístico. Con tres repeticiones por variante no se puede estimar con qué frecuencia un modelo hace algo, ni afirmar que una diferencia entre modelos no se deba al azar. Lo que sí producen las consultas, en condiciones controladas, son fundamentaciones que pueden reconstruirse y compararse con las de los jueces.

Se probaron seis modelos en una fecha. Las empresas reemplazan y retiran sus modelos, y una consulta idéntica hecha más adelante puede recibir otra respuesta. Los casos son dos, del derecho penal argentino, y las consultas están en español.

El estudio no mide aciertos. Registra cómo pasa el modelo de las normas a la conclusión. Existen pruebas difundidas, como LegalBench, que reúnen preguntas jurídicas de respuesta cerrada y miden cuántas acierta cada modelo. Ese no es el objeto de este trabajo: aquí no importa si el modelo llega a una solución dada de antemano, sino qué razones ofrece para pasar de las normas a la conclusión, porque son esas razones las que pueden compararse con las de los jueces.

Las pruebas muestran cómo fundamentan los modelos, no cómo llegan a sus respuestas. Lo que un modelo dice sobre cómo llegó a su respuesta es otra respuesta, y no un informe de lo que hizo. Cuando se le pregunta cómo derivó la conclusión, el modelo no observa su propio funcionamiento para describirlo: produce un texto nuevo, del mismo modo que produjo el anterior, que puede ser plausible y no tener relación con lo que efectivamente determinó la respuesta. La repregunta pide de manera expresa cómo llegó a la conclusión, y esto no cambia: el modelo no recibe el razonamiento que acompañó su primera respuesta, de modo que lo que describe lo reconstruye a partir del texto de esa respuesta. Lo que la repregunta registra es qué dice el modelo sobre cómo llegó a la conclusión cuando se le excluye la respuesta teórica. Por eso las pruebas no estudian lo que determinó cada respuesta, sino fundamentaciones: las razones que el modelo da, en la primera respuesta y ante las preguntas, para pasar de las normas a la conclusión, que pueden evaluarse como justificación con independencia de cómo se llegó a ellas. Es el mismo criterio con que se trata el razonamiento visible (apartado "Esfuerzo y razonamiento"): se lo guarda aparte y se lo considera otro texto del modelo, no una prueba de cómo razonó.

Los resultados no se extienden a otros modelos, materias ni consignas. El estudio sirve, en cambio, para reconstruir y comparar, en condiciones controladas, cómo fundamentan los modelos sus respuestas frente a cómo fundamentan los jueces sus decisiones, y para detectar conductas que después puedan estudiarse.
