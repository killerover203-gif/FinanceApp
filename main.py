# main.py
"""
Arquivo principal do FinanceApp — Versão Firebase.
⚠️ MUDANÇA: init_db() → init_firebase()
"""
import sys
import os

# ✅ Importa o logger PRIMEIRO
try:
    from utils.logger import log, get_log_path
    log("=" * 60)
    log("🚀 FinanceApp iniciando (FIREBASE)...")
    log(f"📝 Log file: {get_log_path()}")
    log("=" * 60)
except ImportError:
    def log(msg):
        print(msg)
    def get_log_path():
        return "N/A"

import flet as ft

# ⚠️ NOVO: importa init_firebase ao invés de init_db
from database.firebase_connection import init_firebase
from services.auth_service import AuthService
from views.auth_view import AuthView
from views.main_view import MainView


class FinanceApp:
    def __init__(self, page: ft.Page):
        log("🎨 FinanceApp.__init__() chamado")
        self.page = page
        self.page.title = "FinanceApp"
        self.page.padding = 0
        self.page.window.maximized = True

        # Aplica tema
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.theme = ft.Theme(
            color_scheme_seed="emerald",
            use_material3=True,
        )

        self.auth_service = AuthService()

        # 🔄 Inicializa Firebase (cria categorias padrão se não existirem)
        log("🔄 Chamando init_firebase()...")
        try:
            init_firebase()
            log("✅ init_firebase() executado com sucesso")
        except Exception as e:
            log(f"❌ ERRO em init_firebase(): {e}")
            import traceback
            log(traceback.format_exc())

        # Cria containers
        self._criar_containers()
        self._mostrar_login()

    def _criar_containers(self):
        log("📦 Criando containers...")
        self.container_auth = ft.Container(expand=True, visible=True)
        self.container_app = ft.Container(expand=True, visible=False)

        self.page.add(
            ft.Stack([
                self.container_auth,
                self.container_app,
            ], expand=True)
        )

        self.page.finance_app = self
        log("✅ Containers criados")

    def _mostrar_login(self):
        log("🔐 Mostrando tela de login...")
        self.container_auth.content = None
        self.page.usuario_logado = None

        auth_view = AuthView(
            self.page,
            on_login_sucesso=self._login_sucesso
        )

        self.container_auth.content = ft.Container(
            content=ft.Row([
                ft.Container(expand=True),
                auth_view.conteudo,
                ft.Container(expand=True),
            ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True),
            expand=True,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOWEST,
        )

        self.container_auth.visible = True
        self.container_app.visible = False
        self.page.update()
        log("✅ Tela de login exibida")

    def _login_sucesso(self, usuario):
        log(f"✅ LOGIN: {usuario.nome} (ID: {usuario.id})")
        self.page.usuario_logado = usuario
        self.container_app.content = None

        main_view = MainView(self.page, usuario_logado=usuario)
        self.container_app.content = main_view.conteudo

        self.container_auth.visible = False
        self.container_app.visible = True
        self.page.update()
        log("✅ MainView exibido")

    def logout(self):
        log(f"🚪 LOGOUT")
        self.auth_service.logout()
        self._mostrar_login()


def main(page: ft.Page):
    log("🎯 main() chamado")
    FinanceApp(page)


import os

# ... resto das importações ...
import os
import flet as ft

# ... todo o resto do código continua IGUAL ...

# ✅ ISSO ESTÁ CERTO na versão 0.86.5:
if __name__ == "__main__":
    init_firebase()

    porta = int(os.getenv("PORT", 10000))

    ft.run(
        main,
        view=ft.AppView.WEB_BROWSER,
        host="0.0.0.0",
        port=porta,
        assets_dir="assets"
    )