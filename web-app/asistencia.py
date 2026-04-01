import datetime

class DataAsistencia:
    id_cena: int
    fecha: datetime

    def __init__(self,id, fecha):
        self.id_cena = id
        self.fecha = fecha
        self.asistencias: dict[str, float] = {}

    def cargar_asistencia(self, persona, asistencia):
        if asistencia != 1 and asistencia != 0 and asistencia != 0.5:
            raise ValueError
        self.asistencias[persona] = asistencia