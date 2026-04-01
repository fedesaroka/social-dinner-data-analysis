class DataFaltas:
    id_cena: int
    
    
    def __init__(self, id):
        self.id = id
        self.faltas: dict[str, dict[str, str]] = {}

    def cargar_falta(self, persona, razon = "", descripcion = ""):
        self.faltas[persona] = {
            "razon": razon, 
            "descripcion": descripcion,
        }

    def to_string(self):
        for persona in self.faltas.keys():
            print(persona)
            for k in self.faltas[persona].keys():
                print(k, self.faltas[persona][k])
