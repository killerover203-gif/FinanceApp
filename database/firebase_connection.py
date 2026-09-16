import os
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore
from utils.logger import log


def inicializar_firebase():
    """
    🌐 Render → usa variáveis de ambiente
    💻 PC → usa arquivo serviceAccountKey.json
    """

    # ──────────────────────────────────────────────────────
    # 🌐 AMBIENTE NA NUVEM (Render)
    # ──────────────────────────────────────────────────────
    # Verifica de forma GARANTIDA se TEM as variáveis
    tipo = os.getenv("FIREBASE_TYPE")
    projeto_id = os.getenv("FIREBASE_PROJECT_ID")

    if tipo and projeto_id:
        log("☁️ AMBIENTE DE NUVEM DETECTADO — usando variáveis do Render")

        firebase_config = {
            "type": tipo,
            "project_id": projeto_id,
            "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID", ""),
            "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n"),
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL", ""),
            "client_id": os.getenv("FIREBASE_CLIENT_ID", ""),
            "auth_uri": os.getenv("FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"),
            "token_uri": os.getenv("FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token"),
            "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL",
                                                     "https://www.googleapis.com/oauth2/v1/certs"),
            "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL", ""),
        }

        cred = credentials.Certificate(firebase_config)

    # ──────────────────────────────────────────────────────
    # 💻 AMBIENTE LOCAL (seu PC)
    # ──────────────────────────────────────────────────────
    else:
        log("💻 AMBIENTE LOCAL — buscando serviceAccountKey.json")

        caminhos = [
            Path(__file__).parent.parent / "serviceAccountKey.json",
            Path.cwd() / "serviceAccountKey.json",
        ]

        caminho_chave = None
        for caminho in caminhos:
            if caminho.exists():
                caminho_chave = caminho
                break

        if not caminho_chave:
            raise FileNotFoundError(
                "🔑 serviceAccountKey.json não encontrado!\n"
                "Coloque na pasta raiz do projeto."
            )

        log(f"🔑 Chave encontrada: {caminho_chave}")
        cred = credentials.Certificate(str(caminho_chave))

    # ──────────────────────────────────────────────────────
    # 🔌 Inicializar
    # ──────────────────────────────────────────────────────
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    log("✅ Firebase conectado com SUCESSO!")
    return db


# Compatibilidade com o resto do código
def init_firebase():
    return inicializar_firebase()


get_db = inicializar_firebase