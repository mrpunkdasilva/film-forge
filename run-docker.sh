#!/bin/bash

# Cores para saída
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== FilmForge Docker Launcher ===${NC}"

# Verificar se o Docker está instalado
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker não está instalado. Por favor, instale o Docker primeiro.${NC}"
    exit 1
fi

# Verificar se o Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose não está instalado. Por favor, instale o Docker Compose primeiro.${NC}"
    exit 1
fi

# Criar diretório de dados se não existir
mkdir -p data

# Verificar se os arquivos de dados existem
if [ ! -f "data/movies.csv" ]; then
    echo -e "${YELLOW}Arquivo data/movies.csv não encontrado. Certifique-se de que os dados necessários estão disponíveis.${NC}"
fi

echo -e "${GREEN}Construindo e iniciando o container FilmForge...${NC}"
docker-compose up --build -d

# Verificar se o container está rodando
if [ "$(docker ps -q -f name=film-forge)" ]; then
    echo -e "${GREEN}FilmForge está rodando!${NC}"
    echo -e "${GREEN}Acesse a aplicação em: http://localhost:8501${NC}"
else
    echo -e "${RED}Erro ao iniciar o container. Verifique os logs com: docker-compose logs${NC}"
    exit 1
fi