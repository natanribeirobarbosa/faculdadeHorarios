



//função que busca nome e cargo atual
function fetchUserData(userId) {
    fetch(`/user/${userId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success){
                console.log('sucesso')
                document.getElementById("userName").innerText = data.user.nome;
                document.getElementById("userCargo").innerText = data.user.cargo;
                if(data.user.cargo == "professor"){
                    

                    document.getElementById("userCargo").innerHTML += "<br>licenciaturas:"
                    if(typeof data.user.licenciaturas !== "undefined" && typeof data.user.licenciaturas !== null){
                        console.log(data.user.licenciaturas
                        )

                        data.user.licenciaturas.forEach(element => {
                            console.log(element)
                            document.getElementById("userCargo").innerHTML += '<br>- '+element
                        });
                    }
                    renderCursosIndex()
                    console.log('resfdsffd')
               }
               
               
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

                
                document.getElementById('administradoresTitle').innerText += ' ('+data.user.users.users_by_cargo.admin.length+')'
                document.getElementById('professoresTitle').innerText += ' ('+data.user.users.users_by_cargo.professor.length+')'
                document.getElementById('coordenadoresTitle').innerText += ' ('+data.user.users.users_by_cargo.coordenador.length+')'
                document.getElementById('usuariosTitle').innerText += ' ('+data.user.users.users_by_cargo.user.length+')'

                
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
    return fetch('/allcourses')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            return data.cursos; // Retorna os cursos para outra função
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
