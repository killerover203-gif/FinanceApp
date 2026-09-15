# models/entities.py
"""
Entidades de domínio.
⚠️ No Firestore, os IDs são strings (não inteiros autoincrementais).
Mantemos compatibilidade aceitando ambos os tipos.
"""
from dataclasses import dataclass
from datetime import date


@dataclass
class Transacao:
    descricao: str
    valor: float
    tipo: str  # 'receita' ou 'despesa'
    data: date
    id: str | int | None = None  # Firestore = string, SQLite = int
    categoria_id: str | int | None = None


@dataclass
class Categoria:
    nome: str
    icone: str
    id: str | int | None = None


@dataclass
class Meta:
    nome: str
    tipo: str  # 'economia', 'gasto_categoria', 'acumulado'
    valor_alvo: float
    id: str | int | None = None
    categoria_id: str | int | None = None
    data_limite: date | None = None
    ativa: bool = True


@dataclass
class ContaPrevista:
    nome: str
    valor: float
    tipo: str  # 'receita' ou 'despesa'
    dia_vencimento: int  # 1-31
    id: str | int | None = None
    categoria_id: str | int | None = None
    ativa: bool = True
