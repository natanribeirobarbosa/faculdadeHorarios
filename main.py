from flask import Flask, request, jsonify, render_template, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas as rotas
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///schedule.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de Professores
class Professor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    disponibilidade = db.Column(db.String(200), nullable=False)  # Ex: "Segunda 08:00-12:00, Quarta 14:00-18:00"
    materias = relationship('Materia', backref='professor')

# Modelo de Matérias
class Materia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('professor.id'))
    horario = db.Column(db.String(50), nullable=True)  # Ex: "Segunda 08:00-10:00"

# Inicializar Banco de Dados
with app.app_context():
    db.create_all()

# Rota principal para a interface web
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# Rota para adicionar professor
@app.route('/add_professor', methods=['POST'])
def add_professor():
    data = request.get_json()
    novo_professor = Professor(nome=data['nome'], disponibilidade=data['disponibilidade'])
    db.session.add(novo_professor)
    db.session.commit()
    return jsonify({"message": "Professor cadastrado com sucesso!"})

# Rota para adicionar matéria
@app.route('/add_materia', methods=['POST'])
def add_materia():
    data = request.get_json()
    nova_materia = Materia(nome=data['nome'], professor_id=data['professor_id'])
    db.session.add(nova_materia)
    db.session.commit()
    return jsonify({"message": "Matéria cadastrada com sucesso!"})

# Rota para listar professores
@app.route('/listar_professores', methods=['GET'])
def listar_professores():
    professores = Professor.query.all()
    professores_lista = []
    
    for prof in professores:
        professores_lista.append({
            'id': prof.id,
            'nome': prof.nome,
            'disponibilidade': prof.disponibilidade
        })
    
    return jsonify({"professores": professores_lista})

# Rota para listar matérias
@app.route('/listar_materias', methods=['GET'])
def listar_materias():
    materias = Materia.query.all()
    materias_lista = []
    
    for mat in materias:
        professor_nome = None
        if mat.professor:
            professor_nome = mat.professor.nome
            
        materias_lista.append({
            'id': mat.id,
            'nome': mat.nome,
            'professor_id': mat.professor_id,
            'professor_nome': professor_nome,
            'horario': mat.horario
        })
    
    return jsonify({"materias": materias_lista})

# Rota para remover professor
@app.route('/remover_professor/<int:professor_id>', methods=['DELETE'])
def remover_professor(professor_id):
    professor = Professor.query.get(professor_id)
    if not professor:
        return jsonify({"error": "Professor não encontrado!"}), 404
    
    # Verificar se o professor tem matérias associadas
    materias = Materia.query.filter_by(professor_id=professor_id).all()
    for materia in materias:
        db.session.delete(materia)
    
    db.session.delete(professor)
    db.session.commit()
    return jsonify({"message": "Professor e suas matérias removidos com sucesso!"})

# Rota para remover matéria
@app.route('/remover_materia/<int:materia_id>', methods=['DELETE'])
def remover_materia(materia_id):
    materia = Materia.query.get(materia_id)
    if not materia:
        return jsonify({"error": "Matéria não encontrada!"}), 404
    
    db.session.delete(materia)
    db.session.commit()
    return jsonify({"message": "Matéria removida com sucesso!"})

# Rota para limpar horário de uma matéria
@app.route('/limpar_horario/<int:materia_id>', methods=['PUT'])
def limpar_horario(materia_id):
    materia = Materia.query.get(materia_id)
    if not materia:
        return jsonify({"error": "Matéria não encontrada!"}), 404
    
    materia.horario = None
    db.session.commit()
    return jsonify({"message": "Horário da matéria removido com sucesso!"})

# Rota para gerar horários sem conflito
@app.route('/gerar_horarios', methods=['POST'])
def gerar_horarios():
    # Função auxiliar para extrair dia e hora de um horário
    def extrair_dia_hora(horario_str):
        partes = horario_str.split(' ', 1)
        if len(partes) >= 2:
            return partes[0], partes[1]  # Dia, Hora
        return horario_str, ""
    
    # Buscar todas as matérias sem horário alocado
    materias = Materia.query.filter(Materia.horario == None).all()
    
    # Ordenar matérias - primeiro professores com menos disponibilidade
    materias_ordenadas = []
    for materia in materias:
        prof = Professor.query.get(materia.professor_id)
        if prof:
            horarios_disp = prof.disponibilidade.split(', ')
            materias_ordenadas.append((materia, len(horarios_disp)))
    
    # Ordenar por disponibilidade (do menor para o maior)
    materias_ordenadas.sort(key=lambda x: x[1])
    
    # Dicionário para armazenar os resultados da alocação
    alocacao = {}
    
    # Mapa de todos os horários já alocados (horário -> professor_id)
    horarios_ocupados = {}
    
    # Preencher o mapa com horários já existentes
    todas_materias_com_horario = Materia.query.filter(Materia.horario != None).all()
    for mat in todas_materias_com_horario:
        if mat.horario:
            horarios_ocupados[mat.horario] = mat.professor_id
    
    # Para cada matéria (começando pelas que têm menos opções)
    for materia, _ in materias_ordenadas:
        prof = Professor.query.get(materia.professor_id)
        if not prof:
            continue
        
        # Obter todos os horários disponíveis do professor
        horarios_disp = prof.disponibilidade.split(', ')
        
        # Obter horários que o professor já está usando
        horarios_usados_pelo_prof = []
        for mat in prof.materias:
            if mat.horario:
                horarios_usados_pelo_prof.append(mat.horario)
        
        # Verificar dias já ocupados pelo professor para distribuir melhor
        dias_ocupados = {}
        for horario in horarios_usados_pelo_prof:
            dia, _ = extrair_dia_hora(horario)
            if dia in dias_ocupados:
                dias_ocupados[dia] += 1
            else:
                dias_ocupados[dia] = 1
        
        # Ordenar horários disponíveis priorizando dias menos usados
        def prioridade_horario(horario):
            dia, _ = extrair_dia_hora(horario)
            return dias_ocupados.get(dia, 0)
        
        horarios_disp.sort(key=prioridade_horario)
        
        # Tentar alocar em algum horário disponível
        horario_encontrado = False
        for horario in horarios_disp:
            # Verificar se o horário já está alocado para outro professor
            if horario in horarios_ocupados and horarios_ocupados[horario] != prof.id:
                continue
            
            # Verificar se o professor já está ocupado neste horário
            if horario in horarios_usados_pelo_prof:
                continue
                
            # Verificar se este horário já foi alocado nesta rodada atual
            if horario in alocacao.values():
                continue
                
            # Encontramos um horário válido!
            alocacao[materia.id] = horario
            materia.horario = horario
            horarios_ocupados[horario] = prof.id
            horario_encontrado = True
            break
        
        if not horario_encontrado:
            # Não encontrou horário - tentar novamente com menos restrições
            # (apenas evitando conflitos diretos)
            for horario in horarios_disp:
                if horario not in horarios_usados_pelo_prof and horario not in alocacao.values():
                    # Verificar conflito com outros professores
                    if horario in horarios_ocupados and horarios_ocupados[horario] != prof.id:
                        continue
                        
                    alocacao[materia.id] = horario
                    materia.horario = horario
                    horarios_ocupados[horario] = prof.id
                    break
    
    db.session.commit()
    return jsonify({"message": "Horários gerados sem conflitos!", "alocacao": alocacao})

# Tratamento de erro 404
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Rota não encontrada. Use uma das rotas disponíveis."}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)