document.getElementById('contact-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const message = document.getElementById("message").value.trim();
  
    if (name && email && message) {
      document.getElementById("form-response").textContent = "Thanks for contacting us, " + name + "!";
      this.reset();
    } else {
      document.getElementById("form-response").textContent = "Please fill in all fields.";
    }
  });
  