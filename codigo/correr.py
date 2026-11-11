#!/usr/bin/env python3
"""Corre las conversaciones de dos o tres turnos del trabajo (Seminario Trasandino) por OpenRouter.

Por cada (caso, modelo, repetición): un primer turno con la consulta inicial, guardado aparte;
después, por cada pregunta pedida, una conversación aparte que parte de esa misma primera respuesta.
Si consignas.json trae una repregunta para esa pregunta (clave opcional "repreguntas" del caso, p. ej.
{"p1": "texto"}), la conversación sigue con un tercer turno: consulta, respuesta 1, pregunta, respuesta 2,
repregunta. En los tres turnos se reenvía solo el content de las respuestas, nunca el razonamiento.
Sin esa clave, el script se comporta como con dos turnos.
Cada modelo corre con el esfuerzo de razonamiento de modelos.json (campo "esfuerzo"), enviado en cada solicitud;
sin temperatura ni búsqueda web. Cada modelo se fija a un proveedor (modelos.json) sin fallbacks de ruteo.
Si responde un modelo distinto del pedido (p. ej., el fallback de Anthropic ante un rechazo), cuenta como falla.
La clave se lee de OPENROUTER_API_KEY.

Candados (solo --dry-run los saltea):
  - consignas.json: "aprobado_por_jlr" debe ser true, salvo con --piloto (excepción aprobada por Tob el
    2026-11-01: una repetición y una sola pregunta; queda registrada en el manifiesto).
  - modelos.json: los modelos pedidos deben estar en estado "aprobado".

Fallas: toda terminación distinta de "stop" se guarda como ERROR con marca de tiempo y no se usa.
Reemplazar una falla es una corrida nueva (--destino); las fallas quedan en la carpeta.
En una pregunta con repregunta, la respuesta del turno 2 se guarda aparte (-turno2.json, como el turno 1)
apenas llega, para que una falla del turno 3 se reanude sin rehacer el turno 2. Si el turno 2 falla,
no se corre el turno 3.

--desde CARPETA: retoma conversaciones de una corrida anterior (solo lectura) sin rehacer los turnos 1 y 2.
De cada conversación guardada toma esos dos turnos y corre solo el turno 3, en una carpeta nueva. Antes de
llamar verifica que la consulta y la pregunta guardadas coincidan literalmente con consignas.json actual
(no compara el hash completo de consignas, que difiere por la repregunta) y que el modelo, el proveedor y el
esfuerzo coincidan con modelos.json; si algo no coincide, aborta. Los candados de arriba rigen igual.

--solo-turno1 con --consignas ARCHIVO: corre solo la consulta inicial, con las consignas de otro archivo de Pruebas/
(variantes de redacción de la consulta; piloto 4, 2026-11-02). Guarda -turno1.json y -turno1.md; no corre los turnos 2 ni 3.

Salida: por defecto ~/corridas-trasandino/ (fuera de iCloud); copiar al proyecto al terminar.

Ejemplos:
  python3 correr.py --caso homicidio --preguntas p1 --reps 1 --dry-run
  python3 correr.py --caso homicidio --preguntas p1 --reps 1 --piloto --etiqueta piloto
  python3 correr.py --caso homicidio --preguntas p1 --reps 1 --destino 20261105-1000-piloto   # reanuda
  python3 correr.py --caso homicidio --preguntas p1 --reps 1 --modelos openai/gpt-6-astra --piloto \\
      --desde Corridas/20261102-0132-piloto-astra --etiqueta piloto-astra-repregunta   # solo el turno 3
"""
import argparse, hashlib, json, os, platform, sys, time, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

AQUI = Path(__file__).resolve().parent
API = "https://openrouter.ai/api/v1"
REINTENTOS = 4  # ante 429, 5xx, error de red o falla dentro de una respuesta 200
SALIDA_DEFECTO = Path.home() / "corridas-trasandino"


class Tope(Exception):
    pass


def ahora():
    return datetime.now(timezone.utc).isoformat()


def marca():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def escribir(ruta, contenido):
    tmp = ruta.with_name(ruta.name + ".tmp")
    tmp.write_text(contenido, encoding="utf-8")
    os.replace(tmp, ruta)


def volcar(ruta, obj):
    escribir(ruta, json.dumps(obj, ensure_ascii=False, indent=2))


def texto(resp):
    try:
        return resp["choices"][0]["message"]["content"] or None
    except (KeyError, IndexError, TypeError, AttributeError):
        return None


def terminacion(resp):
    try:
        return resp["choices"][0].get("finish_reason")
    except (KeyError, IndexError, TypeError, AttributeError):
        return None


def costo(resp):
    try:
        return float(resp["usage"].get("cost") or 0)
    except (KeyError, TypeError, AttributeError):
        return 0.0


def tokens_razonamiento(resp):
    try:
        return resp["usage"]["completion_tokens_details"]["reasoning_tokens"]
    except (KeyError, TypeError):
        return None


# Ids y proveedores aceptados por modelo pedido (modelos.json no trae un campo apto). Derivados de lo que
# devolvieron las corridas del piloto (2026-11-02): el campo "model" de la respuesta fue siempre igual al id
# pedido, y "provider" el nombre de visualización del proveedor. El snapshot con fecha (p. ej.
# deepseek-v4.1-flash-20261017) solo figura en /generation; no es un id aceptable en la respuesta.
# Un modelo nuevo en modelos.json exige agregar su entrada acá (si no, el script no arranca).
ACEPTADOS = {
    "deepseek/deepseek-v4.1-flash-1017": {"modelos": ["deepseek/deepseek-v4.1-flash-1017"], "proveedores": ["DeepSeek"]},
    "anthropic/claude-opus-5.5": {"modelos": ["anthropic/claude-opus-5.5"], "proveedores": ["Anthropic"]},
    "openai/gpt-6-astra": {"modelos": ["openai/gpt-6-astra"], "proveedores": ["OpenAI"]},
    "google/gemini-4-argon": {"modelos": ["google/gemini-4-argon"], "proveedores": ["Google AI Studio"]},
    "z-ai/glm-5.3": {"modelos": ["z-ai/glm-5.3"], "proveedores": ["Z.AI"]},
    "moonshotai/kimi-k3.1-pro": {"modelos": ["moonshotai/kimi-k3.1-pro"], "proveedores": ["Moonshot AI"]},
}
# Snapshots que informó /generation en el piloto; solo se registra si coinciden, no es causa de falla.
SNAPSHOTS = {
    "deepseek/deepseek-v4.1-flash-1017": "deepseek/deepseek-v4.1-flash-20261017",
    "anthropic/claude-opus-5.5": "anthropic/claude-opus-5.5-20260921",
    "openai/gpt-6-astra": "openai/gpt-6-astra-20260903",
    "google/gemini-4-argon": "google/gemini-4-argon-20261013",
}


def modelo_distinto(pedido, resp):
    """True si la respuesta vino de otro modelo o de otro proveedor que el pedido (fallback u otro reemplazo).
    Comparación exacta contra ACEPTADOS; si falta el modelo o el proveedor en la respuesta, también es falla."""
    ok = ACEPTADOS.get(pedido)
    if ok is None:
        return True
    resp = resp or {}
    return resp.get("model") not in ok["modelos"] or resp.get("provider") not in ok["proveedores"]


def falla_de_cuerpo(resp):
    """None si la respuesta 200 es válida; si no, (reintentable, descripción)."""
    err = resp.get("error")
    if err is not None:
        codigo = err.get("code") if isinstance(err, dict) else None
        return (codigo is None or codigo == 429 or (isinstance(codigo, int) and codigo >= 500)), err
    try:
        ch = resp["choices"][0]
    except (KeyError, IndexError, TypeError):
        return True, "respuesta sin choices"
    if ch.get("error"):
        return True, ch["error"]
    if ch.get("finish_reason") == "error":
        return True, "finish_reason=error"
    return None


def llamar(clave, cuerpo):
    """Devuelve (respuesta, intentos_fallidos, gasto_usd de todas las respuestas recibidas)."""
    intentos, gasto, ultimo = [], 0.0, None
    datos = json.dumps(cuerpo).encode()
    for n in range(REINTENTOS):
        espera = 2 ** (n + 1)
        pedido = urllib.request.Request(
            f"{API}/chat/completions", data=datos,
            headers={"Authorization": f"Bearer {clave}", "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(pedido, timeout=900) as r:
                resp = json.load(r)
            gasto += costo(resp)
            falla = falla_de_cuerpo(resp)
            if falla is None:
                return resp, intentos, gasto
            intentos.append({"hora": ahora(), "http": 200, "falla": falla[1]})
            ultimo = resp
            if not falla[0]:
                return resp, intentos, gasto
        except urllib.error.HTTPError as e:
            cuerpo_err = e.read().decode(errors="replace")
            intentos.append({"hora": ahora(), "http": e.code, "falla": cuerpo_err[:1000]})
            ultimo = {"error": {"code": e.code, "body": cuerpo_err}}
            if not (e.code == 429 or e.code >= 500):
                return ultimo, intentos, gasto
            ra = e.headers.get("Retry-After")
            if ra and ra.isdigit():
                espera = max(espera, int(ra))
        except Exception as e:
            intentos.append({"hora": ahora(), "http": None, "falla": repr(e)})
            ultimo = {"error": {"code": None, "body": repr(e)}}
            if isinstance(e, TimeoutError) or isinstance(getattr(e, "reason", None), TimeoutError):
                return ultimo, intentos, gasto  # un timeout puede haberse cobrado: no se reintenta
        if n < REINTENTOS - 1:
            time.sleep(espera)
    return ultimo, intentos, gasto


# Esperas (s) antes de cada consulta a /generation: en el piloto, 3 intentos separados por 2 s dejaron
# 2 de 8 llamadas sin metadatos (los datos tardan en aparecer). Ahora 6 intentos, ~2,3 minutos en total.
ESPERAS_GENERACION = [3, 5, 10, 20, 40, 60]


def generacion(clave, id_):
    """Metadatos de la generación (proveedor efectivo, snapshot, tokens nativos); no gasta tokens.
    Reintenta con espera creciente; devuelve el dato o None si no apareció."""
    if not id_:
        return None
    for espera in ESPERAS_GENERACION:
        time.sleep(espera)
        try:
            pedido = urllib.request.Request(f"{API}/generation?id={id_}", headers={"Authorization": f"Bearer {clave}"})
            with urllib.request.urlopen(pedido, timeout=30) as r:
                d = json.load(r).get("data")
            if d:
                return d
        except Exception:
            continue
    return None


def recuperar_generaciones(clave, carpeta):
    """NO se usa en la corrida. Recupera los metadatos que faltaron (generacion null) en los registros de
    una carpeta de corrida: consulta /generation (sin costo) y escribe el resultado en
    generaciones-recuperadas.json dentro de esa carpeta, sin tocar los registros originales.
    Uso (con red): python3 correr.py --recuperar-generaciones CARPETA   (conviene hacerlo sobre una copia)."""
    carpeta = Path(carpeta)
    pendientes = []  # (archivo, campo, id de generación)
    for f in sorted(carpeta.glob("*.json")):
        if f.name in ("manifiesto.json", "generaciones-recuperadas.json") or "-ERROR-" in f.name:
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        if f.name.endswith(("-turno1.json", "-turno2.json")):
            if not d.get("generacion"):
                pendientes.append((f.name, "generacion", (d.get("respuesta") or {}).get("id")))
        else:
            if not d.get("generacion_turno2"):
                pendientes.append((f.name, "generacion_turno2", d.get("id_turno2")))
            if d.get("id_turno3") and not d.get("generacion_turno3"):
                pendientes.append((f.name, "generacion_turno3", d.get("id_turno3")))
    salida = {}
    for archivo, campo, id_ in pendientes:
        g = generacion(clave, id_)
        salida[f"{archivo}:{campo}"] = {"id": id_, "recuperado_utc": ahora(), "generacion": g}
        print(f"  {archivo} {campo} {id_}: {'ok' if g else 'sigue sin datos'}")
    volcar(carpeta / "generaciones-recuperadas.json", salida)
    return salida


def leer_fuente(carpeta, caso, modelo, rep, p, consignas, cfg_modelo):
    """Para --desde: lee en solo lectura la conversación de dos turnos guardada en una corrida anterior y la
    verifica contra consignas.json y modelos.json actuales. Devuelve (registro, sha256 del archivo);
    si algo no coincide, levanta ValueError con el motivo. No llama a la API ni escribe nada."""
    ruta = Path(carpeta) / f"{caso}-{modelo.replace('/', '_')}-r{rep}-{p}.json"
    if not ruta.exists():
        raise ValueError(f"no existe {ruta.name} en la carpeta de origen")
    crudo = ruta.read_bytes()
    d = json.loads(crudo)
    for campo, esperado in (("caso", caso), ("pregunta", p), ("repeticion", rep), ("modelo_pedido", modelo),
                            ("proveedor_pedido", cfg_modelo["proveedor"]), ("esfuerzo", cfg_modelo["esfuerzo"])):
        if d.get(campo) != esperado:
            raise ValueError(f"{ruta.name}: {campo} guardado {d.get(campo)!r} distinto del actual {esperado!r}")
    r1, r2 = d.get("respuesta_turno1"), d.get("respuesta_turno2")
    msgs = (d.get("cuerpo_turno2") or {}).get("messages") or []
    if [m.get("role") for m in msgs] != ["user", "assistant", "user"]:
        raise ValueError(f"{ruta.name}: los mensajes guardados del turno 2 no son user/assistant/user")
    if msgs[0]["content"] != consignas["consulta"]:
        raise ValueError(f"{ruta.name}: la consulta guardada no coincide literalmente con consignas.json")
    if msgs[2]["content"] != consignas["preguntas"][p]:
        raise ValueError(f"{ruta.name}: el texto de la pregunta {p} guardado no coincide literalmente con consignas.json")
    if texto(r1) is None or msgs[1]["content"] != texto(r1):
        raise ValueError(f"{ruta.name}: el turno 1 guardado no coincide con lo reenviado en el turno 2")
    for n, r in ((1, r1), (2, r2)):
        if texto(r) is None or terminacion(r) != "stop" or modelo_distinto(modelo, r):
            raise ValueError(f"{ruta.name}: el turno {n} guardado no es una respuesta válida (terminación o modelo)")
    return d, sha(crudo)


def saldo(clave):
    pedido = urllib.request.Request(f"{API}/credits", headers={"Authorization": f"Bearer {clave}"})
    with urllib.request.urlopen(pedido, timeout=30) as r:
        d = json.load(r)["data"]
    return d["total_credits"] - d["total_usage"]


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--recuperar-generaciones":
        clave = os.environ.get("OPENROUTER_API_KEY")
        if not clave:
            sys.exit("Falta OPENROUTER_API_KEY")
        recuperar_generaciones(clave, sys.argv[2])
        return
    ap = argparse.ArgumentParser()
    ap.add_argument("--caso", required=True, choices=["homicidio", "bicicleta"])
    ap.add_argument("--preguntas", nargs="+", required=True, help="p1 p2 p3 p4")
    ap.add_argument("--reps", type=int, default=1)
    ap.add_argument("--rep-desde", type=int, default=1, help="primera repetición a correr (las anteriores se saltean); con --destino de una corrida previa, agrega repeticiones sin tocar las hechas")
    ap.add_argument("--modelos", nargs="*", help="ids de modelos.json; por defecto todos")
    ap.add_argument("--etiqueta", default="corrida")
    ap.add_argument("--salida", default=str(SALIDA_DEFECTO), help="carpeta base de las corridas")
    ap.add_argument("--destino", help="carpeta de una corrida anterior (relativa a --salida) para reanudar")
    ap.add_argument("--max-tokens", type=int, default=None, help="tope por respuesta (por defecto, ninguno)")
    ap.add_argument("--tope-usd", type=float, default=None, help="corta si lo gastado en esta sesión lo supera")
    ap.add_argument("--permitir-icloud", action="store_true", help="permite guardar dentro de iCloud (no recomendado)")
    ap.add_argument("--piloto", action="store_true", help="saltea aprobado_por_jlr; exige --reps 1 y una sola pregunta")
    ap.add_argument("--desde", help="carpeta de una corrida anterior (solo lectura): reutiliza sus turnos 1 y 2 y corre solo el turno 3")
    ap.add_argument("--consignas", default="consignas.json", help="archivo de consignas en Pruebas/ (variantes de piloto)")
    ap.add_argument("--solo-turno1", action="store_true", help="corre solo la consulta inicial (pruebas de redacción de la consulta)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.solo_turno1 and a.desde:
        sys.exit("--solo-turno1 y --desde son incompatibles.")

    crudo_consignas = (AQUI / a.consignas).read_bytes()
    crudo_modelos = (AQUI / "modelos.json").read_bytes()
    cfg = json.loads(crudo_consignas)
    cfg_modelos = json.loads(crudo_modelos)
    consignas = cfg["casos"][a.caso]

    por_id = {m["id"]: m for m in cfg_modelos["modelos"]}
    ids = a.modelos or list(por_id)
    for i in ids:
        if i not in por_id or ":" in i:
            sys.exit(f"Modelo fuera de modelos.json o con sufijo: {i}")
        if not por_id[i].get("proveedor"):
            sys.exit(f"Falta el proveedor de {i} en modelos.json")
        if not por_id[i].get("esfuerzo"):
            sys.exit(f"Falta el esfuerzo de {i} en modelos.json")
        if i not in ACEPTADOS:
            sys.exit(f"Falta {i} en ACEPTADOS (lista de ids y proveedores aceptados, en correr.py)")
    for p in a.preguntas:
        if p not in consignas["preguntas"]:
            sys.exit(f"Pregunta desconocida: {p}")
    # Repreguntas (opcional): {"p1": "texto"}; la clave debe ser una pregunta del caso y el texto no puede estar vacío.
    repreguntas = consignas.get("repreguntas") or {}
    for p, t in repreguntas.items():
        if p not in consignas["preguntas"] or not isinstance(t, str) or not t.strip():
            sys.exit(f"Repregunta inválida en consignas.json: {p}")
    con_repregunta = [p for p in a.preguntas if p in repreguntas]
    desde = Path(a.desde).expanduser().resolve() if a.desde else None
    fuentes = {}  # (modelo, rep, pregunta) -> (registro guardado, sha256 del archivo), solo con --desde
    if desde:
        if not desde.is_dir():
            sys.exit(f"--desde: no existe la carpeta {desde}")
        errores = [f"sin repregunta en consignas.json: {p}" for p in a.preguntas if p not in repreguntas]
        if not errores:
            for i in ids:
                for rep in range(a.rep_desde, a.reps + 1):
                    for p in a.preguntas:
                        try:
                            fuentes[(i, rep, p)] = leer_fuente(desde, a.caso, i, rep, p, consignas, por_id[i])
                        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as e:
                            errores.append(f"{i} r{rep} {p}: {e}")
        if errores:
            sys.exit("--desde abortado, no se llamó a la API:\n  " + "\n  ".join(errores))

    n = len(ids) * (a.reps - a.rep_desde + 1) * len(a.preguntas)
    print(f"{a.caso}: {len(ids)} modelos x {a.reps} reps x {len(a.preguntas)} preguntas = {n} conversaciones")
    for i in ids:
        print(f"  {i}  proveedor={por_id[i]['proveedor']}  esfuerzo={por_id[i]['esfuerzo']}  estado={por_id[i]['estado']}")
    if a.dry_run:
        reutil = " (reutilizado de --desde)" if desde else ""
        print(f"\n[dry-run] Turno 1{reutil}:", consignas["consulta"])
        for p in a.preguntas:
            print(f"[dry-run] Turno 2 ({p}){reutil}:", consignas["preguntas"][p])
            if p in repreguntas:
                print(f"[dry-run] Turno 3 ({p}):", repreguntas[p])
        if desde:
            print(f"\n[dry-run] Retoma desde {desde} (solo lectura); verificado contra consignas.json y modelos.json:")
            for (i, rep, p), (d, h) in fuentes.items():
                print(f"  {i} r{rep} {p}: ids turno 1 / turno 2 = {d['id_turno1']} / {d['id_turno2']}  sha256={h[:12]}")
        print(f"\n[dry-run] aprobado_por_jlr={cfg.get('aprobado_por_jlr')!r}; "
              f"modelos no aprobados: {[i for i in ids if por_id[i]['estado'] != 'aprobado']}")
        return

    if a.piloto and (a.reps != 1 or len(a.preguntas) != 1):
        sys.exit("--piloto exige --reps 1 y una sola pregunta.")
    if cfg.get("aprobado_por_jlr") is not True and not a.piloto:
        sys.exit("Bloqueado: consignas.json no tiene aprobado_por_jlr = true. Solo se permite --dry-run o --piloto.")
    sin_aprobar = [i for i in ids if por_id[i]["estado"] != "aprobado"]
    if sin_aprobar:
        sys.exit(f"Bloqueado: modelos no aprobados en modelos.json: {sin_aprobar}")
    clave = os.environ.get("OPENROUTER_API_KEY")
    if not clave:
        sys.exit("Falta OPENROUTER_API_KEY")

    base = Path(a.salida).expanduser()
    destino = (base / a.destino) if a.destino else base / f"{datetime.now(timezone.utc):%Y%m%d-%H%M}-{a.etiqueta}"
    if "Mobile Documents" in str(destino.resolve()) and not a.permitir_icloud:
        sys.exit("El destino está dentro de iCloud: la reanudación puede fallar con archivos descargados a medias. Usá otra --salida.")
    if desde and (destino.resolve() == desde or desde in destino.resolve().parents):
        sys.exit("El destino no puede ser la carpeta de --desde ni estar dentro de ella: la carpeta de origen no se modifica.")
    destino.mkdir(parents=True, exist_ok=True)

    sha_consignas, sha_modelos = sha(crudo_consignas), sha(crudo_modelos)
    ruta_manifiesto = destino / "manifiesto.json"
    if ruta_manifiesto.exists():
        manifiesto = json.loads(ruta_manifiesto.read_text(encoding="utf-8"))
        if (manifiesto["sha256_consignas"], manifiesto["sha256_modelos"], manifiesto["max_tokens"]) != (sha_consignas, sha_modelos, a.max_tokens):
            sys.exit("Reanudación abortada: consignas.json, modelos.json o --max-tokens cambiaron desde que se creó esta corrida.")
        if (manifiesto.get("desde") or {}).get("carpeta") != (str(desde) if desde else None):
            sys.exit("Reanudación abortada: --desde no coincide con el de la corrida original.")
    else:
        manifiesto = {
            "creado_utc": ahora(), "sha256_consignas": sha_consignas, "sha256_modelos": sha_modelos,
            "max_tokens": a.max_tokens, "consignas": cfg, "modelos_json": cfg_modelos,
            "python": platform.python_version(),
            "declaraciones": {
                "cuerpo_enviado": "model, messages, reasoning.effort=[esfuerzo de modelos.json], usage.include=true, provider.order=[proveedor de modelos.json], provider.allow_fallbacks=false; max_tokens solo si se pasó (si no, el máximo del modelo, como en AA). Sin temperatura ni búsqueda web.",
                "turno2": "Reenvía solo el content de la primera respuesta, no su razonamiento, como una interfaz de chat. Las cuatro preguntas de una misma repetición parten del mismo turno 1 guardado (-turno1.json).",
                "fallas": "Toda terminación distinta de 'stop', y toda respuesta de un modelo distinto del pedido (fallback ante un rechazo), se guarda como ERROR con marca de tiempo y no se usa; los reemplazos son corridas nuevas con --destino y las fallas quedan en la carpeta.",
            },
            "sesiones": [],
        }
        if a.solo_turno1:
            manifiesto["declaraciones"]["solo_turno1"] = (
                f"Prueba de redacción de la consulta: solo se corrió el turno 1, con las consignas de {a.consignas}. "
                "No hay turnos 2 ni 3.")
        elif con_repregunta:
            manifiesto["declaraciones"]["turno3"] = (
                "En las preguntas con repregunta en consignas.json, la conversación sigue con un turno 3: consulta, content de la "
                "respuesta 1, pregunta, content de la respuesta 2, repregunta. Solo se reenvía el content, nunca el razonamiento. "
                "Se aplican al turno 3 los mismos criterios de falla, de modelo respondido, de reintentos y de tope de gasto que al turno 2. "
                "La respuesta del turno 2 se guarda aparte (-turno2.json) para reanudar una falla del turno 3 sin rehacer el turno 2. "
                "Si el turno 2 falla, no se corre el turno 3.")
        if desde:
            manifiesto["declaraciones"]["desde"] = (
                "Los turnos 1 y 2 no se corrieron en esta carpeta: se reutilizan, sin cambios, de las conversaciones guardadas en la "
                "carpeta de origen (solo lectura), tras verificar que la consulta y la pregunta coinciden literalmente con consignas.json "
                "actual y que el modelo, el proveedor y el esfuerzo coinciden con modelos.json. Solo se corrió el turno 3.")
            manifiesto["desde"] = {
                "carpeta": str(desde),
                "conversaciones": [
                    {"modelo": i, "repeticion": rep, "pregunta": p, "archivo": f"{a.caso}-{i.replace('/', '_')}-r{rep}-{p}.json",
                     "sha256_archivo": h, "id_turno1": d["id_turno1"], "id_turno2": d["id_turno2"],
                     "fecha_utc": d.get("fecha_utc"), "sha256_consignas": d.get("sha256_consignas")}
                    for (i, rep, p), (d, h) in fuentes.items()],
            }
    saldo_ini = saldo(clave)
    print(f"Saldo inicial: {saldo_ini:.2f} USD. Salida: {destino}")
    sesion = {
        "inicio_utc": ahora(), "argumentos": vars(a), "sha256_script": sha(Path(__file__).read_bytes()),
        "saldo_inicial_usd": saldo_ini, "aprobado_por_jlr": cfg.get("aprobado_por_jlr") is True,
        "piloto_sin_aprobacion_jlr": a.piloto and cfg.get("aprobado_por_jlr") is not True,
        "estados_modelos": {i: por_id[i]["estado"] for i in ids},
        "esfuerzos": {i: por_id[i]["esfuerzo"] for i in ids},
    }
    manifiesto["sesiones"].append(sesion)
    volcar(ruta_manifiesto, manifiesto)

    gastado = [0.0]

    def cobrar(g):
        gastado[0] += g

    def revisar_tope():
        if a.tope_usd and gastado[0] > a.tope_usd:
            raise Tope(f"Tope de {a.tope_usd} USD superado; corrida cortada. Se reanuda con --destino {destino.name}")

    def guardar_error(nombre, contenido):
        volcar(destino / f"{nombre}-ERROR-{marca()}.json", contenido)
        print(f"  ERROR {nombre}")

    def cuerpo_de(modelo, mensajes):
        c = {"model": modelo, "messages": mensajes, "reasoning": {"effort": por_id[modelo]["esfuerzo"]}, "usage": {"include": True},
             "provider": {"order": [por_id[modelo]["proveedor"]], "allow_fallbacks": False}}
        if a.max_tokens:
            c["max_tokens"] = a.max_tokens
        return c

    terminacion_sesion = "completa"
    try:
        for modelo in ids:
            slug = modelo.replace("/", "_")
            for rep in range(a.rep_desde, a.reps + 1):
                pendientes = [p for p in a.preguntas if not (destino / f"{a.caso}-{slug}-r{rep}-{p}.json").exists()]
                if a.solo_turno1:
                    pendientes = [] if (destino / f"{a.caso}-{slug}-r{rep}-turno1.json").exists() else ["turno1"]
                if not pendientes:
                    continue
                m1 = [{"role": "user", "content": consignas["consulta"]}]
                if not desde:
                    ruta_t1 = destino / f"{a.caso}-{slug}-r{rep}-turno1.json"
                    if ruta_t1.exists():
                        r1 = json.loads(ruta_t1.read_text(encoding="utf-8"))["respuesta"]
                    else:
                        r1, int1, g = llamar(clave, cuerpo_de(modelo, m1))
                        cobrar(g)
                        if texto(r1) is None or terminacion(r1) != "stop" or modelo_distinto(modelo, r1):
                            guardar_error(f"{a.caso}-{slug}-r{rep}-turno1", {"respuesta": r1, "intentos": int1})
                            revisar_tope()
                            continue
                        gen1 = generacion(clave, r1.get("id"))
                        volcar(ruta_t1, {"fecha_utc": ahora(), "cuerpo": cuerpo_de(modelo, m1), "respuesta": r1, "intentos": int1,
                                         "generacion": gen1,
                                         "snapshot_coincide": (gen1 or {}).get("model") == SNAPSHOTS.get(modelo) if gen1 else None})
                        revisar_tope()
                    t1 = texto(r1)
                    if a.solo_turno1:
                        escribir(destino / f"{a.caso}-{slug}-r{rep}-turno1.md",
                            f"**Modelo pedido:** {modelo}  \n**Esfuerzo:** {por_id[modelo]['esfuerzo']}  \n"
                            f"**Respondió:** {r1.get('model')} / {r1.get('provider')}  \n**Id:** {r1.get('id')}  \n"
                            f"**Tokens de razonamiento:** {tokens_razonamiento(r1)}  \n**Fecha (UTC):** {ahora()}\n\n"
                            f"**Consulta inicial**\n\n{consignas['consulta']}\n\n**Respuesta**\n\n{t1}\n")
                        print(f"  ok {a.caso}-{slug}-r{rep}-turno1  (acumulado {gastado[0]:.3f} USD)")
                        continue
                for p in pendientes:
                    base_nombre = f"{a.caso}-{slug}-r{rep}-{p}"
                    repregunta = repreguntas.get(p)
                    ruta_t2 = destino / f"{base_nombre}-turno2.json"
                    if desde:
                        # Turnos 1 y 2 tomados tal cual de la conversación guardada (ya verificada al arrancar).
                        fuente = fuentes[(modelo, rep, p)][0]
                        r1, r2 = fuente["respuesta_turno1"], fuente["respuesta_turno2"]
                        t1, t2 = texto(r1), texto(r2)
                        m2 = m1 + [{"role": "assistant", "content": t1}, {"role": "user", "content": consignas["preguntas"][p]}]
                        cuerpo2, int2, gen2 = fuente["cuerpo_turno2"], fuente.get("intentos_turno2", []), fuente.get("generacion_turno2")
                        fecha = ahora()
                    elif repregunta and ruta_t2.exists():
                        # Reanudación: el turno 2 ya se corrió y se guardó; solo falta el turno 3.
                        d2 = json.loads(ruta_t2.read_text(encoding="utf-8"))
                        r2, cuerpo2, int2, gen2 = d2["respuesta"], d2["cuerpo"], d2["intentos"], d2["generacion"]
                        t2 = texto(r2)
                        m2 = m1 + [{"role": "assistant", "content": t1}, {"role": "user", "content": consignas["preguntas"][p]}]
                        fecha = ahora()
                    else:
                        m2 = m1 + [{"role": "assistant", "content": t1}, {"role": "user", "content": consignas["preguntas"][p]}]
                        r2, int2, g = llamar(clave, cuerpo_de(modelo, m2))
                        cobrar(g)
                        t2 = texto(r2)
                        if t2 is None or terminacion(r2) != "stop" or modelo_distinto(modelo, r2):
                            guardar_error(base_nombre, {"id_turno1": r1.get("id"), "respuesta": r2, "intentos": int2})
                            revisar_tope()
                            continue
                        fecha = ahora()
                        gen2 = generacion(clave, r2.get("id"))
                        cuerpo2 = cuerpo_de(modelo, m2)
                        if repregunta:
                            volcar(ruta_t2, {"fecha_utc": ahora(), "cuerpo": cuerpo2, "respuesta": r2, "intentos": int2, "generacion": gen2})
                            revisar_tope()
                    r3 = None
                    if repregunta:
                        m3 = m2 + [{"role": "assistant", "content": t2}, {"role": "user", "content": repregunta}]
                        r3, int3, g = llamar(clave, cuerpo_de(modelo, m3))
                        cobrar(g)
                        t3 = texto(r3)
                        if t3 is None or terminacion(r3) != "stop" or modelo_distinto(modelo, r3):
                            guardar_error(f"{base_nombre}-turno3", {"id_turno1": r1.get("id"), "id_turno2": r2.get("id"),
                                                                   "respuesta": r3, "intentos": int3})
                            revisar_tope()
                            continue
                        fecha = ahora()
                        gen3 = generacion(clave, r3.get("id"))
                    rs = [r1, r2] + ([r3] if r3 else [])
                    registro = {
                        "caso": a.caso, "pregunta": p, "repeticion": rep, "modelo_pedido": modelo,
                        "proveedor_pedido": por_id[modelo]["proveedor"], "esfuerzo": por_id[modelo]["esfuerzo"],
                        "modelo_respondido": [r.get("model") for r in rs],
                        "proveedor_respondio": [r.get("provider") for r in rs],
                        "finish_reason": [terminacion(r) for r in rs],
                        "id_turno1": r1.get("id"), "id_turno2": r2.get("id"),
                        "fecha_utc": fecha, "sha256_consignas": sha_consignas,
                        "cuerpo_turno2": cuerpo2,
                        "respuesta_turno1": r1, "respuesta_turno2": r2,
                        "intentos_turno2": int2, "generacion_turno2": gen2,
                        "snapshot_coincide_turno2": (gen2.get("model") == SNAPSHOTS.get(modelo)) if gen2 else None,
                    }
                    if r3:
                        registro.update({
                            "id_turno3": r3.get("id"), "cuerpo_turno3": cuerpo_de(modelo, m3), "respuesta_turno3": r3,
                            "intentos_turno3": int3, "generacion_turno3": gen3,
                            "snapshot_coincide_turno3": (gen3.get("model") == SNAPSHOTS.get(modelo)) if gen3 else None,
                        })
                    if desde:
                        d, h = fuentes[(modelo, rep, p)]
                        registro["desde"] = {"carpeta": str(desde), "archivo": f"{base_nombre}.json", "sha256_archivo": h,
                                             "fecha_utc": d.get("fecha_utc"), "sha256_consignas": d.get("sha256_consignas")}
                    ids_turnos = " / ".join(str(r.get("id")) for r in rs)
                    tokens = " / ".join(str(tokens_razonamiento(r)) for r in rs)
                    escribir(destino / f"{base_nombre}.md",
                        f"**Modelo pedido:** {modelo}  \n**Proveedor pedido:** {registro['proveedor_pedido']}  \n**Esfuerzo:** {registro['esfuerzo']}  \n"
                        f"**Respondió:** {registro['modelo_respondido']} / {registro['proveedor_respondio']}  \n"
                        f"**Ids:** {ids_turnos}  \n"
                        f"**Tokens de razonamiento:** {tokens}  \n"
                        + (f"**Turnos 1 y 2 reutilizados de:** {desde}  \n" if desde else "") +
                        f"**Fecha (UTC):** {fecha}\n\n"
                        f"**Consulta inicial**\n\n{consignas['consulta']}\n\n**Respuesta**\n\n{t1}\n\n"
                        f"**Pregunta {p}**\n\n{consignas['preguntas'][p]}\n\n**Respuesta**\n\n{t2}\n"
                        + (f"\n**Repregunta {p}**\n\n{repregunta}\n\n**Respuesta**\n\n{t3}\n" if r3 else ""))
                    volcar(destino / f"{base_nombre}.json", registro)
                    print(f"  ok {base_nombre}  (acumulado {gastado[0]:.3f} USD)")
                    revisar_tope()
    except Tope as e:
        terminacion_sesion = str(e)
        print(e)
    except KeyboardInterrupt:
        terminacion_sesion = "interrumpida"
        print("Interrumpida; se puede reanudar con --destino", destino.name)
    finally:
        try:
            fin = saldo(clave)
        except Exception:
            fin = None
        sesion.update({"fin_utc": ahora(), "terminacion": terminacion_sesion, "saldo_final_usd": fin,
                       "gastado_respuestas_usd": gastado[0],
                       "diferencia_saldo_usd": (saldo_ini - fin) if fin is not None else None})
        volcar(ruta_manifiesto, manifiesto)
        print(f"Gastado según respuestas: {gastado[0]:.3f} USD. Saldo final: {fin}. Salida: {destino}")


if __name__ == "__main__":
    main()
