from statistics import mean

from backend.llm_service import OllamaService
from backend.groq_service import GroqService


INCIDENCIAS = [
    "He encontrado un perro atropellado que no puede levantarse.",
    "Mi gato se ha perdido hace dos días y no consigo encontrarlo.",
    "He visto a una persona golpeando a un perro repetidamente.",
    "Quiero adoptar un perro y necesito información sobre el proceso.",
    "Hay un animal solo en la calle y no sé qué le ocurre.",
]


def ejecutar_benchmark():
    ollama = OllamaService()
    groq = GroqService()

    resultados = []

    for numero, incidencia in enumerate(INCIDENCIAS, start=1):
        print(f"\n{'=' * 60}")
        print(f"INCIDENCIA {numero}")
        print(incidencia)
        print("=" * 60)

        # ---------- OLLAMA ----------
        try:
            resultado, metricas = ollama.analizar(incidencia)

            datos = {
                "incidencia": numero,
                "proveedor": "Ollama",
                "modelo": metricas.modelo,
                "latencia": metricas.latencia_segundos,
                "tokens": metricas.tokens_totales,
                "coste": metricas.coste_estimado,
                "categoria": resultado.categoria.value,
                "urgencia": resultado.urgencia.value,
                "departamento": resultado.departamento.value,
                "estado": "OK",
                "error": "",
            }

            resultados.append(datos)

            print("\nOllama:")
            print(f"  Latencia: {metricas.latencia_segundos}s")
            print(f"  Tokens: {metricas.tokens_totales}")
            print(f"  Coste: {metricas.coste_estimado}€")
            print(f"  Categoría: {resultado.categoria.value}")
            print(f"  Urgencia: {resultado.urgencia.value}")
            print(f"  Departamento: {resultado.departamento.value}")

        except Exception as error:
            resultados.append({
                "incidencia": numero,
                "proveedor": "Ollama",
                "modelo": "llama3.2",
                "latencia": None,
                "tokens": None,
                "coste": None,
                "categoria": None,
                "urgencia": None,
                "departamento": None,
                "estado": "ERROR",
                "error": str(error),
            })

            print(f"\nOllama ERROR: {error}")

        # ---------- GROQ ----------
        try:
            resultado, metricas = groq.analizar(incidencia)

            datos = {
                "incidencia": numero,
                "proveedor": "Groq",
                "modelo": metricas.modelo,
                "latencia": metricas.latencia_segundos,
                "tokens": metricas.tokens_totales,
                "coste": metricas.coste_estimado,
                "categoria": resultado.categoria.value,
                "urgencia": resultado.urgencia.value,
                "departamento": resultado.departamento.value,
                "estado": "OK",
                "error": "",
            }

            resultados.append(datos)

            print("\nGroq:")
            print(f"  Latencia: {metricas.latencia_segundos}s")
            print(f"  Tokens: {metricas.tokens_totales}")
            print(f"  Coste: {metricas.coste_estimado}€")
            print(f"  Categoría: {resultado.categoria.value}")
            print(f"  Urgencia: {resultado.urgencia.value}")
            print(f"  Departamento: {resultado.departamento.value}")

        except Exception as error:
            resultados.append({
                "incidencia": numero,
                "proveedor": "Groq",
                "modelo": "openai/gpt-oss-20b",
                "latencia": None,
                "tokens": None,
                "coste": None,
                "categoria": None,
                "urgencia": None,
                "departamento": None,
                "estado": "ERROR",
                "error": str(error),
            })

            print(f"\nGroq ERROR: {error}")

    # ---------- DETALLE COMPLETO ----------
    print("\n\n")
    print("=" * 100)
    print("RESULTADOS COMPLETOS DEL BENCHMARK")
    print("=" * 100)

    for resultado in resultados:
        if resultado["estado"] == "OK":
            print(
                f"{resultado['proveedor']:8} | "
                f"Incidencia {resultado['incidencia']} | "
                f"{resultado['latencia']:>6}s | "
                f"{resultado['tokens']:>4} tokens | "
                f"{resultado['coste']:.8f}€ | "
                f"{resultado['categoria']} | "
                f"{resultado['urgencia']} | "
                f"{resultado['departamento']}"
            )
        else:
            print(
                f"{resultado['proveedor']:8} | "
                f"Incidencia {resultado['incidencia']} | "
                f"ERROR | "
                f"{resultado['error']}"
            )

    # ---------- RESUMEN POR PROVEEDOR ----------
    print("\n\n")
    print("=" * 80)
    print("RESUMEN COMPARATIVO")
    print("=" * 80)

    for proveedor in ["Ollama", "Groq"]:
        validos = [
            r for r in resultados
            if r["proveedor"] == proveedor and r["estado"] == "OK"
        ]

        total_casos = len([
            r for r in resultados
            if r["proveedor"] == proveedor
        ])

        if not validos:
            print(f"\n{proveedor}: no hay respuestas válidas.")
            continue

        latencias = [r["latencia"] for r in validos]
        tokens = [r["tokens"] for r in validos]
        costes = [r["coste"] for r in validos]

        print(f"\n{proveedor}")
        print(f"  Respuestas válidas: {len(validos)}/{total_casos}")
        print(f"  Latencia media: {mean(latencias):.3f}s")
        print(f"  Tokens medios: {mean(tokens):.0f}")
        print(f"  Coste total estimado: {sum(costes):.8f}€")


if __name__ == "__main__":
    ejecutar_benchmark()