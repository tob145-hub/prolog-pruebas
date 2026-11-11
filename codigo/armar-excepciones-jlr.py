#!/usr/bin/env python3
"""Arma el documento de reclasificación de excepciones para JLR (2026-11-09): las 6 primeras respuestas en las que JLR
cargó excepciones, con rótulos nuevos (A a F, orden sorteado con semilla), las reglas de lectura de las excepciones (1 a 8) y el formato de respuesta.
No lleva ninguna marca de TJS. Los textos se copian por programa desde `Formulario/Clasificación TJS.html`; no se leen en la sesión.
Salidas: Versiones/Reclasificación de excepciones por JLR.261109.md y Formulario/clave-excepciones-JLR-261109.json (rótulo -> pantalla).
Uso: python3 -I armar-excepciones-jlr.py        Imprime solo recuentos.
"""
import csv, os, re, sys, json, random, importlib.util

BASE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(BASE)
sys.argv = sys.argv[:1]
SEMILLA = 20261109


def cargar(nombre, ruta):
    sp = importlib.util.spec_from_file_location(nombre, ruta)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


R2 = cargar("r2", os.path.join(BASE, "armar-revision2.py"))
D = R2.leer_datos(os.path.join(BASE, "Formulario", "Clasificación TJS.html"))
ITEMS = {i["id"]: i for i in D["items"] if i.get("secs")}
J = list(csv.DictReader(open(os.path.join(BASE, "Lectura", "clasificacion-JLR-ajuste-261109.csv"), encoding="utf-8-sig")))
T = list(csv.DictReader(open(os.path.join(BASE, "Formulario", "clasificacion-TJS-revisada2-261109.csv"), encoding="utf-8-sig")))
REGLAS = os.path.join(PROJ, "Versiones", "Reglas de lectura de las excepciones.261108.md")
OUT = os.path.join(PROJ, "Versiones", "Reclasificación de excepciones por JLR.261109.md")
CLAVE = os.path.join(BASE, "Formulario", "clave-excepciones-JLR-261109.json")


def reglas():
    txt = open(REGLAS, encoding="utf-8").read().split("\n")
    i = next(k for k, l in enumerate(txt) if l.startswith("1. **Excepción.**"))
    j = next(k for k, l in enumerate(txt) if l.startswith("9. **Valores precargados.**"))
    return [l for l in txt[i:j] if l.strip() != "" or True]


def main():
    cods = sorted({r["cod"] for r in J if r["campo"] == "exc"})
    id_t = {r["cod"]: r["id"] for r in T}
    assert len(cods) == 6, cods
    rnd = random.Random(SEMILLA)
    orden = cods[:]
    rnd.shuffle(orden)
    rot = {chr(65 + k): c for k, c in enumerate(orden)}
    L = [
        "Reclasificación de excepciones en 6 primeras respuestas",
        "",
        "Fecha: 9 de noviembre de 2026. Texto de método.",
        "",
        "## Motivo y reglas de este paso",
        "",
        "1. En el paso 1, JLR marcó \"sin excepciones\" en las 6 primeras respuestas en las que se comparó el criterio de excepciones, y el acuerdo con TJS fue 1 de 6 (alfa -0,57). JLR declaró después que lo hizo por haber entendido mal la consigna o la regla, y que de haberla entendido bien las habría marcado.",
        "2. Se le pide a JLR que clasifique de nuevo solo el criterio de excepciones, en esas 6 respuestas, con las reglas de lectura de las excepciones del 8 de noviembre (abajo), sin consultar las marcas de TJS ni el documento del paso 2.",
        "3. Este paso no es del todo ciego: en el paso 2, JLR conoció las marcas de TJS en excepciones en 5 de estas 6 respuestas. Se declara.",
        "4. Las marcas anteriores de JLR se conservan y se informan. Las nuevas se informan junto a las originales como \"reclasificación de JLR, 9 de noviembre\". Se comparan con las de TJS con la misma regla del paso 1 (presencia o ausencia de al menos una excepción) y, además, por nombre y valor, sin cifra de acuerdo propia.",
        "5. No hay segunda vuelta: TJS no cambia sus marcas después de ver las nuevas, y la reclasificación de JLR tampoco se repite.",
        "6. Las respuestas se presentan con rótulos nuevos (A a F), en un orden sorteado con la semilla 20261109. Esta regla se fijó antes de recibir ninguna reclasificación.",
        "",
        "## Cómo responder",
        "",
        "Para cada respuesta, escribir una línea por cada factor que desplaza la norma que aplica la respuesta (reglas 1 a 5 y 7 de abajo), con este formato: **nombre — valor**. Nombres posibles: los de la regla 8. Valores posibles: inexistente, estipula, exige prueba o ninguna. Si no hay ningún factor que desplace la norma, escribir \"sin excepciones\". Si dudaste entre dos valores o dos nombres, anotar entre cuáles en la misma línea.",
        "",
        "## Reglas de lectura de las excepciones (8 de noviembre)",
        "",
    ] + reglas() + [""]
    sin = 0
    for rotulo in sorted(rot):
        cod = rot[rotulo]
        item = ITEMS.get(id_t[cod])
        sec = next((s for s in item["secs"] if s["turno"] == "R1"), None) if item else None
        L += ["## Respuesta %s" % rotulo, ""]
        if not sec:
            sin += 1
            L += ["[Falta: texto de la primera respuesta]", ""]
        else:
            for p in sec["parrs"]:
                L += [p["t"].replace("\n", "\n\n"), ""]
        L += ["Excepciones (una línea por factor, con nombre y valor; o \"sin excepciones\"): [ ]", "",
              "¿Dudaste en algo? [ ]", ""]
    L += ["Notas relacionadas: [[Reglas de lectura de las excepciones.261108]] · [[Acuerdo final tras el paso 2.261109]] · [[seguir]]", ""]
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    with open(CLAVE, "w", encoding="utf-8") as f:
        json.dump({"semilla": SEMILLA, "rotulo_a_cod": rot}, f, ensure_ascii=False, indent=1)
    print("respuestas", len(rot), "sin texto", sin, "->", OUT)


if __name__ == "__main__":
    main()
