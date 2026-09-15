# config.py
import os
import sys
from pathlib import Path


def get_db_path() -> str:
    if getattr(sys, 'frozen', False):
        # Executável: usa a pasta onde o .exe está
        base_path = Path(sys.executable).parent / 'data'
    else:
        # Desenvolvimento: usa pasta data/
        base_path = Path(__file__).parent.resolve() / 'data'

    base_path.mkdir(parents=True, exist_ok=True)
    return str(base_path / 'financas.db')


DB_PATH = get_db_path()