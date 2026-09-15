# database/user_repository.py
"""
Repositório de usuários para autenticação — Firestore.
Substitui a versão SQLite original.
"""
from database.firebase_connection import get_db
from models.user import User


class UserRepository:
    def __init__(self):
        self.db = get_db()
        self.colecao = self.db.collection("usuarios")

    def salvar(self, user: User) -> str:
        """
        Salva um novo usuário no Firestore.
        Retorna o ID do documento criado (string).
        """
        try:
            # Prepara os dados
            dados = {
                "nome": user.nome,
                "email": user.email.lower(),
                "senha_hash": user.senha_hash,
                "salt": user.salt,
                "pergunta_seguranca": user.pergunta_seguranca,
                "resposta_hash": user.resposta_hash,
                "resposta_salt": user.resposta_salt,
                "criado_em": user.criado_em,
            }

            # Cria um novo documento com ID automático
            doc_ref = self.colecao.document()
            doc_ref.set(dados)

            # Atualiza o objeto user com o novo ID
            user.id = doc_ref.id
            return doc_ref.id

        except Exception as e:
            raise Exception(f"Erro ao salvar usuário: {str(e)}")

    def buscar_por_email(self, email: str) -> User:
        """
        Busca um usuário pelo email.
        No Firestore, fazemos uma consulta com filtro.
        """
        if not email:
            return None

        email_normalizado = email.strip().lower()

        # Consulta: onde email == email_normalizado
        query = self.colecao.where("email", "==", email_normalizado).limit(1)
        resultados = query.stream()

        for doc in resultados:
            dados = doc.to_dict()
            return User(
                id=doc.id,
                nome=dados.get("nome", ""),
                email=dados.get("email", ""),
                senha_hash=dados.get("senha_hash", ""),
                salt=dados.get("salt", ""),
                pergunta_seguranca=dados.get("pergunta_seguranca"),
                resposta_hash=dados.get("resposta_hash"),
                resposta_salt=dados.get("resposta_salt"),
                criado_em=dados.get("criado_em"),
            )

        return None

    def buscar_por_id(self, id: str) -> User:
        """
        Busca um usuário pelo ID do documento.
        """
        if not id:
            return None

        doc = self.colecao.document(str(id)).get()

        if doc.exists:
            dados = doc.to_dict()
            return User(
                id=doc.id,
                nome=dados.get("nome", ""),
                email=dados.get("email", ""),
                senha_hash=dados.get("senha_hash", ""),
                salt=dados.get("salt", ""),
                pergunta_seguranca=dados.get("pergunta_seguranca"),
                resposta_hash=dados.get("resposta_hash"),
                resposta_salt=dados.get("resposta_salt"),
                criado_em=dados.get("criado_em"),
            )

        return None

    def atualizar_senha(self, usuario_id: str, nova_senha_hash: str, novo_salt: str):
        """
        Atualiza a senha de um usuário.
        """
        if not usuario_id:
            raise ValueError("ID do usuário é obrigatório")

        doc_ref = self.colecao.document(str(usuario_id))
        doc_ref.update({
            "senha_hash": nova_senha_hash,
            "salt": novo_salt,
        })
