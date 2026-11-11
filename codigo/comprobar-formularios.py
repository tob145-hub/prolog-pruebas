#!/usr/bin/env python3
"""Comprueba los criterios de aceptación 1 a 3 del cuaderno de citas (2026-11-07).
Imprime solo recuentos. Los criterios 4 a 6 corresponden al cuaderno, que se arma después de abrir la clave.

Uso: python3 -I comprobar-formularios.py [--prueba]
"""
import json, os, re, sys, glob

BASE = os.path.dirname(os.path.abspath(__file__))
PRUEBA = "--prueba" in sys.argv
FORM = os.path.join(BASE, "Formulario", "Prueba") if PRUEBA else os.path.join(BASE, "Formulario")
PUB = os.path.join(BASE, "Transcripciones numeradas" + (" (prueba)" if PRUEBA else ""))
res = []


def ok(n, cond, det):
    res.append(cond)
    print("%s criterio %s: %s" % ("OK " if cond else "FALLA", n, det))


master = json.load(open(os.path.join(FORM, "numeracion.json"), encoding="utf-8"))
clave = json.load(open(os.path.join(FORM, "CLAVE formulario - no abrir antes de clasificar.json"), encoding="utf-8"))

# 1. conversaciones, primeras respuestas, ubicación única
nexp = len(master)
r1 = sum(1 for e in master.values() if e.get("R1"))
conv = nexp * 4
secuencial = all(v == list(range(1, len(v) + 1)) and len(v) > 0 for e in master.values() for v in e.values())
ubic = [(e, t, n) for e, ts in master.items() for t, v in ts.items() for n in v]
ok(1, nexp == 36 and conv == 144 and r1 == 36 and secuencial and len(ubic) == len(set(ubic)),
   "%d expedientes, %d conversaciones, %d primeras respuestas, %d ubicaciones, %d repetidas" % (nexp, conv, r1, len(ubic), len(ubic) - len(set(ubic))))

# 2. numeración: formularios y versión publicada coinciden con la maestra
por_id = {f["id"]: f for f in clave["filas"]}
mal = 0
n_sec = 0
for nombre in ("Clasificación TJS.html", "Clasificación JLR paso 1.html"):
    h = open(os.path.join(FORM, nombre), encoding="utf-8").read()
    datos = json.loads(re.search(r"const D = (.*?);\nconst KEY", h, re.S).group(1))
    for it in [x for x in datos["items"] if x.get("tipo") != "apertura"]:
        f = por_id[it["id"]]
        e = "%s|%s|r%d" % (f["modelo"], f["caso"], f["repeticion"])
        for s in it["secs"]:
            n_sec += 1
            ns = [p["n"] for p in s["parrs"] if p["n"]]
            m = master[e][s["turno"]]
            if it["tipo"] == "marc":
                if not set(ns) <= set(m):
                    mal += 1
            elif ns != m:
                mal += 1
pub_mal = 0
n_pub = 0
for f in glob.glob(os.path.join(PUB, "*", "*.md")):
    t = open(f, encoding="utf-8").read()
    mod = os.path.basename(os.path.dirname(f))
    caso, rep = re.match(r"(\w+)-r(\d)\.md", os.path.basename(f)).groups()
    e = "%s|%s|r%s" % (mod, caso, rep)
    for turno, v in master[e].items():
        n_pub += 1
        tags = [int(x) for x in re.findall(r"^\[%s-(\d+)\] " % turno, t, re.M)]
        if tags != v:
            pub_mal += 1
ok(2, mal == 0 and pub_mal == 0 and n_pub == 36 * 6,
   "%d secciones de formulario con numeración distinta de la maestra; %d de %d turnos publicados con numeración distinta" % (mal, pub_mal, n_pub))

# 3. la versión de lectura no contiene nombres de modelos ni razonamiento visible
pat = re.compile(r"(?i:\b(claude|anthropic|openai|chatgpt|gpt[- ]?\d|gemini|google|deepseek|kimi|moonshot|glm|z\.?ai|zhipu|astra|opus|argon|llama[- ]?\d))|\bLLaMA\b")
hits = 0
razon = 0
for nombre in ("Clasificación TJS.html", "Clasificación JLR paso 1.html"):
    h = open(os.path.join(FORM, nombre), encoding="utf-8").read()
    datos = json.loads(re.search(r"const D = (.*?);\nconst KEY", h, re.S).group(1))
    for it in [x for x in datos["items"] if x.get("tipo") != "apertura"]:
        for s in it["secs"]:
            for p in s["parrs"]:
                hits += len(pat.findall(p["t"]))
                if re.search(r"(reasoning|razonamiento visible)", p["t"], re.I):
                    razon += 1
    hits += len(pat.findall(json.dumps(datos["consulta"]))) + 0
ok(3, hits == 0 and razon == 0,
   "%d menciones de nombres de modelos o empresas en el texto de lectura (con la consulta); %d párrafos que aluden al razonamiento visible" % (hits, razon))
print("Resultado: %d de %d criterios cumplidos" % (sum(res), len(res)))
