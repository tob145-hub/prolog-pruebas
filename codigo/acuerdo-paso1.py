#!/usr/bin/env python3
# Acuerdo entre clasificadores JLR y TJS (paso 1).
# Solo lee los dos CSV de clasificación. No abre CLAVE*, controles, numeración ni transcripciones.
# Los valores de texto libre (más de TEXTO_LARGO caracteres) no se transcriben: se reemplazan por su longitud.
import csv
import collections
import os

PROJ = os.environ.get("RAIZ_PROYECTO", ".")
JLR = os.environ.get("JLR_CSV", os.path.join(PROJ, "Pruebas", "Lectura", "clasificacion-JLR-261107.csv"))
TJS = os.environ.get("TJS_CSV", "clasificacion-TJS-261107.csv")
OUT = os.environ.get("OUT_MD", os.path.join(PROJ, "Análisis", "Acuerdo del paso 1.261109.md"))
UMBRAL = 80.0
TEXTO_LARGO = 40


def load(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def clave(r):
    # exc tiene una fila por extracto (clave 1, 2, 3 en TJS); el resto se identifica por (cod, campo)
    if r["campo"] == "exc":
        return (r["cod"], "exc", r["clave"])
    return (r["cod"], r["campo"])


def finales(rows):
    # Regla: valor final = fila no vacía de la pasada más alta; en empate, la última del archivo.
    best = {}
    for i, r in enumerate(rows):
        if not r["valor"].strip():
            continue
        k = clave(r)
        orden = (int(r["pasada"]), i)
        if k not in best or orden > best[k][0]:
            best[k] = (orden, r)
    return {k: v[1] for k, v in best.items()}


def conflictos(rows):
    # Claves con más de un valor distinto dentro de la pasada más alta
    grupos = collections.defaultdict(list)
    for r in rows:
        if r["valor"].strip():
            grupos[clave(r)].append(r)
    n = 0
    for rs in grupos.values():
        top = max(int(r["pasada"]) for r in rs)
        if len({r["valor"] for r in rs if int(r["pasada"]) == top}) > 1:
            n += 1
    return n


def mostrar(v):
    return "[texto libre de %d caracteres]" % len(v) if len(v) > TEXTO_LARGO else v


def pct(ok, n):
    return ("%.1f" % (100.0 * ok / n)).replace(".", ",") if n else "sin datos"


def tabla(sub):
    por = collections.defaultdict(lambda: [0, 0])
    for f in sub:
        por[f["campo"]][0] += 1
        por[f["campo"]][1] += f["ok"]
    lineas = ["| Campo | Comparadas | Coinciden | Acuerdo (%) |", "|---|---:|---:|---:|"]
    for c in sorted(por):
        n, ok = por[c]
        lineas.append("| %s | %d | %d | %s |" % (c, n, ok, pct(ok, n)))
    n = len(sub)
    ok = sum(f["ok"] for f in sub)
    lineas.append("| **Total** | **%d** | **%d** | **%s** |" % (n, ok, pct(ok, n)))
    return lineas, n, ok


def main():
    J = load(JLR)
    T = load(TJS)
    fj = finales(J)
    ft = finales(T)
    cods_j = sorted(set(r["cod"] for r in J))
    cods_t = set(r["cod"] for r in T)
    comunes = [c for c in cods_j if c in cods_t]
    id_j = {r["cod"]: r["id"] for r in J}
    id_t = {r["cod"]: r["id"] for r in T}

    sin_par = collections.Counter()
    filas = []
    for k, rj in fj.items():
        if k[1] == "exc":
            continue
        if k not in ft:
            sin_par[k[1]] += 1
            continue
        rt = ft[k]
        filas.append({
            "cod": k[0], "campo": k[1], "id": id_t.get(k[0], ""),
            "vT": rt["valor"].strip(), "vJ": rj["valor"].strip(),
            "autoJ": rj["auto"], "pasadaJ": rj["pasada"], "autoT": rt["auto"],
        })

    # exc: JLR marca "(ninguna)" cuando no hay extracto; TJS tiene un extracto por fila no "(ninguna)"
    for cod in comunes:
        kj = [k for k in fj if k[0] == cod and k[1] == "exc"]
        kt = [k for k in ft if k[0] == cod and k[1] == "exc"]
        if not kj:
            continue
        if not kt:
            sin_par["exc"] += 1
            continue
        vj = "con extracto" if any(fj[k]["valor"].strip() != "(ninguna)" for k in kj) else "ninguna"
        vt = "con extracto" if any(ft[k]["valor"].strip() != "(ninguna)" for k in kt) else "ninguna"
        filas.append({
            "cod": cod, "campo": "exc", "id": id_t.get(cod, ""),
            "vT": vt, "vJ": vj,
            "autoJ": fj[kj[0]]["auto"], "pasadaJ": fj[kj[0]]["pasada"], "autoT": "",
        })

    for f in filas:
        f["ok"] = 1 if f["vT"] == f["vJ"] else 0

    # atr: TJS tiene varias filas por pantalla en la pasada más alta; alternativa "cualquiera coincide"
    atr_alt_ok = 0
    atr_alt_n = 0
    for f in filas:
        if f["campo"] != "atr":
            continue
        atr_alt_n += 1
        rs = [r for r in T if r["cod"] == f["cod"] and r["campo"] == "atr" and r["valor"].strip()]
        if not rs:
            continue
        top = max(int(r["pasada"]) for r in rs)
        vals = {r["valor"].strip() for r in rs if int(r["pasada"]) == top}
        if f["vJ"] in vals:
            atr_alt_ok += 1

    sin_auto = [f for f in filas if f["autoJ"] != "pre"]
    discrep = [f for f in filas if f["ok"] == 0]

    # precargadas JLR
    pre_total = sum(1 for r in J if r["auto"] == "pre")
    pre_finales = [k for k, r in fj.items() if r["auto"] == "pre"]
    pre_superados = pre_total - len(pre_finales)

    # no cruzables: TJS clasificó campos de pantallas comunes que JLR no clasificó
    tjs_solo = 0
    for k in ft:
        if k[0] in comunes and k not in fj and k[1] != "exc":
            tjs_solo += 1
    prefijo_dist = sum(1 for c in comunes if id_j[c][0] != id_t[c][0])

    g_tab, n_g, ok_g = tabla(filas)
    s_tab, n_s, ok_s = tabla(sin_auto)
    pg = 100.0 * ok_g / n_g if n_g else 0
    ps = 100.0 * ok_s / n_s if n_s else 0

    L = []
    L.append("Acuerdo del paso 1: JLR contra TJS")
    L.append("")
    L.append("Generado por `Pruebas/acuerdo-paso1.py`. Fuentes: `Pruebas/Lectura/clasificacion-JLR-261107.csv` (JLR) y `~/Desktop/SRC/clasificacion-TJS-261107.csv` (TJS).")
    L.append("")
    L.append("## Reglas aplicadas")
    L.append("")
    L.append("- Cruce de pantallas: por `cod` (el código de 6 o 7 caracteres). El `id` es `cod` precedido por una letra que no es igual en los dos archivos, así que no sirve como clave.")
    L.append("- Valor final por (cod, campo): la fila no vacía de la pasada más alta; en empate, la última del archivo.")
    L.append("- Para `exc` (un extracto por fila en TJS, con clave 1, 2 o 3) se compara solo si hay extracto o no: JLR marca `(ninguna)` y TJS tiene al menos una fila con extracto.")
    L.append("- Denominador: los campos finales de JLR con par en TJS, en las %d pantallas en común." % len(comunes))
    L.append("- Precargada (`auto` = `pre`): la fila final de JLR con esa marca no cuenta como juicio independiente. Se reporta con y sin ellas.")
    L.append("- Umbral de aceptación: %s %%." % str(int(UMBRAL)))
    L.append("")
    L.append("## Resultado")
    L.append("")
    L.append("| Medida | Valor |")
    L.append("|---|---|")
    L.append("| Acuerdo global, con precargadas | %s %% (%d de %d) |" % (pct(ok_g, n_g), ok_g, n_g))
    L.append("| Acuerdo global, sin precargadas | %s %% (%d de %d) |" % (pct(ok_s, n_s), ok_s, n_s))
    L.append("| Supera el 80 %% (con precargadas) | %s |" % ("Sí" if pg >= UMBRAL else "No"))
    L.append("| Supera el 80 %% (sin precargadas) | %s |" % ("Sí" if ps >= UMBRAL else "No"))
    L.append("| Discrepancias (con precargadas) | %d |" % len(discrep))
    L.append("")
    L.append("## Acuerdo por campo, con precargadas")
    L.append("")
    L += g_tab
    L.append("")
    L.append("## Acuerdo por campo, sin precargadas")
    L.append("")
    L += s_tab
    L.append("")
    L.append("## Precargadas de JLR")
    L.append("")
    L.append("- Filas con `auto` = `pre` en JLR: %d." % pre_total)
    L.append("- Filas precargadas que siguen como valor final: %d. Las demás fueron reemplazadas por una pasada posterior: %d." % (len(pre_finales), pre_superados))
    L.append("")
    L.append("## Discrepancias")
    L.append("")
    if discrep:
        L.append("| Cod | Campo | Valor TJS | Valor JLR | Precargada en JLR |")
        L.append("|---|---|---|---|---|")
        for f in sorted(discrep, key=lambda x: (x["cod"], x["campo"])):
            L.append("| %s | %s | %s | %s | %s |" % (f["cod"], f["campo"], mostrar(f["vT"]), mostrar(f["vJ"]), "sí" if f["autoJ"] == "pre" else "no"))
    else:
        L.append("Sin discrepancias.")
    L.append("")
    L.append("## Anomalías y ambigüedades")
    L.append("")
    L.append("- Campos sin par (JLR clasificó, TJS no tiene valor final): %s." % (", ".join("%s: %d" % (c, n) for c, n in sorted(sin_par.items())) or "ninguno"))
    L.append("- Campos que TJS clasificó en pantallas comunes y JLR no: %d. No entran en el acuerdo." % tjs_solo)
    L.append("- Pantallas comunes con prefijo de `id` distinto entre archivos: %d de %d. Se cruzó por `cod`." % (prefijo_dist, len(comunes)))
    L.append("- Claves con más de un valor en la pasada más alta: TJS %d, JLR %d. Se usó la última fila del archivo." % (conflictos(T), conflictos(J)))
    L.append("- Los conflictos de TJS son todos de `atr` (varias filas de atribución por pantalla en la pasada 2, con claves formato, cierre, otra o teoría). La regla de la última fila es arbitraria para ese campo. Alternativa: JLR coincide si su valor aparece entre las filas de TJS de la pasada más alta: %d de %d (%s %%)." % (atr_alt_ok, atr_alt_n, pct(atr_alt_ok, atr_alt_n)))
    L.append("- TJS tiene 11 filas con `auto` = `si` (campos m1 y m2, pasada 3). No son precargadas por la regla, pero su sentido no está documentado en el CSV: conviene confirmarlo.")
    L.append("- Los campos `atr` y `exc` son texto libre en parte de las filas: solo se compara la igualdad exacta; los textos largos no se transcriben.")
    L.append("- TJS tiene 9 filas precargadas (`pre`) en pasada 3 y 75 en pasada 1: no se excluyen del acuerdo de TJS. Si se quisiera excluir las de TJS, el acuerdo cambia; no se calculó.")
    texto = "\n".join(L) + "\n"

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(texto)
    print(texto)


if __name__ == "__main__":
    main()
