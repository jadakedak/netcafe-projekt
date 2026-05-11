const user_container = document.getElementById("user_list");
const admin_container = document.getElementById("admin_user_list");


// User admin handling
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

// Menu admin Handling
const menu_form = document.getElementById("menu_item_form");

const add_button = document.getElementById("add-menu-item")
add_button.addEventListener("click", () => {
    document.getElementById("menu_item_form").style.display = "flex";
});

const close_menu_form_button = document.getElementById("close-form-button");
close_menu_form_button.addEventListener("click", () => {
    menu_form.style.display = "none";
});

const submit_menu_item = document.getElementById("submit-menu-item");
submit_menu_item.addEventListener("click", async (e) => {
    const navn = document.getElementById("menu-item-name").value;
    const beskrivelse = document.getElementById("menu-item-description").value;
    const billede_sti = document.getElementById("menu-item-picture").value;
    const pris = document.getElementById("menu-item-price").value;
        
    if(!navn || !beskrivelse || !pris || isNaN(pris)){
        return alert("Navn, beskrivelse og gyldig pris er påkrævet!");
    }
    
    const item_details = await addMenuItemDB(navn, beskrivelse, billede_sti, pris);
    const menuItem = createMenuItem(item_details["item_id"], navn, beskrivelse, billede_sti, pris);

    document.getElementById("menu_list").appendChild(menuItem);
    menu_form.style.display = "none";
});


function createMenuItem(item_id, navn, beskrivelse, billede_sti, pris){
    const item_container = document.createElement("div")
    item_container.classList.add("menu-item-container")
    item_container.id = `menu-item-${item_id}`

    const remove_button = document.createElement("button")
    remove_button.classList.add("remove-menu-item")
    remove_button.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>`
    remove_button.addEventListener("click", () => {
        removeMenuItem(item_id);
        removeMenuItemDB(item_id);
    });

    const picture = document.createElement("img")
    picture.classList.add("menu-item-picture")
    picture.src = billede_sti
    picture.alt = navn

    const details = document.createElement("div")
    details.classList.add("menu-item-details")

    const name_h2 = document.createElement("h2")
    name_h2.classList.add("menu-item-name")
    name_h2.textContent = navn

    const description_p = document.createElement("p")
    description_p.classList.add("menu-item-description")
    description_p.textContent = beskrivelse

    const price_label = document.createElement("span")
    price_label.classList.add("menu-item-price")
    price_label.textContent = `${pris} kr`

    details.appendChild(name_h2)
    details.appendChild(description_p)
    details.appendChild(price_label)
    item_container.appendChild(picture)
    item_container.appendChild(details)
    item_container.appendChild(remove_button)
    return item_container
}
function removeMenuItem(item_id){
    const item_element = document.getElementById(`menu-item-${item_id}`);
    if(item_element){
        item_element.remove();
    }
}

async function addMenuItemDB(navn, beskrivelse, billede_sti, pris) {
    const response = await fetch("/api/menu/items/add", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            navn: navn,
            beskrivelse: beskrivelse,
            billede_sti: billede_sti,
            pris: pris
        })
    });
    const data = await response.json();
    if (!data.success) {
        alert("Failed to add menu item: " + data.message);
    }
    return data;
}
async function removeMenuItemDB(item_id) {
    const response = await fetch(`/api/menu/items/remove/${item_id}`, {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json"
        },
    });
    const data = await response.json();
    if (!data.success) {
        alert("Failed to remove menu item: " + data.message);
    }
    return data;
}

async function displayMenuItems(){
    const response = await fetch("/api/menu/items", {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
    });
    const data = await response.json();
    const menu_list = document.getElementById("menu_list");
    menu_list.innerHTML = "";
    data.items.forEach(item => {
        const menuItem = createMenuItem(item.id, item.navn, item.beskrivelse, item.billede_sti, item.pris);
        menu_list.appendChild(menuItem);
    });
}


document.addEventListener("DOMContentLoaded", () => {
    displayMenuItems();
    displayUsers();
});