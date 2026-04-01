# 📅 Datos y análisis – 2025

Esta carpeta contiene los datos correspondientes al año 2025, junto con un pipeline más avanzado de procesamiento y enriquecimiento de información respecto a 2024.

---

## 📁 Contenido

### 📄 Datos crudos

* Archivos Excel con información base de las cenas
* Incluyen:

  * Asistencia
  * Datos generales de cada cena
  * Información de participantes

---

### 🧱 Datos estructurados

A partir del procesamiento, se generan datasets normalizados:

* `cena`: información general de cada cena
* `cena_participantes`: relación entre participantes y cenas
* `inasistencia`: motivos de ausencia

Estos archivos permiten trabajar con un modelo más organizado y escalable para análisis.

---

### 🌍 Enriquecimiento de datos

En 2025 se incorporan nuevas fuentes de información externas:

#### 📍 Distancias (Google Maps API)

* Se utiliza un archivo adicional:

  * `Data asistencia Mosca.xlsx`

    * Contiene información de origen (`ida`) y destino (`vuelta`) de cada participante

* A partir de esto se calculan:

  * Distancia ida
  * Distancia vuelta
  * Distancia total por participante

El cálculo se realiza mediante la API de Google Maps, optimizando llamadas mediante cacheo de rutas repetidas .

---

#### 🌦️ Clima (Open-Meteo API)

* Se incorporan variables climáticas para cada cena:

  * Temperatura
  * Sensación térmica
  * Humedad
  * Precipitación
  * Velocidad del viento

* Los datos se obtienen mediante la API de Open-Meteo

* Se calcula un promedio entre las 21:00 y 00:00 para representar mejor el contexto de la cena .

---

#### 💵 Tipo de cambio (USD)

* Se incorpora información del dólar para convertir precios:

  * Precio en moneda local
  * Precio en USD

* Permite analizar el costo de las cenas en términos comparables a lo largo del tiempo

---

### 📊 Visualización

* Archivo `.pbix` (Power BI):

  * Utilizado para análisis y visualización interactiva
  * Permite explorar:

    * Asistencia
    * Costos
    * Distancias
    * Impacto del clima

---

## 🐍 Procesamiento de datos

* Notebooks y scripts en Python encargados de:

  * Limpieza de datos
  * Normalización
  * Integración de múltiples fuentes
  * Enriquecimiento con APIs externas

---

## 🎯 Objetivo

Evolucionar el modelo de datos incorporando nuevas variables que permitan:

* Analizar el comportamiento del grupo con mayor profundidad
* Evaluar el impacto de factores externos (clima, distancia, costos)
* Construir visualizaciones más completas y precisas

---

## 🔗 Relación con el proyecto

Esta etapa representa una evolución significativa respecto a 2024:

* Se pasa de un análisis descriptivo a un enfoque más analítico y enriquecido
* Se incorporan APIs externas para ampliar el dataset
* Se mejora la calidad y profundidad de los insights

Estos avances preparan el camino para la automatización completa mediante la aplicación web desarrollada en 2026.

---
