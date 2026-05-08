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

document.addEventListener("DOMContentLoaded", async () => {
    const profileInfo = await getProfileInfo();
    if (profileInfo) {
        document.getElementById("username").textContent = profileInfo.username;
        document.getElementById("email").textContent = profileInfo.email;
        // Add more fields as needed
    }
});
