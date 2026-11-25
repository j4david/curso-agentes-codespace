# El formulario escaneado · OpenCode

**Tiempo en clase:** 90 min. Trabaja desde `ejemplo12/opencode` en el terminal del Codespace. Usa tu clave individual del curso configurada en OpenCode. Las cinco imágenes ficticias están en la carpeta superior.

## P12.1 · Transcribe un formulario (15 min)

Empieza por la solicitud 1. Ejecuta este comando y guarda el objeto, sin el bloque Markdown, como `solicitud_1.json`.

```bash
opencode run -m openrouter/deepseek/deepseek-v4.1-flash \
  "Transcribe la solicitud adjunta. Devuelve solo JSON con estos campos de tipo cadena: nombre, apellidos, dni_nie, fecha_nacimiento, domicilio, telefono, correo, importe_alquiler_mensual, miembros_unidad_familiar, iban, fecha_solicitud, firma. Copia lo que ves aunque parezca incorrecto. Si un campo está vacío o es ilegible, devuelve una cadena vacía. En firma pon sí si se ve una firma y no si está en blanco." \
  --file ../solicitud_1.png
```

Localiza en el JSON el teléfono y el correo. Mira `OBLIGATORIOS` en `comprobar.mjs` y explica qué diferencia hay entre un campo previsto por el esquema y uno que tiene que venir rellenado.

## P12.2 · Detecta de dónde viene el error (20 min)

1. Repite la transcripción con las solicitudes 2, 3, 4 y 5. Guarda cada objeto con el número de su imagen.
2. Coteja DNI o NIE, IBAN, teléfono y ambas fechas con las imágenes. Cuando encuentres una diferencia, anota si el modelo copió mal el campo, si estaba vacío o si el dato inválido ya estaba escrito.
3. Comprueba tu cotejo con `node cotejar.mjs 3 solicitud_3.json`. La referencia dice lo que **está escrito**, aunque el dato original sea inválido. El cotejo compara cinco campos y devuelve las diferencias.

## P12.3 · Separa formato y contenido (20 min)

```bash
node comprobar.mjs salida-de-ejemplo.txt
node comprobar.mjs solicitud_4.json
node comprobar.mjs solicitud_5.json
```

El primer archivo simula una salida textual alrededor de un objeto. Los otros dos son transcripciones. Anota el destino y separa un fallo de formato del mensaje de un problema del formulario. Decide qué volverías a procesar, qué corregirías mirando el original y qué enviarías a revisión humana.

## P12.4 · Cambia una instrucción y mide (25 min)

1. Repite las solicitudes **3 (manuscrita)** y **1 (control)**. Añade al final de la petición: «En fecha_nacimiento y fecha_solicitud copia solo la fecha en dd/mm/aaaa, sin municipio ni otros rótulos. Conserva los números tal como están escritos, incluso si la fecha no existe». Guarda los nuevos objetos como `solicitud_3_v2.json` y `solicitud_1_v2.json`.
2. Compara ambas versiones con la referencia:

```bash
node cotejar.mjs 3 solicitud_3.json solicitud_3_v2.json
node cotejar.mjs 1 solicitud_1.json solicitud_1_v2.json
```

3. Pasa ambas versiones nuevas por `comprobar.mjs`. Decide si mantendrías la nueva instrucción, a partir de las diferencias por campo. Si no cambia nada, registra ese resultado.

## Qué entregar (10 min)

Entrega una tabla con cinco filas: solicitud, hallazgo al cotejar, avisos del validador y decisión. Añade la comparación antes/después de las solicitudes 3 y 1. Explica un dato que solo puedas comprobar volviendo a la imagen y un aviso que el código pueda detectar aunque la transcripción sea fiel.
