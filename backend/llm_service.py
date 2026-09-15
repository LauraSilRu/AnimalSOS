from backend.schemas import ResultadoTriaje


class LLMService:
    def analizar(self, mensaje: str) -> ResultadoTriaje:
        raise NotImplementedError