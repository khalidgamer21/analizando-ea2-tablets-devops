# Tablets DevOps · Evidencia de aprendizaje 2

[![CI y despliegue](https://github.com/khalidgamer21/analizando-ea2-tablets-devops/actions/workflows/cicd.yml/badge.svg)](https://github.com/khalidgamer21/analizando-ea2-tablets-devops/actions/workflows/cicd.yml)

[Repositorio](https://github.com/khalidgamer21/analizando-ea2-tablets-devops) ·
[Publicación en GitHub Pages](https://khalidgamer21.github.io/analizando-ea2-tablets-devops/)

Continuación de la Unidad 1 de Marlon Monterrosa. El proyecto reproduce la extracción
de **80 referencias de tablets de Alkosto** mediante **BeautifulSoup**, valida los datos
y prepara su análisis para la integración y el despliegue continuos.

El artículo central es la **Redmi Pad 2 de 128 GB**, SKU `6932554444525`.
La captura original corresponde al **27 de octubre de 2026**. No son precios de hoy.

## Flujo DevOps

1. Crear una rama `codex/...` desde `main` y guardar cambios con commits descriptivos.
2. Hacer push y abrir una propuesta de cambio o pull request.
3. GitHub Actions instala las dependencias, revisa el estilo y ejecuta las pruebas.
4. Se exige al menos **85 % de cobertura**; las pruebas también comprueban las 80 fichas.
5. Se construye la publicación y se comprueban el HTML, el CSV y el estado por HTTP.
6. Al integrar un cambio válido en `main`, otro trabajo lo despliega en GitHub Pages.
7. Se verifica que `health.json` publique los 80 registros y el SHA del cambio desplegado.

El trabajo `deploy` depende de `quality`. Un fallo impide generar y publicar una nueva
versión. Las ramas y propuestas ejecutan CI; solo `main` realiza el despliegue.
Las acciones se fijan a un SHA completo y los permisos de publicación se conceden
únicamente al trabajo de despliegue. No hacen falta claves personales en el repositorio.

La configuración está en [cicd.yml](.github/workflows/cicd.yml).
El detalle de roles, evidencia y recuperación está en [docs/flujo_devops.md](docs/flujo_devops.md).
El ejercicio realizado, con la regresión detectada, su reversión y el conflicto
resuelto, está en [docs/ejercicio_recuperacion.md](docs/ejercicio_recuperacion.md).

## Ejecutar las pruebas

```bash
python -m venv .venv
# Activar el entorno virtual según el sistema operativo.
python -m pip install -r requirements-dev.txt
python -m pip install -e .
python -m ruff check .
python -m pytest --cov=tablets_devops --cov-report=term-missing
```

## Construir y consultar los resultados

```bash
python -m tablets_devops replay --output build/catalogo_tablets.csv
python -m tablets_devops build --output build/site
python scripts/smoke.py --directory build/site --expected-records 80
python -m http.server 8000 --directory build/site
```

Abrir `http://localhost:8000`. La página permite buscar referencias, filtrar por marca
y disponibilidad, ordenar por precio y descargar el CSV completo.

## Organización

```text
.github/workflows/cicd.yml  Pruebas, construcción, despliegue y comprobación HTTP
src/tablets_devops/         Extracción, validación, análisis, publicación y comandos
tests/                     Pruebas unitarias y de integración
scripts/smoke.py            Comprobación HTTP local o del despliegue
data/snapshot/              80 fragmentos HTML y registro de captura de EA1
data/catalogo_tablets.csv   Datos de referencia de la Unidad 1
docs/                      Flujo, criterios y registro de los ejercicios
```

## Qué se comprueba

Los controles verifican identidad, precios positivos y moneda COP, unicidad del SKU,
campos obligatorios, fechas con zona horaria y URL de origen. Las huellas SHA-256
detectan cambios en la evidencia. Una prueba de regresión compara la extracción
con el CSV de la Unidad 1. Los nombres de productos se escapan al generar HTML.

GitHub guarda resultados JUnit, cobertura y una vista previa como artefactos de cada
ejecución. `health.json` publica la revisión y la fecha de construcción; los datos
conservan su fecha de captura original. El control HTTP se realiza en cada despliegue.

## Recuperación

Ante una regresión, corregir en la rama o ejecutar `git revert <SHA>` y volver a
ejecutar las pruebas. La reversión agrega un commit sin borrar el historial.
Una recuperación de una versión publicada se tramita mediante otra propuesta hacia
`main`; al aprobarse las comprobaciones, el pipeline vuelve a desplegar.

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
