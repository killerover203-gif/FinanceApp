# models/conta_prevista.py
class ContaPrevista:
    def __init__(self, id: int = None, nome: str = "", valor: float = 0.0,
                 tipo: str = "", dia_vencimento: int = 1, categoria_id: int = None,
                 ativa: int = 1, usuario_id: int = None):
        self.id = id
        self.nome = nome
        self.valor = valor
        self.tipo = tipo
        self.dia_vencimento = dia_vencimento
        self.categoria_id = categoria_id
        self.ativa = ativa
        self.usuario_id = usuario_id