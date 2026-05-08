document.addEventListener("DOMContentLoaded", async () => {
    const response = await fetch("/api/me", {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
    })
    const data = await response.json();
    console.log("logged in:", data.logged_in, "user_id:", data.user_id);
});

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

console.log("User ID:", Getuserid());