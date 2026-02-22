"""
TRANSFORMACIÓN 2 — M2M: PIM → PSM FastAPI
==========================================
Lee pim.api (endpoints abstractos) y genera psm_fastapi.api

Los tipos abstractos del PIM se mapean a tipos Python/Pydantic:
  Text    → str
  Number  → int o float  (según semántica del campo)
  Bool    → bool
  Date    → datetime

Los endpoints reciben status codes HTTP concretos y
sus parámetros se clasifican como path_param o body.
"""

from textx import metamodel_from_file
import re
import os

# Tipos abstractos PIM → tipos Python/Pydantic
PYTHON_TYPES = {
    "Text":   "str",
    "Bool":   "bool",
    "Date":   "datetime",
    "Number": "float",    # default; se afina por nombre de campo
}

# Campos numéricos enteros por nombre
INTEGER_FIELDS = {"id", "stock", "edad", "numero"}

# Mapeo de respuesta abstracta → status code HTTP
STATUS_CODES = {
    "POST": 201,
    "GET":  200,
    "PUT":  200,
    "DELETE": 200,
}

def tipo_python(field_name: str, pim_type: str) -> str:
    if pim_type == "Number":
        return "int" if field_name.lower() in INTEGER_FIELDS else "float"
    return PYTHON_TYPES.get(pim_type, "str")

def extraer_path_param(path: str):
    """Extrae {param} del path si existe, ej: /productos/{id} → id"""
    match = re.search(r'\{(\w+)\}', path)
    return match.group(1) if match else None

def nombre_param_especifico(path: str, resource_name: str) -> str:
    """Convierte {id} en {producto_id} según el recurso."""
    return f"{resource_name.lower()}_id"

def inferir_resource(path: str) -> str:
    """Extrae el nombre del recurso desde la ruta: /productos → Producto"""
    partes = path.strip("/").split("/")
    base   = partes[0]                  # productos
    # Quitar la 's' final y capitalizar
    singular = base.rstrip("s").capitalize()
    return singular


# Schemas a generar (inferidos de los recursos del PIM)
SCHEMAS = {
    "Producto": [
        ("nombre",    "str"),
        ("precio",    "float"),
        ("stock",     "int"),
        ("disponible","bool"),
    ],
    "Cliente": [
        ("nombre", "str"),
        ("email",  "str"),
        ("edad",   "int"),
    ],
    "Pedido": [
        ("numero", "int"),
        ("total",  "float"),
        ("estado", "str"),
        ("fecha",  "datetime"),
    ],
    "Factura": [
        ("numero", "int"),
        ("total",  "float"),
        ("estado", "str"),
        ("fecha",  "datetime"),
    ],
}

def generate_schemas(model, lineas):
    modelClasses = model.modelClasses
    for mc in modelClasses:
        lineas.append(f"    schema {mc.name} {{")
        for field in mc.fields:
            print(f"field {field}")
            lineas.append(f"        {field.name} : {PYTHON_TYPES[field.type]}")
        lineas.append("    }")
        lineas.append("")
            

def generar_psm(pim_model, ruta_salida: str):
    lineas = []
    lineas.append("")
    lineas.append(f"psm fastapi {pim_model.name} {{")
    lineas.append("")
    
    generate_schemas(pim_model, lineas)

    # # Schemas Pydantic
    # for schema_name, fields in SCHEMAS.items():
    #     lineas.append(f"    schema {schema_name} {{")
    #     for fname, ftype in fields:
    #         padding = max(1, 14 - len(fname))
    #         lineas.append(f"        {fname}{' ' * padding}: {ftype}")
    #     lineas.append("    }")
    #     lineas.append("")

    # Routes
    for ep in pim_model.endpoints:
        path      = ep.path.value
        method    = ep.method
        resource  = inferir_resource(path)
        path_param_orig = extraer_path_param(path)
        status    = STATUS_CODES.get(method, 200)

        # Ruta con nombre de param específico
        if path_param_orig:
            param_name = nombre_param_especifico(path, resource)
            ruta_psm   = path.replace(f"{{{path_param_orig}}}", f"{{{param_name}}}")
        else:
            ruta_psm   = path
            param_name = None

        # Respuesta
        if ep.response.list:
            response_str = f"List[{ep.response.name}]"
        elif ep.response.name == "Message":
            response_str = "dict"
        else:
            response_str = ep.response.name

        lineas.append(f'    route {method} "{ruta_psm}" {{')
        lineas.append(f'        summary    : "{ep.summary}"')

        if param_name:
            lineas.append(f"        path_param : {param_name}:int")

        # Body para POST y PUT
        if method in ("POST", "PUT"):
            lineas.append(f"        body       : {resource}")

        lineas.append(f"        response   : {response_str}")
        lineas.append(f"        status     : {status}")
        lineas.append(f"    }}")
        lineas.append("")

    lineas.append("}")

    with open(ruta_salida, "w") as f:
        f.write("\n".join(lineas))

    print(f"  ✅ PSM FastAPI generado → {os.path.basename(ruta_salida)}")


if __name__ == "__main__":
    base    = os.path.dirname(os.path.abspath(__file__))
    modelos = os.path.join(base, "..", "modelos")

    mm  = metamodel_from_file(os.path.join(modelos, "pim_grammar.tx"))

    print("📐 Leyendo PIM...")
    pim = mm.model_from_file(os.path.join(modelos, "pim.api"))
    print(f"   API: {pim.name} — {len(pim.endpoints)} endpoints")

    print("\n🔁 M2M: PIM → PSM FastAPI")
    generar_psm(pim, os.path.join(modelos, "psm_fastapi.api"))
