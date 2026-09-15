# database/connection.py
import sqlite3
import os
from pathlib import Path

# Importa o logger
try:
    from utils.logger import log
except ImportError:
    def log(msg):
        print(msg)

from config import DB_PATH


def get_connection():
    log(f"🔌 get_connection() chamado")
    log(f"   DB_PATH = {DB_PATH}")

    db_dir = os.path.dirname(DB_PATH)
    log(f"   Pasta do banco: {db_dir}")
    log(f"   Pasta existe: {os.path.exists(db_dir)}")

    os.makedirs(db_dir, exist_ok=True)

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        log(f"✅ Conexão estabelecida com: {DB_PATH}")
        return conn
    except Exception as e:
        log(f"❌ ERRO ao conectar: {e}")
        raise


def init_db():
    log(f"🏗️ init_db() chamado")

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Cria tabelas
        log(f"📋 Criando tabela usuarios...")
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS usuarios
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
                           email
                           TEXT
                           UNIQUE
                           NOT
                           NULL,
                           senha_hash
                           TEXT
                           NOT
                           NULL,
                           salt
                           TEXT
                           NOT
                           NULL,
                           pergunta_seguranca
                           TEXT,
                           resposta_hash
                           TEXT,
                           resposta_salt
                           TEXT,
                           criado_em
                           TEXT
                           NOT
                           NULL
                       )
                       ''')

        log(f"📋 Criando tabela categorias...")
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
                           NULL,
                           icone
                           TEXT,
                           usuario_id
                           INTEGER,
                           FOREIGN
                           KEY
                       (
                           usuario_id
                       ) REFERENCES usuarios
                       (
                           id
                       )
                           )
                       ''')

        log(f"📋 Criando tabela transacoes...")
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
                           NULL,
                           data
                           TEXT
                           NOT
                           NULL,
                           categoria_id
                           INTEGER,
                           usuario_id
                           INTEGER
                           NOT
                           NULL,
                           FOREIGN
                           KEY
                       (
                           categoria_id
                       ) REFERENCES categorias
                       (
                           id
                       ),
                           FOREIGN KEY
                       (
                           usuario_id
                       ) REFERENCES usuarios
                       (
                           id
                       )
                           )
                       ''')

        log(f"📋 Criando tabela metas...")
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
                           NULL,
                           valor_alvo
                           REAL
                           NOT
                           NULL,
                           categoria_id
                           INTEGER,
                           data_limite
                           TEXT,
                           ativa
                           INTEGER
                           DEFAULT
                           1,
                           usuario_id
                           INTEGER
                           NOT
                           NULL,
                           FOREIGN
                           KEY
                       (
                           categoria_id
                       ) REFERENCES categorias
                       (
                           id
                       ),
                           FOREIGN KEY
                       (
                           usuario_id
                       ) REFERENCES usuarios
                       (
                           id
                       )
                           )
                       ''')

        log(f"📋 Criando tabela contas_previstas...")
        cursor.execute('''
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
                           NULL,
                           dia_vencimento
                           INTEGER
                           NOT
                           NULL,
                           categoria_id
                           INTEGER,
                           ativa
                           INTEGER
                           DEFAULT
                           1,
                           usuario_id
                           INTEGER
                           NOT
                           NULL,
                           FOREIGN
                           KEY
                       (
                           categoria_id
                       ) REFERENCES categorias
                       (
                           id
                       ),
                           FOREIGN KEY
                       (
                           usuario_id
                       ) REFERENCES usuarios
                       (
                           id
                       )
                           )
                       ''')

        # Categorias padrão
        cursor.execute("SELECT COUNT(*) as total FROM categorias")
        if cursor.fetchone()["total"] == 0:
            log(f"📝 Criando categorias padrão...")
            categorias_padrao = [
                ("Alimentação", "RESTAURANT", None),
                ("Transporte", "DIRECTIONS_CAR", None),
                ("Moradia", "HOME", None),
                ("Lazer", "SPORTS_ESPORTS", None),
                ("Saúde", "LOCAL_HOSPITAL", None),
                ("Educação", "SCHOOL", None),
                ("Salário", "WORK", None),
                ("Investimentos", "TRENDING_UP", None),
            ]
            cursor.executemany(
                "INSERT INTO categorias (nome, icone, usuario_id) VALUES (?, ?, ?)",
                categorias_padrao
            )

        # ✅ COMMIT OBRIGATÓRIO
        log(f"💾 Executando COMMIT...")
        conn.commit()

        # Verifica se o arquivo foi criado
        if os.path.exists(DB_PATH):
            size = os.path.getsize(DB_PATH)
            log(f"✅ Banco criado com sucesso! Tamanho: {size} bytes")
        else:
            log(f"❌ ERRO: Arquivo do banco NÃO foi criado!")

        conn.close()
        log(f"✅ init_db() concluído")

    except Exception as e:
        log(f"❌ ERRO CRÍTICO em init_db(): {e}")
        import traceback
        log(traceback.format_exc())
        raise