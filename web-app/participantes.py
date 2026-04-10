import requests

ORS_URL = "https://api.openrouteservice.org/v2/directions/driving-car"

def _ors_distancia_km(lat1, lon1, lat2, lon2, api_key):
    headers = {"Authorization": api_key}
    params = {"start": f"{lon1},{lat1}", "end": f"{lon2},{lat2}"}
    response = requests.get(ORS_URL, headers=headers, params=params, timeout=10)
    response.raise_for_status()
    metros = response.json()["features"][0]["properties"]["segments"][0]["distance"]
    return round(metros / 1000, 2)


class DataParticipantes:
    id_cena: int
    casa_cena: str
    participantes: dict[str, dict] = {}

    def __init__(self, id, casa, casas_coords, ors_api_key):
        self.id_cena = id
        self.casa_cena = casa
        self.casas_coords = casas_coords  # {nombre: (lat, lon)}
        self.ors_api_key = ors_api_key
        self._cache = {}  # evita llamadas duplicadas para el mismo par

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
        if not coords_origen or not coords_destino:
            return 0
        par = (origen, destino)
        if par not in self._cache:
            try:
                self._cache[par] = _ors_distancia_km(
                    coords_origen[0], coords_origen[1],
                    coords_destino[0], coords_destino[1],
                    self.ors_api_key
                )
            except Exception:
                self._cache[par] = 0
        return self._cache[par]