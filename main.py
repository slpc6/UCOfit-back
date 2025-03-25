# Punto de inicio del api para la aplicaciopn UCOfit

# External libraries
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import importlib
import pkgutil
import uvicorn

# Internal libraries
from path import path


app = FastAPI(version="1.0.0", title="UCOfit API", description="")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


for _, module_name, _ in pkgutil.iter_modules([path.routers]):
    module = importlib.import_module(f"routers.{module_name}")
    if hasattr(module, "router"):
        app.include_router(module.router)


if __name__ == "__main__":
    """Punto de inicio de la aplicacion, corre el servidor."""
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
