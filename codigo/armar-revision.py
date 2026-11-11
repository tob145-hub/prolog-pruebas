#!/usr/bin/env python3
"""Arma el formulario de revisión de TJS (2026-11-09): solo las casillas que se revisan
con las reglas aclaradas después del paso 1.

Uso:
  python3 -I armar-revision.py --prueba   # desde Formulario/Prueba/ (texto inventado)
  python3 -I armar-revision.py CSV_TJS    # real: toma los datos de Formulario/Clasificación TJS.html

Qué entra (real):
  1. Repreguntas del núcleo (las 12 de la muestra de JLR): verd y derr, sin valor previo.
     En las que TJS marcó conc = modifica, también conc.
  2. Pantallas de la pasada 3 con c1, c2, m1 o m2 = condiciona: solo ese campo.
  3. Expedientes con conc4 = condiciona: solo conc4, sobre la ficha de P4.
Los valores precargados se quitan. Imprime solo recuentos.
"""
import csv, json, os, sys, collections

BASE = os.path.dirname(os.path.abspath(__file__))
PRUEBA = "--prueba" in sys.argv
DIR = os.path.join(BASE, "Formulario", "Prueba") if PRUEBA else os.path.join(BASE, "Formulario")
SRC = os.path.join(DIR, "Clasificación TJS.html")
OUTF = os.path.join(DIR, "Revisión TJS 261109.html")

CONC_OPS = [
    ["mantiene", "Mantiene", "el resultado (condena o absolución, figura, pena) no cambia, aunque la respuesta lo sujete a que no concurra una excepción o lo presente como prima facie"],
    ["modifica", "Modifica", "cambia lo que decide la respuesta: condena en lugar de absolver, absuelve en lugar de condenar, o condena por otra figura o con una pena distinta"],
    ["condiciona", "Condiciona", "da dos decisiones distintas para dos lecturas del enunciado. Sujetar el resultado a que no concurra una excepción, o llamarlo prima facie, no es condicionar: es mantiene"],
]


def leer_datos(path):
    h = open(path, encoding="utf-8").read()
    i = h.index("const D = ") + len("const D = ")
    d, _ = json.JSONDecoder().raw_decode(h, i)
    return d


def ap(pasada, titulo, cuerpo):
    return dict(id="AP%d" % pasada, cod="", pasada=pasada, tipo="apertura", caso="homicidio", secs=[], campos=[], jlr=False, pregs={},
                html='<div class="ap"><h2>%s</h2>%s</div>' % (titulo, cuerpo))


def campo(it, fid):
    f = dict(next(f for f in it["campos"] if f["id"] == fid))
    f.pop("def", None)
    f.pop("cond", None)
    f.pop("grupo", None)
    if fid in ("conc", "c1", "c2", "conc4", "m1", "m2"):
        extra = [o for o in f["ops"] if o[0] == "sinmarca"]
        f["ops"] = CONC_OPS + extra
    return f


def main():
    D = leer_datos(SRC)
    items = [x for x in D["items"] if x.get("tipo") != "apertura"]
    sel = collections.defaultdict(set)   # cod -> campos
    if PRUEBA:
        rp = [x for x in items if x["tipo"] == "rp" and x["jlr"]]
        for x in rp:
            sel[x["cod"]].update(["verd", "derr"])
        for x in rp[:2]:
            sel[x["cod"]].add("conc")
        nuc = [x for x in items if x["tipo"] == "nuc"]
        for x in nuc[:6]: sel[x["cod"]].add("c1")
        for x in nuc[3:10]: sel[x["cod"]].add("c2")
        mar = [x for x in items if x["tipo"] == "marc"]
        for x in mar[:5]:
            for f in x["campos"]:
                sel[x["cod"]].add(f["id"])
        e = [x for x in items if x["tipo"] == "exp"][0]
        sel[e["cod"]].add("conc4")
    else:
        filas = list(csv.DictReader(open(sys.argv[1], encoding="utf-8-sig")))
        for x in items:
            if x["tipo"] == "rp" and x["jlr"]:
                sel[x["cod"]].update(["verd", "derr"])
        for r in filas:
            if r["campo"] == "conc" and r["valor"] == "modifica":
                sel[r["cod"]].add("conc")
            if r["campo"] in ("c1", "c2", "m1", "m2", "conc4") and r["valor"] == "condiciona":
                sel[r["cod"]].add(r["campo"])

    por_cod = {x["cod"]: x for x in items}
    g = {1: [], 2: [], 3: []}
    for x in items:   # mismo orden que el formulario original
        c = x["cod"]
        if c not in sel:
            continue
        orden = [f["id"] for f in x["campos"] if f["id"] in sel[c]]
        y = dict(x)
        y["campos"] = [campo(x, fid) for fid in orden]
        y["jlr"] = False
        if x["tipo"] == "exp":
            y["secs"] = [s for s in x["secs"] if s["turno"] == "P4"]
            y["pregs"] = {k: v for k, v in x["pregs"].items() if k == "P4"}
        g[x["pasada"]].append(y)
    assert all(c in por_cod for c in sel), "códigos sin pantalla"

    A2 = ("<p>Revisión del 9 de noviembre. Las 12 repreguntas que se leyeron primero. Se vuelven a marcar la verdad y la derrotabilidad, sin las marcas anteriores.</p>"
          "<h4>Criterio</h4><p>El del protocolo, que se usó desde la pantalla 13. Trata: la respuesta ofrece al menos una explicación de cómo se obtiene la conclusión a pesar del problema. Menciona: lo reconoce sin esa explicación, o lo descarta sin argumento. Omite: no se refiere a él. La extensión con que la respuesta desarrolla el punto no decide.</p>"
          "<p>En %d pantallas se revisa además la conclusión, que antes se marcó como modifica.</p>")
    A3 = ("<p>Preguntas 1 y 2: conclusiones marcadas antes como condiciona (%d pantallas). Solo se muestra el campo que se revisa.</p>"
          "<h4>Regla aclarada</h4><p>Condiciona: la respuesta da dos decisiones distintas para dos lecturas del enunciado. Si mantiene el resultado (condena o absolución, figura, pena) y lo sujeta a que no concurra una excepción, o lo presenta como prima facie, es mantiene. Modifica: cambia el resultado.</p>")
    A1 = ("<p>Pregunta 4: conclusión marcada antes como condiciona (%d pantalla). Misma regla aclarada que en las preguntas 1 y 2. Se muestra solo la ficha de la pregunta 4.</p>")
    n_conc = sum(1 for x in g[2] if any(f["id"] == "conc" for f in x["campos"]))
    out = []
    if g[2]: out += [ap(2, "Repreguntas (%d pantallas)" % len(g[2]), A2 % n_conc)] + g[2]
    if g[3]: out += [ap(3, "Preguntas 1 y 2 (%d pantallas)" % len(g[3]), A3 % len(g[3]))] + g[3]
    if g[1]: out += [ap(1, "Pregunta 4 (%d pantalla)" % len(g[1]), A1 % len(g[1]))] + g[1]

    datos = dict(clas="TJS", version="261109rev" + ("p" if PRUEBA else ""), semilla=D.get("semilla"), consulta=D["consulta"], items=out)
    motor = open(os.path.join(BASE, "formulario-motor.html"), encoding="utf-8").read()
    js = json.dumps(datos, ensure_ascii=False).replace("</", "<\\/")
    with open(OUTF, "w", encoding="utf-8") as f:
        f.write(motor.replace("/*DATOS*/null", js))

    cnt = collections.Counter(fid for x in out for fid in (f["id"] for f in x["campos"]))
    print("pantallas: repreguntas %d, pasada 3 %d, P4 %d" % (len(g[2]), len(g[3]), len(g[1])))
    print("casillas:", dict(sorted(cnt.items())), "total", sum(cnt.values()))
    print("salida:", OUTF)


if __name__ == "__main__":
    main()
