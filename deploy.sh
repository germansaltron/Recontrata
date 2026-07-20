#!/usr/bin/env bash
# Deploy de Recontrata a Railway usando un PROJECT TOKEN.
#
# Por qué: el CLI de Railway guarda una sola sesión global, que en este equipo
# está en la cuenta de Faymex (bodegaquilp01). Recontrata vive en la cuenta
# gsaltron@gmail.com, así que `railway up` con el login normal apunta al workspace
# equivocado. Un project token despliega directo al proyecto correcto sin depender
# del login y sin tocar la sesión de Faymex.
#
# Setup (una sola vez):
#   1. Entra a Railway con la cuenta gsaltron@gmail.com.
#   2. Proyecto Recontrata -> Settings -> Tokens -> crea un "Project Token"
#      (environment: production).
#   3. Pega ese token en el archivo `.railway-token` de esta carpeta (una línea).
#      Ese archivo esta gitignored: NUNCA se commitea.
#
# Uso:
#   ./deploy.sh            # deploy y espera a que termine el build
#   ./deploy.sh --detach   # deploy sin esperar
set -euo pipefail
cd "$(dirname "$0")"

if [[ ! -f .railway-token ]]; then
  echo "ERROR: falta el archivo .railway-token (project token de Railway)." >&2
  echo "Ver instrucciones de setup en la cabecera de deploy.sh." >&2
  exit 1
fi

token="$(tr -d '[:space:]' < .railway-token)"
if [[ -z "$token" ]]; then
  echo "ERROR: .railway-token esta vacio." >&2
  exit 1
fi

echo "Desplegando Recontrata a Railway (produccion)..."
RAILWAY_TOKEN="$token" railway up "$@"
