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
app.secret_key = "clave_secreta_mosca_2024"  # Cambiá esto por algo seguro

# ── Flask-Login ──────────────────────────────────────────────────────────────
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Redirige a /login si no está autenticado

# ── Usuario ──────────────────────────────────────────────────────────────────
USUARIO = "admin"        # Cambiá esto
CONTRASENA = "mosca123"  # Cambiá esto

class Usuario(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    if user_id == USUARIO or user_id == "invitado":
        return Usuario(user_id)
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

# ── Rutas ────────────────────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        usuario    = request.form.get('usuario')
        contrasena = request.form.get('contrasena')
        if usuario == USUARIO and contrasena == CONTRASENA:
            user = Usuario(usuario)
            # Sesión expira en 1 hora
            login_user(user, remember=True, duration=timedelta(hours=1))
            return redirect(url_for('index'))
        else:
            error = "Usuario o contraseña incorrectos"
    return render_template('login.html', error=error)

@app.route('/login-invitado')
def login_invitado():
    user = Usuario("invitado")
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
                           ultima_cena=ultima_cena, es_invitado=current_user.id == "invitado")

@app.route('/guardar', methods=['POST'])
@login_required
def guardar():
    if current_user.id == "invitado":
        return jsonify({"status": "error", "message": "Modo invitado: los datos no se guardan"}), 403

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


        casas_coords = leer_casas_coords(config)
        ors_api_key = os.getenv("ORS_API_KEY")
        participantes = DataParticipantes(id_cena, cena.casa if cena else "", casas_coords, ors_api_key)
        for p in data.get('participantes', []):
            participantes.cargar_data(p['nombre'], p['ida'], p['vuelta'], p['extras'])

        escribir_en_drive_web(id_cena, fecha, asistencias, cena, faltas, participantes, config, hay_asistentes)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


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
