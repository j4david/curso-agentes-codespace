// Datos de formación. En una aplicación real, la identidad procede de la sesión autenticada.
const expedientes = new Map([
  ["vecina-a", {
    referencia: "SIM-104",
    estado: "Pendiente de revisar la documentación",
    notaInterna: "Clasificación provisional del equipo",
  }],
  ["vecino-b", {
    referencia: "SIM-205",
    estado: "En revisión",
    notaInterna: "Pendiente de asignación interna",
  }],
]);

export function consultarExpediente(sesion) {
  const expediente = expedientes.get(sesion);
  if (!expediente) return { disponible: false };

  const { referencia, estado } = expediente;
  return { referencia, estado };
}
