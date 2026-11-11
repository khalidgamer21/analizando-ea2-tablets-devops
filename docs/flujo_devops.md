# Flujo DevOps de la Unidad 2

## Continuidad con la Unidad 1

La fuente es Alkosto y el artículo central es la Redmi Pad 2 de 128 GB. Se conservan
las 80 referencias y los 15 campos de la captura del 27 de octubre de 2026.
BeautifulSoup sigue siendo la única herramienta de scraping. La nueva unidad
incorpora versiones del código, pruebas automáticas y publicación de resultados.

La integración continua reproduce la captura guardada. Así se comprueba el software
sin generar 80 solicitudes al comercio en cada cambio. El registro conserva las URL,
las fechas y las huellas de los HTML completos y de los fragmentos incluidos.

## Responsabilidades de un equipo simulado

| Rol | Responsabilidad |
| --- | --- |
| Desarrollo | Adaptar el extractor y el análisis en una rama. |
| Revisión | Comprobar cambios, pruebas y calidad de los datos antes de integrar. |
| Operación | Mantener el workflow y comprobar la publicación. |

La entrega es individual. Marlon Monterrosa representa los tres roles; no se atribuyen
aprobaciones a otras personas. Las revisiones automáticas son visibles en cada propuesta.

## Integración y despliegue

El evento push ejecuta CI en todas las ramas. Las propuestas dirigidas a main también
disparan las comprobaciones. El trabajo quality ejecuta Ruff, pytest con cobertura,
la construcción del sitio y una prueba HTTP local. Guarda resultados como artefactos.

El trabajo deploy necesita que quality termine correctamente y solo se ejecuta en main.
Recupera el artefacto probado, configura Pages, lo publica y consulta health.json.
La comprobación exige HTTP correcto, 80 registros y el SHA del commit desplegado.
También verifica que el CSV y los recursos de la página se puedan descargar.

## Configuración y seguridad

Las dependencias, reglas de estilo y umbral de cobertura están versionados. Las acciones
oficiales se fijan a SHA completos. Los trabajos de pruebas reciben permiso de lectura;
el trabajo de publicación añade pages:write e id-token:write. La autenticación utiliza
GITHUB_TOKEN y los mecanismos de Pages; no se almacena un token personal en archivos.

La publicación escapa el contenido procedente de las fichas. La validación rechaza
fragmentos alterados, rutas que salgan de la carpeta de datos y URL ajenas a Alkosto.

## Registro de ejercicios

Los ejercicios de recuperación y resolución de conflictos se documentan con sus hashes,
salidas reales y enlaces de ejecución en los archivos de esta carpeta. No se reescribe
el historial para ocultar errores y los cambios de prueba se mantienen fuera de main
hasta que el resultado final supera CI.

## Conexión con las siguientes unidades

La Unidad 3 puede ampliar el pipeline y agregar nuevas capturas fechadas. La actividad
de cierre puede comparar versiones del software y de los datos, conservando su
procedencia. Un nuevo despliegue del código no actualiza los precios por sí mismo.
