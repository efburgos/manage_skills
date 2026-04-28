#!/bin/bash
# ai.sh - Gestor Único para Entornos y Skills de IA

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

show_help() {
    echo -e "\033[0;36m"
    echo "  ██████╗██╗  ██╗██╗██╗     ██╗     ███████╗"
    echo "  ██╔════╝██║ ██╔╝██║██║     ██║     ██╔════╝"
    echo "  ███████╗█████╔╝ ██║██║     ██║     ███████╗"
    echo "  ╚════██║██╔═██╗ ██║██║     ██║     ╚════██║"
    echo "  ███████║██║  ██╗██║███████╗███████╗███████║"
    echo "  ╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚══════╝"
    echo -e "\033[0m"
    echo -e "             \033[1;36mAI Manager v3.0\033[0m\n"
    
    echo -e "Uso: \033[0;32m$0\033[0m <comando> [opciones]"
    echo ""
    echo -e "\033[1;33m► Comandos del Entorno (Bootstrapper):\033[0m"
    echo -e "  \033[0;32minit\033[0m             Inicia configuración interactiva (Cursor/Gemini/Claude, etc)"
    echo ""
    echo -e "\033[1;33m► Comandos de Skills (Gestor de Paquetes):\033[0m"
    echo -e "  \033[0;32madd <url> <name>\033[0m Añade una nueva skill"
    echo -e "  \033[0;32mremove <name>\033[0m    Quita una skill"
    echo -e "  \033[0;32mlist\033[0m             Muestra las skills activas en la configuración"
    echo -e "  \033[0;32msync\033[0m             Descarga solo las skills nuevas o faltantes"
    echo -e "  \033[0;32mupdate\033[0m           Fuerza la reinstalación global de todas las skills"
    echo -e "  \033[0;32mclean\033[0m            Limpia archivos de estado basura de herramientas locales"
}

if [ "$#" -eq 0 ]; then
    show_help
    exit 0
fi

CMD=$1
shift

case "$CMD" in
    init)
        exec "$SCRIPT_DIR/bin/init-env.sh" "$@"
        ;;
    add|remove|list|sync|update|clean)
        exec "$SCRIPT_DIR/bin/manage_skills.py" "$CMD" "$@"
        ;;
    *)
        show_help
        ;;
esac
