
function fecharPopup() {
    document.getElementById("popup").classList.remove("active");
    document.getElementById("nomeInput").value = "";
}

function popUpDeletar(cargo) {
    document.getElementById("nomePopup").innerText='Deletar '+cargo
    document.getElementById("popup").classList.add("active");
    document.getElementById('nomeInput').placeholder = 'Código de acesso do '+cargo;
    document.getElementById("sendButton").addEventListener("click", deletarNome);

}


function abrirPopup(lista) {
    document.getElementById("nomePopup").innerText='Adicionar '+lista
    listaAtual = lista;
    document.getElementById("popup").classList.add("active");
    document.getElementById('nomeInput').placeholder = 'Digite o nome da(o) '+lista;
    document.getElementById("sendButton").addEventListener("click", adicionarNome);

}
