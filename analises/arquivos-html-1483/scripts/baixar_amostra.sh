#!/usr/bin/env bash
# Baixa os arquivos da amostra (dados/amostra.csv) do bucket público do
# Querido Diário. Uso: baixar_amostra.sh <amostra.csv> <pasta_destino>
set -euo pipefail
amostra="$1"; destino="$2"
mkdir -p "$destino"
tail -n +2 "$amostra" | while IFS=, read -r gid _spider _base _data url; do
    [ -s "$destino/$gid" ] || curl -sS -m 60 -o "$destino/$gid" "$url"
    sleep 0.3
done
