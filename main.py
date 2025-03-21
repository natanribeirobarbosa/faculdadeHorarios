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

# Rota para a interface de download
@app.route('/grades', methods=['GET'])
def grades():
    return render_template('grades.html')

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
        user_ref = db.collection("users").document(user_code)
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
 # Função que retorna informações básicas do usuário

@app.route('/user/<user_id>', methods=['GET'])
def get_user_data(user_id):
    try:
        # Acessa o documento do usuário no Firestore
        user_ref = db.collection('users').document(user_id)

        user_doc = user_ref.get()
        print(user_id)
        if user_doc.exists:
            user_data = user_doc.to_dict()  # Obtém os dados do usuário como um dicionário
            
            # Monta o objeto de resposta inicial
            response = {
                'success': True,
                'user': {
                    'nome': user_data.get('nome', '?'),
                    'cargo': user_data.get('cargo', 'none')
                }
            }

            # Se o usuário for professor, buscar as licenciaturas e disciplinas
            if user_data.get('cargo', '').lower() == 'professor':
                licenciaturas_refs = user_data.get('licenciaturas', [])

                print('LICENCIATURAS:', licenciaturas_refs)  # Debug

                if isinstance(licenciaturas_refs, list):
                    licenciaturas = set()  # Usar um conjunto para evitar duplicatas

                    for curso_ref in licenciaturas_refs:
                        # Verifica se curso_ref é uma referência válida
                        if isinstance(curso_ref, firestore.DocumentReference):
                            curso_doc = curso_ref.get()

                            if curso_doc and curso_doc.exists:  # Certifica que curso_doc existe
                                curso_data = curso_doc.to_dict() or {}  # Garante que curso_data seja um dicionário

                                nome_disciplina = curso_data.get('nome')
                                if nome_disciplina:  # Verifica se o nome não é None ou vazio
                                    licenciaturas.add(nome_disciplina)  # Adiciona ao set

                    response['user']['disciplinas'] = list(licenciaturas)  # Converte para lista
            
            return jsonify(response)
        
        else:
            return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404

    except Exception as e:
        print("Erro ao carregar dados do usuário:", str(e))  # Debug no terminal
        return jsonify({'success': False, 'message': f"Erro ao carregar dados do usuário: {str(e)}"}), 500


# Função que retorna todos os usuários separados por cargos
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

        # Verifica se o usuário é admin
        is_admin = (cargo == "admin")

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

            # Se o usuário não for admin, não mostrar os IDs dos outros usuários
            user_data_obj = {
                "id": doc.id if is_admin else None,  # Esconde o ID se não for admin
                "nome": user_info.get("nome", "?")
            }

            if user_role in users_by_cargo:
                users_by_cargo[user_role].append(user_data_obj)

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
                "disciplinas": disciplinas_lista  # Retorna os dados das disciplinas com ID
            })

        return jsonify({"success": True, "cursos": cursos_list})

    except Exception as e:
        print("Erro ao buscar cursos:", str(e))  # Log no console
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/allprofessorcourses/<user_id>', methods=['GET'])
def allprofessorcourses(user_id):
    print('Iniciando a requisição...')
    try:
        # Obtém os dados do usuário pelo ID
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404

        user_data = user_doc.to_dict()
        cargo_usuario = user_data.get('cargo', 'user')  # Define 'user' como padrão se não houver cargo

        # Garantir que só um professor tenha acesso a essa rota
        if cargo_usuario != "professor":
            return jsonify({"success": False, "message": "Acesso negado, apenas professores podem visualizar cursos."}), 403

        # Busca as licenciaturas do professor
        licenciaturas_ref = user_data.get('licenciaturas', [])
        
       
        disciplinas_separadas = []

        for licenciatura_ref in licenciaturas_ref:
            # Verifica se licenciatura_ref é um DocumentReference
            if isinstance(licenciatura_ref, firestore.DocumentReference):
                curso_doc = licenciatura_ref.get()

                if curso_doc.exists:
                    curso_data = curso_doc.to_dict()
                    curso_id = curso_doc.id

                    # Pega as disciplinas do curso
                    disciplinas_lista = curso_data.get('disciplinas', [])
                    #print(disciplinas_lista)
                    # Adiciona as disciplinas separadas
                    for disciplina_ref in disciplinas_lista:
                      if isinstance(disciplina_ref, firestore.DocumentReference):
                        disciplina_doc = disciplina_ref.get()
                        if disciplina_doc.exists:
                            # Converte o DocumentSnapshot em um dicionário
                            disciplina_data = disciplina_doc.to_dict()

                            # Agora você pode acessar o campo 'nome' do dicionário
                            nome_disciplina = disciplina_data.get('nome', 'Nome não disponível')
                            carga = disciplina_data.get('carga', 'Nome não disponível')
                            modalidade = disciplina_data.get('modalidade', 'modalidade não disponível')

                            # Adiciona a disciplina à lista com o campo 'nome'
                            disciplinas_separadas.append({
                                'nome': nome_disciplina,
                                'carga': carga,
                                'modalidade': modalidade
                            })

                

        # Retorna os cursos e as disciplinas separadas
        return jsonify({
            "success": True,
          
            "disciplinas": disciplinas_separadas  # Lista separada com todas as disciplinas de todos os cursos
        })

    except Exception as e:
        print("Erro ao buscar cursos:", str(e))  # Log no console
        return jsonify({"success": False, "message": str(e)}), 500
@app.route('/adcionarlicenciatura', methods=['POST'])
def adcionarlicenciatura():
    try:
        data = request.get_json()
        user_id = data.get("userId")
        lic_id = data.get("licenciatura")  # ID da licenciatura

        if not all([user_id, lic_id]):
            return jsonify({"success": False, "message": "Dados incompletos"}), 400
        
        # Verifica se o usuário tem permissão de admin
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()

        if not user_doc.exists or user_doc.to_dict().get("cargo") != "professor":
            return jsonify({"success": False, "message": "Usuário sem permissão"}), 403
        
        # Obtém a referência do documento da licenciatura
        lic_ref = db.document(f'cursos/{lic_id}')  # Criando referência ao documento

        # Obtém a lista atual de licenciaturas do usuário
        user_data = user_doc.to_dict()
        licenciaturas = user_data.get("licenciaturas", [])

        # Verifica se a referência já está na lista
        if lic_ref not in licenciaturas:
            licenciaturas.append(lic_ref)
            user_ref.update({"licenciaturas": licenciaturas})
        
        return jsonify({"success": True, "message": "Licenciatura adicionada com sucesso"})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500





@app.route('/addDiscipline', methods=['POST'])
def adicionar_disciplina():
    try:
        data = request.get_json()
        user_id = data.get("userId")
        nome = data.get("nome")
        carga_horaria = data.get("carga")
        modalidade = data.get("modalidade")
        cursos = data.get("cursos")  # Agora é uma lista de IDs de cursos

        if not all([user_id, nome, carga_horaria, modalidade, cursos]):
            return jsonify({"success": False, "message": "Dados incompletos"}), 400

        if not isinstance(cursos, list):
            return jsonify({"success": False, "message": "O campo 'cursos' deve ser uma lista"}), 400

        # Verifica se o usuário tem permissão de admin
        user_doc = db.collection("users").document(user_id).get()
        if not user_doc.exists or user_doc.to_dict().get("cargo") != "admin":
            return jsonify({"success": False, "message": "Usuário sem permissão"}), 403

        # Gerando um identificador único para a disciplina
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

        # Adiciona a disciplina a todos os cursos especificados
        for curso_id in cursos:
            curso_ref = db.collection("cursos").document(curso_id)
            
            if curso_ref.get().exists:  # Verifica se o curso existe antes de atualizar
                curso_ref.update({
                    "disciplinas": firestore.ArrayUnion([disciplina_ref])
                })

        return jsonify({"success": True, "message": "Disciplina adicionada com sucesso", "id": disciplina_id})

    except Exception as e:
        print("Erro ao adicionar disciplina:", str(e))
        return jsonify({"success": False, "message": str(e)}), 500
    


@app.route('/deleteDiscipline', methods=['DELETE'])
def deletar_disciplina():
    try:
        data = request.get_json()
        user_id = data.get("userId")
        cursos = data.get("cursos")  # Deve ser uma lista
        disciplina_id = str(data.get("disciplinaId")).strip()

        # Verifica se `cursos` realmente é uma lista
        if not isinstance(cursos, list):
            return jsonify({"success": False, "message": "Formato inválido para cursos"}), 400

        if not all([user_id, disciplina_id, cursos]):
            return jsonify({"success": False, "message": "Dados incompletos"}), 400

        # Verifica usuário e permissões
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return jsonify({"success": False, "message": "Usuário não encontrado"}), 403

        user_data = user_doc.to_dict()
        cargo = user_data.get("cargo", "").lower()

        if cargo != "admin":
            return jsonify({"success": False, "message": "Usuário sem permissão"}), 403

        # Referência da disciplina
        disciplina_ref = db.collection("disciplinas").document(disciplina_id)

        # Verifica se a disciplina existe
        disciplina_doc = disciplina_ref.get()
        if not disciplina_doc.exists:
            return jsonify({"success": False, "message": "Disciplina não encontrada"}), 404

        # Certifica que os IDs dos cursos são strings corretamente formatadas
        cursos = [str(curso).strip() for curso in cursos]

        # Remove a disciplina de todos os cursos fornecidos
        for curso_id in cursos:
            curso_ref = db.collection("cursos").document(curso_id)
            curso_doc = curso_ref.get()

            if curso_doc.exists:
                curso_data = curso_doc.to_dict()
                disciplinas = curso_data.get("disciplinas", [])

                # Verifica se a disciplina está no curso antes de remover
                if disciplina_ref in disciplinas:
                    curso_ref.update({
                        "disciplinas": firestore.ArrayRemove([disciplina_ref])
                    })
                    print(f"Disciplina {disciplina_id} removida do curso {curso_id}")
                else:
                    print(f"A disciplina {disciplina_id} não está no curso {curso_id}, ignorando.")
            else:
                print(f"Curso {curso_id} não encontrado e não foi atualizado.")

        # Exclui a disciplina após removê-la dos cursos
        disciplina_ref.delete()

        return jsonify({"success": True, "message": "Disciplina removida de todos os cursos e deletada com sucesso"})

    except Exception as e:
        print("Erro ao deletar disciplina:", str(e))
        return jsonify({"success": False, "message": str(e)}), 500


# Tratamento de erro 404
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Rota não encontrada. Use uma das rotas disponíveis."}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)