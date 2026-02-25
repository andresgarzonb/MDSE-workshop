# MDSE — API REST con TextX y FastAPI
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

## Generar imágenes

```bash
#Crear archivo .dot
textx generate modelos/psm_fastapi.api --grammar modelos/psm_grammar.tx --target dot
# Convertir a PNG
dot -Tpng -O modelos/psm_fastapi.dot

```