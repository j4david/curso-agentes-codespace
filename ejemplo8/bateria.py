"""La batería: el nodo «clasificar», solo, con los 30 correos.

Compara la categoría y «¿requiere persona?» con las respuestas correctas
(bateria.csv) y dice por qué camino iría cada correo.
Con la clave gratuita tarda unos 3 minutos (12 peticiones por minuto).

Uso: uv run python bateria.py            (los 30)
     uv run python bateria.py 04 09 10   (solo esos)
"""

import csv
import json
import sys
import time

from grafo import clasificar, elegir_camino

correos = json.load(open("correos.json", encoding="utf-8"))
correctas = {f["id"]: f for f in csv.DictReader(open("bateria.csv", encoding="utf-8"))}
elegidos = [n.zfill(2) for n in sys.argv[1:]] or [c["id"] for c in correos]

filas, bien_cat, bien_per = [], 0, 0
inicio = time.time()
for c in correos:
    if c["id"] not in elegidos:
        continue
    r = clasificar({"correo": c})
    ok = correctas[c["id"]]
    per_ok = "sí" if ok["requiere_persona"] == "sí" else "no"
    per = "sí" if r["requiere_persona"] else "no"
    cat_bien, per_bien = r["categoria"] == ok["categoria"], per == per_ok
    bien_cat += cat_bien
    bien_per += per_bien
    camino = elegir_camino(r)
    marca = "" if cat_bien and per_bien else "   <-- revisar"
    print(f"{c['id']}  {r['categoria']:<27} persona={per:<2}  camino={camino:<11}{marca}")
    filas.append({"id": c["id"], "categoria": r["categoria"], "categoria_correcta": ok["categoria"],
                  "requiere_persona": per, "requiere_persona_correcto": per_ok, "camino": camino,
                  "pregunta_para_persona": r["pregunta_para_persona"], "motivo": r["motivo"]})

n = len(filas)
print(f"\nCategoría: {bien_cat}/{n}   ¿Requiere persona?: {bien_per}/{n}   "
      f"Tiempo: {int(time.time() - inicio)} s")
with open("resultado_bateria.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(filas[0]))
    w.writeheader()
    w.writerows(filas)
print("Detalle en resultado_bateria.csv")
