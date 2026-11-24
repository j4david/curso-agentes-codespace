"""Pruebas de las flechas y del tope, sin clave y sin gastar cuota.

Uso: uv run python probar_sin_clave.py
"""

from grafo import MAX_REESCRITURAS, tras_calificar, tras_comprobar, tras_enrutar

UNO = [{"acta": "06", "fecha": "2026-01-20", "texto": "..."}]
CASOS = [
    ("Se busca", tras_enrutar, {"ruta": "buscar"}, "recuperar"),
    ("Hay que contar en todas las actas", tras_enrutar, {"ruta": "contar"}, "contar"),
    ("Fuera de tema", tras_enrutar, {"ruta": "fuera_de_tema"}, "rechazar"),
    ("Ruta desconocida: por defecto, rechazar", tras_enrutar, {"ruta": "otra"}, "rechazar"),
    ("Hay pasajes útiles", tras_calificar, {"utiles": UNO, "reescrituras": 0}, "generar"),
    ("Ninguno útil, primera vez: reescribir", tras_calificar, {"utiles": [], "reescrituras": 0}, "reescribir"),
    ("Ninguno útil y ya se reescribió: rechazar (TOPE)", tras_calificar,
     {"utiles": [], "reescrituras": MAX_REESCRITURAS}, "rechazar"),
    ("Respuesta apoyada y que responde", tras_comprobar, {"apoyada": True, "responde": True, "reescrituras": 0}, "responder"),
    ("No alucinó, pero no respondió", tras_comprobar, {"apoyada": True, "responde": False, "reescrituras": 0}, "reescribir"),
    ("No apoyada y ya se reescribió: rechazar (TOPE)", tras_comprobar,
     {"apoyada": False, "responde": True, "reescrituras": MAX_REESCRITURAS}, "rechazar"),
]

fallos = 0
for nombre, flecha, estado, esperado in CASOS:
    obtenido = flecha(estado)
    ok = obtenido == esperado
    fallos += not ok
    print(f"{'BIEN ' if ok else 'FALLA'}  {nombre}: {obtenido}" + ("" if ok else f" (esperado: {esperado})"))

print(f"\n{'Todo bien' if not fallos else f'{fallos} fallo(s)'}.")
raise SystemExit(1 if fallos else 0)
