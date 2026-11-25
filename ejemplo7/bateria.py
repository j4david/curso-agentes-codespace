"""La batería: las alertas, varias RONDAS, para medir cuánto varía el agente.

Compara con lo que debe salir (bateria.csv, la tabla «Qué debe pasar» del ejemplo 5)
y anota, en cada ronda: qué herramientas pidió y en qué orden, cuántas veces llamó al
modelo, si la verificación se superó y cuánto tardó. La persona se simula: aprueba.

Uso: uv run python bateria.py              (las 5 alertas, 1 ronda: unos 2 minutos)
     uv run python bateria.py 3            (3 rondas)
     uv run python bateria.py 3 0501 0504  (3 rondas, solo esas)
"""

import csv
import sys
import time

from langchain_core.messages import AIMessage
from langgraph.types import Command

from datos import ALERTAS
from grafo import construir

rondas = int(sys.argv[1]) if len(sys.argv) > 1 else 1
elegidas = [f"ALT-{n.zfill(4)}" for n in sys.argv[2:]] or [a["alerta_id"] for a in ALERTAS]
esperado = {f["alerta_id"]: f for f in csv.DictReader(open("bateria.csv", encoding="utf-8"))}
grafo = construir()

filas = []
for r in range(1, rondas + 1):
    for a in [x for x in ALERTAS if x["alerta_id"] in elegidas]:
        config = {"configurable": {"thread_id": f"ronda{r}-{a['alerta_id']}"}}
        t = time.time()
        s = grafo.invoke({"alerta": a}, config)
        paro = "__interrupt__" in s
        if paro:
            s = grafo.invoke(Command(resume={"decision": "aprobar", "revisor": "batería"}), config)
        llamadas = [m for m in s["mensajes"] if isinstance(m, AIMessage)]
        orden = " > ".join(c["name"].split("_")[-1] for m in llamadas for c in m.tool_calls)
        p, e = s.get("propuesta") or {}, esperado[a["alerta_id"]]
        bien = (p.get("clasificacion") == e["clasificacion"]
                and sorted(p.get("acciones") or []) == sorted(e["acciones"].split())
                and paro == (e["necesita_persona"] == "sí"))
        fila = {"ronda": r, "alerta": a["alerta_id"], "como_debe": "sí" if bien else "no",
                "clasificacion": p.get("clasificacion", ""), "acciones": " ".join(p.get("acciones") or []),
                "persona": "sí" if paro else "no", "verificacion": "superada" if s["valida"] else "NO superada",
                "llamadas_al_modelo": len(llamadas), "consultas": orden, "segundos": round(time.time() - t, 1),
                "fallos": " | ".join(c["texto"] for c in s["comprobaciones"] if not c["ok"])}
        filas.append(fila)
        print(f"ronda {r}  {a['alerta_id']}  {fila['clasificacion']:<11} persona={fila['persona']:<2} "
              f"verificación={fila['verificacion']:<11} llamadas={len(llamadas)}  [{orden}]"
              f"{'' if bien else '   <-- revisar'}", flush=True)

with open("resultado_bateria.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(filas[0]))
    w.writeheader()
    w.writerows(filas)
n = len(filas)
print(f"\nComo debe: {sum(f['como_debe'] == 'sí' for f in filas)}/{n}   "
      f"Verificación superada: {sum(f['verificacion'] == 'superada' for f in filas)}/{n}")
if rondas > 1:
    alertas = sorted({f["alerta"] for f in filas})
    cambia = [a for a in alertas if len({f["consultas"] for f in filas if f["alerta"] == a}) > 1]
    print(f"Alertas en las que el orden de las consultas cambió entre rondas: {len(cambia)} de {len(alertas)}"
          + (f" ({', '.join(cambia)})" if cambia else ""))
print("Detalle en resultado_bateria.csv")
