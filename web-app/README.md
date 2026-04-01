# 🍽️ La Mosca - Aplicación Web

Aplicación web desarrollada en **Flask** para gestionar y registrar cenas semanales de un grupo, incluyendo asistencia, comidas, costos y otros detalles relevantes.

La aplicación está desplegada en **PythonAnywhere** y utiliza **Google Sheets** como base de datos.

---

## 🚀 Funcionalidades

* Registro de asistencia por participante (asistió, no asistió, se fue antes)
* Cálculo automático de quorum
* Carga de información de la cena:

  * Casa
  * Comida
  * Precio
  * Tema de la noche
  * Postre
* Interfaz simple basada en formularios
* Almacenamiento automático en Google Sheets
* Datos estructurados para análisis posterior

---

## 🧱 Tecnologías utilizadas

* **Backend:** Python + Flask
* **Frontend:** HTML + JavaScript
* **Base de datos:** Google Sheets (vía gspread)
* **Deploy:** PythonAnywhere

---

## ⚙️ Funcionamiento

1. Se registra la asistencia de cada participante
2. El sistema calcula automáticamente si hay quorum
3. Se cargan los datos de la cena mediante un formulario
4. La información se procesa en el backend
5. Los datos se guardan en Google Sheets

---

## 📂 Estructura del proyecto

├── app.py                  # Aplicación principal Flask

├── templates/

│   └── index.html         # Interfaz de usuario

├── comidas.csv            # Opciones de comida

├── requirements.txt       # Dependencias del proyecto

└── wsgi.py                # Configuración de deploy en PythonAnywhere

---

## ▶️ Ejecución local

1. Clonar el repositorio:

```bash
git clone https://github.com/tuusuario/lamosca.git
cd lamosca
```

2. (Opcional) Crear entorno virtual:

```bash
python -m venv venv
```

3. Activar entorno virtual:

* En Mac/Linux:

```bash
source venv/bin/activate
```

* En Windows:

```bash
venv\Scripts\activate
```

4. Instalar dependencias:

```bash
pip install -r requirements.txt
```

5. Configurar variables de entorno:

```bash
export GOOGLE_CREDENTIALS=tu_archivo.json
```

6. Ejecutar la aplicación:

```bash
python app.py
```

---

## 🔐 Variables de entorno

* `GOOGLE_CREDENTIALS`: ruta al archivo JSON de credenciales de Google

---

## 👥 Autores

* Federico Saroka [https://github.com/fedesaroka](url)
* Axel Zielonka [https://github.com/axel-zielonka](url)

---

## 📌 Mejoras futuras

* Autenticación de usuarios
* Mejora de interfaz (UI/UX)
* Migración a base de datos relacional
* Dashboard dentro de la aplicación

---
