let listaAtual = "";
let cursos = []
let Cursos = null
let cursosDaMateria = null




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

                   // Criar elementos para o identificador dos cursos
            let labelCursos = document.createElement("label");
            labelCursos.textContent = "Identificadores dos cursos (separados por vírgula)";
            let inputCursos = document.createElement("input");
            inputCursos.type = "text";
            inputCursos.id = "cursosInput";
            inputCursos.placeholder = "Ex: 101, 102, 103";

            // Função para converter os identificadores em array
            inputCursos.addEventListener("input", function () {
                cursos = inputCursos.value.split(",").map(valor => valor.trim()).filter(valor => valor !== ""); 
                console.log("Array de identificadores:", cursos);
            });

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

       

        // Adiciona os elementos ao pop-up
        inputsContainer.appendChild(labelNome);
        inputsContainer.appendChild(inputNome);
        inputsContainer.appendChild(labelCursos);
        inputsContainer.appendChild(inputCursos);
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
        body: JSON.stringify({ nome: nome, carga: carga, modalidade, cursos: cursos, userId})
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

function addLicenciatura(){
    let cursoSelecionado = document.getElementById("curso").value;
    if (cursoSelecionado != null && cursoSelecionado != '') {
        fetch(`/adcionarlicenciatura`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ licenciatura: cursoSelecionado, userId})
        })
        .then(response => response.json())
        .then(data => {
        if (data.success) {
            alert("Sucesso! Para visualizar recarregue.");
        } else {
        alert("ERRO");
        }
        })
        .catch(error => console.error("Erro na adição:", error))
    } else {
        window.alert("Digite um nome válido.");
    }
}




async function deletarMateria() {
    console.log(Cursos)
    let disciplinaId = document.getElementById("nomeInput").value.trim(); // Pega o ID da matéria digitado

    // Verifica se o campo está vazio
    if (!disciplinaId) {
        console.log("Por favor, digite um ID válido.");
        return;
    }

    // Filtra os cursos que contêm a disciplina informada
    let cursosEncontrados = Cursos.filter(curso =>
        curso.disciplinas.some(disciplina => disciplina.id === disciplinaId)
    );

    // Cria um objeto JSON com os cursos encontrados
    let resultadoJSON = cursosEncontrados.map(curso => ({ id: curso.id }))
console.log(resultadoJSON)

     
    try {
        let response = await fetch("/deleteDiscipline", {
            method: "DELETE",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ disciplinaId, userId, cursos: resultadoJSON })
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
    /*
    if (!disciplinaId) {
        alert("Por favor, insira o ID da disciplina para deletar.");
        return;
    }

   */


//-----------------------------------dashboard---------------------

function adicionarLicenciaturas(){
    if(document.getElementById("adcionarLic").innerHTML == ''){
        document.getElementById("adcionarLic").innerHTML += `
        <span>Curso</span>
        <select id="curso">
            <option value="001">ADS</option>
            <option value="002">Engenharia de Software</option>
        </select>
        <button class="positive option" onclick="addLicenciatura()">Enviar</button>`;
    }else{
        document.getElementById("adcionarLic").innerHTML = ''
    }   
}

async function removerLicenciatura(licenciaturaId) {
    try {
        const response = await fetch('/removerlicenciatura', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ userId, licenciatura: licenciaturaId })
        });

        const data = await response.json();

        if (response.ok) {
            alert(data.message);
        } else {
            alert(`Erro: ${data.message || "Falha ao remover licenciatura."}`);
        }
    } catch (error) {
        console.error("Erro ao remover licenciatura:", error);
        alert("Erro ao conectar com o servidor.");
    }
}



function adicionarPeriodo(){
    if(document.getElementById("adcionarLic").innerHTML == ''){
        document.getElementById("adcionarLic").innerHTML += `
        <span>Periodo</span>
        <select id="disponibilidade">
            
            <option value="matutino">Matutino</option>
            <option value="noturno">Noturno</option>
        </select>
        <button class="positive option" onclick="addDisponibilidade()">Enviar</button>`;
    }else{
        document.getElementById("adcionarLic").innerHTML = ''
    }
}

function adicionarModalidade(){
    if(document.getElementById("adcionarLic").innerHTML == ''){
        document.getElementById("adcionarLic").innerHTML += `
        <span>Modalidade</span>
        <select id="Modalidade">
            
            <option value="presencial">Presencial</option>
            <option value="remoto">Remoto</option>
        </select>
        <button class="positive option" onclick="addModalidade()">Enviar</button>`;
    }else{
        document.getElementById("adcionarLic").innerHTML = ''
    }
}





function removerDisponibilidade(periodo) {

    // Envia a requisição para a rota de remoção
    fetch('/remove-disponibilidade', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        userId: userId,
        disponibilidade: periodo,
      }),
    })
    .then(response => response.json())
    .then(data => {
      // Exibe a resposta, pode ser uma mensagem de sucesso ou erro
      alert(data.message || data.error);
    })
    .catch((error) => {
      // Exibe erro se algo falhar
      console.error('Erro ao remover a disponibilidade:', error);
      alert('Erro ao tentar remover a disponibilidade');
    });
  }


function addDisponibilidade() {
    var disponibilidade = document.getElementById("disponibilidade").value;
    

    fetch('/add-disponibilidade', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        userId: userId,
        disponibilidade: disponibilidade,
      }),
    })
    .then(response => response.json())
    .then(data => {
      window.alert(data.message);
    })
    .catch((error) => {
      console.error('Erro:', error);
    });
  }


  function addModalidade() {
    var modalidade = document.getElementById("Modalidade").value;
    fetch('/add-modalidade', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        userId: userId,
        modalidade: modalidade,
      }),
    })
    .then(response => response.json())
    .then(data => {
      window.alert(data.message);
    })
    .catch((error) => {
      console.error('Erro:', error);
    });
  }

  async function removerModalidade(modalidade) {
    try {
        const response = await fetch('/remove-modalidade', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ userId, modalidade })
        });

        const data = await response.json();

        if (response.ok) {
            alert(data.message);
        } else {
            alert(`Erro: ${data.message || "Falha ao remover modalidade."}`);
        }
    } catch (error) {
        console.error("Erro ao remover modalidade:", error);
        alert("Erro na conexão com o servidor.");
    }
}



function updateUserDataInDashboard(userData) {
    document.getElementById("userName").innerText = userData.nome;
    document.getElementById("userCargo").innerText = userData.cargo;

    if (userData.cargo === "professor") {
            document.getElementById("licenciaturas").innerHTML += '<br><strong>Licenciaturas:</strong> <span onclick="adicionarLicenciaturas()" class="option">Adcionar</span>';

            userData.licenciaturas.forEach(element => {
            document.getElementById("licenciaturas").innerHTML += `<p>- ${element[1]}<span onclick="removerLicenciatura('${element[0]}')" class="option negative"> remover</span></p>`
            });
            
            document.getElementById("candidaturas").innerHTML += '<br><strong>Pretendo ministrar: </strong>'
            if (Array.isArray(userData.candidaturas) && userData.candidaturas.length > 0) {
            userData.candidaturas.forEach(element => {
            document.getElementById("candidaturas").innerHTML += `<p>- ${element.nome}<span onclick="removerCandidatura(${element.id})" class="option negative"> remover</span></p>`;
            });
            }

            document.getElementById("periodos").innerHTML += '<br><strong>Estou disponível: </strong><span onclick="adicionarPeriodo()" class="option">Adcionar</span>'
            if (Array.isArray(userData.periodos) && userData.periodos.length > 0) {

            userData.periodos.forEach(element => {
            document.getElementById("periodos").innerHTML += `<p>- ${element}<span onclick="removerDisponibilidade('${element}')" class="option negative"> remover</span></p>`;
            });
            }

            document.getElementById("modalidades").innerHTML += '<br><strong>Modalidades: </strong><span onclick="adicionarModalidade()" class="option">Adcionar</span>'
            if (Array.isArray(userData.periodos) && userData.periodos.length > 0) {

            userData.modalidades.forEach(element => {
            document.getElementById("modalidades").innerHTML += `<p>- ${element}<span onclick="removerModalidade('${element}')" class="option negative"> remover</span></p>`;
            });
            }
    }
}

async function removerCandidatura(id) {
    try {
        const response = await fetch("/remover_candidato", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ userId: userId, codigoDisciplina: id })
        })
        
        if (!response.ok) {
            throw new Error('Erro ao remover candidatura');
        }

        
        location.reload();
    } catch (error) {
        console.error('Erro:', error.message);
    }
}


// Função que renderiza os cursos no front-end
function renderCursos(cursos) {
    Cursos = cursos;
    
    const cursosContainer = document.getElementById("cursos");

    document.getElementById('loadingContainer2').style.display = 'none'
    document.getElementById('cursosEDisciplinas').innerHTML += `<span class="onlyAdmins option positive" onclick="abrirPopup('adicionar','matéria')"> Adicionar</span>
            <span class="onlyAdmins negative option" onclick="abrirPopup('deletar','matéria')"> Deletar</span>`
    

    cursos.forEach(curso => {
      
        
        const cursoTitle = document.createElement("h2");
        cursoTitle.innerHTML = curso.nome + ` <span class="numeroDoCurso"> (${curso.id})</span> (${curso.disciplinas.length})`


        
        cursosContainer.appendChild(cursoTitle);

        // Criando a lista de disciplinas (ul)
        const disciplinaList = document.createElement("ul");

        disciplinaList.classList = "disciplinas"
        curso.disciplinas.forEach(disciplina => {
            const disciplinaItem = document.createElement("li");
            disciplinaItem.innerHTML = `<strong>${disciplina.nome}</strong><span class="onlyAdmins"> (${disciplina.id})</span><br>Carga horária: ${disciplina.carga}h <br>Modalidade: ${disciplina.modalidade}`;
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
    

    let ids = [];
    let number = 0



    
    courses.forEach(course => {
        if (ids.indexOf(course.nome) !== -1) {
            number = number + 1
            console.log(number)
        } else {
            ids.push(course.nome);
            console.log("Adicionando curso:", course.nome);
    
        
   
    
        
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
            <p><strong>Periodo:</strong> ${course.periodo}</p>
        `;
        courseBlock.appendChild(courseInfo);

        // Cria o botão "Me Candidatar"
        const button = document.createElement("button");
        button.classList.add(`positive`);
        button.classList.add(`course${course.id}`);
        button.innerText = "Me Candidatar";
        button.onclick = () => alert(`Candidatura realizada para ${course.nome}`);
        courseBlock.appendChild(button);
        button.addEventListener('click', () => meCandidatar(course.id));


        // Adiciona o bloco de curso à lista
        courseList.appendChild(courseBlock);
        }
    });

    // Atualiza o título com o número de cursos
    document.getElementById('vagasTitle').innerText += ` (${ids.length})`;
   
  
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
            listItem.innerHTML = usuario.nome + (exibirId ? `<span class="onlyAdmins"> (${usuario.id})</span>` : '');
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



function aplicarTransparencia() {
    // Obtém o cookie existente
    let disciplinas = document.cookie
        .split('; ')
        .find(row => row.startsWith('disciplinas='));

    if (disciplinas) {
        try {
            disciplinas = JSON.parse(decodeURIComponent(disciplinas.split('=')[1]));
        } catch (e) {
            disciplinas = [];
        }
    } else {
        disciplinas = [];
    }

    // Aplica a transparência nos elementos correspondentes
    disciplinas.forEach(codigo => {
        let elementos = document.querySelectorAll(`.course${codigo}`);
        elementos.forEach(el => {
            el.style.opacity = "0.5"; // 50% de transparência
            el.innerText = "Candidato"
        });
    });
}



function meCandidatar(codigoDisciplina) {
    let disciplinas = document.cookie
        .split('; ')
        .find(row => row.startsWith('disciplinas='));

    if (disciplinas) {
        // Converte para array (se existir)
        disciplinas = JSON.parse(decodeURIComponent(disciplinas.split('=')[1]));
    } else {
        disciplinas = [];
    }

    // Verifica se a disciplina já está no array
    if (!disciplinas.includes(codigoDisciplina)) {
        disciplinas.push(codigoDisciplina);
        
        // Atualiza o cookie com as disciplinas
        document.cookie = `disciplinas=${encodeURIComponent(JSON.stringify(disciplinas))}; path=/; max-age=15552000`;
    }

    let ID = getCookie("userId");

    if (ID) {   
        fetch("/adicionar_candidato", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                userId: ID,
                codigoDisciplina: codigoDisciplina
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log("Resposta do servidor:", data);

            // Aplica a transparência no botão
            let botao = document.querySelector(".course" + codigoDisciplina);
            if (botao) {
                botao.style.opacity = "0.5";
            }
        })
        .catch(error => {
            console.error("Erro ao se candidatar:", error);
        });
    } else {
        console.log("Erro! Usuário não encontrado.");
    }
}