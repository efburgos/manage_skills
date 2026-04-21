#!/bin/bash

# --- Configuración y Colores ---
SKILLS_FILE=".skills.list"
SKILLS_DIR=".agent/skills"
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

touch "$SKILLS_FILE"

# --- Interfaz Visual ---
header() {
    echo -e "${CYAN}"
    echo "  ██████╗██╗  ██╗██╗██╗     ██╗     ███████╗"
    echo "  ██╔════╝██║ ██╔╝██║██║     ██║     ██╔════╝"
    echo "  ███████╗█████╔╝ ██║██║     ██║     ███████╗"
    echo "  ╚════██║██╔═██╗ ██║██║     ██║     ╚════██║"
    echo "  ███████║██║  ██╗██║███████╗███████╗███████║"
    echo "  ╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚══════╝"
    echo -e "             SRE Skills Manager v2.0${NC}\n"
}

show_help() {
    header
    echo -e "${YELLOW}MODO DE USO:${NC}"
    echo -e "  $0 ${GREEN}sync${NC}             Instala TODO globalmente (~/.agents/skills)"
    echo -e "  $0 ${GREEN}list${NC}             Lista las skills configuradas en el proyecto"
    echo -e "  $0 ${GREEN}add${NC} <url> <name>   Añade una nueva skill a la lista"
    echo -e "  $0 ${GREEN}remove${NC} <name>      Quita una skill de la lista"
    echo -e "  $0 ${GREEN}clean${NC}            Limpia carpetas ocultas locales (.claude, .cursor, etc.)"
    echo -e "\n${YELLOW}EJEMPLO:${NC}"
    echo -e "  $0 add https://github.com/usuario/repo \"skill1 skill2\""
}

# --- Lógica de Comandos ---

list_skills() {
    header
    echo -e "${BLUE}Skills configuradas para este proyecto:${NC}"
    if [ ! -s "$SKILLS_FILE" ]; then
        echo "  (Lista vacía)"
    else
        # Quitamos el separador "|" para que formatee bien por espacios
        column -t "$SKILLS_FILE" | sed 's/^/  /'
    fi
}

add_skill() {
    if [[ -z "$1" || -z "$2" ]]; then
        echo -e "${RED}Error:${NC} Faltan argumentos. Uso: add <url> \"nombres\""
        return 1
    fi
    # Limpiamos si el usuario ingresó el flag --skill por error en el input
    local clean_skills=$(echo "$2" | sed 's/--skill //g')

    # Guardamos separado por espacios, no por pipes
    echo "$1 $clean_skills" >> "$SKILLS_FILE"
    echo -e "${GREEN}✓ Añadida:${NC} $clean_skills ($1)"
}

remove_skill() {
    if [ -z "$1" ]; then
        echo -e "${RED}Error:${NC} Indica el nombre de la skill."
        return 1
    fi
    # Búsqueda directa del string en lugar de requerir delimitadores exactos al final
    grep -v "$1" "$SKILLS_FILE" > "${SKILLS_FILE}.tmp" && mv "${SKILLS_FILE}.tmp" "$SKILLS_FILE"
    echo -e "${YELLOW}- Eliminada:${NC} $1 de la lista."
}

sync_skills() {
    header
    echo -e "${BLUE}Iniciando sincronización unificada GLOBAL...${NC}"

    if [ ! -s "$SKILLS_FILE" ]; then
        echo -e "${YELLOW}No hay skills que sincronizar.${NC}"
        return
    fi

    # Quitamos IFS="|" para que bash lea naturalmente: el primer token es URL, el resto es skills_batch
    while read -r url skills_batch <&3; do
        url=$(echo "$url" | xargs)
        skills_batch=$(echo "$skills_batch" | xargs)

        [[ -z "$url" || -z "$skills_batch" ]] && continue

        # Sanitizamos la cadena por si el archivo actual ya tiene "--skill" escrito
        skills_batch=$(echo "$skills_batch" | sed 's/--skill //g')

        echo -e "\n📦 Repo: ${CYAN}$url${NC}"
        echo -e "🚀 Skills: ${GREEN}$skills_batch${NC}"

        # Ejecución Global y Silenciosa
        if npx skills add "$url" --skill "$skills_batch" --global --yes; then
            echo -e "  ${GREEN}✓ Instalación Global Completa${NC}"
        else
            echo -e "  ${RED}✗ Falló la instalación${NC}"
        fi
    done 3< "$SKILLS_FILE"

    echo -e "\n${GREEN}Sincronización finalizada.${NC}"
}

cleanup_local() {
    echo -e "${BLUE}Limpiando contaminación local del workspace...${NC}"
    # Borra carpetas de agentes (evitando .git, .skills.list y el script)
    find . -maxdepth 1 -type d -name ".*" ! -name "." ! -name ".." ! -name ".git" ! -name ".skills.list" -exec rm -rf {} +
    rm -rf skills skills-lock.json
    echo -e "${GREEN}✓ Workspace impecable.${NC}"
}

# --- Router ---
case "$1" in
    add)    add_skill "$2" "$3" ;;
    remove) remove_skill "$2"   ;;
    list)   list_skills         ;;
    sync)   sync_skills         ;;
    clean)  cleanup_local       ;;
    *)      show_help           ;;
esac
