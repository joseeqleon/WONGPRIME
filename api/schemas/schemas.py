"""
Pydantic Schemas para API
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime


class ProductoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    url_imagen: Optional[str] = None
    marca: Optional[str] = None
    categoria: Optional[str] = None


class ProductoCreate(ProductoBase):
    pass


class ProductoResponse(ProductoBase):
    id: int
    fecha_creacion: datetime
    ultima_actualizacion: datetime
    
    class Config:
        from_attributes = True


class PrecioBase(BaseModel):
    precio: float
    tienda: str
    stock: Optional[int] = None
    rating: Optional[float] = None
    url: Optional[str] = None


class PrecioResponse(PrecioBase):
    id: int
    fecha: datetime
    
    class Config:
        from_attributes = True


class ProductoConPrecios(ProductoResponse):
    precios_actuales: List[PrecioResponse] = []


class HistoricoPrecio(BaseModel):
    fecha: datetime
    precio: float
    tienda: str
    variacion_porcentual: Optional[float] = None


class ComparacionTiendas(BaseModel):
    producto_id: int
    producto: str
    marca: Optional[str]
    categoria: Optional[str]
    precio_wong: Optional[float]
    precio_metro: Optional[float]
    precio_plaza_vea: Optional[float]
    precio_minimo: Optional[float]
    precio_maximo: Optional[float]
    mejor_tienda: Optional[str]
    ahorro_maximo: Optional[float]


class AlertaCreate(BaseModel):
    producto_id: int
    email: EmailStr
    precio_objetivo: float = Field(gt=0, description="Precio objetivo debe ser mayor a 0")


class AlertaResponse(BaseModel):
    id: int
    producto_id: int
    email: str
    precio_objetivo: float
    activa: bool
    notificado: bool
    fecha_creacion: datetime
    
    class Config:
        from_attributes = True


class EstadisticasResponse(BaseModel):
    total_productos: int
    total_tiendas: int
    total_categorias: int
    total_alertas_activas: int
    ultimo_scraping: Optional[datetime]
    productos_por_tienda: dict
    productos_por_categoria: dict


class MessageResponse(BaseModel):
    message: str
    success: bool = True
