document.getElementById("sign-up-form").addEventListener("submit", async function(event) {
    event.preventDefault(); // Prevents form submission and page reload

    // Get input values
    const username = document.getElementById("username").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {
        const response = await fetch("http://127.0.0.1:5000/sign-up-api", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username,
                email,
                password
            })
        });

        const responseData = await response.json();

        if (response.ok) {
            alert(responseData.message)
        } else {
            console.error("Error:", responseData);
        }
    } catch (error) {
        console.error("Error signing up:", error);
    }
});

