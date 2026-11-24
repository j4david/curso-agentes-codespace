"""El índice de las actas: trozos y sus vectores (embeddings).

El archivo indice.json ya viene hecho con la carpeta: NO hace falta ejecutar esto.
Si lo ejecutas, rehace el índice con tu clave (unas 60 peticiones de embeddings;
la clave gratuita admite 100 por minuto, así que va en tandas con pausa).

Uso: uv run python indice.py
"""

import json
import math
import pathlib
import re
import time

MODELO_EMBEDDINGS = "models/gemini-embedding-001"
DIMENSIONES = 768
TAMANO_TROZO = 1800   # caracteres, como en el ejemplo 8


def trocear(ruta: pathlib.Path) -> list[dict]:
    """Corta un acta por sus apartados y los junta hasta unos 1800 caracteres.

    Cada trozo lleva delante de qué acta es y su fecha, para poder citarla.
    """
    numero, fecha = re.match(r"acta_(\d+)_(\d{4}-\d{2}-\d{2})", ruta.stem).groups()
    apartados = re.split(r"\n(?=#{2,3} )", ruta.read_text(encoding="utf-8"))
    trozos, actual = [], ""
    for a in apartados:
        if actual and len(actual) + len(a) > TAMANO_TROZO:
            trozos.append(actual)
            actual = ""
        actual += ("\n\n" if actual else "") + a.strip()
    trozos.append(actual)
    return [{"acta": numero, "fecha": fecha, "texto": f"[Acta {numero}, {fecha}]\n{t}"} for t in trozos]


def embeddings():
    from dotenv import load_dotenv
    from langchain_google_genai import GoogleGenerativeAIEmbeddings

    load_dotenv()
    return GoogleGenerativeAIEmbeddings(model=MODELO_EMBEDDINGS, output_dimensionality=DIMENSIONES)


def normalizar(v: list[float]) -> list[float]:
    n = math.sqrt(sum(x * x for x in v)) or 1.0
    return [round(x / n, 6) for x in v]


if __name__ == "__main__":
    trozos = [t for r in sorted(pathlib.Path("actas").glob("acta_*.md")) for t in trocear(r)]
    print(f"{len(trozos)} trozos")
    e = embeddings()
    for i in range(0, len(trozos), 40):            # tandas de 40, con pausa
        tanda = trozos[i:i + 40]
        vectores = e.embed_documents([t["texto"] for t in tanda])
        for t, v in zip(tanda, vectores):
            t["vector"] = normalizar(v)
        print(f"  {i + len(tanda)} de {len(trozos)}")
        if i + 40 < len(trozos):
            time.sleep(65)
    json.dump({"modelo": MODELO_EMBEDDINGS, "dimensiones": DIMENSIONES, "trozos": trozos},
              open("indice.json", "w", encoding="utf-8"), ensure_ascii=False)
    print("Hecho: indice.json")
