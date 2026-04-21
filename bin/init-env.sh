#!/bin/bash

# --- Resolución de Directorio ---
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# --- Configuración y Archivos Base ---
SKILLS_FILE="$PROJECT_DIR/conf/skills.list"
ENV_DIR="$PROJECT_DIR/environments"
GLOBAL_SKILLS_DIR="$HOME/.agents/skills"

BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

header() {
    echo -e "${CYAN}"
    echo "  ╔════════════════════════════════════════╗"
    echo "  ║                                        ║"
    echo "  ║        AI Environment Bootstrapper     ║"
    echo "  ║                                        ║"
    echo "  ╚════════════════════════════════════════╝"
    echo -e "${NC}"
}

install_core_skills() {
    echo -e "\n${BLUE}1. Instalando habilidades base para el entorno IA...${NC}"
    
    if [ ! -f "$SKILLS_FILE" ]; then
        echo -e "${RED}Error:${NC} No se encontró el archivo $SKILLS_FILE"
        return 1
    fi

    echo -e "${YELLOW}Ejecutando manage-skills sync...${NC}"
    "$PROJECT_DIR/bin/manage-skills.sh" sync
}

setup_antigravity_env() {
    echo -e "\n${CYAN}[Antigravity]${NC} Configurando entorno..."
    local TARGET_GEMINI_DIR="$HOME/.gemini"
    local TARGET_ANTIGRAVITY_SKILLS="$TARGET_GEMINI_DIR/antigravity/skills"

    # Link Skills
    if [ -d "$GLOBAL_SKILLS_DIR" ]; then
        mkdir -p "$(dirname "$TARGET_ANTIGRAVITY_SKILLS")"
        if [ ! -e "$TARGET_ANTIGRAVITY_SKILLS" ] && [ ! -L "$TARGET_ANTIGRAVITY_SKILLS" ]; then
            ln -s "$GLOBAL_SKILLS_DIR" "$TARGET_ANTIGRAVITY_SKILLS"
            echo -e "  ${GREEN}✓ Symlink creado:${NC} $TARGET_ANTIGRAVITY_SKILLS"
        fi
    fi

    # Instalar Rules (.gemini/GEMINI.md)
    if [ -f "$ENV_DIR/antigravity/GEMINI.md" ]; then
        mkdir -p "$TARGET_GEMINI_DIR"
        cp "$ENV_DIR/antigravity/GEMINI.md" "$TARGET_GEMINI_DIR/GEMINI.md"
        echo -e "  ${GREEN}✓ Reglas inyectadas:${NC} $TARGET_GEMINI_DIR/GEMINI.md"
    fi
}

setup_cursor_env() {
    echo -e "\n${CYAN}[Cursor]${NC} Configurando entorno local..."
    if [ -f "$ENV_DIR/cursor/cursorrules.template" ]; then
        if [ ! -f ".cursorrules" ]; then
            cp "$ENV_DIR/cursor/cursorrules.template" ".cursorrules"
            echo -e "  ${GREEN}✓ Creado:${NC} .cursorrules en el proyecto actual (${PWD})"
        else
            echo -e "  ${YELLOW}✓ .cursorrules ya existe en el proyecto. Se omitió.${NC}"
        fi
    fi
}

setup_claude_env() {
    echo -e "\n${CYAN}[Claude]${NC} Configurando entorno local..."
    if [ -f "$ENV_DIR/claude/CLAUDE.md" ]; then
        if [ ! -f "CLAUDE.md" ]; then
            cp "$ENV_DIR/claude/CLAUDE.md" "CLAUDE.md"
            echo -e "  ${GREEN}✓ Creado:${NC} CLAUDE.md en el proyecto actual (${PWD})"
        else
            echo -e "  ${YELLOW}✓ CLAUDE.md ya existe en el proyecto. Se omitió.${NC}"
        fi
    fi
}

main() {
    header
    
    if ! command -v npx &> /dev/null; then
        echo -e "${RED}Error: NODE/NPX no detectado. Por favor, instálalo antes de continuar.${NC}"
        exit 1
    fi
    
    install_core_skills

    echo -e "\n${BLUE}¿Para qué entorno deseas configurar los archivos de sistema?${NC}"
    echo "1) Antigravity (Gemini)"
    echo "2) Cursor"
    echo "3) Claude (Code/Roo)"
    echo "4) Todos"
    echo "5) Salir"
    
    read -p "Elige una opción (1-5): " option

    case $option in
        1) setup_antigravity_env ;;
        2) setup_cursor_env ;;
        3) setup_claude_env ;;
        4) 
           setup_antigravity_env
           setup_cursor_env
           setup_claude_env
           ;;
        5) echo "Saliendo..."; exit 0 ;;
        *) echo -e "${RED}Opción inválida.${NC}"; exit 1 ;;
    esac

    echo -e "\n${GREEN}🚀 Entorno configurado correctamente.${NC}"
}

main "$@"
