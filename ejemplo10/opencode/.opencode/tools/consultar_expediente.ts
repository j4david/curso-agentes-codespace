import { tool } from "@opencode-ai/plugin"
import { consultarExpediente } from "../../consulta.mjs"

export default tool({
  description: "Consultas de estado para la persona que abrió esta sesión.",
  args: {},
  async execute() {
    return JSON.stringify(consultarExpediente(process.env.SESION_BUZON))
  },
})
