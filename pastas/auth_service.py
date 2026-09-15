# services/auth_service.py
"""Serviço de autenticação com criptografia de senhas."""
import hashlib
import secrets
from database.user_repository import UserRepository
from models.user import User


class AuthService:
    def __init__(self):
        self.repo = UserRepository()
        self.usuario_atual = None

    def _gerar_salt(self) -> str:
        """Gera um salt aleatório de 32 caracteres."""
        return secrets.token_hex(16)

    def _hash_senha(self, senha: str, salt: str) -> str:
        """Cria um hash da senha usando SHA-256 + salt."""
        senha_com_salt = salt + senha
        hash_atual = senha_com_salt.encode('utf-8')
        for _ in range(100000):
            hash_atual = hashlib.sha256(hash_atual).digest()
        return hash_atual.hex()

    def registrar(self, nome: str, email: str, senha: str, confirma_senha: str,
                  pergunta_seguranca: str = None, resposta_seguranca: str = None) -> dict:
        """Registra um novo usuário com validações."""
        # Validações
        if not nome or not nome.strip():
            return {"sucesso": False, "erro": "Nome é obrigatório"}

        if not email or "@" not in email or "." not in email:
            return {"sucesso": False, "erro": "Email inválido"}

        if len(senha) < 6:
            return {"sucesso": False, "erro": "Senha deve ter pelo menos 6 caracteres"}

        if senha != confirma_senha:
            return {"sucesso": False, "erro": "As senhas não coincidem"}

        # ✅ Validação da pergunta de segurança
        if not pergunta_seguranca or not pergunta_seguranca.strip():
            return {"sucesso": False, "erro": "Pergunta de segurança é obrigatória"}

        if not resposta_seguranca or not resposta_seguranca.strip():
            return {"sucesso": False, "erro": "Resposta de segurança é obrigatória"}

        # Verifica se email já existe
        if self.repo.buscar_por_email(email):
            return {"sucesso": False, "erro": "Este email já está cadastrado"}

        # Gera salt e hash da senha
        salt = self._gerar_salt()
        senha_hash = self._hash_senha(senha, salt)

        # ✅ Gera salt e hash da resposta de segurança
        resposta_salt = self._gerar_salt()
        resposta_hash = self._hash_senha(resposta_seguranca.strip().lower(), resposta_salt)

        # Cria e salva usuário
        novo_usuario = User(
            nome=nome.strip(),
            email=email.strip().lower(),
            senha_hash=senha_hash,
            salt=salt,
            pergunta_seguranca=pergunta_seguranca.strip(),
            resposta_hash=resposta_hash,
            resposta_salt=resposta_salt,
        )

        try:
            novo_usuario.id = self.repo.salvar(novo_usuario)
            self.usuario_atual = novo_usuario
            return {"sucesso": True, "usuario": novo_usuario}
        except Exception as e:
            return {"sucesso": False, "erro": f"Erro ao cadastrar: {str(e)}"}

    def login(self, email: str, senha: str) -> dict:
        """Autentica um usuário."""
        if not email or not senha:
            return {"sucesso": False, "erro": "Email e senha são obrigatórios"}

        usuario = self.repo.buscar_por_email(email.strip().lower())

        if not usuario:
            return {"sucesso": False, "erro": "Email ou senha incorretos"}

        senha_hash = self._hash_senha(senha, usuario.salt)

        if senha_hash != usuario.senha_hash:
            return {"sucesso": False, "erro": "Email ou senha incorretos"}

        self.usuario_atual = usuario
        return {"sucesso": True, "usuario": usuario}

    def verificar_pergunta_seguranca(self, email: str, resposta: str) -> dict:
        """Verifica se a resposta da pergunta de segurança está correta."""
        if not email or not resposta:
            return {"sucesso": False, "erro": "Preencha todos os campos"}

        usuario = self.repo.buscar_por_email(email.strip().lower())

        if not usuario:
            return {"sucesso": False, "erro": "Email não encontrado"}

        if not usuario.pergunta_seguranca:
            return {"sucesso": False, "erro": "Usuário não tem pergunta de segurança configurada"}

        # Verifica a resposta
        resposta_hash = self._hash_senha(resposta.strip().lower(), usuario.resposta_salt)

        if resposta_hash != usuario.resposta_hash:
            return {"sucesso": False, "erro": "Resposta incorreta"}

        return {
            "sucesso": True,
            "usuario": usuario,
            "pergunta": usuario.pergunta_seguranca,
        }

    def redefinir_senha(self, email: str, resposta: str, nova_senha: str, confirma_senha: str) -> dict:
        """Redefine a senha após validar a pergunta de segurança."""
        # Validações
        if len(nova_senha) < 6:
            return {"sucesso": False, "erro": "Nova senha deve ter pelo menos 6 caracteres"}

        if nova_senha != confirma_senha:
            return {"sucesso": False, "erro": "As senhas não coincidem"}

        # Verifica a pergunta de segurança
        verificacao = self.verificar_pergunta_seguranca(email, resposta)

        if not verificacao["sucesso"]:
            return verificacao

        usuario = verificacao["usuario"]

        # Gera novo hash
        novo_salt = self._gerar_salt()
        nova_senha_hash = self._hash_senha(nova_senha, novo_salt)

        # Atualiza no banco
        self.repo.atualizar_senha(usuario.id, nova_senha_hash, novo_salt)

        return {"sucesso": True, "mensagem": "Senha redefinida com sucesso!"}

    def logout(self):
        """Desloga o usuário atual."""
        self.usuario_atual = None

    def esta_logado(self) -> bool:
        return self.usuario_atual is not None

    def obter_usuario_atual(self) -> User:
        return self.usuario_atual