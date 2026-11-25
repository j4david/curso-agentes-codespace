import { readFileSync } from "node:fs";

const [, , numero, ...archivos] = process.argv;
const referencia = JSON.parse(readFileSync(new URL("./campos_de_referencia.json", import.meta.url), "utf8"))[numero];
if (!referencia || archivos.length === 0) {
  console.error("Uso: node cotejar.mjs <1–5> transcripcion.json [otra_transcripcion.json]");
  process.exit(2);
}

// El espacio en un número agrupado puede cambiar al copiarlo. Una cifra o una letra, no.
const normalizar = (campo, valor) => {
  if (typeof valor !== "string") return valor;
  const texto = valor.trim();
  return ["iban", "telefono", "dni_nie"].includes(campo) ? texto.replace(/\s/g, "") : texto;
};

try {
  for (const archivo of archivos) {
    const salida = JSON.parse(readFileSync(archivo, "utf8").replace(/^\uFEFF/, ""));
    if (salida === null || typeof salida !== "object" || Array.isArray(salida)) {
      throw new Error(`${archivo}: se esperaba un objeto JSON.`);
    }
    const diferencias = Object.entries(referencia)
      .filter(([campo, esperado]) => normalizar(campo, salida[campo]) !== normalizar(campo, esperado))
      .map(([campo, esperado]) => ({ campo, esperado, obtenido: salida[campo] ?? null }));
    console.log(JSON.stringify({
      archivo,
      coincidencias: Object.keys(referencia).length - diferencias.length,
      campos_cotejados: Object.keys(referencia).length,
      diferencias,
    }, null, 2));
  }
} catch (error) {
  console.error(error.message);
  process.exitCode = 2;
}
