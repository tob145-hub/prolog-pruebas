#!/usr/bin/env python3
"""Patrones por modelo (2026-11-09): recuentos de las marcas de TJS (36 respuestas de cada tipo) por modelo, con las
dudosas del paso 2 excluidas y las pantallas comunes con JLR contadas aparte. Abre la clave del formulario con autorización de TJS (2026-11-09).
No lee texto de respuestas. Salida: Análisis/Patrones por modelo.261109.md
"""
import csv, os, json, collections, importlib.util

BASE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(BASE)


def cargar(nombre, ruta):
    sp = importlib.util.spec_from_file_location(nombre, ruta)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


AC = cargar("ac", os.path.join(BASE, "acuerdo-paso1.py"))
T = AC.load(os.path.join(BASE, "Formulario", "clasificacion-TJS-revisada3-261110.csv"))
COM = list(csv.DictReader(open(os.path.join(BASE, "Formulario", "clasificacion-comun-261109.csv"), encoding="utf-8-sig")))
K = json.load(open(os.path.join(BASE, "Formulario", "CLAVE formulario - no abrir antes de clasificar.json"), encoding="utf-8"))
OUT = os.path.join(PROJ, "Análisis", "Patrones por modelo.261110.md")
MOD = ["astra", "opus", "gemini", "kimi", "deepseek", "glm"]

modelo = {f["codigo"]: f for f in K["filas"]}
comunes = {r["cod"] for r in COM}
dudosa = {(r["cod"], r["campo"]) for r in COM if r["estado"] == "dudosa"}
F = AC.finales(T)


def vals(cod, campo):
    if (cod, campo) in dudosa:
        return None
    if campo == "atr":
        rs = [r for r in T if r["cod"] == cod and r["campo"] == "atr" and r["valor"].strip()]
        if not rs:
            return None
        t = max(int(r["pasada"]) for r in rs)
        return sorted({r["valor"].split("|")[0] for r in rs if int(r["pasada"]) == t})
    if campo == "exc":
        rs = [r for r in F.values() if r["cod"] == cod and r["campo"] == "exc"]
        if not rs:
            return None
        nombres = sorted({r["valor"].split("|")[0].split(":")[0].strip() for r in rs if r["valor"].strip() != "(ninguna)"})
        return nombres or ["ninguna"]
    r = F.get((cod, campo))
    return [r["valor"].strip()] if r else None


# (campo, título, tipo de pantalla)
CAMPOS = [("err", "Error en la primera respuesta", "rp"), ("nosabe", "No puede saber qué hizo", "rp"), ("atr", "Atribución (una pantalla puede tener varias)", "rp"),
          ("exc", "Excepciones (nombres cargados; una respuesta puede tener varios)", "exp"), ("hechos", "Hechos", "exp"),
          ("veh1", "Vehículo en la primera respuesta (bicicleta)", "exp"), ("veh3", "Vehículo en la pregunta 3 (bicicleta)", "exp"),
          ("raz1", "Razón en la primera respuesta (bicicleta)", "exp"), ("raz3", "Razón en la pregunta 3 (bicicleta)", "exp"),
          ("conc3", "Conclusión tras la pregunta 3, homicidio (falla del acelerador)", "exp", "homicidio"),
          ("conc3", "Conclusión tras la pregunta 3, bicicleta (¿trató a la bicicleta como vehículo?)", "exp", "bicicleta"),
          ("conc4", "Conclusión tras la pregunta 4, homicidio (llegaba tarde, control)", "exp", "homicidio"),
          ("conc4", "Conclusión tras la pregunta 4, bicicleta (¿trató a la vereda como vía pública?, control)", "exp", "bicicleta"),
          ("obj4", "Objeción en la pregunta 4, homicidio", "exp", "homicidio"), ("obj4", "Objeción en la pregunta 4, bicicleta", "exp", "bicicleta")]
# Pregunta 1 y pregunta 2: 12 pantallas (una por modelo y caso), clasificadas solo por TJS (pasada 3; error revisado el 10/11 en la pasada 4).
P12 = [("c1", "Conclusión tras la pregunta 1"), ("c2", "Conclusión tras la pregunta 2"), ("o2", "Objeción en la pregunta 2")]
P12C = [("v1", "Verdad en la pregunta 1"), ("d1", "Derrotabilidad en la pregunta 1"), ("e1", "Error en la primera respuesta, pregunta 1")]
CONST = [("verd", "Verdad"), ("derr", "Derrotabilidad"), ("conc", "Conclusión en la repregunta"), ("inf", "Inferencia")]


def tabla(campo, caso=None):
    por = {m: collections.Counter() for m in MOD}
    n = {m: [0, 0] for m in MOD}  # (pantallas con dato, de ellas comunes)
    todos = collections.Counter()
    for cod, f in modelo.items():
        v = vals(cod, campo)
        if v is None:
            continue
        if caso and f.get("caso") != caso:
            continue
        m = f["modelo"]
        n[m][0] += 1
        n[m][1] += (cod in comunes)
        for x in v:
            por[m][x] += 1
            todos[x] += 1
    cols = [k for k, _ in todos.most_common()]
    L = ["| Modelo | n (comunes) | " + " | ".join(cols) + " |", "|---|---:|" + "---:|" * len(cols)]
    for m in MOD:
        L.append("| %s | %d (%d) | " % (m, n[m][0], n[m][1]) + " | ".join(str(por[m][c]) for c in cols) + " |")
    L.append("| **Total** | %d (%d) | " % (sum(x[0] for x in n.values()), sum(x[1] for x in n.values())) + " | ".join(str(todos[c]) for c in cols) + " |")
    return L, todos


def main():
    L = ["Patrones por modelo", "",
         "Fecha: 10 de noviembre de 2026 (reemplaza la versión del 9 de noviembre: conclusión y objeción tras las preguntas 3 y 4 separadas por caso, y preguntas 1 y 2 agregadas). Texto de método, en impersonal y publicable. Generado con `Pruebas/patrones-por-modelo.py`. Lo clasificado por TJS en las 36 respuestas de cada tipo, desglosado por modelo con la clave del formulario, abierta con autorización de TJS el 9 de noviembre después de terminar la clasificación. Descriptivo: con 6 respuestas por modelo y tipo no hay inferencia estadística.", "",
         "## Contenido", "", "1. [[#Qué datos entran]]", "2. [[#Criterios sin variación]]", "3. [[#Criterios con variación]]", "4. [[#Preguntas 1 y 2]]", "5. [[#Límites]]", "",
         "## Qué datos entran", "",
         "- Marcas de TJS tras su revisión (`clasificacion-TJS-revisada3-261110.csv`) en las 36 pantallas de cada tipo (primeras respuestas y repreguntas).",
         "- Se excluyen las 5 dudosas del paso 2 (error en una pantalla, atribución en una, razón en la bicicleta en dos y hechos en una). El resto de las pantallas comunes con JLR conserva la marca de TJS, que es la clasificación común (o coincide con la de JLR). En la columna \"n (comunes)\" va el número de pantallas con dato y, entre paréntesis, cuántas son de las 18 comunes con JLR. Las demás las clasificó solo TJS.",
         "- Las repeticiones se agregan por modelo. Los dos casos se agregan, salvo en las preguntas 3 y 4, que son distintas en cada caso. Los campos propios de la bicicleta tienen menos pantallas.",
         "- No se usó la reclasificación de JLR en excepciones: las marcas de TJS no cambiaron. La relectura de la respuesta B se informa aparte.", ""]
    L += ["## Criterios sin variación", ""]
    for c, t in CONST:
        tab, todos = tabla(c)
        L.append("- %s: %s." % (t, ", ".join("%s %d" % (k, v) for k, v in todos.most_common())))
    L.append("")
    L += ["## Criterios con variación", ""]
    for x in CAMPOS:
        tab, todos = tabla(x[0], x[3] if len(x) > 3 else None)
        L += ["### " + x[1], ""] + tab + [""]
    L += ["## Preguntas 1 y 2", "", "12 pantallas, una por modelo y caso, clasificadas solo por TJS. El error en la primera respuesta se revisó el 10 de noviembre (9 \"concede\" marcados antes de advertir el malentendido sobre el campo pasaron a \"reinterpreta\"; revisión posterior a los datos).", ""]
    for c, t in P12C:
        tab, todos = tabla(c)
        L.append("- %s: %s." % (t, ", ".join("%s %d" % (k, v) for k, v in todos.most_common())))
    L.append("")
    for c, t in P12:
        tab, todos = tabla(c)
        L += ["### " + t, ""] + tab + [""]
    L += ["## Límites", "",
          "1. Seis respuestas por modelo y tipo: un solo caso cambia una celda entera. No se calculan porcentajes ni pruebas.",
          "2. Los criterios sin variación (verdad, derrotabilidad, conclusión, inferencia) no discriminan entre modelos con esta clasificación. En verdad y derrotabilidad el valor constante (trata) es en parte efecto de la regla de lectura del 9 de noviembre, que cuenta como \"trata\" cualquier explicación de cómo se obtiene la conclusión, aunque sea breve; con una regla más exigente la variación podría ser otra. Esta regla se fijó después de ver el acuerdo del paso 1.",
          "3. 18 de las 36 pantallas de cada tipo no las clasificó JLR: ahí la marca es de un solo clasificador.",
          "4. Las diferencias entre modelos que se leen en las tablas (por ejemplo en \"no puede saber qué hizo\", vehículo y razón en la bicicleta) son descripciones de esta muestra y no se contrastaron con otra clasificación.", "",
          "Notas relacionadas: [[Acuerdo final tras el paso 2.261109]] · [[Patrones por modelo.261109]] · [[Cruce del borrador de JLR con los patrones.261110]] · [[seguir]]", ""]
    open(OUT, "w", encoding="utf-8").write("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main()
