# utils/logger.py
import sys
import os
from pathlib import Path
from datetime import datetime


class Logger:
    _instance = None
    _log_file = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        # Define o caminho do log
        if getattr(sys, 'frozen', False):
            # Executável
            appdata = os.environ.get('APPDATA', str(Path.home()))
            log_dir = Path(appdata) / 'FinanceApp'
        else:
            # Desenvolvimento
            log_dir = Path(__file__).parent.parent / 'data'

        log_dir.mkdir(parents=True, exist_ok=True)
        self._log_file = log_dir / 'financeapp.log'

        # Limpa log antigo se for muito grande
        if self._log_file.exists() and self._log_file.stat().st_size > 1_000_000:
            self._log_file.unlink()

    def log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] {message}\n"

        # Escreve no arquivo
        try:
            with open(self._log_file, 'a', encoding='utf-8') as f:
                f.write(log_line)
        except Exception as e:
            print(f"ERRO AO ESCREVER LOG: {e}")

        # Também imprime no console
        print(message)

    def get_log_path(self):
        return str(self._log_file)


def log(message):
    """Função auxiliar para facilitar o uso."""
    Logger.get_instance().log(message)


def get_log_path():
    return Logger.get_instance().get_log_path()