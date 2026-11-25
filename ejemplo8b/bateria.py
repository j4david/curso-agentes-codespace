"""La batería: los correos por el grafo, y la cuenta de lo que pasa.

Para cada correo dice qué opinó cada modelo y adónde fue. Al final cuenta:
- en cuántos coinciden y cuántos de esos están bien;
- cuántos van a una persona y cuántos errores de cada modelo caza la persona.

Uso: uv run python bateria.py              (los 30)
     uv run python bateria.py 10 12 14     (solo esos)
Con el modelo local en directo tarda unos 7 s por correo.
"""

import csv
import json
import sys
import time

import grafo

GRABAR = "--grabar" in sys.argv   # guarda estas opiniones en grabadas/ (sustituye las que hay)
numeros = [a.zfill(2) for a in sys.argv[1:] if not a.startswith("--")]

correos = json.load(open("correos.json", encoding="utf-8"))
correctas = {f["id"]: f["categoria"] for f in csv.DictReader(open("bateria.csv", encoding="utf-8"))}
elegidos = [c for c in correos if not numeros or c["id"] in numeros]

como = grafo.como_opina()
print(f"Nube: {como['nube']}   Local: {como['local']}   Umbral del local: {grafo.UMBRAL_LOCAL}\n")

app = grafo.construir()
filas = []
inicio = time.time()
for c in elegidos:
    fin = app.invoke({"correo": c})
    op = {o["modelo"]: o for o in fin["opiniones"]}
    bien = correctas[c["id"]]
    fila = {"id": c["id"], "nube": op["nube"]["categoria"], "local": op["local"]["categoria"],
            "confianza_local": op["local"]["confianza"], "correcta": bien,
            "destino": "persona" if fin["destino"] == "bandeja de una persona" else "solo"}
    filas.append(fila)
    marca = "  <-- error que sigue solo" if fila["destino"] == "solo" and fila["nube"] != bien else ""
    print(f"{c['id']}  nube={fila['nube']:<27} local={fila['local']:<27} "
          f"conf={fila['confianza_local']:<5}  -> {fila['destino']}{marca}")

n = len(filas)
solos = [f for f in filas if f["destino"] == "solo"]
persona = [f for f in filas if f["destino"] == "persona"]
print(f"\nCorreos: {n}   Tiempo: {int(time.time() - inicio)} s")
print(f"Nube sola, bien: {sum(f['nube'] == f['correcta'] for f in filas)}/{n}   "
      f"Local solo, bien: {sum(f['local'] == f['correcta'] for f in filas)}/{n}")
print(f"Siguen solos: {len(solos)} (bien: {sum(f['nube'] == f['correcta'] for f in solos)})   "
      f"A una persona: {len(persona)}")
print(f"Errores de la nube que ve una persona: "
      f"{sum(f['nube'] != f['correcta'] for f in persona)} de {sum(f['nube'] != f['correcta'] for f in filas)}")

with open("resultado_bateria.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(filas[0]))
    w.writeheader()
    w.writerows(filas)
print("Detalle en resultado_bateria.csv")

if GRABAR:
    for modelo in ("nube", "local"):
        with open(f"grabadas/opiniones_{modelo}.csv", "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["id", "categoria", "confianza"])
            for fila in filas:
                w.writerow([fila["id"], fila[modelo], fila["confianza_local"] if modelo == "local" else ""])
    print("Guardadas en grabadas/.")
