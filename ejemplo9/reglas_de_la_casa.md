# Reglas de la casa del buzón del Servicio de Ayudas

Cómo decide una persona del Servicio la categoría de cada correo y si requiere que la atienda alguien. Úsalas para mejorar las descripciones de `preguntas.json` (práctica P9.3). Todo es ficticio, para formación.

**categoria** (cerrada): `solicitud_informacion`, `presentacion_documentacion`, `subsanacion`, `queja`, `incidencia_tecnica`, `cita_previa`, `spam`, `otro`. Una sola por correo: la de la petición principal. Si hay una segunda, se dice en `motivo` (correo 08).

- `subsanacion` = responde a un requerimiento del Ayuntamiento sobre un expediente (o pide algo dentro de él, como el 29). Aportar documentos sin requerimiento es `presentacion_documentacion`.
- `otro` = correo legítimo que no es de este buzón o que no pide nada (24, 28).

**requiere_persona** (`sí`/`no`): `sí` cuando la respuesta no puede ser automática porque hay que decidir algo, atender un conflicto o frenar un riesgo: quejas y reclamaciones, instrucciones sospechosas dirigidas al asistente, peticiones de datos de terceros, un conflicto que se está gestando (12) o una decisión discrecional como ampliar un plazo (29). El *spam* va a `no`: se descarta sin responder (si se quiere, se avisa a seguridad, pero no hay que contestar a nadie).

