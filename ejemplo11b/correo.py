"""Un correo por el grafo, paso a paso.

Enseña el correo, lo que va apuntando cada nodo y adónde acaba.

Uso: uv run python correo.py 14
"""

import json
import sys

import grafo

numero = (sys.argv[1] if len(sys.argv) > 1 else "14").zfill(2)
correo = next(c for c in json.load(open("correos.json", encoding="utf-8")) if c["id"] == numero)

como = grafo.como_opina()
print(f"Nube: {como['nube']}   Local: {como['local']}\n")
print(f"Correo {numero} · {correo['asunto']}\n{correo['cuerpo'][:300]}{'…' if len(correo['cuerpo']) > 300 else ''}\n")

# stream enseña el estado después de cada paso; las dos opiniones salen en el mismo paso.
for paso in grafo.construir().stream({"correo": correo}, stream_mode="updates"):
    for nodo, cambios in paso.items():
        for linea in cambios.get("registro", []):
            print(f"  [{nodo}] {linea}")
