# services/finance_service.py
"""Serviço de finanças com isolamento por usuário."""
from database.connection import get_connection
from datetime import datetime, timedelta


class FinanceService:
    def __init__(self, usuario_id: int = None):
        self.usuario_id = usuario_id

    def set_usuario_id(self, usuario_id: int):
        """Define o ID do usuário logado."""
        self.usuario_id = usuario_id

    # ============================================
    # CATEGORIAS
    # ============================================

    def listar_categorias(self) -> list:
        """Lista todas as categorias (globais + do usuário)."""
        conn = get_connection()
        cursor = conn.cursor()
        # ✅ Retorna categorias globais (usuario_id IS NULL) OU do usuário logado
        cursor.execute(
            "SELECT * FROM categorias WHERE usuario_id IS NULL OR usuario_id = ? ORDER BY nome",
            (self.usuario_id,)
        )
        categorias = [dict(row) for row in cursor.fetchall()]
        conn.close()
        print(f"📋 {len(categorias)} categorias encontradas para usuário {self.usuario_id}")
        return categorias

    def criar_categoria(self, nome: str, icone: str = None) -> int:
        """Cria uma nova categoria para o usuário."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO categorias (nome, icone, usuario_id) VALUES (?, ?, ?)",
            (nome, icone, self.usuario_id)
        )
        conn.commit()
        novo_id = cursor.lastrowid
        conn.close()
        return novo_id

    # ============================================
    # TRANSAÇÕES
    # ============================================

    def listar_transacoes(self) -> list:
        """Lista todas as transações do usuário."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM transacoes WHERE usuario_id = ? ORDER BY data DESC",
            (self.usuario_id,)
        )
        transacoes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return transacoes

    def criar_transacao(self, descricao: str, valor: float, tipo: str, data: str, categoria_id: int = None) -> int:
        # ✅ Validação dupla de segurança
        if not tipo or tipo not in ["despesa", "receita"]:
            raise ValueError(f"Tipo inválido: '{tipo}'. Deve ser 'despesa' ou 'receita'")

        if self.usuario_id is None:
            raise ValueError("Não é possível criar transação sem usuario_id!")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO transacoes (descricao, valor, tipo, data, categoria_id, usuario_id) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (descricao, valor, tipo, data, categoria_id, self.usuario_id)
        )
        conn.commit()
        novo_id = cursor.lastrowid
        conn.close()
        print(f"💾 Transação {novo_id} criada: tipo='{tipo}', valor={valor}, usuario={self.usuario_id}")
        return novo_id

    def excluir_transacao(self, id: int):
        """Exclui uma transação do usuário."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM transacoes WHERE id = ? AND usuario_id = ?",
            (id, self.usuario_id)
        )
        conn.commit()
        conn.close()

    # ============================================
    # METAS
    # ============================================

    def listar_metas(self) -> list:
        """Lista todas as metas do usuário."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM metas WHERE usuario_id = ? ORDER BY nome",
            (self.usuario_id,)
        )
        metas = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return metas

    def criar_meta(self, nome: str, tipo: str, valor_alvo: float, categoria_id: int = None,
                   data_limite: str = None) -> int:
        """Cria uma nova meta."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO metas (nome, tipo, valor_alvo, categoria_id, data_limite, usuario_id) VALUES (?, ?, ?, ?, ?, ?)",
            (nome, tipo, valor_alvo, categoria_id, data_limite, self.usuario_id)
        )
        conn.commit()
        novo_id = cursor.lastrowid
        conn.close()
        return novo_id

    def excluir_meta(self, id: int):
        """Exclui uma meta do usuário."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM metas WHERE id = ? AND usuario_id = ?",
            (id, self.usuario_id)
        )
        conn.commit()
        conn.close()

    # ============================================
    # CONTAS PREVISTAS
    # ============================================

    def listar_contas_previstas(self) -> list:
        conn = get_connection()
        cursor = conn.cursor()

        print(f"🔍 Buscando contas previstas para usuário {self.usuario_id}")

        cursor.execute(
            "SELECT * FROM contas_previstas WHERE usuario_id = ? AND ativa = 1 ORDER BY dia_vencimento",
            (self.usuario_id,)
        )
        contas = [dict(row) for row in cursor.fetchall()]
        conn.close()

        print(f"📋 {len(contas)} contas encontradas")
        for c in contas:
            print(f"   • {c['nome']} - R$ {c['valor']:.2f} - tipo={c['tipo']} - ativa={c['ativa']}")

        return contas

    def criar_conta_prevista(self, nome: str, valor: float, tipo: str, dia_vencimento: int,
                             categoria_id: int = None) -> int:
        conn = get_connection()
        cursor = conn.cursor()

        print(f"💾 Criando conta prevista: {nome}, R$ {valor}, tipo={tipo}, ativa=1")

        cursor.execute(
            "INSERT INTO contas_previstas (nome, valor, tipo, dia_vencimento, categoria_id, ativa, usuario_id) "
            "VALUES (?, ?, ?, ?, ?, 1, ?)",  # ✅ ativa = 1 hardcoded
            (nome, valor, tipo, dia_vencimento, categoria_id, self.usuario_id)
        )
        conn.commit()
        novo_id = cursor.lastrowid
        conn.close()

        print(f"✅ Conta criada com ID: {novo_id}")
        return novo_id

    def excluir_conta_prevista(self, id: int):
        """Exclui uma conta prevista do usuário."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM contas_previstas WHERE id = ? AND usuario_id = ?",
            (id, self.usuario_id)
        )
        conn.commit()
        conn.close()

    # ============================================
    # RESUMO E DASHBOARD
    # ============================================

    def obter_resumo(self) -> dict:
        """Retorna o resumo financeiro do usuário."""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COALESCE(SUM(CASE WHEN tipo='receita' THEN valor ELSE 0 END), 0) as receitas, "
            "COALESCE(SUM(CASE WHEN tipo='despesa' THEN valor ELSE 0 END), 0) as despesas, "
            "COUNT(*) as total "
            "FROM transacoes WHERE usuario_id = ?",
            (self.usuario_id,)
        )
        row = cursor.fetchone()
        conn.close()

        receitas = float(row["receitas"])
        despesas = float(row["despesas"])
        return {
            "receitas": receitas,
            "despesas": despesas,
            "saldo": receitas - despesas,
            "total": row["total"]
        }

    def obter_despesas_por_categoria(self) -> list:
        """Retorna as despesas agrupadas por categoria."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT c.nome, SUM(t.valor) as total "
            "FROM transacoes t "
            "LEFT JOIN categorias c ON t.categoria_id = c.id "
            "WHERE t.tipo = 'despesa' AND t.usuario_id = ? "
            "GROUP BY c.nome ORDER BY total DESC",
            (self.usuario_id,)
        )
        dados = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return dados

    def obter_receitas_vs_despesas(self, meses: int = 6) -> list:
        """Retorna receitas vs despesas dos últimos N meses."""
        conn = get_connection()
        cursor = conn.cursor()

        dados = []
        hoje = datetime.now()

        for i in range(meses - 1, -1, -1):
            data_ref = hoje - timedelta(days=i * 30)
            ano_mes = data_ref.strftime("%Y-%m")

            cursor.execute(
                "SELECT COALESCE(SUM(CASE WHEN tipo='receita' THEN valor ELSE 0 END), 0) as receitas, "
                "COALESCE(SUM(CASE WHEN tipo='despesa' THEN valor ELSE 0 END), 0) as despesas "
                "FROM transacoes WHERE usuario_id = ? AND strftime('%Y-%m', data) = ?",
                (self.usuario_id, ano_mes)
            )
            row = cursor.fetchone()
            dados.append({
                "mes": ano_mes,
                "receitas": float(row["receitas"]),
                "despesas": float(row["despesas"])
            })

        conn.close()
        return dados

    def obter_detalhes_media_mensal(self) -> dict:
        """Retorna a média mensal de despesas."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(DISTINCT strftime('%Y-%m', data)) as meses_com_dados, "
            "COALESCE(SUM(CASE WHEN tipo='despesa' THEN valor ELSE 0 END), 0) as total_despesas "
            "FROM transacoes WHERE usuario_id = ?",
            (self.usuario_id,)
        )
        row = cursor.fetchone()
        conn.close()

        meses = row["meses_com_dados"] or 1
        media = row["total_despesas"] / meses
        return {"media": media, "meses_com_dados": meses}

    def obter_categoria_que_mais_gastou(self) -> dict:
        """Retorna a categoria que o usuário mais gastou no mês atual."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT c.nome, SUM(t.valor) as total "
            "FROM transacoes t "
            "LEFT JOIN categorias c ON t.categoria_id = c.id "
            "WHERE t.tipo = 'despesa' AND t.usuario_id = ? "
            "AND strftime('%Y-%m', t.data) = strftime('%Y-%m', 'now') "
            "GROUP BY c.nome ORDER BY total DESC LIMIT 1",
            (self.usuario_id,)
        )
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def obter_maior_despesa_mes(self) -> dict:
        """Retorna a maior despesa do mês atual."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT descricao, valor FROM transacoes "
            "WHERE tipo = 'despesa' AND usuario_id = ? "
            "AND strftime('%Y-%m', data) = strftime('%Y-%m', 'now') "
            "ORDER BY valor DESC LIMIT 1",
            (self.usuario_id,)
        )
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def obter_comparativo_mes_anterior(self) -> dict:
        """Compara despesas do mês atual com o mês anterior."""
        conn = get_connection()
        cursor = conn.cursor()

        # Despesas do mês atual
        cursor.execute(
            "SELECT COALESCE(SUM(valor), 0) as total FROM transacoes "
            "WHERE tipo = 'despesa' AND usuario_id = ? "
            "AND strftime('%Y-%m', data) = strftime('%Y-%m', 'now')",
            (self.usuario_id,)
        )
        mes_atual = cursor.fetchone()["total"]

        # Despesas do mês anterior
        cursor.execute(
            "SELECT COALESCE(SUM(valor), 0) as total FROM transacoes "
            "WHERE tipo = 'despesa' AND usuario_id = ? "
            "AND strftime('%Y-%m', data) = strftime('%Y-%m', 'now', '-1 month')",
            (self.usuario_id,)
        )
        mes_anterior = cursor.fetchone()["total"]

        conn.close()

        if mes_anterior == 0:
            variacao = 0 if mes_atual == 0 else 100
        else:
            variacao = ((mes_atual - mes_anterior) / mes_anterior) * 100

        return {"mes_atual": mes_atual, "mes_anterior": mes_anterior, "variacao": variacao}

    def obter_projecao_mes(self) -> dict:
        """Retorna a projeção do mês baseada nas contas previstas."""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COALESCE(SUM(CASE WHEN tipo='receita' THEN valor ELSE 0 END), 0) as receitas, "
            "COALESCE(SUM(CASE WHEN tipo='despesa' THEN valor ELSE 0 END), 0) as despesas, "
            "COUNT(*) as total_contas "
            "FROM contas_previstas WHERE usuario_id = ? AND ativa = 1",
            (self.usuario_id,)
        )
        row = cursor.fetchone()
        conn.close()

        receitas = float(row["receitas"])
        despesas = float(row["despesas"])
        return {
            "saldo_previsto": receitas - despesas,
            "total_contas": row["total_contas"],
            "tem_contas": row["total_contas"] > 0
        }

    def obter_resumo_contas_previstas(self) -> dict:
        """Retorna o resumo de contas previstas do usuário (receitas, despesas e saldo)."""
        conn = get_connection()
        cursor = conn.cursor()

        # Busca todas as contas previstas ativas do usuário
        cursor.execute(
            "SELECT tipo, COALESCE(SUM(valor), 0) as total, COUNT(*) as quantidade "
            "FROM contas_previstas "
            "WHERE usuario_id = ? AND ativa = 1 "
            "GROUP BY tipo",
            (self.usuario_id,)
        )

        receitas = 0.0
        despesas = 0.0
        total_contas = 0

        for row in cursor.fetchall():
            total_contas += row["quantidade"]
            if row["tipo"] == "receita":
                receitas = float(row["total"])
            elif row["tipo"] == "despesa":
                despesas = float(row["total"])

        conn.close()

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
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COALESCE(SUM(CASE WHEN tipo='receita' THEN valor ELSE 0 END), 0) as receitas, "
            "COALESCE(SUM(CASE WHEN tipo='despesa' THEN valor ELSE 0 END), 0) as despesas "
            "FROM transacoes WHERE usuario_id = ?",
            (self.usuario_id,)
        )
        row = cursor.fetchone()
        conn.close()

        saldo = float(row["receitas"]) - float(row["despesas"])
        print(f"💰 Saldo atual do usuário {self.usuario_id}: R$ {saldo:.2f}")
        return saldo

    def obter_media_mensal_com_saldo(self) -> dict:
        """Calcula a média mensal considerando o saldo atual."""
        conn = get_connection()
        cursor = conn.cursor()

        # Total de meses com transações
        cursor.execute(
            "SELECT COUNT(DISTINCT strftime('%Y-%m', data)) as meses_com_dados "
            "FROM transacoes WHERE usuario_id = ?",
            (self.usuario_id,)
        )
        meses = cursor.fetchone()["meses_com_dados"] or 1

        # Saldo atual
        cursor.execute(
            "SELECT COALESCE(SUM(CASE WHEN tipo='receita' THEN valor ELSE 0 END), 0) as receitas, "
            "COALESCE(SUM(CASE WHEN tipo='despesa' THEN valor ELSE 0 END), 0) as despesas "
            "FROM transacoes WHERE usuario_id = ?",
            (self.usuario_id,)
        )
        row = cursor.fetchone()
        conn.close()

        receitas = float(row["receitas"])
        despesas = float(row["despesas"])
        saldo = receitas - despesas

        # Média mensal do saldo
        media = saldo / meses

        print(f"📊 Média mensal (com saldo): R$ {media:.2f} (saldo R$ {saldo:.2f} / {meses} meses)")

        return {
            "media": media,
            "saldo": saldo,
            "meses_com_dados": meses,
            "receitas": receitas,
            "despesas": despesas,
        }

    def obter_progresso_meta_com_saldo(self, meta_id: int) -> dict:
        """Calcula o progresso de uma meta considerando o saldo atual."""
        conn = get_connection()
        cursor = conn.cursor()

        # Busca a meta
        cursor.execute("SELECT * FROM metas WHERE id = ? AND usuario_id = ?", (meta_id, self.usuario_id))
        meta_row = cursor.fetchone()

        if not meta_row:
            conn.close()
            return {"valor_atual": 0, "percentual": 0}

        # ✅ Converte sqlite3.Row para dict
        meta = dict(meta_row)

        valor_alvo = meta["valor_alvo"]
        tipo = meta["tipo"]
        categoria_id = meta.get("categoria_id")

        # Saldo atual (considerando todas as transações)
        cursor.execute(
            "SELECT COALESCE(SUM(CASE WHEN tipo='receita' THEN valor ELSE 0 END), 0) as receitas, "
            "COALESCE(SUM(CASE WHEN tipo='despesa' THEN valor ELSE 0 END), 0) as despesas "
            "FROM transacoes WHERE usuario_id = ?",
            (self.usuario_id,)
        )
        row = dict(cursor.fetchone())
        saldo_geral = float(row["receitas"]) - float(row["despesas"])

        # Se a meta tem categoria, calcula apenas daquela categoria
        if categoria_id:
            cursor.execute(
                "SELECT COALESCE(SUM(CASE WHEN tipo='receita' THEN valor ELSE 0 END), 0) as receitas, "
                "COALESCE(SUM(CASE WHEN tipo='despesa' THEN valor ELSE 0 END), 0) as despesas "
                "FROM transacoes WHERE usuario_id = ? AND categoria_id = ?",
                (self.usuario_id, categoria_id)
            )
            row = dict(cursor.fetchone())
            valor_categoria = float(row["receitas"]) - float(row["despesas"])
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
                cursor.execute(
                    "SELECT COALESCE(SUM(valor), 0) as total FROM transacoes "
                    "WHERE usuario_id = ? AND categoria_id = ? AND tipo = 'despesa'",
                    (self.usuario_id, categoria_id)
                )
                valor_atual = float(dict(cursor.fetchone())["total"])
            else:
                cursor.execute(
                    "SELECT COALESCE(SUM(valor), 0) as total FROM transacoes "
                    "WHERE usuario_id = ? AND tipo = 'despesa'",
                    (self.usuario_id,)
                )
                valor_atual = float(dict(cursor.fetchone())["total"])
        else:
            valor_atual = 0

        percentual = min(100, (valor_atual / valor_alvo) * 100) if valor_alvo > 0 else 0

        print(f"🎯 Progresso meta {meta_id}: R$ {valor_atual:.2f} / R$ {valor_alvo:.2f} ({percentual:.1f}%)")

        conn.close()

        return {
            "valor_atual": valor_atual,
            "percentual": percentual,
            "saldo_geral": saldo_geral,
        }
    def obter_projecao_mes_com_saldo(self) -> dict:
        """Calcula a projeção do mês considerando o saldo atual."""
        conn = get_connection()
        cursor = conn.cursor()

        # Saldo atual
        cursor.execute(
            "SELECT COALESCE(SUM(CASE WHEN tipo='receita' THEN valor ELSE 0 END), 0) as receitas, "
            "COALESCE(SUM(CASE WHEN tipo='despesa' THEN valor ELSE 0 END), 0) as despesas "
            "FROM transacoes WHERE usuario_id = ?",
            (self.usuario_id,)
        )
        row = cursor.fetchone()
        saldo_atual = float(row["receitas"]) - float(row["despesas"])

        # Contas previstas
        cursor.execute(
            "SELECT COALESCE(SUM(CASE WHEN tipo='receita' THEN valor ELSE 0 END), 0) as receitas_previstas, "
            "COALESCE(SUM(CASE WHEN tipo='despesa' THEN valor ELSE 0 END), 0) as despesas_previstas, "
            "COUNT(*) as total_contas "
            "FROM contas_previstas WHERE usuario_id = ? AND ativa = 1",
            (self.usuario_id,)
        )
        row = cursor.fetchone()
        conn.close()

        receitas_previstas = float(row["receitas_previstas"])
        despesas_previstas = float(row["despesas_previstas"])

        # Projeção = saldo atual + receitas previstas - despesas previstas
        saldo_previsto = saldo_atual + receitas_previstas - despesas_previstas

        print(
            f"📈 Projeção do mês: Saldo atual R$ {saldo_atual:.2f} + Previstas R$ {receitas_previstas - despesas_previstas:.2f} = R$ {saldo_previsto:.2f}")

        return {
            "saldo_atual": saldo_atual,
            "receitas_previstas": receitas_previstas,
            "despesas_previstas": despesas_previstas,
            "saldo_previsto": saldo_previsto,
            "total_contas": row["total_contas"],
            "tem_contas": row["total_contas"] > 0,
        }

    def obter_saldo_atual(self) -> float:
        """Retorna o saldo atual do usuário."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COALESCE(SUM(CASE WHEN tipo='receita' THEN valor ELSE 0 END), 0) as receitas, "
            "COALESCE(SUM(CASE WHEN tipo='despesa' THEN valor ELSE 0 END), 0) as despesas "
            "FROM transacoes WHERE usuario_id = ?",
            (self.usuario_id,)
        )
        row = cursor.fetchone()
        conn.close()

        saldo = float(row["receitas"]) - float(row["despesas"])
        print(f"💰 Saldo atual do usuário {self.usuario_id}: R$ {saldo:.2f}")
        return saldo

    def obter_projecao_mes_com_saldo(self) -> dict:
        """Calcula a projeção do mês considerando o saldo atual."""
        conn = get_connection()
        cursor = conn.cursor()

        # Saldo atual
        cursor.execute(
            "SELECT COALESCE(SUM(CASE WHEN tipo='receita' THEN valor ELSE 0 END), 0) as receitas, "
            "COALESCE(SUM(CASE WHEN tipo='despesa' THEN valor ELSE 0 END), 0) as despesas "
            "FROM transacoes WHERE usuario_id = ?",
            (self.usuario_id,)
        )
        row = cursor.fetchone()
        saldo_atual = float(row["receitas"]) - float(row["despesas"])

        # Contas previstas
        cursor.execute(
            "SELECT COALESCE(SUM(CASE WHEN tipo='receita' THEN valor ELSE 0 END), 0) as receitas_previstas, "
            "COALESCE(SUM(CASE WHEN tipo='despesa' THEN valor ELSE 0 END), 0) as despesas_previstas, "
            "COUNT(*) as total_contas "
            "FROM contas_previstas WHERE usuario_id = ? AND ativa = 1",
            (self.usuario_id,)
        )
        row = cursor.fetchone()
        conn.close()

        receitas_previstas = float(row["receitas_previstas"])
        despesas_previstas = float(row["despesas_previstas"])

        print(
            f"📈 Projeção: Saldo atual R$ {saldo_atual:.2f}, Previstas R$ {receitas_previstas - despesas_previstas:.2f}")

        return {
            "saldo_atual": saldo_atual,
            "receitas_previstas": receitas_previstas,
            "despesas_previstas": despesas_previstas,
            "saldo_previsto": saldo_atual + receitas_previstas - despesas_previstas,
            "total_contas": row["total_contas"],
            "tem_contas": row["total_contas"] > 0,
        }