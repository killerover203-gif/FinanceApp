# views/main_view.py
import flet as ft
from datetime import datetime
from views.transactions_view import TransactionsView
from views.dashboard_view import DashboardView
from views.metas_view import MetasView
from views.contas_view import ContasView
from views.settings_view import SettingsView
from services.tema_service import TemaService


class MainView:
    def __init__(self, page: ft.Page, usuario_logado=None):
        self.page = page
        self.page.title = "Finanças Pessoais"
        self.page.padding = 0
        self.usuario_logado = usuario_logado

        # Service de tema
        self.tema_service = TemaService()

        # Estado
        self.tela_atual = "transacoes"

        # Aplica tema
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self._aplicar_tema_flet()

        # Área de conteúdo
        self.content_area = ft.Container(
            expand=True,
            content=TransactionsView(page),
            padding=20,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOWEST
        )

        # Botões da sidebar
        self.btn_transacoes = self._criar_botao_menu("Transações", ft.Icons.RECEIPT_LONG, "transacoes")
        self.btn_resumo = self._criar_botao_menu("Resumo", ft.Icons.DASHBOARD, "resumo")
        self.btn_metas = self._criar_botao_menu("Metas", ft.Icons.FLAG, "metas")
        self.btn_contas = self._criar_botao_menu("Contas", ft.Icons.RECEIPT, "contas")
        self.btn_config = self._criar_botao_menu("Configurações", ft.Icons.SETTINGS, "config")

        # Botão de toggle de tema
        self.btn_tema = ft.IconButton(
            icon=ft.Icons.DARK_MODE,
            icon_size=22,
            on_click=self._alternar_tema,
            tooltip="Alternar tema claro/escuro"
        )

        # Data formatada
        data_atual = datetime.now()
        dias_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
        meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        self.texto_data = f"{dias_semana[data_atual.weekday()]}, {data_atual.day:02d} {meses[data_atual.month - 1]} {data_atual.year}"

        # Sidebar
        self.sidebar = ft.Container(
            width=240,
            padding=ft.Padding(left=15, top=20, right=15, bottom=20),
            content=ft.Column(
                controls=[
                    ft.Row([
                        ft.Container(
                            content=ft.Icon(ft.Icons.ACCOUNT_BALANCE, size=28),
                            width=45, height=45, border_radius=12,
                            alignment=ft.Alignment.CENTER,
                        ),
                        ft.Column([
                            ft.Text("FinanceApp", size=18, weight=ft.FontWeight.BOLD),
                            ft.Text("Premium", size=10, weight=ft.FontWeight.W_300),
                        ], spacing=0)
                    ], alignment=ft.MainAxisAlignment.START, spacing=10),

                    ft.Container(height=20),
                    ft.Text("MENU", size=11, weight=ft.FontWeight.BOLD),
                    ft.Container(height=5),

                    self.btn_transacoes,
                    self.btn_resumo,
                    self.btn_metas,
                    self.btn_contas,

                    ft.Container(height=10),
                    ft.Text("SISTEMA", size=11, weight=ft.FontWeight.BOLD),
                    ft.Container(height=5),
                    self.btn_config,

                    ft.Container(expand=True),

                    ft.Divider(),
                    ft.Row([
                        self.btn_tema,
                        ft.Text("Tema", size=12),
                    ], alignment=ft.MainAxisAlignment.START, spacing=8),
                ],
                spacing=4
            )
        )

        # Topbar com nome do usuário
        self.topbar_titulo = ft.Text("Transações", size=22, weight=ft.FontWeight.BOLD)

        if self.usuario_logado:
            texto_usuario = ft.Row([
                ft.Icon(ft.Icons.PERSON, size=16, color=ft.Colors.PRIMARY),
                ft.Text(f"Olá, {self.usuario_logado.nome.split()[0]}",
                        size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                ft.IconButton(
                    icon=ft.Icons.LOGOUT,
                    icon_size=18,
                    tooltip="Sair",
                    on_click=self._fazer_logout,
                ),
            ], spacing=8)
        else:
            texto_usuario = ft.Text(self.texto_data, size=12, color=ft.Colors.ON_SURFACE_VARIANT)

        self.topbar = ft.Container(
            height=60,
            padding=ft.Padding(left=25, right=25, top=0, bottom=0),
            bgcolor=ft.Colors.SURFACE,
            border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT)),
            content=ft.Row([
                self.topbar_titulo,
                ft.Container(expand=True),
                texto_usuario,
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER)
        )

        # ✅ Container interno exposto como 'conteudo'
        self.conteudo = ft.Container(
            content=ft.Row([
                self.sidebar,
                ft.Column([
                    self.topbar,
                    self.content_area,
                ], expand=True, spacing=0)
            ], expand=True, spacing=0),
            expand=True,
        )

        self._atualizar_cores_sidebar()
        self._marcar_ativo(self.btn_transacoes)

    def _criar_botao_menu(self, texto: str, icone: str, tela: str) -> ft.Container:
        return ft.Container(
            content=ft.Row([
                ft.Icon(icone, size=20),
                ft.Text(texto, size=14, weight=ft.FontWeight.W_500),
            ], spacing=12),
            padding=ft.Padding(left=15, top=12, right=15, bottom=12),
            border_radius=10,
            ink=True,
            on_click=lambda e, t=tela: self._navegar(t),
            data=tela,
        )

    def _obter_botao_ativo_atual(self):
        for btn in [self.btn_transacoes, self.btn_resumo, self.btn_metas,
                    self.btn_contas, self.btn_config]:
            if btn.bgcolor is not None:
                return btn
        return self.btn_transacoes

    def _marcar_ativo(self, botao_ativo: ft.Container):
        paleta = self.tema_service.obter_paleta_atual(
            self.page.theme_mode == ft.ThemeMode.DARK
        )

        botoes = [self.btn_transacoes, self.btn_resumo, self.btn_metas,
                  self.btn_contas, self.btn_config]
        for btn in botoes:
            if btn == botao_ativo:
                btn.bgcolor = paleta["botao_ativo"]
                btn.content.controls[0].color = paleta["botao_ativo_texto"]
                btn.content.controls[1].color = paleta["botao_ativo_texto"]
                btn.content.controls[1].weight = ft.FontWeight.BOLD
            else:
                btn.bgcolor = None
                btn.content.controls[0].color = paleta["botao_normal_icone"]
                btn.content.controls[1].color = paleta["botao_normal_texto"]
                btn.content.controls[1].weight = ft.FontWeight.W_500
        self.page.update()

    def _atualizar_cores_sidebar(self):
        paleta = self.tema_service.obter_paleta_atual(
            self.page.theme_mode == ft.ThemeMode.DARK
        )

        self.sidebar.bgcolor = paleta["sidebar_fundo"]
        self.sidebar.border = ft.Border(right=ft.BorderSide(1, paleta["sidebar_borda"]))

        logo_container = self.sidebar.content.controls[0].controls[0]
        logo_container.bgcolor = paleta["logo_fundo"]
        logo_container.content.color = paleta["logo_icone"]
        logo_container.border = ft.Border.all(1.5, paleta["sidebar_borda"])

        logo_texto = self.sidebar.content.controls[0].controls[1].controls[0]
        logo_texto.color = paleta["logo_texto"]

        subtitulo_logo = self.sidebar.content.controls[0].controls[1].controls[1]
        subtitulo_logo.color = paleta["tema_label"]

        self.sidebar.content.controls[3].color = paleta["menu_label"]
        self.sidebar.content.controls[9].color = paleta["menu_label"]

        self.sidebar.content.controls[13].color = paleta["sidebar_borda"]
        self.sidebar.content.controls[14].controls[1].color = paleta["tema_label"]
        self.btn_tema.icon_color = paleta["tema_label"]

        botao_ativo = self._obter_botao_ativo_atual()
        self._marcar_ativo(botao_ativo)

    def _navegar(self, tela: str):
        self.tela_atual = tela

        telas = {
            "transacoes": (TransactionsView, "Transações"),
            "resumo": (DashboardView, "Resumo"),
            "metas": (MetasView, "Metas"),
            "contas": (ContasView, "Contas"),
            "config": (None, "Configurações"),
        }

        if tela == "config":
            self.content_area.content = SettingsView(
                self.page, on_tema_alterado=self._ao_tema_alterado
            )
        else:
            classe_view, titulo = telas[tela]
            self.content_area.content = classe_view(self.page)

        self.topbar_titulo.value = telas[tela][1]

        botoes = {
            "transacoes": self.btn_transacoes,
            "resumo": self.btn_resumo,
            "metas": self.btn_metas,
            "contas": self.btn_contas,
            "config": self.btn_config,
        }
        self._marcar_ativo(botoes[tela])
        self.page.update()

    def _ao_tema_alterado(self):
        self._aplicar_tema_flet()
        self._atualizar_cores_sidebar()

        telas = {
            "transacoes": TransactionsView,
            "resumo": DashboardView,
            "metas": MetasView,
            "contas": ContasView,
            "config": lambda page: SettingsView(page, on_tema_alterado=self._ao_tema_alterado),
        }

        classe_view = telas.get(self.tela_atual)
        if classe_view:
            self.content_area.content = classe_view(self.page)

        self.page.update()

    def _aplicar_tema_flet(self):
        seed = self.tema_service.obter_seed_tema()
        self.page.theme = ft.Theme(color_scheme_seed=seed, use_material3=True)
        self.page.dark_theme = ft.Theme(color_scheme_seed=seed, use_material3=True)

    def _alternar_tema(self, e):
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.btn_tema.icon = ft.Icons.LIGHT_MODE
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.btn_tema.icon = ft.Icons.DARK_MODE

        self._atualizar_cores_sidebar()
        self.page.update()

    def _fazer_logout(self, e):
        """Mostra dialog de confirmação de logout."""

        def cancelar(e):
            dialog.open = False
            self.page.update()

        def confirmar_saida(e):
            # 1. Fecha o dialog
            dialog.open = False
            self.page.update()

            # 2. Chama o logout do app principal
            if hasattr(self.page, 'finance_app'):
                self.page.finance_app.logout()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar saída"),
            content=ft.Text("Deseja realmente sair da sua conta?"),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar),
                ft.TextButton(
                    "Sair",
                    on_click=confirmar_saida,
                    style=ft.ButtonStyle(color=ft.Colors.ERROR),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()