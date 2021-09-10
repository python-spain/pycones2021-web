# PyConES 2021

Sitio estático para la versión 2021 de la PyConES.
Para modificar el archivo principal `index.html` se debe generar
con el script en `gen_programa/gen_index.py`.

La idea principal del script es poder generar el programa de la conferencia
basado en distintos archivos CSV para información como Charlas, Keynotes,
Talleres, etc.

Para modificar un aspecto que no sea el programa, los cambios deben
aplicarse en `gen_programa/base.html` y luego ejecutar directamente
el script desde el directorio `gen_programa/`.

La creación del sitio web solo utiliza `pandas` y `jinja2`,
los cuales pueden instalarse utilizando el `gen_programa/requirements.txt`.
