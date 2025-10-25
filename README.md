# UCOfit Backend

API REST para la aplicación UCOfit - una plataforma de entrenamiento y motivación deportiva.

## Características

- **Autenticación JWT**: Sistema seguro de autenticación con tokens JWT
- **Gestión de usuarios**: Registro, login, perfil y actualización de datos
- **Sistema de retos**: Creación y gestión de retos deportivos
- **Publicaciones**: Subida de videos y gestión de contenido
- **Sistema de puntuación**: Evaluación de publicaciones por otros usuarios
- **Recuperación de contraseña**: Sistema de recuperación por email
- **Manejo de archivos**: Almacenamiento de videos usando GridFS

## Tecnologías

- **FastAPI**: Framework web moderno y rápido
- **MongoDB**: Base de datos NoSQL con GridFS para archivos
- **Pydantic**: Validación de datos y serialización
- **JWT**: Autenticación basada en tokens
- **bcrypt**: Encriptación de contraseñas
- **FastAPI-Mail**: Envío de emails
- **Jinja2**: Templates para emails

## Estructura del Proyecto

```
src/
├── exceptions/          # Sistema de excepciones personalizadas
├── data/               # Conexión a base de datos
├── model/              # Modelos de datos (Pydantic)
├── router/             # Endpoints de la API
├── services/           # Servicios de negocio
├── templates/          # Templates HTML para emails
├── util/               # Utilidades y helpers
└── main.py            # Punto de entrada de la aplicación
```

## Mejoras Implementadas

### 1. Sistema de Excepciones Personalizadas
- Excepciones específicas para diferentes tipos de errores
- Manejo centralizado de errores con códigos HTTP apropiados
- Mensajes de error descriptivos y consistentes

### 2. Limpieza de Código
- Formato consistente usando Black
- Organización de importaciones con isort
- Eliminación de espacios y tabulaciones innecesarias
- Líneas de código optimizadas

### 3. Documentación Mejorada
- Docstrings completos en todas las funciones y clases
- Documentación de parámetros, valores de retorno y excepciones
- Comentarios descriptivos en el código

### 4. Buenas Prácticas
- Validación robusta de datos de entrada
- Manejo seguro de contraseñas con bcrypt
- Validación de tokens JWT
- Principios SOLID aplicados
- Código limpio y mantenible

### 5. Refactorización con Modelos Pydantic
- **Funciones simplificadas**: Reducción de argumentos múltiples usando modelos de datos
- **Validación automática**: Pydantic valida automáticamente los datos de entrada
- **Tipado fuerte**: Mejor documentación y detección de errores en tiempo de desarrollo
- **Modelos específicos**: Request/Response models para cada operación

#### Modelos Creados:
- `RetoConPublicacionRequest` - Para crear reto con publicación inicial
- `RetoConPublicacionResponse` - Respuesta de creación de reto con publicación
- `PublicacionCrearRequest` - Para crear nuevas publicaciones
- `PublicacionCrearResponse` - Respuesta de creación de publicación
- `PublicacionEditarRequest` - Para editar publicaciones existentes
- `ComentarioCrearRequest` - Para crear comentarios
- `ComentarioResponse` - Respuesta de comentarios

## Instalación

1. Clonar el repositorio
2. Crear un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Configurar variables de entorno:
   ```bash
   cp .env.example .env
   # Editar .env con tus configuraciones
   ```

5. Ejecutar la aplicación:
   ```bash
   python src/main.py
   ```

## Variables de Entorno

```env
MONGO_URI=mongodb://localhost:27017
SECRET_KEY=tu_clave_secreta_aqui
ALGORITHM=HS256
GMAIL_USERNAME=tu_email@gmail.com
GMAIL_APP_PASSWORD=tu_app_password
```

## API Endpoints

### Autenticación
- `POST /usuario/login` - Iniciar sesión
- `POST /usuario/logout` - Cerrar sesión
- `POST /usuario/registrar` - Registrar nuevo usuario

### Usuarios
- `GET /usuario/perfil` - Obtener perfil del usuario
- `PUT /usuario/actualizar` - Actualizar datos del usuario
- `DELETE /usuario/eliminar` - Eliminar cuenta

### Publicaciones
- `POST /publicacion/crear` - Crear nueva publicación
- `GET /publicacion/general` - Listar todas las publicaciones
- `GET /publicacion/reto/{reto_id}` - Publicaciones de un reto
- `GET /publicacion/usuario` - Publicaciones del usuario
- `GET /publicacion/{id}` - Obtener publicación específica
- `PUT /publicacion/editar/{id}` - Editar publicación
- `DELETE /publicacion/eliminar/{id}` - Eliminar publicación

### Retos
- `POST /reto/crear` - Crear nuevo reto
- `POST /reto/crear-con-publicacion` - Crear reto con publicación inicial
- `GET /reto/listar` - Listar retos disponibles
- `GET /reto/{id}` - Obtener reto específico
- `PUT /reto/editar/{id}` - Editar reto
- `DELETE /reto/eliminar/{id}` - Eliminar reto

### Comentarios
- `POST /comentario/comentar/{publicacion_id}` - Agregar comentario a publicación

## Ejemplos de Uso

### Crear Reto con Publicación Inicial
```json
POST /reto/crear-con-publicacion
Content-Type: multipart/form-data

{
  "titulo_reto": "Reto de 30 días de ejercicio",
  "descripcion_reto": "Completa 30 días consecutivos de ejercicio",
  "titulo_publicacion": "Mi primer día",
  "descripcion_publicacion": "Empezando mi reto de ejercicio",
  "video": [archivo de video]
}
```

### Crear Publicación
```json
POST /publicacion/crear
Content-Type: multipart/form-data

{
  "titulo": "Mi progreso día 5",
  "descripcion": "Completando el día 5 del reto",
  "reto_id": "64a1b2c3d4e5f6789012345",
  "video": [archivo de video]
}
```

### Agregar Comentario
```json
POST /comentario/comentar/64a1b2c3d4e5f6789012345
Content-Type: application/json

{
  "comentario": "¡Excelente progreso!",
  "publicacion_id": "64a1b2c3d4e5f6789012345"
}
```

## Desarrollo

### Herramientas de Calidad de Código

El proyecto incluye configuración para:

- **Black**: Formateador de código automático
- **isort**: Organizador de importaciones
- **Pylint**: Analizador estático de código

### Ejecutar Herramientas de Calidad

```bash
# Formatear código
black src/

# Organizar importaciones
isort src/

# Verificar calidad de código
pylint src/
```

## Contribución

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.
