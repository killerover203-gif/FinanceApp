# models/entities.py
from dataclasses import dataclass
from datetime import date

@dataclass
class Transacao:
    descricao: str
    valor: float
    tipo: str  # 'receita' ou 'despesa'
    data: date
    id: int | None = None
    categoria_id: int | None = None

@dataclass
class Categoria:
    nome: str
    icone: str
    id: int | None = None

@dataclass
class Meta:
    nome: str
    tipo: str  # 'economia', 'gasto_categoria', 'acumulado'
    valor_alvo: float
    id: int | None = None
    categoria_id: int | None = None
    data_limite: date | None = None
    ativa: bool = True

@dataclass
class ContaPrevista:
    nome: str
    valor: float
    tipo: str  # 'receita' ou 'despesa'
    dia_vencimento: int  # 1-31
    id: int | None = None
    categoria_id: int | None = None
    ativa: bool = True