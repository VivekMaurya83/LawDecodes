document.addEventListener("DOMContentLoaded", () => {
  // --- NEW: Scroll Animation for Feature Cards ---
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

  // --- PREVIOUS: Carousel/Slider Logic ---
  const nextButton = document.querySelector('.next');
  const prevButton = document.querySelector('.prev');

  if (nextButton) {
    nextButton.addEventListener('click', () => {
      let items = document.querySelectorAll('.item');
      if (items.length > 0) {
        document.querySelector('.slide').appendChild(items[0]);
      }
    });
  }

  if (prevButton) {
    prevButton.addEventListener('click', () => {
      let items = document.querySelectorAll('.item');
      if (items.length > 0) {
        document.querySelector('.slide').prepend(items[items.length - 1]);
      }
    });
  }

  // --- PREVIOUS: Modal Logic ---
  const modal = document.getElementById('profileModal');
  const btn = document.getElementById('profileButton');
  const closeBtn = document.querySelector('.close'); // More specific selector

  if (btn && modal) {
    btn.onclick = function() {
      modal.style.display = 'block';
    }
  }

  if (closeBtn && modal) {
    closeBtn.onclick = function() {
      modal.style.display = 'none';
    }
  }

  // Close modal when clicking outside of it
  window.addEventListener('click', function(event) {
    if (event.target == modal) {
      modal.style.display = 'none';
    }
  });

});

// --- PREVIOUS: Global Functions ---
function toggleInput(inputId) {
  var inputSection = document.getElementById(inputId);
  if (inputSection) {
    if (inputSection.style.display === "none" || inputSection.style.display === "") {
      inputSection.style.display = "flex";
    } else {
      inputSection.style.display = "none";
    }
  }
}

function saveInput(fieldId) {
  var fieldElement = document.getElementById(fieldId);
  if (fieldElement) {
    var fieldValue = fieldElement.value;
    if (fieldValue) {
      alert("Saved: " + fieldValue);
      fieldElement.value = '';
    } else {
      alert("Please fill in the field");
    }
  }
}
document.addEventListener("DOMContentLoaded", () => {
  // --- Log Out Button ---
  const logoutButton = document.getElementById('logout-button');
  if (logoutButton) {
    logoutButton.addEventListener('click', () => {
      localStorage.removeItem('access_token');
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
