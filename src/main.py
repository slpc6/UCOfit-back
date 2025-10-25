"""Punto de inicio del API para la aplicación UCOfit."""

import importlib
import pkgutil
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from dotenv import load_dotenv

from util.path import Path
from exceptions.custom_exceptions import UCOfitException
from exceptions.exception_handlers import (
    ucofit_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)


load_dotenv()

app = FastAPI(
    version="1.0.0",
    title="UCOfit API",
    description="Aplicación de entrenamiento y motivación para el deporte",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.add_exception_handler(UCOfitException, ucofit_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

for _, module_name, _ in pkgutil.iter_modules([Path.ROUTERS]):
    module = importlib.import_module(f"router.{module_name}")
    if hasattr(module, "router"):
        app.include_router(module.router)


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
