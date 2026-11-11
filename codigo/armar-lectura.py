#!/usr/bin/env python3
"""Arma las tandas anónimas de lectura (2026-11-06).

Uso: python3 -I armar-lectura.py
Lee Pruebas/Corridas/20261105-rep1-<modelo>/ (turnos 1 y 2 de p1; p2 a p4) y
Pruebas/Corridas/20261106-repregunta-v2-A/ (turno 3 de p1, v2). El turno 3
original (v1) no se usa. Escribe en Pruebas/Lectura/: 8 tandas, la clave aparte
y un informe de controles. No se incluye el razonamiento visible.
"""
import json, random, re, os, sys, collections

BASE = os.path.dirname(os.path.abspath(__file__))
COR = os.path.join(BASE, "Corridas")
OUT = os.path.join(BASE, "Lectura")
V2 = os.path.join(COR, "20261106-repregunta-v2-A")
SEED = 20261106
MODELOS = {  # carpeta rep1 -> (carpeta v2, nombre en archivos)
    "astra": "openai_gpt-6-astra",
    "deepseek": "deepseek_deepseek-v4.1-flash-1017",
    "gemini": "google_gemini-4-argon",
    "glm": "z-ai_glm-5.3",
    "kimi": "moonshotai_kimi-k3.1-pro",
    "opus": "anthropic_claude-opus-5.5",
}
CASOS = ["homicidio", "bicicleta"]
PREGS = ["p1", "p2", "p3", "p4"]
REPS = [1, 2, 3]

avisos = []


def cargar(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def contenido(resp):
    ch = resp["choices"][0]
    if ch.get("finish_reason") not in ("stop", None) and ch.get("native_finish_reason") not in ("completed", "stop", "end_turn", None):
        pass
    return ch["message"]["content"], ch.get("finish_reason"), ch.get("native_finish_reason")


def limpiar(t):
    """Quita marcas de formato que delatan al modelo, sin tocar el texto."""
    t = t.replace("\r\n", "\n")
    t = re.sub(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$", "", t, flags=re.M)      # reglas horizontales
    t = re.sub(r"^\s{0,3}#{1,6}\s*", "", t, flags=re.M)                  # encabezados
    t = re.sub(r"\*\*(.+?)\*\*", r"\1", t, flags=re.S)                   # negrita
    t = re.sub(r"__(.+?)__", r"\1", t, flags=re.S)
    t = re.sub(r"(?<![\*\w])\*(?!\s)([^\*\n]+?)(?<!\s)\*(?![\*\w])", r"\1", t)  # cursiva
    t = re.sub(r"^(\s*)[\*•·]\s+", r"\1- ", t, flags=re.M)               # viñetas
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


# ---------------------------------------------------------------- carga
items = []
consulta = {}
preguntas = {}
repregunta = set()
for m, nom in MODELOS.items():
    d = os.path.join(COR, f"20261105-rep1-{m}")
    for caso in CASOS:
        for r in REPS:
            pref = f"{caso}-{nom}-r{r}"
            t1 = cargar(os.path.join(d, f"{pref}-turno1.json"))
            txt1, fr1, nfr1 = contenido(t1["respuesta"])
            consulta.setdefault(caso, set()).add(t1["cuerpo"]["messages"][0]["content"])
            for p in PREGS:
                if p == "p1":  # Opus no tiene p1.json (su turno 3 original falló): se usa p1-turno2.json en todos
                    j = cargar(os.path.join(d, f"{pref}-p1-turno2.json"))
                    c2, fr2, nfr2 = contenido(j["respuesta"])
                    preguntas.setdefault((caso, p), set()).add(j["cuerpo"]["messages"][-1]["content"])
                    if j["cuerpo"]["messages"][1]["content"] != txt1:
                        avisos.append(f"turno1 distinto en {pref}-p1-turno2.json")
                    jp = os.path.join(d, f"{pref}-p1.json")
                    if os.path.exists(jp) and contenido(cargar(jp)["respuesta_turno2"])[0] != c2:
                        avisos.append(f"p1.json y p1-turno2.json difieren en {pref}")
                else:
                    j = cargar(os.path.join(d, f"{pref}-{p}.json"))
                    c1, _, _ = contenido(j["respuesta_turno1"])
                    if c1 != txt1:
                        avisos.append(f"turno1 distinto en {pref}-{p} respecto de turno1.json")
                    c2, fr2, nfr2 = contenido(j["respuesta_turno2"])
                    preguntas.setdefault((caso, p), set()).add(j["cuerpo_turno2"]["messages"][-1]["content"])
                it = dict(caso=caso, modelo=m, rep=r, p=p, t1=txt1, c2=c2, c3=None,
                          fin=[fr1, fr2], fuente=f"{os.path.basename(d)}/{pref}-{p}" + ("-turno2" if p == "p1" else "") + ".json")
                if p == "p1":
                    v = cargar(os.path.join(V2, nom, f"{pref}-p1-v2A-turno3.json"))
                    if not v.get("pasa_el_filtro"):
                        avisos.append(f"v2 no pasa el filtro: {pref}")
                    it["c3"], fr3, _ = contenido(v["respuesta"])
                    it["fin"].append(fr3)
                    repregunta.add(v["texto_turno3"])
                    msgs = v["cuerpo"]["messages"]
                    if msgs[1]["content"] != txt1 or msgs[3]["content"] != c2:
                        avisos.append(f"el contexto de la v2 no coincide con los turnos guardados: {pref}")
                    it["fuente"] += f" + {os.path.basename(V2)}/{nom}/{pref}-p1-v2A-turno3.json"
                for x in (txt1, c2, it["c3"]):
                    if x is not None and not x.strip():
                        avisos.append(f"respuesta vacía en {pref}-{p}")
                if any(f not in ("stop", None) for f in it["fin"]):
                    avisos.append(f"finish_reason no 'stop' en {pref}-{p}: {it['fin']}")
                items.append(it)

assert len(items) == 144, len(items)
for caso, s in consulta.items():
    assert len(s) == 1, f"consulta no uniforme en {caso}"
for k, s in preguntas.items():
    assert len(s) == 1, f"pregunta no uniforme en {k}"
assert len(repregunta) == 1, "repregunta v2 no uniforme"
REPREG = next(iter(repregunta))

# ---------------------------------------------------------------- controles de autoidentificación
pat = re.compile(r"\b(claude|anthropic|openai|chatgpt|gpt[- ]?\d|gemini|google|deepseek|kimi|moonshot|glm|z\.?ai|zhipu|astra|opus|argon|llama|modelo de lenguaje|soy una? (ia|inteligencia))\b", re.I)
for it in items:
    for nombre, x in (("turno1", it["t1"]), ("turno2", it["c2"]), ("turno3", it["c3"])):
        if x:
            for mm in pat.finditer(x):
                a = max(0, mm.start() - 40); b = mm.end() + 40
                avisos.append(f"posible autoidentificación [{it['caso']}-{it['modelo']}-r{it['rep']}-{it['p']} {nombre}]: …{x[a:b]!r}…")

# ---------------------------------------------------------------- códigos y tandas
rng = random.Random(SEED)
alfabeto = "BCDFGHJKLMNPQRSTVWXZ23456789"
usados = set()
for it in items:
    while True:
        c = "".join(rng.choice(alfabeto) for _ in range(5))
        if c not in usados:
            usados.add(c); it["cod"] = c; break

os.makedirs(OUT, exist_ok=True)
NOMBRE_CASO = {"homicidio": "Homicidio", "bicicleta": "Bicicleta"}
NOM_TANDA = {}
n = 0
clave = []
resumen = []
for caso in CASOS:
    for p in PREGS:
        n += 1
        grupo = [i for i in items if i["caso"] == caso and i["p"] == p]
        rng.shuffle(grupo)
        nombre = f"Tanda {n} - {NOMBRE_CASO[caso]} {p.upper()}.md"
        NOM_TANDA[(caso, p)] = nombre
        L = []
        L.append(f"Tanda {n} de 8. Caso: {NOMBRE_CASO[caso]}. Pregunta: {p.upper()}. {len(grupo)} conversaciones, en orden al azar.\n")
        L.append("Texto de las respuestas con las marcas de formato quitadas (encabezados, negritas, cursivas, reglas, viñetas unificadas). Sin razonamiento visible. Las respuestas del modelo van tal cual.\n")
        L.append("**Consulta inicial (igual en todas)**\n")
        L.append(next(iter(consulta[caso])) + "\n")
        L.append(f"**Pregunta (igual en todas)**\n")
        L.append(next(iter(preguntas[(caso, p)])) + "\n")
        if p == "p1":
            L.append("**Repregunta (igual en todas)**\n")
            L.append(REPREG + "\n")
        for k, it in enumerate(grupo, 1):
            L.append("\n---\n")
            L.append(f"**Código {it['cod']}** ({k} de {len(grupo)})\n")
            L.append("**Primera respuesta**\n")
            L.append(limpiar(it["t1"]) + "\n")
            L.append("**Respuesta a la pregunta**\n")
            L.append(limpiar(it["c2"]) + "\n")
            if p == "p1":
                L.append("**Respuesta a la repregunta**\n")
                L.append(limpiar(it["c3"]) + "\n")
            clave.append(dict(codigo=it["cod"], tanda=n, caso=caso, pregunta=p, modelo=it["modelo"], repeticion=it["rep"], fuente=it["fuente"]))
        txt = "\n".join(L)
        with open(os.path.join(OUT, nombre), "w", encoding="utf-8") as f:
            f.write(txt)
        resumen.append((nombre, len(grupo), len(txt.split())))

with open(os.path.join(OUT, "CLAVE - no abrir antes de clasificar.json"), "w", encoding="utf-8") as f:
    json.dump(dict(semilla=SEED, filas=sorted(clave, key=lambda x: x["codigo"])), f, ensure_ascii=False, indent=1)

with open(os.path.join(OUT, "Controles del armado.md"), "w", encoding="utf-8") as f:
    f.write("Controles del armado (2026-11-06). Este archivo menciona fuentes y modelos: no abrir antes de clasificar.\n\n")
    f.write("Tandas (palabras con la consulta y las preguntas incluidas):\n\n")
    for nombre, c, w in resumen:
        f.write(f"- {nombre}: {c} conversaciones, {w} palabras\n")
    f.write(f"\nAvisos ({len(avisos)}):\n\n")
    for a in avisos:
        f.write(f"- {a}\n")
print("\n".join(f"{a}: {b} conv, {c} palabras" for a, b, c in resumen))
print(f"{len(avisos)} avisos")
for a in avisos[:40]:
    print(" -", a[:200])
