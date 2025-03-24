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

# Registrando o Blueprint
app.register_blueprint(admin_bp, url_prefix='/admin')

if __name__ == '__main__':
    app.run(debug=True)
