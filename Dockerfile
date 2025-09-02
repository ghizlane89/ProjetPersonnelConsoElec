FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de configuration
COPY environment.yml .
COPY requirements.txt ./config/

# Installer les dépendances Conda
RUN conda env create -f environment.yml && \
    echo "source activate energy-agent" > ~/.bashrc

# Copier le code source
COPY . .

# Exposer le port Streamlit
EXPOSE 8501

# Commande par défaut
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]





