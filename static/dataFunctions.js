


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
            console.log('cursos'+data.cursos[0])
            renderCursos(data.cursos)
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

// Função para obter os cursos de um professor via POST
async function getCourses(userId) {

    try {
        const url = `/allprofessorcourses`;
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ userId })
        });

        if (!response.ok) {
            throw new Error(`Erro na requisição: ${response.status}`);
        }

        const data = await response.json();

        if (data.success) {
            if (Array.isArray(data.disciplinas)) {
                displayCourses(data.disciplinas);
            } else {
                document.getElementById('vagasTitle').innerText = "Nenhuma vaga disponível";
                document.getElementById('loadingContainer3').style.display = "none";
            }
        } else {
            alert(data.message || "Erro ao obter os dados");
        }
    } catch (error) {
        console.error("Erro ao obter os cursos:", error);
        alert(`Erro ao obter os cursos: ${error.message}`);
    }
}


// Função para obter os cursos com a porcentagem de disciplinas com candidatos
async function getCordCourses(userId) {
    try {
        const url = "/allcordcourses";
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ userId })
        });

        if (!response.ok) {
            throw new Error(`Erro na requisição: ${response.status}`);
        }

        const data = await response.json();

        if (data.success) {
           return data.cursos

        } else {
            console.error("Erro ao obter cursos:", data.message);
        }
    } catch (error) {
        console.error("Erro ao obter os cursos:", error);
    }
}


