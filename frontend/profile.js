document.addEventListener("DOMContentLoaded", () => {
    const API_BASE_URL = "http://127.0.0.1:8000";
    // Accept token from query param as fallback (after verification redirect)
    const urlParams = new URLSearchParams(window.location.search);
    const tokenFromParam = urlParams.get('access_token');
    if (tokenFromParam) {
        localStorage.setItem('access_token', tokenFromParam);
        // remove param from URL to keep it clean
        urlParams.delete('access_token');
        const newUrl = window.location.pathname + (urlParams.toString() ? '?' + urlParams.toString() : '');
        window.history.replaceState({}, '', newUrl);
    }
    const token = localStorage.getItem('access_token');
    
    if (!token) {
        alert("You are not logged in. Please log in to view your profile.");
        window.location.href = "./Login.html";
        return;
    }

    const nameInput = document.getElementById("name");
    const emailInput = document.getElementById("email");
    const saveButton = document.getElementById("save-profile-button");
    const chatHistorySelect = document.getElementById("chat-history");

    const authHeaders = {
        'Authorization': `Bearer ${token}`
    };

    async function loadProfile() {
        try {
            const response = await fetch(`${API_BASE_URL}/api/profile`, { headers: authHeaders });
            
            if (response.status === 401) {
                alert("Your session has expired. Please log in again.");
                localStorage.removeItem('access_token');
                window.location.href = "./Login.html";
                return;
            }
            if (!response.ok) throw new Error('Failed to fetch profile');

            const data = await response.json();
            nameInput.value = data.name || '';
            emailInput.value = data.email || '';
        } catch (error) {
            console.error("Error loading profile:", error);
        }
    }

    async function loadChatHistory() {
        try {
            const response = await fetch(`${API_BASE_URL}/api/chats`, { headers: authHeaders });
            if (!response.ok) throw new Error('Failed to fetch chat history');

            const chats = await response.json();
            chatHistorySelect.innerHTML = '';

            if (chats.length === 0) {
                const option = document.createElement('option');
                option.textContent = "No chat history found.";
                chatHistorySelect.appendChild(option);
            } else {
                const defaultOption = document.createElement('option');
                defaultOption.value = "";
                defaultOption.textContent = "Select a chat to view...";
                chatHistorySelect.appendChild(defaultOption);

                chats.forEach(chat => {
                    const option = document.createElement('option');
                    option.value = chat.chat_id;
                    option.textContent = chat.title;
                    chatHistorySelect.appendChild(option);
                });
            }
        } catch (error) {
            console.error("Error loading chat history:", error);
            chatHistorySelect.innerHTML = '<option>Could not load chats.</option>';
        }
    }
    
    saveButton.addEventListener("click", async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/profile`, {
                method: 'PUT',
                headers: { ...authHeaders, 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: nameInput.value.trim(),
                    email: emailInput.value.trim()
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to save profile');
            }
            
            alert('Profile updated successfully!');
        } catch (error) {
            console.error("Error saving profile:", error);
            alert(`Error: ${error.message}`);
        }
    });

    // --- NEW: EVENT LISTENER TO LOAD SELECTED CHAT ---
    chatHistorySelect.addEventListener('change', (event) => {
        const selectedChatId = event.target.value;
        if (selectedChatId) {
            // Redirect to the chat page with the chat ID in the URL
            window.location.href = `./chat.html?chat_id=${selectedChatId}`;
        }
    });

    // Initial Page Load
    loadProfile();
    loadChatHistory();
});
document.addEventListener("DOMContentLoaded", () => {
  // --- Log Out Button ---
  const logoutButton = document.getElementById('logout-button');
  if (logoutButton) {
    logoutButton.addEventListener('click', () => {
      // Clear the user's token from storage
      localStorage.removeItem('access_token');
      // Redirect to the login page
      window.location.href = './Login.html';
    });
  }

  // --- Scroll Animation for Feature Cards ---
  const featureCards = document.querySelectorAll('.feature-card');
  if (featureCards.length > 0) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
          observer.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.1
    });
    featureCards.forEach(card => {
      observer.observe(card);
    });
  }
});