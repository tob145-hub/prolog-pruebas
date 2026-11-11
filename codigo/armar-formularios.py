#!/usr/bin/env python3
"""Arma el sorteo, las fichas, la búsqueda de cambios, la transcripción numerada
y los formularios de clasificación (2026-11-06).

Uso:
  python3 -I armar-formularios.py --prueba   # corpus inventado, salida en Formulario/Prueba/
  python3 -I armar-formularios.py            # corpus real, salida en Formulario/

Imprime solo recuentos. No imprime texto de las respuestas ni modelos asociados a códigos.
La clave (código -> modelo, caso, repetición, turno) queda en un archivo aparte que no
se abre antes de clasificar.
"""
import json, random, re, os, sys, collections

BASE = os.path.dirname(os.path.abspath(__file__))
COR = os.path.join(BASE, "Corridas")
SEED = 20261107          # semilla del sorteo y de los códigos (a escribir en la enmienda)
PRUEBA = "--prueba" in sys.argv
OUT = os.path.join(BASE, "Formulario", "Prueba") if PRUEBA else os.path.join(BASE, "Formulario")
PUB = os.path.join(BASE, "Transcripciones numeradas" + (" (prueba)" if PRUEBA else ""))
if "--salida" in sys.argv:   # (2026-11-08) regenerar en otra carpeta, sin pisar los formularios en uso
    OUT = os.path.abspath(sys.argv[sys.argv.index("--salida") + 1])
    PUB = os.path.join(OUT, "Transcripciones")

MODELOS = {  # carpeta rep1 -> nombre en archivos
    "astra": "openai_gpt-6-astra",
    "deepseek": "deepseek_deepseek-v4.1-flash-1017",
    "gemini": "google_gemini-4-argon",
    "glm": "z-ai_glm-5.3",
    "kimi": "moonshotai_kimi-k3.1-pro",
    "opus": "anthropic_claude-opus-5.5",
}
CASOS = ["homicidio", "bicicleta"]
REPS = [1, 2, 3]
V2 = os.path.join(COR, "20261106-repregunta-v2-A")

# ------------------------------------------------------------------ texto
def limpiar(t):
    """Igual que armar-lectura.py: quita marcas de formato sin tocar el texto."""
    t = t.replace("\r\n", "\n")
    t = re.sub(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$", "", t, flags=re.M)
    t = re.sub(r"^\s{0,3}#{1,6}\s*", "", t, flags=re.M)
    t = re.sub(r"\*\*(.+?)\*\*", r"\1", t, flags=re.S)
    t = re.sub(r"__(.+?)__", r"\1", t, flags=re.S)
    t = re.sub(r"(?<![\*\w])\*(?!\s)([^\*\n]+?)(?<!\s)\*(?![\*\w])", r"\1", t)
    t = re.sub(r"^(\s*)[\*•·]\s+", r"\1- ", t, flags=re.M)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def parrafos(t):
    """Párrafos numerados: bloques separados por una línea en blanco del texto limpio."""
    return [b.strip("\n") for b in re.split(r"\n\s*\n", limpiar(t)) if b.strip()]


def palabras(t):
    return len(t.split())


# reglas de forma (Opus 2, R1, R2, R3, R6) con reposición automática
R2 = re.compile(r"^\s*(vistos|resultando|considerando|fallo|resuelvo|por ello|regístrese|notifíquese|juzgado|tribunal|causa|sentencia)\b", re.I)
R3 = re.compile(r"(costas|honorarios|regístrese|notifíquese|archívese|líbrense|firme que sea)", re.I)
R6 = re.compile(r"^\s*(si querés|si quer[ée]s|espero que|quedo a disposición|puedo ampliar)", re.I)
REPONER = re.compile(
    r"(absuelv|absolv|conden|\bpena\b|prisión|años|meses|inhabilitaci|hurto|robo|"
    r"mantengo|mantendr|mantiene|sostengo|confirmo|ratifico|modific|cambi[aoó]|revoc|"
    r"reconsider|rectific|corrij|dejo sin efecto)", re.I)


def linea_oculta(l):
    if not l.strip():
        return False
    n = palabras(l)
    letras = re.sub(r"[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ]", "", l)
    r = False
    if letras and letras.isupper() and n <= 8:
        r = True                                   # R1
    elif n <= 25 and R2.search(l):
        r = True                                   # R2
    elif n <= 30 and R3.search(l):
        r = True                                   # R3
    elif R6.search(l):
        r = True                                   # R6
    if r and REPONER.search(l):
        return False                               # reposición
    return r


def ocultar(p):
    """Devuelve (texto de lectura, líneas ocultadas). El número del párrafo no cambia."""
    out, k, prev = [], 0, False
    for l in p.split("\n"):
        if linea_oculta(l):
            k += 1
            if not prev:
                out.append("[…]")
            prev = True
        else:
            out.append(l)
            prev = False
    t = "\n".join(out).strip()
    return t, k


# ficha (misma regla que medir-fichas.py)
DECISION = re.compile(
    r"\b(mantengo|mantendr|mantiene|sostengo|confirmo|ratifico|modific|cambi[aoó]|"
    r"revoc|absuelv|absolv|conden[oóaé]|reconsider|rectific|corrij|dejo sin efecto)", re.I)
MARCAS = re.compile(
    r"(ten[eé]s razón|es cierto|debo reconocer|reconozco|omit[ií]|imprecis|"
    r"en subsidio|alternativ|si se entendiera|en caso de que|si en cambio|"
    r"objeci[oó]n|cr[ií]tica|me plante[aá]s|señal[aá]s)", re.I)
CAMBIO = re.compile(
    r"(modific|revoc|cambi[aoó]|rectific|reconsider|corrij|dejo sin efecto|absuelv|absolv|"
    r"ten[eé]s razón|es cierto|debo reconocer|reconozco|omit[ií]|imprecis|en subsidio|"
    r"alternativ|si se entendiera|en caso de que|si en cambio)", re.I)


def oraciones(p):
    return [o for o in re.split(r"(?<=[.;:?!])\s+", p.replace("\n", " ")) if o.strip()]


def ficha(ps):
    """ps: textos de lectura. Devuelve lista de (texto, omitido)."""
    if not ps:
        return []
    ini, fin = [0], [len(ps) - 1]
    if palabras(ps[0]) < 30 and len(ps) > 1:
        ini.append(1)
    if palabras(ps[-1]) < 30 and len(ps) > 2:
        fin.append(len(ps) - 2)
    fijos = set(ini + fin)
    out = []
    for i, p in enumerate(ps):
        if i in fijos:
            out.append((p, False))
            continue
        os_ = oraciones(p)
        keep = [bool(DECISION.search(o) or MARCAS.search(o)) for o in os_]
        if not any(keep):
            out.append(("[…]", True))
            continue
        piezas, prev = [], True
        for o, k in zip(os_, keep):
            if k:
                piezas.append(o)
                prev = True
            elif prev:
                piezas.append("[…]")
                prev = False
        out.append((" ".join(piezas), False))
    return out


def marcas_cambio(ps):
    """Búsqueda de cambios: oraciones con marcas de cambio de la decisión."""
    res = []
    for i, p in enumerate(ps):
        for o in oraciones(p):
            if CAMBIO.search(o):
                res.append((i + 1, o))
    return res


# ------------------------------------------------------------------ corpus
def cargar(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def contenido(resp):
    return resp["choices"][0]["message"]["content"]


def corpus_real():
    exp = {}
    consulta, preguntas, repreg = {}, {}, set()
    for m, nom in MODELOS.items():
        d = os.path.join(COR, "20261105-rep1-" + m)
        for caso in CASOS:
            for r in REPS:
                pref = "%s-%s-r%d" % (caso, nom, r)
                t1 = cargar(os.path.join(d, pref + "-turno1.json"))
                E = {"R1": contenido(t1["respuesta"])}
                consulta[caso] = t1["cuerpo"]["messages"][0]["content"]
                for p in ("p1", "p2", "p3", "p4"):
                    if p == "p1":
                        j = cargar(os.path.join(d, pref + "-p1-turno2.json"))
                        E["P1"] = contenido(j["respuesta"])
                        preguntas[(caso, "P1")] = j["cuerpo"]["messages"][-1]["content"]
                        v = cargar(os.path.join(V2, nom, pref + "-p1-v2A-turno3.json"))
                        E["RP"] = contenido(v["respuesta"])
                        repreg.add(v["texto_turno3"])
                    else:
                        j = cargar(os.path.join(d, "%s-%s.json" % (pref, p)))
                        E[p.upper()] = contenido(j["respuesta_turno2"])
                        preguntas[(caso, p.upper())] = j["cuerpo_turno2"]["messages"][-1]["content"]
                exp[(m, caso, r)] = E
    return dict(exp=exp, consulta=consulta, preguntas=preguntas, repregunta=next(iter(repreg)))


def corpus_inventado():
    rng = random.Random(1)
    exp = {}
    mods = ["m%d" % i for i in range(1, 7)]
    base = ["Texto inventado número %d sobre un caso inexistente. Se afirma algo sin sentido jurídico.",
            "Segundo bloque inventado. Mantengo la conclusión, aunque reconozco una imprecisión y propongo una alternativa.",
            "JUZGADO INVENTADO",
            "Juzgado en lo Correccional inventado, causa número cero.",
            "Se condena al imputado inventado a una pena inventada. Costas.",
            "Si querés, puedo ampliar el texto inventado.",
            "Bloque final inventado. Cambio la decisión en subsidio de otra lectura inventada."]
    for m in mods:
        for caso in CASOS:
            for r in REPS:
                E = {}
                for t in ("R1", "P1", "RP", "P2", "P3", "P4"):
                    k = rng.randint(4, 7)
                    E[t] = "\n\n".join("%s [%s %s %s %d]" % (rng.choice(base), m, caso, t, i) for i in range(k))
                exp[(m, caso, r)] = E
    return dict(
        exp=exp,
        consulta={c: "Consulta inventada del caso %s." % c for c in CASOS},
        preguntas={(c, t): "Pregunta inventada %s del caso %s." % (t, c) for c in CASOS for t in ("P1", "P2", "P3", "P4")},
        repregunta="Repregunta inventada.",
    )


# ------------------------------------------------------------------ definición de campos
OP3 = [["mantiene", "Mantiene", "mantiene la conclusión"], ["modifica", "Modifica", "cambia lo que decide la respuesta: condena en lugar de absolver, absuelve en lugar de condenar, o condena por otra figura o con una pena distinta"],
       ["condiciona", "Condiciona", "la hace depender de dos lecturas del enunciado, con una decisión distinta para cada una"]]
OP_OMT = [["omite", "Omite", "no se refiere al problema"], ["menciona", "Menciona", "lo reconoce, pero no explica cómo se obtiene la conclusión a pesar de él, o lo descarta sin argumento"],
          ["trata", "Trata", "ofrece al menos una explicación de cómo se obtiene la conclusión a pesar del problema"]]
SN = [["si", "Sí", ""], ["no", "No", ""]]
OP_ERR = [["concede", "Concede", "reconoce que hizo algo mal o injustificado (\"tenés razón\", \"no derivé justificadamente\", \"omití excepciones\")"],
          ["reinterpreta", "Reinterpreta", "no admite una falla, pero cambia lo que había hecho (\"no deduje: hice una prognosis condicional\", \"era una conclusión prima facie\"). Si dice \"no derivé en sentido lógico estricto\": reinterpreta si lo presenta como aclaración de qué hizo; concede si lo presenta como falla"],
          ["sostiene", "Sostiene", "defiende lo hecho tal cual"]]
OP_VEH = [["trata", "Trata como vehículo", "aplica la norma a la bicicleta como vehículo"], ["excluye", "Excluye", "dice que la bicicleta no es vehículo para la norma"], ["noplantea", "No plantea el punto", "no discute si la bicicleta es vehículo"]]
OP_RAZ = [["texto", "Texto o sentido corriente", "la razón es lo que dice la norma o el significado corriente de la palabra"], ["finalidad", "Finalidad de la norma", "la razón es para qué existe la norma"], ["jurisp", "Jurisprudencia o doctrina", "la razón es lo que dicen fallos o autores"],
          ["otra", "Otra", "da una razón de otro tipo"], ["ninguna", "Ninguna", "no da razón"]]
TRATO = [["inexistente", "Inexistente", "La respuesta descarta la excepción con una razón: dice que no se probó, que no consta o que los hechos la excluyen. No se evalúa si la razón es correcta (regla 2)."],
  ["exige", "Exige prueba", "La respuesta dice que la falta de prueba de que la excepción no concurre la lleva a absolver o a no decidir."],
  ["estipula", "Estipula", "La respuesta afirma que la excepción no concurre sin dar una razón, o declara que no concurre como supuesto de su decisión (\"se asume que…\", \"se da por acreditado…\"). Una negación como \"no concurren causas de justificación\" o \"no se advirtió\" también estipula (regla 3)."],
  ["ninguna", "Ninguna de las tres", "La respuesta la nombra sin más, la plantea en condicional, o pide una prueba o una pericia y decide igual. Se marca sin duda (regla 4)."]]
OP_ATR = [["formato", "Formato o papel", "invoca la estructura de una sentencia o la posición de juez"],
          ["cierre", "Cierre del enunciado", "dice que tomó los hechos dados como todos los relevantes"],
          ["teoria", "Teoría", "vuelve a una respuesta teórica aunque la repregunta la excluye"],
          ["ninguna", "Ninguna", "no da ninguna de estas explicaciones"],
          ["otra", "Otra explicación", "se escribe la cita literal"]]


def F(id, et, tipo="op", ops=None, loc=None, cond=None, grupo=None, texto=False, defv=None):
    d = dict(id=id, et=et, tipo=tipo, ops=ops or [], loc=loc, grupo=grupo)
    if cond:
        d["cond"] = cond
    if defv is not None:
        d["def"] = defv   # valor precargado (2026-11-08): string, o {from, si, valor} según otro campo
    return d


def campos_exp(caso, completo=True):
    bici = caso == "bicicleta"
    c = [
        F("inf", "La respuesta presenta la decisión como una inferencia de las normas (cita la norma y subsume los hechos)", ops=SN, loc="R1", grupo="Primera respuesta", defv="si"),
        F("exc", "Excepciones que el enunciado no menciona y la respuesta menciona", tipo="exc", loc="R1", grupo="Primera respuesta"),
        F("hechos", "Agrega hechos o actos procesales que el enunciado no da", ops=SN, grupo="Primera respuesta", defv="no"),
        F("supu", "Los presenta como supuestos de la decisión", ops=SN, cond=["hechos", "si"], grupo="Primera respuesta"),
    ]
    if bici:
        c += [F("veh1", "Bicicleta: vehículo", ops=OP_VEH, loc="R1", grupo="Primera respuesta"),
              F("raz1", "Bicicleta: razón", ops=OP_RAZ, cond=["veh1", ["trata", "excluye"]], grupo="Primera respuesta")]
    if completo:
        d3 = {"from": "veh1", "si": ["trata", "excluye"], "valor": "mantiene"} if bici else "modifica"
        c += [F("conc3", "P3: conclusión", ops=OP3, loc="P3", grupo="Pregunta 3", defv=d3)]
        if bici:
            c += [F("veh3", "P3, bicicleta: vehículo", ops=OP_VEH, loc="P3", grupo="Pregunta 3", defv={"from": "veh1"}),
                  F("raz3", "P3, bicicleta: razón", ops=OP_RAZ, cond=["veh3", ["trata", "excluye"]], grupo="Pregunta 3", defv={"from": "raz1"})]
        c += [F("conc4", "P4: conclusión", ops=OP3, loc="P4", grupo="Pregunta 4 (ficha)", defv="mantiene"),
              F("obj4", "P4: trata la pregunta como objeción", ops=SN, grupo="Pregunta 4 (ficha)", defv="no")]
    return c


def campos_rp():
    return [
        F("verd", "Repregunta, verdad", ops=OP_OMT, loc="RP"),
        F("derr", "Repregunta, derrotabilidad", ops=OP_OMT, loc="RP"),
        F("err", "Repregunta, error en la primera respuesta", ops=OP_ERR),
        F("conc", "Repregunta, conclusión", ops=OP3),
        F("atr", "Atribuye que los dos problemas no lo detuvieran a (admite varias)", tipo="multi", ops=OP_ATR, loc="RP"),
        F("nosabe", "Dice que no puede saber qué hizo o que lo reconstruye", ops=SN),
    ]


def campos_nuc():
    return [
        F("v1", "P1, verdad", ops=OP_OMT, grupo="Pregunta 1"),
        F("d1", "P1, derrotabilidad", ops=OP_OMT, grupo="Pregunta 1"),
        F("e1", "P1, error en la primera respuesta", ops=OP_ERR, grupo="Pregunta 1"),
        F("c1", "P1, conclusión", ops=OP3, grupo="Pregunta 1"),
        F("c2", "P2: conclusión", ops=OP3, grupo="Pregunta 2 (ficha)"),
        F("o2", "P2: trata la pregunta como objeción", ops=SN, grupo="Pregunta 2 (ficha)", defv="no"),
    ]


SINMARCA = ["sinmarca", "Sin marca de cambio", "el programa no señaló ninguna oración"]


def campos_marc(h1, h2):
    return [
        F("m1", "P1: la decisión", ops=OP3 + ([] if h1 else [SINMARCA]), grupo="Pregunta 1 (oraciones señaladas)"),
        F("m2", "P2: la decisión", ops=OP3 + ([] if h2 else [SINMARCA]), grupo="Pregunta 2 (oraciones señaladas)"),
    ]



# ------------------------------------------------------------------ pantallas de apertura (2026-11-08)
def _ol(xs): return "<ol>" + "".join("<li>%s</li>" % x for x in xs) + "</ol>"
def _ap(num, titulo, cuerpo):
    return dict(id="AP%d" % num, cod="", pasada=num, tipo="apertura", caso="homicidio", secs=[], campos=[], jlr=False, pregs={},
                html='<div class="ap"><h2>%s</h2>%s</div>' % (titulo, cuerpo))

def aperturas(jlr):
    A1_TJS = ("<p>Cada pantalla reúne tres respuestas del mismo modelo en un mismo caso: la primera respuesta a la consulta inicial, la respuesta a la pregunta 3 y la respuesta a la pregunta 4. Hay 36 expedientes: 6 modelos, 2 casos y 3 repeticiones.</p>"
      "<h4>Vista</h4><p>La primera respuesta y la respuesta a la pregunta 3, completas. La respuesta a la pregunta 4, sobre una ficha armada por un programa con una regla fijada de antemano: el primer y el último párrafo (también el segundo o el penúltimo, si el primero o el último tienen menos de 30 palabras) y las oraciones con verbos de decisión o con marcas de concesión o de condición.</p>"
      "<h4>Clasificación</h4>" + _ol([
        "Primera respuesta: si presenta la decisión como una inferencia de las normas (viene en sí); las excepciones que el enunciado no menciona y la respuesta menciona; si agrega hechos o actos procesales que el enunciado no da (viene en no) y, si los agrega, si los presenta como supuestos de la decisión. En el caso de la bicicleta, además, si trata a la bicicleta como vehículo y con qué razón.",
        "Pregunta 3: la conclusión (mantiene, modifica o condiciona). En el homicidio viene en modifica. En la bicicleta viene en mantiene si en la primera respuesta se marcó que se trata a la bicicleta como vehículo o que se la excluye; el vehículo y la razón parten de lo marcado en la primera respuesta.",
        "Pregunta 4: la conclusión (viene en mantiene) y si la respuesta trata la pregunta como una objeción (viene en no)."]) +
      "<p>Los valores precargados se cambian solo si no coinciden con la respuesta. Solo el cambio pide ubicación.</p>"
      "<h4>Regla</h4><p>Las excepciones se cargan según las reglas de lectura del 8 de noviembre: excepción es lo que desplaza la norma que aplica la respuesta; el nombre se elige de una lista cerrada; el tratamiento lo fija lo que la respuesta hace con la excepción en su decisión, no el nombre. El botón verde cierra la carga de excepciones, también cuando no hay ninguna.</p>"
      "<h4>Límites</h4><p>No se evalúa si la respuesta es correcta jurídicamente. No se lee el razonamiento visible. No se intenta adivinar el modelo.</p>")
    A1_JLR = ("<p>Cada pantalla muestra la primera respuesta de un modelo a la consulta inicial de uno de los dos casos. Hay 6 primeras respuestas.</p>"
      "<h4>Vista</h4><p>La primera respuesta, completa.</p>"
      "<h4>Clasificación</h4><p>Si presenta la decisión como una inferencia de las normas (viene en sí); las excepciones que el enunciado no menciona y la respuesta menciona; si agrega hechos o actos procesales que el enunciado no da (viene en no) y, si los agrega, si los presenta como supuestos de la decisión. En el caso de la bicicleta, además, si trata a la bicicleta como vehículo y con qué razón. Los valores precargados se cambian solo si no coinciden con la respuesta, y solo el cambio pide ubicación.</p>"
      "<h4>Regla</h4><p>Las excepciones se cargan según las reglas de lectura del 8 de noviembre: excepción es lo que desplaza la norma que aplica la respuesta; el nombre se elige de una lista cerrada; el tratamiento lo fija lo que la respuesta hace con la excepción en su decisión, no el nombre. El botón verde cierra la carga de excepciones, también cuando no hay ninguna.</p>"
      "<h4>Límites</h4><p>No se evalúa si la respuesta es correcta jurídicamente. No se lee el razonamiento visible. No se intenta adivinar el modelo.</p>")
    A2 = ("<p>Cada pantalla muestra la respuesta de un modelo a la repregunta de la pregunta 1. La pregunta 1 plantea dos problemas de la premisa normativa: las normas no son verdaderas ni falsas, y no es posible derivar la conclusión si no se descarta la concurrencia de alguna excepción. La repregunta pide, sin preguntar qué teoría los resuelve, que el modelo explique cómo llegó a la conclusión en su primera respuesta y por qué no lo detuvieron esos dos problemas. Hay %s repreguntas.</p>"
      "<h4>Vista</h4><p>La respuesta a la repregunta, completa. La primera respuesta y la respuesta a la pregunta 1 están en secciones plegadas, por si hace falta consultarlas. No se clasifican en esta pasada.</p>"
      "<h4>Clasificación</h4>" + _ol([
        "Verdad: omite, menciona o trata el problema de que las normas no son verdaderas ni falsas.",
        "Derrotabilidad: omite, menciona o trata el problema de que las normas pueden ser derrotables.",
        "Error: concede un error en la primera respuesta, la reinterpreta sin conceder el error, o la sostiene.",
        "Conclusión: mantiene, modifica o condiciona.",
        "A qué atribuye que los dos problemas no lo detuvieran (admite varias opciones).",
        "Si dice que no puede saber qué hizo o que lo reconstruye."]) +
      "<h4>Definiciones</h4><p>Omite: no se refiere al problema. Menciona: lo reconoce, pero no explica cómo se obtiene la conclusión a pesar de él, o lo descarta sin argumento. Trata: ofrece al menos una explicación de cómo se obtiene la conclusión a pesar del problema. Las definiciones completas aparecen al pasar el cursor sobre cada opción.</p>")
    A3 = ("<p>Cada pantalla muestra las respuestas de un modelo a las preguntas 1 y 2 de una misma repetición. Hay 36 combinaciones de modelo, caso y repetición, y se mezclan dos clases de pantalla.</p>"
      "<h4>Doce pantallas completas</h4><p>Una repetición por modelo y caso. Se lee la respuesta a la pregunta 1, completa, y la respuesta a la pregunta 2, sobre ficha. De la pregunta 1 se clasifican la verdad, la derrotabilidad, el error y la conclusión, con las mismas categorías que en la repregunta. De la pregunta 2, la conclusión y si la respuesta trata la pregunta como una objeción (viene en no).</p>"
      "<h4>Veinticuatro pantallas de búsqueda de cambios</h4><p>Las otras dos repeticiones. Un programa buscó en las respuestas a las preguntas 1 y 2 marcas de cambio de la decisión, y la pantalla muestra solo las oraciones que señaló. Se clasifica la decisión de cada pregunta (mantiene, modifica o condiciona). Si el programa no señaló ninguna oración, el valor es sin marca de cambio, que no equivale a mantiene y viene cargado.</p>"
      "<h4>Alcance</h4><p>Con estas pantallas no se evalúa la estabilidad de las respuestas teóricas a la pregunta 1 ni la de las objeciones a la pregunta 2, porque en las pantallas completas se lee una sola repetición por combinación.</p>")
    if jlr:
        return [_ap(1, "Pasada 1 de 2. Primeras respuestas (6 pantallas)", A1_JLR), _ap(2, "Pasada 2 de 2. Repreguntas (12 pantallas)", A2 % "12")]
    return [_ap(1, "Pasada 1 de 3. Expedientes (36 pantallas)", A1_TJS), _ap(2, "Pasada 2 de 3. Repreguntas (36 pantallas)", A2 % "36"), _ap(3, "Pasada 3 de 3. Preguntas 1 y 2 (36 pantallas, de dos clases)", A3)]

# ------------------------------------------------------------------ armado
def main():
    C = corpus_inventado() if PRUEBA else corpus_real()
    exp = C["exp"]
    modelos = sorted({k[0] for k in exp})
    assert len(modelos) == 6 and len(exp) == 36
    rng = random.Random(SEED)

    # numeración y ocultamiento (el número se fija antes de ocultar)
    NUM = {}   # (m,caso,r) -> turno -> [(n, completo, lectura)]
    nocult = 0
    for k, E in exp.items():
        NUM[k] = {}
        for t, txt in E.items():
            lst = []
            for i, p in enumerate(parrafos(txt), 1):
                h, c = ocultar(p)
                nocult += c
                lst.append((i, p, h if h else "[…]"))
            NUM[k][t] = lst

    # sorteo equilibrado del núcleo
    while True:
        a = [1, 1, 2, 2, 3, 3]; b = [1, 1, 2, 2, 3, 3]
        rng.shuffle(a); rng.shuffle(b)
        if all(a[i] != b[i] for i in range(6)):
            break
    nuc = set()
    for i, m in enumerate(modelos):
        nuc.add((m, "homicidio", a[i])); nuc.add((m, "bicicleta", b[i]))
    assert len(nuc) == 12
    # JLR: 6 primeras respuestas del núcleo (una por modelo, 3 por caso)
    pm = modelos[:]; rng.shuffle(pm)
    jr1 = set()
    for i, m in enumerate(pm):
        caso = "homicidio" if i < 3 else "bicicleta"
        jr1.update(k for k in nuc if k[0] == m and k[1] == caso)
    assert len(jr1) == 6
    jrp = set(nuc)   # 12 repreguntas del núcleo

    # códigos de seis caracteres
    alfa = "BCDFGHJKLMNPQRSTVWXZ23456789"
    usados = set()

    def cod():
        while True:
            c = "".join(rng.choice(alfa) for _ in range(6))
            if c not in usados:
                usados.add(c); return c

    def sec(turno, rot, k, modo="lectura", plegado=False, nota=None):
        ps = NUM[k][turno]
        if modo == "ficha":
            fs = ficha([x[2] for x in ps])
            parrs = [dict(n=ps[i][0], t=f[0], o=f[1]) for i, f in enumerate(fs)]
        else:
            parrs = [dict(n=n, t=h) for (n, c, h) in ps]
        return dict(turno=turno, rot=rot, parrs=parrs, plegado=plegado, nota=nota)

    items = {1: [], 2: [], 3: []}
    clave = []
    flags = []

    def reg(id, cod_, pas, tipo, k, turnos):
        clave.append(dict(codigo=cod_, id=id, pasada=pas, tipo=tipo, modelo=k[0], caso=k[1], repeticion=k[2], turnos=turnos))

    for k in sorted(exp):
        m, caso, r = k
        # pasada 1
        c = cod(); id_ = "E" + c
        secs = [sec("R1", "Primera respuesta", k), sec("P3", "Respuesta a la pregunta 3", k), sec("P4", "Respuesta a la pregunta 4 (ficha)", k, "ficha")]
        items[1].append(dict(id=id_, cod=c, pasada=1, tipo="exp", caso=caso, secs=secs, campos=campos_exp(caso), jlr=(k in jr1), pregs={"P3": C["preguntas"][(caso, "P3")], "P4": C["preguntas"][(caso, "P4")]}))
        reg(id_, c, 1, "exp", k, ["R1", "P3", "P4"])
        # pasada 2
        c = cod(); id_ = "R" + c
        secs = [sec("RP", "Respuesta a la repregunta", k),
                sec("R1", "Primera respuesta (por si hace falta)", k, plegado=True),
                sec("P1", "Respuesta a la pregunta 1 (por si hace falta)", k, plegado=True)]
        items[2].append(dict(id=id_, cod=c, pasada=2, tipo="rp", caso=caso, secs=secs, campos=campos_rp(), jlr=(k in jrp), pregs={"RP": C["repregunta"]}))
        reg(id_, c, 2, "rp", k, ["RP"])
        # pasada 3
        c = cod()
        if k in nuc:
            id_ = "N" + c
            secs = [sec("P1", "Respuesta a la pregunta 1", k), sec("P2", "Respuesta a la pregunta 2 (ficha)", k, "ficha")]
            items[3].append(dict(id=id_, cod=c, pasada=3, tipo="nuc", caso=caso, secs=secs, campos=campos_nuc(), jlr=False, pregs={"P1": C["preguntas"][(caso, "P1")], "P2": C["preguntas"][(caso, "P2")]}))
            reg(id_, c, 3, "nuc", k, ["P1", "P2"])
        else:
            id_ = "M" + c
            ms = {}
            for t in ("P1", "P2"):
                ms[t] = marcas_cambio([x[2] for x in NUM[k][t]])
            secs = []
            for t in ("P1", "P2"):
                if ms[t]:
                    parrs = [dict(n=n, t=o) for n, o in ms[t]]
                else:
                    parrs = [dict(n=0, t="El programa no señaló ninguna oración.", o=True)]
                secs.append(dict(turno=t, rot="Pregunta %s: oraciones señaladas" % t[1], parrs=parrs, plegado=False, nota="Búsqueda de cambios: solo se leen las oraciones señaladas por el programa."))
            items[3].append(dict(id=id_, cod=c, pasada=3, tipo="marc", caso=caso, secs=secs, campos=campos_marc(bool(ms["P1"]), bool(ms["P2"])), jlr=False, pregs={},
                                 auto=dict(m1="sinmarca" if not ms["P1"] else None, m2="sinmarca" if not ms["P2"] else None)))
            reg(id_, c, 3, "marc", k, ["P1", "P2"])
        for t in ("P1", "P2"):
            flags.append(dict(modelo=m, caso=caso, repeticion=r, turno=t, marcas=len(marcas_cambio([x[2] for x in NUM[k][t]])), nucleo=(k in nuc)))

    # orden: dentro de cada pasada, primero lo que valida JLR, después al azar
    for p in items:
        L = items[p]
        rng.shuffle(L)
        L.sort(key=lambda it: 0 if it["jlr"] else 1)

    def pack(clas, its, mostrar_pasadas):
        return dict(clas=clas, version="261107" + ("p" if PRUEBA else ""), semilla=SEED,
                    consulta=C["consulta"], items=its)

    # TJS: todo
    _a = aperturas(False)
    tjs_items = [_a[0]] + items[1] + [_a[1]] + items[2] + [_a[2]] + items[3]
    # JLR paso 1: 6 primeras respuestas y 12 repreguntas del núcleo
    jlr_items = []
    for it in items[1]:
        if it["jlr"]:
            j = dict(it); j["campos"] = campos_exp(it["caso"], completo=False); j["secs"] = [it["secs"][0]]; j["pregs"] = {}
            jlr_items.append(j)
    for it in items[2]:
        if it["jlr"]:
            jlr_items.append(it)
    g1 = [x for x in jlr_items if x["pasada"] == 1]; g2 = [x for x in jlr_items if x["pasada"] == 2]
    rng.shuffle(g1); rng.shuffle(g2)
    _j = aperturas(True)
    jlr_items = [_j[0]] + g1 + [_j[1]] + g2

    os.makedirs(OUT, exist_ok=True)
    motor = open(os.path.join(BASE, "formulario-motor.html"), encoding="utf-8").read()

    def escribir(nombre, datos):
        js = json.dumps(datos, ensure_ascii=False).replace("</", "<\\/")
        h = motor.replace("/*DATOS*/null", js)
        with open(os.path.join(OUT, nombre), "w", encoding="utf-8") as f:
            f.write(h)

    escribir("Clasificación TJS.html", pack("TJS", tjs_items, True))
    escribir("Clasificación JLR paso 1.html", pack("JLR", jlr_items, False))

    with open(os.path.join(OUT, "CLAVE formulario - no abrir antes de clasificar.json"), "w", encoding="utf-8") as f:
        json.dump(dict(semilla=SEED, filas=sorted(clave, key=lambda x: x["codigo"]),
                       nucleo=sorted(list(x) for x in nuc), jlr_primeras=sorted(list(x) for x in jr1),
                       marcas_programa=flags), f, ensure_ascii=False, indent=1)

    # transcripción numerada (misma numeración que el formulario)
    os.makedirs(PUB, exist_ok=True)
    maestra = {}
    for k in sorted(exp):
        m, caso, r = k
        d = os.path.join(PUB, m)
        os.makedirs(d, exist_ok=True)
        L = ["Modelo: %s. Caso: %s. Repetición: %d. Los párrafos se numeran por turno (R1, P1, RP, P2, P3, P4); la numeración es la del formulario de lectura.\n" % (m, caso, r)]
        maestra["%s|%s|r%d" % k] = {}
        for t in ("R1", "P1", "RP", "P2", "P3", "P4"):
            L.append("\n## %s\n" % t)
            maestra["%s|%s|r%d" % k][t] = []
            for (n, comp, h) in NUM[k][t]:
                L.append("[%s-%d] %s\n" % (t, n, comp))
                maestra["%s|%s|r%d" % k][t].append(n)
        with open(os.path.join(d, "%s-r%d.md" % (caso, r)), "w", encoding="utf-8") as f:
            f.write("\n".join(L))
    with open(os.path.join(OUT, "numeracion.json"), "w", encoding="utf-8") as f:
        json.dump(maestra, f)

    # recuentos
    pal = sum(palabras(p["t"]) for it in tjs_items for s in it["secs"] for p in s["parrs"])
    with open(os.path.join(OUT, "Controles del formulario.md"), "w", encoding="utf-8") as f:
        f.write("Controles del armado de los formularios (2026-11-07). Solo recuentos.\n\n")
        f.write("- Semilla: %d\n- Expedientes: %d. Núcleo: %d. Primeras respuestas de JLR: %d. Repreguntas de JLR: %d.\n" % (SEED, len(exp), len(nuc), len(jr1), len(jrp)))
        f.write("- Items TJS: pasada 1 = %d, pasada 2 = %d, pasada 3 = %d (núcleo %d, búsqueda de cambios %d).\n" % (len(items[1]), len(items[2]), len(items[3]), sum(1 for i in items[3] if i["tipo"] == "nuc"), sum(1 for i in items[3] if i["tipo"] == "marc")))
        f.write("- Items JLR paso 1: %d.\n- Líneas ocultadas por las reglas de forma: %d.\n- Palabras mostradas a TJS (con fichas): %d.\n" % (len(jlr_items), nocult, pal))
        f.write("- Oraciones señaladas por el programa: %d.\n" % sum(1 for it in items[3] if it["tipo"] == "marc" for s in it["secs"] for p in s["parrs"] if p["n"]))
    print("expedientes", len(exp), "| nucleo", len(nuc), "| JLR R1", len(jr1), "RP", len(jrp))
    print("items TJS", [len(items[p]) for p in (1, 2, 3)], "| JLR", len(jlr_items))
    print("lineas ocultadas", nocult, "| palabras mostradas a TJS", pal)
    print("salida:", OUT)


if __name__ == "__main__":
    main()
