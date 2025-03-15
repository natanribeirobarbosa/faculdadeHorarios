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

#edita nome
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


#adiciona usuarios
@app.route('/addUser', methods=['POST'])
def add_user():
    try:
        data = request.get_json()
        nome = data.get("nome")
        cargo = data.get("cargo", '')  # Cargo pode ser vazio
        user_id = data.get("userId")  # ID do usuário para autenticação

        if not nome or not user_id:
            return jsonify({"success": False, "error": "Nome e userId são obrigatórios"}), 400
        
        # Gerando um identificador único
        while True:
            user_code = str(random.randint(1000000, 9999999))
            user_ref = db.collection("users").document(user_code)
            
            if not user_ref.get().exists:  # Verifica se já existe no Firestore
                break  # Sai do loop se o código for único

        # Criando um novo usuário no Firestore
        user_ref = db.collection("users").document('999991')
        user_ref.set({
            "nome": nome,
            "cargo": cargo,

        })

        return jsonify({"success": True, "userCode": user_code}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

#rota deletar usuario
@app.route("/deleteUser", methods=["POST"])
def deleteUser():
    data = request.json
    user_id = data.get("userId")
    user_deleted = data.get("id")   

    if not user_id:
        return jsonify({"success": False, "message": "Código inválido!"}), 400

     
    user_ref = db.collection("users").document(str(user_id))
    user_doc = user_ref.get()
     
     # 2️⃣ Buscar usuário no Firestore
    user_ref2 = db.collection("users").document(str(user_deleted))
    user_doc2 = user_ref2.get()

    if not user_doc.exists or user_doc.to_dict().get("cargo") != "admin" or not user_doc2.exists:
        return jsonify({"success": False, "message": "Erro de validação!"}), 403

    db.collection("users").document(user_deleted).delete()
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
    
#função que retorna informações basicas do usuario
@app.route('/user/<user_id>', methods=['GET'])
def get_user_data(user_id):
    try:
        # Acessa o documento do usuário no Firestore
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if user_doc.exists:
            user_data = user_doc.to_dict()  # Obtém os dados do usuário como um dicionário
            return jsonify({
                'success': True,
                'user': {
                    'nome': user_data.get('nome', '?'),  # Evita erro se o campo 'nome' não existir
                    'cargo': user_data.get('cargo', 'none'),  # Evita erro se o campo 'cargo' não existir
                    'licenciaturas': user_data.get('licenciaturas', "undefined")
                }
            })
        else:
            return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


#função que retorna todos os usuarios separados por cargos
@app.route('/allusers/<user_id>', methods=['GET'])
def get_all_users(user_id):
    try:
        # Obtém os dados do usuário pelo ID
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()

        if not user_doc.exists:
            return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404

        user_data = user_doc.to_dict()
        cargo = user_data.get('cargo', 'user')  # Define 'user' como padrão se não houver cargo
        
        # Busca todos os usuários agrupados por cargo
        users_by_cargo = {
            "admin": [],
            "professor": [],
            "coordenador": [],
            "user": []
        }

        users_ref = db.collection('users').stream()
        for doc in users_ref:
            user_info = doc.to_dict()
            user_role = user_info.get("cargo", "user")
            
            if user_role in users_by_cargo:
                users_by_cargo[user_role].append({
                    "id": doc.id,
                    "nome": user_info.get("nome", "?")
                })

        return jsonify({
            'success': True,
            'user': {
                'nome': user_data.get('nome', '?'),
                'cargo': cargo,
                'users': {
                    'users_by_cargo': users_by_cargo
                }
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


#função que retorna a tabela completa de usuarios
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


# Função que retorna todos os cursos
@app.route('/allcourses', methods=['GET'])
def get_all_courses():
    try:
        # Referência à coleção "cursos" no Firestore
        cursos_ref = db.collection('cursos')
        cursos = cursos_ref.get()
        
        cursos_list = []

        for curso in cursos:
            curso_data = curso.to_dict()
            
            if not curso_data:
                continue  # Pula cursos vazios
            
            # Buscar dados das disciplinas referenciadas
            disciplinas_lista = []
            for ref in curso_data.get("disciplinas", []):
                if isinstance(ref, firestore.DocumentReference):  # Garante que é uma referência válida
                    disciplina_doc = ref.get()
                    if disciplina_doc.exists:
                        disciplina_data = disciplina_doc.to_dict()
                        disciplina_data["id"] = disciplina_doc.id  # Adiciona o ID da disciplina
                        disciplinas_lista.append(disciplina_data)  # Converte em JSON
            
            cursos_list.append({
                "id": curso.id,  # ID do curso
                "nome": curso_data.get("nome", "Desconhecido"),
                "carga": curso_data.get("carga_horaria", "Desconhecido"),
                "modalidade": curso_data.get("modalidade", "Não informado"),
                "disciplinas": disciplinas_lista  # Retorna os dados das disciplinas com ID
            })

        return jsonify({"success": True, "cursos": cursos_list})

    except Exception as e:
        print("Erro ao buscar cursos:", str(e))  # Log no console
        return jsonify({"success": False, "message": str(e)}), 500

#adiciona novas disciplinas
@app.route('/addDiscipline', methods=['POST'])
def adicionar_disciplina():
    try:
        data = request.get_json()
        user_id = data.get("userId")
        nome = data.get("nome")
        carga_horaria = data.get("carga")
        modalidade = data.get("modalidade")
        curso = data.get("curso")

        if not all([user_id, nome, carga_horaria, modalidade]):
            return jsonify({"success": False, "message": "Dados incompletos"}), 400

        # Verifica se o usuário tem permissão de admin
        user_doc = db.collection("users").document(user_id).get()
        if not user_doc.exists or user_doc.to_dict().get("cargo") != "admin":
            return jsonify({"success": False, "message": "Usuário sem permissão"}), 403

        # Gerando um identificador único
        while True:
            disciplina_id = str(random.randint(1000, 9999))
            disciplina_ref = db.collection("disciplinas").document(disciplina_id)
            
            if not disciplina_ref.get().exists:  # Verifica se já existe no Firestore
                break  # Sai do loop se o código for único


        # Salva a nova disciplina no Firestore
        disciplina_ref.set({
            "nome": nome,
            "carga": carga_horaria,
            "modalidade": modalidade
        })

        # Referência do documento "engenharia de software" dentro da coleção "cursos"
        curso_ref = db.collection("cursos").document(curso)

        # Atualiza o campo "disciplinas" no curso, adicionando a referência à nova disciplina
        curso_ref.update({
            "disciplinas": firestore.ArrayUnion([disciplina_ref])
        })

        return jsonify({"success": True, "message": "Disciplina adicionada com sucesso", "id": disciplina_id})

    except Exception as e:
        print("Erro ao adicionar disciplina:", str(e))
        return jsonify({"success": False, "message": str(e)}), 500

# Deleta disciplina
@app.route('/deleteDiscipline', methods=['DELETE'])
def deletar_disciplina():
    try:
        data = request.get_json()
        user_id = data.get("userId")
        curso = data.get("curso")
        
        disciplina_id = data.get("disciplinaId")

        if not all([user_id, disciplina_id]):
            return jsonify({"success": False, "message": "Dados incompletos"}), 400

        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        
        if not user_doc.exists:
            return jsonify({"success": False, "message": "Usuário não encontrado"}), 403



        user_data = user_doc.to_dict()  # Converte o documento em dicionário
        cargo = user_data.get("cargo", "").lower()  # Evita erro de None e padroniza para minúsculas

        print("Usuário existe:", user_doc.exists)
        print("Cargo do usuário:", cargo)
        print("ID do usuário:", user_id)

        # Verifica se o usuário tem permissão de admin
        if cargo != "admin":
            return jsonify({"success": False, "message": "Usuário sem permissão"}), 403

        # Referência da disciplina
        disciplina_ref = db.collection("disciplinas").document(disciplina_id)

        # Verifica se a disciplina existe
        if not disciplina_ref.get().exists:
            return jsonify({"success": False, "message": "Disciplina não encontrada"}), 404

        # Remove a disciplina do curso "engenharia de software"
        curso_ref = db.collection("cursos").document(curso)
        curso_ref.update({
            "disciplinas": firestore.ArrayRemove([disciplina_ref])
        })

        # Exclui a disciplina do Firestore
        disciplina_ref.delete()

        return jsonify({"success": True, "message": "Disciplina removida com sucesso"})

    except Exception as e:
        print("Erro ao deletar disciplina:", str(e))
        return jsonify({"success": False, "message": str(e)}), 500


# Tratamento de erro 404
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Rota não encontrada. Use uma das rotas disponíveis."}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)