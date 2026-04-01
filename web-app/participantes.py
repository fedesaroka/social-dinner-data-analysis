class DataParticipantes:
    id_cena: int
    casa_cena: str
    participantes: dict[str, dict] = {}

    def __init__(self, id, casa):
        self.id_cena = id
        self.casa_cena = casa

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

    def _calcular_distancia(self, casa, ida, vuelta):
        if ida == casa:
            d_ida = 0
        else: 
            d_ida = 1
        if vuelta == casa:
            d_vuelta = 0
        else:
            d_vuelta = 1
        
        d_total = d_ida + d_vuelta 
        return d_ida, d_vuelta, d_total