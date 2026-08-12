const API_URL = "http://127.0.0.1:8000/" 

let navLists = document.getElementById("side-bar-lists");
let todolist = document.getElementById("main-lists");

async function get_todo_lists(todo_id){
    try{
        let userId = localStorage.getItem("userId");
        let token = localStorage.getItem("jwtToken");
        let request = await fetch(API_URL+`todo/${userId}?token=${token}`);
        let data = await request.json();
        if (!request.ok){
            throw new Error(data.detail);
        }

        for (let todo of data){
            let sideBarLi = document.createElement("li");
            sideBarLi.className = 'nav-link'
            sideBarLi.innerHTML = `
            <button onclick='direct(${todo.id})'>${todo.title ? todo.title : "No title"}</button>
            `;

            navLists.appendChild(sideBarLi);
        }

        let sideBarAdd = document.createElement("li");
        sideBarAdd.className = 'nav-link';
        sideBarAdd.innerHTML = `
            <button onclick='direct(-1)'>New Todo list</button> 
        `
        navLists.appendChild(sideBarAdd);

        if (todo_id){
            if (todo_id == -1){
                let todoDiv = document.createElement("div");
                todoDiv.className = "todo";
                todoDiv.innerHTML = `
                    <input type='text' id='todo-title' class='todo-title' placeholder='Title'>
                    <div contenteditable="true" id='todo-content' class='todo-content' placeholder='todo: eat breakfast'></div>
                    <button onclick='addTodo()' class='save-btn'>save</button>
                `;
                todolist.appendChild(todoDiv);
                return;
            }
            for (let todo of data){
                if (todo.id == todo_id){
                    let todoDiv = document.createElement("div");
                    todoDiv.className = "todo";
                    let parsedHtml = parseContent(todo.content);
                    todoDiv.innerHTML = `
                        <input type='text' id='todo-title' class='todo-title' placeholder='Title' value='${todo.title}'>
                        <div contenteditable="true" id='todo-content' class='todo-content' placeholder='todo: eat breakfast'>${parsedHtml}</div>
                        <button onclick='editTodo(${todo.id})' class='save-btn'>save</button>
                    `;

                    todolist.appendChild(todoDiv);
                }
            }
        }
        else {
            todolist.innerHTML = `
                <h1>No todo list selected</h1>
                <p>select your todo list from the side bar</p>
            `
        }
    }
    catch(e){
        console.log(e);
    }
}

function parseContent(content){
    if (!content) return '';

    let result = content;

    result = result.replace(/\[\/\]/g,"<input type='checkbox' checked>");
    result = result.replace(/\[\s\]/g,"<input type='checkbox'>");

    result = result.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");

    result = result.replace(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g, "<em>$1</em>");

    return result
}

function parseHTML(Html){
    if (!Html) return;

    let result = Html;

    result = result.replace(/<input[^>]*type=['"]checkbox['"][^>]*checked[^>]*>/gi, "[/]");

    result = result.replace(/<input[^>]*type=['"]checkbox['"][^>]*>/gi, "[ ]");

    result = result.replace(/<strong>(.*?)<\/strong>/gi, "**$1**");

    result = result.replace(/<em>(.*?)<\/em>/gi, "*$1*");

    result = result.replace(/<br\s*\/?>/gi, "\n");
    result = result.replace(/<\/div><div>/gi, "\n");
    result = result.replace(/<\/?div[^>]*>/gi, "\n");

    return result;
}

function direct(id){
    window.location.href = window.location.origin + window.location.pathname + `?id=${id}`;
}

async function addTodo(){
    let title = document.getElementById("todo-title").value;
    let content = document.getElementById("todo-content").innerHTML;
    let token = localStorage.getItem("jwtToken");
    try {
        let request = await fetch(API_URL+"add_todo/",{
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body:JSON.stringify({
                token: token,
                title: title,
                content: parseHTML(content)
            })
        });
        let data = await request.json();
        if (!request.ok){
            throw new Error(data.detail);
        }
    }
    catch(e){
        console.log(e);
    }
}

async function editTodo(id){
    let title = document.getElementById("todo-title").value;
    let content = document.getElementById("todo-content").innerHTML;
    let token = localStorage.getItem("jwtToken");
    try {
        let request = await fetch(API_URL+"edit_todo",{
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                token:token,
                id:id,
                title:title,
                content:parseHTML(content)
            })
        })
        let data = await request.json();
        if (!request.ok){
            throw new Error(data.detail);
        }
    }
    catch(e){
        console.log(e)
    }
}

document.addEventListener("DOMContentLoaded", async (e) => {
    let urlParams = new URLSearchParams(window.location.search);

    let id = urlParams.get("id");


    await get_todo_lists(id);

    contentArea = document.getElementById("todo-content");

    contentArea.addEventListener("input",(e)=>{
        e.preventDefault();
        contentArea.innerHTML = parseContent(contentArea.innerHTML);
        const range = document.createRange();
        const selection = window.getSelection();

        range.selectNodeContents(contentArea);
        range.collapse(false);

        selection.removeAllRanges();
        selection.addRange(range);
        contentArea.focus();
    })

    contentArea.addEventListener("click", (e)=>{
        if (e.target && e.target.type === "checkbox") {
            const isChecked = e.target.checked;
            
            if (isChecked) {
                e.target.setAttribute("checked", "checked");
            } else {
                e.target.removeAttribute("checked");
            }

            let currentMarkdown = parseHTML(contentArea.innerHTML);
            contentArea.innerHTML = parseContent(currentMarkdown);

            contentArea.dispatchEvent(new Event('input', { bubbles: true }));
        }
    })
})

