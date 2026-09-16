import os
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore
from utils.logger import log


def inicializar_firebase():
    """
    🌐 Render → lê das variáveis de ambiente (DETECÇÃO FORÇADA)
    💻 PC → lê do arquivo serviceAccountKey.json
    """

    # ──────────────────────────────────────────────────────
    # 🌐 DETECTAÇÃO — se estamos no Render, TEM variáveis
    # ──────────────────────────────────────────────────────
    projeto_id = os.getenv("FIREBASE_PROJECT_ID")

    # ✅ SE EXISTIR projeto_id = ESTAMOS NO RENDER
    if projeto_id and len(projeto_id.strip()) > 0:
        log("☁️ RENDER DETECTADO — Usando variáveis de ambiente")

        # Monta a configuração
        config = {
            "type": os.getenv("FIREBASE_TYPE", "service_account"),
            "project_id": projeto_id.strip(),
            "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID", "").strip(),
            "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n").strip(),
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL", "").strip(),
            "client_id": os.getenv("FIREBASE_CLIENT_ID", "").strip(),
            "auth_uri": os.getenv("FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"),
            "token_uri": os.getenv("FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token"),
            "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL",
                                                     "https://www.googleapis.com/oauth2/v1/certs"),
            "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL", "").strip(),
        }

        log(f"✅ Projeto: {config['project_id']}")
        log(f"✅ Email: {config['client_email']}")
        log(f"✅ Chave privada: {'PRESENTE' if config['private_key'] else 'FALTANDO!'}")

        cred = credentials.Certificate(config)

    # ──────────────────────────────────────────────────────
    # 💻 AMBIENTE LOCAL
    # ──────────────────────────────────────────────────────
    else:
        log("💻 AMBIENTE LOCAL — Buscando serviceAccountKey.json")

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
    # 🔌 Conectar
    # ──────────────────────────────────────────────────────
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    log("✅ FIREBASE CONECTADO COM SUCESSO! 🎉")
    # ──────────────────────────────────────────────────────
    # ✅ CATEGORIAS PADRÃO — IGUAIS AO SQLite ANTIGO!
    # ──────────────────────────────────────────────────────
    # ──────────────────────────────────────────────────────
    # ✅ GARANTE que as CATEGORIAS PADRÃO EXISTAM
    # ──────────────────────────────────────────────────────
    db = firestore.client()
    log("✅ Firebase conectado com SUCESSO! 🎉")

    try:
        categorias_ref = db.collection("categorias")
        docs = list(categorias_ref.stream())

        # Lista DEFINITIVA das categorias PADRÃO
        categorias_padrao = [
            {"nome": "Alimentação", "icone": "RESTAURANT", "tipo": "despesa"},
            {"nome": "Transporte", "icone": "DIRECTIONS_CAR", "tipo": "despesa"},
            {"nome": "Moradia", "icone": "HOME", "tipo": "despesa"},
            {"nome": "Lazer", "icone": "SPORTS_ESPORTS", "tipo": "despesa"},
            {"nome": "Saúde", "icone": "LOCAL_HOSPITAL", "tipo": "despesa"},
            {"nome": "Educação", "icone": "SCHOOL", "tipo": "despesa"},
            {"nome": "Salário", "icone": "WORK", "tipo": "receita"},
            {"nome": "Investimentos", "icone": "TRENDING_UP", "tipo": "receita"},
        ]

        # Se não tem NENHUMA categoria → CRIA TODAS
        if len(docs) == 0:
            log("📂 Nenhuma categoria encontrada! Criando PADRÃO...")
            for cat in categorias_padrao:
                categorias_ref.document().set(cat)
            log("✅ 8 Categorias PADRÃO criadas com SUCESSO! 🎉")
        else:
            log(f"✅ Já existem {len(docs)} categorias — mantendo!")

    except Exception as e:
        log(f"⚠️ Erro ao verificar/criar categorias: {e}")

    return db


def init_firebase():
    return inicializar_firebase()


get_db = inicializar_firebase