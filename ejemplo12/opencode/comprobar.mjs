import { readFileSync } from "node:fs";

// Reglas del formulario ficticio, adaptadas del nodo de validación de mc12.
const OBLIGATORIOS = ['nombre', 'apellidos', 'dni_nie', 'fecha_nacimiento', 'domicilio',
  'telefono', 'importe_alquiler_mensual', 'miembros_unidad_familiar', 'iban',
  'fecha_solicitud', 'firma'];
const LETRAS = 'TRWAGMYFPDXBNJZSQVHLCKE';

const texto = (v) => (v === null || v === undefined) ? '' : String(v).trim();

function comprobarDni(valor, avisos) {
  const s = texto(valor).toUpperCase().replace(/[\s.-]/g, '');
  const m = s.match(/^([XYZ]\d{7}|\d{8})([A-Z])$/);
  if (!m) { avisos.push(`DNI_FORMATO: «${valor}» no tiene forma de DNI (8 cifras y letra) ni de NIE (X/Y/Z, 7 cifras y letra)`); return; }
  const numero = Number(m[1].replace('X', '0').replace('Y', '1').replace('Z', '2'));
  const correcta = LETRAS[numero % 23];
  if (m[2] !== correcta) avisos.push(`DNI_LETRA: la letra de ${s} no corresponde (sería ${correcta})`);
}

function comprobarIban(valor, avisos) {
  const s = texto(valor).toUpperCase().replace(/\s/g, '');
  if (!/^ES\d{22}$/.test(s)) { avisos.push(`IBAN: «${valor}» no tiene forma de IBAN español (ES y 22 cifras)`); return; }
  const reordenado = s.slice(4) + s.slice(0, 4);
  const cifras = reordenado.replace(/[A-Z]/g, (c) => String(c.charCodeAt(0) - 55));
  let resto = 0;  // mod 97 por trozos para no pasarse de Number
  for (const c of cifras) resto = (resto * 10 + Number(c)) % 97;
  if (resto !== 1) avisos.push(`IBAN: ${s} no supera el control (mod 97); hay alguna cifra mal`);
}

function leerFecha(valor, campo, avisos) {
  const s = texto(valor);
  const m = s.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/);
  if (!m) { avisos.push(`FECHA_IMPOSIBLE: ${campo} «${s}» no tiene el formato dd/mm/aaaa`); return null; }
  const [d, mes, a] = [Number(m[1]), Number(m[2]), Number(m[3])];
  const f = new Date(Date.UTC(a, mes - 1, d));
  if (f.getUTCFullYear() !== a || f.getUTCMonth() !== mes - 1 || f.getUTCDate() !== d) {
    avisos.push(`FECHA_IMPOSIBLE: ${campo} «${s}» no existe en el calendario`); return null;
  }
  if (a < 1900 || a > 2100) { avisos.push(`FECHA_IMPOSIBLE: ${campo} «${s}» tiene un año fuera de lo razonable`); return null; }
  return f;
}

function edadEn(nac, ref) {
  let edad = ref.getUTCFullYear() - nac.getUTCFullYear();
  if (ref.getUTCMonth() < nac.getUTCMonth() ||
     (ref.getUTCMonth() === nac.getUTCMonth() && ref.getUTCDate() < nac.getUTCDate())) edad--;
  return edad;
}

function comprobar(sol) {
  const avisos = [];
  for (const c of OBLIGATORIOS) {
    if (texto(sol[c]) === '') avisos.push(`CAMPO_VACIO: falta «${c}», que es obligatorio`);
  }
  if (texto(sol.dni_nie)) comprobarDni(sol.dni_nie, avisos);
  if (texto(sol.iban)) comprobarIban(sol.iban, avisos);

  const nac = texto(sol.fecha_nacimiento) ? leerFecha(sol.fecha_nacimiento, 'fecha_nacimiento', avisos) : null;
  const fsol = texto(sol.fecha_solicitud) ? leerFecha(sol.fecha_solicitud, 'fecha_solicitud', avisos) : null;
  if (nac && fsol) {
    if (fsol <= nac) avisos.push('FECHA_INCOHERENTE: la fecha de solicitud no es posterior a la de nacimiento');
    else if (edadEn(nac, fsol) < 18) avisos.push(`MENOR_DE_EDAD: tenía ${edadEn(nac, fsol)} años en la fecha de solicitud`);
  }

  const imp = texto(sol.importe_alquiler_mensual);
  if (imp) {
    const n = Number(imp.replace(/[€\s]/g, '').replace(/\.(?=\d{3}(\D|$))/g, '').replace(',', '.'));
    if (!Number.isFinite(n) || n <= 0) avisos.push(`IMPORTE: «${imp}» no es un importe válido`);
  }
  const miem = texto(sol.miembros_unidad_familiar);
  if (miem && !(/^\d{1,2}$/.test(miem) && Number(miem) >= 1)) avisos.push(`MIEMBROS: «${miem}» no es un número de miembros válido`);
  const tel = texto(sol.telefono).replace(/[\s.-]/g, '').replace(/^(\+34|0034)/, '');
  if (tel && !/^[6789]\d{8}$/.test(tel)) avisos.push(`TELEFONO: «${sol.telefono}» no tiene 9 cifras de un teléfono español`);
  const correo = texto(sol.correo);
  if (correo && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correo)) avisos.push(`CORREO: «${correo}» no parece una dirección de correo`);

  return { ok: avisos.length === 0, avisos };
}

const archivo = process.argv[2];
if (!archivo) {
  console.error("Uso: node comprobar.mjs solicitud.json");
  process.exit(2);
}
try {
  const solicitud = JSON.parse(readFileSync(archivo, "utf8").replace(/^\uFEFF/, ""));
  if (solicitud === null || typeof solicitud !== "object" || Array.isArray(solicitud)) {
    throw new Error("La transcripción debe ser un objeto JSON.");
  }
  const resultado = comprobar(solicitud);
  console.log(JSON.stringify({
    destino: resultado.ok ? "comprobaciones_superadas" : "revision_humana",
    avisos: resultado.avisos,
  }, null, 2));
} catch (error) {
  const destino = error instanceof SyntaxError || !error.code ? "error_formato" : "error_archivo";
  console.log(JSON.stringify({ destino, detalle: error.message }, null, 2));
  process.exitCode = 2;
}
