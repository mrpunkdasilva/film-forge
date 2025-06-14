#!/bin/bash

# Cores para saída
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== FilmForge Docker Stopper ===${NC}"

# Verificar se o Docker está instalado
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker não está instalado.${NC}"
    exit 1
fi

# Verificar se o Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose não está instalado.${NC}"
    exit 1
fi

# Verificar se o container está rodando
if [ "$(docker ps -q -f name=film-forge)" ]; then
    echo -e "${YELLOW}Parando o container FilmForge...${NC}"
    docker-compose down
    echo -e "${GREEN}Container parado com sucesso!${NC}"
else
    echo -e "${YELLOW}O container FilmForge não está rodando.${NC}"
fi