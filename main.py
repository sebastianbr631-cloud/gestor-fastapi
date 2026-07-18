from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from typing import Annotated
from pydantic import BaseModel, StringConstraints, field_validator
import database as db
from helpers import dni_valido



class ModeloCliente(BaseModel):
    dni: Annotated[str, StringConstraints(min_length=3, max_length=3)]
    nombre:Annotated[str, StringConstraints(min_length=2, max_length=30)]
    apellido: Annotated[str, StringConstraints(min_length=2, max_length=30)]

class ModeloCrearCliente(ModeloCliente):
    @field_validator('dni')
    @classmethod
    def validar_dni(cls, dni):
        if dni_valido(dni, db.Clientes.lista):
            return dni
        raise ValueError("Cliente ya existente o DNI incorrecto")


app = FastAPI(
    title="API del gestor de clientes",
    description="Ofrece diferentes funciones para gestionar los clientes."
)


@app.get('/', tags=["Inicio"])
async def Inicio():
    return {"mensaje": "API del gestor de clientes funcionando correctamente",
        "documentacion": "/docs"}
        
@app.get("/clientes/", tags=["Clientes"])
async def clientes():
    content = [cliente.to_dict() for cliente in db.Clientes.lista]
    return JSONResponse(content=content)

@app.get('/clientes/buscar/{dni}', tags=["Clientes"])
async def clientes_buscar(dni: str):
    cliente = db.Clientes.buscar(dni=dni)
    if not cliente :
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return JSONResponse(content=cliente.to_dict())


@app.post('/clientes/crear/', tags=["Clientes"])
async def clientes_crear(datos: ModeloCrearCliente):
    cliente = db.Clientes.crear(datos.dni, datos.nombre, datos.apellido)
    if cliente:
        return JSONResponse(content=cliente.to_dict())
    raise HTTPException(status_code=404, detail="Cliente no creado")


@app.put('/clientes/actualizar', tags=["Clientes"])
async def clientes_actualizar(datos: ModeloCliente):
    if db.Clientes.buscar(datos.dni):
        cliente = db.Clientes.modificar(datos.dni, datos.nombre, datos.apellido)
        if cliente:
            return JSONResponse(content=cliente.to_dict(),)
    raise HTTPException(status_code=404, detail="Cliente no encontrado")

@app.delete('/clientes/borrar/{dni}/', tags=["Clientes"])
async def clientes_borrar(dni: str):
    if db.Clientes.buscar(dni):
        cliente = db.Clientes.borrar(dni=dni)
        return JSONResponse(content=cliente.to_dict())
    raise HTTPException(status_code=404, detail="Cliente no encontrado")



print("Servidor de la API...")