from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore

# Inicializar o Firebase
cred = credentials.Certificate('./horarios-e6e7e-firebase-adminsdk-fbsvc-13e0648b7e.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas as rotas

# Rota principal para a interface web
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# Rota para adicionar professor
@app.route('/add_professor', methods=['POST'])
def add_professor():
    data = request.get_json()
    professor_ref = db.collection("professores").add(data)
    return jsonify({"message": "Professor cadastrado com sucesso!", "id": professor_ref[1].id})

# Rota para adicionar matéria
@app.route('/add_materia', methods=['POST'])
def add_materia():
    data = request.get_json()
    materia_ref = db.collection("materias").add(data)
    return jsonify({"message": "Matéria cadastrada com sucesso!", "id": materia_ref[1].id})

# Rota para listar professores
@app.route('/listar_professores', methods=['GET'])
def listar_professores():
    professores = db.collection("professores").stream()
    professores_lista = [{"id": prof.id, **prof.to_dict()} for prof in professores]
    return jsonify({"professores": professores_lista})

# Rota para listar matérias
@app.route('/listar_materias', methods=['GET'])
def listar_materias():
    materias = db.collection("materias").stream()
    materias_lista = [{"id": mat.id, **mat.to_dict()} for mat in materias]
    return jsonify({"materias": materias_lista})

# Rota para remover professor
@app.route('/remover_professor/<string:professor_id>', methods=['DELETE'])
def remover_professor(professor_id):
    db.collection("professores").document(professor_id).delete()
    return jsonify({"message": "Professor removido com sucesso!"})

# Rota para remover matéria
@app.route('/remover_materia/<string:materia_id>', methods=['DELETE'])
def remover_materia(materia_id):
    db.collection("materias").document(materia_id).delete()
    return jsonify({"message": "Matéria removida com sucesso!"})

# Rota para limpar horário de uma matéria
@app.route('/limpar_horario/<string:materia_id>', methods=['PUT'])
def limpar_horario(materia_id):
    db.collection("materias").document(materia_id).update({"horario": None})
    return jsonify({"message": "Horário da matéria removido com sucesso!"})

# Tratamento de erro 404
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Rota não encontrada. Use uma das rotas disponíveis."}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
