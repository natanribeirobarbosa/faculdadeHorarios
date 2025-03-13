



//função que busca nome e cargo atual
function fetchUserData(userId) {
    fetch(`http://127.0.0.1:5000/user/${userId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success){
                document.getElementById("userName").innerText = data.user.nome;
                document.getElementById("userCargo").innerText = data.user.cargo;
               
            } else {
                alert("Erro ao carregar usuário.");
            }
        })
        .catch(error => console.error("Erro ao buscar usuário:", error));
}

var admin = false

//função que busca todos os nomes e usuarios
function fetchAllUserData(userId) {
    fetch(`http://127.0.0.1:5000/allusers/${userId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success){
                if(data.user.cargo == 'admin'){
                    admin = true
                }

       
                

                
                const admins = data.user.users.users_by_cargo.admin;
                const prof = data.user.users.users_by_cargo.professor;
                const cord = data.user.users.users_by_cargo.coordenador;
                const users = data.user.users.users_by_cargo.user;
                //const cursos = data.user.cursos;
                //console.log(cursos);
                // Seleciona o elemento onde os <li> serão adicionados
                const listAdmin = document.getElementById('admins');
                const listProf = document.getElementById('professores'); 
                const listCord = document.getElementById('coordenadores');
                const listUsers = document.getElementById('usuarios'); 

                // Cria os <li> para cada admin
                admins.forEach(admin => {
                const listItem = document.createElement('li');
                listItem.innerHTML = admin.nome;  
                listAdmin.appendChild(listItem);
                });

                prof.forEach(admin => {
                const listItem = document.createElement('li');
                listItem.innerHTML = admin.nome+'<span class="onlyAdmins"> ('+admin.id+')</span>'
                listProf.appendChild(listItem);
                });

                cord.forEach(admin => {
                const listItem = document.createElement('li');
                listItem.innerHTML = admin.nome+'<span class="onlyAdmins"> ('+admin.id+')<span>';
                listCord.appendChild(listItem);
                });

                users.forEach(admin => {
                const listItem = document.createElement('li');
                listItem.innerHTML = admin.nome+'<span class="onlyAdmins"> ('+admin.id+')<span>';
                listUsers.appendChild(listItem);
                });

                if(admin == true){
                    var elementos = document.querySelectorAll('.onlyAdmins');
                                    elementos.forEach(function(elemento) {
                                        elemento.style.display = 'inline';
                                
                                });

                    
                }

                
            } else {
                alert("Erro ao carregar usuários.");
            }
        })
        .catch(error => console.error("Erro ao buscar usuário:", error));
}

//função que busca todos os cursos e disciplinas
function fetchAllCurses() {
    fetch('http://127.0.0.1:5000/allcourses')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const cursosContainer = document.getElementById("cursos");

            data.cursos.forEach(curso => {
                // Criando o título do curso (h2)
                const cursoTitle = document.createElement("h2");
                cursoTitle.innerHTML = curso.nome+`<span class="onlyAdmins" onclick="abrirPopup('matéria')"> Adicionar</span><span class="onlyAdmins negative" onclick="popUpDeletar('matéria')"> Deletar</span>`
                cursosContainer.appendChild(cursoTitle);

                // Criando a lista de disciplinas (ul)
                const disciplinaList = document.createElement("ul");

                curso.disciplinas.forEach(disciplina => {
                    const disciplinaItem = document.createElement("li");
                    disciplinaItem.innerHTML = '<strong>'+disciplina.nome+'</strong>'+'<br>Carga horária: '+disciplina.carga+'h <br>modalidade: '+disciplina.modalidade
                    disciplinaList.appendChild(disciplinaItem);
                });

                cursosContainer.appendChild(disciplinaList);

                if(admin == true){
                    var elementos = document.querySelectorAll('.onlyAdmins');
                                    elementos.forEach(function(elemento) {
                                        elemento.style.display = 'inline';
                                
                                });

                    
                }
            });
        } else {
            alert("Erro ao carregar cursos.");
        }
    })
    .catch(error => console.error("Erro ao buscar cursos:", error));
}
