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

//função que busca todos os nomes e usuarios
function fetchAllUserData(userId) {
    fetch(`http://127.0.0.1:5000/allusers/${userId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success){

                
                const admins = data.user.users.users_by_cargo.admin;
                const prof = data.user.users.users_by_cargo.professor;
                const cord = data.user.users.users_by_cargo.coordenador;
                const users = data.user.users.users_by_cargo.user;
                //const cursos = data.user.cursos;
                //console.log(cursos);
                console.log(data)

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


                if(data.user.cargo == 'admin'){
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
    
}