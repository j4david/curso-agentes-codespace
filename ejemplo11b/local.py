"""El modelo local: decider-0.8b, servido por llama-server en tu ordenador.

Es un modelo de decisión: no escribe texto, elige una opción y dice con qué
confianza. Aquí solo le hacemos una pregunta: la categoría del correo.

No hace falta entender este archivo para la práctica. Lo que hace:
1. Escribe el correo, la pregunta y las opciones (A), (B), (C)... en el formato
   con el que se entrenó el modelo.
2. Pide a llama-server la probabilidad de cada letra.
3. Devuelve la opción más probable y una confianza entre 0 y 1.
"""

import json
import math
import urllib.request

URL = "http://127.0.0.1:8092"
TEMPERATURA = 1.03   # la del archivo decider_config.json del modelo
LETRAS = "ABCDEFGHIJ"

PREGUNTA = json.load(open("preguntas_local.json", encoding="utf-8"))["categoria"]


def esta_encendido() -> bool:
    """¿Responde llama-server? (un segundo como mucho)."""
    try:
        with urllib.request.urlopen(URL + "/health", timeout=1) as r:
            return r.status == 200
    except Exception:
        return False


def _probabilidades(prompt: str, n: int) -> list[float]:
    datos = {"prompt": prompt, "n_predict": 1, "n_probs": 200, "temperature": 0, "cache_prompt": True}
    peticion = urllib.request.Request(URL + "/completion", data=json.dumps(datos).encode("utf-8"),
                                      headers={"Content-Type": "application/json"})
    respuesta = json.load(urllib.request.urlopen(peticion, timeout=300))
    lp = {}
    for x in respuesta["completion_probabilities"][0]["top_logprobs"]:
        if x["token"] in LETRAS[:n] and x["token"] not in lp:
            lp[x["token"]] = x["logprob"]
    piso = min(lp.values()) - 5 if lp else -30.0   # una letra que no sale: casi cero
    valores = [lp.get(letra, piso) for letra in LETRAS[:n]]
    m = max(valores)
    e = [math.exp((v - m) / TEMPERATURA) for v in valores]
    return [v / sum(e) for v in e]


def clasificar(texto: str) -> tuple[str, float]:
    """Devuelve (categoría, confianza)."""
    nombres = list(PREGUNTA["criteria"])
    opciones = [f"{n}: {d}" for n, d in PREGUNTA["criteria"].items()]
    prompt = (f"Context:\n{texto}\n\nQuestion: {PREGUNTA['instructions']}\nOptions:"
              + "".join(f"\n({LETRAS[i]}) {o}" for i, o in enumerate(opciones)) + "\nAnswer: (")
    p = _probabilidades(prompt, len(opciones))
    j = max(range(len(p)), key=p.__getitem__)
    n = len(p)
    confianza = max(0.0, min(1.0, (n * p[j] - 1) / (n - 1)))   # 0 = al azar, 1 = segurísimo
    return nombres[j], round(confianza, 3)
