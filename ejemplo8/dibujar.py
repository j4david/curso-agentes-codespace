"""Dibuja el grafo.

- dibujo.md: el dibujo en texto Mermaid. No necesita internet; OpenCode y muchos visores lo pintan.
- dibujo.png: la imagen. La hace el servicio público mermaid.ink, que solo recibe
  los nombres de las cajas y de las flechas (ningún correo ni ningún dato).

Uso: uv run python dibujar.py
"""

from grafo import construir

dibujo = construir(guardar_en=None).get_graph()

with open("dibujo.md", "w", encoding="utf-8") as f:
    f.write("```mermaid\n" + dibujo.draw_mermaid() + "```\n")
print("Hecho: dibujo.md")

try:
    dibujo.draw_mermaid_png(output_file_path="dibujo.png")
    print("Hecho: dibujo.png")
except Exception as error:  # sin conexión, o el servicio no responde
    print(f"No se pudo hacer dibujo.png ({type(error).__name__}). Usa dibujo.md.")
