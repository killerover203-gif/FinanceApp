# database/repositories.py
"""
Repositórios de dados — Firestore.
Substitui a versão SQLite original.
Mantém a mesma interface para compatibilidade com o resto do sistema.
"""
from database.firebase_connection import get_db
from models.entities import Transacao, Categoria, Meta, ContaPrevista
from datetime import datetime, date


class TransacaoRepository:
    def __init__(self):
        self.db = get_db()
        self.colecao = self.db.collection("transacoes")

    def salvar(self, transacao: Transacao, usuario_id: str = None) -> str:
        """
        Salva uma nova transação.
        Retorna o ID do documento criado.
        """
        dados = {
            "descricao": transacao.descricao,
            "valor": float(transacao.valor),
            "tipo": transacao.tipo,
            "data": transacao.data.isoformat() if hasattr(transacao.data, 'isoformat') else str(transacao.data),
            "categoria_id": transacao.categoria_id,
            "usuario_id": usuario_id,
        }

        doc_ref = self.colecao.document()
        doc_ref.set(dados)
        transacao.id = doc_ref.id
        return doc_ref.id

    def listar_todas(self, usuario_id: str = None) -> list[Transacao]:
        """
        Lista todas as transações.
        Se usuario_id for fornecido, filtra por usuário.
        """
        query = self.colecao

        if usuario_id:
            query = query.where("usuario_id", "==", usuario_id)

        query = query.order_by("data", direction="DESCENDING")
        docs = query.stream()

        resultado = []
        for doc in docs:
            d = doc.to_dict()
            try:
                data_obj = datetime.fromisoformat(d["data"]).date()
            except:
                data_obj = date.today()

            resultado.append(Transacao(
                id=doc.id,
                descricao=d.get("descricao", ""),
                valor=d.get("valor", 0.0),
                tipo=d.get("tipo", ""),
                data=data_obj,
                categoria_id=d.get("categoria_id"),
            ))

        return resultado

    def atualizar(self, transacao: Transacao) -> None:
        """Atualiza uma transação existente."""
        if not transacao.id:
            raise ValueError("ID da transação é obrigatório para atualizar")

        dados = {
            "descricao": transacao.descricao,
            "valor": float(transacao.valor),
            "tipo": transacao.tipo,
            "data": transacao.data.isoformat() if hasattr(transacao.data, 'isoformat') else str(transacao.data),
            "categoria_id": transacao.categoria_id,
        }

        self.colecao.document(str(transacao.id)).update(dados)

    def deletar(self, id: str) -> None:
        """Exclui uma transação."""
        self.colecao.document(str(id)).delete()

    def _buscar_todas_como_dict(self, usuario_id: str = None) -> list[dict]:
        """Helper: retorna transações como lista de dicts (para cálculos)."""
        query = self.colecao
        if usuario_id:
            query = query.where("usuario_id", "==", usuario_id)

        docs = query.stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]

    def despesas_por_categoria(self, usuario_id: str = None) -> list[dict]:
        """
        Agrupa despesas por categoria.
        No Firestore, fazemos a agregação em memória.
        """
        transacoes = self._buscar_todas_como_dict(usuario_id)
        categorias = self._buscar_categorias_dict()

        agrupado = {}
        for t in transacoes:
            if t.get("tipo") != "despesa":
                continue

            cat_id = t.get("categoria_id")
            cat = categorias.get(str(cat_id) if cat_id else "", {"nome": "Sem categoria", "icone": "HELP"})
            nome = cat.get("nome", "Sem categoria")
            icone = cat.get("icone", "HELP")

            if nome not in agrupado:
                agrupado[nome] = {"nome": nome, "icone": icone, "total": 0.0}
            agrupado[nome]["total"] += t.get("valor", 0.0)

        resultado = sorted(agrupado.values(), key=lambda x: x["total"], reverse=True)
        return resultado

    def _buscar_categorias_dict(self) -> dict:
        """Helper: busca categorias em um dict indexado por ID."""
        cat_ref = self.db.collection("categorias")
        docs = cat_ref.stream()
        return {doc.id: doc.to_dict() for doc in docs}

    def receitas_vs_despesas_por_mes(self, limite_meses: int = 6, usuario_id: str = None) -> list[dict]:
        """
        Retorna receitas vs despesas dos últimos N meses.
        Agregação feita em memória.
        """
        transacoes = self._buscar_todas_como_dict(usuario_id)

        # Agrupa por mês
        por_mes = {}
        for t in transacoes:
            data_str = t.get("data", "")
            if not data_str or len(data_str) < 7:
                continue
            ano_mes = data_str[:7]  # "YYYY-MM"

            if ano_mes not in por_mes:
                por_mes[ano_mes] = {"mes": ano_mes, "receitas": 0.0, "despesas": 0.0}

            if t.get("tipo") == "receita":
                por_mes[ano_mes]["receitas"] += t.get("valor", 0.0)
            elif t.get("tipo") == "despesa":
                por_mes[ano_mes]["despesas"] += t.get("valor", 0.0)

        # Ordena e pega os últimos N meses
        resultado = sorted(por_mes.values(), key=lambda x: x["mes"], reverse=True)[:limite_meses]
        resultado.reverse()  # Do mais antigo para o mais novo
        return resultado

    def media_mensal_despesas(self, meses: int = 6, usuario_id: str = None) -> float:
        """Calcula a média mensal de despesas."""
        hoje = date.today()
        total_despesas = 0.0

        for i in range(meses):
            mes = hoje.month - i
            ano = hoje.year
            while mes <= 0:
                mes += 12
                ano -= 1
            ano_mes = f"{ano}-{mes:02d}"
            total_mes = self.total_despesas_mes(ano_mes, usuario_id)
            total_despesas += total_mes

        return total_despesas / meses if meses > 0 else 0.0

    def total_despesas_mes(self, ano_mes: str, usuario_id: str = None) -> float:
        """Retorna o total de despesas de um mês específico."""
        transacoes = self._buscar_todas_como_dict(usuario_id)
        total = 0.0

        for t in transacoes:
            data_str = t.get("data", "")
            if t.get("tipo") == "despesa" and data_str.startswith(ano_mes):
                total += t.get("valor", 0.0)

        return total

    def categoria_que_mais_gastou_mes_atual(self, usuario_id: str = None) -> dict | None:
        """Retorna a categoria com mais gastos no mês atual."""
        hoje = date.today()
        inicio_mes = hoje.replace(day=1).isoformat()
        ano_mes_atual = inicio_mes[:7]

        transacoes = self._buscar_todas_como_dict(usuario_id)
        categorias = self._buscar_categorias_dict()

        agrupado = {}
        for t in transacoes:
            if t.get("tipo") != "despesa":
                continue
            data_str = t.get("data", "")
            if not data_str.startswith(ano_mes_atual):
                continue

            cat_id = t.get("categoria_id")
            cat = categorias.get(str(cat_id) if cat_id else "", {"nome": "Sem categoria"})
            nome = cat.get("nome", "Sem categoria")

            if nome not in agrupado:
                agrupado[nome] = 0.0
            agrupado[nome] += t.get("valor", 0.0)

        if not agrupado:
            return None

        top = max(agrupado.items(), key=lambda x: x[1])
        return {"nome": top[0], "total": top[1]}

    def maior_despesa_mes_atual(self, usuario_id: str = None) -> dict | None:
        """Retorna a maior despesa do mês atual."""
        hoje = date.today()
        ano_mes_atual = hoje.replace(day=1).isoformat()[:7]

        transacoes = self._buscar_todas_como_dict(usuario_id)

        maior = None
        for t in transacoes:
            if t.get("tipo") != "despesa":
                continue
            data_str = t.get("data", "")
            if not data_str.startswith(ano_mes_atual):
                continue

            if maior is None or t.get("valor", 0) > maior.get("valor", 0):
                maior = t

        if maior:
            return {
                "descricao": maior.get("descricao", ""),
                "valor": maior.get("valor", 0.0),
                "data": maior.get("data", ""),
            }
        return None


class CategoriaRepository:
    def __init__(self):
        self.db = get_db()
        self.colecao = self.db.collection("categorias")

    def listar_todas(self, usuario_id: str = None) -> list[Categoria]:
        """
        Lista todas as categorias: globais (usuario_id=None) + do usuário.
        """
        # Busca globais
        query_globais = self.colecao.where("usuario_id", "==", None)
        docs_globais = list(query_globais.stream())

        # Busca do usuário
        docs_usuario = []
        if usuario_id:
            query_usuario = self.colecao.where("usuario_id", "==", usuario_id)
            docs_usuario = list(query_usuario.stream())

        todos = docs_globais + docs_usuario
        # Ordena por nome
        todos.sort(key=lambda d: d.to_dict().get("nome", "").lower())

        resultado = []
        for doc in todos:
            d = doc.to_dict()
            resultado.append(Categoria(
                id=doc.id,
                nome=d.get("nome", ""),
                icone=d.get("icone"),
            ))

        return resultado

    def listar_como_dict(self, usuario_id: str = None) -> list[dict]:
        """Retorna categorias como lista de dicts."""
        query_globais = self.colecao.where("usuario_id", "==", None)
        docs_globais = list(query_globais.stream())

        docs_usuario = []
        if usuario_id:
            query_usuario = self.colecao.where("usuario_id", "==", usuario_id)
            docs_usuario = list(query_usuario.stream())

        todos = docs_globais + docs_usuario
        todos.sort(key=lambda d: d.to_dict().get("nome", "").lower())

        return [{"id": doc.id, **doc.to_dict()} for doc in todos]


class MetaRepository:
    def __init__(self):
        self.db = get_db()
        self.colecao = self.db.collection("metas")

    def salvar(self, meta: Meta, usuario_id: str = None) -> str:
        """Salva uma nova meta."""
        data_limite = None
        if meta.data_limite:
            if hasattr(meta.data_limite, 'isoformat'):
                data_limite = meta.data_limite.isoformat()
            else:
                data_limite = str(meta.data_limite)

        dados = {
            "nome": meta.nome,
            "tipo": meta.tipo,
            "valor_alvo": float(meta.valor_alvo),
            "categoria_id": meta.categoria_id,
            "data_limite": data_limite,
            "ativa": bool(meta.ativa),
            "usuario_id": usuario_id,
        }

        doc_ref = self.colecao.document()
        doc_ref.set(dados)
        meta.id = doc_ref.id
        return doc_ref.id

    def listar_todas(self, usuario_id: str = None) -> list[Meta]:
        """Lista todas as metas do usuário."""
        query = self.colecao
        if usuario_id:
            query = query.where("usuario_id", "==", usuario_id)

        docs = query.stream()
        # Ordena em memória: ativas primeiro, depois por nome
        lista = []
        for doc in docs:
            d = doc.to_dict()
            try:
                data_limite = datetime.fromisoformat(d["data_limite"]).date() if d.get("data_limite") else None
            except:
                data_limite = None

            lista.append(Meta(
                id=doc.id,
                nome=d.get("nome", ""),
                tipo=d.get("tipo", ""),
                valor_alvo=d.get("valor_alvo", 0.0),
                categoria_id=d.get("categoria_id"),
                data_limite=data_limite,
                ativa=d.get("ativa", True),
            ))

        lista.sort(key=lambda m: (not m.ativa, m.nome.lower()))
        return lista

    def listar_como_dict(self, usuario_id: str = None) -> list[dict]:
        """Retorna metas como lista de dicts."""
        query = self.colecao
        if usuario_id:
            query = query.where("usuario_id", "==", usuario_id)

        docs = query.stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]

    def atualizar(self, meta: Meta) -> None:
        """Atualiza uma meta existente."""
        if not meta.id:
            raise ValueError("ID da meta é obrigatório")

        data_limite = None
        if meta.data_limite:
            if hasattr(meta.data_limite, 'isoformat'):
                data_limite = meta.data_limite.isoformat()
            else:
                data_limite = str(meta.data_limite)

        dados = {
            "nome": meta.nome,
            "tipo": meta.tipo,
            "valor_alvo": float(meta.valor_alvo),
            "categoria_id": meta.categoria_id,
            "data_limite": data_limite,
            "ativa": bool(meta.ativa),
        }

        self.colecao.document(str(meta.id)).update(dados)

    def deletar(self, id: str) -> None:
        """Exclui uma meta."""
        self.colecao.document(str(id)).delete()


class ContaPrevistaRepository:
    def __init__(self):
        self.db = get_db()
        self.colecao = self.db.collection("contas_previstas")

    def salvar(self, conta: ContaPrevista, usuario_id: str = None) -> str:
        """Salva uma nova conta prevista."""
        dados = {
            "nome": conta.nome,
            "valor": float(conta.valor),
            "tipo": conta.tipo,
            "dia_vencimento": int(conta.dia_vencimento),
            "categoria_id": conta.categoria_id,
            "ativa": bool(conta.ativa),
            "usuario_id": usuario_id,
        }

        doc_ref = self.colecao.document()
        doc_ref.set(dados)
        conta.id = doc_ref.id
        return doc_ref.id

    def listar_todas(self, usuario_id: str = None, apenas_ativas: bool = True) -> list[ContaPrevista]:
        """Lista todas as contas previstas do usuário."""
        query = self.colecao
        if usuario_id:
            query = query.where("usuario_id", "==", usuario_id)
        if apenas_ativas:
            query = query.where("ativa", "==", True)

        docs = query.stream()
        lista = []
        for doc in docs:
            d = doc.to_dict()
            lista.append(ContaPrevista(
                id=doc.id,
                nome=d.get("nome", ""),
                valor=d.get("valor", 0.0),
                tipo=d.get("tipo", ""),
                dia_vencimento=d.get("dia_vencimento", 1),
                categoria_id=d.get("categoria_id"),
                ativa=d.get("ativa", True),
            ))

        lista.sort(key=lambda c: c.dia_vencimento)
        return lista

    def listar_como_dict(self, usuario_id: str = None, apenas_ativas: bool = True) -> list[dict]:
        """Retorna contas previstas como lista de dicts."""
        query = self.colecao
        if usuario_id:
            query = query.where("usuario_id", "==", usuario_id)
        if apenas_ativas:
            query = query.where("ativa", "==", True)

        docs = query.stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]

    def atualizar(self, conta: ContaPrevista) -> None:
        """Atualiza uma conta prevista existente."""
        if not conta.id:
            raise ValueError("ID da conta é obrigatório")

        dados = {
            "nome": conta.nome,
            "valor": float(conta.valor),
            "tipo": conta.tipo,
            "dia_vencimento": int(conta.dia_vencimento),
            "categoria_id": conta.categoria_id,
            "ativa": bool(conta.ativa),
        }

        self.colecao.document(str(conta.id)).update(dados)

    def deletar(self, id: str) -> None:
        """Exclui uma conta prevista."""
        self.colecao.document(str(id)).delete()
