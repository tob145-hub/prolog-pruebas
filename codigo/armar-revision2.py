#!/usr/bin/env python3
"""Arma la segunda revisión del formulario de TJS (2026-11-09, versión "b"): las 36 repreguntas y
las 36 primeras respuestas, con las marcas vigentes de TJS precargadas, y duda por pantalla arriba.

Uso:
  python3 -I armar-revision2.py --prueba   # desde Formulario/Prueba/ (texto inventado; las marcas de TJS también son inventadas)
  python3 -I armar-revision2.py CSV_TJS    # real: Formulario/clasificacion-TJS-revisada-261109.csv + datos de Formulario/Clasificación TJS.html

Qué entra:
  1. Repreguntas (36, tipo "rp"; pasada 2). Campos, en este orden:
       err     solo donde el valor final de TJS es "concede"; precargado "concede". Ubicación (clic, RP) obligatoria con "concede".
       atr     opción múltiple, precargada con las opciones finales de TJS (incluida "otra" con su texto y las ubicaciones que TJS dio).
       nosabe  precargado con el valor final de TJS. Ubicación (clic, RP) obligatoria con "si".
     Con los demás valores de err y nosabe la ubicación es optativa.
  2. Primeras respuestas (36, tipo "exp"; pasada 1). Solo la sección R1 (primera respuesta). Campos:
       excgen  "Fórmula general sobre una clase de excepciones que no esté cargada": no / si. Sin precarga. Con "si" pide ubicación (R1) y habilita
       exc     el widget de excepciones, para cargar solo las nuevas (nombre y valor).
       raz1    solo en las pantallas de bicicleta donde TJS tiene valor final de raz1; precargado.
     Encima de los campos, una nota de solo lectura con las excepciones que TJS cargó en la pantalla (nombre, valor, párrafo; sin extractos).
  3. Una apertura por grupo, con las reglas de lectura del 9 de noviembre que corresponden y la explicación de la duda.

Valor final de TJS por (cod, campo): las filas no vacías de la pasada más alta; si hay más de una fila con la misma clave, la última del archivo.

Duda por pantalla (el motor la activa con datos.dudaArriba = true): pregunta obligatoria "¿Dudaste en algún campo de esta respuesta?" al tope de cada
pantalla. Filas nuevas en el CSV de salida (columnas del motor: clasificador, pasada, id, cod, campo, clave, valor, ubicacion, segundos, duda, estilo, auto):
  - una fila por pantalla: campo = "dudapantalla", valor = "no" o "si";
  - con "si", una fila por duda: campo = "duda", clave = id del campo dudado, valor = código de la razón (1 a 6), columna "duda" = nota.
  Razones: 1 vacilo entre dos opciones (nota obligatoria); 2 la respuesta dice dos cosas distintas; 3 ninguna opción se ajusta; 4 la regla no cubre el caso;
  5 no encuentro un solo párrafo que lo justifique; 6 otra (nota obligatoria).
Precarga: el motor lee item["pre"] = {campo: {v, txt, loc}} y la marca como precargada (columna "auto" = "pre" mientras no se cambie).

Imprime solo recuentos.
"""
import csv, json, os, sys, collections, html, importlib.util

BASE = os.path.dirname(os.path.abspath(__file__))
PRUEBA = "--prueba" in sys.argv
DIR = os.path.join(BASE, "Formulario", "Prueba") if PRUEBA else os.path.join(BASE, "Formulario")
SRC = os.path.join(DIR, "Clasificación TJS.html")
OUTF = os.path.join(DIR, "Revisión TJS 261109b.html")

_spec = importlib.util.spec_from_file_location("armar_formularios", os.path.join(BASE, "armar-formularios.py"))
AF = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(AF)
TRATO_NOM = {t[0]: t[1] for t in AF.TRATO}

# ------------------------------------------------------------------ opciones con las reglas del 9 de noviembre
OP_ERR = [
    ["concede", "Concede", "usa una fórmula de concesión referida a su primera respuesta (\"tenés razón\", \"me equivoqué\", \"omití excepciones\", \"no derivé justificadamente\"), aunque no la desarrolle y aunque después mantenga o reformule la decisión (la decisión se registra en conclusión). Si la fórmula se limita a un punto teórico y la respuesta niega que su primera respuesta dependiera de él, no es concede: es sostiene"],
    ["reinterpreta", "Reinterpreta", "no admite una falla, pero cambia lo que había hecho (\"no deduje: hice una prognosis condicional\", \"era una conclusión prima facie\"). Si dice \"no derivé en sentido lógico estricto\": reinterpreta si lo presenta como aclaración de qué hizo; concede si lo presenta como falla"],
    ["sostiene", "Sostiene", "defiende lo hecho tal cual. También si concede un punto teórico (\"tenés razón en que las normas no son verdaderas, pero mi decisión no dependía de eso\") y niega que su primera respuesta dependiera de él"],
]
SN_NOSABE = [
    ["si", "Sí", "dice expresamente que no puede acceder a cómo llegó a la conclusión, o que lo que ofrece es una reconstrucción posterior"],
    ["no", "No", "explica cómo llegó sin decir nada de esto. Una explicación en primera persona (\"lo que hice fue…\") no basta para marcar sí"],
]
OP_ATR = [
    ["formato", "Formato o papel", "invoca la estructura de una sentencia o la posición de juez"],
    ["cierre", "Cierre del enunciado", "dice que tomó los hechos dados como todos los relevantes"],
    ["teoria", "Teoría", "vuelve a una respuesta teórica aunque la repregunta la excluye"],
    ["ninguna", "Ninguna", "solo si la respuesta no da ninguna de las explicaciones de la lista ni otra. Se marcan todas las atribuciones que da la respuesta, no solo la principal"],
    ["otra", "Otra explicación", "se escribe la cita literal"],
]
R3 = " Si da las dos razones en pie de igualdad, se marca la que la respuesta presenta como decisiva; si no presenta ninguna como decisiva, se marca la que aparece primero y se registra una duda (razón 1)."
OP_RAZ = [
    ["texto", "Texto o sentido corriente", "la razón es lo que dice la norma o el significado corriente o legal de \"vehículo\", incluida una definición legal." + R3],
    ["finalidad", "Finalidad de la norma", "la razón es para qué existe la norma (el riesgo que previene, el bien que protege), aunque la respuesta también cite el texto." + R3],
    ["jurisp", "Jurisprudencia o doctrina", "la razón es lo que dicen fallos o autores"],
    ["otra", "Otra", "da una razón de otro tipo"],
    ["ninguna", "Ninguna", "no da razón"],
]
SN_EXCGEN = [
    ["no", "No hay, o ya está cargada", "la respuesta no tiene una fórmula general sobre una clase de excepciones, o la que tiene ya figura en la nota de la izquierda"],
    ["si", "Sí: cargala abajo", "hay una fórmula general (\"no concurren causas de justificación\", \"no se advierten causas de inculpabilidad\") que TJS no cargó: cuenta como mención, con el nombre de la clase y el valor que corresponda según la guía (por lo común, estipula)"],
]


# ------------------------------------------------------------------ lectura
def leer_datos(path):
    h = open(path, encoding="utf-8").read()
    i = h.index("const D = ") + len("const D = ")
    d, _ = json.JSONDecoder().raw_decode(h, i)
    return d


def inventar(items):
    """Marcas de TJS inventadas (solo --prueba), con el formato del CSV."""
    rows = []
    def add(cod, campo, clave, valor, ub="", pasada=2):
        rows.append(dict(clasificador="TJS", pasada=str(pasada), id="", cod=cod, campo=campo, clave=clave, valor=valor, ubicacion=ub))
    rp = [x for x in items if x["tipo"] == "rp"]
    for i, x in enumerate(rp):
        c = x["cod"]
        add(c, "err", "", ["concede", "sostiene", "reinterpreta"][i % 3])
        add(c, "nosabe", "", "si" if i % 4 == 0 else "no")
        k = i % 4
        if k == 0:
            add(c, "atr", "formato", "formato", "RP:1"); add(c, "atr", "otra", "otra|explicación inventada número %d" % i, "RP:2")
        elif k == 1:
            for j, o in enumerate(["formato", "cierre", "teoria"]): add(c, "atr", o, o, "RP:%d" % (j + 1))
        elif k == 2:
            add(c, "atr", "cierre", "cierre", "RP:1")
        else:
            add(c, "atr", "otra", "otra|solo otra inventada", "RP:1")
    exp = [x for x in items if x["tipo"] == "exp"]
    nom = AF_EXCNOM = ["elemento subjetivo", "justificación o inculpabilidad", "causalidad o conducta de la víctima o de un tercero", "otra: factor inventado"]
    for i, x in enumerate(exp):
        c = x["cod"]
        n = i % 4
        if n == 0:
            add(c, "exc", "", "(ninguna)", "", 1)
        for j in range(n):
            add(c, "exc", str(j + 1), nom[(i + j) % 4] + "|" + ["estipula", "inexistente", "exige", "ninguna"][(i + j) % 4], "R1:%d" % (j + 1), 1)
        if x["caso"] == "bicicleta" and i % 2 == 0:
            add(c, "raz1", "", ["texto", "finalidad", "otra"][(i // 2) % 3], "", 1)
    return rows


def finales(filas):
    """(cod, campo) -> lista de filas finales (pasada más alta; última por clave)."""
    g = collections.defaultdict(list)
    for r in filas:
        if r["valor"] != "":
            g[(r["cod"], r["campo"])].append(r)
    out = {}
    for k, rs in g.items():
        top = max(int(r["pasada"]) for r in rs)
        por = {}
        for r in rs:
            if int(r["pasada"]) == top:
                por[r["clave"]] = r   # la última pisa
        out[k] = list(por.values())
    return out


# ------------------------------------------------------------------ campos
def fld(id, et, tipo="op", ops=None, loc=None, locSi=None, cond=None):
    d = dict(id=id, et=et, tipo=tipo, ops=ops or [], loc=loc, grupo=None)
    if locSi: d["locSi"] = locSi
    if cond: d["cond"] = cond
    return d


def ref_txt(ref):
    return ref.replace(":", " párr. ") if ref else "sin párrafo"


def nota_exc(filas):
    reales = [r for r in filas if r["valor"] != "(ninguna)"]
    if not reales:
        return "<b>TJS no cargó ninguna excepción en esta pantalla.</b>", 0
    li = []
    for r in sorted(reales, key=lambda r: int(r["clave"]) if str(r["clave"]).isdigit() else 0):
        nombre, _, trato = r["valor"].rpartition("|")
        li.append("<li>%s: %s (%s)</li>" % (html.escape(nombre), html.escape(TRATO_NOM.get(trato, trato)), html.escape(ref_txt(r["ubicacion"]))))
    return "<b>Excepciones que TJS ya cargó en esta pantalla (%d)</b><ul>%s</ul>" % (len(reales), "".join(li)), len(reales)


def ap(pasada, titulo, cuerpo):
    return dict(id="AP%d" % pasada, cod="", pasada=pasada, tipo="apertura", caso="homicidio", secs=[], campos=[], jlr=False, pregs={},
                html='<div class="ap"><h2>%s</h2>%s</div>' % (titulo, cuerpo))


def ol(xs):
    return "<ol>" + "".join("<li>%s</li>" % x for x in xs) + "</ol>"


DUDA = ("<h4>Duda</h4><p>Arriba de cada pantalla hay una pregunta obligatoria: si dudaste en algún campo de esa respuesta. No se pasa a la siguiente sin contestarla. "
        "Si contestás que sí, se agrega una fila por cada duda: el campo, la razón y una nota. La nota es obligatoria con las razones 1 y 6.</p>"
        + ol(["Vacilo entre dos opciones (escribí cuáles)", "La respuesta dice dos cosas distintas", "Ninguna opción se ajusta", "La regla no cubre el caso",
              "No encuentro un solo párrafo que lo justifique", "Otra (escribila)"]))


def main():
    D = leer_datos(SRC)
    items = [x for x in D["items"] if x.get("tipo") != "apertura"]
    args = [x for x in sys.argv[1:] if not x.startswith('--')]
    filas = inventar(items) if PRUEBA else list(csv.DictReader(open(args[0], encoding='utf-8-sig')))
    fin = finales(filas)

    rps, exps = [], []
    n_conc = n_nota = n_exc = n_raz = 0
    cnt = collections.Counter()
    for x in items:
        c = x["cod"]
        if x["tipo"] == "rp":
            y = dict(x); y["jlr"] = False
            campos, pre = [], {}
            e = fin.get((c, "err"), [])
            if e and e[0]["valor"] == "concede":
                campos.append(fld("err", "Repregunta, error en la primera respuesta", ops=OP_ERR, loc="RP", locSi=["concede"]))
                pre["err"] = {"v": "concede"}
                if e[0]["ubicacion"]: pre["err"]["loc"] = {"": e[0]["ubicacion"]}
                n_conc += 1
            campos.append(fld("atr", "Atribuye que los dos problemas no lo detuvieran a (se marcan todas las que da la respuesta)", tipo="multi", ops=OP_ATR, loc="RP"))
            a = fin.get((c, "atr"), [])
            if a:
                v, loc, txt = [], {}, ""
                for r in a:
                    v.append(r["clave"])
                    if r["ubicacion"]: loc[r["clave"]] = r["ubicacion"]
                    if r["clave"] == "otra": txt = r["valor"].partition("|")[2]
                pre["atr"] = {"v": v, "loc": loc}
                if "otra" in v: pre["atr"]["txt"] = txt
                cnt["atr_opciones"] += len(v)
            campos.append(fld("nosabe", "Dice que no puede saber qué hizo o que lo reconstruye", ops=SN_NOSABE, loc="RP", locSi=["si"]))
            ns = fin.get((c, "nosabe"), [])
            if ns:
                pre["nosabe"] = {"v": ns[0]["valor"]}
                if ns[0]["ubicacion"]: pre["nosabe"]["loc"] = {"": ns[0]["ubicacion"]}
                if ns[0]["valor"] == "si": cnt["nosabe_si"] += 1
            y["campos"], y["pre"] = campos, pre
            rps.append(y)
        elif x["tipo"] == "exp":
            y = dict(x); y["jlr"] = False
            y["secs"] = [s for s in x["secs"] if s["turno"] == "R1"]
            y["pregs"] = {}
            campos = [fld("excgen", "Fórmula general sobre una clase de excepciones que no esté cargada", ops=SN_EXCGEN, loc="R1", locSi=["si"]),
                      fld("exc", "Excepciones nuevas (solo las que TJS no cargó)", tipo="exc", loc="R1", cond=["excgen", "si"])]
            pre = {}
            rz = fin.get((c, "raz1"), [])
            if x["caso"] == "bicicleta" and rz:
                campos.append(fld("raz1", "Bicicleta: razón", ops=OP_RAZ))
                pre["raz1"] = {"v": rz[0]["valor"]}
                n_raz += 1
            nota, k = nota_exc(fin.get((c, "exc"), []))
            y["nota"] = nota
            if k: n_nota += 1
            n_exc += k
            y["campos"], y["pre"] = campos, pre
            exps.append(y)
    assert len(rps) == 36 and len(exps) == 36, (len(rps), len(exps))
    assert all(len(y["secs"]) == 1 for y in exps), "turno R1 no encontrado"

    A_RP = ("<p>Revisión del 9 de noviembre, con las reglas de lectura de ese día. Las %d repreguntas. Se revisan tres campos y vienen cargadas las marcas vigentes de TJS: se cambian solo si no coinciden con la respuesta.</p>"
            "<h4>Reglas</h4>" % len(rps) + ol([
                "<b>Error en la primera respuesta.</b> Solo aparece donde la marca es concede. Concede si la respuesta usa una fórmula de concesión referida a su primera respuesta (\"tenés razón\", \"me equivoqué\", \"omití excepciones\"), aunque no la desarrolle y aunque después mantenga o reformule la decisión. Si la fórmula se limita a un punto teórico y la respuesta niega que su primera respuesta dependiera de él, es sostiene. La distinción entre reinterpreta y sostiene no cambia. Con concede hay que hacer clic en el párrafo que lo justifica.",
                "<b>Atribución.</b> Se marcan todas las atribuciones que da la respuesta, no solo la principal. Ninguna se marca solo si la respuesta no da ninguna de las explicaciones de la lista ni otra.",
                "<b>No puede saber qué hizo.</b> Sí si la respuesta dice expresamente que no puede acceder a cómo llegó a la conclusión, o que lo que ofrece es una reconstrucción posterior. No si explica cómo llegó sin decir nada de esto: una explicación en primera persona (\"lo que hice fue…\") no basta. Con sí hay que hacer clic en el párrafo que lo justifica."]) +
            "<p>En los demás valores de error y de \"no puede saber\", la ubicación es optativa.</p>" + DUDA)
    A_EXP = ("<p>Revisión del 9 de noviembre, con las reglas de lectura de ese día. Las %d primeras respuestas; se muestra solo la primera respuesta de cada expediente. Vienen cargadas las marcas vigentes de TJS en la nota de excepciones y, en la bicicleta, en la razón.</p>" % len(exps) +
             "<h4>Reglas</h4>" + ol([
                 "<b>Excepciones.</b> Una fórmula general sobre una clase de excepciones (\"no concurren causas de justificación\", \"no se advierten causas de inculpabilidad\") cuenta como mención: se carga una excepción con el nombre de esa clase y el valor que corresponda según la guía (por lo común, estipula). \"No hay excepciones\" se marca solo si la respuesta no se refiere a ningún factor que desplace la norma que aplica, ni siquiera con una fórmula general.",
                 "<b>Qué se marca acá.</b> Arriba de los campos, una nota muestra las excepciones que TJS ya cargó (nombre, valor y párrafo). La pregunta es si hay una fórmula general sobre una clase de excepciones que no esté cargada. Si hay, se hace clic en el párrafo y se carga solo la excepción nueva.",
                 "<b>Razón en la bicicleta.</b> Texto o sentido corriente si la razón es lo que dice la norma o el significado corriente o legal de \"vehículo\". Finalidad si es para qué existe la norma, aunque también cite el texto. Si da las dos en pie de igualdad, se marca la que presenta como decisiva; si no presenta ninguna, la que aparece primero y se registra una duda."]) +
             DUDA)

    out = [ap(2, "Repreguntas (%d pantallas)" % len(rps), A_RP)] + rps + [ap(1, "Primeras respuestas (%d pantallas)" % len(exps), A_EXP)] + exps
    datos = dict(clas="TJS", version="261109b" + ("p" if PRUEBA else ""), semilla=D.get("semilla"), consulta=D["consulta"], items=out, dudaArriba=True)
    motor = open(os.path.join(BASE, "formulario-motor.html"), encoding="utf-8").read()
    js = json.dumps(datos, ensure_ascii=False).replace("</", "<\\/")
    assert "/*DATOS*/null" in motor
    with open(OUTF, "w", encoding="utf-8") as f:
        f.write(motor.replace("/*DATOS*/null", js))

    cf = collections.Counter(f["id"] for x in out for f in x["campos"])
    print("pantallas: repreguntas %d, primeras respuestas %d (aperturas 2)" % (len(rps), len(exps)))
    print("casillas por campo:", dict(sorted(cf.items())), "total", sum(cf.values()))
    print("err = concede: %d; raz1: %d; nosabe = si: %d; opciones de atr precargadas: %d" % (n_conc, n_raz, cnt["nosabe_si"], cnt["atr_opciones"]))
    print("pantallas con nota de excepciones: %d de %d (excepciones en las notas: %d)" % (n_nota, len(exps), n_exc))
    print("salida:", OUTF)


if __name__ == "__main__":
    main()
