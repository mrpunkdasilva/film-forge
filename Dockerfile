FROM python:3.10-slim as builder

WORKDIR /app

# Instalar dependências de compilação e ferramentas
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar apenas o arquivo de requisitos primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Criar e ativar ambiente virtual
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instalar dependências no ambiente virtual
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Segunda etapa - imagem final
FROM python:3.10-slim

WORKDIR /app

# Instalar apenas o curl para o healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar o ambiente virtual da etapa anterior
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copiar o código da aplicação
COPY . .

# Criar usuário não-root para executar a aplicação
RUN useradd -m appuser && \
    chown -R appuser:appuser /app

# Mudar para o usuário não-root
USER appuser

# Configurar variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Expor a porta do Streamlit
EXPOSE 8501

# Verificar se a aplicação está funcionando
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Criar diretório de dados e garantir que ele exista
RUN mkdir -p /app/data

# Comando para iniciar a aplicação
ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]