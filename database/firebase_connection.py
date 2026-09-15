import os
import sys
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore
from utils.logger import log


def inicializar_firebase():
    """
    🌐 Se estiver na nuvem (Render): lê das variáveis de ambiente
    💻 Se estiver no PC: lê do arquivo serviceAccountKey.json (IGUAL ANTES!)
    """

    # ──────────────────────────────────────────────────────
    # 🌐 AMBIENTE NA NUVEM (Render)
    # ──────────────────────────────────────────────────────
    if os.getenv("FIREBASE_PROJECT_ID"):
        log("☁️ Ambiente de nuvem detectado — usando variáveis de ambiente")

        firebase_config = {
            "type": os.getenv("FIREBASE_TYPE"),
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n"),
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.getenv("FIREBASE_CLIENT_ID"),
            "auth_uri": os.getenv("FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"),
            "token_uri": os.getenv("FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token"),
            "auth_provider_x509_cert_url": os.getenv("FIREBASE_CERT_URL",
                                                     "https://www.googleapis.com/oauth2/v1/certs"),
            "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL"),
        }

        cred = credentials.Certificate(firebase_config)

    # ──────────────────────────────────────────────────────
    # 💻 AMBIENTE LOCAL (seu computador) — IGUALZINHO ANTES!
    # ──────────────────────────────────────────────────────
    else:
        log("💻 Ambiente local detectado — buscando serviceAccountKey.json")

        # Procura a chave nos mesmos locais de antes
        caminhos = [
            Path(__file__).parent.parent / "serviceAccountKey.json",
            Path.cwd() / "serviceAccountKey.json",
            Path(__file__).parent.parent / "config" / "serviceAccountKey.json",
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

        log(f"🔑 Chave encontrada em: {caminho_chave}")
        cred = credentials.Certificate(str(caminho_chave))

    # ──────────────────────────────────────────────────────
    # 🔌 Inicializa a conexão
    # ──────────────────────────────────────────────────────
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    log("✅ Firebase inicializado com sucesso!")
    return db


# Mantive a função init_firebase() para não quebrar o main.py
def init_firebase():
    return inicializar_firebase()