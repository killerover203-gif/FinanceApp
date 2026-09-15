# models/meta.py
class Meta:
    def __init__(self, id: int = None, nome: str = "", tipo: str = "",
                 valor_alvo: float = 0.0, categoria_id: int = None,
                 data_limite: str = None, ativa: int = 1, usuario_id: int = None):
        self.id = id
        self.nome = nome
        self.tipo = tipo
        self.valor_alvo = valor_alvo
        self.categoria_id = categoria_id
        self.data_limite = data_limite
        self.ativa = ativa
        self.usuario_id = usuario_id