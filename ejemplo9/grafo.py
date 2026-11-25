"""Ejemplo 9 · Un RAG que se corrige.

Las mismas 25 actas ficticias del ejemplo 13, ahora con un grafo que se revisa a sí mismo:

  enrutar → recuperar → calificar los pasajes ─┬─ hay pasajes útiles → generar → comprobar ─┬─ bien → responder
                 ↑                             │                                           │
                 └──── reescribir (una vez) ←──┴─ no hay útiles ←──────── no está apoyada ──┘
                                                         └─ ya se reescribió → rechazar

- El modelo hace de BUSCADOR (reescribir), de REDACTOR (generar) y de JUEZ (calificar, comprobar).
- El CÓDIGO decide las flechas y pone el TOPE: como mucho, MAX_REESCRITURAS.
- «Contar en todas las actas» no se intenta: eso se hace extrayendo y contando con código (ejemplo 13).
"""

import json
import math
import operator
from typing import Annotated, Literal, TypedDict

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langgraph.graph import END, START, StateGraph

load_dotenv()  # lee la clave del archivo .env de esta carpeta

# ---------------------------------------------------------------------------
# 1. Las reglas de la casa
# ---------------------------------------------------------------------------

MAX_REESCRITURAS = 1   # el TOPE: cuántas veces se puede reescribir la búsqueda
PASAJES = 4            # cuántos trozos se recuperan en cada búsqueda (como el ejemplo 13)

# Lo que se le pide al juez de pasajes. Se mide con medir_juez.py antes de fiarse de él.
INSTRUCCIONES_JUEZ = ("Eres un juez estricto. Para cada pasaje, di solo si ayuda a responder la pregunta: "
                      "que trate el mismo tema no basta; tiene que contener el dato que se pide.")

# ---------------------------------------------------------------------------
# 2. El estado
# ---------------------------------------------------------------------------


class Estado(TypedDict, total=False):
    pregunta: str            # la del usuario; no se toca
    busqueda: str            # lo que se busca (al principio, la pregunta; luego, la reescrita)
    ruta: str
    pasajes: list[dict]      # lo recuperado: acta, fecha, texto
    utiles: list[dict]       # lo que el juez dejó pasar
    reescrituras: int
    respuesta: str
    apoyada: bool
    responde: bool
    destino: str
    registro: Annotated[list[str], operator.add]   # solo crece


# ---------------------------------------------------------------------------
# 3. El modelo, las salidas estructuradas y el índice
# ---------------------------------------------------------------------------

_modelo = None


def modelo():
    """Gemini (o OpenRouter, si lo eliges en .env; ver proveedor.py). Como mucho 12 peticiones por minuto."""
    global _modelo
    if _modelo is None:
        from proveedor import chat

        _modelo = chat()
    return _modelo


class Ruta(BaseModel):
    ruta: Literal["buscar", "contar", "fuera_de_tema"] = Field(description=(
        "buscar: casi siempre. La respuesta está en una o varias actas: un dato, una fecha, "
        "una decisión, una lista de unas pocas reuniones. "
        "contar: SOLO si hay que revisar las 25 actas una a una para contar o comprobar algo en "
        "todas (quién asistió a todas, cuántas veces se trató un tema en todo el año). "
        "fuera_de_tema: nada que ver con lo que trata la comisión (ver la lista de temas)."))
    motivo: str = Field(description="Una frase.")


TEMAS_DE_LA_COMISION = (
    "el Portal de Ayudas Municipales y su servidor (caídas, migración, límite de los adjuntos), "
    "las convocatorias de ayudas que se presentan por el portal (alquiler, comedor, fachadas), "
    "la cita previa y la atención en la OAC, el Registro General, la accesibilidad, "
    "las encuestas a los usuarios, la empresa mantenedora y quién asiste a las reuniones"
)


class Calificacion(BaseModel):
    sirve: list[bool] = Field(description="Uno por pasaje, en el mismo orden: true si ayuda a responder la pregunta.")


class Comprobacion(BaseModel):
    apoyada: bool = Field(description="true si TODO lo que afirma la respuesta está en los pasajes.")
    responde: bool = Field(description=(
        "true si la respuesta contesta a TODO lo que se pregunta. false si dice que los pasajes "
        "no lo contienen, si contesta solo a una parte o si da varios datos sin decir cuál es el que se pide."))
    motivo: str = Field(description="Una frase.")


_indice = None


def indice() -> list[dict]:
    global _indice
    if _indice is None:
        _indice = json.load(open("indice.json", encoding="utf-8"))["trozos"]
    return _indice


def vector_de(texto: str) -> list[float]:
    from indice import embeddings, normalizar

    return normalizar(embeddings().embed_query(texto))


def numerados(pasajes: list[dict]) -> str:
    return "\n\n".join(f"PASAJE {i + 1}:\n{p['texto']}" for i, p in enumerate(pasajes))


# ---------------------------------------------------------------------------
# 4. Los nodos
# ---------------------------------------------------------------------------


def enrutar(e: Estado) -> dict:
    """MODELO (juicio fijo, campo cerrado). ¿Se busca, se cuenta o no es de aquí?"""
    r = modelo().with_structured_output(Ruta).invoke([
        ("system", "Decides cómo atender una pregunta sobre las 25 actas (un año de reuniones) de la "
                   "comisión de seguimiento del Portal de Ayudas Municipales de un ayuntamiento. "
                   f"La comisión trata de: {TEMAS_DE_LA_COMISION}. Las actas van del 4 de noviembre de "
                   "2025 al 13 de octubre de 2026: no uses la fecha de hoy ni lo que sepas del mundo. "
                   "Ejemplos: «¿Qué dijo la empresa del contrato en verano?» → buscar. "
                   "«¿Qué cifras de usuarios se dieron entre enero y marzo?» → buscar (unas pocas actas). "
                   "«¿Quién faltó alguna vez a una reunión?» → contar (hay que mirar las 25). "
                   "«¿Cuál es el horario del polideportivo?» → fuera_de_tema."),
        ("human", e["pregunta"])])
    return {"ruta": r.ruta, "busqueda": e["pregunta"], "reescrituras": 0,
            "registro": [f"enrutar: {r.ruta} ({r.motivo})"]}


def recuperar(e: Estado) -> dict:
    """CÓDIGO. Los PASAJES trozos más parecidos a la búsqueda."""
    q = vector_de(e["busqueda"])
    puntuados = sorted(indice(), key=lambda t: -sum(a * b for a, b in zip(q, t["vector"])))
    elegidos = [{k: t[k] for k in ("acta", "fecha", "texto")} for t in puntuados[:PASAJES]]
    return {"pasajes": elegidos,
            "registro": [f"recuperar «{e['busqueda']}»: actas {', '.join(p['acta'] for p in elegidos)}"]}


def calificar(e: Estado) -> dict:
    """MODELO (juez 1). ¿Sirve cada pasaje? Sí o no, todos en una sola llamada."""
    r = modelo().with_structured_output(Calificacion).invoke([
        ("system", INSTRUCCIONES_JUEZ),
        ("human", f"Pregunta: {e['pregunta']}\n\n{numerados(e['pasajes'])}")])
    marcas = (r.sirve + [False] * len(e["pasajes"]))[:len(e["pasajes"])]
    utiles = [p for p, s in zip(e["pasajes"], marcas) if s]
    return {"utiles": utiles,
            "registro": [f"calificar: sirven {len(utiles)} de {len(e['pasajes'])} "
                         f"({', '.join(p['acta'] for p in utiles) or 'ninguno'})"]}


def reescribir(e: Estado) -> dict:
    """MODELO. Otra forma de buscar lo mismo. Cuenta las vueltas para el tope."""
    r = modelo().invoke([
        ("system", "Reescribe la pregunta como una búsqueda mejor para encontrar el pasaje de un acta "
                   "que la responda: palabras que aparecerían en el acta. Si no puedes mejorarla, "
                   "devuelve la original. Responde solo con la búsqueda."),
        ("human", e["pregunta"])])
    return {"busqueda": r.text.strip(), "reescrituras": e.get("reescrituras", 0) + 1,
            "registro": [f"reescribir (vuelta {e.get('reescrituras', 0) + 1}): «{r.text.strip()}»"]}


def generar(e: Estado) -> dict:
    """MODELO (redactor). Responde solo con los pasajes útiles y cita el acta."""
    r = modelo().invoke([
        ("system", "Responde a la pregunta solo con los pasajes. Cita el acta y su fecha de cada dato, "
                   "así: (acta 06, 2026-01-20). Si los pasajes no bastan, dilo. Breve."),
        ("human", f"Pregunta: {e['pregunta']}\n\n{numerados(e['utiles'])}")])
    return {"respuesta": r.text.strip(), "registro": ["generar: respuesta con citas"]}


def comprobar(e: Estado) -> dict:
    """MODELO (jueces 2 y 3). ¿Está apoyada en los pasajes? ¿Responde a la pregunta?"""
    r = modelo().with_structured_output(Comprobacion).invoke([
        ("system", "Eres un revisor estricto. No sabes nada más que lo que hay en los pasajes."),
        ("human", f"Pregunta: {e['pregunta']}\n\n{numerados(e['utiles'])}\n\nRESPUESTA:\n{e['respuesta']}")])
    return {"apoyada": r.apoyada, "responde": r.responde,
            "registro": [f"comprobar: apoyada = {r.apoyada}, responde = {r.responde} ({r.motivo})"]}


def responder(e: Estado) -> dict:
    return {"destino": "respuesta", "registro": ["responder"]}


def rechazar(e: Estado) -> dict:
    """CÓDIGO. Mejor decir que no consta que inventar."""
    texto = "No he encontrado en las actas una respuesta apoyada en lo que dicen."
    if e.get("ruta") == "fuera_de_tema":
        texto = "La pregunta no trata de la comisión del Portal de Ayudas."
    return {"destino": "rechazo", "respuesta": texto, "registro": ["rechazar"]}


def contar(e: Estado) -> dict:
    """CÓDIGO. No se intenta: se remite al método que sí funciona."""
    return {"destino": "contar con código",
            "respuesta": ("Esta pregunta pide recorrer todas las actas. Un buscador de pasajes no la "
                          "resuelve bien: hay que extraer una tabla de cada acta y contar con código "
                          "(flujo «contar asistencias» del ejemplo 13)."),
            "registro": ["contar: se remite a extraer y contar con código"]}


# ---------------------------------------------------------------------------
# 5. Las flechas: las decide el CÓDIGO
# ---------------------------------------------------------------------------


def tras_enrutar(e: Estado) -> str:
    return {"buscar": "recuperar", "contar": "contar"}.get(e["ruta"], "rechazar")


def tras_calificar(e: Estado) -> str:
    if e["utiles"]:
        return "generar"
    if e.get("reescrituras", 0) < MAX_REESCRITURAS:
        return "reescribir"
    return "rechazar"


def tras_comprobar(e: Estado) -> str:
    if e["apoyada"] and e["responde"]:
        return "responder"
    if e.get("reescrituras", 0) < MAX_REESCRITURAS:
        return "reescribir"
    return "rechazar"


# ---------------------------------------------------------------------------
# 6. El grafo
# ---------------------------------------------------------------------------


def construir():
    g = StateGraph(Estado)
    for nodo in (enrutar, recuperar, calificar, reescribir, generar, comprobar, responder, rechazar, contar):
        g.add_node(nodo.__name__, nodo)
    g.add_edge(START, "enrutar")
    g.add_conditional_edges("enrutar", tras_enrutar, ["recuperar", "contar", "rechazar"])
    g.add_edge("recuperar", "calificar")
    g.add_conditional_edges("calificar", tras_calificar, ["generar", "reescribir", "rechazar"])
    g.add_edge("reescribir", "recuperar")
    g.add_edge("generar", "comprobar")
    g.add_conditional_edges("comprobar", tras_comprobar, ["responder", "reescribir", "rechazar"])
    for final in ("responder", "rechazar", "contar"):
        g.add_edge(final, END)
    return g.compile()
