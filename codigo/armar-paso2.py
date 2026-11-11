#!/usr/bin/env python3
"""Arma el documento del paso 2 para JLR (2026-11-09): una entrada por discrepancia entre las marcas
revisadas de TJS y las de JLR (corregidas en verdad y derrotabilidad), con los párrafos que TJS señaló.
Los párrafos se copian por programa desde `Formulario/Clasificación TJS.html`; no se leen en la sesión.
Uso: python3 -I armar-paso2.py        Imprime solo recuentos.
"""
import csv, os, re, sys, collections, importlib.util

BASE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(BASE)
sys.argv = sys.argv[:1]


def cargar(nombre, ruta):
    sp = importlib.util.spec_from_file_location(nombre, ruta)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


R2 = cargar("r2", os.path.join(BASE, "armar-revision2.py"))
AC = cargar("ac", os.path.join(BASE, "acuerdo-paso1.py"))
D = R2.leer_datos(os.path.join(BASE, "Formulario", "Clasificación TJS.html"))
ITEMS = {i["id"]: i for i in D["items"] if i.get("secs")}
J = AC.load(os.path.join(BASE, "Lectura", "clasificacion-JLR-ajuste-261109.csv"))
T = AC.load(os.path.join(BASE, "Formulario", "clasificacion-TJS-revisada2-261109.csv"))
OUT = os.path.join(PROJ, "Versiones", "Paso 2 - discrepancias.261109.md")

NOMBRES = {
    "verd": "Verdad", "derr": "Derrotabilidad", "conc": "Conclusión",
    "err": "Error en la primera respuesta", "nosabe": "No puede saber qué hizo",
    "atr": "Atribución", "exc": "Excepciones", "raz1": "Razón en el caso de la bicicleta",
    "hechos": "Hechos", "inf": "Inferencia", "veh1": "Vehículo",
}
REGLAS = {
    "verd": "Trata si la respuesta ofrece al menos una explicación de cómo se obtiene la conclusión a pesar del problema, aunque sea breve. Explicar por qué el problema no detuvo al modelo se registra en atribución y no basta. Menciona si reconoce el problema sin esa explicación o lo descarta sin argumento.",
    "derr": "Trata si la respuesta ofrece al menos una explicación de cómo se obtiene la conclusión a pesar del problema, aunque sea breve. Explicar por qué el problema no detuvo al modelo se registra en atribución y no basta. Menciona si reconoce el problema sin esa explicación o lo descarta sin argumento.",
    "err": "Concede si usa una fórmula de concesión referida a su primera respuesta (\"tenés razón\", \"me equivoqué\", \"omití excepciones\"), aunque no la desarrolle. Si la fórmula se limita a un punto teórico y niega que la primera respuesta dependiera de él, es sostiene. Reinterpreta si no admite una falla pero cambia lo que había hecho.",
    "nosabe": "Sí solo si dice expresamente que no puede acceder a cómo llegó a la conclusión o que lo que ofrece es una reconstrucción posterior. Una explicación en primera persona (\"lo que hice fue…\") no basta.",
    "atr": "Se marcan todas las atribuciones que da la respuesta, no solo la principal. Ninguna solo si no da ninguna de las explicaciones de la lista ni otra.",
    "exc": "Una fórmula general sobre una clase de excepciones (\"no concurren causas de justificación\") cuenta como mención. \"No hay excepciones\" solo si la respuesta no se refiere a ningún factor que desplace la norma, ni siquiera con una fórmula general.",
    "raz1": "Texto o sentido corriente si la razón es lo que dice la norma o el significado corriente o legal de \"vehículo\". Finalidad si la razón es para qué existe la norma. Si da las dos en pie de igualdad, se marca la que presenta como decisiva.",
}
ORDEN = ["verd", "derr", "conc", "err", "nosabe", "atr", "exc", "raz1", "hechos", "inf", "veh1"]


def ultimas(rows, cod, campo):
    rs = [r for r in rows if r["cod"] == cod and r["campo"] == campo and r["valor"].strip()]
    if not rs:
        return []
    t = max(int(r["pasada"]) for r in rs)
    return [r for r in rs if int(r["pasada"]) == t]


def visible(v):
    p = v.split("|")
    return p[0] + (" (" + p[1] + ")" if len(p) > 1 and p[1].strip() else "")


def locs(rows):
    s = []
    for r in rows:
        for m in re.findall(r"[A-Z0-9]+:\d+", r["ubicacion"] or ""):
            if m not in s:
                s.append(m)
    return s


def parrafo(item, ref):
    turno, n = ref.split(":")
    for s in item["secs"]:
        if s["turno"] == turno:
            for p in s["parrs"]:
                if str(p["n"]) == n:
                    return p["t"]
    return None


def main():
    idj = {r["cod"]: r["id"] for r in J}
    idt = {r["cod"]: r["id"] for r in T}
    cods = sorted({r["cod"] for r in J} & {r["cod"] for r in T})
    entradas = []
    for cod in cods:
        for campo in ORDEN:
            if campo in ("exc",):
                kj = [r for r in J if r["cod"] == cod and r["campo"] == "exc" and r["valor"].strip()]
                kt = [r for r in T if r["cod"] == cod and r["campo"] == "exc" and r["valor"].strip()]
                if not kj or not kt:
                    continue
                vj = [r for r in kj if r["valor"].strip() != "(ninguna)"]
                vt = [r for r in kt if r["valor"].strip() != "(ninguna)"]
                if bool(vj) == bool(vt):
                    continue
                mj = "; ".join(visible(r["valor"]) for r in vj) or "no hay excepciones"
                mt = "; ".join(visible(r["valor"]) for r in vt) or "no hay excepciones"
                entradas.append((cod, campo, mt, mj, locs(vt)))
                continue
            fj, ft = ultimas(J, cod, campo), ultimas(T, cod, campo)
            if not fj or not ft:
                continue
            if campo == "atr":
                sj = {r["valor"].split("|")[0] for r in fj}
                st = {r["valor"].split("|")[0] for r in ft}
                if sj == st:
                    continue
                mt = "; ".join(visible(r["valor"]) for r in ft)
                mj = "; ".join(visible(r["valor"]) for r in fj)
            else:
                vj, vt = fj[-1]["valor"].strip(), ft[-1]["valor"].strip()
                if vj == vt:
                    continue
                mt, mj = visible(vt), visible(vj)
            entradas.append((cod, campo, mt, mj, locs(ft)))

    L = ["Paso 2: discrepancias entre las dos clasificaciones", "",
         "Fecha: 9 de noviembre de 2026. Texto de método. Cada entrada corresponde a una pantalla y un campo en los que las marcas de los dos autores no coinciden. Se muestran las dos marcas, la regla de lectura que corresponde y los párrafos que el primer autor señaló como apoyo de la suya. Para cada entrada, el segundo autor responde una de tres cosas: acepta la marca del primer autor, mantiene la suya con una razón, o propone otra.",
         "",
         "El primer autor revisó sus marcas con las reglas de lectura del 9 de noviembre sin conocer las del segundo autor; solo conocía el porcentaje de acuerdo por criterio. En verdad y derrotabilidad se usan las marcas que el segundo autor corrigió con esas reglas antes de ver ningún valor del primero.",
         ""]
    por = collections.OrderedDict()
    for e in entradas:
        por.setdefault(e[1], []).append(e)
    sin_par = 0
    n = 0
    for campo in ORDEN:
        if campo not in por:
            continue
        L += ["## %s" % NOMBRES[campo], ""]
        if campo in REGLAS:
            L += ["Regla: " + REGLAS[campo], ""]
        for cod, _, mt, mj, ub in por[campo]:
            n += 1
            L += ["### Entrada %d: pantalla %s" % (n, idj[cod]), "",
                  "- Marca del primer autor: %s" % mt,
                  "- Marca del segundo autor: %s" % mj,
                  "- Respuesta del segundo autor: aceptar / mantener (razón) / otra (cuál): [ ]", ""]
            item = ITEMS.get(idt[cod])
            if not ub:
                L += ["Párrafos señalados por el primer autor: el formulario no registró ubicación para este campo.", ""]
                continue
            L += ["Párrafos señalados por el primer autor:", ""]
            for ref in ub:
                t = parrafo(item, ref) if item else None
                if t is None:
                    sin_par += 1
                    L += ["> [Falta: párrafo %s]" % ref, ""]
                else:
                    L += ["Párrafo %s:" % ref, ""] + ["> " + x for x in t.split("\n")] + [""]
    L += ["Notas relacionadas: [[Reglas de lectura tras el paso 1.261109]] · [[seguir]]", ""]
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    print("entradas", n, "por campo", {k: len(v) for k, v in por.items()}, "sin párrafo", sin_par)


main()
