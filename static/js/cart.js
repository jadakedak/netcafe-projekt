
async function getItemsbyId(itemlist){
    const response = await fetch("/api/menu/items/get", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({"items": itemlist})
    })
    const data = await response.json()
    return data
}

let price_total = 0;
let quantity_total = 0

function createCartItem(item_id, navn, beskrivelse, billede_sti, pris, quantity){
    const item_container = document.createElement("li")
    item_container.classList.add("cart-item-container")
    item_container.id = `cart-item-${item_id}`

    const picture = document.createElement("img")
    picture.classList.add("cart-item-picture")
    picture.src = billede_sti
    picture.alt = navn

    const details = document.createElement("div")
    details.classList.add("cart-item-details")

    const name_h2 = document.createElement("h2")
    name_h2.classList.add("cart-item-name")
    name_h2.textContent = navn

    const description_p = document.createElement("p")
    description_p.classList.add("cart-item-description")
    description_p.textContent = beskrivelse

    const price_label = document.createElement("span")
    price_label.classList.add("cart-item-price")
    price_label.textContent = `${pris*quantity} C`

    const quantity_span = document.createElement("span")
    quantity_span.classList.add("cart-item-quantity")
    quantity_span.textContent = `x${quantity}`

    details.appendChild(name_h2)
    details.appendChild(description_p)
    details.appendChild(price_label)
    item_container.appendChild(picture)
    item_container.appendChild(details)
    item_container.appendChild(quantity_span)
    return item_container
}
function calculateTotal(pricequant_list){
    let total = 0
    for(let price in pricequant_list){
        quantity = pricequant_list[price]
        let total_price = price*quantity
        total += total_price
    }
    return total
}

document.getElementById("checkout-button").addEventListener("click", async () => {
    const response = await fetch("/api/checkout", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            "item": "food",
            "price_total": price_total,
            "quantity_total": quantity_total
        })
    })
    const data = await response.json()
    if(!data.success){
        alert(data.message)
    }else{
        alert("items were bought successfully!")
    }
})

document.addEventListener("DOMContentLoaded", async () => {
    let pricelist = {}

    const items = await getItemsbyId(shoppingCart)
    for(let index in items){
        const item = items[index]
        let cartitem = createCartItem(item.id, item.navn, item.beskrivelse, item.billede_sti, item.pris, item.quantity)
        document.getElementById("cart-list").appendChild(cartitem)

        pricelist[item.pris] = item.quantity
        quantity_total += item.quantity
    }
    const total = calculateTotal(pricelist)
    
    price_total = total
    document.getElementById("total").textContent = `${total} C`
})