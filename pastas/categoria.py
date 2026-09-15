# models/categoria.py
class Categoria:
    def __init__(self, id: int = None, nome: str = "", icone: str = None, usuario_id: int = None):
        self.id = id
        self.nome = nome
        self.icone = icone
        self.usuario_id = usuario_id