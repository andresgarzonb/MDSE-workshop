"""
PIPELINE COMPLETO — MDSE API REST con TextX
============================================

  requirements.req
       │
       │  [M2M] Operaciones abstractas → Endpoints HTTP
       ▼
    pim.api
       │
       │  [M2M] Tipos abstractos → Tipos Python/Pydantic + Status codes
       ▼
  psm_fastapi.api
       │
       ├──[M2T]──► salida/schemas.py   (modelos Pydantic)
       └──[M2T]──► salida/main.py      (app FastAPI ejecutable)

Uso:
    python pipeline.py

Para ejecutar la API generada:
    pip install fastapi uvicorn
    cd salida
    uvicorn main:app --reload
    # Abrir http://localhost:8000/docs
"""

import sys
import os

base = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(base, "generadores"))

from textx import metamodel_from_file, metamodel_from_str
import step1_req_to_pim  as paso1
import step2_pim_to_psm  as paso2
import step3_psm_to_code as paso3


def run():
    modelos = os.path.join(base, "modelos")
    salida  = os.path.join(base, "salida")
    os.makedirs(salida, exist_ok=True)

    print("=" * 60)
    print("  PIPELINE MDSE — API REST TiendaOnline")
    print("=" * 60)

    # ── PASO 1: Requisitos → PIM ──────────────────────────────
    print("\n📋 PASO 1 — Leyendo Requisitos")
    mm_req = metamodel_from_file(os.path.join(modelos, "req_grammar.tx"))
    req    = mm_req.model_from_file(os.path.join(modelos, "requirements.req"))
    print(f"req_model {req.resources[0].fields[0].type}")
    print(f"   API '{req.name}': {len(req.resources)} recursos")
    for r in req.resources:
        ops = [op.name for op in r.operations]
        print(f"   • {r.name}: {ops}")

    print("\n🔁 M2M: Requisitos → PIM")
    paso1.generar_pim(req, os.path.join(modelos, "pim.api"))

    # ── PASO 2: PIM → PSM ─────────────────────────────────────
    print("\n📐 PASO 2 — Leyendo PIM")
    mm_pim = metamodel_from_file(os.path.join(modelos, "pim_grammar.tx"))
    pim    = mm_pim.model_from_file(os.path.join(modelos, "pim.api"))
    print(f"   {len(pim.endpoints)} endpoints en el PIM")
    print(f"   {len(pim.modelClasses)} modelClasses en el PIM")

    print("\n🔁 M2M: PIM → PSM FastAPI")
    paso2.generar_psm(pim, os.path.join(modelos, "psm_fastapi.api"))

    # ── PASO 3: PSM → Código ──────────────────────────────────
    print("\n⚙️  PASO 3 — Generando código FastAPI")
    mm_psm = metamodel_from_file(os.path.join(modelos, "psm_grammar.tx"))
    psm    = mm_psm.model_from_file(os.path.join(modelos, "psm_fastapi.api"))
    print(f"   {len(psm.schemas)} schemas, {len(psm.routes)} routes")

    print("\n📝 M2T: PSM → schemas.py")
    paso3.generar_schemas(psm, os.path.join(salida, "schemas.py"))

    print("\n📝 M2T: PSM → main.py")
    paso3.generar_main(psm, os.path.join(salida, "main.py"))

    # ── Resumen ───────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  ✅ PIPELINE COMPLETADO")
    print("=" * 60)
    print(f"\n  Modelos intermedios  →  modelos/")
    print(f"    • requirements.req    (entrada — escrito por el analista)")
    print(f"    • pim.api             (M2M — endpoints HTTP abstractos)")
    print(f"    • psm_fastapi.api     (M2M — tipos Python/Pydantic concretos)")
    print(f"\n  Código generado      →  salida/")
    print(f"    • schemas.py          (modelos Pydantic)")
    print(f"    • main.py             (app FastAPI ejecutable)")
    print(f"\n  Para ejecutar la API:")
    print(f"    pip install fastapi uvicorn")
    print(f"    cd salida && uvicorn main:app --reload")
    print(f"    → http://localhost:8000/docs")
    print()


if __name__ == "__main__":
    run()
