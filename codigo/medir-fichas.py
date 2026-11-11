#!/usr/bin/env python3
"""Mide cuánto texto quedaría en una ficha de decisión, por tanda.

Solo imprime recuentos de palabras. No imprime texto de las respuestas
y no abre la clave ni los controles del armado.
"""
import re
import statistics as st
from pathlib import Path

LECTURA = Path(__file__).parent / "Lectura"

DECISION = re.compile(
    r"\b(mantengo|mantendr|mantiene|sostengo|confirmo|ratifico|modific|cambi[aoó]|"
    r"revoc|absuelv|absolv|conden[oóaé]|reconsider|rectific|corrij|dejo sin efecto)",
    re.I,
)
MARCAS = re.compile(
    r"(ten[eé]s razón|es cierto|debo reconocer|reconozco|omit[ií]|imprecis|"
    r"en subsidio|alternativ|si se entendiera|en caso de que|si en cambio|"
    r"objeci[oó]n|cr[ií]tica|me plante[aá]s|señal[aá]s)",
    re.I,
)


def palabras(t):
    return len(t.split())


def oraciones(parrafo):
    return re.split(r"(?<=[.;:?!])\s+", parrafo)


def ficha(texto, con_marcas=True):
    """Devuelve (palabras de apertura y cierre, palabras de la ficha completa)."""
    ps = [p.strip() for p in re.split(r"\n\s*\n", texto) if p.strip()]
    if not ps:
        return 0, 0
    ini, fin = [0], [len(ps) - 1]
    if palabras(ps[0]) < 30 and len(ps) > 1:
        ini.append(1)
    if palabras(ps[-1]) < 30 and len(ps) > 2:
        fin.append(len(ps) - 2)
    fijos = set(ini + fin)
    base = sum(palabras(ps[i]) for i in fijos)
    extra = 0
    for i, p in enumerate(ps):
        if i in fijos:
            continue
        for o in oraciones(p):
            if DECISION.search(o) or (con_marcas and MARCAS.search(o)):
                extra += palabras(o)
    return base, base + extra


def partes(md):
    """Separa cada conversación en sus turnos, por los rótulos de la tanda."""
    bloques = re.split(r"\*\*Código [A-Z0-9]+\*\* \(\d+ de \d+\)", md)[1:]
    out = []
    for b in bloques:
        b = re.split(r"\n---\s*\n", b)[0]
        trozos = re.split(
            r"\*\*(Primera respuesta|Respuesta a la pregunta|Respuesta a la repregunta)\*\*",
            b,
        )
        d = {trozos[i]: trozos[i + 1] for i in range(1, len(trozos) - 1, 2)}
        out.append(d)
    return out


def main():
    print("tanda | n | turno | palabras | apertura+cierre | ficha | mediana ficha")
    tot = {}
    for f in sorted(LECTURA.glob("Tanda *.md")):
        convs = partes(f.read_text(encoding="utf-8"))
        for turno in ("Respuesta a la pregunta", "Respuesta a la repregunta"):
            textos = [c[turno] for c in convs if turno in c]
            if not textos:
                continue
            w = sum(palabras(t) for t in textos)
            fs = [ficha(t) for t in textos]
            base = sum(x[0] for x in fs)
            comp = sum(x[1] for x in fs)
            med = st.median(x[1] for x in fs)
            nombre = f.stem.replace("Tanda ", "T")
            print(f"{nombre} | {len(textos)} | {turno[13:]} | {w} | {base} | {comp} | {med}")
            tot[(nombre, turno)] = (w, base, comp)
    print("total palabras", sum(v[0] for v in tot.values()))
    print("total apertura+cierre", sum(v[1] for v in tot.values()))
    print("total ficha", sum(v[2] for v in tot.values()))


if __name__ == "__main__":
    main()
