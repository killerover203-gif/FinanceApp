# views/metas_view.py
import flet as ft
from services.finance_service import FinanceService
from datetime import datetime


class MetasView(ft.Column):
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
            print(f"🎯 MetasView: Usuário ID = {usuario_id}")

        self.service = FinanceService(usuario_id=usuario_id)

        # DatePicker para data limite
        self.date_picker = ft.DatePicker(
            on_change=self._data_limite_selecionada,
            first_date=datetime.now(),
            last_date=datetime(2030, 12, 31),
        )
        self.root_page.overlay.append(self.date_picker)

        self._build_ui()
        self.carregar_metas()

    def _build_ui(self):
        # Formulário de nova meta
        self.campo_nome = ft.TextField(
            label="Nome da Meta", width=300,
            prefix_icon=ft.Icons.FLAG,
            border=ft.InputBorder.UNDERLINE
        )

        self.campo_valor_alvo = ft.TextField(
            label="Valor Alvo (R$)", width=150,
            prefix_icon=ft.Icons.ATTACH_MONEY,
            border=ft.InputBorder.UNDERLINE,
            keyboard_type=ft.KeyboardType.NUMBER
        )

        # Campo de data com DatePicker
        self.campo_data_limite = ft.TextField(
            label="Data Limite", width=200,
            prefix_icon=ft.Icons.CALENDAR_TODAY,
            border=ft.InputBorder.UNDERLINE,
            read_only=True,
            on_click=lambda e: self._abrir_date_picker(),
        )

        self.dropdown_tipo = ft.Dropdown(
            label="Tipo", width=150,
            options=[
                ft.dropdown.Option("economia", "Economia"),
                ft.dropdown.Option("investimento", "Investimento"),
                ft.dropdown.Option("compra", "Compra"),
            ],
            value="economia"
        )

        self.dropdown_categoria = ft.Dropdown(
            label="Categoria (opcional)", width=200,
            options=self._carregar_opcoes_categorias(),
            border=ft.InputBorder.UNDERLINE
        )

        # Lista de metas
        self.lista_metas = ft.Column(spacing=10)

        self.controls = [
            ft.Text("Metas Financeiras", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.PRIMARY),

            ft.Container(
                content=ft.Column([
                    ft.Text("Nova Meta", size=16, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        self.campo_nome,
                        self.campo_valor_alvo,
                        self.dropdown_tipo,
                    ], spacing=10, wrap=True),
                    ft.Row([
                        self.campo_data_limite,
                        self.dropdown_categoria,
                    ], spacing=10, wrap=True),
                    ft.Row([
                        ft.FilledButton(
                            "Criar Meta",
                            icon=ft.Icons.ADD_CIRCLE,
                            on_click=self._salvar_meta,
                            bgcolor=ft.Colors.PRIMARY,
                            color=ft.Colors.ON_PRIMARY
                        ),
                        ft.TextButton(
                            "Limpar",
                            on_click=self._limpar_formulario,
                        ),
                    ], spacing=10),
                ], spacing=10),
                padding=20,
                border=ft.Border.all(1, ft.Colors.OUTLINE),
                border_radius=12,
                bgcolor=ft.Colors.SURFACE_CONTAINER_LOWEST,
            ),

            ft.Divider(),

            ft.Text("Minhas Metas", size=18, weight=ft.FontWeight.BOLD),
            self.lista_metas,
        ]

    # ============================================
    # DATE PICKER
    # ============================================

    def _abrir_date_picker(self):
        """Abre o DatePicker."""
        self.date_picker.open = True
        self.root_page.update()

    def _data_limite_selecionada(self, e):
        """Callback quando uma data é selecionada."""
        if self.date_picker.value:
            data_obj = self.date_picker.value
            self.campo_data_limite.value = data_obj.strftime("%d/%m/%Y")
            self.root_page.update()

    # ============================================
    # CÁLCULO DE PROGRESSO (COM SALDO ATUAL)
    # ============================================

    def _calcular_progresso(self, meta: dict) -> dict:
        """Calcula o progresso considerando o saldo atual."""
        valor_alvo = meta["valor_alvo"]
        data_limite = meta.get("data_limite")

        print(f"\n🎯 Calculando progresso da meta: '{meta['nome']}'")

        # ✅ Usa o novo método que considera o saldo
        progresso = self.service.obter_progresso_meta_com_saldo(meta["id"])
        valor_atual = progresso["valor_atual"]
        percentual = progresso["percentual"]

        print(f"   Valor atual: R$ {valor_atual:.2f}")
        print(f"   Percentual: {percentual:.1f}%")

        # Determina status
        hoje = datetime.now().date()

        if percentual >= 100:
            status = "concluida"
            status_texto = "Concluída"
            status_cor = ft.Colors.GREEN_700
            status_icone = ft.Icons.CHECK_CIRCLE
        elif data_limite:
            try:
                data_limite_obj = datetime.strptime(data_limite, "%Y-%m-%d").date()
                if hoje > data_limite_obj:
                    status = "atrasada"
                    status_texto = "Atrasada"
                    status_cor = ft.Colors.RED_700
                    status_icone = ft.Icons.WARNING
                elif percentual > 0:
                    status = "em_andamento"
                    status_texto = "Em andamento"
                    status_cor = ft.Colors.BLUE_700
                    status_icone = ft.Icons.TRENDING_UP
                else:
                    status = "nao_iniciada"
                    status_texto = "Não iniciada"
                    status_cor = ft.Colors.ORANGE_700
                    status_icone = ft.Icons.HOURGLASS_EMPTY
            except:
                if percentual > 0:
                    status = "em_andamento"
                    status_texto = "Em andamento"
                    status_cor = ft.Colors.BLUE_700
                    status_icone = ft.Icons.TRENDING_UP
                else:
                    status = "nao_iniciada"
                    status_texto = "Não iniciada"
                    status_cor = ft.Colors.ORANGE_700
                    status_icone = ft.Icons.HOURGLASS_EMPTY
        else:
            if percentual > 0:
                status = "em_andamento"
                status_texto = "Em andamento"
                status_cor = ft.Colors.BLUE_700
                status_icone = ft.Icons.TRENDING_UP
            else:
                status = "nao_iniciada"
                status_texto = "Não iniciada"
                status_cor = ft.Colors.ORANGE_700
                status_icone = ft.Icons.HOURGLASS_EMPTY

        return {
            "valor_atual": valor_atual,
            "percentual": percentual,
            "status": status,
            "status_texto": status_texto,
            "status_cor": status_cor,
            "status_icone": status_icone,
        }

    # ============================================
    # CATEGORIAS
    # ============================================

    def _carregar_opcoes_categorias(self) -> list:
        """Carrega as categorias para o dropdown."""
        categorias = self.service.listar_categorias()
        options = [ft.dropdown.Option(key="", text="Nenhuma")]
        for cat in categorias:
            options.append(ft.dropdown.Option(key=str(cat["id"]), text=cat["nome"]))
        return options

    # ============================================
    # SALVAR E EXCLUIR METAS
    # ============================================

    def _salvar_meta(self, e):
        """Salva uma nova meta."""
        nome = self.campo_nome.value
        valor_texto = self.campo_valor_alvo.value
        data_texto = self.campo_data_limite.value
        tipo = self.dropdown_tipo.value
        categoria_id_texto = self.dropdown_categoria.value

        if not nome:
            self._mostrar_erro("Preencha o nome da meta")
            return

        try:
            valor_alvo = float(valor_texto.replace(",", "."))
        except:
            self._mostrar_erro("Valor alvo inválido")
            return

        if valor_alvo <= 0:
            self._mostrar_erro("O valor alvo deve ser maior que zero")
            return

        data_limite = None
        if data_texto:
            try:
                data_limite = datetime.strptime(data_texto, "%d/%m/%Y").strftime("%Y-%m-%d")
            except:
                self._mostrar_erro("Data limite inválida")
                return

        categoria_id = None
        if categoria_id_texto and categoria_id_texto != "":
            try:
                categoria_id = int(categoria_id_texto)
            except:
                categoria_id = None

        self.service.criar_meta(nome, tipo, valor_alvo, categoria_id, data_limite)

        self._mostrar_sucesso("Meta criada com sucesso!")
        self._limpar_formulario(e)
        self.carregar_metas()

    def _limpar_formulario(self, e):
        """Limpa o formulário."""
        self.campo_nome.value = ""
        self.campo_valor_alvo.value = ""
        self.campo_data_limite.value = ""
        self.dropdown_tipo.value = "economia"
        self.dropdown_categoria.value = ""
        self.root_page.update()

    def _excluir_meta(self, id: int):
        """Exclui uma meta."""
        self.service.excluir_meta(id)
        self._mostrar_sucesso("Meta excluída!")
        self.carregar_metas()

    # ============================================
    # CARREGAR METAS (COM SALDO ATUAL)
    # ============================================

    def carregar_metas(self):
        """Carrega a lista de metas com barras de progresso considerando o saldo atual."""
        print("\n🎯 Carregando metas...")

        metas = self.service.listar_metas()
        print(f"📋 {len(metas)} metas encontradas")

        self.lista_metas.controls.clear()

        if not metas:
            self.lista_metas.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.FLAG_OUTLINED, size=60, color=ft.Colors.ON_SURFACE_VARIANT),
                        ft.Text("Nenhuma meta cadastrada.",
                                color=ft.Colors.ON_SURFACE_VARIANT, italic=True),
                        ft.Text("Crie sua primeira meta acima!",
                                size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                    ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10),
                    padding=40,
                    alignment=ft.Alignment.CENTER,
                )
            )
        else:
            # ✅ Mostra saldo atual no topo
            saldo_atual = self.service.obter_saldo_atual()
            self.lista_metas.controls.append(self._criar_card_saldo_atual(saldo_atual))

            # Contadores de status
            stats = {"concluida": 0, "em_andamento": 0, "atrasada": 0, "nao_iniciada": 0}

            for meta in metas:
                print(f"\n🎯 Processando meta: '{meta['nome']}' (ID: {meta['id']})")
                progresso = self._calcular_progresso(meta)
                stats[progresso["status"]] += 1

                print(f"   Status: {progresso['status_texto']} ({progresso['percentual']:.1f}%)")

                self.lista_metas.controls.append(
                    self._criar_card_meta(meta, progresso)
                )

            # Adiciona resumo de status
            self.lista_metas.controls.insert(1, self._criar_resumo_status(stats, len(metas)))

        self.root_page.update()
        print(f"✅ Metas carregadas com sucesso!")

    def _criar_card_saldo_atual(self, saldo: float) -> ft.Container:
        """Cria um card mostrando o saldo atual do usuário."""
        cor = ft.Colors.GREEN_700 if saldo >= 0 else ft.Colors.RED_700
        icone = ft.Icons.ARROW_UPWARD if saldo >= 0 else ft.Icons.ARROW_DOWNWARD

        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(icone, color=ft.Colors.ON_PRIMARY, size=28),
                    width=50, height=50, border_radius=12,
                    bgcolor=cor,
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Column([
                    ft.Text("Saldo Atual Disponível", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                    ft.Text(
                        self._formatar_valor(saldo),
                        size=22, weight=ft.FontWeight.BOLD, color=cor
                    ),
                ], spacing=2, expand=True),
                ft.Icon(ft.Icons.INFO_OUTLINE, size=18, color=ft.Colors.ON_SURFACE_VARIANT),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=15,
            border=ft.Border.all(2, cor),
            border_radius=12,
            bgcolor=ft.Colors.with_opacity(0.05, cor),
            margin=ft.Margin(bottom=10),
        )

    def _criar_resumo_status(self, stats: dict, total: int) -> ft.Container:
        """Cria um resumo visual dos status das metas."""
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.ANALYTICS, size=18, color=ft.Colors.PRIMARY),
                    ft.Text(f"Resumo ({total} {('meta' if total == 1 else 'metas')})",
                            size=13, weight=ft.FontWeight.BOLD),
                ], spacing=6),
                ft.Container(height=5),
                ft.Row([
                    self._criar_badge_status(
                        "Concluídas", stats["concluida"],
                        ft.Colors.GREEN_700, ft.Icons.CHECK_CIRCLE
                    ),
                    self._criar_badge_status(
                        "Em andamento", stats["em_andamento"],
                        ft.Colors.BLUE_700, ft.Icons.TRENDING_UP
                    ),
                    self._criar_badge_status(
                        "Atrasadas", stats["atrasada"],
                        ft.Colors.RED_700, ft.Icons.WARNING
                    ),
                    self._criar_badge_status(
                        "Não iniciadas", stats["nao_iniciada"],
                        ft.Colors.ORANGE_700, ft.Icons.HOURGLASS_EMPTY
                    ),
                ], spacing=10, wrap=True),
            ], spacing=0),
            padding=15,
            border=ft.Border.all(1, ft.Colors.OUTLINE),
            border_radius=10,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOWEST,
            margin=ft.Margin(bottom=10),
        )

    def _criar_badge_status(self, label: str, count: int, cor: str, icone: str) -> ft.Container:
        """Cria um badge de status."""
        return ft.Container(
            content=ft.Row([
                ft.Icon(icone, size=18, color=cor),
                ft.Column([
                    ft.Text(str(count), size=16, weight=ft.FontWeight.BOLD, color=cor),
                    ft.Text(label, size=10, color=ft.Colors.ON_SURFACE_VARIANT),
                ], spacing=0),
            ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=12, right=12, top=8, bottom=8),
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=8,
            bgcolor=ft.Colors.with_opacity(0.05, cor),
        )

    def _criar_card_meta(self, meta: dict, progresso: dict) -> ft.Container:
        """Cria um card de meta com barra de progresso considerando o saldo atual."""
        nome = meta["nome"]
        valor_alvo = meta["valor_alvo"]
        tipo = meta["tipo"]
        data_limite = meta.get("data_limite")
        categoria_id = meta.get("categoria_id")

        # Ícone e cor do tipo
        if tipo == "economia":
            icone_tipo = ft.Icons.SAVINGS
            cor_tipo = ft.Colors.BLUE_700
            tipo_texto = "Economia"
        elif tipo == "investimento":
            icone_tipo = ft.Icons.TRENDING_UP
            cor_tipo = ft.Colors.GREEN_700
            tipo_texto = "Investimento"
        else:
            icone_tipo = ft.Icons.SHOPPING_CART
            cor_tipo = ft.Colors.ORANGE_700
            tipo_texto = "Compra"

        # Formata data limite
        data_formatada = "Sem data limite"
        if data_limite:
            try:
                data_formatada = datetime.strptime(data_limite, "%Y-%m-%d").strftime("%d/%m/%Y")
            except:
                data_formatada = data_limite

        # Busca nome da categoria
        nome_categoria = ""
        if categoria_id:
            categorias = self.service.listar_categorias()
            for cat in categorias:
                if cat["id"] == categoria_id:
                    nome_categoria = f" • {cat['nome']}"
                    break

        # ProgressBar com cor baseada no progresso
        percentual = progresso["percentual"]
        valor_atual = progresso["valor_atual"]

        if percentual >= 100:
            cor_barra = ft.Colors.GREEN_700
        elif percentual >= 50:
            cor_barra = ft.Colors.BLUE_700
        elif percentual > 0:
            cor_barra = ft.Colors.ORANGE_700
        else:
            cor_barra = ft.Colors.GREY_400

        progress_bar = ft.ProgressBar(
            value=percentual / 100,
            color=cor_barra,
            bgcolor=ft.Colors.with_opacity(0.1, cor_barra),
        )

        # Badge de status
        badge_status = ft.Container(
            content=ft.Row([
                ft.Icon(progresso["status_icone"], size=14, color=ft.Colors.ON_PRIMARY),
                ft.Text(progresso["status_texto"], size=11, weight=ft.FontWeight.BOLD,
                        color=ft.Colors.ON_PRIMARY),
            ], spacing=4),
            bgcolor=progresso["status_cor"],
            padding=ft.Padding(left=10, right=10, top=4, bottom=4),
            border_radius=12,
        )

        # Formata valores
        valor_atual_fmt = self._formatar_valor(valor_atual)
        valor_alvo_fmt = self._formatar_valor(valor_alvo)

        return ft.Container(
            content=ft.Column([
                # Linha superior: ícone + nome + badge + excluir
                ft.Row([
                    ft.Container(
                        content=ft.Icon(icone_tipo, color=cor_tipo, size=28),
                        width=45, height=45, border_radius=10,
                        bgcolor=ft.Colors.with_opacity(0.1, cor_tipo),
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Column([
                        ft.Text(nome, weight=ft.FontWeight.BOLD, size=15),
                        ft.Text(
                            f"{tipo_texto}{nome_categoria} • Limite: {data_formatada}",
                            size=11, color=ft.Colors.ON_SURFACE_VARIANT
                        ),
                    ], spacing=2, expand=True),
                    badge_status,
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color=ft.Colors.ERROR,
                        on_click=lambda e, mid=meta["id"]: self._excluir_meta(mid),
                        tooltip="Excluir meta",
                        icon_size=18,
                    ),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),

                ft.Container(height=10),

                # Linha do progresso
                ft.Row([
                    ft.Column([
                        ft.Text(
                            valor_atual_fmt,
                            size=13, weight=ft.FontWeight.BOLD,
                            color=cor_barra,
                        ),
                        ft.Text("acumulado", size=10, color=ft.Colors.ON_SURFACE_VARIANT),
                    ], spacing=0),
                    ft.Container(expand=True),
                    ft.Column([
                        ft.Text(
                            valor_alvo_fmt,
                            size=13, weight=ft.FontWeight.W_500,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                        ft.Text("meta", size=10, color=ft.Colors.ON_SURFACE_VARIANT),
                    ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.END),
                ], vertical_alignment=ft.CrossAxisAlignment.START),

                ft.Container(height=5),

                # Barra de progresso
                progress_bar,

                ft.Container(height=5),

                # Porcentagem
                ft.Row([
                    ft.Container(expand=True),
                    ft.Text(
                        f"{percentual:.1f}% concluído",
                        size=12, weight=ft.FontWeight.BOLD,
                        color=cor_barra,
                    ),
                ]),
            ], spacing=0),
            padding=15,
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=10,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOWEST,
        )

    # ============================================
    # UTILITÁRIOS
    # ============================================

    def _formatar_valor(self, valor: float) -> str:
        """Formata valor monetário."""
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # ============================================
    # FEEDBACK VISUAL
    # ============================================

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