"""
TRANSFORMACIÓN 3 — M2T: PSM FastAPI → Código ejecutable
=========================================================
Lee psm_fastapi.api y genera DOS archivos Python reales:

  salida/schemas.py  →  modelos Pydantic (validación automática)
  salida/main.py     →  aplicación FastAPI con todos los endpoints

El código generado es 100% ejecutable:
    pip install fastapi uvicorn
    uvicorn salida.main:app --reload
"""

from textx import metamodel_from_str
import os
import re

PSM_GRAMMAR = """
PSMApi:
    'psm' platform=ID name=ID '{'
        schemas += Schema
        routes  += Route
    '}'
;

Schema:
    'schema' name=ID '{'
        fields += SchemaField
    '}'
;

SchemaField:
    name=ID ':' type=ID
;

Route:
    'route' method=ID path=STRING '{'
        'summary'    ':' summary=STRING
        (path_param=PathParam)?
        (body=Body)?
        'response'   ':' response=ResponseType
        'status'     ':' status=INT
    '}'
;

PathParam:
    'path_param' ':' name=ID ':' type=ID
;

Body:
    'body' ':' type=ID
;

ResponseType:
    list?='List[' name=ID ']' | name=ID
;
"""


# ── Generador de schemas.py ───────────────────────────────────

def generar_schemas(psm_model, ruta_salida: str):
    necesita_datetime = any(
        f.type == "datetime"
        for schema in psm_model.schemas
        for f in schema.fields
    )

    lineas = []
    lineas.append("# " + "=" * 58)
    lineas.append("# SCHEMAS PYDANTIC — GENERADOS AUTOMÁTICAMENTE")
    lineas.append("# Fuente: psm_fastapi.api  |  NO EDITAR")
    lineas.append("# " + "=" * 58)
    lineas.append("")
    lineas.append("from pydantic import BaseModel")
    if necesita_datetime:
        lineas.append("from datetime import datetime")
    lineas.append("")
    lineas.append("")

    for schema in psm_model.schemas:
        lineas.append(f"class {schema.name}(BaseModel):")
        for field in schema.fields:
            padding = max(1, 14 - len(field.name))
            lineas.append(f"    {field.name}{' ' * padding}: {field.type}")
        lineas.append("")
        lineas.append(f"    class Config:")
        lineas.append(f'        json_schema_extra = {{')
        lineas.append(f'            "example": {{')
        for field in schema.fields:
            ejemplo = _ejemplo_valor(field.name, field.type)
            lineas.append(f'                "{field.name}": {ejemplo},')
        lineas.append(f'            }}')
        lineas.append(f'        }}')
        lineas.append("")
        lineas.append("")

    with open(ruta_salida, "w") as f:
        f.write("\n".join(lineas))

    print(f"  ✅ schemas.py generado → {os.path.basename(ruta_salida)}")


def _ejemplo_valor(nombre: str, tipo: str) -> str:
    """Genera un valor de ejemplo para el schema Pydantic."""
    ejemplos = {
        "nombre":    '"Laptop Pro"',
        "email":     '"usuario@ejemplo.com"',
        "precio":    "999.99",
        "total":     "150.00",
        "stock":     "42",
        "edad":      "30",
        "numero":    "1001",
        "estado":    '"pendiente"',
        "fecha":     '"2024-01-15"',
        "disponible":"True",
    }
    if nombre in ejemplos:
        return ejemplos[nombre]
    if tipo == "str":      return f'"{nombre} ejemplo"'
    if tipo == "int":      return "1"
    if tipo == "float":    return "0.0"
    if tipo == "bool":     return "True"
    if tipo == "datetime": return '"2024-01-15T00:00:00"'
    return '"ejemplo"'


# ── Generador de main.py ──────────────────────────────────────

def generar_main(psm_model, ruta_salida: str):
    # Recolectar schemas usados en responses
    schemas_usados = {s.name for s in psm_model.schemas}

    lineas = []
    lineas.append("# " + "=" * 58)
    lineas.append("# APLICACIÓN FASTAPI — GENERADA AUTOMÁTICAMENTE")
    lineas.append("# Fuente: psm_fastapi.api  |  NO EDITAR")
    lineas.append("# " + "=" * 58)
    lineas.append("# Para ejecutar:")
    lineas.append("#   pip install fastapi uvicorn")
    lineas.append("#   uvicorn main:app --reload")
    lineas.append("# " + "=" * 58)
    lineas.append("")
    lineas.append("from fastapi import FastAPI, HTTPException")
    lineas.append("from typing import List")
    lineas.append(f"from schemas import {', '.join(sorted(schemas_usados))}")
    lineas.append("")
    lineas.append(f'app = FastAPI(title="{psm_model.name}", version="1.0.0")')
    lineas.append("")
    lineas.append("# Base de datos simulada en memoria")

    for schema in psm_model.schemas:
        lineas.append(f"{schema.name.lower()}s_db: List[{schema.name}] = []")

    lineas.append("")
    lineas.append("")

    # Generar cada route
    for route in psm_model.routes:
        method   = route.method.lower()
        path     = route.path
        summary  = route.summary
        status   = route.status
        response = route.response

        # Tipo de respuesta
        if response.list:
            resp_type = f"List[{response.name}]"
        elif response.name == "dict":
            resp_type = "dict"
        else:
            resp_type = response.name

        # Decorador
        if status != 200:
            lineas.append(f'@app.{method}("{path}", response_model={resp_type}, status_code={status})')
        else:
            lineas.append(f'@app.{method}("{path}", response_model={resp_type})')

        # Firma de la función
        resource   = _inferir_resource(path)
        func_name  = _generar_nombre_funcion(method, path)
        args       = []

        if route.path_param:
            args.append(f"{route.path_param.name}: {route.path_param.type}")
        if route.body:
            args.append(f"data: {route.body.type}")

        lineas.append(f'def {func_name}({", ".join(args)}):')
        lineas.append(f'    """{summary}"""')

        # Cuerpo stub con lógica simulada
        db_name = f"{resource.lower()}s_db"
        lineas += _generar_cuerpo(method, resource, db_name, route)

        lineas.append("")
        lineas.append("")

    with open(ruta_salida, "w") as f:
        f.write("\n".join(lineas))

    print(f"  ✅ main.py    generado → {os.path.basename(ruta_salida)}")


def _inferir_resource(path: str) -> str:
    partes = path.strip('/"').split("/")
    base   = partes[0].rstrip("s")
    return base.capitalize()

def _generar_nombre_funcion(method: str, path: str) -> str:
    clean = re.sub(r'[{}"/]', '_', path).strip("_").replace("__", "_")
    return f"{method}_{clean}"

def _generar_cuerpo(method: str, resource: str, db_name: str, route) -> list:
    """Genera un cuerpo stub realista para cada tipo de endpoint."""
    nombre_id = route.path_param.name if route.path_param else None

    if method == "get" and not nombre_id:
        return [f"    return {db_name}"]

    if method == "get" and nombre_id:
        return [
            f"    item = next((x for x in {db_name} if x.numero == {nombre_id}), None)"
            if resource == "Pedido" else
            f"    item = next((i, x) for i, x in enumerate({db_name}) if i == {nombre_id})",
            f"    if not item:",
            f'        raise HTTPException(status_code=404, detail="{resource} no encontrado")',
            f"    return item",
        ]

    if method == "post":
        return [
            f"    {db_name}.append(data)",
            f"    return data",
        ]

    if method == "put":
        return [
            f"    if {nombre_id} >= len({db_name}):",
            f'        raise HTTPException(status_code=404, detail="{resource} no encontrado")',
            f"    {db_name}[{nombre_id}] = data",
            f"    return data",
        ]

    if method == "delete":
        return [
            f"    if {nombre_id} >= len({db_name}):",
            f'        raise HTTPException(status_code=404, detail="{resource} no encontrado")',
            f"    {db_name}.pop({nombre_id})",
            f'    return {{"message": "{resource} eliminado correctamente"}}',
        ]

    return ["    pass"]


# ── Main ──────────────────────────────────────────────────────

if __name__ == "__main__":
    base    = os.path.dirname(os.path.abspath(__file__))
    modelos = os.path.join(base, "..", "modelos")
    salida  = os.path.join(base, "..", "salida")
    os.makedirs(salida, exist_ok=True)

    mm  = metamodel_from_str(PSM_GRAMMAR)

    print("⚙️  Leyendo PSM FastAPI...")
    psm = mm.model_from_file(os.path.join(modelos, "psm_fastapi.api"))
    print(f"   {len(psm.schemas)} schemas, {len(psm.routes)} routes")

    print("\n📝 M2T: PSM → schemas.py")
    generar_schemas(psm, os.path.join(salida, "schemas.py"))

    print("\n📝 M2T: PSM → main.py")
    generar_main(psm, os.path.join(salida, "main.py"))
