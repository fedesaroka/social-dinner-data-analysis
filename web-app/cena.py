from datetime import datetime
import string
from typing import List


class DataCena:
    id_cena: int
    fecha_cena: datetime
    quorum: bool
    realizada: bool
    comida: str
    categoria_comida: str
    tipo_comida: str
    precio: float
    precio_usd: float
    casa: str
    tema: str
    postre: str
    cantidad_personas: int
    temperatura_c: float
    sensacion_termica_c: float
    humedad_relativa_pct: float
    precipitacion_mm: float
    velocidad_viento_kmh: float

    def __init__(self, id, fecha, quorum, realizada, comida, categoria_comida, tipo_comida, precio, casa, tema, postre, cantidad_personas):
        self.id_cena = id
        self.fecha_cena = fecha
        self.quorum = quorum
        self.realizada = realizada
        self.comida = comida
        self.categoria_comida = categoria_comida
        self.tipo_comida = tipo_comida
        self.precio = precio
        self.precio_usd = 0
        self.casa = casa
        self.tema = tema
        self.postre = postre
        self.cantidad_personas = cantidad_personas
        self.temperatura_c = 0
        self.sensacion_termica_c = 0
        self.humedad_relativa_pct = 0
        self.precipitacion_mm = 0
        self.velocidad_viento_kmh = 0
