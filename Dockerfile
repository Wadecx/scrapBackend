FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers dans l'image Docker
COPY . .

# Installer les dépendances Python
RUN pip install -r requirements.txt

# Exposer le port sur lequel l'app Flask va tourner
EXPOSE 5000

# Lancer l'application Flask avec gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
