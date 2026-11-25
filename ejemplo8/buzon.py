"""Pasar correos por el grafo, revisar, corregir y volver atrás.

Uso (desde esta carpeta):
  uv run python buzon.py ver 09                     pasa el correo 09 por el grafo
  uv run python buzon.py seguir 09 aprobar          aprueba el borrador
  uv run python buzon.py seguir 09 descartar        lo descarta
  uv run python buzon.py seguir 09 corregir subsanacion   corrige la categoría
  uv run python buzon.py seguir 09 responder cita_previa  responde a «pedir ayuda»
  uv run python buzon.py ficha 09                   enseña la ficha guardada
  uv run python buzon.py historia 09                los pasos guardados, numerados
  uv run python buzon.py volver 09 3                vuelve al paso 3 y sigue desde ahí

Cada correo tiene su HILO («correo-09»). Lo que pasa en un hilo no lo sabe otro.
"""

import json
import sys

from langgraph.types import Command

from grafo import construir

CORREOS = {c["id"]: c for c in json.load(open("correos.json", encoding="utf-8"))}
grafo = construir()


def hilo(n: str) -> dict:
    return {"configurable": {"thread_id": f"correo-{n}"}}


def recorrer(entrada, config):
    """Ejecuta el grafo y enseña cada paso según ocurre."""
    for paso in grafo.stream(entrada, config, stream_mode="updates"):
        for nodo, cambios in paso.items():
            if nodo == "__interrupt__":
                continue
            for linea in (cambios or {}).get("registro", []):
                print(f"  · {linea}")
    estado = grafo.get_state(config)
    if estado.interrupts:
        print("\nEL GRAFO ESTÁ PARADO esperando a una persona:")
        print(json.dumps(estado.interrupts[0].value, ensure_ascii=False, indent=2))
        print("\nPara seguir: uv run python buzon.py seguir <n.º> aprobar | descartar | corregir <categoría>"
              " | responder <categoría>")
    else:
        print(f"\nFIN. Destino: {estado.values.get('destino')}")


def main(args):
    orden, n = args[0], args[1].zfill(2)
    config = hilo(n)
    if orden == "ver":
        print(f"Correo {n}: {CORREOS[n]['asunto']}")
        recorrer({"correo": CORREOS[n], "registro": []}, config)
    elif orden == "seguir":
        que = args[2]
        if que == "responder":
            respuesta = args[3]
        elif que == "corregir":
            respuesta = {"decision": "corregir", "categoria": args[3]}
        else:
            respuesta = {"decision": que}
        recorrer(Command(resume=respuesta), config)
    elif orden == "ficha":
        valores = dict(grafo.get_state(config).values)
        valores.pop("correo", None)
        print(json.dumps(valores, ensure_ascii=False, indent=2))
    elif orden == "historia":
        pasos = list(grafo.get_state_history(config))[::-1]   # del primero al último
        for i, p in enumerate(pasos):
            siguiente = ", ".join(p.next) or "(fin)"
            print(f"{i:>2}. siguiente: {siguiente:<12} categoría: {p.values.get('categoria', '-')}")
    elif orden == "volver":
        pasos = list(grafo.get_state_history(config))[::-1]
        p = pasos[int(args[2])]
        print(f"Vuelvo al paso {args[2]} (siguiente: {', '.join(p.next)}) y sigo desde ahí.")
        recorrer(None, p.config)
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:]) if len(sys.argv) > 2 else print(__doc__)
