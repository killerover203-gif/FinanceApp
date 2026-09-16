# views/transactions_view.py
import flet as ft
from services.finance_service import FinanceService
from datetime import datetime

# ✅ Lista de ícones disponíveis para categorias
ICONES_DISPONIVEIS = [
    ("RESTAURANT", "Alimentação"),
    ("DIRECTIONS_CAR", "Transporte"),
    ("HOME", "Casa"),
    ("SPORTS_ESPORTS", "Esporte"),
    ("LOCAL_HOSPITAL", "Saúde"),
    ("SCHOOL", "Educação"),
    ("WORK", "Trabalho"),
    ("TRENDING_UP", "Investimento"),
    ("SHOPPING_CART", "Compras"),
    ("FLIGHT", "Viagem"),
    ("MOVIE", "Cinema"),
    ("MUSIC_NOTE", "Música"),
    ("PET", "Pet"),
    ("CHILD_CARE", "Filhos"),
    ("FITNESS_CENTER", "Academia"),
    ("LOCAL_GAS_STATION", "Combustível"),
    ("PHONE_ANDROID", "Celular"),
    ("WIFI", "Internet"),
    ("LOCAL_ATM", "Dinheiro"),
    ("CREDIT_CARD", "Cartão"),
    ("SAVINGS", "Poupança"),
    ("ACCOUNT_BALANCE", "Banco"),
    ("GIFT", "Presente"),
    ("CELEBRATION", "Festa"),
    ("LABEL", "Outros"),
]


def _obter_icone(nome_icone: str) -> str:
    """Converte string do banco em objeto de ícone Flet."""
    if not nome_icone:
        return ft.Icons.LABEL
    try:
        return getattr(ft.Icons, nome_icone)
    except AttributeError:
        return ft.Icons.LABEL


class TransactionsView(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.root_page = page
        self.expand = True
        self.spacing = 15
        self.scroll = ft.ScrollMode.AUTO

        # Obtém o usuario_id da página
        usuario_id = None
        if hasattr(page, 'usuario_logado') and page.usuario_logado:
            usuario_id = page.usuario_logado.id

        self.service = FinanceService(usuario_id=usuario_id)
        self.categoria_selecionada = None

        self._build_ui()
        self.carregar_transacoes()

    def _build_ui(self):
        # Formulário
        self.campo_descricao = ft.TextField(
            label="Descrição", width=300,
            prefix_icon=ft.Icons.DESCRIPTION,
            border=ft.InputBorder.UNDERLINE
        )
        self.campo_valor = ft.TextField(
            label="Valor (R$)", width=150,
            prefix_icon=ft.Icons.ATTACH_MONEY,
            border=ft.InputBorder.UNDERLINE,
            keyboard_type=ft.KeyboardType.NUMBER
        )

        # Campo de data com DatePicker
        self.campo_data = ft.TextField(
            label="Data", width=150,
            prefix_icon=ft.Icons.CALENDAR_TODAY,
            border=ft.InputBorder.UNDERLINE,
            value=datetime.now().strftime("%d/%m/%Y"),
            read_only=True,
            on_click=lambda e: self._abrir_date_picker(),
        )

        # DatePicker
        self.date_picker = ft.DatePicker(
            on_change=self._data_selecionada,
            first_date=datetime(2020, 1, 1),
            last_date=datetime(2030, 12, 31),
        )
        self.root_page.overlay.append(self.date_picker)

        self.dropdown_tipo = ft.Dropdown(
            label="Tipo", width=150,
            options=[
                ft.dropdown.Option("despesa", "Despesa"),
                ft.dropdown.Option("receita", "Receita"),
            ],
            value="despesa"
        )

        # Chips de categoria
        self.container_categorias = ft.Container(
            content=ft.Row(
                controls=self._criar_chips_categorias(),
                wrap=True, spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER
            )
        )

        # Lista de transações
        self.lista_transacoes = ft.Column(spacing=8)

        self.controls = [
            ft.Text("Nova Transação", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.PRIMARY),

            ft.Row([
                self.campo_descricao,
                self.campo_valor,
                self.campo_data,
                self.dropdown_tipo,
            ], spacing=10, wrap=True),

            # ✅ Cabeçalho da seção de categorias com botão "+"
            ft.Row([
                ft.Text("Categoria:", size=13, weight=ft.FontWeight.W_500),
                ft.Container(expand=True),
                ft.TextButton(
                    "Nova categoria",
                    icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                    on_click=lambda e: self._abrir_dialog_nova_categoria(),
                    style=ft.ButtonStyle(color=ft.Colors.PRIMARY),
                ),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),

            self.container_categorias,

            ft.Row([
                ft.FilledButton(
                    "Adicionar",
                    icon=ft.Icons.ADD_CIRCLE,
                    on_click=self._salvar_transacao,
                    bgcolor=ft.Colors.PRIMARY,
                    color=ft.Colors.ON_PRIMARY
                ),
                ft.TextButton(
                    "Limpar",
                    on_click=self._limpar_formulario,
                ),
            ], spacing=10),

            ft.Divider(),

            ft.Text("Histórico de Transações", size=18, weight=ft.FontWeight.BOLD),
            self.lista_transacoes,
        ]

    # ============================================
    # DATE PICKER
    # ============================================

    def _abrir_date_picker(self):
        """Abre o DatePicker."""
        self.date_picker.open = True
        self.root_page.update()

    def _data_selecionada(self, e):
        """Callback quando uma data é selecionada."""
        if self.date_picker.value:
            data_obj = self.date_picker.value
            self.campo_data.value = data_obj.strftime("%d/%m/%Y")
            self.root_page.update()

    # ============================================
    # CATEGORIAS
    # ============================================

    def _criar_chips_categorias(self) -> list:
        """Cria os chips de categoria com ícones."""
        categorias = self.service.listar_categorias()
        chips = []

        if not categorias:
            chips.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.WARNING, size=16, color=ft.Colors.ORANGE_700),
                        ft.Text("Nenhuma categoria encontrada!", size=12, color=ft.Colors.ORANGE_700),
                    ], spacing=8),
                    padding=10,
                    bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.ORANGE_700),
                    border_radius=8,
                )
            )
            return chips

        for cat in categorias:
            nome = cat["nome"]
            nome_icone = cat.get("icone")
            icone_obj = _obter_icone(nome_icone)  # ✅ Converte string em objeto

            selected = self.categoria_selecionada == nome

            chip = ft.Chip(
                label=ft.Text(nome, size=13),
                leading=ft.Icon(icone_obj, size=16),  # ✅ Agora mostra o ícone
                selected=selected,
                on_select=lambda e, n=nome: self._selecionar_categoria(n),
            )
            chips.append(chip)

        return chips

    def _selecionar_categoria(self, nome: str):
        """Seleciona/desseleciona uma categoria."""
        if self.categoria_selecionada == nome:
            self.categoria_selecionada = None
        else:
            self.categoria_selecionada = nome

        # Atualiza os chips
        self.container_categorias.content.controls = self._criar_chips_categorias()
        self.root_page.update()

    def _abrir_dialog_nova_categoria(self):
        """Abre o dialog para criar nova categoria."""
        # Campo de nome
        campo_nome_cat = ft.TextField(
            label="Nome da categoria",
            prefix_icon=ft.Icons.LABEL,
            border=ft.InputBorder.UNDERLINE,
            autofocus=True,
        )

        # Dropdown de ícones
        opcoes_icones = [
            ft.dropdown.Option(key=icone[0], text=f"{icone[1]} ({icone[0]})")
            for icone in ICONES_DISPONIVEIS
        ]

        dropdown_icone = ft.Dropdown(
            label="Ícone",
            options=opcoes_icones,
            value="LABEL",
            border=ft.InputBorder.UNDERLINE,
        )

        # Preview do ícone
        preview_icone = ft.Container(
            content=ft.Icon(ft.Icons.LABEL, size=32, color=ft.Colors.PRIMARY),
            width=60, height=60, border_radius=10,
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.PRIMARY),
            alignment=ft.Alignment.CENTER,
        )

        def atualizar_preview(e):
            """Atualiza o preview do ícone quando o dropdown muda."""
            nome_icone = dropdown_icone.value
            icone_obj = _obter_icone(nome_icone)
            preview_icone.content = ft.Icon(icone_obj, size=32, color=ft.Colors.PRIMARY)
            self.root_page.update()

        dropdown_icone.on_change = atualizar_preview

        def salvar_categoria(e):
            """Salva a nova categoria."""
            nome = campo_nome_cat.value
            icone = dropdown_icone.value

            if not nome or not nome.strip():
                self._mostrar_erro("Digite um nome para a categoria")
                return

            try:
                self.service.criar_categoria(nome.strip(), icone)
                self._mostrar_sucesso(f"Categoria '{nome}' criada!")
                dialog.open = False
                self.root_page.update()

                # Atualiza os chips
                self.container_categorias.content.controls = self._criar_chips_categorias()
                self.root_page.update()
            except Exception as ex:
                self._mostrar_erro(f"Erro ao criar categoria: {str(ex)}")

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.LABEL, color=ft.Colors.PRIMARY, size=24),
                ft.Text("Nova Categoria"),
            ], spacing=10),
            content=ft.Column([
                campo_nome_cat,
                ft.Container(height=10),
                ft.Text("Escolha um ícone:", size=13, weight=ft.FontWeight.W_500),
                ft.Container(height=5),
                ft.Row([
                    dropdown_icone,
                    preview_icone,
                ], spacing=15, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ], tight=True, spacing=0),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e: self._fechar_dialog(dialog),
                ),
                ft.FilledButton(
                    "Criar",
                    icon=ft.Icons.CHECK,
                    on_click=salvar_categoria,
                    bgcolor=ft.Colors.PRIMARY,
                    color=ft.Colors.ON_PRIMARY,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.root_page.overlay.append(dialog)
        dialog.open = True
        self.root_page.update()

    def _fechar_dialog(self, dialog):
        """Fecha um dialog."""
        dialog.open = False
        self.root_page.update()

    # ============================================
    # TRANSAÇÕES
    # ============================================

    def _obter_categoria_id(self, nome: str) -> int:
        """Retorna o ID da categoria pelo nome."""
        categorias = self.service.listar_categorias()
        for cat in categorias:
            if cat["nome"] == nome:
                return cat["id"]
        return None

    def _salvar_transacao(self, e):
        """Salva uma nova transação."""
        descricao = self.campo_descricao.value
        valor_texto = self.campo_valor.value
        data_texto = self.campo_data.value
        tipo = self.dropdown_tipo.value  # ✅ Pode ser None se não selecionado

        print(f"\n💾 DEBUG: Salvando transação...")
        print(f"   Descrição: {descricao}")
        print(f"   Valor: {valor_texto}")
        print(f"   Data: {data_texto}")
        print(f"   Tipo: {tipo}")
        print(f"   Categoria: {self.categoria_selecionada}")

        # ✅ Validação do TIPO (CRÍTICO!)
        if not tipo or tipo not in ["despesa", "receita"]:
            print(f"❌ ERRO: Tipo inválido = '{tipo}'")
            self._mostrar_erro("Selecione o tipo (Receita ou Despesa)")
            return

        # Validações
        if not descricao:
            self._mostrar_erro("Preencha a descrição")
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
            data_formatada = datetime.strptime(data_texto, "%d/%m/%Y").strftime("%Y-%m-%d")
        except:
            self._mostrar_erro("Data inválida")
            return

        # Obtém ID da categoria
        categoria_id = None
        if self.categoria_selecionada:
            categoria_id = self._obter_categoria_id(self.categoria_selecionada)

        # ✅ Força o tipo como string válida antes de salvar
        tipo_final = "despesa" if tipo == "despesa" else "receita"

        print(f"✅ Salvando: tipo='{tipo_final}', valor={valor}, categoria_id={categoria_id}")

        self.service.criar_transacao(descricao, valor, tipo_final, data_formatada, categoria_id)

        self._mostrar_sucesso("Transação adicionada!")
        self._limpar_formulario(e)
        self.carregar_transacoes()

    def _limpar_formulario(self, e):
        """Limpa o formulário."""
        self.campo_descricao.value = ""
        self.campo_valor.value = ""
        self.campo_data.value = datetime.now().strftime("%d/%m/%Y")
        self.dropdown_tipo.value = "despesa"
        self.categoria_selecionada = None
        self.container_categorias.content.controls = self._criar_chips_categorias()
        self.root_page.update()

    def _excluir_transacao(self, id: int):
        """Exclui uma transação."""
        self.service.excluir_transacao(id)
        self._mostrar_sucesso("Transação excluída!")
        self.carregar_transacoes()

    def carregar_transacoes(self):
        """Carrega a lista de transações."""
        transacoes = self.service.listar_transacoes()
        self.lista_transacoes.controls.clear()

        if not transacoes:
            self.lista_transacoes.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.RECEIPT_LONG, size=60, color=ft.Colors.ON_SURFACE_VARIANT),
                        ft.Text("Nenhuma transação registrada.",
                                color=ft.Colors.ON_SURFACE_VARIANT, italic=True),
                    ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10),
                    padding=40,
                    alignment=ft.Alignment.CENTER,
                )
            )
        else:
            for trans in transacoes:
                cor = ft.Colors.GREEN_700 if trans["tipo"] == "receita" else ft.Colors.RED_700
                icone = ft.Icons.ARROW_UPWARD if trans["tipo"] == "receita" else ft.Icons.ARROW_DOWNWARD

                try:
                    data_formatada = datetime.strptime(trans["data"], "%Y-%m-%d").strftime("%d/%m/%Y")
                except:
                    data_formatada = trans["data"]

                # Busca nome e ícone da categoria
                nome_categoria = "Sem categoria"
                icone_categoria = ft.Icons.LABEL
                if trans.get("categoria_id"):
                    categorias = self.service.listar_categorias()
                    for cat in categorias:
                        if cat["id"] == trans["categoria_id"]:
                            nome_categoria = cat["nome"]
                            icone_categoria = _obter_icone(cat.get("icone"))
                            break

                self.lista_transacoes.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Container(
                                content=ft.Icon(icone_categoria, color=cor, size=20),
                                width=40, height=40, border_radius=10,
                                bgcolor=ft.Colors.with_opacity(0.1, cor),
                                alignment=ft.Alignment.CENTER,
                            ),
                            ft.Column([
                                ft.Text(trans["descricao"], weight=ft.FontWeight.W_500),
                                ft.Text(f"{data_formatada} • {nome_categoria}",
                                        size=11, color=ft.Colors.ON_SURFACE_VARIANT),
                            ], spacing=2, expand=True),
                            ft.Text(f"R$ {trans['valor']:.2f}".replace(".", ","),
                                    weight=ft.FontWeight.BOLD, color=cor),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_color=ft.Colors.ERROR,
                                on_click=lambda e, tid=trans["id"]: self._excluir_transacao(tid),
                                tooltip="Excluir"
                            ),
                        ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=12,
                        border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                        border_radius=8,
                        bgcolor=ft.Colors.SURFACE_CONTAINER_LOWEST,
                    )
                )

        self.root_page.update()

    def _mostrar_erro(self, mensagem: str):
        snack = ft.SnackBar(
            content=ft.Row([
                ft.Icon(ft.Icons.ERROR_OUTLINE, color=ft.Colors.ON_PRIMARY, size=18),
                ft.Text(mensagem),
            ], spacing=8),
            bgcolor=ft.Colors.ERROR,
            behavior=ft.SnackBarBehavior.FLOATING,
        )
        self.root_page.overlay.append(snack)
        snack.open = True
        self.root_page.update()

    def _mostrar_sucesso(self, mensagem: str):
        snack = ft.SnackBar(
            content=ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.ON_PRIMARY, size=18),
                ft.Text(mensagem),
            ], spacing=8),
            bgcolor=ft.Colors.GREEN_700,
            behavior=ft.SnackBarBehavior.FLOATING,
        )
        self.root_page.overlay.append(snack)
        snack.open = True
        self.root_page.update()