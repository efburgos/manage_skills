# SRE Skills Manager

Este repositorio contiene las herramientas y configuraciones para manejar y sincronizar *skills* (habilidades de IA) en el entorno local.

## Dependencias

Se requiere tener Node.js y `npx` instalados. Las *skills* se descargan de manera global en el directorio `~/.agents/skills`.

## Uso

El script interactúa con los archivos locales `.skills.list` (donde se configuran los repositorios) y `.skills.installed` (donde guarda el estado para no reinstalar).

```bash
./manage-skills.sh sync             # Instala solo las skills nuevas o faltantes
./manage-skills.sh update           # Fuerza la actualización/reinstalación de TODAS las skills
./manage-skills.sh list             # Lista las skills configuradas en el proyecto
./manage-skills.sh add <url> <name> # Añade una nueva skill a la lista
./manage-skills.sh remove <name>    # Quita una skill de la lista
./manage-skills.sh clean            # Limpia carpetas ocultas locales
```

## Antigravity (Gemini)

Para que el framework **Antigravity** (herramienta basada en Gemini) reconozca correctamente todas las *skills* descargadas globalmente, es necesario enlazar los directorios. El script `manage-skills.sh` crea automáticamente este `symlink` al terminar las operaciones de sincronización (`sync` o `update`).

La ruta de enlace lógico que crea el script es la siguiente:
```bash
ln -s /Users/ezequiel/.agents/skills ~/.gemini/antigravity/skills
```

De esta manera, todas las herramientas que obtengas con este gestor quedarán documentadas y listas para usar con tu agente Antigravity.
