async function insert_transaction(item, amount){
    const response = await fetch(`/api/transactions/insert`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            "item": item, 
            "amount": amount,
            "total": null
        })
    })
    const data = await response.json()
    if(data.success){
        console.log(`Transaction of ${amount} credits is complete!`)
    }else{
        console.log("Transaction logging failed!")
    }
}

document.getElementById("buy-button").addEventListener("click", async () => {
    const amount = document.getElementById("credit-amount").value
    const item = "credits"
    const response = await fetch(`/api/buy/credits`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({"item": item, "amount": amount})
    })
    const data = await response.json()
    if(data.success){
        insert_transaction(item, amount)
        alert(data.message)
    }else{
        alert("Failed to buy credits!")
    }
})
