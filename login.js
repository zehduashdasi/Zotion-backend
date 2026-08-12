const API_URL = "http://127.0.0.1:8000/"

async function login(){
    let username = document.getElementById("LoginUsername").value;
    let password = document.getElementById("LoginPassword").value;

    try{
        let request = await fetch(API_URL+"login/",{
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body:JSON.stringify({
                username: username,
                password: password
            })
        });
        let data = await request.json();
        if (!request.ok){
            throw new Error(data.detail);
        }
        let token = data.token;
        let id = data.id;
        localStorage.setItem("jwtToken",token);
        localStorage.setItem("userId",id);
        window.location.href = 'index.html';
    }
    catch(e){
        document.getElementById("msg").innerHTML = e;
    }
}

async function register(){
    let username = document.getElementById("RegisterUsername").value;
    let password = document.getElementById("RegisterPassword").value;
    try{
        let request = await fetch(API_URL+"register/", {
            method: 'POST',
            headers: {
                'Content-Type':'application/json'
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        })
        let data = await request.json();
        if (!request.ok){
            throw new Error(data.detail)
        }
        
        console.log(request);
        let token = data.token;
        let id = data.id;
        localStorage.setItem("jwtToken",token);
        localStorage.setItem("userId",id);
        
    }
    catch(e){
        console.log(e);
        document.getElementById("msg").innerHTML = e;
    }
}


try{
    document.getElementById("login-btn").addEventListener("click", login);
}
catch(e){
    document.getElementById("register-btn").addEventListener("click", register);
}






