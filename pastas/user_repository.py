# database/user_repository.py
"""Repositório de usuários para autenticação."""
from database.connection import get_connection
from models.user import User


class UserRepository:
    def salvar(self, user: User) -> int:
        """Salva um novo usuário no banco."""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO usuarios (nome, email, senha_hash, salt, "
                "pergunta_seguranca, resposta_hash, resposta_salt, criado_em) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (user.nome, user.email, user.senha_hash, user.salt,
                 user.pergunta_seguranca, user.resposta_hash, user.resposta_salt,
                 user.criado_em)
            )
            conn.commit()
            novo_id = cursor.lastrowid
            conn.close()
            return novo_id
        except Exception as e:
            conn.close()
            raise e

    def buscar_por_email(self, email: str) -> User:
        """Busca um usuário pelo email."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return User(
                id=row["id"],
                nome=row["nome"],
                email=row["email"],
                senha_hash=row["senha_hash"],
                salt=row["salt"],
                pergunta_seguranca=row["pergunta_seguranca"],
                resposta_hash=row["resposta_hash"],
                resposta_salt=row["resposta_salt"],
                criado_em=row["criado_em"]
            )
        return None

    def buscar_por_id(self, id: int) -> User:
        """Busca um usuário pelo ID."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return User(
                id=row["id"],
                nome=row["nome"],
                email=row["email"],
                senha_hash=row["senha_hash"],
                salt=row["salt"],
                pergunta_seguranca=row["pergunta_seguranca"],
                resposta_hash=row["resposta_hash"],
                resposta_salt=row["resposta_salt"],
                criado_em=row["criado_em"]
            )
        return None

    def atualizar_senha(self, usuario_id: int, nova_senha_hash: str, novo_salt: str):
        """Atualiza a senha de um usuário."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE usuarios SET senha_hash = ?, salt = ? WHERE id = ?",
            (nova_senha_hash, novo_salt, usuario_id)
        )
        conn.commit()
        conn.close()