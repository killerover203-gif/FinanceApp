# models/user.py
"""
Modelo de usuário para autenticação.
⚠️ No Firestore, o ID é uma string (não inteiro autoincremental).
"""
from datetime import datetime


class User:
    def __init__(self, id: str = None, nome: str = "", email: str = "",
                 senha_hash: str = "", salt: str = "",
                 pergunta_seguranca: str = None,
                 resposta_hash: str = None,
                 resposta_salt: str = None,
                 criado_em: str = None):
        self.id = id  # Agora é string (ID do documento Firestore)
        self.nome = nome
        self.email = email
        self.senha_hash = senha_hash
        self.salt = salt
        self.pergunta_seguranca = pergunta_seguranca
        self.resposta_hash = resposta_hash
        self.resposta_salt = resposta_salt
        self.criado_em = criado_em or datetime.now().isoformat()
