from flask import Flask, render_template, request, jsonify, Blueprint
from firebase_admin import firestore
from config.firebase_config import db  # Importando a configuração do Firestore

# Criação do Blueprint para usuários
user_bp = Blueprint('user', __name__)

# Rota principal para a interface web
@user_bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# Rota para a interface dashboard
@user_bp.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template('dashboard.html')


@user_bp.route("/login", methods=["POST"])
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




# Rota para a interface de download
@user_bp.route('/grades', methods=['GET'])
def grades():
    return render_template('grades.html')

# Edita nome
@user_bp.route("/editname", methods=["POST"])
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

# Rota para obter dados do usuário
@user_bp.route('/user/<user_id>', methods=['GET'])
def get_user_data(user_id):
    try:
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if user_doc.exists:
            user_data = user_doc.to_dict()
            
            response = {
                'success': True,
                'user': {
                    'nome': user_data.get('nome', '?'),
                    'cargo': user_data.get('cargo', 'none')
                }
            }

            if user_data.get('cargo', '').lower() == 'professor':
                licenciaturas_refs = user_data.get('licenciaturas', [])
                candidaturas_refs = user_data.get('candidaturas', [])  # Adiciona a busca pelas candidaturas
                
                if isinstance(licenciaturas_refs, list):
                    licenciaturas = set()

                    for curso_ref in licenciaturas_refs:
                        if isinstance(curso_ref, firestore.DocumentReference):
                            curso_doc = curso_ref.get()
                            if curso_doc and curso_doc.exists:
                                curso_data = curso_doc.to_dict() or {}
                                nome_disciplina = curso_data.get('nome')
                                if nome_disciplina:
                                    licenciaturas.add(nome_disciplina)

                    response['user']['disciplinas'] = list(licenciaturas)
                
                # Agora, também inclui as candidaturas
                if isinstance(candidaturas_refs, list):
                    candidaturas = set()

                    for candidatura_ref in candidaturas_refs:
                        if isinstance(candidatura_ref, firestore.DocumentReference):
                            disciplina_doc = candidatura_ref.get()  # Aqui resolvemos a referência da candidatura
                            if disciplina_doc and disciplina_doc.exists:
                                disciplina_data = disciplina_doc.to_dict() or {}
                                nome_disciplina = disciplina_data.get('nome')
                                if nome_disciplina:
                                    candidaturas.add(nome_disciplina)

                    response['user']['candidaturas'] = list(candidaturas)
            
            return jsonify(response)
        
        else:
            return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404

    except Exception as e:
        return jsonify({'success': False, 'message': f"Erro ao carregar dados do usuário: {str(e)}"}), 500



# Rota para todos os cursos
@user_bp.route('/allcourses', methods=['GET'])
def get_all_courses():
    try:
        cursos_ref = db.collection('cursos')
        cursos = cursos_ref.get()
        
        cursos_list = []

        for curso in cursos:
            curso_data = curso.to_dict()
            if not curso_data:
                continue

            disciplinas_lista = []
            for ref in curso_data.get("disciplinas", []):
                if isinstance(ref, firestore.DocumentReference):
                    disciplina_doc = ref.get()
                    if disciplina_doc.exists:
                        disciplina_data = disciplina_doc.to_dict()
                        disciplina_data["id"] = disciplina_doc.id
                        disciplinas_lista.append(disciplina_data)
            
            cursos_list.append({
                "id": curso.id,
                "nome": curso_data.get("nome", "Desconhecido"),
                "disciplinas": disciplinas_lista
            })

        return jsonify({"success": True, "cursos": cursos_list})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# Configurando a aplicação principal
app = Flask(__name__)

# Registrando o Blueprint
app.register_blueprint(user_bp, url_prefix='/user')

if __name__ == '__main__':
    app.run(debug=True)
