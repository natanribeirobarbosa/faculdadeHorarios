from flask import Flask, Blueprint, request, jsonify
from config.firebase_config import db  # Importando a configuração do Firestore
from firebase_admin import firestore

app = Flask(__name__)

# Criando o Blueprint para professor
professor_bp = Blueprint('professor', __name__)


@professor_bp.route("/adicionar_candidato", methods=["POST"])
def adicionar_candidato():
    try:
        # Obtém os dados enviados
        data = request.json
        user_id = data.get("userId")
        codigo_disciplina = data.get("codigoDisciplina")

        # Valida os parâmetros recebidos
        if not all([user_id, codigo_disciplina]):
            return jsonify({"success": False, "message": "Parâmetros inválidos!"}), 400

        # Verifica se o usuário existe e tem o cargo "professor"
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()

        if not user_doc.exists:
            return jsonify({"success": False, "message": "Usuário não encontrado!"}), 404

        user_data = user_doc.to_dict()
        if user_data.get("cargo") != "professor":
            return jsonify({"success": False, "message": "Usuário não tem permissão para se candidatar!"}), 403

        # Verifica se a disciplina existe
        disciplina_ref = db.collection("disciplinas").document(codigo_disciplina)
        disciplina_doc = disciplina_ref.get()

        if not disciplina_doc.exists:
            return jsonify({"success": False, "message": "Disciplina não encontrada!"}), 404
        
        # Verifica o array de candidaturas do usuário
        candidaturasNoUsuario = user_data.get("candidaturas", [])
        if len(candidaturasNoUsuario) == 1:
            for candidatura in candidaturasNoUsuario:
                candidatura.update({
                "candidatos": firestore.ArrayUnion([user_ref])  # Adiciona a referência do usuário como candidato
            })
                disciplina_ref.update({
                "candidatos": firestore.ArrayUnion([user_ref])  # Adiciona a referência do usuário
                    })
                user_ref.update({
                "candidaturas": firestore.ArrayUnion([disciplina_ref]),
                "mensagens": firestore.ArrayUnion(["mensagem"])
        })
                return jsonify({"success": True, "message": "Candidato adicionado com sucesso!"}), 200
            

        elif len(candidaturasNoUsuario) >= 2:
                disciplina_ref.update({
                "candidatos": firestore.ArrayUnion([user_ref])  # Adiciona a referência do usuário
                    })
                user_ref.update({
                "candidaturas": firestore.ArrayUnion([disciplina_ref]),
                "mensagens": firestore.ArrayUnion(["mensagem"])
        })
                return jsonify({"success": True, "message": "Candidato adicionado com sucesso!"}), 200
        
        elif len(candidaturasNoUsuario) == 0:
                user_ref.update({
                "candidaturas": firestore.ArrayUnion([disciplina_ref]),
                "mensagens": firestore.ArrayUnion(["mensagem"])
                })
                return jsonify({"success": True, "message": "Candidato adicionado com sucesso!"}), 200  
                        


            




        # Adiciona a referência da disciplina ao array "candidaturas" do usuário

         
    
    except Exception as e:
        # Mensagem de erro mais detalhada para depuração
        return jsonify({"success": False, "message": f"Ocorreu um erro: {str(e)}"}), 500



@professor_bp.route("/remover_candidato", methods=["POST"])
def remover_candidato():
    try:
        print("📌 Iniciando remoção de candidatura")

        # Captura os dados da requisição
        data = request.json
        print("📌 Dados recebidos:", data)

        user_id = str(data.get("userId"))
        codigo_disciplina = str(data.get("codigoDisciplina"))  # Converte logo ao capturar o dado

        if not all([user_id, codigo_disciplina]):
            print("❌ Parâmetros inválidos!")
            return jsonify({"success": False, "message": "Parâmetros inválidos!"}), 400

        print(f"📌 User ID: {user_id}, Código Disciplina: {codigo_disciplina}")

        # Referências no Firestore
        user_ref = db.collection("users").document(user_id)
        disciplina_ref = db.collection("disciplinas").document(codigo_disciplina)

        # Verifica se o usuário existe
        user_doc = user_ref.get()
        if not user_doc.exists:
            print("❌ Usuário não encontrado!")
            return jsonify({"success": False, "message": "Usuário não encontrado!"}), 404

        user_data = user_doc.to_dict()
        print("📌 Dados do usuário:", user_data)

        if user_data.get("cargo") != "professor":
            print("❌ Usuário não tem permissão para remover candidatura!")
            return jsonify({"success": False, "message": "Usuário não tem permissão para remover candidatura!"}), 403

        # Verifica se a disciplina existe
        disciplina_doc = disciplina_ref.get()
        if not disciplina_doc.exists:
            print("❌ Disciplina não encontrada!")
            return jsonify({"success": False, "message": "Disciplina não encontrada!"}), 404

        

        # Formata os valores corretamente
        candidato_path = f"users/{user_id}"
        disciplina_path = f"disciplinas/{codigo_disciplina}"

        
        disciplina_doc = disciplina_ref.get().to_dict()
        user_data = user_ref.get().to_dict()

        candidato_ref = db.document(candidato_path)  # Convertendo string para DocumentReference
        disciplina_ref_to_remove = db.document(disciplina_path)  # Convertendo string para DocumentReference

        print("📌 Disciplina doc:", disciplina_ref_to_remove)
        print("📌 User data:", candidato_ref)

        if "candidatos" in disciplina_doc:
            disciplina_ref.update({
                "candidatos": firestore.ArrayRemove([candidato_ref])
            })
            print("✅ Candidato removido da disciplina!")
        else:
            print("❌ Campo 'candidatos' não encontrado na disciplina!")

        if "candidaturas" in user_data:
            user_ref.update({
                "candidaturas": firestore.ArrayRemove([disciplina_ref_to_remove])
            })
            print("✅ Disciplina removida do usuário!")
        else:
            print("❌ Campo 'candidaturas' não encontrado no usuário!")

        
        return jsonify({"success": True, "message": "Candidatura removida com sucesso!"}), 200

    except Exception as e:
        print("❌ Erro inesperado:", str(e))
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
    

@professor_bp.route('/add-disponibilidade', methods=['POST'])
def add_disponibilidade():
    try:
        # Obtém os dados da requisição
        data = request.get_json()
        user_id = data.get('userId')
        disponibilidade = data.get('disponibilidade')

        # Valida se os dados estão completos
        if not all([user_id, disponibilidade]):
            return jsonify({"error": "userId e disponibilidade são obrigatórios"}), 400

        # Verifica se o usuário é um professor
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()

        if not user_doc.exists or user_doc.to_dict().get("cargo") != "professor":
            return jsonify({"error": "Usuário sem permissão ou não é professor"}), 403

        # Obtém a lista atual de disponibilidades do usuário
        user_data = user_doc.to_dict()
        disponibilidades_atual = user_data.get("periodos", [])

        # Verifica se a disponibilidade já existe na lista
        if disponibilidade not in disponibilidades_atual:
            disponibilidades_atual.append(disponibilidade)
            user_ref.update({"periodos": disponibilidades_atual})

        return jsonify({"success": True, "message": f"Disponibilidade {disponibilidade} adicionada com sucesso! Para ver atualize a página."})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500



@professor_bp.route('/remove-disponibilidade', methods=['POST'])
def remove_disponibilidade():
    try:
        # Obtém os dados da requisição
        data = request.get_json()
        user_id = data.get('userId')
        disponibilidade = data.get('disponibilidade')

        # Valida se os dados estão completos
        if not all([user_id, disponibilidade]):
            return jsonify({"error": "userId e disponibilidade são obrigatórios"}), 400

        # Verifica se o usuário é um professor
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()

        if not user_doc.exists or user_doc.to_dict().get("cargo") != "professor":
            return jsonify({"error": "Usuário sem permissão ou não é professor"}), 403

        # Obtém a lista atual de disponibilidades do usuário
        user_data = user_doc.to_dict()
        disponibilidades_atual = user_data.get("periodos", [])

        # Verifica se a disponibilidade está na lista
        if disponibilidade in disponibilidades_atual:
            print('removido.')
            disponibilidades_atual.remove(disponibilidade)
            user_ref.update({"periodos": disponibilidades_atual})
            return jsonify({"success": True, "message": f"Disponibilidade {disponibilidade} removida com sucesso! Para ver atualize a página."})
        else:
            return jsonify({"error": f"A disponibilidade {disponibilidade} não foi encontrada."}), 404

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# Registrando o Blueprint
app.register_blueprint(professor_bp, url_prefix='/professor')

if __name__ == '__main__':
    app.run(debug=True)
