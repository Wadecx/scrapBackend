#!/bin/bash

# Installer les dépendances Python
pip install -r requirements.txt

# Installer les navigateurs nécessaires à Playwright avec les bonnes dépendances système
playwright install --with-deps
