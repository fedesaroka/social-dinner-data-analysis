import requests

# =========================
# CONFIG
# =========================
TZ = "America/Argentina/Buenos_Aires"

# métricas (Open-Meteo Archive)
HOURLY_VARS = [
    "temperature_2m",
    "apparent_temperature",
    "relative_humidity_2m",
    "precipitation",
    "windspeed_10m",
]

# columnas en castellano (output)
SPANISH_COLS = {
    "temperature_2m": "temperatura_c",
    "apparent_temperature": "sensacion_termica_c",
    "relative_humidity_2m": "humedad_relativa_pct",
    "precipitation": "precipitacion_mm",
    "windspeed_10m": "velocidad_viento_kmh",
}

# horas a promediar: 21, 22, 23, 0 (21:00 a 00:59)
HOURS = {21, 22, 23, 0}

# =========================
# 1) Lookup coords desde 'casas'
# (asumo columnas: nombre, lat, lon)
# =========================
coords_map = {
    r["casa"]: (float(r["latitud"]), float(r["longitud"]))
    for _, r in casas[["casa", "latitud", "longitud"]].dropna().iterrows()
}

def get_coords_or_none(place_name):
    if pd.isna(place_name) or place_name in {"-", "nan"}:
        return None
    return coords_map.get(place_name, None)

# =========================
# 2) Función para pedir clima y promediar 21–00
# =========================
weather_cache = {}  # (lat, lon, fecha_str) -> dict métricas promediadas o None

def fetch_weather_avg_21_to_00_nextday(lat, lon, fecha_str):
    """
    Promedia 21,22,23 del día fecha_str + 00 del día siguiente.
    Si no se consigue la hora 00 del día siguiente, promedia solo 21-23 del mismo día.
    """
    fecha = pd.to_datetime(fecha_str).date()
    fecha_next = (pd.to_datetime(fecha_str) + pd.Timedelta(days=1)).date()

    key = (lat, lon, str(fecha), str(fecha_next))
    if key in weather_cache:
        return weather_cache[key]

    start_date = str(fecha)
    end_date = str(fecha_next)

    url = (
        "https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={lat}&longitude={lon}"
        f"&start_date={start_date}&end_date={end_date}"
        f"&hourly={','.join(HOURLY_VARS)}"
        f"&timezone=America%2FArgentina%2FBuenos_Aires"
    )

    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        hourly = data.get("hourly", {})
        if not hourly or "time" not in hourly:
            weather_cache[key] = None
            return None

        dfh = pd.DataFrame(hourly)
        dfh["time"] = pd.to_datetime(dfh["time"])

        # selección exacta: 21-23 del día + 00 del día siguiente
        mask_21_23 = (dfh["time"].dt.date == fecha) & (dfh["time"].dt.hour.isin([21, 22, 23]))
        mask_00_next = (dfh["time"].dt.date == fecha_next) & (dfh["time"].dt.hour == 0)

        sel = dfh[mask_21_23 | mask_00_next].copy()

        # fallback: si no está la 00 del día siguiente, usar 21-23 del mismo día
        if sel.empty or not mask_00_next.any():
            sel = dfh[mask_21_23].copy()

        if sel.empty:
            weather_cache[key] = None
            return None

        out = {}
        for var in HOURLY_VARS:
            out[var] = float(sel[var].mean()) if var in sel.columns else None

        weather_cache[key] = out
        return out

    except Exception:
        weather_cache[key] = None
        return None

# =========================
# 3) Agregar clima a 'cena'
# - coords: casa de cada cena
# - si realizada == "no": usar casa == "cdc"
# - promedio 21–00
# =========================
cena_clima = cena.copy()

# asegurar fecha YYYY-MM-DD
# (si ya es datetime/date, esto lo deja bien)
cena_clima["fecha_str"] = pd.to_datetime(cena_clima["fecha"]).dt.strftime("%Y-%m-%d")

# si no hubo cena => casa = 'cdc' solo para el clima (sin tocar tu columna real si no querés)
mask_no = cena_clima["realizada"].astype(str).str.strip().str.lower().eq("no")
casa_para_clima = cena_clima["casa"].copy()
casa_para_clima.loc[mask_no] = "cdc"

# crear columnas nuevas en castellano (inicialmente NA)
for var, col_es in SPANISH_COLS.items():
    cena_clima[col_es] = pd.NA

# calcular por fila (con cache)
for idx, row in cena_clima.iterrows():
    casa_name = casa_para_clima.loc[idx]
    coords = get_coords_or_none(casa_name)

    if coords is None:
        continue

    lat, lon = coords
    fecha_str = row["fecha_str"]

    w = fetch_weather_avg_21_to_00_nextday(lat, lon, fecha_str)

    
    if not w:
        continue

    for var, col_es in SPANISH_COLS.items():
        val = w.get(var, None)
        if val is not None:
            # redondeos razonables
            if var in {"temperature_2m", "apparent_temperature"}:
                cena_clima.at[idx, col_es] = round(val, 1)
            elif var == "relative_humidity_2m":
                cena_clima.at[idx, col_es] = round(val, 1)
            elif var == "precipitation":
                cena_clima.at[idx, col_es] = round(val, 2)
            elif var == "windspeed_10m":
                cena_clima.at[idx, col_es] = round(val, 1)

# (opcional) eliminar helper
cena_clima = cena_clima.drop(columns=["fecha_str"])

# si querés que el resultado reemplace tu df 'cena'
cena = cena_clima
