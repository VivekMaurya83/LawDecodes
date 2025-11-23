document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("loginForm");
    const securityForm = document.getElementById("securityForm");
    const loginSection = document.getElementById("loginSection");
    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");
    const securityAnswerInput = document.getElementById("securityAnswer");
    const securityQuestionText = document.querySelector("#securitySection p");

    let currentUser = null;
    const API_BASE = "http://127.0.0.1:8000";

    // LOGIN FORM SUBMISSION
    loginForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        console.log("🚀 Login form submitted!");
        
        const username = usernameInput.value.trim();
        const password = passwordInput.value.trim();

        try {
            const response = await fetch(`${API_BASE}/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (response.ok) {
                alert("Login successful!");
                window.location.href = "./MainHomePage.html";
            } else if (response.status === 401) {
                alert("Incorrect password. Please answer your security question.");
                await fetchSecurityQuestion(username);
            } else {
                alert("Login failed: " + (data.detail || "Please try again"));
            }
        } catch (error) {
            console.error("Error during login:", error);
            alert("Connection error. Please check if the server is running.");
        }
    });

    // SECURITY FORM SUBMISSION
    securityForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        console.log("🔐 Security form submitted!");
        
        const answer = securityAnswerInput.value.trim();

        try {
            const response = await fetch(`${API_BASE}/verify-security`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    username: currentUser,
                    securityAnswer: answer
                })
            });

            if (response.ok) {
                alert("Security verification successful! Redirecting...");
                window.location.href = "./MainHomePage.html";
            } else {
                alert("Incorrect security answer. Please try again.");
            }
        } catch (error) {
            console.error("Error verifying security answer:", error);
            alert("Verification failed. Please try again.");
        }
    });

    // SHOW SECURITY QUESTION
    async function fetchSecurityQuestion(username) {
        try {
            const response = await fetch(`${API_BASE}/get-security-question/${username}`);
            
            if (response.ok) {
                const data = await response.json();
                currentUser = username;
                securityQuestionText.textContent = data.securityQuestion;

                // Hide login form and show security form
                loginForm.style.display = "none";
                securityForm.style.display = "block";
            } else {
                const errorData = await response.json();
                alert("Error: " + (errorData.detail || "Username not found"));
            }
        } catch (error) {
            console.error("Error fetching security question:", error);
            alert("Failed to load security question. Please try again.");
        }
    }

    // BACK TO LOGIN
    document.getElementById("backToLoginBtn").addEventListener("click", () => {
        securityForm.style.display = "none";
        loginForm.style.display = "block";
        securityAnswerInput.value = "";
        currentUser = null;
    });

    // FORGOT PASSWORD
    document.getElementById("forgotPasswordLink").addEventListener("click", async (event) => {
        event.preventDefault();
        const username = usernameInput.value.trim();
        
        if (!username) {
            alert("Please enter your username first.");
            return;
        }

        await fetchSecurityQuestion(username);
    });
});
