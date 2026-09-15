# config/__init__.py
"""Configurações do aplicativo."""
import os

# Caminho do banco de dados
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Cria a pasta data se não existir
os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "financas.db")

# Importa os temas
from config.temas import TEMAS, TEMA_PADRAO