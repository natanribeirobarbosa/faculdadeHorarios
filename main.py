from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
import random


# Inicializa o Firebase apenas se ainda não estiver inicializado
if not firebase_admin._apps:
    cred = credentials.Certificate("./horarios-e6e7e-firebase-adminsdk-fbsvc-13e0648b7e.json")  # Caminho do seu arquivo JSON
    firebase_admin.initialize_app(cred)

# Inicializa o cliente do Firestore
db = firestore.client()


app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas as rotas


#------------------------------Rotas Nathan-----------------------------------------------------------------------
# Rota principal para a interface web
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


# Rota para a interface dashboard
@app.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template('dashboard.html')


@app.route("/editname", methods=["POST"])
def editName():
    data = request.json
    user_id = data.get("userId")

    if not user_id:
        return jsonify({"success": False, "message": "Código inválido!"}), 400

    # Consulta ao Firestore para verificar se o usuário existe
    user_ref = db.collection("users").document(user_id)
    user_data = user_ref.get()

    if user_data.exists:
        user_ref.update({"nome": data.get("nome")})
        return jsonify({"success": True, "message": "Nome alterado com sucesso!"})
    else:
        return jsonify({"success": False, "message": "Código inválido!"}), 401


@app.route("/addUser", methods=["POST"])
def addUser():
    data = request.json
    user_id = data.get("userId")  
    print("User ID recebido:", user_id)

    if not user_id:
        return jsonify({"success": False, "message": "Código inválido!"}), 400

     # 2️⃣ Buscar usuário no Firestore
    user_ref = db.collection("users").document(str(user_id))
    user_doc = user_ref.get()

    if not user_doc.exists or user_doc.to_dict().get("cargo") != "admin":
        return jsonify({"success": False, "message": "Apenas administradores podem cadastrar usuários!"}), 403

    # Gerando código aleatório
    codigo_aleatorio = random.randint(1000000, 9999999)
    print("Código aleatório gerado:", codigo_aleatorio)

    new_user_data = {
        'nome': data.get("nome"),
        'cargo': data.get("cargo")
    }

    # Convertendo código para string antes de salvar no Firestore
    user_ref = db.collection("users").document(str(codigo_aleatorio))
    user_ref.set(new_user_data)

    return jsonify({"success": True, "message": "Usuário cadastrado com sucesso!"}), 200



@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user_id = data.get("userId")

    if not user_id:
        return jsonify({"success": False, "message": "Código inválido!"}), 400

    # Consulta ao Firestore para verificar se o usuário existe
    user_ref = db.collection("users").document(user_id)
    user_data = user_ref.get()

    if user_data.exists:
        return jsonify({"success": True, "message": "Login bem-sucedido!"})
    else:
        return jsonify({"success": False, "message": "Código inválido!"}), 401
    

@app.route('/user/<user_id>', methods=['GET'])
def get_user_data(user_id):
    try:
        # Acessa o documento do usuário no Firestore
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()

        if user_doc.exists:
            user_data = user_doc.to_dict()  # Obtém os dados do usuário
            cargo = user_data.get('cargo', 'user')  # Defina 'user' como padrão caso não haja cargo

            return jsonify({
                'success': True,
                'user': {
                    'cargo': cargo,
                    # Adicione outras informações que quiser retornar
                    'nome': user_data.get('nome', 'N/A'),
                    'email': user_data.get('email', 'N/A'),
                    'godmode': user_data.get('godmode', False),
                    'users':get_users_by_cargo(cargo)
                }
            })

        return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


def get_users_by_cargo(model):
    try:
        # Acessa toda a coleção 'users'
        users_ref = db.collection('users')
        users_docs = users_ref.get()  # Obtém todos os documentos da coleção

        if users_docs:
            # Dicionário para armazenar os usuários por cargo
            users_by_cargo = {}

            # Itera sobre cada documento (usuário)
            for user_doc in users_docs:
                user_data = user_doc.to_dict()  # Converte cada documento para um dicionário
                cargo = user_data.get('cargo', 'user')  # Obtém o cargo, 'user' é o valor padrão

                # Cria uma lista de usuários para cada cargo
                if cargo not in users_by_cargo:
                    users_by_cargo[cargo] = []

                # Adiciona o usuário à lista do respectivo cargo
                if model == 'admin':
                    users_by_cargo[cargo].append({
                        'id': user_doc.id, 
                        'nome': user_data.get('nome', 'N/A'),
                        'email': user_data.get('email', 'N/A'),
                        'godmode': user_data.get('godmode', 'false')
                    })

                if model != 'admin':
                    users_by_cargo[cargo].append({
                        'nome': user_data.get('nome', 'N/A'),
                        'email': user_data.get('email', 'N/A'),
                    })

                


            return {'success': True, 'users_by_cargo': users_by_cargo}

        return {'success': False, 'message': 'Nenhum usuário encontrado'}

    except Exception as e:
        return {'success': False, 'message': str(e)}



#------------------rotas Moita Algumas modificadas por Nathan-kkkkkkk-------------------------------------------------------------

# Rota para adicionar professor
@app.route('/add_professor', methods=['POST'])
def add_professor():
    data = request.get_json()
    # Verifica se o nome foi enviado do front-end
    if "nome" not in data or not data["nome"].strip():
        return jsonify({"error": "O campo 'nome' é obrigatório!"}), 400

    # Gera um código aleatório de 7 dígitos
    codigo_documento = random.randint(1000000, 9999999)
    
    # Adiciona o código gerado aos dados do professor
    data["codigo_documento"] = codigo_documento
    
    # Adiciona ao Firestore
    professor_ref = db.collection("professores").add(data)

    return jsonify({
        "message": "Professor cadastrado com sucesso!",
        "id": professor_ref[1].id,
        "codigo_documento": codigo_documento
    })

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
