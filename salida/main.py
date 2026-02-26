# ==========================================================
# APLICACIÓN FASTAPI — GENERADA AUTOMÁTICAMENTE
# Fuente: psm_fastapi.api  |  NO EDITAR
# ==========================================================
# Para ejecutar:
#   pip install fastapi uvicorn
#   uvicorn main:app --reload
# ==========================================================

from fastapi import FastAPI, HTTPException
from typing import List
from schemas import Cliente, Factura, Pedido, Producto

app = FastAPI(title="TiendaOnline", version="1.0.0")

# Base de datos simulada en memoria
productos_db: List[Producto] = []
clientes_db: List[Cliente] = []
pedidos_db: List[Pedido] = []
facturas_db: List[Factura] = []


@app.get("/productos", response_model=List[Producto])
def get_productos():
    """Listar todos los productos"""
    return productos_db


@app.get("/productos/{producto_id}", response_model=Producto)
def get_productos_producto_id(producto_id: int):
    """Obtener un producto por ID"""
    item = next((i, x) for i, x in enumerate(productos_db) if i == producto_id)
    if not item:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return item


@app.post("/productos", response_model=Producto, status_code=201)
def post_productos(data: Producto):
    """Crear un nuevo producto"""
    productos_db.append(data)
    return data


@app.put("/productos/{producto_id}", response_model=Producto)
def put_productos_producto_id(producto_id: int, data: Producto):
    """Actualizar un producto existente"""
    if producto_id >= len(productos_db):
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    productos_db[producto_id] = data
    return data


@app.delete("/productos/{producto_id}", response_model=dict)
def delete_productos_producto_id(producto_id: int):
    """Eliminar un producto"""
    if producto_id >= len(productos_db):
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    productos_db.pop(producto_id)
    return {"message": "Producto eliminado correctamente"}


@app.get("/clientes", response_model=List[Cliente])
def get_clientes():
    """Listar todos los clientes"""
    return clientes_db


@app.get("/clientes/{cliente_id}", response_model=Cliente)
def get_clientes_cliente_id(cliente_id: int):
    """Obtener un cliente por ID"""
    item = next((i, x) for i, x in enumerate(clientes_db) if i == cliente_id)
    if not item:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return item


@app.post("/clientes", response_model=Cliente, status_code=201)
def post_clientes(data: Cliente):
    """Crear un nuevo cliente"""
    clientes_db.append(data)
    return data


@app.delete("/clientes/{cliente_id}", response_model=dict)
def delete_clientes_cliente_id(cliente_id: int):
    """Eliminar un cliente"""
    if cliente_id >= len(clientes_db):
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    clientes_db.pop(cliente_id)
    return {"message": "Cliente eliminado correctamente"}


@app.get("/pedidos", response_model=List[Pedido])
def get_pedidos():
    """Listar todos los pedidos"""
    return pedidos_db


@app.get("/pedidos/{pedido_id}", response_model=Pedido)
def get_pedidos_pedido_id(pedido_id: int):
    """Obtener un pedido por ID"""
    item = next((x for x in pedidos_db if x.numero == pedido_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return item


@app.post("/pedidos", response_model=Pedido, status_code=201)
def post_pedidos(data: Pedido):
    """Crear un nuevo pedido"""
    pedidos_db.append(data)
    return data


@app.get("/facturas", response_model=List[Factura])
def get_facturas():
    """Listar todos los facturas"""
    return facturas_db


@app.get("/facturas/{factura_id}", response_model=Factura)
def get_facturas_factura_id(factura_id: int):
    """Obtener un factura por ID"""
    item = next((i, x) for i, x in enumerate(facturas_db) if i == factura_id)
    if not item:
        raise HTTPException(status_code=404, detail="Factura no encontrado")
    return item


@app.post("/facturas", response_model=Factura, status_code=201)
def post_facturas(data: Factura):
    """Crear un nuevo factura"""
    facturas_db.append(data)
    return data

