from database.connection import get_connection
from models.entities import Transacao, Categoria, Meta, ContaPrevista
from datetime import datetime, date


class TransacaoRepository:
    def salvar(self, transacao: Transacao) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO transacoes (descricao, valor, tipo, data, categoria_id) VALUES (?, ?, ?, ?, ?)",
            (transacao.descricao, transacao.valor, transacao.tipo,
             transacao.data.isoformat(), transacao.categoria_id)
        )
        conn.commit()
        novo_id = cursor.lastrowid
        conn.close()
        return novo_id

    def listar_todas(self) -> list[Transacao]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transacoes ORDER BY data DESC")
        rows = cursor.fetchall()
        conn.close()
        return [
            Transacao(id=row['id'], descricao=row['descricao'], valor=row['valor'],
                      tipo=row['tipo'], data=datetime.fromisoformat(row['data']).date(),
                      categoria_id=row['categoria_id'])
            for row in rows
        ]

    def atualizar(self, transacao: Transacao) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE transacoes SET descricao=?, valor=?, tipo=?, data=?, categoria_id=? WHERE id=?",
            (transacao.descricao, transacao.valor, transacao.tipo,
             transacao.data.isoformat(), transacao.categoria_id, transacao.id)
        )
        conn.commit()
        conn.close()

    def deletar(self, id: int) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transacoes WHERE id=?", (id,))
        conn.commit()
        conn.close()

    def despesas_por_categoria(self) -> list[dict]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.nome, c.icone, SUM(t.valor) as total
            FROM transacoes t LEFT JOIN categorias c ON t.categoria_id = c.id
            WHERE t.tipo = 'despesa'
            GROUP BY t.categoria_id ORDER BY total DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        return [{"nome": row["nome"] or "Sem categoria", "icone": row["icone"] or "HELP", "total": row["total"]} for row in rows]

    def receitas_vs_despesas_por_mes(self, limite_meses: int = 6) -> list[dict]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT strftime('%Y-%m', data) as mes,
                   SUM(CASE WHEN tipo = 'receita' THEN valor ELSE 0 END) as receitas,
                   SUM(CASE WHEN tipo = 'despesa' THEN valor ELSE 0 END) as despesas
            FROM transacoes GROUP BY mes ORDER BY mes DESC LIMIT ?
        ''', (limite_meses,))
        rows = cursor.fetchall()
        conn.close()
        resultado = [{"mes": row["mes"], "receitas": row["receitas"], "despesas": row["despesas"]} for row in rows]
        resultado.reverse()
        return resultado

    def media_mensal_despesas(self, meses: int = 6) -> float:
        hoje = date.today()
        total_despesas = 0.0
        for i in range(meses):
            mes = hoje.month - i
            ano = hoje.year
            while mes <= 0:
                mes += 12
                ano -= 1
            ano_mes = f"{ano}-{mes:02d}"
            total_mes = self.total_despesas_mes(ano_mes)
            total_despesas += total_mes
        return total_despesas / meses if meses > 0 else 0.0

    def categoria_que_mais_gastou_mes_atual(self) -> dict | None:
        hoje = date.today()
        inicio_mes = hoje.replace(day=1).isoformat()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.nome, SUM(t.valor) as total
            FROM transacoes t LEFT JOIN categorias c ON t.categoria_id = c.id
            WHERE t.tipo = 'despesa' AND t.data >= ?
            GROUP BY t.categoria_id ORDER BY total DESC LIMIT 1
        ''', (inicio_mes,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {"nome": row["nome"] or "Sem categoria", "total": row["total"]}
        return None

    def maior_despesa_mes_atual(self) -> dict | None:
        hoje = date.today()
        inicio_mes = hoje.replace(day=1).isoformat()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT descricao, valor, data FROM transacoes
            WHERE tipo = 'despesa' AND data >= ?
            ORDER BY valor DESC LIMIT 1
        ''', (inicio_mes,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {"descricao": row["descricao"], "valor": row["valor"], "data": row["data"]}
        return None

    def total_despesas_mes(self, ano_mes: str) -> float:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COALESCE(SUM(valor), 0) as total FROM transacoes
            WHERE tipo = 'despesa' AND strftime('%Y-%m', data) = ?
        ''', (ano_mes,))
        row = cursor.fetchone()
        conn.close()
        return row["total"]


class CategoriaRepository:
    def listar_todas(self) -> list[Categoria]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM categorias ORDER BY nome")
        rows = cursor.fetchall()
        conn.close()
        return [Categoria(id=row['id'], nome=row['nome'], icone=row['icone']) for row in rows]


class MetaRepository:
    def salvar(self, meta: Meta) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        data_limite = meta.data_limite.isoformat() if meta.data_limite else None
        cursor.execute(
            "INSERT INTO metas (nome, tipo, valor_alvo, categoria_id, data_limite, ativa) VALUES (?, ?, ?, ?, ?, ?)",
            (meta.nome, meta.tipo, meta.valor_alvo, meta.categoria_id, data_limite, int(meta.ativa))
        )
        conn.commit()
        novo_id = cursor.lastrowid
        conn.close()
        return novo_id

    def listar_todas(self) -> list[Meta]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM metas ORDER BY ativa DESC, nome")
        rows = cursor.fetchall()
        conn.close()
        return [
            Meta(
                id=row['id'], nome=row['nome'], tipo=row['tipo'],
                valor_alvo=row['valor_alvo'], categoria_id=row['categoria_id'],
                data_limite=datetime.fromisoformat(row['data_limite']).date() if row['data_limite'] else None,
                ativa=bool(row['ativa'])
            ) for row in rows
        ]

    def atualizar(self, meta: Meta) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        data_limite = meta.data_limite.isoformat() if meta.data_limite else None
        cursor.execute(
            "UPDATE metas SET nome=?, tipo=?, valor_alvo=?, categoria_id=?, data_limite=?, ativa=? WHERE id=?",
            (meta.nome, meta.tipo, meta.valor_alvo, meta.categoria_id, data_limite, int(meta.ativa), meta.id)
        )
        conn.commit()
        conn.close()

    def deletar(self, id: int) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM metas WHERE id=?", (id,))
        conn.commit()
        conn.close()


class ContaPrevistaRepository:
    def salvar(self, conta: ContaPrevista) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO contas_previstas (nome, valor, tipo, dia_vencimento, categoria_id, ativa) VALUES (?, ?, ?, ?, ?, ?)",
            (conta.nome, conta.valor, conta.tipo, conta.dia_vencimento, conta.categoria_id, int(conta.ativa))
        )
        conn.commit()
        novo_id = cursor.lastrowid
        conn.close()
        return novo_id

    def listar_todas(self) -> list[ContaPrevista]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contas_previstas ORDER BY dia_vencimento")
        rows = cursor.fetchall()
        conn.close()
        return [
            ContaPrevista(
                id=row['id'], nome=row['nome'], valor=row['valor'],
                tipo=row['tipo'], dia_vencimento=row['dia_vencimento'],
                categoria_id=row['categoria_id'], ativa=bool(row['ativa'])
            ) for row in rows
        ]

    def atualizar(self, conta: ContaPrevista) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE contas_previstas SET nome=?, valor=?, tipo=?, dia_vencimento=?, categoria_id=?, ativa=? WHERE id=?",
            (conta.nome, conta.valor, conta.tipo, conta.dia_vencimento, conta.categoria_id, int(conta.ativa), conta.id)
        )
        conn.commit()
        conn.close()

    def deletar(self, id: int) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM contas_previstas WHERE id=?", (id,))
        conn.commit()
        conn.close()