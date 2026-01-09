from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import hashlib
import secrets
from datetime import datetime, timedelta
from jose import jwt
from typing import Dict, Any, Optional
import json
from uuid import uuid4

app = FastAPI(title="Collique Delivery API Demo", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory "database"
users_db: Dict[str, Dict] = {}
stores_db: Dict[str, Dict] = {}
admins_db: Dict[str, Dict] = {
    "admin@colliquedelivery.com": {
        "id": str(uuid4()),
        "name": "Admin Principal",
        "email": "admin@colliquedelivery.com",
        "password": "admin123",
        "role": "superadmin",
        "is_active": True
    }
}

# Security functions
SECRET_KEY = "collique_delivery_jwt_secret_2025_jsalasinnovatech"
ALGORITHM = "HS256"

def get_password_hash(password: str) -> str:
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${password_hash.hex()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        if '$' not in hashed_password:  # Simple password for demo
            return plain_password == hashed_password
        salt, stored_hash = hashed_password.split('$')
        password_hash = hashlib.pbkdf2_hmac('sha256', plain_password.encode(), salt.encode(), 100000)
        return password_hash.hex() == stored_hash
    except:
        return False

def create_access_token(subject: str, expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Routes
@app.get("/")
async def root():
    return {
        "success": True,
        "message": "Collique Delivery API Demo",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/api/v1/auth",
            "stores": "/api/v1/stores",
            "products": "/api/v1/products",
            "orders": "/api/v1/orders",
            "users": "/api/v1/users",
        },
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "success": True,
        "status": "OK",
        "service": "Collique Delivery API Demo",
        "version": "1.0.0"
    }

@app.post("/api/v1/auth/client/register")
async def register_client(request: Dict[str, Any]):
    name = request.get("name")
    email = request.get("email", "").lower()
    phone = request.get("phone")
    password = request.get("password")

    if not all([name, email, password]):
        return {
            "success": False,
            "message": "Nombre, email y contraseña son requeridos"
        }

    if email in users_db:
        return {
            "success": False,
            "message": "El email ya está registrado"
        }

    user_id = str(uuid4())
    users_db[email] = {
        "id": user_id,
        "name": name,
        "email": email,
        "phone": phone,
        "password": get_password_hash(password),
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    }

    token = create_access_token(f"{user_id}:client")

    return {
        "success": True,
        "message": "Usuario registrado exitosamente",
        "data": {
            "user": {
                "id": user_id,
                "name": name,
                "email": email,
                "phone": phone
            },
            "token": token
        }
    }

@app.post("/api/v1/auth/client/login")
async def login_client(request: Dict[str, Any]):
    email = request.get("email", "").lower()
    password = request.get("password")

    if not all([email, password]):
        return {
            "success": False,
            "message": "Email y contraseña son requeridos"
        }

    user = users_db.get(email)
    if not user or not verify_password(password, user["password"]):
        return {
            "success": False,
            "message": "Credenciales incorrectas"
        }

    if not user["is_active"]:
        return {
            "success": False,
            "message": "Cuenta desactivada. Contacta al soporte."
        }

    token = create_access_token(f"{user['id']}:client")

    return {
        "success": True,
        "message": "Login exitoso",
        "data": {
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "phone": user["phone"]
            },
            "token": token
        }
    }

@app.post("/api/v1/auth/store/register")
async def register_store(request: Dict[str, Any]):
    owner_name = request.get("owner_name")
    owner_email = request.get("owner_email", "").lower()
    owner_phone = request.get("owner_phone")
    password = request.get("password")
    store_name = request.get("store_name")
    address = request.get("address")

    if not all([owner_name, owner_email, owner_phone, password, store_name, address]):
        return {
            "success": False,
            "message": "Todos los campos son requeridos"
        }

    if owner_email in stores_db:
        return {
            "success": False,
            "message": "El email ya está registrado"
        }

    store_id = str(uuid4())
    stores_db[owner_email] = {
        "id": store_id,
        "owner_name": owner_name,
        "owner_email": owner_email,
        "owner_phone": owner_phone,
        "password": get_password_hash(password),
        "store_name": store_name,
        "description": request.get("description"),
        "address": address,
        "delivery_fee": request.get("delivery_fee", 3.00),
        "delivery_time_min": request.get("delivery_time_min", 20),
        "delivery_time_max": request.get("delivery_time_max", 40),
        "rating": 0.0,
        "is_active": True,
        "is_approved": False,
        "created_at": datetime.utcnow().isoformat()
    }

    return {
        "success": True,
        "message": "Tienda registrada. Pendiente de aprobación por el administrador.",
        "data": {
            "store": {
                "id": store_id,
                "store_name": store_name,
                "owner_email": owner_email,
                "is_approved": False
            }
        }
    }

@app.post("/api/v1/auth/store/login")
async def login_store(request: Dict[str, Any]):
    email = request.get("email", "").lower()
    password = request.get("password")

    if not all([email, password]):
        return {
            "success": False,
            "message": "Email y contraseña son requeridos"
        }

    store = stores_db.get(email)
    if not store or not verify_password(password, store["password"]):
        return {
            "success": False,
            "message": "Credenciales incorrectas"
        }

    if not store["is_active"]:
        return {
            "success": False,
            "message": "Tienda desactivada. Contacta al administrador."
        }

    if not store["is_approved"]:
        return {
            "success": False,
            "message": "Tu tienda aún no ha sido aprobada. Por favor espera la aprobación del administrador."
        }

    token = create_access_token(f"{store['id']}:store")

    return {
        "success": True,
        "message": "Login exitoso",
        "data": {
            "store": {
                "id": store["id"],
                "owner_name": store["owner_name"],
                "store_name": store["store_name"],
                "address": store["address"],
                "delivery_fee": store["delivery_fee"],
                "rating": store["rating"]
            },
            "token": token
        }
    }

@app.post("/api/v1/auth/admin/login")
async def login_admin(request: Dict[str, Any]):
    email = request.get("email", "").lower()
    password = request.get("password")

    if not all([email, password]):
        return {
            "success": False,
            "message": "Email y contraseña son requeridos"
        }

    admin = admins_db.get(email)
    if not admin or not verify_password(password, admin["password"]):
        return {
            "success": False,
            "message": "Credenciales incorrectas"
        }

    if not admin["is_active"]:
        return {
            "success": False,
            "message": "Cuenta desactivada"
        }

    token = create_access_token(f"{admin['id']}:admin")

    return {
        "success": True,
        "message": "Login exitoso",
        "data": {
            "admin": {
                "id": admin["id"],
                "name": admin["name"],
                "email": admin["email"],
                "role": admin["role"]
            },
            "token": token
        }
    }

@app.get("/api/v1/stores/")
async def get_stores():
    approved_stores = [
        {
            "id": store["id"],
            "store_name": store["store_name"],
            "description": store.get("description"),
            "address": store["address"],
            "delivery_fee": store["delivery_fee"],
            "delivery_time_min": store["delivery_time_min"],
            "delivery_time_max": store["delivery_time_max"],
            "rating": store["rating"]
        }
        for store in stores_db.values()
        if store["is_active"] and store["is_approved"]
    ]

    return {
        "success": True,
        "data": approved_stores,
        "pagination": {
            "skip": 0,
            "limit": 20,
            "total": len(approved_stores)
        }
    }

@app.get("/demo/data")
async def get_demo_data():
    """Endpoint para mostrar datos de demostración"""
    return {
        "users_count": len(users_db),
        "stores_count": len(stores_db),
        "admins_count": len(admins_db),
        "sample_users": list(users_db.keys())[:5],
        "sample_stores": list(stores_db.keys())[:5]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)