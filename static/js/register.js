function validateRegistrationForm(){
    const fornavn = document.getElementById("fornavn").value;
    const efternavn = document.getElementById("efternavn").value;
    const email = document.getElementById("email").value;

    const username = document.getElementById("brugernavn").value;
    const password = document.getElementById("adgangskode").value;

    if(!fornavn || !efternavn || !email || !username || !password){
        return false;
    }
    if(!email.includes("@")){
        return false;
    }
    if(password.length < 8){
        return false;
    }
    return true;
}

async function SendUserRegistration(){
    const fornavn = document.getElementById("fornavn").value;
    const efternavn = document.getElementById("efternavn").value;
    const email = document.getElementById("email").value;

    const username = document.getElementById("brugernavn").value;
    const password = document.getElementById("adgangskode").value;

    const data = {
        fornavn: fornavn,
        efternavn: efternavn,
        email: email,
        username: username,
        password: password,
        credits: 0
    }

    const response = await fetch("/api/register", {
        method: "POST",
        credentials: "include",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
    const result = await response.json();

    if(result.message === "User registered successfully"){
        document.getElementById("success-overlay").classList.add("visible");
        setTimeout(() => {
            window.location.href = "/login";
        }, 2500);
    }else{
        alert("Registration failed: " + result.message);
    }
}

document.getElementById("btn-submit").addEventListener("click", async (e) => {
    e.preventDefault();
    if(validateRegistrationForm()){
        await SendUserRegistration();
    }
})
