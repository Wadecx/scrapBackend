# Étape 1 : Utilise une image Python avec les outils nécessaires
FROM python:3.10-slim

# Étape 2 : Définis le dossier de travail
WORKDIR /app

# Étape 3 : Copie les fichiers de ton projet dans le conteneur
COPY . /app

# Étape 4 : Installe les dépendances Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Étape 5 : Installe Playwright et ses navigateurs (important)
RUN pip install playwright && \
    playwright install chromium

# Étape 6 : Expose le port utilisé par Flask (ou Gunicorn)
EXPOSE 5000

# Étape 7 : Démarre l'app avec Gunicorn (change `app:app` si besoin)
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
