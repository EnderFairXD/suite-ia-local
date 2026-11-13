"""Cliente de Ollama falso para los tests: no necesita ningún modelo."""
from types import SimpleNamespace


class ClienteFalso:
    """Imita la parte de `ollama.Client` que usa la suite.

    `respuestas` puede ser una lista (se devuelven en orden y la última se repite) o una
    función que recibe los `messages` de cada llamada y devuelve el texto.
    `tokens_leidos` fija el `prompt_eval_count`; si es None se estima a partir de los
    mensajes, a 4 caracteres por token.
    """

    def __init__(self, respuestas=("ok",), tokens_leidos=None, error=None, modelos=("llama3.1:latest",)):
        self.respuestas = respuestas
        self.tokens_leidos = tokens_leidos
        self.error = error
        self.modelos = list(modelos)
        self.llamadas = []

    def chat(self, model="", messages=None, *, options=None, **_):
        if self.error:
            raise self.error
        self.llamadas.append({"model": model, "messages": list(messages), "options": dict(options or {})})
        if callable(self.respuestas):
            texto = self.respuestas(messages)
        else:
            lista = list(self.respuestas)
            texto = lista[min(len(self.llamadas) - 1, len(lista) - 1)]
        leidos = self.tokens_leidos
        if leidos is None:
            leidos = sum(len(m["content"]) for m in messages) // 4
        return SimpleNamespace(message=SimpleNamespace(content=texto), prompt_eval_count=leidos)

    def list(self):
        if self.error:
            raise self.error
        return SimpleNamespace(models=[SimpleNamespace(model=m) for m in self.modelos])

    def sistemas(self):
        """El mensaje de sistema de cada llamada, en orden."""
        return [ll["messages"][0]["content"] for ll in self.llamadas]

    def usuarios(self):
        """El mensaje de usuario de cada llamada, en orden."""
        return [ll["messages"][-1]["content"] for ll in self.llamadas]
