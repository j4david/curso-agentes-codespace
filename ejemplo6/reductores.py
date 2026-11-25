"""¿Qué pasa cuando dos pasos escriben en el mismo campo de la ficha? Sin modelo, sin clave.

Tres casos con el mismo campo «notas»:
1. Uno detrás de otro, SIN reductor: el segundo BORRA lo del primero (sobrescribe).
2. Uno detrás de otro, CON reductor (operator.add): se JUNTAN las dos notas.
3. Los dos A LA VEZ, sin reductor: LangGraph da un error, porque no sabe con cuál quedarse.
   Con reductor, se juntan (es lo que hace el ejemplo de la segunda opinión).

Uso: uv run python reductores.py
"""

import operator
from typing import Annotated, TypedDict

from langgraph.errors import InvalidUpdateError
from langgraph.graph import END, START, StateGraph


class SinReductor(TypedDict):
    notas: list[str]


class ConReductor(TypedDict):
    notas: Annotated[list[str], operator.add]


def jefatura(_):
    return {"notas": ["jefatura: conforme"]}


def intervencion(_):
    return {"notas": ["intervención: falta el informe"]}


def en_fila(Estado):
    g = StateGraph(Estado)
    g.add_node("jefatura", jefatura)
    g.add_node("intervencion", intervencion)
    g.add_edge(START, "jefatura")
    g.add_edge("jefatura", "intervencion")
    g.add_edge("intervencion", END)
    return g.compile()


def a_la_vez(Estado):
    g = StateGraph(Estado)
    g.add_node("jefatura", jefatura)
    g.add_node("intervencion", intervencion)
    g.add_edge(START, "jefatura")        # dos flechas desde el inicio:
    g.add_edge(START, "intervencion")    # los dos pasos van a la vez
    g.add_edge("jefatura", END)
    g.add_edge("intervencion", END)
    return g.compile()


print("1. En fila, sin reductor:  ", en_fila(SinReductor).invoke({"notas": []})["notas"])
print("2. En fila, con reductor:  ", en_fila(ConReductor).invoke({"notas": []})["notas"])
try:
    print("3. A la vez, sin reductor: ", a_la_vez(SinReductor).invoke({"notas": []})["notas"])
except InvalidUpdateError as e:
    print("3. A la vez, sin reductor:  ERROR:", str(e).splitlines()[0])
print("   A la vez, con reductor: ", a_la_vez(ConReductor).invoke({"notas": []})["notas"])
