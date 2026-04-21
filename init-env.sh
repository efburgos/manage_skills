#!/bin/bash
# Script de conveniencia que reenvía los argumentos al directorio ./bin/
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/bin/init-env.sh" "$@"
