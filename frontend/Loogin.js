document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("loginForm");
    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");

    const forgotPasswordLink = document.getElementById("forgotPasswordLink");
    const loginSection = document.getElementById("loginSection");
    const securitySection = document.getElementById("securitySection");
    const backToLoginBtn = document.getElementById("backToLoginBtn");
    const securityForm = document.getElementById("securityForm");
    const securityQuestionText = document.getElementById("securityQuestionText");
    const securityAnswerInput = document.getElementById("securityAnswer");
    const securityMessage = document.getElementById("securityMessage");

    // Try multiple backend base URLs in order. This handles cases where the
    // frontend static server (python -m http.server) is running on port 8000
    // and the backend is on a different port. We'll cache the working base.
    const baseCandidates = [];
    const origin = window.location.origin;
    if (origin && origin !== 'null' && origin !== 'file://') baseCandidates.push(origin);
    // common local backends to try
    baseCandidates.push('http://127.0.0.1:8000');
    baseCandidates.push('http://127.0.0.1:8001');
    baseCandidates.push('http://localhost:8000');
    let chosenBase = null;
    console.debug('[Loogin] baseCandidates =', baseCandidates);

    loginForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        
        // --- THIS IS THE CRITICAL FIX ---
        // The backend's OAuth2 endpoint expects 'x-www-form-urlencoded' data.
        const body = new URLSearchParams();
        body.append('username', usernameInput.value.trim());
        body.append('password', passwordInput.value.trim());

        try {
            const response = await fetch('http://127.0.0.1:8000/login', {
                method: 'POST',
                headers: {
                    // Set the correct content type for the backend to understand.
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: body // Send the correctly formatted body
            });

            const data = await response.json();
            if (!response.ok) {
                // Handle specific 401 error to trigger the forgot password flow
                if (response.status === 401) {
                    if (confirm("Incorrect username or password. Would you like to try recovering your account?")) {
                        forgotPasswordLink.click();
                    }
                } else {
                    alert(`Login failed: ${data.detail || 'An unknown error occurred.'}`);
                }
                return;
            }

            if (data.access_token) {
                // CRUCIAL: If login is successful, save the token to local storage.
                localStorage.setItem('access_token', data.access_token);
                alert("Login successful!");
                window.location.href = "./MainHomePage.html"; 
            } else {
                alert("Login failed: No access token was received from the server.");
            }
        } catch (error) {
            console.error("Login error:", error);
            alert("Could not connect to the server. Please ensure it is running.");
        }
    });

    forgotPasswordLink.addEventListener("click", async (e) => {
        e.preventDefault();
        const username = usernameInput.value.trim();
        if (!username) {
            alert("Please enter your username first to recover your password.");
            return;
        }

        try {
            // Try each candidate base until one returns a 200 OK for this path.
            let data = null;
            let ok = false;
            for (const base of baseCandidates) {
                const url = `${base.replace(/\/$/, '')}/get-security-question/${encodeURIComponent(username)}`;
                console.debug('[Loogin] trying', url);
                try {
                    const response = await fetch(url);
                    if (!response.ok) {
                        const txt = await response.text().catch(()=>null);
                        console.warn('[Loogin] non-ok', response.status, txt);
                        continue;
                    }
                    // parse JSON or text
                    try { data = await response.json(); } catch { data = { securityQuestion: await response.text() } }
                    chosenBase = base;
                    ok = true;
                    break;
                } catch (err) {
                    console.warn('[Loogin] fetch failed for', url, err);
                    continue;
                }
            }

            if (!ok) {
                alert('Could not reach backend to fetch security question. Check that the backend is running.');
                return;
            }

            securityQuestionText.textContent = data.securityQuestion || data;
            loginSection.style.display = "none";
            securitySection.style.display = "block";

        } catch (error) {
            console.error("Error fetching security question:", error);
            alert("Could not connect to the server.");
        }
    });

    backToLoginBtn.addEventListener("click", () => {
        loginSection.style.display = "block";
        securitySection.style.display = "none";
    });

    securityForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        securityMessage && (securityMessage.textContent = '');
        const username = usernameInput.value.trim();
        const answer = securityAnswerInput.value.trim();
        if (!username || !answer) {
            securityMessage && (securityMessage.textContent = 'Please provide your answer.');
            return;
        }

        try {
            // Use chosenBase if found during question fetch, otherwise try candidates.
            const verifyBases = chosenBase ? [chosenBase, ...baseCandidates] : baseCandidates;
            let verified = false;
            let lastErr = null;
            for (const base of verifyBases) {
                const url = `${base.replace(/\/$/, '')}/verify-security`;
                try {
                    const res = await fetch(url, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ username: username, securityAnswer: answer })
                    });

                    if (res.ok) {
                        // try to read token from response
                        try {
                            const payload = await res.json();
                            if (payload && payload.access_token) {
                                localStorage.setItem('access_token', payload.access_token);
                                // also remember token for redirect as a fallback
                                window.__LOOGIN_SAVED_TOKEN = payload.access_token;
                            }
                        } catch (e) {
                            // ignore parse errors
                        }
                        verified = true;
                        break;
                    }

                    if (res.status === 401) { lastErr = { type: 'unauthorized' }; break; }

                    const bodyText = await res.text().catch(()=>res.statusText);
                    lastErr = { type: 'other', body: bodyText };
                } catch (err) {
                    console.warn('[Loogin] verify fetch failed for', url, err);
                    lastErr = { type: 'network', err };
                    continue;
                }
            }

            if (verified) {
                // verified
                securityMessage && (securityMessage.style.color = '#0b6623');
                securityMessage && (securityMessage.textContent = 'Verified — you can now sign in or reset your password. Redirecting...');
                // small delay so user sees message
                setTimeout(() => {
                    // In this simple flow we redirect to main page; in a full flow we'd show a reset-password form.
                    // If we captured a token, include it as a query param so other pages can pick it up reliably.
                    const token = window.__LOOGIN_SAVED_TOKEN || localStorage.getItem('access_token');
                    if (token) {
                        window.location.href = `./MainHomePage.html?access_token=${encodeURIComponent(token)}`;
                    } else {
                        window.location.href = './MainHomePage.html';
                    }
                }, 900);
                return;
            }
            // After attempts, inspect lastErr
            if (lastErr && lastErr.type === 'unauthorized') {
                securityMessage && (securityMessage.style.color = '#b91c1c');
                securityMessage && (securityMessage.textContent = 'Incorrect answer — please try again.');
                return;
            }
            securityMessage && (securityMessage.style.color = '#b91c1c');
            securityMessage && (securityMessage.textContent = 'Verification failed. Ensure the backend is running and try again.');
        } catch (err) {
            console.error('Verification error outer catch:', err);
            securityMessage && (securityMessage.style.color = '#b91c1c');
            securityMessage && (securityMessage.textContent = 'Could not connect to server.');
        }
    });
});