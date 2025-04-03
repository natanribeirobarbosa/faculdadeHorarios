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



@user_bp.route('/grades/<course>/<id>/<user>', methods=['GET'])
def render_grades(course, id, user):
    try:
        # Buscar o curso pelo ID
        curso_ref = db.collection('cursos').document(id)
        curso_doc = curso_ref.get()

        if not curso_doc.exists:
            return jsonify({"success": False, "message": "Curso não encontrado"}), 404

        curso_data = curso_doc.to_dict()
        disciplinas_refs = curso_data.get('disciplinas', [])  # Array de referências das disciplinas

        candidatos_por_disciplina = {}

        disciplina_index = 1  # Para gerar chaves únicas

        for disciplina_ref in disciplinas_refs:
            if isinstance(disciplina_ref, firestore.DocumentReference):
                disciplina_doc = disciplina_ref.get()
                
                if disciplina_doc.exists:
                    disciplina_data = disciplina_doc.to_dict()
                    disciplina_nome = disciplina_data.get('nome', 'Disciplina desconhecida')

                    # Gerar a chave única para a disciplina
                    chave_disciplina = f"d{disciplina_index}"

                    # Lista de referências aos candidatos
                    candidatos_refs = disciplina_data.get('candidatos', [])

                    # Buscar informações reais dos candidatos
                    candidatos_info = []

                    for i, candidato_ref in enumerate(candidatos_refs, 1):
                        if isinstance(candidato_ref, firestore.DocumentReference):
                            candidato_doc = candidato_ref.get()
                            if candidato_doc.exists:
                                candidato_data = candidato_doc.to_dict()
                                candidatos_info.append({
                                    "nome": candidato_data.get('nome', 'Nome desconhecido'),
                                    "codigo": candidato_doc.id,
                                    "ref": chave_disciplina,  
                                    "chave": f"a{i}"  
                                })

                    # Adiciona a disciplina com os candidatos formatados
                    candidatos_por_disciplina[chave_disciplina] = {
                        "nome_disciplina": disciplina_nome,
                        "codigo": disciplina_doc.id,
                        "candidatos": candidatos_info,
                        "ref_disciplina": chave_disciplina  # Adiciona a referência da disciplina
                    }

                    disciplina_index += 1  # Incrementa a indexação das disciplinas

        # 🔍 Print para Debug
        print("DADOS ENVIADOS PARA O TEMPLATE:", candidatos_por_disciplina)

        return render_template('grades.html', 
                               course=course, 
                               id=id, 
                               user=user, 
                               disciplinas=candidatos_por_disciplina)

    except Exception as e:
        print(f"Erro: {str(e)}")
        return jsonify({"success": False, "message": "Erro interno no servidor"}), 500
    

@user_bp.route('/downloads', methods=['GET'])
def render_download():
    return render_template('download.html')








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

            candidaturas_refs = user_data.get('candidaturas', [])  # Garantindo que candidaturas_refs sempre tenha valor

            if user_data.get('cargo', '').lower() == 'professor':
                licenciaturas_refs = user_data.get('licenciaturas', [])
                periodos_ref = user_data.get('periodos', [])
                modalidades_ref = user_data.get('modalidades', [])
                
                if isinstance(licenciaturas_refs, list):
                    licenciaturas = set()

                    for curso_ref in licenciaturas_refs:
                        if isinstance(curso_ref, firestore.DocumentReference):
                            curso_doc = curso_ref.get()
                            if curso_doc and curso_doc.exists:
                                curso_data = curso_doc.to_dict() or {}
                                nome_disciplina = curso_data.get('nome')
                                if nome_disciplina:
                                     licenciaturas.add((curso_doc.id, nome_disciplina))  # Adiciona ID e nome

                    response['user']['licenciaturas'] = list(licenciaturas)

                    
                if isinstance(periodos_ref, list):
                    periodos = set()
                    print(periodos_ref)
                    
                    # Verificando se periodos_ref não está vazio
                    if len(periodos_ref) > 0:  
                        periodos.update(periodos_ref)

                    response['user']['periodos'] = list(periodos)  # Converte de volta para lista


                if isinstance(periodos_ref, list):
                    modalidades = set()
                
                
                # Verificando se periodos_ref não está vazio
                if len(modalidades_ref) > 0:  
                    modalidades.update(modalidades_ref)

                response['user']['modalidades'] = list(modalidades)  # Converte de volta para lista




                
            # Agora, também inclui as candidaturas (sempre verifica se candidaturas_refs foi definida)
            if isinstance(candidaturas_refs, list):
                candidaturas = []  # Alterado para lista

                for candidatura_ref in candidaturas_refs:
                    if isinstance(candidatura_ref, firestore.DocumentReference):
                        disciplina_doc = candidatura_ref.get()  # Obtém o documento da candidatura
                        if disciplina_doc and disciplina_doc.exists:
                            disciplina_data = disciplina_doc.to_dict() or {}
                            nome_disciplina = disciplina_data.get('nome')

                            if nome_disciplina:
                                candidaturas.append({
                                    "id": disciplina_doc.id,  # Agora armazenando o ID corretamente
                                    "nome": nome_disciplina
                                })

                response['user']['candidaturas'] = candidaturas  # Já está em formato de lista

            return jsonify(response)
        
        else:
            return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404

    except Exception as e:
        return jsonify({'success': False, 'message': f"Erro ao carregar dados do usuário: {str(e)}"}), 500




@user_bp.route('/allcourses', methods=['GET'])
def get_all_courses():
    try:
        print("Iniciando busca por cursos...")

        # Buscar todos os cursos
        cursos_ref = db.collection('cursos')
        cursos = cursos_ref.get()

        cursos_list = []
        print(f"Total de cursos encontrados: {len(cursos)}")

        # Criar uma lista de todas as referências de disciplinas para buscar de uma vez
        disciplinas_refs = []
        for curso in cursos:
            curso_data = curso.to_dict()
            if not curso_data:
                print(f"Curso {curso.id} sem dados.")
                continue

            disciplinas_refs.extend([
                ref for ref in curso_data.get("disciplinas", [])
                if isinstance(ref, firestore.DocumentReference)
            ])

        # Buscar todas as disciplinas de uma vez para evitar múltiplas chamadas
        disciplinas_docs = {doc.id: doc.to_dict() for doc in db.get_all(disciplinas_refs)}

        # Processar cursos e disciplinas
        for curso in cursos:
            curso_data = curso.to_dict()
            if not curso_data:
                continue

            print(f"Processando curso: {curso.id} - {curso_data.get('nome', 'Desconhecido')}")

            disciplinas_info = [
                {
                    "id": ref.id,
                    "carga": disciplinas_docs.get(ref.id, {}).get("carga"),
                    "modalidade": disciplinas_docs.get(ref.id, {}).get("modalidade"),
                    "nome": disciplinas_docs.get(ref.id, {}).get("nome"),
                }
                for ref in curso_data.get("disciplinas", [])
                if isinstance(ref, firestore.DocumentReference) and ref.id in disciplinas_docs
            ]

            cursos_list.append({
                "id": curso.id,
                "nome": curso_data.get("nome", "Desconhecido"),
                "disciplinas": disciplinas_info
            })

        response = {"success": True, "cursos": cursos_list}
        print("Resposta gerada com sucesso:", response)
        return jsonify(response)

    except Exception as e:
        print("Erro ao buscar cursos:", str(e))
        return jsonify({"success": False, "message": str(e)}), 500



@user_bp.route('/getGrades/<curso>', methods=['GET'])
def get_grades(curso):
    db_ref = firestore.client().collection('grades').document(curso)
    doc = db_ref.get()

    if not doc.exists:
        return jsonify({"erro": "Grade não encontrada"}), 404

    data = doc.to_dict()

    for disciplina, info in data.items():  
        professor_ref = info.get("professor")  # Obtém a referência do professor
        
        if isinstance(professor_ref, firestore.DocumentReference):  
            professor_doc = professor_ref.get()  
            if professor_doc.exists:  
                info["professor"] = professor_doc.to_dict().get("nome", "Sem nome")  # Substitui pela string do nome
            else:
                info["professor"] = "Desconhecido"

    return jsonify(data)



@user_bp.route('/getCursosDowload/', methods=['GET'])
def get_cursos_download():
    try:
        grades_ref = db.collection('grades')
        docs = grades_ref.stream()
        
        ids = [doc.id for doc in docs]
        print(ids)
        return jsonify({"ids": ids}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# Configurando a aplicação principal
app = Flask(__name__)

# Registrando o Blueprint
app.register_blueprint(user_bp, url_prefix='/user')

if __name__ == '__main__':
    app.run(debug=True)
