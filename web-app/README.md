# 🍽️ La Mosca - Aplicación Web

Aplicación web desarrollada en **Flask** para gestionar y registrar cenas semanales de un grupo de amigos, incluyendo asistencia, comidas, costos, faltas, transporte y otros detalles relevantes.

La aplicación está desplegada en **PythonAnywhere** y utiliza **Google Sheets** como base de datos. Los datos se consumen luego desde **Power BI** para análisis y visualización.

---

## 🚀 Funcionalidades

- **Asistencia:** registro por participante (asistió ✅, media ½, no asistió ❌)
- **Cálculo automático de quórum** (mínimo 6 personas)
- **Datos de la cena:** comida, categoría, tipo (cocinada/comprada), precio, casa, tema, postre y cantidad de personas
- **Faltas:** se generan automáticamente para los ausentes con razón y descripción
- **Participantes:** registro de ida/vuelta desde cada casa con cálculo de distancias reales vía Google Maps API (ejecución manual anual, desde 2025)
- **Categorías dinámicas:** se pueden agregar nuevas categorías de comida desde la app
- **Autenticación:** login con usuario admin e ingreso como invitado (solo lectura)
- **PWA:** instalable como app en celular (Progressive Web App)
- **Formulario guiado:** wizard de 6 pasos con barra de progreso y resumen final
- **Almacenamiento automático** en Google Sheets (4 hojas: asistencia, cena, faltas, participantes)

---

## 🧱 Tecnologías utilizadas

- **Backend:** Python + Flask
- **Frontend:** HTML + JavaScript + Tailwind CSS
- **Autenticación:** Flask-Login
- **Base de datos:** Google Sheets (vía gspread + service account)
- **Distancias:** Google Maps API
- **Deploy:** PythonAnywhere

---

## ⚙️ Funcionamiento

1. El usuario inicia sesión (admin o invitado)
2. Ingresa el ID y fecha de la cena
3. Registra la asistencia de cada participante
4. Si hubo asistentes, carga los datos de la cena (comida, precio, casa, etc.)
5. Completa las faltas de los ausentes (razón y descripción)
6. Registra los participantes con ida/vuelta desde cada casa
7. Revisa el resumen y guarda — los datos se envían a Google Sheets

Si no hubo asistentes, se saltean los pasos de cena, faltas y participantes automáticamente.

---

## 📂 Estructura del proyecto

```
├── app.py                  # Aplicación principal Flask
├── cena.py                 # Modelo de datos de la cena
├── asistencia.py           # Modelo de asistencias
├── faltas.py               # Modelo de faltas/inasistencias
├── participantes.py        # Modelo de participantes y distancias
├── drive_config.py         # Configuración de Google Sheets
├── service_account.json    # Credenciales de Google (NO incluido en el repo)
├── casas.csv               # Casas disponibles con coordenadas (lat/long)
├── comidas.csv             # Categorías de comida
├── requirements.txt        # Dependencias del proyecto
├── static/
│   ├── manifest.json       # Configuración PWA
│   ├── service-worker.js   # Service worker para PWA
│   ├── icon-192.png        # Ícono PWA
│   └── icon-512.png        # Ícono PWA
└── templates/
    ├── index.html          # Interfaz principal (wizard de 6 pasos)
    └── login.html          # Pantalla de login
```

---

## ▶️ Ejecución local

1. Clonar el repositorio:

```bash
git clone https://github.com/tuusuario/lamosca.git
cd lamosca
```

2. Crear y activar entorno virtual:

```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

4. Agregar el archivo `service_account.json` con las credenciales de Google en la raíz del proyecto.

5. Ejecutar la aplicación:

```bash
python app.py
```

---

## 🔐 Configuración requerida

- `service_account.json`: archivo de credenciales de service account de Google con acceso al spreadsheet "Asistencia Mosca Nuevo"

> ⚠️ Este archivo contiene credenciales sensibles y está excluido del repositorio vía `.gitignore`.

---

## 👥 Autores

- Federico Saroka — [github.com/fedesaroka](https://github.com/fedesaroka)
- Axel Zielonka — [github.com/axel-zielonka](https://github.com/axel-zielonka)

---

## 📌 Mejoras futuras

- Migración a base de datos relacional
- Dashboard de estadísticas dentro de la app
- Integración de datos climáticos automáticos por fecha
- Conversión automática de precio a USD
