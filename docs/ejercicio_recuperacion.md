# Recuperación y resolución de conflictos

## Regresión controlada

La versión inicial se integró mediante la [propuesta 1](https://github.com/khalidgamer21/analizando-ea2-tablets-devops/pull/1)
y se publicó correctamente en la [ejecución 42932183692](https://github.com/khalidgamer21/analizando-ea2-tablets-devops/actions/runs/42932183692).

En la rama `codex/recuperacion-precios`, el commit
`952ec46bc309e2ddd7292b34de456ef4e46d59db` cambió deliberadamente la condición
del precio de `> 0` a `>= 0`. El objetivo fue comprobar que un precio de cero
fuera detectado por las pruebas, sin publicar ese cambio en `main`.

La [ejecución 42932395827](https://github.com/khalidgamer21/analizando-ea2-tablets-devops/actions/runs/42932395827)
falló en las pruebas del precio cero. La publicación no se ejecutó.

Se ejecutó `git revert 952ec46bc309e2ddd7292b34de456ef4e46d59db`.
El commit `ad27cea3f2c74eef5a4253b9fd2cfcd240bcbe33` restauró la condición
de precio positivo. Tanto el error como su corrección permanecen en el historial.
Este ejercicio prueba la recuperación de una regresión en una rama; no representa
una caída ni una reversión de un despliegue de producción.

## Conflicto entre dos roles simulados

El mismo estudiante asumió dos roles en ramas diferentes:

- Análisis: `codex/recuperacion-precios`, commit `9a3adbd`.
- Visualización: `codex/visualizacion-criterios`, commit `5ee496c`.

Ambas ramas cambiaron la misma línea de `docs/criterios.md`. Al ejecutar
`git merge codex/visualizacion-criterios`, Git produjo un conflicto de contenido.
Se leyeron las dos propuestas y se sustituyeron los marcadores de conflicto por:

> Prioridad: validar identidad y precio, y facilitar la comparación por marca y disponibilidad.

Después de `git add docs/criterios.md` y `git commit`, el commit de integración
`77528e1716ddf6363da09005554535ad27e604fa` conservó ambos antecedentes.
`git diff --name-only --diff-filter=U` quedó vacío, lo que confirmó que no había
archivos pendientes de resolución.

## Repetición del ejercicio

```bash
git log --graph --oneline --all
git show 952ec46 -- src/tablets_devops/scraping.py
git show ad27cea -- src/tablets_devops/scraping.py
git show 77528e1 --cc -- docs/criterios.md
python -m pytest --cov=tablets_devops --cov-report=term-missing
```

Para una nueva regresión se debe crear otra rama, corregir o revertir el cambio,
abrir una propuesta y esperar a que pase `Calidad y pruebas` antes de integrar.
La comprobación automática de `main` exige una rama actualizada y el resultado
correcto de ese trabajo. No se exige una aprobación de otra persona porque la
evidencia es individual.
