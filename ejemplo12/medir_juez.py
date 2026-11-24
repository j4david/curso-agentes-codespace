"""¿Nos fiamos del juez? Lo medimos con 10 pasajes que ya sabemos si sirven o no.

pasajes_etiquetados.json: pregunta, pasaje, «sirve» (la respuesta correcta) y por qué.
El juez es el nodo «calificar» del grafo, con sus instrucciones (INSTRUCCIONES_JUEZ en grafo.py).
Gasta 10 peticiones: unos 50 s.

Uso: uv run python medir_juez.py
"""

import json

from grafo import calificar

casos = json.load(open("pasajes_etiquetados.json", encoding="utf-8"))
bien = 0
dejo_pasar_malos = 0
for c in casos:
    r = calificar({"pregunta": c["pregunta"], "pasajes": [c]})
    dice = bool(r["utiles"])
    ok = dice == c["sirve"]
    bien += ok
    dejo_pasar_malos += dice and not c["sirve"]
    print(f"{c['id']}  correcto={'sí' if c['sirve'] else 'no'}  juez={'sí' if dice else 'no'}  "
          f"{'BIEN' if ok else 'FALLA: ' + c['por_que']}")

print(f"\nAciertos del juez: {bien} de {len(casos)}. "
      f"Pasajes que no sirven y dejó pasar: {dejo_pasar_malos}.")
