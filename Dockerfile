# Usamos la imagen oficial de Python como base
FROM python:3.12-alpine

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /UCOfit-back

# Copiamos los archivos necesarios al contenedor
COPY . .

# Instalamos las dependencias dentro de un entorno virtual
RUN python -m venv /UCOfit-back/venv \
    && /UCOfit-back/venv/bin/pip install --upgrade pip \
    && /UCOfit-back/venv/bin/pip install -r requirements.txt

# Exponemos el puerto 80 para acceder a la API
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["/UCOfit-back/venv/bin/python", "src/main.py"]
