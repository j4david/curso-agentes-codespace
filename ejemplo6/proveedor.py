"""Qué modelo usa el grafo: Gemini (por defecto) u OpenRouter (alternativa).

Se elige en el archivo .env:
- Gemini (por defecto): GOOGLE_API_KEY=tu clave de Google AI Studio.
- OpenRouter: PROVEEDOR=openrouter y OPENROUTER_API_KEY=tu clave del curso (la de OpenCode).
  La misma clave sirve para los embeddings del ejemplo 9.

El resto del grafo no cambia: solo cambia quién responde.
"""

import json
import os
import urllib.request

from dotenv import load_dotenv

load_dotenv()  # lee el archivo .env de esta carpeta

MODELO_GEMINI = "gemini-flash-lite-latest"
MODELO_OPENROUTER = "deepseek/deepseek-v4.1-flash"   # el único que admite la clave del curso
EMBEDDINGS_OPENROUTER = "google/gemini-embedding-001"  # el mismo del índice del ejemplo 9

_VACIAS = {"", "pega_aqui_tu_clave"}


def proveedor() -> str:
    return os.environ.get("PROVEEDOR", "gemini").strip().lower() or "gemini"


def hay_clave() -> bool:
    nombre = "OPENROUTER_API_KEY" if proveedor() == "openrouter" else "GOOGLE_API_KEY"
    return os.environ.get(nombre, "").strip() not in _VACIAS


def nombre_modelo() -> str:
    return MODELO_OPENROUTER if proveedor() == "openrouter" else MODELO_GEMINI


def chat():
    """El modelo de chat, con temperatura 0 y como mucho 12 peticiones por minuto."""
    from langchain_core.rate_limiters import InMemoryRateLimiter

    ritmo = InMemoryRateLimiter(requests_per_second=0.2, check_every_n_seconds=0.1, max_bucket_size=1)
    if proveedor() == "openrouter":
        from langchain_openrouter import ChatOpenRouter

        return ChatOpenRouter(model=MODELO_OPENROUTER, temperature=0, rate_limiter=ritmo, max_retries=3)
    from langchain_google_genai import ChatGoogleGenerativeAI

    return ChatGoogleGenerativeAI(model=MODELO_GEMINI, temperature=0, rate_limiter=ritmo, max_retries=3)


class EmbeddingsOpenRouter:
    """gemini-embedding-001 a través de OpenRouter: da los mismos vectores que Gemini directo."""

    def __init__(self, dimensiones: int):
        self.dimensiones = dimensiones
        self.clave = os.environ.get("OPENROUTER_API_KEY", "").strip()
        if self.clave in _VACIAS:
            raise RuntimeError("Falta OPENROUTER_API_KEY en el archivo .env (tu clave del curso, la de OpenCode).")

    def _pedir(self, textos: list[str], tipo: str) -> list[list[float]]:
        cuerpo = json.dumps({"model": EMBEDDINGS_OPENROUTER, "input": textos,
                             "dimensions": self.dimensiones, "input_type": tipo}).encode("utf-8")
        req = urllib.request.Request("https://openrouter.ai/api/v1/embeddings", data=cuerpo, headers={
            "Authorization": f"Bearer {self.clave}", "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as r:
            datos = json.load(r)["data"]
        return [d["embedding"] for d in sorted(datos, key=lambda d: d["index"])]

    def embed_query(self, texto: str) -> list[float]:
        return self._pedir([texto], "search_query")[0]

    def embed_documents(self, textos: list[str]) -> list[list[float]]:
        return self._pedir(textos, "search_document")
