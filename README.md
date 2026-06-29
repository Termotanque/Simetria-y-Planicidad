# Análisis de Planicidad y Simetría — Física Médica

Este script es una herramienta de Control de Calidad (QA) desarrollada en Python para el análisis automatizado de perfiles de radiación en aceleradores lineales. 
La aplicación procesa archivos .csv para evaluar los parámetros de simetría (tanto puntual como por áreas debajo de la curva) y planicidad del haz de tratamiento,
contrastando los resultados directamente con las tolerancias de la institución y emitiendo reportes en formato PDF.

## Características Principales

* **Análisis Multimétrica de Simetría:**
    * *Simetría por Áreas (Integrada):* Evaluación global del balance del haz mediante integración numérica las mitades del perfil.
    * *Simetría Puntual Máxima:*  punto a punto se localiza el peor desvío local dentro de la zona del 80% para detectar puntos calientes.
* **Cálculo Automático de Parámetros Geométricos:** Algoritmo de detección del ancho de campo real basado en el perfil FWHM al 50% de la dosis central.
* **Definición Dinámica del 80% Central:** Acotamiento automático de la zona de aplanamiento útil (*flattened area*) adaptándose de forma dinámica a cualquier tamaño de campo clínico evaluado (ej. 10x10 cm², 20x20 cm²).
* **Interfaz Gráfica Interactiva (GUI):** Diseñada en Tkinter.
* **Reportes:** PDF institucional con notas y observaciones clínicas.

## Estructura del Proyecto

El código fuente se encuentra modulado de forma limpia para asegurar la mantenibilidad técnica:
* `gui.py`: Script principal que gestiona la interfaz de usuario, eventos de botones, campos de texto monoespaciados para consistencia visual y ventanas de diálogo de archivos.
* `analisis.py`: Hace los calculos utilizando Pandas y NumPy para manipulación matricial, ordenamiento de coordenadas espaciales y cálculo de perfiles.
* `reporte.py`: Módulo encargado de estructurar y renderizar el documento PDF formal mediante la librería FPDF

## Criterios de Tolerancia Clínicos (Especificos de la institución)

| Parámetro Evaluado | Estado OK | Nivel de Acción / Revisar |
| :--- | :---: | :---: |
| **Planicidad (Zona 80%)** | < 2.0 % | ≥ 2.0 % |
| **Simetría Puntual Máxima** | < 2.0 % | ≥ 2.0 % |
| **Simetría por Áreas** | < 2.0 % | ≥ 2.0 % |

## Requisitos del Entorno de Desarrollo

Para ejecutar el código fuente en su entorno nativo, se requiere contar con Python 3.10+ y las siguientes librerías de soporte científico:

```bash
pip install pandas numpy matplotlib fpdf pyinstaller

```

Cualquier cambio que quiera hacer, proceda
