# Étape 1 : Utilise une image Python légère
FROM python:3.10-slim

# Étape 2 : Installe les dépendances système nécessaires à Chromium (Playwright)
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    libnss3 \
    libatk-bridge2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libxshmfence1 \
    libgtk-3-0 \
    libdrm2 \
    libx11-xcb1 \
    --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Étape 3 : Crée le dossier de travail
WORKDIR /app

# Étape 4 : Copie les fichiers de l'application dans le conteneur
COPY . /app

# Étape 5 : Installe les dépendances Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install playwright && \
    playwright install chromium && \
    rm -rf ~/.cache/pip

# Étape 6 : Expose le port pour Render / Flask
EXPOSE 5000

# Étape 7 : Démarrage avec Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
