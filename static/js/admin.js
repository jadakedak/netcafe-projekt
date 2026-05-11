const user_container = document.getElementById("user_list");
const admin_container = document.getElementById("admin_user_list");

async function getUsers(){
    const response = await fetch("/api/users", {
        method: "GET",
        credentials: "include",
        headers: {
            "Content-Type": "application/json"
        }
    })
    const data = await response.json();
    return data.users;
}

function createuserItem(user){
    const userDiv = document.createElement("div");
    if(user.is_admin){
        userDiv.classList.add("admin-item");
    }else{
        userDiv.classList.add("user-item");
    }
    userDiv.innerHTML = `
        <div class="user-avatar">${user.fornavn[0]}${user.efternavn[0]}</div>
        <div class="user-details">
            <span class="user-name">${user.fornavn} ${user.efternavn}</span>
            <span class="user-username">@${user.brugernavn}</span>
        </div>
        <span class="user-email">${user.email}</span>
    `;
    return userDiv;
}

async function displayUsers(){
    const users = await getUsers();
    user_container.innerHTML = "";
    users.forEach(user => {
        const userDiv = document.createElement("div");
        const userItem = createuserItem(user);
        if(user.is_admin){
            userDiv.classList.add("admin-item");
            admin_container.appendChild(userItem);
        }else{
            userDiv.classList.add("user-item");
            user_container.appendChild(userItem);
        }
    });
}

document.addEventListener("DOMContentLoaded", () => {
    displayUsers();
});