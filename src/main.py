"""Punto de inicio del api para la aplicaciopn UCOfit"""

import importlib
import pkgutil
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv


from util.path import Path


app = FastAPI(version="1.0.0",
              title="UCOfit API",
              description="Aplicacion de entrenamiento y motivacion para el deporte")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://192.168.1.51:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

for _, module_name, _ in pkgutil.iter_modules([Path.ROUTERS]):
    module = importlib.import_module(f"router.{module_name}")
    if hasattr(module, "router"):
        app.include_router(module.router)


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
    load_dotenv()
