# views/dashboard_view.py
import flet as ft
import flet_charts as fch
from services.finance_service import FinanceService
from datetime import datetime

CORES_CATEGORIA = [
    ft.Colors.BLUE_700, ft.Colors.RED_700, ft.Colors.GREEN_700, ft.Colors.AMBER_700,
    ft.Colors.PURPLE_700, ft.Colors.TEAL_700, ft.Colors.ORANGE_700, ft.Colors.PINK_700,
    ft.Colors.INDIGO_700, ft.Colors.CYAN_700
]
COR_RECEITA_NORMAL = ft.Colors.GREEN_700
COR_RECEITA_HOVER = ft.Colors.GREEN_400
COR_DESPESA_NORMAL = ft.Colors.RED_700
COR_DESPESA_HOVER = ft.Colors.RED_400


class DashboardView(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.root_page = page
        self.expand = True
        self.spacing = 15
        self.scroll = ft.ScrollMode.AUTO
        self.chart_barras = None

        # ✅ CRÍTICO: Obtém o usuario_id da página
        usuario_id = None
        if hasattr(page, 'usuario_logado') and page.usuario_logado:
            usuario_id = page.usuario_logado.id
            print(f"📊 Dashboard: Usuário logado ID = {usuario_id}")
        else:
            print("⚠️ Dashboard: NENHUM usuário logado encontrado!")

        # ✅ Cria o service COM o usuario_id
        self.service = FinanceService(usuario_id=usuario_id)

        self._build_ui()
        self.carregar_resumo()

    def _build_ui(self):
        # Cards principais
        self.card_receitas = self._criar_card("Receitas", "R$ 0,00", ft.Colors.GREEN_700, ft.Icons.ARROW_UPWARD)
        self.card_despesas = self._criar_card("Despesas", "R$ 0,00", ft.Colors.RED_700, ft.Icons.ARROW_DOWNWARD)
        self.card_saldo = self._criar_card("Saldo", "R$ 0,00", ft.Colors.PRIMARY, ft.Icons.ACCOUNT_BALANCE)

        # Cards de especificações
        self.card_media = self._criar_card_especificacao("Média Mensal", "R$ 0,00", ft.Colors.TEAL_700,
                                                         ft.Icons.TRENDING_UP, "últimos 6 meses")
        self.card_top_categoria = self._criar_card_especificacao("Mais Gasto", "-", ft.Colors.PURPLE_700,
                                                                 ft.Icons.SHOPPING_CART, "categoria do mês")
        self.card_maior_despesa = self._criar_card_especificacao("Maior Despesa", "-", ft.Colors.ORANGE_700,
                                                                 ft.Icons.WARNING_AMBER, "do mês atual")
        self.card_comparativo = self._criar_card_especificacao("vs Mês Anterior", "0%", ft.Colors.INDIGO_700,
                                                               ft.Icons.COMPARE_ARROWS, "variação")
        self.card_projecao = self._criar_card_especificacao("Projeção do Mês", "R$ 0,00", ft.Colors.CYAN_700,
                                                            ft.Icons.ACCOUNT_BALANCE_WALLET, "saldo previsto")

        self.txt_total = ft.Text("Total de Transações: 0", size=14, weight=ft.FontWeight.W_500)

        self.container_pizza = ft.Container(
            expand=True, padding=20, border=ft.Border.all(1, ft.Colors.OUTLINE),
            border_radius=12, bgcolor=ft.Colors.SURFACE_CONTAINER_LOWEST,
            content=ft.Column([ft.Text("Carregando...")])
        )
        self.container_barras = ft.Container(
            expand=True, padding=20, border=ft.Border.all(1, ft.Colors.OUTLINE),
            border_radius=12, bgcolor=ft.Colors.SURFACE_CONTAINER_LOWEST,
            content=ft.Column([ft.Text("Carregando...")])
        )

        self.controls = [
            ft.Text("Resumo Financeiro", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.PRIMARY),

            ft.Row(controls=[self.card_receitas, self.card_despesas, self.card_saldo],
                   alignment=ft.MainAxisAlignment.SPACE_AROUND, spacing=15, wrap=True),

            self.txt_total,
            ft.Divider(),

            ft.Text("Análise Rápida", size=18, weight=ft.FontWeight.BOLD),
            ft.Row(controls=[self.card_media, self.card_top_categoria, self.card_maior_despesa,
                             self.card_comparativo, self.card_projecao],
                   alignment=ft.MainAxisAlignment.SPACE_AROUND, spacing=15, wrap=True),

            ft.Divider(),
            ft.Text("Despesas por Categoria", size=18, weight=ft.FontWeight.BOLD),
            self.container_pizza,
            ft.Text("Receitas vs Despesas (últimos 6 meses)", size=18, weight=ft.FontWeight.BOLD),
            self.container_barras,
        ]

    def _criar_card(self, titulo: str, valor: str, cor: str, icone: str) -> ft.Container:
        return ft.Container(
            content=ft.Column([
                ft.Icon(icone, size=36, color=cor),
                ft.Text(titulo, size=13, color=ft.Colors.ON_SURFACE_VARIANT),
                ft.Text(valor, size=22, weight=ft.FontWeight.BOLD, color=cor)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
            width=180, padding=15, border=ft.Border.all(1, ft.Colors.OUTLINE),
            border_radius=12, bgcolor=ft.Colors.SURFACE_CONTAINER_LOWEST
        )

    def _criar_card_especificacao(self, titulo: str, valor: str, cor: str, icone: str, subtitulo: str) -> ft.Container:
        return ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(icone, size=22, color=cor), ft.Text(titulo, size=12, weight=ft.FontWeight.BOLD)],
                       spacing=6),
                ft.Text(valor, size=18, weight=ft.FontWeight.BOLD, color=cor),
                ft.Text(subtitulo, size=10, color=ft.Colors.ON_SURFACE_VARIANT)
            ], spacing=4),
            width=180, padding=12, border=ft.Border.all(1, ft.Colors.OUTLINE),
            border_radius=10, bgcolor=ft.Colors.SURFACE_CONTAINER_LOWEST
        )

    def _formatar_valor(self, valor: float) -> str:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def _formatar_valor_eixo(self, valor: float) -> str:
        if valor >= 1000000:
            return f"{valor / 1000000:.1f}M"
        elif valor >= 1000:
            return f"{valor / 1000:.1f}k"
        else:
            return f"{valor:.0f}"

    def _formatar_valor_real(self, valor: float) -> str:
        return self._formatar_valor(valor)

    def _construir_grafico_pizza(self, dados: list) -> ft.Control:
        if not dados:
            return ft.Column([
                ft.Icon(ft.Icons.PIE_CHART_OUTLINE, size=60, color=ft.Colors.ON_SURFACE_VARIANT),
                ft.Text("Nenhuma despesa registrada.", color=ft.Colors.ON_SURFACE_VARIANT)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)

        total = sum(d["total"] for d in dados)
        secoes = []
        legenda_items = []

        for i, d in enumerate(dados):
            porcentagem = (d["total"] / total) * 100
            cor = CORES_CATEGORIA[i % len(CORES_CATEGORIA)]
            secoes.append(fch.PieChartSection(
                value=d["total"], color=cor, radius=80,
                title=f"{porcentagem:.1f}%",
                title_style=ft.TextStyle(size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
            ))
            legenda_items.append(ft.Row([
                ft.Container(width=16, height=16, bgcolor=cor, border_radius=4),
                ft.Text(f"{d['nome']}: {self._formatar_valor(d['total'])}", size=13)
            ], spacing=8))

        return ft.Row(controls=[
            fch.PieChart(sections=secoes, sections_space=2, center_space_radius=40, expand=True, height=250),
            ft.Column(controls=legenda_items, spacing=8, width=220)
        ], alignment=ft.MainAxisAlignment.SPACE_AROUND, vertical_alignment=ft.CrossAxisAlignment.CENTER)

    def _construir_grafico_barras(self, dados: list) -> ft.Control:
        if not dados:
            return ft.Column([
                ft.Icon(ft.Icons.BAR_CHART, size=60, color=ft.Colors.ON_SURFACE_VARIANT),
                ft.Text("Nenhum dado registrado.", color=ft.Colors.ON_SURFACE_VARIANT)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)

        max_valor = max((max(d["receitas"], d["despesas"]) for d in dados), default=100)
        max_y = max_valor * 1.25 if max_valor > 0 else 100

        left_labels = []
        for i in range(6):
            valor = (max_y / 5) * i
            left_labels.append(fch.ChartAxisLabel(
                value=valor,
                label=ft.Text(self._formatar_valor_eixo(valor), size=11, color=ft.Colors.ON_SURFACE_VARIANT)
            ))

        grupos = []
        bottom_labels = []

        for i, d in enumerate(dados):
            try:
                ano, mes = d["mes"].split("-")
                label_mes = f"{mes}/{ano[2:]}"
            except:
                label_mes = d["mes"]

            grupos.append(fch.BarChartGroup(x=i, rods=[
                fch.BarChartRod(
                    from_y=0, to_y=d["receitas"], color=COR_RECEITA_NORMAL, width=20,
                    border_radius=ft.BorderRadius(top_left=6, top_right=6, bottom_left=0, bottom_right=0),
                    tooltip=fch.BarChartRodTooltip(self._formatar_valor_real(d["receitas"]))
                ),
                fch.BarChartRod(
                    from_y=0, to_y=d["despesas"], color=COR_DESPESA_NORMAL, width=20,
                    border_radius=ft.BorderRadius(top_left=6, top_right=6, bottom_left=0, bottom_right=0),
                    tooltip=fch.BarChartRodTooltip(self._formatar_valor_real(d["despesas"]))
                )
            ]))
            bottom_labels.append(fch.ChartAxisLabel(
                value=i, label=ft.Text(label_mes, size=12, weight=ft.FontWeight.W_500)
            ))

        self.chart_barras = fch.BarChart(
            groups=grupos, max_y=max_y,
            border=ft.Border.all(0, ft.Colors.TRANSPARENT),
            horizontal_grid_lines=fch.ChartGridLines(color=ft.Colors.OUTLINE_VARIANT, width=1, dash_pattern=[5, 5]),
            left_axis=fch.ChartAxis(labels=left_labels, label_size=50),
            bottom_axis=fch.ChartAxis(labels=bottom_labels, label_size=30),
            tooltip=fch.BarChartTooltip(bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST, border_radius=8),
            on_event=self._on_chart_event, expand=True, height=300
        )

        return ft.Column([
            self.chart_barras,
            ft.Row([
                ft.Row([
                    ft.Container(width=16, height=16, bgcolor=COR_RECEITA_NORMAL, border_radius=4),
                    ft.Text("Receitas", size=13)
                ], spacing=8),
                ft.Row([
                    ft.Container(width=16, height=16, bgcolor=COR_DESPESA_NORMAL, border_radius=4),
                    ft.Text("Despesas", size=13)
                ], spacing=8),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=30)
        ])

    def _on_chart_event(self, e: fch.BarChartEvent):
        if not self.chart_barras:
            return
        for group_index, group in enumerate(self.chart_barras.groups):
            for rod_index, rod in enumerate(group.rods):
                is_hovered = (e.group_index == group_index and e.rod_index == rod_index)
                if is_hovered:
                    rod.color = COR_RECEITA_HOVER if rod_index == 0 else COR_DESPESA_HOVER
                    rod.width = 24
                else:
                    rod.color = COR_RECEITA_NORMAL if rod_index == 0 else COR_DESPESA_NORMAL
                    rod.width = 20
        self.chart_barras.update()

    def carregar_resumo(self):
        print(f"\n🔄 Carregando resumo para usuário ID = {self.service.usuario_id}")

        resumo = self.service.obter_resumo()
        print(f"📊 Resumo: {resumo}")

        self.card_receitas.content.controls[2].value = self._formatar_valor(resumo['receitas'])
        self.card_despesas.content.controls[2].value = self._formatar_valor(resumo['despesas'])
        self.card_saldo.content.controls[2].value = self._formatar_valor(resumo['saldo'])
        cor_saldo = ft.Colors.GREEN_700 if resumo['saldo'] >= 0 else ft.Colors.RED_700
        self.card_saldo.content.controls[2].color = cor_saldo
        self.txt_total.value = f"Total de Transações: {resumo['total']}"

        # ✅ MÉDIA MENSAL COM SALDO ATUAL
        detalhes_media = self.service.obter_media_mensal_com_saldo()
        self.card_media.content.controls[1].value = self._formatar_valor(detalhes_media['media'])
        self.card_media.content.controls[2].value = f"Saldo: {self._formatar_valor(detalhes_media['saldo'])}"

        # ... resto do código continua igual ...
        top_cat = self.service.obter_categoria_que_mais_gastou()
        if top_cat:
            self.card_top_categoria.content.controls[1].value = top_cat["nome"]
            self.card_top_categoria.content.controls[2].value = self._formatar_valor(top_cat["total"])
        else:
            self.card_top_categoria.content.controls[1].value = "-"
            self.card_top_categoria.content.controls[2].value = "sem despesas no mês"

        maior = self.service.obter_maior_despesa_mes()
        if maior:
            desc = maior["descricao"]
            if len(desc) > 20:
                desc = desc[:17] + "..."
            self.card_maior_despesa.content.controls[1].value = self._formatar_valor(maior["valor"])
            self.card_maior_despesa.content.controls[2].value = desc
        else:
            self.card_maior_despesa.content.controls[1].value = "-"
            self.card_maior_despesa.content.controls[2].value = "sem despesas no mês"

        comp = self.service.obter_comparativo_mes_anterior()
        variacao = comp["variacao"]
        if variacao > 0:
            texto_comp = f"+{variacao:.1f}%"
            cor_comp = ft.Colors.RED_700
            icone_comp = ft.Icons.ARROW_UPWARD
        elif variacao < 0:
            texto_comp = f"{variacao:.1f}%"
            cor_comp = ft.Colors.GREEN_700
            icone_comp = ft.Icons.ARROW_DOWNWARD
        else:
            texto_comp = "0%"
            cor_comp = ft.Colors.ON_SURFACE_VARIANT
            icone_comp = ft.Icons.REMOVE

        self.card_comparativo.content.controls[0].controls[0] = ft.Icon(icone_comp, size=22, color=cor_comp)
        self.card_comparativo.content.controls[1].value = texto_comp
        self.card_comparativo.content.controls[1].color = cor_comp

        projecao = self.service.obter_projecao_mes()
        if projecao['tem_contas']:
            self.card_projecao.content.controls[1].value = self._formatar_valor(projecao['saldo_previsto'])
            cor_projecao = ft.Colors.GREEN_700 if projecao['saldo_previsto'] >= 0 else ft.Colors.RED_700
            self.card_projecao.content.controls[1].color = cor_projecao
            self.card_projecao.content.controls[2].value = f"{projecao['total_contas']} contas ativas"
        else:
            self.card_projecao.content.controls[1].value = "-"
            self.card_projecao.content.controls[1].color = ft.Colors.ON_SURFACE_VARIANT
            self.card_projecao.content.controls[2].value = "cadastre contas previstas"

        self.container_pizza.content = self._construir_grafico_pizza(self.service.obter_despesas_por_categoria())
        self.container_barras.content = self._construir_grafico_barras(self.service.obter_receitas_vs_despesas(6))

        self.root_page.update()