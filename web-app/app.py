from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from drive_config import DriveConfiguration
from asistencia import DataAsistencia
from cena import DataCena
from faltas import DataFaltas
from participantes import DataParticipantes
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# ── Flask-Login ──────────────────────────────────────────────────────────────
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# ── Credenciales admin ───────────────────────────────────────────────────────
USUARIO    = os.getenv("ADMIN_USER")
CONTRASENA = os.getenv("ADMIN_PASSWORD")

# ── Caché de usuarios readonly (de Google Sheets) ───────────────────────────
_usuarios_cache      = {}   # {username: {"contrasena": ..., "participante": ...}}
_usuarios_cache_time = None
_CACHE_TTL           = timedelta(minutes=5)

def _cargar_usuarios_sheets():
    global _usuarios_cache, _usuarios_cache_time
    ahora = datetime.now()
    if _usuarios_cache_time and (ahora - _usuarios_cache_time) < _CACHE_TTL:
        return _usuarios_cache
    try:
        config = DriveConfiguration()
        rows = config.sheet_usuarios.get_all_records()
        _usuarios_cache = {
            r["user"].strip(): {
                "contrasena":   str(r["pass"]).strip(),
                "participante": r.get("participante", "").strip(),
            }
            for r in rows if r.get("user", "").strip()
        }
        _usuarios_cache_time = ahora
    except Exception as e:
        print(f"Error cargando usuarios desde Sheets: {e}")
    return _usuarios_cache

# ── Modelo de usuario ────────────────────────────────────────────────────────
class Usuario(UserMixin):
    """tipo: 'admin' | 'readonly' | 'invitado'"""
    def __init__(self, id, tipo="admin", participante=None):
        self.id          = id
        self.tipo        = tipo
        self.participante = participante

    @property
    def es_admin(self):
        return self.tipo == "admin"

    @property
    def puede_guardar(self):
        return self.tipo == "admin"

@login_manager.user_loader
def load_user(user_id):
    if user_id == USUARIO:
        return Usuario(user_id, tipo="admin")
    if user_id == "invitado":
        return Usuario(user_id, tipo="invitado")
    usuarios = _cargar_usuarios_sheets()
    if user_id in usuarios:
        return Usuario(user_id, tipo="readonly",
                       participante=usuarios[user_id]["participante"])
    return None

# ── Datos ────────────────────────────────────────────────────────────────────
ASISTENTES = ["Axel Zielonka", "Federico Saroka", "Federico Cabelli", "Federico Koltan",
              "Manuel Hirsch", "Joaquin Sokolowicz", "Lucas Rotmitrovsky",
              "Gonzalo Borinsky", "Matias Nemirovsky", "Ianick Izon", "Santiago Tabak"]

RAZONES_FALTA = ["Enfermedad", "Trabajo", "Viaje", "Compromiso Familiar", "Estudio", "Cumpleaños", "Traicion","Otro"]

# ── Helpers Sheets ───────────────────────────────────────────────────────────
def leer_categorias(config):
    valores = config.sheet_comidas.col_values(1)
    return sorted(set(v.strip() for v in valores if v.strip()), key=str.lower)

def leer_casas(config):
    registros = config.sheet_casas.get_all_records()
    return sorted((r["casa"].strip() for r in registros if r.get("casa", "").strip()), key=str.lower)

def leer_casas_coords(config):
    registros = config.sheet_casas.get_all_records()
    return {
        r["casa"].strip(): (float(r["latitud"]), float(r["longitud"]))
        for r in registros
        if r.get("casa", "").strip() and r.get("latitud") and r.get("longitud")
    }

def agregar_categoria_si_no_existe(nueva, config):
    nueva = (nueva or "").strip()
    if not nueva:
        return None
    existentes = set(c.lower() for c in leer_categorias(config))
    if nueva.lower() not in existentes:
        config.sheet_comidas.append_row([nueva])
    return nueva

def agregar_casa_si_no_existe(nombre, latitud, longitud, config):
    nombre = (nombre or "").strip()
    if not nombre:
        return None
    existentes = set(c.lower() for c in leer_casas(config))
    if nombre.lower() not in existentes:
        try:
            lat = float(latitud) if latitud else ""
            lon = float(longitud) if longitud else ""
        except (ValueError, TypeError):
            lat, lon = "", ""
        config.sheet_casas.append_row([nombre, lat, lon])
    return nombre

# ── Rutas ────────────────────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        usuario    = request.form.get('usuario', '').strip()
        contrasena = request.form.get('contrasena', '')

        if usuario == USUARIO and contrasena == CONTRASENA:
            user = Usuario(usuario, tipo="admin")
            login_user(user, remember=True, duration=timedelta(hours=1))
            return redirect(url_for('index'))

        usuarios = _cargar_usuarios_sheets()
        if usuario in usuarios and usuarios[usuario]["contrasena"] == contrasena:
            user = Usuario(usuario, tipo="readonly",
                           participante=usuarios[usuario]["participante"])
            login_user(user, remember=True, duration=timedelta(hours=1))
            return redirect(url_for('stats'))

        error = "Usuario o contraseña incorrectos"
    return render_template('login.html', error=error)

@app.route('/login-invitado')
def login_invitado():
    user = Usuario("invitado", tipo="invitado")
    login_user(user, remember=False)
    return redirect(url_for('index'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    if current_user.tipo == "readonly":
        return redirect(url_for('stats'))

    config = DriveConfiguration()
    col_id = config.sheet_data.col_values(1)
    id_cena = int(col_id[-1]) + 1
    fecha = datetime.now().strftime("%Y-%m-%d")
    categorias = leer_categorias(config)
    casas = leer_casas(config)

    # ── Última cena cargada ──────────────────────────────────────────────────
    ultima_cena = None
    try:
        ultima_fila = config.sheet_data.get_all_values()
        if len(ultima_fila) > 1:  # Si hay más que el header
            fila = ultima_fila[-1]
            ultima_cena = {
                "id":    fila[0],
                "fecha": fila[1],
                "comida": fila[4],
                "casa":  fila[9],
                "tema":  fila[10]
            }

    except Exception as e:
        print(f"Error leyendo última cena: {e}")

    return render_template('index.html', asistentes=ASISTENTES, razones=RAZONES_FALTA,
                           comidas=categorias, casas=casas, id_cena=id_cena, fecha=fecha,
                           ultima_cena=ultima_cena, es_invitado=not current_user.puede_guardar)

@app.route('/guardar', methods=['POST'])
@login_required
def guardar():
    if not current_user.puede_guardar:
        return jsonify({"status": "error", "message": "No tenés permiso para guardar datos"}), 403

    try:
        data = request.json
        config = DriveConfiguration()
        id_cena = int(data['id_cena'])
        fecha = datetime.strptime(data['fecha'], "%Y-%m-%d").date()

        hay_asistentes = any(float(v) > 0 for v in data['asistencias'].values())

        asistencias = DataAsistencia(id_cena, fecha)
        for p, valor in data['asistencias'].items():
            asistencias.cargar_asistencia(p, float(valor))

        # ── Solo procesar datos de cena si hubo asistentes ──
        cena = None
        faltas = DataFaltas(id_cena)
        if hay_asistentes:
            data["categoria_comida"] = agregar_categoria_si_no_existe(data.get("categoria_comida"), config)
            if not data["categoria_comida"]:
                return jsonify({"status": "error", "message": "Categoria de comida vacía"}), 400

            cena = DataCena(id_cena, fecha, data['quorum'], data['realizada'],
                            data['comida'], data['categoria_comida'], data['tipo_comida'],
                            float(data['precio']), data['casa'], data['tema'],
                            data['postre'], data['cant_personas'])

            for f in data.get('faltas', []):
                faltas.cargar_falta(f['nombre'], f['razon'], f['descripcion'])
        else:
            for p in ASISTENTES:
                faltas.cargar_falta(p, "no hubo cena", "")


        for nc in data.get('nuevas_casas', []):
            agregar_casa_si_no_existe(nc.get('nombre'), nc.get('latitud'), nc.get('longitud'), config)

        casas_coords = leer_casas_coords(config)
        ors_api_key = os.getenv("ORS_API_KEY")
        participantes = DataParticipantes(id_cena, cena.casa if cena else "", casas_coords, ors_api_key)
        for p in data.get('participantes', []):
            participantes.cargar_data(p['nombre'], p['ida'], p['vuelta'], p['extras'])

        escribir_en_drive_web(id_cena, fecha, asistencias, cena, faltas, participantes, config, hay_asistentes)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/stats')
@login_required
def stats():
    periodo = request.args.get('periodo', 'all')
    datos = _calcular_stats(periodo)
    return render_template('stats.html', datos=datos, periodo=periodo,
                           participante=current_user.participante)


def _calcular_stats(periodo):
    hoy = datetime.now().date()
    _PERIODOS = {
        'month':   timedelta(days=30),
        '3months': timedelta(days=90),
        'year':    timedelta(days=365),
    }
    fecha_inicio = (hoy - _PERIODOS[periodo]) if periodo in _PERIODOS else None

    def dentro(fecha_str):
        if not fecha_inicio:
            return True
        try:
            return datetime.strptime(fecha_str, "%Y-%m-%d").date() >= fecha_inicio
        except Exception:
            return False

    config = DriveConfiguration()

    # ── Data cena: fuente maestra de fechas, casas y precio por id_cena ──────
    cena_rows   = config.sheet_data.get_all_values()
    cena_header = [h.strip().lower() for h in (cena_rows[0] if cena_rows else [])]

    def col(nombre):
        try:
            return cena_header.index(nombre.lower())
        except ValueError:
            return None

    idx_id       = col('id_cena') if col('id_cena') is not None else 0
    idx_fecha    = col('fecha')
    idx_casa     = col('casa')
    idx_precio   = col('precio')
    idx_realizada = col('realizada')

    ids_en_periodo  = set()          # id_cena (str) del período
    precio_por_cena = {}             # {id_cena_str: precio} solo cenas realizadas
    casas_count     = {}
    cenas_realizadas = 0

    for row in cena_rows[1:]:
        fecha_str = row[idx_fecha] if idx_fecha is not None and len(row) > idx_fecha else ""
        if not dentro(fecha_str):
            continue

        id_str = ""
        try:
            id_str = str(int(float(row[idx_id])))
            ids_en_periodo.add(id_str)
        except Exception:
            pass

        realizada = row[idx_realizada].strip().lower() if idx_realizada is not None and len(row) > idx_realizada else ""
        if realizada == 'si' and id_str:
            cenas_realizadas += 1
            if idx_precio is not None and len(row) > idx_precio:
                try:
                    precio_por_cena[id_str] = float(row[idx_precio])
                except (ValueError, TypeError):
                    pass

        if idx_casa is not None and len(row) > idx_casa:
            casa = row[idx_casa].strip()
            if casa:
                casas_count[casa] = casas_count.get(casa, 0) + 1

    casas_ranking = sorted(casas_count.items(), key=lambda x: x[1], reverse=True)

    # ── Ranking de asistencias + plata gastada por persona ───────────────────
    # (Data asistencia, filtrado por ids de Data cena)
    asist_rows   = config.sheet_asistencia.get_all_values()
    header_asist = asist_rows[0] if asist_rows else []
    nombres      = header_asist[2:]   # columnas tras id_cena y fecha

    conteo            = {n: 0.0 for n in nombres}
    gastado_por_persona = {n: 0.0 for n in nombres}

    for row in asist_rows[1:]:
        id_row = row[0].strip() if row else ""
        if fecha_inicio is not None and id_row not in ids_en_periodo:
            continue
        precio_cena = precio_por_cena.get(id_row, 0.0)
        for i, nombre in enumerate(nombres):
            try:
                asist = float(row[i + 2])
                if asist > 0:
                    conteo[nombre] += 1
                    gastado_por_persona[nombre] += precio_cena
            except (ValueError, IndexError):
                pass

    ranking       = sorted(conteo.items(), key=lambda x: x[1], reverse=True)
    total_gastado = sum(precio_por_cena.values())
    promedio_cena = total_gastado / cenas_realizadas if cenas_realizadas else 0
    promedio_gasto_por_persona = {
        p: gastado_por_persona[p] / conteo[p]
        for p in conteo if conteo[p] > 0
    }

    # ── Cena participantes: distancias, ida y vuelta más frecuentes ──────────
    part_rows   = config.sheet_participantes.get_all_values()
    part_header = [h.strip().lower() for h in (part_rows[0] if part_rows else [])]

    # Orden fijo de columnas según escribir_en_drive_web:
    # 0:id_cena 1:persona 2:ida 3:vuelta 4:dist_ida 5:dist_vuelta 6:dist_total 7:extras
    def pcol(nombre, fallback):
        try:
            return part_header.index(nombre.lower())
        except ValueError:
            return fallback

    pidx_id      = pcol('id_cena', 0)
    pidx_persona = pcol('persona',  1)
    pidx_ida     = pcol('ida',      2)
    pidx_vuelta  = pcol('vuelta',   3)
    pidx_dist    = pcol('distancia total', 6)


    distancias    = {}   # {persona: km totales}
    cenas_viajadas = {}  # {persona: cantidad de cenas con viaje}
    conteo_ida    = {}   # {persona: {lugar: count}}
    conteo_vuelta = {}   # {persona: {lugar: count}}

    for row in part_rows[1:]:
        id_row = row[pidx_id].strip() if pidx_id is not None and len(row) > pidx_id else ""
        if fecha_inicio is not None and id_row not in ids_en_periodo:
            continue

        persona = row[pidx_persona].strip() if pidx_persona is not None and len(row) > pidx_persona else ""
        if not persona:
            continue

        if pidx_dist is not None and len(row) > pidx_dist:
            raw = row[pidx_dist].strip()
            if raw:
                try:
                    km = float(raw.replace(',', '.'))
                    if km > 0:
                        distancias[persona] = distancias.get(persona, 0.0) + km
                        cenas_viajadas[persona] = cenas_viajadas.get(persona, 0) + 1
                except (ValueError, TypeError):
                    pass

        if pidx_ida is not None and len(row) > pidx_ida:
            ida = row[pidx_ida].strip()
            if ida:
                conteo_ida.setdefault(persona, {})
                conteo_ida[persona][ida] = conteo_ida[persona].get(ida, 0) + 1

        if pidx_vuelta is not None and len(row) > pidx_vuelta:
            vuelta = row[pidx_vuelta].strip()
            if vuelta:
                conteo_vuelta.setdefault(persona, {})
                conteo_vuelta[persona][vuelta] = conteo_vuelta[persona].get(vuelta, 0) + 1

    dist_ranking     = sorted(distancias.items(), key=lambda x: x[1], reverse=True)
    dist_promedio    = {p: distancias[p] / cenas_viajadas[p] for p in distancias if cenas_viajadas.get(p)}

    # Lugar más frecuente de ida y vuelta por persona
    ida_frecuente    = {p: max(v.items(), key=lambda x: x[1])[0] for p, v in conteo_ida.items()}
    vuelta_frecuente = {p: max(v.items(), key=lambda x: x[1])[0] for p, v in conteo_vuelta.items()}

    return {
        'ranking':             ranking,
        'casas_ranking':       casas_ranking,
        'total_gastado':       total_gastado,
        'cenas_realizadas':    cenas_realizadas,
        'promedio_cena':       promedio_cena,
        'dist_ranking':        dist_ranking,
        'ida_frecuente':       ida_frecuente,
        'vuelta_frecuente':    vuelta_frecuente,
        'dist_promedio':       dist_promedio,
        'total_cenas':         len(ids_en_periodo),
        'gastado_por_persona':          gastado_por_persona,
        'promedio_gasto_por_persona':   promedio_gasto_por_persona,
    }


def escribir_en_drive_web(id_cena, fecha, asistencias, cena, faltas, participantes, config, hay_asistentes=True):
    fila_asistencias = [id_cena, fecha.strftime("%Y-%m-%d")] + list(asistencias.asistencias.values())

    try:
        primera_fila = config.sheet_asistencia.row_values(1)
        if not primera_fila:
            header = ["id_cena", "fecha"] + list(asistencias.asistencias.keys())
            config.sheet_asistencia.update('A1', [header])

        config.sheet_asistencia.append_row(fila_asistencias, value_input_option='USER_ENTERED')

        # Solo escribir datos de cena si hubo asistentes
        if hay_asistentes and cena:
            quorum_str    = "Si" if cena.quorum    else "No"
            realizada_str = "Si" if cena.realizada else "No"
            fila_data = [
                id_cena, fecha.strftime("%Y-%m-%d"), quorum_str, realizada_str,
                cena.comida, cena.categoria_comida, cena.tipo_comida,
                cena.precio, cena.precio_usd, cena.casa, cena.tema, cena.cantidad_personas, cena.postre,
                cena.temperatura_c, cena.sensacion_termica_c, cena.humedad_relativa_pct,
                cena.precipitacion_mm, cena.velocidad_viento_kmh
            ]
        else:
            quorum_str = "no"
            realizada_str = "no"
            fila_data = [
                id_cena, fecha.strftime("%Y-%m-%d"), quorum_str,realizada_str,
                "", "", "", "", "", "", "", 0, "", "", "", "", "", ""]
        config.sheet_data.append_row(fila_data, value_input_option='USER_ENTERED')
        filas_faltas = [
            [id_cena, persona, faltas.faltas[persona]["razon"] or "", faltas.faltas[persona]["descripcion"] or ""]
            for persona in faltas.faltas
        ]
        filas_participantes = [
            [id_cena, persona, p["ida"], p["vuelta"], p["distancia ida"], p["distancia vuelta"], p["distancia total"], p["extras"]]
            for persona, p in participantes.participantes.items()
        ]

        if filas_faltas:
            config.sheet_inasistencias.append_rows(filas_faltas, value_input_option='USER_ENTERED')
        if filas_participantes:
            config.sheet_participantes.append_rows(filas_participantes, value_input_option='USER_ENTERED')

    except Exception as e:
        print(f"Error: {e}")
        raise



if __name__ == '__main__':
    app.run(debug=True)
