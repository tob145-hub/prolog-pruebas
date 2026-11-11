#!/usr/bin/env python3
"""Arma la tercera revisión del formulario de TJS (2026-11-10): las pantallas de la pasada 3 (tipo "nuc", respuesta a la pregunta 1)
cuyo valor final de e1 (error en la primera respuesta) es "concede" (deben ser 9), con duda obligatoria arriba de cada pantalla.

Uso:
  python3 -I armar-revision3.py --prueba   # desde Formulario/Prueba/ (texto inventado; marcas inventadas)
  python3 -I armar-revision3.py            # real: Formulario/clasificacion-TJS-revisada2-261109.csv + datos de Formulario/Clasificación TJS.html
  python3 -I armar-revision3.py CSV        # real, con otro CSV de marcas

Salida: Formulario/Revisión TJS 261110.html (Formulario/Prueba/ con --prueba).

Valor final por (cod, campo): misma regla que armar-revision2 (filas no vacías de la pasada más alta; en empate, la última del archivo).
Si las pantallas que entran no son 9, el script frena e informa el número sin armar nada (en --prueba se inventan 9).

Cada pantalla: las secciones que el original tenía para el tipo "nuc" salvo la ficha de la pregunta 2, que no se muestra porque la revisión no la usa;
queda la respuesta a la pregunta 1 (sección P1). El original no trae la primera respuesta en las pantallas nuc. Un solo campo:
  e1  "Pregunta 1, error en la primera respuesta": concede / sostiene / reinterpreta, precargado "concede" (con la ubicación original si existe).
      Ubicación por clic (P1) obligatoria con "concede", optativa con los otros valores.
Duda por pantalla: igual que armar-revision2 (dudaArriba): fila campo="dudapantalla" (no/si) y, con "si", filas campo="duda" (clave = id del campo,
valor = razón 1 a 6, columna "duda" = nota).
Columnas del CSV de salida (las del motor): clasificador, pasada, id, cod, campo, clave, valor, ubicacion, segundos, duda, estilo, auto.
Pasada: las pantallas llevan pasada = 4 (el motor escribe it.pasada), distinta de la 3 original, para no confundirse con las marcas previas; la apertura es AP4.
La ubicación del csv sale por el botón de guardado de la pantalla final del motor (nombre sugerido clasificacion-TJS-261110.csv).
Imprime solo recuentos.
"""
import csv, json, os, sys, collections, importlib.util

BASE = os.path.dirname(os.path.abspath(__file__))
PRUEBA = "--prueba" in sys.argv
DIR = os.path.join(BASE, "Formulario", "Prueba") if PRUEBA else os.path.join(BASE, "Formulario")
SRC = os.path.join(DIR, "Clasificación TJS.html")
OUTF = os.path.join(DIR, "Revisión TJS 261110.html")
CSV_DEF = os.path.join(BASE, "Formulario", "clasificacion-TJS-revisada2-261109.csv")

_spec = importlib.util.spec_from_file_location("armar_revision2", os.path.join(BASE, "armar-revision2.py"))
AR = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(AR)

REGLA = ("<p>Error en la primera respuesta. Paso 1: ¿la respuesta usa una fórmula de concesión (\"tenés razón\", \"me equivoqué\", \"omití excepciones\", \"no derivé justificadamente\")? "
         "Si no, no es concede. Paso 2: ¿a qué se refiere la fórmula? Si se refiere a lo que hizo en su primera respuesta (la decisión, la derivación, las excepciones que consideró o no), es concede, "
         "aunque no lo desarrolle y aunque mantenga o reformule la decisión. Si se refiere solo a un punto teórico (que las normas no son verdaderas ni falsas, que pueden ser derrotables) y no a su primera respuesta, no es concede. "
         "Si no es concede: reinterpreta si dice que lo que hizo era otra cosa (\"no deduje: hice una prognosis condicional\"); sostiene si defiende lo hecho tal cual. "
         "\"No derivé en sentido lógico estricto\" es concede si lo presenta como una falla y reinterpreta si aclara qué hizo en su lugar. La decisión se registra en conclusión, no aquí.</p>")


def main():
    D = AR.leer_datos(SRC)
    nucs = [x for x in D["items"] if x.get("tipo") == "nuc"]
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    if PRUEBA:
        filas = [dict(clasificador="TJS", pasada="3", id="", cod=x["cod"], campo="e1", clave="", valor=("concede" if i < 9 else ["sostiene", "reinterpreta"][i % 2]),
                      ubicacion=("P1:1" if i % 2 == 0 else "")) for i, x in enumerate(nucs)]
    else:
        filas = list(csv.DictReader(open(args[0] if args else CSV_DEF, encoding="utf-8-sig")))
    fin = AR.finales(filas)

    sel = []
    for x in nucs:
        e = fin.get((x["cod"], "e1"), [])
        if e and e[0]["valor"] == "concede":
            sel.append((x, e[0]))
    if len(sel) != 9:
        print("FRENO: pantallas nuc con e1 = concede: %d (se esperaban 9); nuc totales %d. No se armó nada." % (len(sel), len(nucs)))
        sys.exit(1)

    out = []
    n_loc = 0
    for x, e in sel:
        y = dict(x)
        y["pasada"] = 4
        y["jlr"] = False
        y["secs"] = [s for s in x["secs"] if s["turno"] == "P1"]
        assert len(y["secs"]) == 1, "sección P1 no encontrada"
        y["pregs"] = {"P1": x["pregs"]["P1"]} if "P1" in x.get("pregs", {}) else {}
        y["campos"] = [AR.fld("e1", "Pregunta 1, error en la primera respuesta", ops=AR.OP_ERR, loc="P1", locSi=["concede"])]
        pre = {"e1": {"v": "concede"}}
        if e["ubicacion"]:
            pre["e1"]["loc"] = {"": e["ubicacion"]}
            n_loc += 1
        y["pre"] = pre
        out.append(y)

    cuerpo = ("<p>Revisión del 10 de noviembre. %d respuestas a la pregunta 1 en las que la marca de error en la primera respuesta es concede. Se revisa un solo campo, ya cargado con concede: "
              "se cambia solo si la respuesta no coincide con la regla. Con concede hay que hacer clic en el párrafo que lo justifica; con los otros valores, la ubicación es optativa.</p>"
              "<h4>Regla</h4>" % len(out) + REGLA + AR.DUDA)
    items = [AR.ap(4, "Error en la primera respuesta (%d pantallas)" % len(out), cuerpo)] + out
    datos = dict(clas="TJS", version="261110" + ("p" if PRUEBA else ""), semilla=D.get("semilla"), consulta=D["consulta"], items=items, dudaArriba=True)
    motor = open(os.path.join(BASE, "formulario-motor.html"), encoding="utf-8").read()
    js = json.dumps(datos, ensure_ascii=False).replace("</", "<\\/")
    assert "/*DATOS*/null" in motor
    with open(OUTF, "w", encoding="utf-8") as f:
        f.write(motor.replace("/*DATOS*/null", js))
    print("pantallas: %d (apertura 1); con ubicación precargada: %d" % (len(out), n_loc))
    print("salida:", OUTF)


if __name__ == "__main__":
    main()
