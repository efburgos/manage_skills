#!/bin/bash
# ai.sh - Central AI Environments and Skills Manager

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
    
    echo -e "Usage: \033[0;32m$0\033[0m <command> [options]"
    echo ""
    echo -e "\033[1;33m► Environment Commands (Bootstrapper):\033[0m"
    echo -e "  \033[0;32minit\033[0m             Start interactive setup (Cursor/Gemini/Claude, etc)"
    echo ""
    echo -e "\033[1;33m► Skills Commands (Package Manager):\033[0m"
    echo -e "  \033[0;32madd <url> <name>\033[0m Add a new skill"
    echo -e "  \033[0;32mremove <name>\033[0m    Remove a skill"
    echo -e "  \033[0;32mlist\033[0m             Show active skills in the configuration"
    echo -e "  \033[0;32msync\033[0m             Download only new or missing skills"
    echo -e "  \033[0;32mupdate [name]\033[0m    Force update of a specific skill or all of them"
    echo -e "  \033[0;32mclean\033[0m            Clean up local cache/state folders"
}

check_dependencies() {
    local missing=0

    if ! command -v npx &> /dev/null; then
        echo -e "\033[0;31mError: npx (Node.js) is not installed.\033[0m"
        
        # Detect the OS to provide easy installation recommendations
        OS="$(uname -s)"
        if [ "$OS" = "Darwin" ]; then
            echo -e "On \033[1;36mmacOS\033[0m, you can easily install it using Homebrew:"
            echo -e "  \033[0;32mbrew install node\033[0m"
        elif [ "$OS" = "Linux" ]; then
            echo -e "On \033[1;36mLinux\033[0m, you can quickly install it using NodeSource or nvm."
            echo -e "For Debian/Ubuntu:"
            echo -e "  \033[0;32mcurl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -\033[0m"
            echo -e "  \033[0;32msudo apt-get install -y nodejs\033[0m"
            echo -e "Or as a universal alternative (nvm):"
            echo -e "  \033[0;32mcurl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash\033[0m"
        else
            echo -e "Please install Node.js from: \033[0;34mhttps://nodejs.org/\033[0m"
        fi
        
        missing=1
    fi

    if ! command -v uv &> /dev/null; then
        echo -e "\033[0;31mError: uv (Python Package Manager) is not installed.\033[0m"
        echo "Installing uv automatically..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        
        # Attempt to reload PATH so uv is immediately available
        if [ -f "$HOME/.cargo/env" ]; then
            source "$HOME/.cargo/env"
        elif [ -f "$HOME/.local/bin/uv" ]; then
            export PATH="$HOME/.local/bin:$PATH"
        fi

        if ! command -v uv &> /dev/null; then
            echo -e "\033[0;31mFailed to install uv automatically. Please install it manually: curl -LsSf https://astral.sh/uv/install.sh | sh\033[0m"
            missing=1
        else
            echo -e "\033[0;32m✓ uv successfully installed.\033[0m"
        fi
    fi

    if [ "$missing" -eq 1 ]; then
        exit 1
    fi
}

if [ "$#" -eq 0 ]; then
    show_help
    exit 0
fi

check_dependencies

CMD=$1
shift

case "$CMD" in
    init)
        exec "$SCRIPT_DIR/bin/init_env.py" "$@"
        ;;
    add|remove|list|sync|update|clean)
        exec "$SCRIPT_DIR/bin/manage_skills.py" "$CMD" "$@"
        ;;
    *)
        show_help
        ;;
esac
