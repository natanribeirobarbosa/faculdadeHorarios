from flask import Flask
from routes.professor_routes import professor_bp
from routes.admin_routes import admin_bp
from routes.user_routes import user_bp

def create_app():
    app = Flask(__name__)
    
    # Registra os Blueprints
    app.register_blueprint(professor_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    
    # Tratamento de erro 404
    @app.errorhandler(404)
    def not_found(e):
        return {"error": "Rota não encontrada. Use uma das rotas disponíveis."}, 404
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
