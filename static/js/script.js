const hamBurger = document.querySelector(".toggle-btn");

hamBurger.addEventListener("click", function () {
  document.querySelector("#sidebar").classList.toggle("expand");
});


function validateForm() {
  var email = document.getElementById("email").value;
  var firstName = document.getElementById("firstName").value;
  var lastName = document.getElementById("lastName").value;
  var phoneNumber = document.getElementById("phoneNumber").value;
  var password = document.getElementById("password").value;
  var password1 = document.getElementById("password1").value;
  var captcha = document.getElementById("captcha").value;
  var agreeTerms = document.getElementById("agree_terms").checked;

  // Simple email validation
  var emailRegex = /\S+@\S+\.\S+/;
  if (!emailRegex.test(email)) {
      alert("Please enter a valid email address.");
      return false;
  }

  // Check if first name and last name are not empty
  if (firstName.trim() === "" || lastName.trim() === "") {
      alert("Please enter your first name and last name.");
      return false;
  }

  // Phone number validation
  var phoneNumberRegex = /^\d{10,}$/;
  if (!phoneNumberRegex.test(phoneNumber)) {
      alert("Please enter a valid phone number.");
      return false;
  }

  // Password length validation
  if (password.length < 8) {
      alert("Password must be at least 8 characters long.");
      return false;
  }

  // Password match validation
  if (password !== password1) {
      alert("Passwords do not match.");
      return false;
  }

  // CAPTCHA validation
  if (captcha !== "{{ captcha }}") {
      alert("CAPTCHA is incorrect.");
      return false;
  }

  // Terms agreement validation
  if (!agreeTerms) {
      alert("Please agree to the terms of service.");
      return false;
  }

  return true;  // Form validation successful
}