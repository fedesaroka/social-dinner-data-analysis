import gspread
from oauth2client.service_account import ServiceAccountCredentials

class DriveConfiguration:

    def __init__(self):
        self.scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        self.creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", self.scope)
        self.client = gspread.authorize(self.creds)
        self.spreadsheet = self.client.open("Asistencia Mosca Nuevo")
        self.sheet_asistencia = self.spreadsheet.worksheet("Data asistencia")
        self.sheet_data = self.spreadsheet.worksheet("Data cena")
        self.sheet_inasistencias = self.spreadsheet.worksheet("Data faltas")
        self.sheet_participantes = self.spreadsheet.worksheet("Cena participantes")
        self.sheet_casas = self.spreadsheet.worksheet("Casas")
        self.sheet_comidas = self.spreadsheet.worksheet("Comidas")
