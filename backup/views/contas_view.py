# views/contas_view.py
import flet as ft
from services.finance_service import FinanceService


class ContasView(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.root_page = page
        self.expand = True
        self.spacing = 15
        self.scroll = ft.ScrollMode.AUTO

        usuario_id = None
        if hasattr(page, 'usuario_logado') and page.usuario_logado:
            usuario_id = page.usuario_logado.id
            print(f"💳 ContasView: Usuário ID = {usuario_id}")

        self.service = FinanceService(usuario_id=usuario_id)

        self._build_ui()
        self.carregar_contas()

    def _build_ui(self):
        self.campo_nome = ft.TextField(
            label="Nome da Conta", width=300,
            prefix_icon=ft.Icons.RECEIPT,
            border=ft.InputBorder.UNDERLINE
        )

        self.campo_valor = ft.TextField(
            label="Valor (R$)", width=150,
            prefix_icon=ft.Icons.ATTACH_MONEY,
            border=ft.InputBorder.UNDERLINE,
            keyboard_type=ft.KeyboardType.NUMBER
        )

        self.campo_dia_vencimento = ft.TextField(
            label="Dia Vencimento (1-31)", width=150,
            prefix_icon=ft.Icons.CALENDAR_MONTH,
            border=ft.InputBorder.UNDERLINE,
            keyboard_type=ft.KeyboardType.NUMBER
        )

        self.dropdown_tipo = ft.Dropdown(
            label="Tipo", width=150,
            options=[
                ft.dropdown.Option(key="despesa", text="Despesa"),
                ft.dropdown.Option(key="receita", text="Receita"),
            ],
            value="despesa"
        )

        self.dropdown_categoria = ft.Dropdown(
            label="Categoria (opcional)", width=200,
            options=self._carregar_opcoes_categorias(),
            border=ft.InputBorder.UNDERLINE
        )

        self.lista_contas = ft.Column(spacing=10)
        self.container_resumo = ft.Container()

        self.controls = [
            ft.Text("Contas Previstas", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.PRIMARY),

            ft.Container(
                content=ft.Column([
                    ft.Text("Nova Conta Prevista", size=16, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        self.campo_nome,
                        self.campo_valor,
                        self.campo_dia_vencimento,
                    ], spacing=10, wrap=True),
                    ft.Row([
                        self.dropdown_tipo,
                        self.dropdown_categoria,
                    ], spacing=10, wrap=True),
                    ft.Row([
                        ft.FilledButton(
                            "Adicionar Conta",
                            icon=ft.Icons.ADD_CIRCLE,
                            on_click=self._salvar_conta,
                            bgcolor=ft.Colors.PRIMARY,
                            color=ft.Colors.ON_PRIMARY
                        ),
                        ft.TextButton("Limpar", on_click=self._limpar_formulario),
                    ], spacing=10),
                ], spacing=10),
                padding=20,
                border=ft.Border.all(1, ft.Colors.OUTLINE),
                border_radius=12,
                bgcolor=ft.Colors.SURFACE_CONTAINER_LOWEST,
            ),

            ft.Divider(),

            # ✅ PROJEÇÃO MENSAL (versão simples)
            self.container_resumo,

            ft.Text("Contas Ativas", size=18, weight=ft.FontWeight.BOLD),
            self.lista_contas,
        ]

    def _carregar_opcoes_categorias(self) -> list:
        categorias = self.service.listar_categorias()
        options = [ft.dropdown.Option(key="", text="Nenhuma")]
        for cat in categorias:
            options.append(ft.dropdown.Option(key=str(cat["id"]), text=cat["nome"]))
        return options

    def _salvar_conta(self, e):
        nome = self.campo_nome.value
        valor_texto = self.campo_valor.value
        dia_texto = self.campo_dia_vencimento.value
        tipo = self.dropdown_tipo.value
        categoria_id_texto = self.dropdown_categoria.value

        if not nome:
            self._mostrar_erro("Preencha o nome da conta")
            return

        try:
            valor = float(valor_texto.replace(",", "."))
        except:
            self._mostrar_erro("Valor inválido")
            return

        if valor <= 0:
            self._mostrar_erro("O valor deve ser maior que zero")
            return

        try:
            dia_vencimento = int(dia_texto)
            if dia_vencimento < 1 or dia_vencimento > 31:
                raise ValueError
        except:
            self._mostrar_erro("Dia de vencimento inválido (use 1-31)")
            return

        categoria_id = None
        if categoria_id_texto and categoria_id_texto != "":
            try:
                categoria_id = int(categoria_id_texto)
            except:
                categoria_id = None

        tipo_final = "despesa" if tipo == "despesa" else "receita"

        self.service.criar_conta_prevista(nome, valor, tipo_final, dia_vencimento, categoria_id)

        self._mostrar_sucesso("Conta prevista adicionada!")
        self._limpar_formulario(e)
        self.carregar_contas()

    def _limpar_formulario(self, e):
        self.campo_nome.value = ""
        self.campo_valor.value = ""
        self.campo_dia_vencimento.value = ""
        self.dropdown_tipo.value = "despesa"
        self.dropdown_categoria.value = ""
        self.root_page.update()

    def _excluir_conta(self, id: int):
        self.service.excluir_conta_prevista(id)
        self._mostrar_sucesso("Conta excluída!")
        self.carregar_contas()

    def carregar_contas(self):
        """Carrega a lista de contas previstas e a projeção mensal."""
        print("\n🔄 Carregando contas previstas...")

        try:
            contas = self.service.listar_contas_previstas()
            print(f"📋 {len(contas)} contas encontradas")

            # ✅ PROJEÇÃO MENSAL (versão simples e robusta)
            try:
                resumo = self.service.obter_projecao_mes_com_saldo()
                self.container_resumo.content = self._criar_card_projecao_simples(resumo)
                print(f"📊 Projeção calculada com sucesso")
            except Exception as e:
                print(f"❌ Erro ao calcular projeção: {e}")
                self.container_resumo.content = ft.Container()

            # Lista de contas
            self.lista_contas.controls.clear()

            if not contas:
                self.lista_contas.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.RECEIPT_LONG, size=60, color=ft.Colors.ON_SURFACE_VARIANT),
                            ft.Text("Nenhuma conta prevista cadastrada.",
                                    color=ft.Colors.ON_SURFACE_VARIANT, italic=True),
                        ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=10),
                        padding=40,
                        alignment=ft.Alignment.CENTER,
                    )
                )
            else:
                despesas = [c for c in contas if c["tipo"] == "despesa"]
                receitas = [c for c in contas if c["tipo"] == "receita"]

                if despesas:
                    self.lista_contas.controls.append(
                        ft.Text(f"Despesas Mensais ({len(despesas)})",
                                size=14, weight=ft.FontWeight.BOLD,
                                color=ft.Colors.RED_700)
                    )
                    for conta in despesas:
                        self.lista_contas.controls.append(self._criar_card_conta(conta, ft.Colors.RED_700))

                if receitas:
                    self.lista_contas.controls.append(ft.Container(height=10))
                    self.lista_contas.controls.append(
                        ft.Text(f"Receitas Mensais ({len(receitas)})",
                                size=14, weight=ft.FontWeight.BOLD,
                                color=ft.Colors.GREEN_700)
                    )
                    for conta in receitas:
                        self.lista_contas.controls.append(self._criar_card_conta(conta, ft.Colors.GREEN_700))

            self.root_page.update()

        except Exception as e:
            print(f"❌ ERRO ao carregar contas: {e}")
            import traceback
            traceback.print_exc()
            self._mostrar_erro(f"Erro ao carregar contas: {str(e)}")

    def _criar_card_projecao_simples(self, resumo: dict) -> ft.Container:
        """Cria um card simples com a projeção mensal."""
        saldo_atual = resumo["saldo_atual"]
        receitas_previstas = resumo["receitas_previstas"]
        despesas_previstas = resumo["despesas_previstas"]
        saldo_previsto = resumo["saldo_previsto"]
        total_contas = resumo["total_contas"]

        cor_saldo_atual = ft.Colors.GREEN_700 if saldo_atual >= 0 else ft.Colors.RED_700
        cor_saldo_previsto = ft.Colors.GREEN_700 if saldo_previsto >= 0 else ft.Colors.RED_700

        return ft.Container(
            content=ft.Column([
                # Cabeçalho
                ft.Row([
                    ft.Icon(ft.Icons.ACCOUNT_BALANCE, size=24, color=ft.Colors.PRIMARY),
                    ft.Text("Projeção Mensal", size=16, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.Text(f"{total_contas} conta(s)",
                            size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),

                ft.Container(height=10),

                # ✅ Informações em formato de lista (mais simples e robusto)
                self._criar_linha_projecao(
                    ft.Icons.ACCOUNT_BALANCE_WALLET, "Saldo Atual",
                    saldo_atual, cor_saldo_atual
                ),
                self._criar_linha_projecao(
                    ft.Icons.ARROW_UPWARD, "Receitas Previstas",
                    receitas_previstas, ft.Colors.GREEN_700
                ),
                self._criar_linha_projecao(
                    ft.Icons.ARROW_DOWNWARD, "Despesas Previstas",
                    despesas_previstas, ft.Colors.RED_700
                ),

                ft.Divider(),

                # Saldo previsto (destaque)
                ft.Row([
                    ft.Icon(ft.Icons.TRENDING_UP, size=20, color=cor_saldo_previsto),
                    ft.Text("Saldo Previsto no Final do Mês",
                            size=13, weight=ft.FontWeight.W_500,
                            color=ft.Colors.ON_SURFACE_VARIANT),
                    ft.Container(expand=True),
                    ft.Text(
                        self._formatar_valor(saldo_previsto),
                        size=18, weight=ft.FontWeight.BOLD, color=cor_saldo_previsto
                    ),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ], spacing=8),
            padding=20,
            border=ft.Border.all(1, ft.Colors.OUTLINE),
            border_radius=12,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOWEST,
            margin=ft.Margin(bottom=10),
        )

    def _criar_linha_projecao(self, icone: str, label: str, valor: float, cor: str) -> ft.Row:
        """Cria uma linha da projeção."""
        return ft.Row([
            ft.Icon(icone, size=18, color=cor),
            ft.Text(label, size=13, color=ft.Colors.ON_SURFACE_VARIANT),
            ft.Container(expand=True),
            ft.Text(
                self._formatar_valor(valor),
                size=14, weight=ft.FontWeight.BOLD, color=cor
            ),
        ], vertical_alignment=ft.CrossAxisAlignment.CENTER)

    def _criar_card_conta(self, conta: dict, cor: str) -> ft.Container:
        """Cria um card para uma conta prevista."""
        nome = conta["nome"]
        valor = conta["valor"]
        dia_vencimento = conta["dia_vencimento"]
        categoria_id = conta.get("categoria_id")

        nome_categoria = ""
        if categoria_id:
            categorias = self.service.listar_categorias()
            for cat in categorias:
                if cat["id"] == categoria_id:
                    nome_categoria = f" • {cat['nome']}"
                    break

        icone = ft.Icons.ARROW_DOWNWARD if conta["tipo"] == "despesa" else ft.Icons.ARROW_UPWARD

        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(icone, color=cor, size=28),
                    width=45, height=45, border_radius=10,
                    bgcolor=ft.Colors.with_opacity(0.1, cor),
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Column([
                    ft.Text(nome, weight=ft.FontWeight.W_500, size=14),
                    ft.Text(
                        f"Vence todo dia {dia_vencimento}{nome_categoria}",
                        size=11, color=ft.Colors.ON_SURFACE_VARIANT
                    ),
                ], spacing=2, expand=True),
                ft.Text(
                    self._formatar_valor(valor),
                    weight=ft.FontWeight.BOLD, size=16, color=cor
                ),
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_color=ft.Colors.ERROR,
                    on_click=lambda e, cid=conta["id"]: self._excluir_conta(cid),
                    tooltip="Excluir conta",
                    icon_size=18,
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=12,
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=10,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOWEST,
        )

    def _formatar_valor(self, valor: float) -> str:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def _mostrar_erro(self, mensagem: str):
        snack = ft.SnackBar(
            content=ft.Text(mensagem),
            bgcolor=ft.Colors.ERROR,
            behavior=ft.SnackBarBehavior.FLOATING,
        )
        self.root_page.overlay.append(snack)
        snack.open = True
        self.root_page.update()

    def _mostrar_sucesso(self, mensagem: str):
        snack = ft.SnackBar(
            content=ft.Text(mensagem),
            bgcolor=ft.Colors.GREEN_700,
            behavior=ft.SnackBarBehavior.FLOATING,
        )
        self.root_page.overlay.append(snack)
        snack.open = True
        self.root_page.update()