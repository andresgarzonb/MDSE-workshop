"""
TRANSFORMACIÓN 1 — M2M: Requisitos → PIM
==========================================
Lee requirements.req y genera pim.api

Las operaciones abstractas (listar, obtener, crear...)
se convierten en endpoints HTTP con método, ruta,
parámetros y tipo de respuesta.

operación  →  método HTTP  +  ruta
─────────────────────────────────────
listar     →  GET    /recursos
obtener    →  GET    /recursos/{id}
crear      →  POST   /recursos
actualizar →  PUT    /recursos/{id}
eliminar   →  DELETE /recursos/{id}
"""

from textx import metamodel_from_file
import os

# Mapa: operación abstracta → (método HTTP, tiene {id} en ruta)
OPERATION_MAP = {
    "listar":     ("GET",    False, "List[{name}]"),
    "obtener":    ("GET",    True,  "{name}"),
    "crear":      ("POST",   False, "{name}"),
    "actualizar": ("PUT",    True,  "{name}"),
    "eliminar":   ("DELETE", True,  "Message"),
}

SUMMARIES = {
    "listar":     "Listar todos los {plural}",
    "obtener":    "Obtener un {singular} por ID",
    "crear":      "Crear un nuevo {singular}",
    "actualizar": "Actualizar un {singular} existente",
    "eliminar":   "Eliminar un {singular}",
}

def generate_model_class(lineas, model):    
    for resource in model.resources:
        lineas.append(f"    modelClass {resource.name} {{")
        for field in resource.fields: 
            lineas.append(f"        {field.name} : {field.type}")
        lineas.append(f"    }}")
        lineas.append("")

def generar_pim(req_model, ruta_salida: str):
    lineas = []
    lineas.append("")
    lineas.append(f"pim {req_model.name} {{")
    lineas.append("")
    
    generate_model_class(lineas, req_model)
    

    for resource in req_model.resources:
        nombre     = resource.name                     # Producto
        ruta_base  = f"/{nombre.lower()}s"             # /productos
        singular   = nombre.lower()                    # producto
        plural     = f"{nombre.lower()}s"              # productos    

        print(f"   • {nombre}: {[op.name for op in resource.operations]}")

        for op in resource.operations:
            op_name = op.name.lower()
            if op_name not in OPERATION_MAP:
                continue

            metodo, tiene_id, resp_tpl = OPERATION_MAP[op_name]
            summary_tpl                = SUMMARIES[op_name]

            ruta     = f"{ruta_base}/{{id}}" if tiene_id else ruta_base
            response = resp_tpl.format(name=nombre)
            summary  = summary_tpl.format(singular=singular, plural=plural)

            # Parámetros
            params = []
            if tiene_id:
                params.append("id:Number")
            if op_name in ("crear", "actualizar"):
                params.append(f"body:{nombre}")
            param_str = ", ".join(params) if params else "none"

            lineas.append(f"    endpoint {metodo} {ruta} {{")
            lineas.append(f'        summary  : "{summary}"')
            lineas.append(f"        params   : {param_str}")
            lineas.append(f"        response : {response}")
            lineas.append(f"    }}")
            lineas.append("")

    lineas.append("}")

    with open(ruta_salida, "w") as f:
        f.write("\n".join(lineas))

    print(f"\n  ✅ PIM generado → {os.path.basename(ruta_salida)}")


if __name__ == "__main__":
    base    = os.path.dirname(os.path.abspath(__file__))
    modelos = os.path.join(base, "..", "modelos")

    mm  = metamodel_from_file(os.path.join(modelos, "req_grammar.tx"))

    print("📋 Leyendo requisitos de API...")
    req = mm.model_from_file(os.path.join(modelos, "requirements.req"))
    print(f"   API: {req.name} — {len(req.resources)} recursos")

    print("\n🔁 M2M: Requisitos → PIM")
    generar_pim(req, os.path.join(modelos, "pim.api"))
