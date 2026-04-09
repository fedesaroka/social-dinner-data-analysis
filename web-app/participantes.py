import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return round(R * 2 * math.asin(math.sqrt(a)), 2)


class DataParticipantes:
    id_cena: int
    casa_cena: str
    participantes: dict[str, dict] = {}

    def __init__(self, id, casa, casas_coords):
        self.id_cena = id
        self.casa_cena = casa
        self.casas_coords = casas_coords  # {nombre: (lat, lon)}

    def cargar_data(self, nombre, ida, vuelta, extra):
        d_ida, d_vuelta, d_total = self._calcular_distancia(self.casa_cena, ida, vuelta)
        self.participantes[nombre] = {
            "ida": ida,
            "vuelta": vuelta,
            "distancia ida": d_ida,
            "distancia vuelta": d_vuelta,
            "distancia total": d_total,
            "extras": extra
        }

    def _calcular_distancia(self, casa_cena, ida, vuelta):
        d_ida = self._distancia_entre(ida, casa_cena)
        d_vuelta = self._distancia_entre(casa_cena, vuelta)
        return d_ida, d_vuelta, round(d_ida + d_vuelta, 2)

    def _distancia_entre(self, origen, destino):
        if origen == destino:
            return 0
        coords_origen = self.casas_coords.get(origen)
        coords_destino = self.casas_coords.get(destino)
        if coords_origen and coords_destino:
            return haversine(coords_origen[0], coords_origen[1], coords_destino[0], coords_destino[1])
        return 0