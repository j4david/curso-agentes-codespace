# El buzón · Mínimo privilegio con OpenCode

**Tiempo en clase:** 75 min. Trabaja desde `ejemplo10/opencode` en el terminal del Codespace. Usa tu clave individual del curso en OpenCode. Si todavía no la has puesto, ejecuta `opencode auth login -p openrouter`.

## P10.1 · Consulta de estado (15 min)

```bash
SESION_BUZON=vecina-a opencode run -m openrouter/deepseek/deepseek-v4.1-flash "Consulta el estado de mi solicitud. Redacta solo un borrador de dos frases con lo que conste."
```

Anota la llamada a la herramienta, la referencia y el estado. Subraya toda afirmación del borrador que no puedas apoyar en esos dos campos. El expediente y el estado son ficticios.

## P10.2 · Tres límites (15 min)

1. En `opencode.json`, localiza qué herramienta puede usar el agente.
2. En `.opencode/tools/consultar_expediente.ts`, señala de dónde sale la sesión y qué argumentos recibe la herramienta.
3. En `consulta.mjs`, distingue el registro interno de los dos campos que salen. Explica por qué se conserva la nota en el registro y por qué no se envía al modelo.

`SESION_BUZON` simula el dato que entregaría una aplicación después de autenticar a la persona. Aquí lo pones tú en el terminal para cambiar el caso de prueba.

## P10.3 · Cambia el alcance y compruébalo (25 min)

1. Ejecuta `node --test consulta.test.mjs` y lee qué comprueban los tres casos de partida.
2. Pide a OpenCode que añada una tercera sesión ficticia con su propia referencia y que agregue una prueba de su salida. Mantén las salidas de A, B y de la sesión desconocida.

   **Petición para copiar:** «Trabaja solo en `consulta.mjs` y `consulta.test.mjs`. Añade la sesión `vecina-c`, referencia `SIM-306`, estado `Recibida` y una nota interna ficticia. Añade una prueba que compruebe que C obtiene exactamente referencia y estado. Conserva las tres pruebas existentes, el comportamiento sin sesión y la firma de la función. Ejecuta las pruebas si puedes y enséñame el cambio».

   Pasa a OpenCode la petición y adjunta los dos archivos (puedes usar `--file consulta.mjs --file consulta.test.mjs` al ejecutar `opencode run`). Pídele que devuelva los cambios propuestos. Revísalos y aplícalos en el editor del Codespace. Ejecuta las pruebas en el terminal.
3. Contrasta el resultado con la prueba inicial. Enseña qué dos campos recibe C y cómo sabes que no se ha alterado el resultado de A y B.

## P10.4 · Revisa antes de usar el borrador (15 min)

Repite el comando de P10.1 con `SESION_BUZON=sesion-inexistente`. Compara con la respuesta de A. En un caso, el estado «pendiente de revisar la documentación» admite varias lecturas. En el otro, la consulta no entrega datos. Para cada caso, decide qué respuesta dejarías en borrador y qué dato pedirías comprobar a una persona.

## Qué entregar (5 min)

Incluye una tabla con las tres sesiones válidas y la sesión desconocida, el resultado de las pruebas y los dos borradores revisados. Explica en una frase cada límite: qué herramienta puede usar, a qué expediente accede y qué datos devuelve.
