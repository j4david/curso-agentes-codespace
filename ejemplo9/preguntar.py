"""Hacer una pregunta a las actas y ver el registro del grafo paso a paso.

Uso: uv run python preguntar.py "¿Cuál es el límite de tamaño de los adjuntos?"
     uv run python preguntar.py K1          (una pregunta de preguntas.csv por su código)
"""

import csv
import sys

from grafo import construir

PREGUNTAS = {f["id"]: f["pregunta"] for f in csv.DictReader(open("preguntas.csv", encoding="utf-8"))}


def preguntar(pregunta: str, ver=True) -> dict:
    final = {}
    for paso in construir().stream({"pregunta": pregunta, "registro": []}, stream_mode="updates"):
        for nodo, cambios in paso.items():
            for linea in (cambios or {}).get("registro", []):
                if ver:
                    print(f"  · {linea}")
            cambios = dict(cambios or {})
            registro = final.get("registro", []) + cambios.pop("registro", [])
            final.update(cambios, registro=registro)
    return final


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit
    p = PREGUNTAS.get(sys.argv[1], " ".join(sys.argv[1:]))
    print(f"Pregunta: {p}\n")
    r = preguntar(p)
    print(f"\n[{r.get('destino')}]\n{r.get('respuesta')}")
