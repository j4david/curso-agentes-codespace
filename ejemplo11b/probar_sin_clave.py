"""Pruebas de la regla de comparar, sin clave y sin modelo local.

No llaman a ningún modelo: le damos a mano las dos opiniones y miramos
adónde manda el código cada caso.

Uso: uv run python probar_sin_clave.py
"""

import grafo


def ficha(nube, local, confianza):
    return {"opiniones": [{"modelo": "nube", "categoria": nube, "confianza": ""},
                          {"modelo": "local", "categoria": local, "confianza": confianza}]}


CASOS = [
    # (qué se prueba, opinión de la nube, opinión del local, confianza del local, camino esperado)
    ("Coinciden", "cita_previa", "cita_previa", 0.95, "seguir_solo"),
    ("No coinciden", "queja", "solicitud_informacion", 0.67, "a_persona"),
    ("No coinciden, aunque el local esté muy seguro", "spam", "otro", 0.99, "a_persona"),
    ("El orden en que llegan no importa", "subsanacion", "subsanacion", 0.9, "seguir_solo"),
]

fallos = 0
for nombre, nube, local, conf, esperado in CASOS:
    obtenido = grafo.elegir_camino(ficha(nube, local, conf))
    ok = obtenido == esperado
    fallos += not ok
    print(f"{'BIEN ' if ok else 'FALLA'}  {nombre}: {obtenido}" + ("" if ok else f" (esperado: {esperado})"))

# El umbral: con 0.9, un acuerdo con poca confianza del local va a una persona.
antes = grafo.UMBRAL_LOCAL
grafo.UMBRAL_LOCAL = 0.9
for nombre, conf, esperado in [("Umbral 0,9: coinciden con 0,5", 0.5, "a_persona"),
                               ("Umbral 0,9: coinciden con 0,95", 0.95, "seguir_solo")]:
    obtenido = grafo.elegir_camino(ficha("cita_previa", "cita_previa", conf))
    ok = obtenido == esperado
    fallos += not ok
    print(f"{'BIEN ' if ok else 'FALLA'}  {nombre}: {obtenido}" + ("" if ok else f" (esperado: {esperado})"))
grafo.UMBRAL_LOCAL = antes

# El grafo entero, con las opiniones grabadas: las dos se juntan y ninguna borra a la otra.
import json

antes = grafo.SOLO_GRABADAS
grafo.SOLO_GRABADAS = True
correo = next(c for c in json.load(open("correos.json", encoding="utf-8")) if c["id"] == "10")
fin = grafo.construir().invoke({"correo": correo})
grafo.SOLO_GRABADAS = antes
ok = sorted(o["modelo"] for o in fin["opiniones"]) == ["local", "nube"] and "destino" in fin
fallos += not ok
print(f"{'BIEN ' if ok else 'FALLA'}  Grafo entero con las grabadas: {len(fin['opiniones'])} opiniones, {fin['destino']}")

print(f"\n{'Todo bien' if not fallos else f'{fallos} fallo(s)'}.")
raise SystemExit(1 if fallos else 0)
