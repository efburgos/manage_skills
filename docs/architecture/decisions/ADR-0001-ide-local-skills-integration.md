# ADR-0001: Integración Local de Skills para Cursor y VSCode

- **Date:** 2026-04-28
- **Status:** Proposed

## Context
El sistema actual sincroniza las *skills* de IA en un directorio global (`~/.agents/skills`) y crea un symlink para que el agente Antigravity (`~/.gemini/antigravity/skills`) pueda utilizarlas automáticamente. Sin embargo, IDEs modernos como **Cursor**, **Roo Code (Cline)** y **GitHub Copilot** no soportan la lectura automática desde un directorio global. Estos editores esperan que las reglas y configuraciones residan directamente en la raíz de cada proyecto (ej. `.cursor/rules/`, `.github/copilot-instructions.md`, `.clinerules`).

Los desarrolladores necesitan una forma sencilla y estandarizada de inyectar o referenciar las skills globales dentro de los repositorios individuales en los que están trabajando.

## Decision
Implementar un nuevo comando en el CLI `manage_skills.py`, llamado tentativamente `inject` o `link-project`.

Cuando un usuario ejecute `uv run bin/manage_skills.py inject` estando ubicado en la raíz de su proyecto, el script realizará lo siguiente:
1. Detectará el entorno local (verificará si es un repositorio válido o si el usuario confirma la acción).
2. **Para Cursor:** Creará el directorio `.cursor/rules/` y generará symlinks a los archivos `.mdc` alojados en `~/.agents/skills`.
3. **Para VSCode / Copilot:** Generará o actualizará `.github/copilot-instructions.md` integrando referencias o inyectando los prompts base.
4. **Para Roo Code:** Creará un symlink para `.clinerules` o `.roomodes` apuntando a las reglas globales.

## Consequences
- **Ventajas:** Los usuarios obtienen una experiencia "plug and play" en sus IDEs favoritos sin tener que recordar cómo o dónde enlazar las reglas manualmente por cada proyecto. Centraliza la fuente de verdad en `~/.agents/skills`.
- **Desventajas:** Añade complejidad al script principal. Los symlinks pueden generar ruido en los commits si no están correctamente excluidos en los `.gitignore` de los proyectos de destino, por lo que el comando `inject` también podría necesitar sugerir o agregar automáticamente estas rutas al `.gitignore` del proyecto local.

## Alternatives Considered
- **Configuración Manual:** Proveer instrucciones en el README sobre cómo crear los symlinks manualmente. Rechazado por tener una mala experiencia de usuario (UX) y ser propenso a errores u olvidos por parte de los desarrolladores.
- **Sincronización Copiada (Hard Copy):** En lugar de symlinks, copiar físicamente los archivos a cada repositorio. Rechazado porque las reglas se desactualizarían cuando se ejecute un `update` global.
