import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
import os

# Configuración de logs
logging.basicConfig(level=logging.DEBUG)

# Configuración de la base de datos
DATABASE_URL = os.getenv("postgresql://sofutu_ai_db_user:1z9m2km53znqorHOAj380ChYgs04Gmpl@dpg-cv1ak452ng1s73874sog-a/sofutu_ai_dbr")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo de Usuario
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

# Crear tablas
Base.metadata.create_all(bind=engine)

# Seguridad para contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Clase para recibir datos de registro
class UserCreate(BaseModel):
    username: str
    password: str

# Instancia de FastAPI
app = FastAPI()

# Endpoint para registrar usuarios
@app.post("/register")
def register(user: UserCreate):
    logging.debug("Iniciando proceso de registro...")
    db = SessionLocal()
    try:
        logging.debug(f"Verificando si el usuario '{user.username}' ya existe...")
        existing_user = db.query(User).filter(User.username == user.username).first()
        if existing_user:
            logging.warning(f"El usuario '{user.username}' ya existe.")
            raise HTTPException(status_code=400, detail="El usuario ya existe")
        
        logging.debug(f"Hasheando contraseña para el usuario '{user.username}'...")
        hashed_password = pwd_context.hash(user.password)
        
        logging.debug(f"Creando nuevo usuario '{user.username}' en la base de datos...")
        new_user = User(username=user.username, hashed_password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logging.info(f"Usuario '{user.username}' registrado exitosamente.")
        return {"message": "Usuario registrado exitosamente"}
    except Exception as e:
        logging.error(f"Error durante el registro: {e}")
        raise
    finally:
        logging.debug("Cerrando sesión de la base de datos...")
        db.close()