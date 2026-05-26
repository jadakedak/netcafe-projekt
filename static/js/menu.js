let item_counter = 0
let item_count = document.getElementById("item-count")

document.getElementById("go-to-cart").addEventListener("click", () => {
    window.location.href = `/${userId}/cart`
})

// creates the menu item container along with the elements
function createMenuItem(item_id, navn, beskrivelse, billede_sti, pris){
    const item_container = document.createElement("div")
    item_container.classList.add("menu-item-container")
    item_container.id = `menu-item-${item_id}`

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
    price_label.textContent = `${pris} C`

    const add_to_cart = document.createElement("button")
    add_to_cart.classList.add("menu-item-add-cart")
    add_to_cart.innerHTML = `<label>add</label><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>`
    add_to_cart.addEventListener("click", async () => {
        const response = await fetch(`/api/menu/add_cart/${item_id}`, {
            method: "PUT",
            credentials: "include",
            headers: {
                "Content-Type": "application/json"
            }
        })
        const data = await response.json()
        if(data.success){
            item_counter += 1
            item_count.textContent = item_counter
        }
    })

    details.appendChild(name_h2)
    details.appendChild(description_p)
    details.appendChild(price_label)
    item_container.appendChild(picture)
    item_container.appendChild(details)
    item_container.appendChild(add_to_cart)
    return item_container
}

document.addEventListener("DOMContentLoaded", async () => {
    const response = await fetch("/api/menu/items", {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
    })
    const data = await response.json()
    
    setTimeout(() => {
    for(let item of data.items){
        const new_item = createMenuItem(
            item["id"], 
            item["navn"], 
            item["beskrivelse"], 
            item["billede_sti"],
            item["pris"],
        )
        document.getElementById("menu-container").appendChild(new_item)
    }}, 200)

    const cart_items = await fetch("/api/menu/get_cart", {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
    })
    const items = await cart_items.json()
    if(items.success){
        for(let elem in items["cart"]){
            let quantity = items["cart"][elem]
            item_counter += quantity
        }
        item_count.textContent = item_counter
    }else{
        item_count.textContent = 0
    }
})