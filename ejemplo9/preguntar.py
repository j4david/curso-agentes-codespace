"""Preguntar a las actas por código de preguntas.csv o con una pregunta entre comillas."""

import argparse
import csv

from grafo import construir, generar, recuperar

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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pregunta", nargs="+")
    parser.add_argument("--simple", action="store_true",
                        help="Recupera los pasajes una vez y encarga al modelo que responda.")
    args = parser.parse_args()
    entrada = " ".join(args.pregunta)
    p = PREGUNTAS.get(entrada, entrada)
    print(f"Pregunta: {p}\n")
    if args.simple:
        recuperacion = recuperar({"busqueda": p})
        print(f"  · {recuperacion['registro'][0]}")
        respuesta = generar({"pregunta": p, "utiles": recuperacion["pasajes"]})
        print(f"\n[RAG simple]\n{respuesta['respuesta']}")
    else:
        r = preguntar(p)
        print(f"\n[{r.get('destino')}]\n{r.get('respuesta')}")
