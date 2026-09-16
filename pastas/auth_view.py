# views/auth_view.py
"""View de autenticação com login, registro e recuperação de senha."""
import flet as ft
from services.auth_service import AuthService


class AuthView:
    def __init__(self, root_page: ft.Page, on_login_sucesso=None,
                 largura_form=450, altura_tela=600):
        self.root_page = root_page
        self.auth_service = AuthService()
        self.on_login_sucesso = on_login_sucesso
        self.largura_form = largura_form
        self.altura_tela = altura_tela

        # Cores do tema
        self.cor_primaria = "#2E7D5B"
        self.cor_texto_escuro = ft.Colors.ON_SURFACE
        self.cor_texto_claro = ft.Colors.ON_SURFACE_VARIANT
        self.cor_texto_botao = "#FFFFFF"

        # Cria os campos
        self._criar_campos()

        # Constrói a UI
        self._build_ui()

    def _criar_campos(self):
        """Cria todos os campos de texto seguindo o padrão original."""
        largura_campo = min(320, self.largura_form - 60)
        largura_botao = min(320, self.largura_form - 60)
        self.largura_botao = largura_botao

        # === Campos de Login ===
        self.campo_email_login = ft.TextField(
            label="E-mail", width=largura_campo,
            prefix_icon=ft.Icons.EMAIL, border=ft.InputBorder.UNDERLINE
        )
        self.campo_senha_login = ft.TextField(
            label="Senha", width=largura_campo,
            prefix_icon=ft.Icons.LOCK, password=True,
            can_reveal_password=True, border=ft.InputBorder.UNDERLINE
        )

        # === Campos de Registro ===
        self.campo_nome_registro = ft.TextField(
            label="Nome Completo", width=largura_campo,
            prefix_icon=ft.Icons.PERSON, border=ft.InputBorder.UNDERLINE
        )
        self.campo_email_registro = ft.TextField(
            label="E-mail", width=largura_campo,
            prefix_icon=ft.Icons.EMAIL, border=ft.InputBorder.UNDERLINE
        )
        self.campo_senha_registro = ft.TextField(
            label="Senha", width=largura_campo,
            prefix_icon=ft.Icons.LOCK, password=True,
            can_reveal_password=True, border=ft.InputBorder.UNDERLINE
        )
        self.campo_confirma_senha = ft.TextField(
            label="Confirmar Senha", width=largura_campo,
            prefix_icon=ft.Icons.LOCK_OUTLINE, password=True,
            can_reveal_password=True, border=ft.InputBorder.UNDERLINE
        )

        # === Campos de Pergunta de Segurança ===
        self.campo_pergunta_seguranca = ft.TextField(
            label="Pergunta de segurança", width=largura_campo,
            prefix_icon=ft.Icons.HELP_OUTLINE,
            border=ft.InputBorder.UNDERLINE,
        )
        self.campo_resposta_seguranca = ft.TextField(
            label="Resposta", width=largura_campo,
            prefix_icon=ft.Icons.QUESTION_ANSWER,
            border=ft.InputBorder.UNDERLINE,
        )

        # Textos de erro
        self.txt_erro_login = ft.Text("", color=ft.Colors.ERROR, size=12, visible=False)
        self.txt_erro_registro = ft.Text("", color=ft.Colors.ERROR, size=12, visible=False)

    def _build_ui(self):
        """Constrói a interface seguindo o padrão dos arquivos originais."""
        largura_botao = self.largura_botao

        # =============================================
        # TELA DE LOGIN (igual tela_login.py)
        # =============================================
        self.conteudo_login = ft.Container(
            content=ft.Column([
                ft.Text("Bem-vindo de volta!", size=28, weight=ft.FontWeight.BOLD,
                        color=self.cor_texto_escuro),
                ft.Text("Entre com sua conta", size=16,
                        color=self.cor_texto_claro),
                ft.Container(height=30),
                self.campo_email_login,
                self.campo_senha_login,
                self.txt_erro_login,
                ft.Container(height=10),
                ft.TextButton(
                    "Esqueci minha senha",
                    on_click=lambda e: self._abrir_dialog_recuperar_senha(),
                    style=ft.ButtonStyle(color=self.cor_primaria)
                ),
                ft.Container(height=20),
                ft.FilledButton(
                    "ENTRAR", width=largura_botao,
                    bgcolor=self.cor_primaria,
                    color=self.cor_texto_botao,
                    on_click=lambda e: self._fazer_login(),
                ),
                ft.Container(height=30),
                ft.Row([
                    ft.Text("Não tem conta? "),
                    ft.TextButton(
                        "Registrar-se",
                        on_click=lambda e: self._mostrar_registro(),
                        style=ft.ButtonStyle(color=self.cor_primaria)
                    )
                ], alignment=ft.MainAxisAlignment.CENTER)
            ], alignment=ft.MainAxisAlignment.CENTER,
               horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
            width=self.largura_form, height=self.altura_tela, padding=20,
            left=0, top=0, visible=True, opacity=1,
            animate_opacity=ft.Animation(duration=350)
        )

        # =============================================
        # TELA DE REGISTRO (igual tela_registro.py + segurança)
        # =============================================
        self.conteudo_registro = ft.Container(
            content=ft.Column([
                ft.Text("Criar Conta", size=28, weight=ft.FontWeight.BOLD,
                        color=self.cor_texto_escuro),
                ft.Text("Preencha seus dados", size=16,
                        color=self.cor_texto_claro),
                ft.Container(height=25),
                self.campo_nome_registro,
                self.campo_email_registro,
                self.campo_senha_registro,
                self.campo_confirma_senha,
                ft.Container(height=10),
                ft.Divider(),
                ft.Container(height=5),
                ft.Row([
                    ft.Icon(ft.Icons.SHIELD, size=16, color=self.cor_primaria),
                    ft.Text("Pergunta de segurança", size=13,
                            weight=ft.FontWeight.BOLD, color=self.cor_primaria),
                ], spacing=6),
                ft.Text("Usada para recuperar sua senha",
                        size=10, color=self.cor_texto_claro, italic=True),
                ft.Container(height=5),
                self.campo_pergunta_seguranca,
                ft.Text("Ex: Nome do seu primeiro animal de estimação?",
                        size=9, color=self.cor_texto_claro, italic=True),
                ft.Container(height=3),
                self.campo_resposta_seguranca,
                ft.Text("Não diferencia maiúsculas de minúsculas",
                        size=9, color=self.cor_texto_claro, italic=True),
                self.txt_erro_registro,
                ft.Container(height=15),
                ft.FilledButton(
                    "CADASTRAR", width=largura_botao,
                    bgcolor=self.cor_primaria,
                    color=self.cor_texto_botao,
                    on_click=lambda e: self._fazer_registro(),
                ),
                ft.Container(height=20),
                ft.Row([
                    ft.Text("Já tem conta? "),
                    ft.TextButton(
                        "Entrar",
                        on_click=lambda e: self._mostrar_login(),
                        style=ft.ButtonStyle(color=self.cor_primaria)
                    )
                ], alignment=ft.MainAxisAlignment.CENTER)
            ], alignment=ft.MainAxisAlignment.CENTER,
               horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5,
               scroll=ft.ScrollMode.AUTO),
            width=self.largura_form, height=self.altura_tela, padding=20,
            left=self.largura_form, top=0, visible=False, opacity=0,
            animate_opacity=ft.Animation(duration=350)
        )

        # =============================================
        # CONTAINER PRINCIPAL (Stack com as duas telas)
        # =============================================
        self.conteudo = ft.Stack([
            self.conteudo_login,
            self.conteudo_registro,
        ], width=self.largura_form, height=self.altura_tela)

    # ============================================
    # MÉTODOS DE NAVEGAÇÃO (igual original)
    # ============================================

    def _mostrar_registro(self):
        """Mostra tela de registro com animação (igual original)."""
        self.conteudo_login.opacity = 0
        self.conteudo_login.visible = False
        self.conteudo_registro.left = 0
        self.conteudo_registro.visible = True
        self.conteudo_registro.opacity = 1
        self._limpar_erros()
        self.root_page.update()

    def _mostrar_login(self):
        """Mostra tela de login com animação (igual original)."""
        self.conteudo_registro.opacity = 0
        self.conteudo_registro.visible = False
        self.conteudo_registro.left = self.largura_form
        self.conteudo_login.left = 0
        self.conteudo_login.visible = True
        self.conteudo_login.opacity = 1
        self._limpar_erros()
        self.root_page.update()

    def mostrar(self):
        """Mostra o container principal (igual original)."""
        self.conteudo.visible = True
        self.conteudo.opacity = 1

    def esconder(self):
        """Esconde o container principal (igual original)."""
        self.conteudo.opacity = 0
        self.conteudo.visible = False

    def atualizar_tamanho(self, nova_largura, nova_altura):
        """Atualiza tamanhos quando a janela muda (igual original)."""
        self.largura_form = nova_largura
        self.altura_tela = nova_altura
        largura_campo = min(320, nova_largura - 60)

        self.conteudo.width = nova_largura
        self.conteudo.height = nova_altura
        self.conteudo_login.width = nova_largura
        self.conteudo_login.height = nova_altura
        self.conteudo_registro.width = nova_largura
        self.conteudo_registro.height = nova_altura

        self.campo_email_login.width = largura_campo
        self.campo_senha_login.width = largura_campo
        self.campo_nome_registro.width = largura_campo
        self.campo_email_registro.width = largura_campo
        self.campo_senha_registro.width = largura_campo
        self.campo_confirma_senha.width = largura_campo
        self.campo_pergunta_seguranca.width = largura_campo
        self.campo_resposta_seguranca.width = largura_campo

    def _limpar_erros(self):
        self.txt_erro_login.visible = False
        self.txt_erro_registro.visible = False

    # ============================================
    # LOGIN E REGISTRO
    # ============================================

    def _fazer_login(self):
        """Processa o login."""
        email = self.campo_email_login.value.strip()
        senha = self.campo_senha_login.value

        resultado = self.auth_service.login(email, senha)

        if resultado["sucesso"]:
            self._mostrar_sucesso(f"Bem-vindo, {resultado['usuario'].nome}!")
            if self.on_login_sucesso:
                self.on_login_sucesso(resultado["usuario"])
        else:
            self.txt_erro_login.value = resultado["erro"]
            self.txt_erro_login.visible = True
            self.root_page.update()

    def _fazer_registro(self):
        """Processa o registro."""
        nome = self.campo_nome_registro.value
        email = self.campo_email_registro.value
        senha = self.campo_senha_registro.value
        confirma = self.campo_confirma_senha.value
        pergunta = self.campo_pergunta_seguranca.value
        resposta = self.campo_resposta_seguranca.value

        resultado = self.auth_service.registrar(
            nome, email, senha, confirma, pergunta, resposta
        )

        if resultado["sucesso"]:
            self._mostrar_sucesso(f"Conta criada! Bem-vindo, {nome}!")
            if self.on_login_sucesso:
                self.on_login_sucesso(resultado["usuario"])
        else:
            self.txt_erro_registro.value = resultado["erro"]
            self.txt_erro_registro.visible = True
            self.root_page.update()

    def _mostrar_sucesso(self, mensagem: str):
        """Mostra snackbar de sucesso."""
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

    # ============================================
    # RECUPERAÇÃO DE SENHA
    # ============================================

    def _abrir_dialog_recuperar_senha(self):
        """Abre o dialog de recuperação de senha."""
        campo_email = ft.TextField(
            label="Seu e-mail cadastrado",
            prefix_icon=ft.Icons.EMAIL,
            border=ft.InputBorder.UNDERLINE,
            width=360,
        )
        campo_pergunta = ft.Text(
            "", size=14, weight=ft.FontWeight.W_500,
            color=self.cor_primaria, visible=False
        )
        campo_resposta = ft.TextField(
            label="Resposta da pergunta de segurança",
            prefix_icon=ft.Icons.QUESTION_ANSWER,
            border=ft.InputBorder.UNDERLINE,
            width=360,
            visible=False,
        )
        txt_erro = ft.Text("", color=ft.Colors.ERROR, size=12, visible=False)

        def verificar_email(e):
            email = campo_email.value.strip()
            if not email:
                txt_erro.value = "Digite seu email"
                txt_erro.visible = True
                dialog.update()
                return

            usuario = self.auth_service.repo.buscar_por_email(email)
            if not usuario:
                txt_erro.value = "Email não encontrado"
                txt_erro.visible = True
                dialog.update()
                return

            if not usuario.pergunta_seguranca:
                txt_erro.value = "Usuário sem pergunta de segurança"
                txt_erro.visible = True
                dialog.update()
                return

            campo_pergunta.value = f"🔒 {usuario.pergunta_seguranca}"
            campo_pergunta.visible = True
            campo_resposta.visible = True
            txt_erro.visible = False

            dialog.content = ft.Column([
                ft.Text("Responda a pergunta para continuar:", size=13),
                campo_email,
                ft.Container(height=10),
                campo_pergunta,
                ft.Container(height=5),
                campo_resposta,
                txt_erro,
            ], tight=True, spacing=0)

            dialog.actions = [
                ft.TextButton("Cancelar", on_click=lambda e: fechar()),
                ft.FilledButton(
                    "Verificar",
                    icon=ft.Icons.CHECK,
                    on_click=lambda e: verificar_resposta(),
                    bgcolor=self.cor_primaria,
                    color=self.cor_texto_botao,
                ),
            ]
            dialog.update()

        def verificar_resposta():
            email = campo_email.value.strip()
            resposta = campo_resposta.value

            resultado = self.auth_service.verificar_pergunta_seguranca(email, resposta)
            if not resultado["sucesso"]:
                txt_erro.value = resultado["erro"]
                txt_erro.visible = True
                dialog.update()
                return

            dialog.open = False
            dialog.update()
            self._abrir_dialog_nova_senha(email, resposta)

        def fechar():
            dialog.open = False
            self.root_page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.LOCK_RESET, color=self.cor_primaria, size=24),
                ft.Text("Recuperar Senha"),
            ], spacing=10),
            content=ft.Column([
                ft.Text("Digite seu email para continuar:", size=13),
                campo_email,
                ft.Container(height=10),
                campo_pergunta,
                ft.Container(height=5),
                campo_resposta,
                txt_erro,
            ], tight=True, spacing=0),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: fechar()),
                ft.FilledButton(
                    "Verificar",
                    icon=ft.Icons.SEARCH,
                    on_click=verificar_email,
                    bgcolor=self.cor_primaria,
                    color=self.cor_texto_botao,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.root_page.overlay.append(dialog)
        dialog.open = True
        self.root_page.update()

    def _abrir_dialog_nova_senha(self, email: str, resposta: str):
        """Abre o dialog para criar nova senha."""
        campo_nova = ft.TextField(
            label="Nova senha",
            prefix_icon=ft.Icons.LOCK,
            password=True,
            can_reveal_password=True,
            border=ft.InputBorder.UNDERLINE,
            width=360,
        )
        campo_confirma = ft.TextField(
            label="Confirmar nova senha",
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            password=True,
            can_reveal_password=True,
            border=ft.InputBorder.UNDERLINE,
            width=360,
        )
        txt_erro = ft.Text("", color=ft.Colors.ERROR, size=12, visible=False)

        def salvar():
            resultado = self.auth_service.redefinir_senha(
                email, resposta, campo_nova.value, campo_confirma.value
            )
            if resultado["sucesso"]:
                dialog.open = False
                self.root_page.update()
                self._mostrar_sucesso("Senha redefinida! Faça login com a nova senha.")
            else:
                txt_erro.value = resultado["erro"]
                txt_erro.visible = True
                dialog.update()

        def fechar():
            dialog.open = False
            self.root_page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.KEY, color=self.cor_primaria, size=24),
                ft.Text("Criar Nova Senha"),
            ], spacing=10),
            content=ft.Column([
                ft.Text("Digite sua nova senha:", size=13),
                ft.Container(height=10),
                campo_nova,
                campo_confirma,
                txt_erro,
            ], tight=True, spacing=0),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: fechar()),
                ft.FilledButton(
                    "Salvar",
                    icon=ft.Icons.SAVE,
                    on_click=lambda e: salvar(),
                    bgcolor=self.cor_primaria,
                    color=self.cor_texto_botao,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.root_page.overlay.append(dialog)
        dialog.open = True
        self.root_page.update()