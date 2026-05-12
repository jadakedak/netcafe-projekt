async function Getuserid(){
    const response = await fetch("/api/me", {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
    })
    const data = await response.json();
    return data.user_id
}

document.addEventListener("DOMContentLoaded", async () => {
    const logged_in = Getuserid()
    if(logged_in.user_id){
        console.log("user is logged in!")
    }
});