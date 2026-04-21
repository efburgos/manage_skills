#!/bin/bash

# --- Resolución de Directorio ---
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# --- Configuración y Colores ---
SKILLS_FILE="$PROJECT_DIR/conf/skills.list"
INSTALLED_FILE="$PROJECT_DIR/conf/skills.installed"

BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Aseguramos que los archivos existan
mkdir -p "$PROJECT_DIR/conf"
touch "$SKILLS_FILE"
touch "$INSTALLED_FILE"

# --- Interfaz Visual ---
header() {
    echo -e "${CYAN}"
    echo "  ██████╗██╗  ██╗██╗██╗     ██╗     ███████╗"
    echo "  ██╔════╝██║ ██╔╝██║██║     ██║     ██╔════╝"
    echo "  ███████╗█████╔╝ ██║██║     ██║     ███████╗"
    echo "  ╚════██║██╔═██╗ ██║██║     ██║     ╚════██║"
    echo "  ███████║██║  ██╗██║███████╗███████╗███████║"
    echo "  ╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚══════╝"
    echo -e "             SRE Skills Manager v2.3${NC}\n"
}

show_help() {
    header
    echo -e "${YELLOW}MODO DE USO:${NC}"
    echo -e "  $0 ${GREEN}sync${NC}             Instala solo las skills nuevas o faltantes"
    echo -e "  $0 ${GREEN}update${NC}           Fuerza la actualización/reinstalación de TODAS las skills"
    echo -e "  $0 ${GREEN}list${NC}             Lista las skills configuradas en el proyecto"
    echo -e "  $0 ${GREEN}add${NC} <url> <name>   Añade una nueva skill a la lista"
    echo -e "  $0 ${GREEN}remove${NC} <name>      Quita una skill de la lista"
    echo -e "  $0 ${GREEN}clean${NC}            Limpia carpetas ocultas locales (.claude, .cursor, etc.)"
    echo -e "\n${YELLOW}EJEMPLO:${NC}"
    echo -e "  $0 add https://github.com/usuario/repo skill-name"
}

# --- Lógica de Comandos ---

list_skills() {
    header
    echo -e "${BLUE}Skills configuradas para este proyecto:${NC}"
    if [ ! -s "$SKILLS_FILE" ]; then
        echo "  (Lista vacía)"
    else
        column -t "$SKILLS_FILE" | sed 's/^/  /'
    fi
}

add_skill() {
    if [[ -z "$1" || -z "$2" ]]; then
        echo -e "${RED}Error:${NC} Faltan argumentos. Uso: add <url> <nombre>"
        return 1
    fi
    local clean_skills=$(echo "$2" | sed 's/--skill //g')
    echo "$1 $clean_skills" >> "$SKILLS_FILE"

    # Ordena y quita duplicados automáticamente al añadir
    sort -u "$SKILLS_FILE" -o "$SKILLS_FILE"

    echo -e "${GREEN}✓ Añadida:${NC} $clean_skills ($1)"
}

remove_skill() {
    if [ -z "$1" ]; then
        echo -e "${RED}Error:${NC} Indica el nombre de la skill."
        return 1
    fi

    # Lo quitamos de la lista principal
    grep -v "$1" "$SKILLS_FILE" > "${SKILLS_FILE}.tmp" && mv "${SKILLS_FILE}.tmp" "$SKILLS_FILE"

    # También lo quitamos del historial de instalados para que se pueda reinstalar en el futuro
    grep -v "$1" "$INSTALLED_FILE" > "${INSTALLED_FILE}.tmp" && mv "${INSTALLED_FILE}.tmp" "$INSTALLED_FILE"

    echo -e "${YELLOW}- Eliminada:${NC} $1 de la configuración."
}

setup_antigravity_symlink() {
    local source_dir="$HOME/.agents/skills"
    local target_dir="$HOME/.gemini/antigravity/skills"

    if [ ! -d "$source_dir" ]; then
        return
    fi
    
    if [ ! -e "$target_dir" ] && [ ! -L "$target_dir" ]; then
        echo -e "\n${BLUE}Configurando symlink para Antigravity...${NC}"
        mkdir -p "$(dirname "$target_dir")"
        ln -s "$source_dir" "$target_dir"
        echo -e "  ${GREEN}✓ Symlink creado:${NC} $target_dir -> $source_dir"
    fi
}

process_skills() {
    local force_update=$1
    header

    if [ "$force_update" = true ]; then
        echo -e "${BLUE}Iniciando ACTUALIZACIÓN FORZADA de todas las skills...${NC}"
        > "$INSTALLED_FILE"
    else
        echo -e "${BLUE}Iniciando sincronización...${NC}"
    fi

    if [ ! -s "$SKILLS_FILE" ]; then
        echo -e "${YELLOW}No hay skills en la lista para procesar.${NC}"
        return
    fi

    while read -r url skills_batch <&3; do
        url=$(echo "$url" | xargs)
        skills_batch=$(echo "$skills_batch" | xargs | sed 's/--skill //g')

        [[ -z "$url" || -z "$skills_batch" ]] && continue

        if [[ "$force_update" == false ]] && grep -q -x "$skills_batch" "$INSTALLED_FILE"; then
            echo -e "⚡ ${YELLOW}Saltando:${NC} $skills_batch"
            continue
        fi

        echo -e "\n📦 Repo: ${CYAN}$url${NC}"
        echo -e "🚀 Instalando: ${GREEN}$skills_batch${NC}"

        if npx skills add "$url" --skill "$skills_batch" --global --yes; then
            echo -e "  ${GREEN}✓ Instalación exitosa${NC}"
            echo "$skills_batch" >> "$INSTALLED_FILE"
            sort -u "$INSTALLED_FILE" -o "$INSTALLED_FILE"
        else
            echo -e "  ${RED}✗ Falló la instalación${NC}"
        fi
    done 3< "$SKILLS_FILE"

    setup_antigravity_symlink

    echo -e "\n${GREEN}Proceso finalizado.${NC}"
}

cleanup_local() {
    echo -e "${BLUE}Limpiando contaminación local del workspace...${NC}"
    find . -maxdepth 1 -type d -name ".*" ! -name "." ! -name ".." ! -name ".git" ! -name ".skills*" -exec rm -rf {} +
    rm -rf skills skills-lock.json
    echo -e "${GREEN}✓ Workspace impecable.${NC}"
}

# --- Router ---
case "$1" in
    add)    add_skill "$2" "$3" ;;
    remove) remove_skill "$2"   ;;
    list)   list_skills         ;;
    sync)   process_skills false;;
    update) process_skills true ;;
    clean)  cleanup_local       ;;
    *)      show_help           ;;
esac
