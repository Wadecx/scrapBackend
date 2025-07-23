#!/bin/bash

# Installer les dépendances Python
pip install -r requirements.txt

# Installer Chromium pour Playwright
playwright install chromium