# services/finance_service.py
"""
Serviço de finanças com isolamento por usuário — Firestore.
Substitui a versão SQLite original.
Mantém a MESMA interface para compatibilidade total com as views.
"""
from database.firebase_connection import get_db
from database.repositories import (
    TransacaoRepository,
    CategoriaRepository,
    MetaRepository,
    ContaPrevistaRepository,
)
from datetime import datetime, timedelta, date


class FinanceService:
    def __init__(self, usuario_id: str = None):
        self.usuario_id = usuario_id
        self.db = get_db()

        # Repositórios
        self.transacao_repo = TransacaoRepository()
        self.categoria_repo = CategoriaRepository()
        self.meta_repo = MetaRepository()
        self.conta_repo = ContaPrevistaRepository()

    def set_usuario_id(self, usuario_id: str):
        """Define o ID do usuário logado."""
        self.usuario_id = usuario_id

    # ============================================
    # CATEGORIAS
    # ============================================
    def listar_categorias(self) -> list:
        """
        Lista todas as categorias (globais + do usuário).
        Retorna lista de dicts com 'id', 'nome', 'icone'.
        """
        categorias = self.categoria_repo.listar_como_dict(usuario_id=self.usuario_id)
        print(f"📋 {len(categorias)} categorias encontradas para usuário {self.usuario_id}")
        return categorias

    def criar_categoria(self, nome: str, icone: str = None) -> str:
        """
        Cria uma nova categoria para o usuário.
        Retorna o ID do documento criado.
        """
        dados = {
            "nome": nome.strip(),
            "icone": icone or "LABEL",
            "usuario_id": self.usuario_id,
        }

        doc_ref = self.db.collection("categorias").document()
        doc_ref.set(dados)
        return doc_ref.id

    # ============================================
    # TRANSAÇÕES
    # ============================================
    def listar_transacoes(self) -> list:
        """
        Lista todas as transações do usuário.
        Retorna lista de dicts.
        """
        transacoes = self.transacao_repo._buscar_todas_como_dict(usuario_id=self.usuario_id)
        # Ordena por data decrescente
        transacoes.sort(key=lambda t: t.get("data", ""), reverse=True)
        return transacoes

    def criar_transacao(self, descricao: str, valor: float, tipo: str, data: str,
                        categoria_id: str = None) -> str:
        """
        Cria uma nova transação.
        """
        # Validação dupla de segurança
        if not tipo or tipo not in ["despesa", "receita"]:
            raise ValueError(f"Tipo inválido: '{tipo}'. Deve ser 'despesa' ou 'receita'")
        if self.usuario_id is None:
            raise ValueError("Não é possível criar transação sem usuario_id!")

        dados = {
            "descricao": descricao,
            "valor": float(valor),
            "tipo": tipo,
            "data": data,
            "categoria_id": categoria_id,
            "usuario_id": self.usuario_id,
        }

        doc_ref = self.db.collection("transacoes").document()
        doc_ref.set(dados)
        novo_id = doc_ref.id
        print(f"💾 Transação {novo_id} criada: tipo='{tipo}', valor={valor}, usuario={self.usuario_id}")
        return novo_id

    def excluir_transacao(self, id: str):
        """Exclui uma transação do usuário."""
        self.db.collection("transacoes").document(str(id)).delete()

    # ============================================
    # METAS
    # ============================================
    def listar_metas(self) -> list:
        """Lista todas as metas do usuário."""
        return self.meta_repo.listar_como_dict(usuario_id=self.usuario_id)

    def criar_meta(self, nome: str, tipo: str, valor_alvo: float,
                   categoria_id: str = None, data_limite: str = None) -> str:
        """Cria uma nova meta."""
        dados = {
            "nome": nome,
            "tipo": tipo,
            "valor_alvo": float(valor_alvo),
            "categoria_id": categoria_id,
            "data_limite": data_limite,
            "ativa": True,
            "usuario_id": self.usuario_id,
        }

        doc_ref = self.db.collection("metas").document()
        doc_ref.set(dados)
        return doc_ref.id

    def excluir_meta(self, id: str):
        """Exclui uma meta do usuário."""
        self.db.collection("metas").document(str(id)).delete()

    # ============================================
    # CONTAS PREVISTAS
    # ============================================
    def listar_contas_previstas(self) -> list:
        """Lista contas previstas ativas do usuário."""
        print(f"🔍 Buscando contas previstas para usuário {self.usuario_id}")
        contas = self.conta_repo.listar_como_dict(usuario_id=self.usuario_id, apenas_ativas=True)
        print(f"📋 {len(contas)} contas encontradas")
        for c in contas:
            print(f"   • {c['nome']} - R$ {c['valor']:.2f} - tipo={c['tipo']} - ativa={c.get('ativa')}")
        return contas

    def criar_conta_prevista(self, nome: str, valor: float, tipo: str, dia_vencimento: int,
                             categoria_id: str = None) -> str:
        """Cria uma nova conta prevista."""
        print(f"💾 Criando conta prevista: {nome}, R$ {valor}, tipo={tipo}, ativa=True")
        dados = {
            "nome": nome,
            "valor": float(valor),
            "tipo": tipo,
            "dia_vencimento": int(dia_vencimento),
            "categoria_id": categoria_id,
            "ativa": True,
            "usuario_id": self.usuario_id,
        }

        doc_ref = self.db.collection("contas_previstas").document()
        doc_ref.set(dados)
        novo_id = doc_ref.id
        print(f"✅ Conta criada com ID: {novo_id}")
        return novo_id

    def excluir_conta_prevista(self, id: str):
        """Exclui uma conta prevista."""
        self.db.collection("contas_previstas").document(str(id)).delete()

    # ============================================
    # HELPERS INTERNOS
    # ============================================
    def _buscar_transacoes(self) -> list[dict]:
        """Busca todas as transações do usuário como dicts."""
        return self.transacao_repo._buscar_todas_como_dict(usuario_id=self.usuario_id)

    def _calcular_saldo(self, transacoes: list = None) -> dict:
        """Calcula receitas, despesas e saldo a partir de uma lista de transações."""
        if transacoes is None:
            transacoes = self._buscar_transacoes()

        receitas = 0.0
        despesas = 0.0
        for t in transacoes:
            if t.get("tipo") == "receita":
                receitas += t.get("valor", 0.0)
            elif t.get("tipo") == "despesa":
                despesas += t.get("valor", 0.0)

        return {"receitas": receitas, "despesas": despesas, "saldo": receitas - despesas}

    # ============================================
    # RESUMO E DASHBOARD
    # ============================================
    def obter_resumo(self) -> dict:
        """Retorna o resumo financeiro do usuário."""
        transacoes = self._buscar_transacoes()
        receitas = 0.0
        despesas = 0.0

        for t in transacoes:
            if t.get("tipo") == "receita":
                receitas += t.get("valor", 0.0)
            elif t.get("tipo") == "despesa":
                despesas += t.get("valor", 0.0)

        return {
            "receitas": receitas,
            "despesas": despesas,
            "saldo": receitas - despesas,
            "total": len(transacoes),
        }

    def obter_despesas_por_categoria(self) -> list:
        """Retorna as despesas agrupadas por categoria."""
        return self.transacao_repo.despesas_por_categoria(usuario_id=self.usuario_id)

    def obter_receitas_vs_despesas(self, meses: int = 6) -> list:
        """Retorna receitas vs despesas dos últimos N meses."""
        transacoes = self._buscar_transacoes()

        # Agrupa por mês
        por_mes = {}
        for t in transacoes:
            data_str = t.get("data", "")
            if not data_str or len(data_str) < 7:
                continue
            ano_mes = data_str[:7]

            if ano_mes not in por_mes:
                por_mes[ano_mes] = {"mes": ano_mes, "receitas": 0.0, "despesas": 0.0}

            if t.get("tipo") == "receita":
                por_mes[ano_mes]["receitas"] += t.get("valor", 0.0)
            elif t.get("tipo") == "despesa":
                por_mes[ano_mes]["despesas"] += t.get("valor", 0.0)

        # Pega os últimos N meses (meses com ou sem dados)
        hoje = datetime.now()
        resultado = []
        for i in range(meses - 1, -1, -1):
            data_ref = hoje - timedelta(days=i * 30)
            ano_mes = data_ref.strftime("%Y-%m")
            if ano_mes in por_mes:
                resultado.append(por_mes[ano_mes])
            else:
                resultado.append({"mes": ano_mes, "receitas": 0.0, "despesas": 0.0})

        return resultado

    def obter_detalhes_media_mensal(self) -> dict:
        """Retorna a média mensal de despesas."""
        transacoes = self._buscar_transacoes()

        meses_com_dados = set()
        total_despesas = 0.0

        for t in transacoes:
            if t.get("tipo") == "despesa":
                total_despesas += t.get("valor", 0.0)
                data_str = t.get("data", "")
                if data_str and len(data_str) >= 7:
                    meses_com_dados.add(data_str[:7])

        meses = len(meses_com_dados) or 1
        media = total_despesas / meses

        return {"media": media, "meses_com_dados": len(meses_com_dados)}

    def obter_categoria_que_mais_gastou(self) -> dict:
        """Retorna a categoria que o usuário mais gastou no mês atual."""
        return self.transacao_repo.categoria_que_mais_gastou_mes_atual(usuario_id=self.usuario_id)

    def obter_maior_despesa_mes(self) -> dict:
        """Retorna a maior despesa do mês atual."""
        return self.transacao_repo.maior_despesa_mes_atual(usuario_id=self.usuario_id)

    def obter_comparativo_mes_anterior(self) -> dict:
        """Compara despesas do mês atual com o mês anterior."""
        transacoes = self._buscar_transacoes()

        hoje = date.today()
        mes_atual_str = hoje.strftime("%Y-%m")

        # Mês anterior
        if hoje.month == 1:
            mes_anterior_str = f"{hoje.year - 1}-12"
        else:
            mes_anterior_str = f"{hoje.year}-{hoje.month - 1:02d}"

        mes_atual = 0.0
        mes_anterior = 0.0

        for t in transacoes:
            if t.get("tipo") != "despesa":
                continue
            data_str = t.get("data", "")
            if data_str.startswith(mes_atual_str):
                mes_atual += t.get("valor", 0.0)
            elif data_str.startswith(mes_anterior_str):
                mes_anterior += t.get("valor", 0.0)

        if mes_anterior == 0:
            variacao = 0 if mes_atual == 0 else 100
        else:
            variacao = ((mes_atual - mes_anterior) / mes_anterior) * 100

        return {"mes_atual": mes_atual, "mes_anterior": mes_anterior, "variacao": variacao}

    def obter_projecao_mes(self) -> dict:
        """Retorna a projeção do mês baseada nas contas previstas."""
        contas = self.conta_repo.listar_como_dict(usuario_id=self.usuario_id, apenas_ativas=True)

        receitas = 0.0
        despesas = 0.0
        total_contas = len(contas)

        for c in contas:
            if c.get("tipo") == "receita":
                receitas += c.get("valor", 0.0)
            elif c.get("tipo") == "despesa":
                despesas += c.get("valor", 0.0)

        return {
            "saldo_previsto": receitas - despesas,
            "total_contas": total_contas,
            "tem_contas": total_contas > 0,
        }

    def obter_resumo_contas_previstas(self) -> dict:
        """Retorna o resumo de contas previstas do usuário."""
        contas = self.conta_repo.listar_como_dict(usuario_id=self.usuario_id, apenas_ativas=True)

        receitas = 0.0
        despesas = 0.0
        total_contas = len(contas)

        for c in contas:
            if c.get("tipo") == "receita":
                receitas += c.get("valor", 0.0)
            elif c.get("tipo") == "despesa":
                despesas += c.get("valor", 0.0)

        print(f"📊 Resumo Contas Previstas (usuário {self.usuario_id}):")
        print(f"   Receitas: R$ {receitas:.2f}")
        print(f"   Despesas: R$ {despesas:.2f}")
        print(f"   Saldo: R$ {receitas - despesas:.2f}")
        print(f"   Total de contas: {total_contas}")

        return {
            "receitas": receitas,
            "despesas": despesas,
            "saldo": receitas - despesas,
            "total_contas": total_contas,
            "tem_contas": total_contas > 0,
        }

    def obter_saldo_atual(self) -> float:
        """Retorna o saldo atual do usuário (receitas - despesas)."""
        transacoes = self._buscar_transacoes()
        saldo = self._calcular_saldo(transacoes)["saldo"]
        print(f"💰 Saldo atual do usuário {self.usuario_id}: R$ {saldo:.2f}")
        return saldo

    def obter_media_mensal_com_saldo(self) -> dict:
        """Calcula a média mensal considerando o saldo atual."""
        transacoes = self._buscar_transacoes()

        meses_com_dados = set()
        for t in transacoes:
            data_str = t.get("data", "")
            if data_str and len(data_str) >= 7:
                meses_com_dados.add(data_str[:7])

        meses = len(meses_com_dados) or 1
        calculo = self._calcular_saldo(transacoes)

        media = calculo["saldo"] / meses
        print(f"📊 Média mensal (com saldo): R$ {media:.2f} "
              f"(saldo R$ {calculo['saldo']:.2f} / {meses} meses)")

        return {
            "media": media,
            "saldo": calculo["saldo"],
            "meses_com_dados": len(meses_com_dados),
            "receitas": calculo["receitas"],
            "despesas": calculo["despesas"],
        }

    def obter_progresso_meta_com_saldo(self, meta_id: str) -> dict:
        """Calcula o progresso de uma meta considerando o saldo atual."""
        # Busca a meta
        meta_doc = self.db.collection("metas").document(str(meta_id)).get()
        if not meta_doc.exists:
            return {"valor_atual": 0, "percentual": 0}

        meta = meta_doc.to_dict()
        valor_alvo = meta.get("valor_alvo", 0.0)
        tipo = meta.get("tipo", "")
        categoria_id = meta.get("categoria_id")

        # Busca transações
        transacoes = self._buscar_transacoes()
        calculo_geral = self._calcular_saldo(transacoes)
        saldo_geral = calculo_geral["saldo"]

        # Se a meta tem categoria, calcula apenas daquela categoria
        if categoria_id:
            transacoes_cat = [t for t in transacoes if t.get("categoria_id") == categoria_id]
            calculo_cat = self._calcular_saldo(transacoes_cat)
            valor_categoria = calculo_cat["saldo"]
        else:
            valor_categoria = saldo_geral

        # Calcula valor atual baseado no tipo de meta
        if tipo == "economia":
            valor_atual = max(0, saldo_geral)
        elif tipo == "investimento":
            valor_atual = max(0, valor_categoria if categoria_id else saldo_geral)
        elif tipo == "compra":
            # Para compra, considera apenas despesas
            if categoria_id:
                transacoes_cat_despesas = [
                    t for t in transacoes
                    if t.get("categoria_id") == categoria_id and t.get("tipo") == "despesa"
                ]
                valor_atual = sum(t.get("valor", 0.0) for t in transacoes_cat_despesas)
            else:
                valor_atual = sum(
                    t.get("valor", 0.0) for t in transacoes
                    if t.get("tipo") == "despesa"
                )
        else:
            valor_atual = 0

        percentual = min(100, (valor_atual / valor_alvo) * 100) if valor_alvo > 0 else 0
        print(f"🎯 Progresso meta {meta_id}: R$ {valor_atual:.2f} / R$ {valor_alvo:.2f} ({percentual:.1f}%)")

        return {
            "valor_atual": valor_atual,
            "percentual": percentual,
            "saldo_geral": saldo_geral,
        }

    def obter_projecao_mes_com_saldo(self) -> dict:
        """Calcula a projeção do mês considerando o saldo atual."""
        # Saldo atual
        saldo_atual = self.obter_saldo_atual()

        # Contas previstas
        contas = self.conta_repo.listar_como_dict(usuario_id=self.usuario_id, apenas_ativas=True)

        receitas_previstas = 0.0
        despesas_previstas = 0.0
        total_contas = len(contas)

        for c in contas:
            if c.get("tipo") == "receita":
                receitas_previstas += c.get("valor", 0.0)
            elif c.get("tipo") == "despesa":
                despesas_previstas += c.get("valor", 0.0)

        saldo_previsto = saldo_atual + receitas_previstas - despesas_previstas
        print(
            f"📈 Projeção: Saldo atual R$ {saldo_atual:.2f}, "
            f"Previstas R$ {receitas_previstas - despesas_previstas:.2f}"
        )

        return {
            "saldo_atual": saldo_atual,
            "receitas_previstas": receitas_previstas,
            "despesas_previstas": despesas_previstas,
            "saldo_previsto": saldo_previsto,
            "total_contas": total_contas,
            "tem_contas": total_contas > 0,
        }
