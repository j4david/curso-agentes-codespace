// Herramienta «decidir» del ejemplo 14: pregunta a un modelo de decisión que corre en TU ordenador.
//
// El modelo (decider-0.8b) lo sirve llama-server (arrancar_decider.cmd). La herramienta escribe el texto
// con el formato de los modelos decider y lee la probabilidad de cada opción (A, B, C...), sin generar texto.
// Con «texto» decide un solo correo; sin él, pasa los primeros N correos de correos.json y cuenta los aciertos
// con respuestas_correctas.csv. Todo es ficticio, para formación.
import { tool } from "@opencode-ai/plugin"
import { readFileSync, writeFileSync } from "node:fs"
import { join } from "node:path"

const SERVIDOR = process.env.DECIDER_URL ?? "http://127.0.0.1:8092"
const TEMPERATURA = 1.03 // la del archivo decider_config.json del modelo
const LETRAS = "ABCDEFGHIJ"

type Pregunta = { type: "choice" | "noul"; instructions: string; criteria?: Record<string, string | null> }

function opciones(p: Pregunta): { nombres: string[]; textos: string[] } {
  const c = p.criteria ?? {}
  if (p.type === "noul") {
    return { nombres: ["no", "sí"], textos: [c["false"] ? `no: ${c["false"]}` : "no", c["true"] ? `yes: ${c["true"]}` : "yes"] }
  }
  const nombres = Object.keys(c)
  return { nombres, textos: nombres.map((n) => (c[n] ? `${n}: ${c[n]}` : n)) }
}

async function preguntar(estado: string, p: Pregunta) {
  const { nombres, textos } = opciones(p)
  if (textos.length > LETRAS.length) throw new Error("Como mucho 10 opciones por pregunta.")
  const prompt =
    `Context:\n${estado}\n\nQuestion: ${p.instructions}\nOptions:` +
    textos.map((t, j) => `\n(${LETRAS[j]}) ${t}`).join("") +
    "\nAnswer: ("
  const r = await fetch(`${SERVIDOR}/completion`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt, n_predict: 1, n_probs: 200, temperature: 0, cache_prompt: true, post_sampling_probs: false }),
  })
  if (!r.ok) throw new Error(`llama-server respondió ${r.status}. ¿Está arrancado con arrancar_decider.cmd?`)
  const top: { token: string; logprob: number }[] = (await r.json()).completion_probabilities[0].top_logprobs
  const lp: Record<string, number> = {}
  for (const x of top) if (LETRAS.slice(0, textos.length).includes(x.token) && !(x.token in lp)) lp[x.token] = x.logprob
  const piso = Math.min(...Object.values(lp), 0) - 5
  const z = textos.map((_, j) => (lp[LETRAS[j]] ?? piso) / TEMPERATURA)
  const m = Math.max(...z)
  const e = z.map((v) => Math.exp(v - m))
  const s = e.reduce((a, b) => a + b, 0)
  const prob = e.map((v) => v / s)
  const j = prob.indexOf(Math.max(...prob))
  const n = prob.length
  const confianza = n <= 1 ? 1 : Math.max(0, Math.min(1, (n * prob[j] - 1) / (n - 1)))
  return { eleccion: nombres[j], confianza, prob: Object.fromEntries(nombres.map((nm, i) => [nm, prob[i]])) }
}

const r2 = (x: number) => Math.round(x * 100) / 100

export default tool({
  description:
    "Pregunta a un modelo de decisión local (decider-0.8b en llama-server) sobre un correo del Servicio de Ayudas. " +
    "Devuelve, para cada pregunta de preguntas.json, la opción elegida con su probabilidad y su confianza; no escribe texto. " +
    "Sin «texto», pasa los primeros N correos de correos.json, cuenta los aciertos con respuestas_correctas.csv y guarda resultado.csv. " +
    "Úsala siempre que haya que clasificar correos del buzón; no clasifiques de memoria.",
  args: {
    texto: tool.schema.string().optional().describe("Un correo concreto (asunto y cuerpo). Si se omite, se pasa la batería."),
    cuantos: tool.schema.number().int().min(1).max(30).default(10).describe("Cuántos correos de la batería (1–30). Cada uno tarda unos 10 s."),
    umbral: tool.schema.number().min(0).max(1).default(0.9).describe("Confianza mínima para clasificar solo; por debajo, va a una persona."),
    preguntas: tool.schema.string().default("preguntas.json").describe("Archivo con las preguntas y sus opciones."),
  },
  async execute(args, context) {
    const dir = context.directory
    const cuantos = args.cuantos ?? 10, umbral = args.umbral ?? 0.9, fichPreg = args.preguntas ?? "preguntas.json"
    const preguntas: Record<string, Pregunta> = JSON.parse(readFileSync(join(dir, fichPreg), "utf8"))

    if (args.texto) {
      const lineas = [`Correo decidido en local (decider-0.8b):`]
      for (const [k, p] of Object.entries(preguntas)) {
        const d = await preguntar(args.texto, p)
        const prob = Object.entries(d.prob).map(([o, v]) => `${o} ${r2(v)}`).join(", ")
        lineas.push(p.type === "noul"
          ? `- ${k}: ${d.eleccion} (probabilidad de «sí»: ${r2(d.prob["sí"])})`
          : `- ${k}: ${d.eleccion} (confianza ${r2(d.confianza)}; probabilidades: ${prob})`)
      }
      return lineas.join("\n")
    }

    const correos: { id: string; asunto: string; cuerpo: string }[] = JSON.parse(readFileSync(join(dir, "correos.json"), "utf8"))
    const filasCsv = readFileSync(join(dir, "respuestas_correctas.csv"), "utf8").trim().split(/\r?\n/)
    const cab = filasCsv[0].split(",")
    const ref: Record<string, Record<string, string>> = {}
    for (const linea of filasCsv.slice(1)) {
      const celdas = linea.split(",") // id y categoria van antes de cualquier campo con comas
      ref[celdas[0]] = { categoria: celdas[cab.indexOf("categoria")], requiere_persona: "" }
      ref[celdas[0]].requiere_persona = linea.match(/,(sí|no),"/)?.[1] ?? ""
    }

    const salida = ["id,pregunta,eleccion,confianza_o_prob_si,correcta,acierta,decide"]
    const resumen: Record<string, { ok: number; total: number; solos: number; solosOk: number }> = {}
    const aPersona: string[] = []
    const t0 = Date.now()
    for (const c of correos.slice(0, cuantos)) {
      const estado = `Asunto: ${c.asunto}\n\n${c.cuerpo}`
      for (const [k, p] of Object.entries(preguntas)) {
        const d = await preguntar(estado, p)
        const correcta = ref[c.id]?.[k] ?? ""
        const acierta = correcta ? d.eleccion === correcta : null
        const solo = p.type === "choice" ? d.confianza >= umbral : true
        const R = (resumen[k] ??= { ok: 0, total: 0, solos: 0, solosOk: 0 })
        if (acierta !== null) { R.total++; if (acierta) R.ok++ }
        if (p.type === "choice" && solo) { R.solos++; if (acierta) R.solosOk++ }
        if (p.type === "choice" && !solo) aPersona.push(`${c.id} (${k}: ${d.eleccion}, confianza ${r2(d.confianza)})`)
        salida.push([c.id, k, d.eleccion, r2(p.type === "noul" ? d.prob["sí"] : d.confianza), correcta, acierta ?? "", p.type === "noul" ? "" : solo ? "máquina" : "persona"].join(","))
      }
    }
    writeFileSync(join(dir, "resultado.csv"), "﻿" + salida.join("\n"), "utf8")
    const seg = Math.round((Date.now() - t0) / 1000)
    const lineas = [`Batería: ${cuantos} correos en ${seg} s con decider-0.8b en tu ordenador. Detalle en resultado.csv.`]
    for (const [k, R] of Object.entries(resumen)) {
      lineas.push(`- ${k}: ${R.ok} aciertos de ${R.total}` +
        (preguntas[k].type === "choice" ? `; con umbral ${umbral}: ${R.solos} los decide la máquina (${R.solosOk} bien) y ${cuantos - R.solos} van a una persona` : ""))
    }
    if (aPersona.length) lineas.push(`Para revisar por una persona: ${aPersona.join("; ")}`)
    return lineas.join("\n")
  },
})
