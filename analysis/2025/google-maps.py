import googlemaps
import os
from dotenv import load_dotenv
import pandas as pd

casas = pd.read_csv('casa.csv')
cena = pd.read_excel('cena.xlsx')
cena_participantes_iv = pd.read_excel("cena_participantes.xlsx")

# 1) Cargar API key
load_dotenv()
api_key = os.getenv("GOOGLE_MAPS_API_KEY")
gmaps = googlemaps.Client(key=api_key)

MENSAJE_NO_SE_PUDO = "No se pudo calcular la distancia"

# ---- Ajustá estos nombres si en tu df 'casas' son distintos ----
CASAS_COL_NOMBRE = "casa"
CASAS_COL_LAT = "latitud"
CASAS_COL_LON = "longitud"

# 2) Lookup de coordenadas (nombre -> (lat, lon))
coords_map = {
    row[CASAS_COL_NOMBRE]: (float(row[CASAS_COL_LAT]), float(row[CASAS_COL_LON]))
    for _, row in casas[[CASAS_COL_NOMBRE, CASAS_COL_LAT, CASAS_COL_LON]].dropna().iterrows()
}

def get_coords(name):
    if pd.isna(name) or name in {"-", "nan"}:
        return None
    return coords_map.get(name, None)

# 3) Traer "casa" a la tabla de asistencia (join por id_cena)
cp = cena_participantes_iv.merge(cena[["id_cena", "casa"]], on="id_cena", how="left")

# 4) Cache para no llamar a la API si la ruta se repite
dist_cache = {}
alertas = []

def km_directions(origen_coords, destino_coords, row_info=""):
    if origen_coords is None or destino_coords is None:
        return None

    # mismas coords => 0
    if origen_coords == destino_coords:
        return 0.0

    key = (origen_coords, destino_coords)
    if key in dist_cache:
        return dist_cache[key]

    try:
        res = gmaps.directions(origen_coords, destino_coords, mode="driving")
    except Exception as e:
        alertas.append(f"[ERROR API] {row_info} -> {e}")
        dist_cache[key] = None
        return None

    if not res:
        alertas.append(f"[NO ROUTE DRIVING] {row_info}")
        dist_cache[key] = None
        return None

    try:
        meters = res[0]["legs"][0]["distance"]["value"]
        km = round(meters / 1000, 2)
        dist_cache[key] = km
        return km
    except Exception as e:
        alertas.append(f"[PARSE ERROR] {row_info} -> {e}")
        dist_cache[key] = None
        return None

# 5) Calcular distancias por fila
dist_ida = []
dist_vuelta = []
dist_total = []

for r in cp.itertuples(index=False):
    ida = getattr(r, "ida")
    vuelta = getattr(r, "vuelta")
    casa = getattr(r, "casa")

    # Regla: si hay '-' o 'nan' => no se puede calcular
    if ida in {"-", "nan"} or vuelta in {"-", "nan"} or casa in {"-", "nan"} or pd.isna(ida) or pd.isna(vuelta) or pd.isna(casa):
        dist_ida.append(MENSAJE_NO_SE_PUDO)
        dist_vuelta.append(MENSAJE_NO_SE_PUDO)
        dist_total.append(MENSAJE_NO_SE_PUDO)
        continue

    o = get_coords(ida)
    h = get_coords(casa)
    d = get_coords(vuelta)

    # Si falta alguna coordenada en el CSV => no se puede
    if o is None or h is None or d is None:
        dist_ida.append(MENSAJE_NO_SE_PUDO)
        dist_vuelta.append(MENSAJE_NO_SE_PUDO)
        dist_total.append(MENSAJE_NO_SE_PUDO)
        continue

    row_info = f"id_cena={getattr(r,'id_cena')} | {getattr(r,'nombre')} | ida={ida} | casa={casa} | vuelta={vuelta}"

    km1 = km_directions(o, h, row_info=row_info + " | ida->casa")
    km2 = km_directions(h, d, row_info=row_info + " | casa->vuelta")

    if km1 is None or km2 is None:
        dist_ida.append(MENSAJE_NO_SE_PUDO if km1 is None else km1)
        dist_vuelta.append(MENSAJE_NO_SE_PUDO if km2 is None else km2)
        dist_total.append(MENSAJE_NO_SE_PUDO)
    else:
        dist_ida.append(km1)
        dist_vuelta.append(km2)
        dist_total.append(round(km1 + km2, 2))

# 6) Agregar columnas a cena_participantes_iv (sin exponer 'casa')
cp["distancia ida"] = dist_ida
cp["distancia vuelta"] = dist_vuelta
cp["distancia total"] = dist_total

cena_participantes_iv = cp[[
    "id_cena", "nombre", "extras", "ida", "vuelta",
    "distancia ida", "distancia vuelta", "distancia total"
]].reset_index(drop=True)

# 7) Alertas
if alertas:
    print("ALERTAS (rutas driving no disponibles / errores):")
    for a in alertas[:50]:
        print("-", a)
    if len(alertas) > 50:
        print(f"... y {len(alertas)-50} más")
else:
    print("Sin alertas.")
