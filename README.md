# 🚀 Collique Delivery FastAPI Backend

API moderna para Collique Delivery construida con FastAPI, SQLModel y las mejores prácticas de desarrollo.

## 🌟 Características

- **FastAPI**: Framework moderno y rápido para construir APIs
- **SQLModel**: ORM declarativo con validación Pydantic integrada
- **PostgreSQL**: Base de datos robusta con soporte async
- **JWT Authentication**: Autenticación segura con tokens
- **Alembic**: Migraciones de base de datos automáticas
- **Documentación automática**: OpenAPI/Swagger integrado
- **Validación de datos**: Pydantic para validación y serialización
- **Tipado estático**: Full type hints con mypy
- **Async/Await**: Operaciones de base de datos asíncronas

## 🏗️ Arquitectura

```
app/
├── api/                    # API routes
│   └── v1/
│       ├── endpoints/      # API endpoints por módulo
│       └── api.py         # Router principal
├── core/                  # Configuración y utilidades core
│   ├── config.py         # Settings y configuración
│   ├── security.py       # JWT y autenticación
│   └── database.py       # Configuración de base de datos
├── models/               # Modelos SQLModel
└── main.py              # Aplicación FastAPI principal
```

## 🚀 Inicio rápido

### 1. Configuración del entorno

```bash
# Clonar/copiar el proyecto
cd collique_delivery_fastapi

# Instalar dependencias
pip install -r requirements.txt
# O usando Poetry:
# poetry install

# Copiar configuración
cp .env.example .env
```

### 2. Configurar variables de entorno

Edita el archivo `.env` con tus credenciales:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/collique_delivery_fastapi
SECRET_KEY=your-super-secret-key-here-change-this-in-production
```

### 3. Configurar base de datos

```bash
# Crear la base de datos
createdb collique_delivery_fastapi

# Ejecutar migraciones
alembic upgrade head

# O crear las tablas directamente (desarrollo)
python -c "
import asyncio
from app.core.database import init_db
asyncio.run(init_db())
"
```

### 4. Ejecutar servidor

```bash
# Desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Producción
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📚 API Endpoints

### Autenticación
- `POST /api/v1/auth/client/register` - Registro de cliente
- `POST /api/v1/auth/client/login` - Login de cliente
- `POST /api/v1/auth/store/register` - Registro de tienda
- `POST /api/v1/auth/store/login` - Login de tienda
- `POST /api/v1/auth/admin/login` - Login de administrador
- `GET /api/v1/auth/profile` - Obtener perfil actual

### Tiendas
- `GET /api/v1/stores/` - Listar tiendas
- `GET /api/v1/stores/{store_id}` - Obtener tienda por ID
- `PUT /api/v1/stores/me` - Actualizar mi tienda
- `GET /api/v1/stores/admin/pending` - Tiendas pendientes (admin)
- `POST /api/v1/stores/{store_id}/approve` - Aprobar tienda (admin)

## 🔧 Desarrollo

### Migraciones de base de datos

```bash
# Crear nueva migración
alembic revision --autogenerate -m "Add new table"

# Aplicar migraciones
alembic upgrade head

# Revertir migración
alembic downgrade -1
```

### Comandos útiles

```bash
# Formatear código
black app/
isort app/

# Verificar tipos
mypy app/

# Ejecutar tests
pytest

# Pre-commit hooks
pre-commit install
pre-commit run --all-files
```

## 🌍 Mejores prácticas implementadas

### 1. **Arquitectura modular**
- Separación clara de responsabilidades
- Modelos, rutas y lógica de negocio separados
- Configuración centralizada

### 2. **Validación robusta**
- Modelos Pydantic para entrada y salida
- Validación automática de tipos
- Mensajes de error claros

### 3. **Seguridad**
- JWT tokens para autenticación
- Hashing seguro de contraseñas con bcrypt
- Validación de roles y permisos

### 4. **Base de datos**
- Pool de conexiones async
- Transacciones automáticas
- Migraciones versionadas

### 5. **Documentación**
- OpenAPI/Swagger automático en `/docs`
- ReDoc en `/redoc`
- Docstrings en todas las funciones

## 🔌 Extensiones futuras

El proyecto está preparado para agregar:

- **Products endpoints** - Gestión de productos
- **Orders endpoints** - Sistema de pedidos
- **Cart endpoints** - Carrito de compras
- **File upload** - Subida de imágenes
- **Email notifications** - Notificaciones por correo
- **Real-time updates** - WebSockets
- **Background tasks** - Celery para tareas asíncronas
- **Caching** - Redis para caché

## 📊 Monitoreo

```bash
# Health check
curl http://localhost:8000/health

# Documentación
open http://localhost:8000/docs
```

## 🚀 Despliegue

### Docker (Recomendado)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Railway/Heroku

El proyecto está configurado para despliegue directo en:
- Railway
- Heroku
- Vercel
- DigitalOcean App Platform

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add some amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## 📝 Licencia

MIT License - ver el archivo [LICENSE](LICENSE) para detalles.

## 👨‍💻 Autor

**JSALASINNOVATECH**
Email: admin@colliquedelivery.com

---

🚀 **¡Happy Coding!** 🚀