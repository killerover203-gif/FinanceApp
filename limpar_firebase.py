import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

colecoes = ["usuarios", "transacoes", "metas", "contas_previstas", "categorias"]

print("⚠️  Vai apagar TUDO!")
if input("Digite SIM para confirmar: ").strip().upper() == "SIM":
    for nome in colecoes:
        for doc in db.collection(nome).stream():
            doc.reference.delete()
        print(f"✅ {nome} apagada")
    print("\n🎉 Banco limpo!")
else:
    print("Cancelado.")