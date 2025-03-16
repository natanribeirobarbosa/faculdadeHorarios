let listaAtual = "";





//----------------------------POP UPS -----------------------------------------------------------------------------------------

let cursoAtual = null;

function fecharPopup() {
    document.getElementById("popup").classList.remove("active");
    document.getElementById("nomeInput").value = "";
}





function abrirPopup(funcao, lista, curso) {

    listaAtual = lista
    let popup = document.getElementById("popup");
    let nomePopup = document.getElementById("nomePopup");
    let inputsContainer = document.getElementById("inputs");

    

 
    

    if (!popup || !nomePopup || !inputsContainer) {
        console.error("Elementos não encontrados.");
        return;
    }

    // Define o título do popup
    nomePopup.innerText = (funcao === "adicionar" ? "Adicionar " : "Deletar ") + lista;

    if(curso != null){
        let novoElemento = document.createElement("p");
        cursoAtual = curso
        novoElemento.textContent = curso;
        nomePopup.innerHTML += '<br><span id="curso">'+curso+'</span>';
    }


    // Esconde todos os elementos primeiro
    let adicionarNome = document.getElementById('adicionarNome');
    let adicionarMateria = document.getElementById('adicionarMateria');
    let deletarNome = document.getElementById('deletarNome');
    let deletarMateria = document.getElementById('deletarMateria');

    if (adicionarNome) adicionarNome.style.display = "none";
    if (adicionarMateria) adicionarMateria.style.display = "none";
    if (deletarNome) deletarNome.style.display = "none";
    if (deletarMateria) deletarMateria.style.display = "none";

    // Limpa o conteúdo atual dos inputs
    inputsContainer.innerHTML = "";

    // Normaliza lista para "nome" caso seja professor, coordenador ou user
    if (["professor", "coordenador", "user"].includes(lista)) {
        lista = "nome";
    }

    if (funcao === "adicionar") {
        if (lista === "matéria") {
            if (adicionarMateria) adicionarMateria.style.display = "block"; // Mostra adicionarMateria

            // Criar elementos para adicionar matéria
            let labelNome = document.createElement("label");
            labelNome.textContent = "Nome da matéria";
            let inputNome = document.createElement("input");
            inputNome.type = "text";
            inputNome.id = "nomeInput";
            inputNome.placeholder = "Digite o nome da matéria";

            let labelModalidade = document.createElement("label");
            labelModalidade.textContent = "Modalidade:";
            let selectModalidade = document.createElement("select");
            selectModalidade.id = "workType";
            selectModalidade.name = "workType";

            let optionRemoto = document.createElement("option");
            optionRemoto.value = "remoto";
            optionRemoto.textContent = "Remoto";

            let optionPresencial = document.createElement("option");
            optionPresencial.value = "presencial";
            optionPresencial.textContent = "Presencial";

            selectModalidade.appendChild(optionRemoto);
            selectModalidade.appendChild(optionPresencial);

            let labelCarga = document.createElement("label");
            labelCarga.textContent = "Carga horária:";
            let selectCarga = document.createElement("select");
            selectCarga.id = "cargaHoraria";
            selectCarga.name = "cargaHoraria";

            let option60 = document.createElement("option");
            option60.value = "60";
            option60.textContent = "60h";

            let option80 = document.createElement("option");
            option80.value = "80";
            option80.textContent = "80h";

            selectCarga.appendChild(option60);
            selectCarga.appendChild(option80);

            inputsContainer.appendChild(labelNome);
            inputsContainer.appendChild(inputNome);
            inputsContainer.appendChild(document.createElement("br"));

            inputsContainer.appendChild(labelModalidade);
            inputsContainer.appendChild(selectModalidade);
            inputsContainer.appendChild(document.createElement("br"));

            inputsContainer.appendChild(labelCarga);
            inputsContainer.appendChild(selectCarga);
        } else {
            if (adicionarNome) adicionarNome.style.display = "block"; // Mostra adicionarNome

            let inputGenerico = document.createElement("input");
            inputGenerico.type = "text";
            inputGenerico.id = "nomeInput";
            inputGenerico.placeholder = `Digite o nome da(o) ${lista}`;
            inputsContainer.appendChild(inputGenerico);
        }
    } else if (funcao === "deletar") {
        if (lista === "nome" && deletarNome) deletarNome.style.display = "block";
        if (lista === "matéria" && deletarMateria) deletarMateria.style.display = "block";

        let inputDeletar = document.createElement("input");
        inputDeletar.type = "text";
        inputDeletar.id = "nomeInput";
        inputDeletar.placeholder = `Digite o nome da(o) ${lista} a deletar`;

        inputsContainer.appendChild(inputDeletar);
    }

    popup.classList.add("active");
}



//------------------------------------------FORMULARIOS POST -----------------------------------------------------------------


function deletarNome(){
    let cod = document.getElementById("nomeInput").value

    if (cod) {
        fetch(`/deleteUser`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: cod, userId})
        })
        .then(response => response.json())
        .then(data => {
        if (data.success) {
            location.reload();
        } else {
        alert("Erro adicionar usuario!");
        }
        })
        .catch(error => console.error("Erro na adição:", error))

    }else{
        window.alert("Digite um nome válido.");
    }

}
function adicionarNome() {
    let nome = document.getElementById("nomeInput").value.trim();
    console.log(listaAtual)
    
    if (!nome) {
        window.alert("Digite um nome válido.");
        return;
    }

    if (typeof userId === "undefined") {
        console.error("Erro: userId não está definido.");
        return;
    }

    fetch(`/addUser`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nome: nome, cargo: listaAtual, userId: userId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert("Erro ao adicionar usuário: " + data.error);
        }
    })
    .catch(error => console.error("Erro na adição:", error));
}



function adicionarMateria(curso) {
    let nome = document.getElementById("nomeInput").value
    let carga = document.getElementById("cargaHoraria").value
    let modalidade = document.getElementById('workType').value

    if (nome != null && nome != '') {
        fetch(`/addDiscipline`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nome: nome, carga: carga, modalidade, curso: curso, userId})
        })
        .then(response => response.json())
        .then(data => {
        if (data.success) {
           
            location.reload();
        } else {
        alert("Erro adicionar usuario!");
        }
        })
        .catch(error => console.error("Erro na adição:", error))
    } else {
        window.alert("Digite um nome válido.");
    }
}


async function deletarMateria() {
    let disciplinaId = document.getElementById("nomeInput").value.trim(); // Pega o ID da matéria digitado
    if (!disciplinaId) {
        alert("Por favor, insira o ID da disciplina para deletar.");
        return;
    }

    try {
        let response = await fetch("/deleteDiscipline", {
            method: "DELETE",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ disciplinaId, userId, curso: cursoAtual })
        });

        let data = await response.json();

        if (data.success) {
            location.reload(); // Recarrega a página para atualizar a lista de disciplinas
        } else {
            alert("Erro ao deletar disciplina: " + data.message);
        }
    } catch (error) {
        console.error("Erro ao deletar disciplina:", error);
        alert("Erro ao conectar com o servidor.");
    }
}

//-----------------------------------dashboard---------------------

function updateUserDataInDashboard(userData) {
    document.getElementById("userName").innerText = userData.nome;
    document.getElementById("userCargo").innerText = userData.cargo;

    if (userData.cargo === "professor") {
        document.getElementById("userCargo").innerHTML += "<br>Licenciaturas:";

        if (Array.isArray(userData.licenciaturas) && userData.licenciaturas.length > 0) {
            userData.licenciaturas.forEach(element => {
                document.getElementById("userCargo").innerHTML += `<br>- ${element}`;
            });
        }
    }
}

// Função que renderiza os cursos no front-end
function renderCursos(cursos) {
    
    const cursosContainer = document.getElementById("cursos");

    document.getElementById('loadingContainer2').style.display = 'none'
    

    cursos.forEach(curso => {
        // Criando o título do curso (h2)
        const cursoTitle = document.createElement("h2");
        cursoTitle.innerHTML = curso.nome + ` (${curso.disciplinas.length})` + 
                               `<span class="onlyAdmins" onclick="abrirPopup('adicionar','matéria','${curso.id}')"> Adicionar</span>` + 
                               `<span class="onlyAdmins negative" onclick="abrirPopup('deletar','matéria','${curso.id}')"> Deletar</span>`;
        cursosContainer.appendChild(cursoTitle);

        // Criando a lista de disciplinas (ul)
        const disciplinaList = document.createElement("ul");

        curso.disciplinas.forEach(disciplina => {
            const disciplinaItem = document.createElement("li");
            disciplinaItem.innerHTML = `<strong>${disciplina.nome}</strong><span class="onlyAdmins">(${disciplina.id})</span><br>Carga horária: ${disciplina.carga}h <br>Modalidade: ${disciplina.modalidade}`;
            disciplinaList.appendChild(disciplinaItem);
        });

        cursosContainer.appendChild(disciplinaList);

        if (cargo == 'admin') {
            var elementos = document.querySelectorAll('.onlyAdmins');
            elementos.forEach(function(elemento) {
                elemento.style.display = 'inline';
            });
        }
    });
}

//-------------------INDEX -------------------------------------------

// Função para exibir os cursos na página index
async function displayCourses(courses) {
    
    // Garante que courses seja um array antes de continuar
    if (!Array.isArray(courses)) {
        console.warn("Erro: courses não é um array válido!", courses);
        return; // Evita erro no forEach()
    }

    const courseList = document.getElementById("vagas");
    courseList.innerHTML = ''; // Limpa a lista antes de adicionar os novos cursos

    courses.forEach(course => {
        // Cria o bloco de curso
        const courseBlock = document.createElement("div");
        courseBlock.classList.add("course-block");

        // Adiciona informações do curso
        const courseInfo = document.createElement("div");
        courseInfo.classList.add("course-info");
        courseInfo.innerHTML = `
            <h2>${course.nome}</h2>
            <p><strong>Carga Horária:</strong> ${course.carga}h</p>
            <p><strong>Modalidade:</strong> ${course.modalidade}</p>
        `;
        courseBlock.appendChild(courseInfo);

        // Cria o botão "Me Candidatar"
        const button = document.createElement("button");
        button.classList.add("positive");
        button.innerText = "Me Candidatar";
        button.onclick = () => alert(`Candidatura realizada para ${course.nome}`);
        courseBlock.appendChild(button);

        // Adiciona o bloco de curso à lista
        courseList.appendChild(courseBlock);
    });

    // Atualiza o título com o número de cursos
    document.getElementById('vagasTitle').innerText += ` (${courses.length})`;
}


function showContentBasedOnCargo(cargo, name) {
    // Esconde todas as seções primeiro
    
    document.querySelector('.user-section').style.display = 'none';
    document.getElementById('login').style.display="none"
    document.getElementById("btnDashboard").style.display = "block";

    // Exibe a seção correspondente ao cargo
    if (cargo == 'admin') {
        document.querySelector('.user-section').style.display = 'block';
        document.getElementById('titleUser').innerHTML = 'Bem vindo '+name+'!'
        document.getElementById('pUser').innerHTML = 'Sendo ADM, aqui você pode gerenciar tudo!'
        
        
    } else if (cargo == 'user') {
        document.querySelector('.user-section').style.display = 'block';
        document.getElementById('titleUser').innerHTML = 'Bem vindo '+name+'!'
        document.getElementById('pUser').innerHTML = 'Seu cargo não foi definido ainda... contate o ADM!'

       
        
    }else if(cargo == 'professor') {
        document.querySelector('.user-section').style.display = 'block';
        document.getElementById('titleUser').innerHTML = 'Bem vindo '+name+'!'
        document.getElementById('pUser').innerHTML = 'Como professor, aqui você pode se candidatar as vagas!'
        return
     
      
    }else if(cargo == 'coordenador') {
        document.querySelector('.user-section').style.display = 'block';
        document.getElementById('titleUser').innerHTML = 'Bem vindo '+name+'!'
        document.getElementById('pUser').innerHTML = 'Como coordenador, aqui você pode se definir a grade das matérias!'
     
      
    }else{
        console.log('erro!')
    }
}



function renderCargos(data) {
    document.getElementById('loadingContainer1').style.display = 'none'

    // Acessando corretamente os dados
    const usersByCargo = data; // O JSON já está estruturado corretamente

    // Atualiza os títulos com a contagem correta de usuários por cargo
    document.getElementById('administradoresTitle').innerText = `Administradores (${usersByCargo.admin.length})`;
    document.getElementById('professoresTitle').innerText = `Professores (${usersByCargo.professor.length})`;
    document.getElementById('coordenadoresTitle').innerText = `Coordenadores (${usersByCargo.coordenador.length})`;
    document.getElementById('usuariosTitle').innerText = `Usuários (${usersByCargo.user.length})`;

    // Obtendo as listas
    const listAdmin = document.getElementById('admins');
    const listProf = document.getElementById('professores');
    const listCord = document.getElementById('coordenadores');
    const listUsers = document.getElementById('usuarios');

    // Limpa as listas antes de adicionar novos elementos
    listAdmin.innerHTML = '';
    listProf.innerHTML = '';
    listCord.innerHTML = '';
    listUsers.innerHTML = '';

    // Função auxiliar para adicionar itens à lista
    function adicionarUsuarios(lista, usuarios, exibirId = false) {
        usuarios.forEach(usuario => {
            const listItem = document.createElement('li');
            listItem.innerHTML = usuario.nome + (exibirId ? `<span class="onlyAdmins">(${usuario.id})</span>` : '');
            lista.appendChild(listItem);
        });
    }

    // Adiciona os usuários às listas corretas
    adicionarUsuarios(listAdmin, usersByCargo.admin);
    adicionarUsuarios(listProf, usersByCargo.professor, true);
    adicionarUsuarios(listCord, usersByCargo.coordenador, true);
    adicionarUsuarios(listUsers, usersByCargo.user, true);

    console.log(data)

    // Verifica se há um administrador logado para exibir IDs
    if (cargo == 'admin') {
        console.log('admin')
        document.querySelectorAll('.onlyAdmins').forEach(elemento => {
            elemento.style.display = 'inline';
        });
    }
}
