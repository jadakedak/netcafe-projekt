
document.getElementById("buy-button").addEventListener("click", async () => {
    const amount = document.getElementById("credit-amount").value
    const response = await fetch(`/api/buy/credits`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({"amount": amount})
    })
    const data = await response.json()
    if(data.success){
        alert(data.message)
    }else{
        alert("Failed to buy credits!")
    }
})