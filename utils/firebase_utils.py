from google.cloud import firestore

# Crie uma instância do Firestore
db = firestore.Client()

def get_user_data(user_id):
    """Recupera os dados de um usuário específico"""
    try:
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()

        if not user_doc.exists:
            return None  # Retorna None se o usuário não for encontrado
        
        return user_doc.to_dict()  # Retorna os dados do usuário como um dicionário
    except Exception as e:
        print(f"Erro ao obter dados do usuário: {str(e)}")
        return None

def get_all_courses():
    """Recupera todos os cursos disponíveis"""
    try:
        courses_ref = db.collection("cursos")
        courses = courses_ref.stream()  # Recupera todos os documentos da coleção 'cursos'
        
        all_courses = []
        for course in courses:
            all_courses.append(course.to_dict())
        
        return all_courses
    except Exception as e:
        print(f"Erro ao obter cursos: {str(e)}")
        return []

def get_user_courses(user_id):
    """Recupera todos os cursos de um usuário"""
    try:
        user_data = get_user_data(user_id)
        
        if user_data is None:
            return []  # Retorna lista vazia se o usuário não existir

        cursos_ref = user_data.get("cursos", [])
        
        return cursos_ref  # Retorna lista de cursos do usuário
    except Exception as e:
        print(f"Erro ao obter cursos do usuário: {str(e)}")
        return []
