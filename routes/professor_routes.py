from flask import Flask, Blueprint, request, jsonify
from config.firebase_config import db  # Importando a configuração do Firestore
from firebase_admin import firestore

app = Flask(__name__)

# Criando o Blueprint para professor
professor_bp = Blueprint('professor', __name__)
@professor_bp.route("/adicionar_candidato", methods=["POST"])
def adicionar_candidato():
    try:
        data = request.json
        user_id = data.get("userId")
        codigo_disciplina = data.get("codigoDisciplina")

        if not all([user_id, codigo_disciplina]):
            return jsonify({"success": False, "message": "Parâmetros inválidos!"}), 400

        # Verifica se o usuário existe e se tem o cargo "professor"
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()

        if not user_doc.exists:
            return jsonify({"success": False, "message": "Usuário não encontrado!"}), 404

        if user_doc.to_dict().get("cargo") != "professor":
            return jsonify({"success": False, "message": "Usuário não tem permissão para se candidatar!"}), 403

        # Verifica se a disciplina existe
        disciplina_ref = db.collection("disciplinas").document(codigo_disciplina)
        if not disciplina_ref.get().exists:
            return jsonify({"success": False, "message": "Disciplina não encontrada!"}), 404

        # Adiciona o candidato ao array "candidatos" da disciplina
        disciplina_ref.update({
            "candidatos": firestore.ArrayUnion([f"/users/{user_id}"])
        })

        # Adiciona a referência da disciplina ao array "candidaturas" do usuário
        user_ref.update({
            "candidaturas": firestore.ArrayUnion([disciplina_ref])
        })

        return jsonify({"success": True, "message": "Candidato adicionado com sucesso!"}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500



# Rota para listar cursos e disciplinas de um professor
@professor_bp.route('/allprofessorcourses/<user_id>', methods=['GET'])
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
                                periodo = disciplina_data.get('periodo', 'modalidade não disponível')

                                # Adiciona a disciplina à lista com o campo 'nome'
                                disciplinas_separadas.append({
                                    'id': disciplina_doc.id,
                                    'nome': nome_disciplina,
                                    'carga': carga,
                                    'modalidade': modalidade,
                                    'periodo': periodo
                                })

        # Retorna os cursos e as disciplinas separadas
        return jsonify({
            "success": True,
            "disciplinas": disciplinas_separadas  # Lista separada com todas as disciplinas de todos os cursos
        })

    except Exception as e:
        print("Erro ao buscar cursos:", str(e))  # Log no console
        return jsonify({"success": False, "message": str(e)}), 500


# Rota para adicionar licenciatura ao professor
@professor_bp.route('/adcionarlicenciatura', methods=['POST'])
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


# Registrando o Blueprint
app.register_blueprint(professor_bp, url_prefix='/professor')

if __name__ == '__main__':
    app.run(debug=True)
