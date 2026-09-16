# views/settings_view.py
import flet as ft
from services.tema_service import TemaService


class SettingsView(ft.Column):
    def __init__(self, page: ft.Page, on_tema_alterado=None):
        super().__init__()
        self.root_page = page
        self.service = TemaService()
        self.on_tema_alterado = on_tema_alterado
        self.expand = True
        self.spacing = 20
        self.scroll = ft.ScrollMode.AUTO

        self._build_ui()

    def _build_ui(self):
        tema_atual_id = self.service.obter_tema_atual()
        temas = self.service.listar_temas()

        cards_temas = []
        for tema in temas:
            eh_atual = tema["id"] == tema_atual_id
            cards_temas.append(self._criar_card_tema(tema, eh_atual))

        self.controls = [
            ft.Row([
                ft.Icon(ft.Icons.PALETTE, size=28, color=ft.Colors.PRIMARY),
                ft.Column([
                    ft.Text("Personalização", size=22, weight=ft.FontWeight.BOLD),
                    ft.Text("Escolha o tema que combina com você", size=13,
                            color=ft.Colors.ON_SURFACE_VARIANT),
                ], spacing=2),
            ], spacing=12),

            ft.Text("Temas disponíveis", size=16, weight=ft.FontWeight.BOLD),
            ft.Text("Clique em um tema para aplicá-lo. A sidebar atualiza na hora; "
                    "as outras telas precisam reiniciar o app.",
                    size=12, color=ft.Colors.ON_SURFACE_VARIANT),

            ft.Row(
                controls=cards_temas,
                spacing=15,
                wrap=True,
            ),

            ft.Divider(),

            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.INFO_OUTLINE, size=20, color=ft.Colors.PRIMARY),
                        ft.Text("Dica", size=14, weight=ft.FontWeight.BOLD),
                    ], spacing=8),
                    ft.Text(
                        "O tema escolhido é salvo automaticamente. "
                        "Você pode alternar entre modo claro e escuro a qualquer momento "
                        "usando o botão no rodapé da sidebar.",
                        size=12,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                ], spacing=8),
                padding=15,
                border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                border_radius=10,
                bgcolor=ft.Colors.SURFACE_CONTAINER_LOWEST,
            ),
        ]

    def _criar_card_tema(self, tema: dict, eh_atual: bool) -> ft.Container:
        cores_preview = tema["preview_cores"]

        circulos_cores = ft.Row([
            ft.Container(
                width=24, height=24, border_radius=12,
                bgcolor=cor,
                border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT)
            )
            for cor in cores_preview
        ], spacing=6)

        badge_ativo = ft.Container(
            content=ft.Text("ATIVO", size=10, weight=ft.FontWeight.BOLD,
                            color=ft.Colors.ON_PRIMARY),
            bgcolor=ft.Colors.PRIMARY,
            padding=ft.Padding(left=8, right=8, top=3, bottom=3),
            border_radius=10,
            visible=eh_atual,
        )

        card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(tema["nome"], size=16, weight=ft.FontWeight.BOLD),
                    badge_ativo,
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Text(tema["descricao"], size=12,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                        max_lines=2),
                ft.Container(height=8),
                circulos_cores,
                ft.Container(height=8),
                ft.TextButton(
                    "Aplicar tema" if not eh_atual else "Tema atual",
                    icon=ft.Icons.CHECK_CIRCLE if eh_atual else ft.Icons.PALETTE,
                    on_click=lambda e, tid=tema["id"]: self._aplicar_tema(tid),
                    disabled=eh_atual,
                ),
            ], spacing=4),
            width=260,
            padding=18,
            border=ft.Border.all(2, ft.Colors.PRIMARY if eh_atual else ft.Colors.OUTLINE),
            border_radius=12,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOWEST,
        )

        return card

    def _aplicar_tema(self, tema_id: str):
        """Aplica o tema e mostra instrução para reiniciar."""
        self.service.definir_tema(tema_id)

        # Atualiza a sidebar em tempo real
        if self.on_tema_alterado:
            self.on_tema_alterado()

        tema_nome = next((t["nome"] for t in self.service.listar_temas() if t["id"] == tema_id), tema_id)

        # Dialog elegante pedindo reinicialização manual
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN_700, size=28),
                ft.Text(f"Tema '{tema_nome}' aplicado!"),
            ], spacing=10),
            content=ft.Column([
                ft.Text(
                    "A sidebar já foi atualizada com o novo tema.",
                    size=14,
                    weight=ft.FontWeight.W_500,
                ),
                ft.Container(height=8),
                ft.Text(
                    "Para aplicar o tema em todas as telas, "
                    "feche o aplicativo e abra novamente.",
                    size=13,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
                ft.Container(height=12),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.KEYBOARD, size=16, color=ft.Colors.PRIMARY),
                        ft.Text("Atalho: Alt + F4 para fechar rapidamente",
                                size=12, color=ft.Colors.PRIMARY),
                    ], spacing=8),
                    padding=10,
                    bgcolor=ft.Colors.PRIMARY_CONTAINER,
                    border_radius=8,
                ),
            ], tight=True, spacing=0),
            actions=[
                ft.FilledButton(
                    "Entendi!",
                    icon=ft.Icons.THUMB_UP,
                    on_click=lambda e: self._fechar_dialog(dialog),
                    bgcolor=ft.Colors.PRIMARY,
                    color=ft.Colors.ON_PRIMARY,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )

        self.root_page.overlay.append(dialog)
        dialog.open = True
        self.root_page.update()

    def _fechar_dialog(self, dialog):
        dialog.open = False
        self.root_page.update()