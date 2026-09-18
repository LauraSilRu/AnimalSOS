import json
from datetime import datetime
from pathlib import Path


RUTA_REGISTRO = Path(__file__).resolve().parent.parent / "data" / "incidencias.json"


def cargar_incidencias() -> list:
    """Carga las incidencias guardadas en el registro."""

    if not RUTA_REGISTRO.exists():
        return []

    try:
        with open(RUTA_REGISTRO, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except (json.JSONDecodeError, OSError):
        return []


def guardar_incidencia(
    mensaje: str,
    proveedor: str,
    resultado_ia: dict | None,
    decision_final: dict | None,
    validacion_humana: bool = False,
) -> dict:
    """Guarda una incidencia y devuelve el registro creado."""

    incidencias = cargar_incidencias()

    nueva_incidencia = {
        "id": len(incidencias) + 1,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mensaje": mensaje,
        "proveedor": proveedor,
        "resultado_ia": resultado_ia,
        "decision_final": decision_final,
        "validacion_humana": validacion_humana,
    }

    incidencias.append(nueva_incidencia)

    RUTA_REGISTRO.parent.mkdir(parents=True, exist_ok=True)

    with open(RUTA_REGISTRO, "w", encoding="utf-8") as archivo:
        json.dump(incidencias, archivo, ensure_ascii=False, indent=2)

    return nueva_incidencia

def actualizar_decision_humana(
    incidencia_id: int,
    decision_final: dict,
) -> dict | None:
    """Actualiza la decisión final de una incidencia."""

    incidencias = cargar_incidencias()

    for incidencia in incidencias:
        if incidencia["id"] == incidencia_id:

            incidencia["decision_final"] = decision_final
            incidencia["validacion_humana"] = True

            with open(RUTA_REGISTRO, "w", encoding="utf-8") as archivo:
                json.dump(
                    incidencias,
                    archivo,
                    ensure_ascii=False,
                    indent=2,
                )

            return incidencia

    return None