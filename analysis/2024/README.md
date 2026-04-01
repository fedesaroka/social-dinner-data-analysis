# 📅 Datos y análisis – 2024

Esta carpeta contiene los datos correspondientes al año 2024 y el proceso de transformación utilizado para analizarlos.

---

## 📁 Contenido

### 📄 Datos crudos

* `ASISTENCIA 2024.csv`: archivo original con los datos sin procesar

  * Contiene la información inicial registrada de las cenas
  * Utilizado como fuente principal para el análisis

---

### 🐍 Procesamiento de datos

* `Datos crudos a SQL 2024.ipynb`:

  * Notebook donde se realiza la transformación de los datos
  * Se encarga de:

    * Limpiar y estructurar la información
    * Normalizar los datos
    * Separar la información en distintas tablas

---

### 🧱 Datos procesados

A partir del procesamiento, se generan archivos estructurados para análisis:

* `cena`: información general de cada cena
* `cena_asistencia`: registro de asistencia por persona
* `cena_participante`: relación entre participantes y cenas

Estos datasets permiten trabajar con un modelo más organizado y escalable.

---

### 📊 Visualización

* Archivo `.twbx` (Tableau Workbook):

  * Utilizado para la visualización de los datos
  * Permite explorar:

    * Asistencia
    * Costos
    * Patrones de comportamiento

También se puede acceder a la versión publicada en Tableau Public.[
https://public.tableau.com/app/profile/federico.saroka/viz/CenasMosca2024/Cantidaddecenasporpersona](url)

---

## 🎯 Objetivo

Transformar datos crudos en un modelo estructurado que permita:

* Analizar patrones de asistencia
* Evaluar características de las cenas
* Construir visualizaciones interactivas
* Facilitar el análisis en herramientas como Tableau

---

## 🔗 Relación con el proyecto

Este flujo representa la primera etapa del proyecto (2024), donde:

* Los datos se registraban manualmente
* El procesamiento se realizaba mediante notebooks
* Las visualizaciones se construían en Tableau

Este proceso evolucionó posteriormente hacia una automatización mediante una aplicación web.

---
