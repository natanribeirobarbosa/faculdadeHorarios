


function fetchUserData(userId) {
    return fetch(`/user/${userId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('data'+data.user.nome)
                return data.user;  // Retorna os dados do usuário
            } else {
                throw new Error("Erro ao carregar usuário.");
            }
        })
        .catch(error => console.error("Erro ao buscar usuário:", error));
}


cargo = ''


function fetchAllUserData(userId) {
    return fetch(`/allusers/${userId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                return(data.user.users.users_by_cargo);  // Retorna os dados dos usuários por cargo
            } else {
                alert("Erro ao carregar usuários.");
                return null;  // Retorna null em caso de erro
            }
        })
        .catch(error => {
            console.error("Erro ao buscar usuário:", error);
            return null;  // Retorna null em caso de erro
        });
}
let ids = {}
//função que busca todos os cursos e disciplinas
function fetchAllCurses() {
    return fetch('/allcourses').then(response => response.json())
    .then(data => {
        if (data.success) {
            
            renderCursos(data.cursos)
            //return data.cursos; // Retorna os cursos para outra função

        } else {
            alert("Erro ao carregar cursos.");
            return []; // Retorna um array vazio caso haja erro
        }
    })
    .catch(error => {
        console.error("Erro ao buscar cursos:", error);
        return []; // Retorna um array vazio em caso de erro
    });
}
// Função para obter os cursos de um usuário
async function getCourses(userId) {
    document.getElementById('course-list').style.display= 'block'
    try {
        const url = `/allprofessorcourses/${userId}`;
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`Erro na requisição: ${response.status}`);
        }

        const data = await response.json();
       

        if (data.success) {
            if (data.message) {
                alert(data.message);
            }

            // Verifica se "disciplinas" existe e é um array
            if (Array.isArray(data.disciplinas)) {
                
                displayCourses(data.disciplinas); // Agora chamamos apenas se for um array válido
            } else {
                console.warn("O campo 'disciplinas' está ausente ou não é um array.");
                document.getElementById('vagasTitle').innerText = "Nenhuma vaga disponível";
            }
        } else {
            alert(data.message || 'Erro ao obter os dados');
        }
    } catch (error) {
        console.error("Erro ao obter os cursos:", error);
        alert(`Erro ao obter os cursos: ${error.message}`);
    }
}
