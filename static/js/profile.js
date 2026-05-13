async function getProfileInfo() {
    const response = await fetch("/api/profileinfo", {
        method: "GET",
        credentials: "include",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ userid: userId })
    });

    if (!response.ok) {
        console.error("Failed to fetch profile info:", response.status);
        return null;
    }
    return await response.json();
}

async function LoadTransactions(){
    const response = await fetch("/api/transactions/history", {
        method: "GET",
        headers: {
            "Content-Type": "application/jsons"
        }
    })
    const data = await response.json()
    return data
}

function CreateTransaction(transaction_id, item, amount, total, purchased_at){
    const item_container = document.createElement("div")
    item_container.classList.add("transaction-container")
    item_container.id = `transaction-${transaction_id}`

    const item_span = document.createElement("span")
    item_span.classList.add("transaction-item")
    item_span.textContent = item

    const amount_span = document.createElement("span")
    amount_span.classList.add("transaction-amount")
    amount_span.textContent = `x${amount}`

    const total_span = document.createElement("span")
    total_span.classList.add("transaction-total")
    if(total != null){
        total_span.textContent = `${total} C`
    }
 
    const date_span = document.createElement("span")
    date_span.classList.add("transaction-date")
    date_span.textContent = purchased_at

    item_container.appendChild(item_span)
    item_container.appendChild(amount_span)
    if(total != null){
        item_container.appendChild(total_span)
    }
    item_container.appendChild(date_span)
    return item_container
}

document.addEventListener("DOMContentLoaded", async () => {
    const user_transactions = await LoadTransactions()
    for(let index in user_transactions.transactions){
        let transaction = user_transactions.transactions[index]
        const transaction_object = CreateTransaction(transaction.transaction_id, transaction.item, transaction.amount, transaction.total, transaction.purchased_at)
        document.getElementById("transaction-history").appendChild(transaction_object)
    }
});
