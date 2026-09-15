#!/usr/bin/env python3
"""
============================================================================
SCRIPT DE MIGRAÇÃO: SQLite → Firebase Firestore
============================================================================

⚠️  LEIA ANTES DE EXECUTAR:
1. Instale o firebase-admin: pip install firebase-admin
2. Coloque o arquivo serviceAccountKey.json na pasta raiz
3. Coloque o caminho correto do seu banco SQLite em DB_SQLITE_PATH
4. Execute este script APENAS UMA VEZ!
5. Recomendado: faça um backup do seu arquivo .db antes

O que este script faz:
- Lê todos os dados do seu banco SQLite antigo
- Cria os documentos correspondentes no Firestore
- Mantém os relacionamentos (mapeia IDs antigos → novos IDs)
- Preserva TODOS os seus dados históricos
============================================================================
"""

import sqlite3
import sys
import os

# ============================================
# CONFIGURAÇÕES — AJUSTE AQUI!
# ============================================
DB_SQLITE_PATH = "data/financas.db"  # Caminho do seu banco antigo
CHAVE_FIREBASE = "serviceAccountKey.json"  # Sua chave do Firebase

# ============================================
# IMPORTS
# ============================================
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except ImportError:
    print("❌ ERRO: firebase-admin não instalado!")
    print("   Execute: pip install firebase-admin")
    sys.exit(1)

# ============================================
# INICIALIZA FIREBASE
# ============================================
print("=" * 60)
print("🔌 Conectando com Firebase...")
print("=" * 60)

if not os.path.exists(CHAVE_FIREBASE):
    print(f"❌ Arquivo de chave não encontrado: {CHAVE_FIREBASE}")
    print("   Baixe-o em: Firebase Console → Configurações → Contas de Serviço")
    sys.exit(1)

cred = credentials.Certificate(CHAVE_FIREBASE)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()
print("✅ Firebase conectado!\n")

# ============================================
# CONECTA SQLITE
# ============================================
if not os.path.exists(DB_SQLITE_PATH):
    print(f"❌ Banco SQLite não encontrado: {DB_SQLITE_PATH}")
    print(f"   Verifique o caminho na variável DB_SQLITE_PATH")
    sys.exit(1)

conn = sqlite3.connect(DB_SQLITE_PATH)
conn.row_factory = sqlite3.Row
print(f"✅ SQLite conectado: {DB_SQLITE_PATH}\n")

# ============================================
# MAPEAMENTO DE IDs (antigo SQLite → novo Firestore)
# ============================================
mapa_usuarios = {}   # {id_sqlite: id_firestore}
mapa_categorias = {}  # {id_sqlite: id_firestore}
mapa_transacoes = {}
mapa_metas = {}
mapa_contas = {}

# ============================================
# 1. MIGRAR USUÁRIOS
# ============================================
print("=" * 60)
print("👤 Migrando USUÁRIOS...")
print("=" * 60)

cursor = conn.cursor()
cursor.execute("SELECT * FROM usuarios ORDER BY id")
usuarios = cursor.fetchall()

for u in usuarios:
    dados = {
        "nome": u["nome"],
        "email": u["email"].lower(),
        "senha_hash": u["senha_hash"],
        "salt": u["salt"],
        "pergunta_seguranca": u["pergunta_seguranca"],
        "resposta_hash": u["resposta_hash"],
        "resposta_salt": u["resposta_salt"],
        "criado_em": u["criado_em"],
        "id_sqlite": u["id"],  # Guarda o ID antigo para referência
    }

    doc_ref = db.collection("usuarios").document()
    doc_ref.set(dados)
    mapa_usuarios[u["id"]] = doc_ref.id
    print(f"   ✅ Usuário: {u['nome']} ({u['email']}) → ID: {doc_ref.id}")

print(f"\n📊 Total de usuários migrados: {len(usuarios)}\n")

# ============================================
# 2. MIGRAR CATEGORIAS
# ============================================
print("=" * 60)
print("🏷️  Migrando CATEGORIAS...")
print("=" * 60)

cursor.execute("SELECT * FROM categorias ORDER BY id")
categorias = cursor.fetchall()

for c in categorias:
    usuario_id_firestore = None
    if c["usuario_id"] is not None and c["usuario_id"] in mapa_usuarios:
        usuario_id_firestore = mapa_usuarios[c["usuario_id"]]

    dados = {
        "nome": c["nome"],
        "icone": c["icone"],
        "usuario_id": usuario_id_firestore,
        "id_sqlite": c["id"],
    }

    # Para categorias globais (usuario_id None), usa ID previsível
    if c["usuario_id"] is None:
        doc_id = f"global_{c['nome'].lower().replace(' ', '_')}"
        doc_ref = db.collection("categorias").document(doc_id)
        # Só cria se não existir
        if not doc_ref.get().exists:
            doc_ref.set(dados)
        else:
            print(f"   ℹ️  Categoria global já existe: {c['nome']}")
    else:
        doc_ref = db.collection("categorias").document()
        doc_ref.set(dados)

    mapa_categorias[c["id"]] = doc_ref.id
    tipo = "GLOBAL" if c["usuario_id"] is None else "USUÁRIO"
    print(f"   ✅ [{tipo}] {c['nome']} → ID: {doc_ref.id}")

print(f"\n📊 Total de categorias migradas: {len(categorias)}\n")

# ============================================
# 3. MIGRAR TRANSAÇÕES
# ============================================
print("=" * 60)
print("💰 Migrando TRANSAÇÕES...")
print("=" * 60)

cursor.execute("SELECT * FROM transacoes ORDER BY id")
transacoes = cursor.fetchall()

for i, t in enumerate(transacoes, 1):
    # Mapeia IDs
    usuario_id_firestore = mapa_usuarios.get(t["usuario_id"])
    categoria_id_firestore = None
    if t["categoria_id"] is not None:
        categoria_id_firestore = mapa_categorias.get(t["categoria_id"])

    dados = {
        "descricao": t["descricao"],
        "valor": float(t["valor"]),
        "tipo": t["tipo"],
        "data": t["data"],
        "categoria_id": categoria_id_firestore,
        "usuario_id": usuario_id_firestore,
        "id_sqlite": t["id"],
    }

    doc_ref = db.collection("transacoes").document()
    doc_ref.set(dados)
    mapa_transacoes[t["id"]] = doc_ref.id

    if i % 50 == 0 or i == len(transacoes):
        print(f"   ⏳ Progresso: {i}/{len(transacoes)} transações...")

print(f"\n📊 Total de transações migradas: {len(transacoes)}\n")

# ============================================
# 4. MIGRAR METAS
# ============================================
print("=" * 60)
print("🎯 Migrando METAS...")
print("=" * 60)

cursor.execute("SELECT * FROM metas ORDER BY id")
metas = cursor.fetchall()

for m in metas:
    usuario_id_firestore = mapa_usuarios.get(m["usuario_id"])
    categoria_id_firestore = None
    if m["categoria_id"] is not None:
        categoria_id_firestore = mapa_categorias.get(m["categoria_id"])

    dados = {
        "nome": m["nome"],
        "tipo": m["tipo"],
        "valor_alvo": float(m["valor_alvo"]),
        "categoria_id": categoria_id_firestore,
        "data_limite": m["data_limite"],
        "ativa": bool(m["ativa"]),
        "usuario_id": usuario_id_firestore,
        "id_sqlite": m["id"],
    }

    doc_ref = db.collection("metas").document()
    doc_ref.set(dados)
    mapa_metas[m["id"]] = doc_ref.id
    print(f"   ✅ Meta: {m['nome']} (R$ {m['valor_alvo']:.2f}) → ID: {doc_ref.id}")

print(f"\n📊 Total de metas migradas: {len(metas)}\n")

# ============================================
# 5. MIGRAR CONTAS PREVISTAS
# ============================================
print("=" * 60)
print("📅 Migrando CONTAS PREVISTAS...")
print("=" * 60)

cursor.execute("SELECT * FROM contas_previstas ORDER BY id")
contas = cursor.fetchall()

for c in contas:
    usuario_id_firestore = mapa_usuarios.get(c["usuario_id"])
    categoria_id_firestore = None
    if c["categoria_id"] is not None:
        categoria_id_firestore = mapa_categorias.get(c["categoria_id"])

    dados = {
        "nome": c["nome"],
        "valor": float(c["valor"]),
        "tipo": c["tipo"],
        "dia_vencimento": int(c["dia_vencimento"]),
        "categoria_id": categoria_id_firestore,
        "ativa": bool(c["ativa"]),
        "usuario_id": usuario_id_firestore,
        "id_sqlite": c["id"],
    }

    doc_ref = db.collection("contas_previstas").document()
    doc_ref.set(dados)
    mapa_contas[c["id"]] = doc_ref.id
    print(f"   ✅ Conta: {c['nome']} (dia {c['dia_vencimento']}) → ID: {doc_ref.id}")

print(f"\n📊 Total de contas previstas migradas: {len(contas)}\n")

# ============================================
# FINALIZAÇÃO
# ============================================
conn.close()

print("=" * 60)
print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
print("=" * 60)
print(f"\n📊 RESUMO:")
print(f"   👤 Usuários:        {len(usuarios)}")
print(f"   🏷️  Categorias:      {len(categorias)}")
print(f"   💰 Transações:      {len(transacoes)}")
print(f"   🎯 Metas:           {len(metas)}")
print(f"   📅 Contas previstas: {len(contas)}")
print(f"\n⚠️  PRÓXIMOS PASSOS:")
print(f"   1. Substitua os arquivos antigos pelos novos da pasta 'migracao_firebase'")
print(f"   2. Mantenha o serviceAccountKey.json na pasta raiz")
print(f"   3. Adicione serviceAccountKey.json no seu .gitignore")
print(f"   4. Execute o app normalmente: python main.py")
print(f"\n🔒 DICA DE SEGURANÇA:")
print(f"   Vá em Firestore → Regras e ajuste as permissões!")
print(f"   O modo de teste expira em 30 dias.")
print("=" * 60)
