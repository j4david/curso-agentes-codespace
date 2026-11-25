import assert from "node:assert/strict";
import { test } from "node:test";
import { consultarExpediente } from "./consulta.mjs";

test("la sesión A recibe solo la referencia y el estado de SIM-104", () => {
  assert.deepEqual(consultarExpediente("vecina-a"), {
    referencia: "SIM-104",
    estado: "Pendiente de revisar la documentación",
  });
});

test("la sesión B recibe solo la referencia y el estado de SIM-205", () => {
  assert.deepEqual(consultarExpediente("vecino-b"), {
    referencia: "SIM-205",
    estado: "En revisión",
  });
});

test("sin sesión válida no se devuelve ningún dato del expediente", () => {
  assert.deepEqual(consultarExpediente(undefined), { disponible: false });
  assert.deepEqual(consultarExpediente("sesion-inexistente"), { disponible: false });
});
