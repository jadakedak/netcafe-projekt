const login_button = document.getElementById("btn-submit");

login_button.addEventListener("click", async (e) => {
    const brugernavn = document.getElementById("brugernavn").value.toLowerCase();
    const adgangskode = document.getElementById("adgangskode").value;

    if(brugernavn && adgangskode) {
        console.log("Attempting login with:", brugernavn, adgangskode);
    } else {
        alert("Please enter both username and password.");
        return;
    }

    try {   
        const response = await fetch("/api/login", {
            method: "POST",
            credentials: "include",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                brugernavn: brugernavn,
                adgangskode: adgangskode
            })
        });

        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                console.log("Login successful");
                window.location.href = `/${data.user_id}/home`; 
            } else {
                alert("Login failed: " + data.message);
            }
        } else {
            alert("An error occurred while logging in.");
        }
    } catch (error) {
        console.error("Error during login:", error);
        alert("An error occurred while logging in.");
    }
})
