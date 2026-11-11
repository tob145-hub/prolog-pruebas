#!/usr/bin/env python3
"""Clasificación común y cifras finales tras el paso 2 (2026-11-09).
Lee: los CSV de las dos clasificaciones (paso 1 y revisión), el documento del paso 2 en .md (entradas) y el .docx con las
respuestas de JLR. No abre CLAVE*, controles, numeración ni transcripciones.
Salidas: Pruebas/Formulario/clasificacion-comun-261109.csv y un resumen por pantalla (stdout).
Uso: python3 -I informe-paso2.py RUTA_DOCX_CON_RESPUESTAS
"""
import csv, os, re, sys, random, subprocess, collections, importlib.util

BASE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(BASE)
DOCX = sys.argv[1]
sys.argv = sys.argv[:1]


def cargar(nombre, ruta):
    sp = importlib.util.spec_from_file_location(nombre, ruta)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


AC = cargar("ac", os.path.join(BASE, "acuerdo-paso1.py"))
J0 = AC.load(os.path.join(BASE, "Lectura", "clasificacion-JLR-261107.csv"))
T0 = AC.load(os.path.expanduser("~/Desktop/SRC/clasificacion-TJS-261107.csv"))
J = AC.load(os.path.join(BASE, "Lectura", "clasificacion-JLR-ajuste-261109.csv"))
T = AC.load(os.path.join(BASE, "Formulario", "clasificacion-TJS-revisada2-261109.csv"))
MD = os.path.join(PROJ, "Versiones", "Paso 2 - discrepancias.261109.md")
OUT = os.path.join(BASE, "Formulario", "clasificacion-comun-261109.csv")
SEMILLA = 20261109
NOM = {"Verdad": "verd", "Derrotabilidad": "derr", "Conclusión": "conc", "Error en la primera respuesta": "err",
       "No puede saber qué hizo": "nosabe", "Atribución": "atr", "Excepciones": "exc",
       "Razón en el caso de la bicicleta": "raz1", "Hechos": "hechos", "Inferencia": "inf", "Vehículo": "veh1"}


def entradas():
    campo, res = None, {}
    for ln in open(MD, encoding="utf-8"):
        m = re.match(r"## (.+)", ln.strip())
        if m and m.group(1) in NOM:
            campo = NOM[m.group(1)]
        m = re.match(r"### Entrada (\d+): pantalla (\w+)", ln)
        if m:
            res[int(m.group(1))] = {"campo": campo, "id": m.group(2), "cod": m.group(2)[1:]}
        m = re.match(r"- Marca del primer autor: (.*)", ln)
        if m and res:
            res[max(res)]["tjs"] = m.group(1)
        m = re.match(r"- Marca del segundo autor: (.*)", ln)
        if m and res:
            res[max(res)]["jlr"] = m.group(1)
    return res


def respuestas():
    txt = subprocess.run(["pandoc", DOCX, "-t", "plain", "--wrap=none"], capture_output=True, text=True).stdout
    out, n = {}, None
    for ln in txt.splitlines():
        m = re.match(r"Entrada (\d+):", ln)
        if m:
            n = int(m.group(1))
        m = re.match(r"- Respuesta del segundo autor:.*\[(.*)\]\s*$", ln)
        if m and n:
            out[n] = m.group(1).strip()
    return out


def clase(r):
    r = r.strip().lower()
    if r.startswith("a"):
        return "A"
    if r.startswith("m"):
        return "M"
    if r.startswith("o"):
        return "O"
    return "?"


def valor(rows, cod, campo):
    f = AC.finales(rows)
    r = f.get((cod, campo))
    return r["valor"].strip() if r else None


def conjunto_atr(rows, cod):
    rs = [r for r in rows if r["cod"] == cod and r["campo"] == "atr" and r["valor"].strip()]
    if not rs:
        return None
    t = max(int(r["pasada"]) for r in rs)
    return frozenset(r["valor"].split("|")[0].strip() for r in rs if int(r["pasada"]) == t)


def presencia_exc(rows, cod):
    rs = [r for r in rows if r["cod"] == cod and r["campo"] == "exc" and r["valor"].strip()]
    if not rs:
        return None
    return any(r["valor"].strip() != "(ninguna)" for r in rs)


def alfa(pares):
    """Alfa de Krippendorff nominal, dos codificadores, sin faltantes. pares: lista de (a, b)."""
    n = 2 * len(pares)
    c = collections.Counter()
    for a, b in pares:
        c[a] += 1
        c[b] += 1
    do = sum(1 for a, b in pares if a != b) * 2
    de = sum(c[x] * c[y] for x in c for y in c if x != y)
    if de == 0:
        return None
    return 1 - (do / n) / (de / (n * (n - 1)))


def alfa_ic(unidades):
    """unidades: lista de listas de pares (agrupadas por pantalla). IC percentil 95 por remuestreo de pantallas."""
    pares = [p for u in unidades for p in u]
    a = alfa(pares)
    rnd = random.Random(SEMILLA)
    v = []
    for _ in range(2000):
        s = [rnd.choice(unidades) for _ in unidades]
        x = alfa([p for u in s for p in u])
        if x is not None:
            v.append(x)
    v.sort()
    ic = (v[int(0.025 * len(v))], v[int(0.975 * len(v)) - 1]) if len(v) > 50 else None
    return a, ic, len(v)


def f(x):
    return "no definido" if x is None else ("%.2f" % x).replace(".", ",")


def main():
    E, R = entradas(), respuestas()
    assert set(E) == set(R) == set(range(1, 27)), (sorted(E), sorted(R))
    cls = {n: clase(R[n]) for n in E}
    for n in E:
        E[n]["resp"] = R[n]
        E[n]["clase"] = cls[n]
    print("Respuestas:", collections.Counter(cls.values()))
    print("Dudosas:", [(n, E[n]["campo"], E[n]["id"], R[n]) for n in E if cls[n] != "A"])

    comunes = sorted({r["cod"] for r in J} & {r["cod"] for r in T})
    ids = {r["cod"]: r["id"] for r in T}
    ent_por = {(E[n]["cod"], E[n]["campo"]): n for n in E}

    # --- clasificación común (CSV por pantalla y campo) ---
    filas = []
    campos = ["verd", "derr", "conc", "err", "nosabe", "atr", "exc", "raz1", "hechos", "inf", "veh1"]
    for cod in comunes:
        for c in campos:
            if c == "atr":
                sj, st = conjunto_atr(J, cod), conjunto_atr(T, cod)
                if st is None or sj is None:
                    continue
                vt, vj = "; ".join(sorted(st)), "; ".join(sorted(sj))
                igual = (sj == st)
            elif c == "exc":
                pj, pt = presencia_exc(J, cod), presencia_exc(T, cod)
                if pj is None or pt is None:
                    continue
                vt, vj = ("con excepciones" if pt else "ninguna"), ("con excepciones" if pj else "ninguna")
                igual = (pj == pt)
            else:
                vt, vj = valor(T, cod, c), valor(J, cod, c)
                if vt is None or vj is None:
                    continue
                igual = (vt == vj)
            if igual:
                estado, comun = "acuerdo", vt
            else:
                n = ent_por.get((cod, c))
                if n is None:
                    estado, comun = "sin entrada", ""
                elif cls[n] == "A":
                    estado, comun = "aceptada", vt
                else:
                    estado, comun = "dudosa", ""
            filas.append({"id": ids[cod], "cod": cod, "campo": c, "marca_TJS": vt, "marca_JLR": vj,
                          "estado": estado, "valor_comun": comun})
    with open(OUT, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)
    print("CSV:", OUT, len(filas), "filas")
    print("Sin entrada (desacuerdo que no llegó al paso 2):", [x for x in filas if x["estado"] == "sin entrada"])

    # --- tabla por campo ---
    L = ["| Campo | Pantallas | Acuerdo tras la revisión | Aceptadas en paso 2 | Dudosas | Coincidencia tras el paso 2 |", "|---|---:|---:|---:|---:|---:|"]
    tot = collections.Counter()
    for c in campos:
        fs = [x for x in filas if x["campo"] == c]
        if not fs:
            continue
        n = len(fs)
        a = sum(1 for x in fs if x["estado"] == "acuerdo")
        ac = sum(1 for x in fs if x["estado"] == "aceptada")
        du = sum(1 for x in fs if x["estado"] == "dudosa")
        tot.update({"n": n, "a": a, "ac": ac, "du": du})
        L.append("| %s | %d | %d | %d | %d | %d de %d (%s %%) |" % (c, n, a, ac, du, a + ac, n, AC.pct(a + ac, n)))
    L.append("| **Total** | **%d** | **%d** | **%d** | **%d** | **%d de %d (%s %%)** |" % (
        tot["n"], tot["a"], tot["ac"], tot["du"], tot["a"] + tot["ac"], tot["n"], AC.pct(tot["a"] + tot["ac"], tot["n"])))
    print("\n".join(L))

    # --- alfas sobre las marcas tras la revisión (y paso 1 para comparar) ---
    def unidades(campo, JR, TR):
        us = []
        for cod in comunes:
            if campo == "atr":
                sj, st = conjunto_atr(JR, cod), conjunto_atr(TR, cod)
                if sj is None or st is None:
                    continue
                cats = sorted(CATS)
                us.append([(c in st, c in sj) for c in cats])
            elif campo == "exc":
                pj, pt = presencia_exc(JR, cod), presencia_exc(TR, cod)
                if pj is None or pt is None:
                    continue
                us.append([(pt, pj)])
            else:
                vt, vj = valor(TR, cod, campo), valor(JR, cod, campo)
                if vt is None or vj is None:
                    continue
                us.append([(vt, vj)])
        return us

    CATS = {"cierre", "formato", "teoria"}  # las categorías fijas con ejemplo en la guía; "otra" se informa aparte
    print("Categorías de atr:", sorted(CATS))
    print("\n| Campo | Unidades | Alfa paso 1 | Alfa tras la revisión (IC 95 %) |\n|---|---:|---:|---:|")
    for c in ["verd", "derr", "conc", "err", "nosabe", "atr", "exc"]:
        u0, u1 = unidades(c, J0, T0), unidades(c, J, T)
        a0 = alfa([p for u in u0 for p in u])
        a1, ic, nb = alfa_ic(u1)
        print("| %s | %d | %s | %s %s |" % (c, len(u1), f(a0), f(a1), ("[%s; %s]" % (f(ic[0]), f(ic[1]))) if ic else "(sin IC: varianza nula en las muestras)"))

    # --- atribución: acuerdo por categoría (principal) y cota ---
    ok = n = 0
    cota_ok = cota_n = 0
    for cod in comunes:
        sj, st = conjunto_atr(J, cod), conjunto_atr(T, cod)
        if sj is None or st is None:
            continue
        for c in CATS:
            n += 1
            ok += ((c in sj) == (c in st))
        cota_n += 1
        cota_ok += bool(sj & st)
    print("\natr por categoría tras la revisión: %d de %d (%s %%); cota alguna coincide: %d de %d" % (ok, n, AC.pct(ok, n), cota_ok, cota_n))
    # tras el paso 2: atr aceptadas
    acept = [x for x in filas if x["campo"] == "atr" and x["estado"] == "aceptada"]
    dud = [x for x in filas if x["campo"] == "atr" and x["estado"] == "dudosa"]
    print("atr con 'otra' en TJS tras la revisión:", sum(1 for cod in comunes if "otra" in (conjunto_atr(T, cod) or ())))
    print("atr: pantallas aceptadas %d, dudosas %d" % (len(acept), len(dud)))


if __name__ == "__main__":
    main()
