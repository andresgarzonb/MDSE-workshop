# MDSE — API REST con TextX y FastAPI
## Requisitos → PIM → PSM → Código

---

## Estructura del proyecto

```
mdse_api/
│
├── pipeline.py                    ← Ejecuta TODO el flujo de una sola vez
│
├── modelos/
│   ├── requirements.req           ← ENTRADA: el analista describe recursos y operaciones
│   ├── pim.api                    ← M2M: operaciones → endpoints HTTP abstractos
│   └── psm_fastapi.api            ← M2M: tipos abstractos → tipos Python/Pydantic
│
├── generadores/
│   ├── step1_req_to_pim.py        ← M2M: Requisitos → PIM
│   ├── step2_pim_to_psm.py        ← M2M: PIM → PSM FastAPI
│   └── step3_psm_to_code.py       ← M2T: PSM → código Python real
│
└── salida/
    ├── schemas.py                 ← Modelos Pydantic (validación automática)
    └── main.py                    ← App FastAPI ejecutable con todos los endpoints
```

---

## Cómo ejecutarlo

```bash
# 1. Instalar dependencias
pip install textx fastapi uvicorn

# 2. Ejecutar el pipeline completo
python pipeline.py

# 3. Levantar la API generada
cd salida
uvicorn main:app --reload

# 4. Abrir la documentación interactiva automática
# → http://localhost:8000/docs
```

---

## El flujo visualizado

```
requirements.req          pim.api                psm_fastapi.api         salida/
─────────────────         ───────────────────    ───────────────────     ──────────────────────
resource Producto    M2M► endpoint GET           route GET "/productos"  @app.get("/productos")
  operations:             /productos {      M2M►   response: List[Producto] response_model=List[Producto]
    listar                  response:               status: 200         def get_productos():
    obtener                 List[Producto]        }                         return productos_db
    crear               }
    actualizar
    eliminar
```

---

## La transformación más poderosa para mostrar en la charla

Mostrar cómo **una sola operación** en los requisitos recorre todos los niveles:

```
requirements.req          pim.api                  psm_fastapi.api         main.py
────────────────          ───────────────────      ─────────────────       ─────────────────────────
operations: crear   M2M►  endpoint POST            route POST "/productos"  @app.post("/productos",
                          /productos {        M2M►   body: Producto            response_model=Producto,
                            params: body:Prod         response: Producto        status_code=201)
                            response: Producto        status: 201           def post_productos(data: Producto):
                          }                                                     productos_db.append(data)
                                                                                return data
```

Una línea en el `.req` → decorador FastAPI completo con validación Pydantic.

---

## Guión para la charla (7-10 minutos)

### Apertura — el problema
> "Cada vez que construimos una API, escribimos lo mismo:
> los endpoints, los modelos de validación, los status codes...
> ¿Y si solo describiéramos QUÉ queremos, y la máquina escribiera CÓMO?"

---

### Paso 1 — Mostrar `requirements.req`
> "El analista escribe esto. No conoce FastAPI. No conoce Pydantic.
> Solo sabe que existe un recurso 'Producto' y que se puede
> listar, obtener, crear, actualizar y eliminar."

**Punto clave:** `operations: listar, obtener, crear` es vocabulario del dominio,
no de ningún framework.

---

### Paso 2 — Ejecutar step1, mostrar `pim.api`
> "La primera transformación convierte esas operaciones abstractas
> en endpoints HTTP. 'listar' se convierte en GET /productos.
> 'crear' en POST /productos. 'obtener' en GET /productos/{id}.
> Esta lógica está en el generador, no la escribimos a mano cada vez."

Mostrar el mapeo en el código:
```python
OPERATION_MAP = {
    "listar":     ("GET",    False, "List[{name}]"),
    "crear":      ("POST",   False, "{name}"),
    "obtener":    ("GET",    True,  "{name}"),
    "eliminar":   ("DELETE", True,  "Message"),
}
```

---

### Paso 3 — Ejecutar step2, mostrar `psm_fastapi.api`
> "Ahora tenemos un PSM: el mismo modelo pero expresado en
> el lenguaje de FastAPI. Tipos Python concretos, status codes,
> path params con nombre específico. Ya es 100% FastAPI,
> pero todavía no es código."

---

### Paso 4 — Ejecutar step3, mostrar `schemas.py` y `main.py`
> "Y aquí está el resultado. Un archivo de schemas Pydantic
> con ejemplos incluidos. Y una app FastAPI completa con
> todos los endpoints, decoradores, validaciones y manejo de errores."

**El momento WOW:** abrir `http://localhost:8000/docs` en vivo.
FastAPI genera documentación interactiva automáticamente.
El modelo generó código, y el código generó documentación.

---

### Crear imágenes

```bash
#Crear archivo .dot
textx generate modelos/psm_fastapi.api --grammar modelos/psm_grammar.tx --target dot
# Convertir a PNG
dot -Tpng -O modelos/psm_fastapi.dot

```


textx generate modelos/psm_fastapi.api --grammar modelos/psm_grammar.tx --target dot

### Cierre — conectar con el ejemplo anterior
> "En el ejemplo anterior, el mismo modelo de Producto
> generaba clases Python Y tablas SQL.
> Ahora generamos una API REST completa.
> Mismo concepto MDSE, distinto dominio.
> La fuente de verdad siempre es el modelo."

---

## Diferencias clave respecto al ejemplo de BD

| Aspecto              | Ejemplo BD                    | Este ejemplo (API)            |
|----------------------|-------------------------------|-------------------------------|
| Requisito abstracto  | campos sin tipo               | operaciones (listar, crear…)  |
| PIM                  | entidades con tipos abstractos| endpoints HTTP abstractos      |
| PSM                  | tipos Python / SQL            | tipos Pydantic + status codes |
| Salida M2T           | clases + CREATE TABLE         | schemas.py + main.py FastAPI  |
| Se puede ejecutar    | No directamente               | Sí: `uvicorn main:app --reload` |
