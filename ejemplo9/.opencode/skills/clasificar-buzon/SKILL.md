---
name: clasificar-buzon
description: Clasifica los correos del buzón del Servicio de Ayudas con el modelo de decisión local y separa lo que puede decidir la máquina de lo que debe revisar una persona. Úsala cuando pidan clasificar, ordenar o repartir correos del buzón.
---

## Cómo se hace

1. Usa SIEMPRE la herramienta `decidir`. No clasifiques de memoria ni con tu propio criterio.
2. Si te dan un correo concreto, pásalo en `texto`. Si te piden la batería, usa `cuantos` (por defecto 10) y el `umbral` que te digan (por defecto 0,9).
3. Informa con una tabla: correo, categoría elegida, confianza y quién decide (máquina o persona).
4. Debajo de la tabla, lista los correos que van a una persona y por qué (confianza baja o «requiere persona»).
5. Si la herramienta da un error de conexión, di que hay que arrancar `arrancar_decider.cmd` y no sigas.

## Prohibido

- Cambiar la categoría que dio el modelo, aunque te parezca mal: dila y explica tu duda aparte.
- Redactar respuestas a los ciudadanos: eso no es parte de esta tarea.
- Inventar aciertos: los aciertos los cuenta la herramienta con respuestas_correctas.csv.
