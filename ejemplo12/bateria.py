"""La batería: varias preguntas de preguntas.csv por el grafo.

Guarda, para cada una, el camino, las reescrituras, la respuesta y la respuesta correcta,
para comparar a mano (resultado_bateria.csv). Cada pregunta gasta de 5 a 8 peticiones:
con la clave gratuita, unos 30 s por pregunta.

Uso: uv run python bateria.py C1 C6 K1 N1 J10    (las que digas)
     uv run python bateria.py todas              (las 24: unos 12 minutos)
"""

import csv
import sys
import time

from preguntar import preguntar

filas_ref = list(csv.DictReader(open("preguntas.csv", encoding="utf-8")))
elegidas = [f for f in filas_ref if sys.argv[1:] == ["todas"] or f["id"] in sys.argv[1:]]

salida = []
for f in elegidas:
    t = time.time()
    r = preguntar(f["pregunta"], ver=False)
    camino = " > ".join(l.split(":")[0].split(" ")[0] for l in r.get("registro", []))
    print(f"{f['id']:<4} {r.get('destino', ''):<18} reescrituras={r.get('reescrituras', 0)}  "
          f"{int(time.time() - t)} s")
    salida.append({"id": f["id"], "destino": r.get("destino"), "reescrituras": r.get("reescrituras", 0),
                   "registro": " | ".join(r.get("registro", [])), "respuesta": r.get("respuesta"),
                   "respuesta_correcta": f["respuesta_correcta"]})

with open("resultado_bateria.csv", "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(salida[0]))
    w.writeheader()
    w.writerows(salida)
print("Detalle en resultado_bateria.csv")
