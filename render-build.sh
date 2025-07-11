#!/bin/bash

# Mise à jour des outils pip, setuptools et wheel
pip install --upgrade pip setuptools wheel

# Installer Cython en premier pour éviter les erreurs de build
pip install cython==0.29.36

# Installer les autres dépendances
pip install -r requirements.txt
