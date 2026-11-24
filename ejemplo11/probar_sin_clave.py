"""Pruebas de las ramas y de la consulta, sin clave y sin gastar cuota.

No llaman al modelo: le damos a mano lo que «habría dicho» y miramos
por dónde manda el código cada caso.

Uso: uv run python probar_sin_clave.py
"""

from grafo import consultar, elegir_camino, tras_revisar

CASOS = [
    # (qué se prueba, ficha de partida, camino esperado)
    ("Correo normal", {"categoria": "solicitud_informacion", "requiere_persona": False}, "consultar"),
    ("Spam", {"categoria": "spam", "requiere_persona": False}, "descartar"),
    ("Queja, aunque el modelo diga que no hace falta persona", {"categoria": "queja", "requiere_persona": False}, "a_persona"),
    ("Orden escondida (el modelo marca requiere persona)", {"categoria": "presentacion_documentacion", "requiere_persona": True}, "a_persona"),
    ("Correo que no es de este buzón", {"categoria": "otro", "requiere_persona": False}, "a_persona"),
    ("El modelo no sabe y pregunta", {"categoria": "subsanacion", "pregunta_para_persona": "¿Es subsanación o documentación?"}, "pedir_ayuda"),
    ("Categoría que no existe", {"categoria": "felicitacion", "requiere_persona": False}, "a_persona"),
    ("Tope: ya se redactó dos veces", {"categoria": "cita_previa", "requiere_persona": False, "redacciones": 2}, "a_persona"),
]

fallos = 0
for nombre, ficha, esperado in CASOS:
    obtenido = elegir_camino(ficha)
    ok = obtenido == esperado
    fallos += not ok
    print(f"{'BIEN ' if ok else 'FALLA'}  {nombre}: {obtenido}" + ("" if ok else f" (esperado: {esperado})"))

# Al revisar: aprobar archiva; corregir vuelve a decidir con la categoría nueva.
for nombre, ficha, esperado in [
    ("Revisar: aprobar", {"decision": "aprobar", "categoria": "cita_previa"}, "archivar"),
    ("Revisar: corregir a queja", {"decision": "corregir", "categoria": "queja"}, "a_persona"),
]:
    obtenido = tras_revisar(ficha)
    ok = obtenido == esperado
    fallos += not ok
    print(f"{'BIEN ' if ok else 'FALLA'}  {nombre}: {obtenido}" + ("" if ok else f" (esperado: {esperado})"))

# La consulta solo devuelve las solicitudes del DNI del correo.
datos = consultar({"dni_o_nie": "11223344B"})["datos_consultados"]
ok = "alquiler" in datos and "fachadas" not in datos
fallos += not ok
print(f"{'BIEN ' if ok else 'FALLA'}  Consultar solo lo del remitente: {datos}")

print(f"\n{'Todo bien' if not fallos else f'{fallos} fallo(s)'}.")
raise SystemExit(1 if fallos else 0)
