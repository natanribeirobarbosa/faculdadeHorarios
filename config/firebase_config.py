import firebase_admin
from firebase_admin import credentials, firestore

# Inicializando o Firebase
cred = credentials.Certificate("./horarios-e6e7e-firebase-adminsdk-fbsvc-13e0648b7e.json")  # Caminho do seu arquivo JSON
firebase_admin.initialize_app(cred)

# Criando uma referência para o Firestore
db = firestore.client()
