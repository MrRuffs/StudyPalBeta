document.addEventListener("DOMContentLoaded", function () {
    const access_token = localStorage.getItem("access_token");
    const username = "Ibrahim";  // Replace with dynamic user data
    document.getElementById("username").textContent = username;
});