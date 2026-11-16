#!/usr/bin/env bash
# Verificación local del repositorio: no toca el sistema ni necesita root.
#   1. shellcheck sobre todos los scripts (si está instalado)
#   2. los self-checks (self_check_*.sh)
#   3. los enlaces relativos de los .md (scripts/check_links.py)
#
# Uso, desde cualquier directorio:
#   ./scripts/verificar_repo.sh
set -uo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAIZ="$(dirname "$AQUI")"
fallos=0

paso() { printf '\n== %s\n' "$1"; }

paso "shellcheck"
if command -v shellcheck >/dev/null 2>&1; then
  if (cd "$RAIZ" && shellcheck scripts/*.sh); then echo "OK"; else fallos=$((fallos + 1)); fi
else
  echo "shellcheck no está instalado: se omite (sudo apt install shellcheck)"
fi

paso "self-checks"
for sc in "$AQUI"/self_check_*.sh; do
  echo "-- $(basename "$sc")"
  if "$sc" >/dev/null; then echo "OK"; else echo "FALLA"; fallos=$((fallos + 1)); fi
done

paso "enlaces de la documentación"
(cd "$RAIZ" && python3 scripts/check_links.py) || fallos=$((fallos + 1))

echo
if [[ $fallos -eq 0 ]]; then
  echo "OK: verificación completa"
else
  echo "FALLÓ: $fallos paso(s) con problemas"
  exit 1
fi
