#!/usr/bin/env python3
"""Piloto de reformulación de la repregunta de p1 (turno 3) para un modelo cuya repregunta original fue
bloqueada. Reutiliza los turnos 1 y 2 guardados (-turno1.json y -turno2.json de una carpeta de origen,
solo lectura), arma la conversación user/assistant/user/assistant/user con la candidata elegida de
consignas-repregunta-v2.json y llama una vez con los mismos parámetros que el turno 2 (modelo, esfuerzo,
proveedor fijo, sin fallback). Sin --ejecutar solo muestra lo que enviaría (no llama a la API).
Uso: python3 probar-repregunta.py --origen Corridas/20261105-rep1-opus --caso homicidio --rep 1 --candidata A [--ejecutar]
La clave se lee de OPENROUTER_API_KEY. Salida en ~/corridas-trasandino/ (no se escribe en Corridas/)."""
import argparse, json, os, sys
from pathlib import Path
import correr as c

AQUI = Path(__file__).resolve().parent

ap = argparse.ArgumentParser()
ap.add_argument("--origen", required=True)
ap.add_argument("--caso", required=True, choices=["homicidio", "bicicleta"])
ap.add_argument("--rep", type=int, required=True)
ap.add_argument("--candidata", required=True)
ap.add_argument("--modelo", default="anthropic/claude-opus-5.5")
ap.add_argument("--max-tokens", type=int, default=None)
ap.add_argument("--ejecutar", action="store_true")
a = ap.parse_args()

v2 = json.loads((AQUI / "consignas-repregunta-v2.json").read_text(encoding="utf-8"))
if a.candidata not in v2["candidatas"]:
    sys.exit(f"candidata desconocida: {a.candidata}")
nueva = v2["candidatas"][a.candidata]

base = f"{a.caso}-{a.modelo.replace('/', '_')}-r{a.rep}-p1"
origen = Path(a.origen)
t1 = json.loads((origen / f"{a.caso}-{a.modelo.replace('/', '_')}-r{a.rep}-turno1.json").read_bytes())
t2 = json.loads((origen / f"{base}-turno2.json").read_bytes())

msgs = t2["cuerpo"]["messages"]
if [m["role"] for m in msgs] != ["user", "assistant", "user"]:
    sys.exit("turno 2 guardado: mensajes inesperados")
r1 = t1.get("respuesta") or t1
if c.texto(r1) != msgs[1]["content"]:
    sys.exit("el turno 1 guardado no coincide con lo reenviado en el turno 2")
r2 = t2["respuesta"]
for n, r in ((1, r1), (2, r2)):
    if c.texto(r) is None or c.terminacion(r) != "stop" or c.modelo_distinto(a.modelo, r):
        sys.exit(f"turno {n} guardado no es una respuesta válida")
cuerpo = {k: v for k, v in t2["cuerpo"].items() if k != "messages"}
if a.max_tokens:
    cuerpo["max_tokens"] = a.max_tokens
cuerpo["messages"] = msgs + [{"role": "assistant", "content": c.texto(r2)}, {"role": "user", "content": nueva}]

print(f"Caso {a.caso}, r{a.rep}, candidata {a.candidata}, modelo {cuerpo['model']}, proveedor {cuerpo['provider']}, esfuerzo {cuerpo['reasoning']}")
print("Turno 3 enviado:", nueva)
print("Mensajes:", [m["role"] for m in cuerpo["messages"]])
if not a.ejecutar:
    print("[dry-run] No se llamó a la API.")
    sys.exit(0)

clave = os.environ.get("OPENROUTER_API_KEY")
if not clave:
    sys.exit("Falta OPENROUTER_API_KEY")
antes = c.saldo(clave)
resp, intentos, gasto = c.llamar(clave, cuerpo)
destino = c.SALIDA_DEFECTO / f"{c.marca()}-piloto-repregunta-v2-{a.candidata}-{a.caso}-r{a.rep}"
destino.mkdir(parents=True, exist_ok=True)
pasa = c.texto(resp) is not None and c.terminacion(resp) == "stop" and not c.modelo_distinto(a.modelo, resp)
reg = {"fecha_utc": c.ahora(), "candidata": a.candidata, "texto_turno3": nueva, "origen": str(origen),
       "cuerpo": cuerpo, "respuesta": resp, "intentos": intentos, "gasto_usd": gasto, "saldo_antes": antes, "pasa_el_filtro": pasa}
c.volcar(destino / f"{base}-v2{a.candidata}-turno3.json", reg)
if c.texto(resp):
    c.escribir(destino / f"{base}-v2{a.candidata}-turno3.md", c.texto(resp))
print(f"finish_reason={c.terminacion(resp)} pasa_el_filtro={pasa} gasto={gasto:.4f} USD. Salida: {destino}")
