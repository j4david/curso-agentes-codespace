"""Un grafo SIN modelo: la solicitud que se comprueba antes de registrarse.

Sirve para ver las piezas de LangGraph sin gastar nada:
- el ESTADO: la ficha que viaja de paso en paso;
- los NODOS: funciones que leen la ficha y devuelven lo que cambian;
- las FLECHAS: fijas (siempre van al mismo sitio) o con CONDICIÓN (las decide el código).

Todo es ficticio.

Uso: uv run python expediente.py            (las tres solicitudes de ejemplo)
     uv run python expediente.py dibujo     (además, dibujo.md y dibujo.png)
"""

import operator
import sys
from typing import Annotated, TypedDict

# Que se vean bien las flechas (→) aunque la salida vaya a otro programa, como OpenCode.
sys.stdout.reconfigure(encoding="utf-8")

from langgraph.graph import END, START, StateGraph

# Los campos que tiene que traer una solicitud. Cambia esta lista y cambia el grafo.
OBLIGATORIOS = ["nombre", "dni", "ayuda", "iban"]


class Ficha(TypedDict, total=False):
    solicitud: dict        # lo que llega
    faltan: list[str]      # lo rellena «comprobar»
    destino: str           # cómo acaba
    # El registro SOLO CRECE: cada nodo añade su línea (operator.add = juntar listas).
    registro: Annotated[list[str], operator.add]


def comprobar(f: Ficha) -> dict:
    """CÓDIGO. Mira qué campos obligatorios faltan."""
    faltan = [c for c in OBLIGATORIOS if not f["solicitud"].get(c)]
    return {"faltan": faltan, "registro": [f"comprobar: faltan {faltan or 'ninguno'}"]}


def pedir_datos(f: Ficha) -> dict:
    """CÓDIGO. Prepara el requerimiento de subsanación (no lo envía)."""
    return {"destino": "requerimiento", "registro": [f"pedir_datos: pedir {', '.join(f['faltan'])}"]}


def registrar(f: Ficha) -> dict:
    """CÓDIGO. Da la solicitud por registrada (simulado)."""
    return {"destino": "registrada", "registro": ["registrar: solicitud completa"]}


def elegir_camino(f: Ficha) -> str:
    """La flecha con condición. La decide el CÓDIGO, con una regla que se puede leer."""
    return "pedir_datos" if f["faltan"] else "registrar"


def construir():
    g = StateGraph(Ficha)
    g.add_node("comprobar", comprobar)
    g.add_node("pedir_datos", pedir_datos)
    g.add_node("registrar", registrar)
    g.add_edge(START, "comprobar")
    # Las etiquetas del diccionario son las que salen en las flechas del dibujo.
    g.add_conditional_edges("comprobar", elegir_camino,
                            {"pedir_datos": "pedir_datos", "registrar": "registrar"})
    g.add_edge("pedir_datos", END)
    g.add_edge("registrar", END)
    return g.compile()


SOLICITUDES = [
    {"nombre": "Lucía Ficticia", "dni": "00000000T", "ayuda": "alquiler", "iban": "ES00 0000 0000 0000 0000 0000"},
    {"nombre": "Pedro Inventado", "dni": "", "ayuda": "comedor", "iban": ""},
    {"nombre": "Ana Ejemplo", "dni": "11111111H", "ayuda": "fachadas"},
]

if __name__ == "__main__":
    grafo = construir()
    for s in SOLICITUDES:
        final = grafo.invoke({"solicitud": s})
        print(f"\n{s['nombre']}:")
        for linea in final["registro"]:
            print(f"  · {linea}")
        print(f"  → {final['destino']}")
    if "dibujo" in sys.argv[1:]:
        d = grafo.get_graph()
        open("dibujo.md", "w", encoding="utf-8").write("```mermaid\n" + d.draw_mermaid() + "```\n")
        print("\nHecho: dibujo.md")
        try:
            d.draw_mermaid_png(output_file_path="dibujo.png")
            print("Hecho: dibujo.png (lo hace mermaid.ink, que solo recibe los nombres de las cajas)")
        except Exception as e:  # sin conexión
            print(f"No se pudo hacer dibujo.png ({type(e).__name__}). Usa dibujo.md.")
