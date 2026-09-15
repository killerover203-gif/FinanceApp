# database/connection.py
import sqlite3
from config import DB_PATH


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Tabela de categorias
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS categorias
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       nome
                       TEXT
                       NOT
                       NULL
                       UNIQUE,
                       icone
                       TEXT
                       NOT
                       NULL
                       DEFAULT
                       'CATEGORY'
                   )
                   ''')

    # Tabela de transações
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS transacoes
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       descricao
                       TEXT
                       NOT
                       NULL,
                       valor
                       REAL
                       NOT
                       NULL,
                       tipo
                       TEXT
                       NOT
                       NULL
                       CHECK (
                       tipo
                       IN
                   (
                       'receita',
                       'despesa'
                   )),
                       data TEXT NOT NULL,
                       categoria_id INTEGER,
                       FOREIGN KEY
                   (
                       categoria_id
                   ) REFERENCES categorias
                   (
                       id
                   )
                       )
                   ''')

    # Tabela de metas
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS metas
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       nome
                       TEXT
                       NOT
                       NULL,
                       tipo
                       TEXT
                       NOT
                       NULL
                       CHECK (
                       tipo
                       IN
                   (
                       'economia',
                       'gasto_categoria',
                       'acumulado'
                   )),
                       valor_alvo REAL NOT NULL,
                       categoria_id INTEGER,
                       data_limite TEXT,
                       ativa INTEGER NOT NULL DEFAULT 1,
                       FOREIGN KEY
                   (
                       categoria_id
                   ) REFERENCES categorias
                   (
                       id
                   )
                       )
                   ''')

    # ✅ TABELA DE CONTAS PREVISTAS
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS contas_previstas
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       nome
                       TEXT
                       NOT
                       NULL,
                       valor
                       REAL
                       NOT
                       NULL,
                       tipo
                       TEXT
                       NOT
                       NULL
                       CHECK (
                       tipo
                       IN
                   (
                       'receita',
                       'despesa'
                   )),
                       dia_vencimento INTEGER NOT NULL CHECK
                   (
                       dia_vencimento
                       BETWEEN
                       1
                       AND
                       31
                   ),
                       categoria_id INTEGER,
                       ativa INTEGER NOT NULL DEFAULT 1,
                       FOREIGN KEY
                   (
                       categoria_id
                   ) REFERENCES categorias
                   (
                       id
                   )
                       )
                   """)

    # Categorias padrão
    cursor.execute("SELECT COUNT(*) FROM categorias")
    if cursor.fetchone()[0] == 0:
        categorias_padrao = [
            ("Alimentação", "RESTAURANT"), ("Transporte", "DIRECTIONS_CAR"),
            ("Moradia", "HOME"), ("Lazer", "SPORTS_ESPORTS"),
            ("Saúde", "LOCAL_HOSPITAL"), ("Educação", "SCHOOL"),
            ("Salário", "WORK"), ("Outros", "CATEGORY"),
        ]
        cursor.executemany("INSERT INTO categorias (nome, icone) VALUES (?, ?)", categorias_padrao)

    conn.commit()
    conn.close()