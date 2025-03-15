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

