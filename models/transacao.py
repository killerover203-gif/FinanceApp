# models/transacao.py
class Transacao:
    def __init__(self, id: int = None, descricao: str = "", valor: float = 0.0,
                 tipo: str = "", data: str = "", categoria_id: int = None,
                 usuario_id: int = None):
        self.id = id
        self.descricao = descricao
        self.valor = valor
        self.tipo = tipo
        self.data = data
        self.categoria_id = categoria_id
        self.usuario_id = usuario_id