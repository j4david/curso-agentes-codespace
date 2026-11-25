"""Pasar una alerta por el grafo y verlo paso a paso.

Uso (desde esta carpeta):
  uv run python triaje.py 0501          la alerta ALT-0501 (también 0502, 0503, 0504 y 0505)
  uv run python triaje.py 0504 mensajes además, la conversación entera con el modelo

Si la propuesta necesita a una persona, el grafo se PARA y te pregunta.
Nada se ejecuta: solo se propone.
"""

import json
import sys

from langgraph.types import Command

from datos import ALERTAS
from grafo import construir

grafo = construir()


def recorrer(entrada, config):
    for paso in grafo.stream(entrada, config, stream_mode="updates"):
        for nodo, cambios in paso.items():
            if nodo != "__interrupt__":
                for linea in (cambios or {}).get("registro", []):
                    print(f"  · {linea}")


def main(n: str, ver_mensajes: bool):
    alerta = next((a for a in ALERTAS if a["alerta_id"] == f"ALT-{n.zfill(4)}"), None)
    if not alerta:
        sys.exit(f"No existe la alerta ALT-{n}. Hay: {', '.join(a['alerta_id'] for a in ALERTAS)}")
    print(f"{alerta['alerta_id']} · {alerta['sistema']}\n  «{alerta['texto_alerta']}»\n")
    config = {"configurable": {"thread_id": alerta["alerta_id"]}}
    recorrer({"alerta": alerta}, config)

    estado = grafo.get_state(config)
    if estado.interrupts:
        v = estado.interrupts[0].value
        print("\nEL GRAFO ESTÁ PARADO esperando a una persona.")
        print("Motivos: " + "; ".join(v["motivos"]))
        print(json.dumps(v["propuesta"], ensure_ascii=False, indent=2))
        decision = ""
        while decision not in ("aprobar", "rechazar"):
            decision = input("\n¿aprobar o rechazar? ").strip().lower()
        revisor = input("Tu nombre (ficticio): ").strip() or "Sin nombre"
        recorrer(Command(resume={"decision": decision, "revisor": revisor}), config)

    final = grafo.get_state(config).values
    print("\nComprobaciones del código:")
    for c in final.get("comprobaciones", []):
        print(f"  {'BIEN ' if c['ok'] else 'FALLA'} {c['texto']}")
    print(f"\nFIN. {final.get('estado')}")
    if ver_mensajes:
        print("\nLa conversación con el modelo:")
        for m in final["mensajes"]:
            print(f"\n--- {m.type}\n{(str(m.text) or str(getattr(m, 'tool_calls', '')))[:600]}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
    else:
        main(sys.argv[1], "mensajes" in sys.argv[2:])
