from flask import Flask, Blueprint, request, jsonify
from config.firebase_config import db  # Importando a configuração do Firestore
from firebase_admin import firestore
import random

app = Flask(__name__)

# Criando o Blueprint para admin
admin_bp = Blueprint('admin', __name__)

# Rota para adicionar usuários
@admin_bp.route('/addUser', methods=['POST'])
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

# Rota para deletar usuário
@admin_bp.route("/deleteUser", methods=["POST"])
def delete_user():
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
    return jsonify({"success": True, "message": "Usuário deletado com sucesso!"}), 200





# Rota para obter todos os usuários
@admin_bp.route('/allusers/<user_id>', methods=['GET'])
def get_all_users(user_id):
    try:
        # Obtém os dados do usuário pelo ID
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()

        if not user_doc.exists:
            return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404

        user_data = user_doc.to_dict()
   

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

            # Adiciona o ID e nome do usuário, pois o usuário que fez a requisição é admin
            user_data_obj = {
                "id": doc.id,
                "nome": user_info.get("nome", "?")
            }

            if user_role in users_by_cargo:
                users_by_cargo[user_role].append(user_data_obj)

        return jsonify({
            'success': True,
            'user': {
                'nome': user_data.get('nome', '?'),
              
                'users': {
                    'users_by_cargo': users_by_cargo
                }
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    

@admin_bp.route('/addDiscipline', methods=['POST'])
def add_discipline():
    try:
        data = request.get_json()
        
        # Verificar se todos os campos obrigatórios foram enviados
        nome = data.get("nome")
        carga = data.get("carga")
        modalidade = data.get("modalidade")
        cursos = data.get("cursos", [])  # Lista de IDs dos cursos
        user_id = data.get("userId")  # ID do usuário que está tentando adicionar

        if not nome or not carga or not modalidade:
            return jsonify({"success": False, "message": "Todos os campos são obrigatórios."}), 400
        
        # Verificar se o usuário tem cargo 'admin' na coleção 'users'
        user_ref = db.collection("users").document(user_id)  # Utilizando a coleção 'users'
        user_data = user_ref.get().to_dict()
        
        if not user_data or user_data.get("cargo") != "admin":  # Verifica se o cargo é 'admin'
            return jsonify({"success": False, "message": "Você não tem permissão para adicionar disciplinas."}), 403

        # Criar a nova disciplina
        disciplina_ref = db.collection("disciplinas").add({
            "nome": nome,
            "carga": carga,
            "modalidade": modalidade,
            "criado_por": user_id  # Opcional: registrar quem adicionou
        })[1]  # disciplina_ref contém a referência ao novo documento

        disciplina_id = disciplina_ref.id
        
        # Adicionar a disciplina nos cursos informados
        for curso_id in cursos:
            curso_ref = db.collection("cursos").document(curso_id)
            curso_data = curso_ref.get().to_dict()
            if curso_data:
                disciplinas_atualizadas = curso_data.get("disciplinas", [])
                disciplinas_atualizadas.append(disciplina_ref)  # Adiciona a referência
                curso_ref.update({"disciplinas": disciplinas_atualizadas})

        return jsonify({"success": True, "message": "Disciplina adicionada com sucesso!", "id": disciplina_id})

    except Exception as e:
        print("Erro ao adicionar disciplina:", str(e))
        return jsonify({"success": False, "message": str(e)}), 500

@admin_bp.route('/deleteDiscipline', methods=['DELETE'])
def delete_discipline():
    try:
        data = request.get_json()  # Obter o corpo da requisição
        disciplina_id = data.get("disciplinaId")  # ID da disciplina a ser deletada
        user_id = data.get("userId")  # ID do usuário que está tentando deletar
        cursos = data.get("cursos", [])  # Lista de cursos (caso necessário para atualização)

        # Verificar se o usuário tem cargo 'admin'
        user_ref = db.collection("users").document(user_id)  # Utilizando a coleção 'users'
        user_data = user_ref.get().to_dict()
        
        if not user_data or user_data.get("cargo") != "admin":  # Verifica se o cargo é 'admin'
            return jsonify({"success": False, "message": "Você não tem permissão para deletar disciplinas."}), 403
        
        # Referência do documento da disciplina que será deletada
        disciplina_ref = db.collection("disciplinas").document(disciplina_id)
        
        # Verifica se a disciplina existe
        if not disciplina_ref.get().exists:
            return jsonify({"success": False, "message": "Disciplina não encontrada."}), 404
        
        # Excluir o documento da disciplina
        disciplina_ref.delete()
        
        # Remover a referência dessa disciplina de todos os cursos
        cursos_ref = db.collection("cursos")
        cursos = cursos_ref.get()
        
        for curso in cursos:
            curso_data = curso.to_dict()
            if "disciplinas" in curso_data:
                # Filtra a lista de disciplinas removendo a referência da disciplina deletada
                disciplinas_atualizadas = [
                    ref for ref in curso_data["disciplinas"]
                    if ref.id != disciplina_id
                ]
                if len(disciplinas_atualizadas) != len(curso_data["disciplinas"]):
                    # Atualiza o curso com a nova lista de disciplinas
                    db.collection("cursos").document(curso.id).update({
                        "disciplinas": disciplinas_atualizadas
                    })

        return jsonify({"success": True, "message": "Disciplina e referências removidas com sucesso."})
    
    except Exception as e:
        print("Erro ao excluir disciplina:", str(e))
        return jsonify({"success": False, "message": str(e)}), 500

@admin_bp.route('/salvarGrade', methods=['POST'])
def salvar_grade():
    try:
        data = request.json
        user_id = request.cookies.get("userId")
        professores = data.get("professores", [])
        materias = data.get("materias", [])
        curso = data.get("curso")

        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()

        if not user_doc.exists or user_doc.to_dict().get("cargo") != "coordenador":
            return jsonify({"error": "Acesso negado. Apenas coordenadores podem salvar a grade."}), 403

        dias_semana = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira"]
        nova_grade = {}

        for i, materia_id in enumerate(materias):
            professor_ref = db.collection("users").document(professores[i]) if i < len(professores) else None
            dia = dias_semana[i % len(dias_semana)]

            materia_ref = db.collection('disciplinas').document(materia_id)
            materia_doc = materia_ref.get()

            if not materia_doc.exists:
                return jsonify({"error": f"Disciplina {materia_id} não encontrada."}), 400

            materia_data = materia_doc.to_dict()
            nova_grade[materia_data["nome"]] = {
                "dia": dia,
                "carga": materia_data.get("carga"),
                "professor": professor_ref,
                "modalidade": materia_data.get("modalidade")
            }

        # Obtém a grade atual
        doc_ref = db.collection('grades').document(curso)
        doc = doc_ref.get()

        if doc.exists:
            grade_atual = doc.to_dict()  # Obtém os dados existentes
            grade_atual.update(nova_grade)  # Atualiza os repetidos e adiciona os novos
            doc_ref.set(grade_atual)  # Salva de volta
        else:
            doc_ref.set(nova_grade)  # Cria a grade se não existir

        return jsonify({"message": "Grade salva ou atualizada com sucesso!"})

    except Exception as e:
        print(f"Erro ao salvar a grade: {e}")
        return jsonify({"error": "Erro ao salvar a grade."}), 500


# Registrando o Blueprint
app.register_blueprint(admin_bp, url_prefix='/admin')

if __name__ == '__main__':
    app.run(debug=True)
