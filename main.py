from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///schedule.db'
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
@app.before_first_request
def create_tables():
    db.create_all()

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

# Rota para gerar horários sem conflito
@app.route('/gerar_horarios', methods=['POST'])
def gerar_horarios():
    professores = Professor.query.all()
    materias = Materia.query.filter(Materia.horario == None).all()
    alocacao = {}

    for materia in materias:
        prof = Professor.query.get(materia.professor_id)
        horarios_disp = prof.disponibilidade.split(', ')
        
        for horario in horarios_disp:
            if horario not in alocacao.values():
                alocacao[materia.id] = horario
                materia.horario = horario
                break
    
    db.session.commit()
    return jsonify({"message": "Horários gerados!", "alocacao": alocacao})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)