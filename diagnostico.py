# diagnostico.py
"""Diagnóstico para verificar onde o banco está sendo criado."""
import sys
import os
from pathlib import Path

print("=" * 60)
print("🔍 DIAGNÓSTICO DO FINANCEAPP")
print("=" * 60)

# 1. Verifica se é executável
frozen = getattr(sys, 'frozen', False)
print(f"\n1. É executável? {frozen}")
print(f"   sys.executable: {sys.executable}")

# 2. Verifica APPDATA
appdata = os.environ.get('APPDATA')
print(f"\n2. APPDATA: {appdata}")

# 3. Define o caminho do banco
if frozen:
    base_path = Path(appdata) / 'FinanceApp'
else:
    base_path = Path(__file__).parent.resolve() / 'data'

db_file = base_path / 'financas.db'

print(f"\n3. Caminho do banco seria: {db_file}")
print(f"   Pasta base: {base_path}")

# 4. Tenta criar a pasta
try:
    base_path.mkdir(parents=True, exist_ok=True)
    print(f"\n4. ✅ Pasta criada com sucesso!")
    print(f"   Pasta existe: {base_path.exists()}")
except Exception as e:
    print(f"\n4. ❌ ERRO ao criar pasta: {e}")

# 5. Tenta criar o banco
try:
    import sqlite3

    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS teste (id INTEGER)")
    cursor.execute("INSERT INTO teste VALUES (1)")
    conn.commit()
    conn.close()

    print(f"\n5. ✅ Banco criado com sucesso!")
    print(f"   Arquivo existe: {db_file.exists()}")
    print(f"   Tamanho: {db_file.stat().st_size} bytes")
except Exception as e:
    print(f"\n5. ❌ ERRO ao criar banco: {e}")
    import traceback

    traceback.print_exc()

# 6. Lista arquivos na pasta
print(f"\n6. Arquivos na pasta {base_path}:")
if base_path.exists():
    for arquivo in base_path.iterdir():
        print(f"   - {arquivo.name} ({arquivo.stat().st_size} bytes)")
else:
    print("   ❌ Pasta não existe!")

print("\n" + "=" * 60)
input("Pressione ENTER para sair...")