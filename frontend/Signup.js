document.addEventListener("DOMContentLoaded", () => {
    const moveForwardBtn = document.getElementById("moveForwardBtn");
    const signupForm = document.getElementById("signupForm");
    const signupFields = document.getElementById("signupFields");
    const securitySection = document.getElementById("securitySection");
    const backToSignupBtn = document.getElementById("backToSignupBtn");

    const usernameInput = document.getElementById("username");
    const emailInput = document.getElementById("email");
    const passwordInput = document.getElementById("password");
    const confirmPasswordInput = document.getElementById("confirmPassword");
    const securityQuestionSelect = document.getElementById("securityQuestionSelect");
    const securityAnswerInput = document.getElementById("securityAnswer");
    const termsCheckbox = document.getElementById("terms");

    // --- Password Validation Elements ---
    const lengthCheck = document.getElementById("length");
    const capitalCheck = document.getElementById("capital");
    const numberCheck = document.getElementById("number");
    const matchCheck = document.getElementById("match");

    // --- Real-time Password Validation ---
    function validatePassword() {
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;
        let allValid = true;

        // Check length
        if (password.length >= 6) {
            lengthCheck.className = 'valid';
        } else {
            lengthCheck.className = 'invalid';
            allValid = false;
        }
        
        // Check for a capital letter
        if (/[A-Z]/.test(password)) {
            capitalCheck.className = 'valid';
        } else {
            capitalCheck.className = 'invalid';
            allValid = false;
        }

        // Check for a number
        if (/\d/.test(password)) {
            numberCheck.className = 'valid';
        } else {
            numberCheck.className = 'invalid';
            allValid = false;
        }

        // Check if passwords match
        if (password && password === confirmPassword) {
            matchCheck.className = 'valid';
        } else {
            matchCheck.className = 'invalid';
            allValid = false;
        }

        return allValid;
    }
    passwordInput.addEventListener('input', validatePassword);
    confirmPasswordInput.addEventListener('input', validatePassword);


    async function populateSecurityQuestions() {
        try {
            const response = await fetch('http://127.0.0.1:8000/security-questions');
            if (!response.ok) throw new Error("Could not fetch security questions.");
            const data = await response.json();
            const questions = data.questions;
            securityQuestionSelect.innerHTML = '<option value="">-- Please select a question --</option>';
            for (const id in questions) {
                const option = document.createElement("option");
                option.value = id;
                option.textContent = questions[id];
                securityQuestionSelect.appendChild(option);
            }
        } catch (error) {
            console.error("Error populating security questions:", error);
            alert("Failed to load security questions. Please ensure the backend server is running.");
        }
    }
    populateSecurityQuestions();

    moveForwardBtn.addEventListener("click", (e) => {
        e.preventDefault();
        
        if (!usernameInput.value.trim() || !emailInput.value.trim()) {
            alert("Please fill in username and email fields.");
            return;
        }
        if (!validatePassword()) {
            alert("Please ensure your password meets all the requirements.");
            return;
        }
        if (!termsCheckbox.checked) {
            alert("You must agree to the Terms & Conditions.");
            return;
        }
        
        signupFields.style.display = "none";
        securitySection.style.display = "block";
    });

    backToSignupBtn.addEventListener("click", (e) => {
        e.preventDefault();
        signupFields.style.display = "block";
        securitySection.style.display = "none";
    });

    signupForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (!validatePassword() || !termsCheckbox.checked) {
            alert("Please ensure all fields are correct and terms are accepted.");
            return;
        }
        if (!securityQuestionSelect.value || !securityAnswerInput.value.trim()) {
            alert("Please select a security question and provide an answer.");
            return;
        }

        const userData = {
            username: usernameInput.value.trim(),
            email: emailInput.value.trim(),
            password: passwordInput.value.trim(),
            securityQuestion: parseInt(securityQuestionSelect.value, 10),
            securityAnswer: securityAnswerInput.value.trim()
        };

        try {
            const response = await fetch('http://127.0.0.1:8000/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(userData),
            });

            if (response.ok) {
                alert("Account created successfully! You can now login.");
                window.location.href = "Login.html"; 
            } else {
                const errorData = await response.json();
                alert(`Signup failed: ${errorData.detail}`);
            }
        } catch (error) {
            console.error("Error during signup:", error);
            alert("An error occurred. Please try again later.");
        }
    });
});
