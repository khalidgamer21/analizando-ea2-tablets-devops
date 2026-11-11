# Tablets DevOps · Evidencia de aprendizaje 2

Continuación de la Unidad 1 de Marlon Monterrosa. El proyecto reproduce la extracción
de **80 referencias de tablets de Alkosto** mediante **BeautifulSoup**, valida los datos
y prepara su análisis para la integración y el despliegue continuos.

El artículo central es la **Redmi Pad 2 de 128 GB**, SKU `6932554444525`.
La captura original corresponde al **27 de octubre de 2026**. No son precios de hoy.

## Ejecutar las pruebas

```bash
python -m venv .venv
# Activar el entorno virtual según el sistema operativo.
python -m pip install -r requirements-dev.txt
python -m pip install -e .
python -m ruff check .
python -m pytest --cov=tablets_devops --cov-report=term-missing
```

## Procedencia de los datos

`data/catalogo_tablets.csv` conserva los datos de la Unidad 1. `data/snapshot`
incluye los fragmentos originales y su registro de captura con huellas SHA-256.
Las páginas completas permanecen en el paquete de la Unidad 1; el repositorio
publica únicamente los fragmentos necesarios para repetir el análisis.

La metodología de scraping sigue siendo BeautifulSoup. La automatización usa la
captura guardada para que las pruebas no dependan de la disponibilidad del comercio.

## Trabajo individual

El mismo estudiante representa los roles de desarrollo, revisión y operación.
La actividad no implica la participación de otras personas ni revisiones externas.
