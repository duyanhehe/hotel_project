//////////      Toggle sidebar nav      //////////
const hamBurger = document.querySelector(".toggle-btn");

hamBurger.addEventListener("click", function () {
  document.querySelector("#sidebar").classList.toggle("expand");
});

//////////      Form validation     ////////// 
document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');

    form.addEventListener('submit', function (event) {
        event.preventDefault(); // Prevent the form from submitting initially

        // Validate email
        const email = document.getElementById('email').value.trim();
        if (!isValidEmail(email)) {
            alert('Please enter a valid email address.');
            return;
        }

        // Validate first name
        const firstName = document.getElementById('firstName').value.trim();
        if (firstName === '') {
            alert('Please enter your first name.');
            return;
        }

        // Validate last name
        const lastName = document.getElementById('lastName').value.trim();
        if (lastName === '') {
            alert('Please enter your last name.');
            return;
        }

        // Validate phone number
        const phoneNumber = document.getElementById('phoneNumber').value.trim();
        if (!isValidPhoneNumber(phoneNumber)) {
            alert('Please enter a valid phone number.');
            return;
        }

        // Validate password
        const password = document.getElementById('password').value;
        if (password.length < 8) {
            alert('Password must be at least 8 characters long.');
            return;
        }

        // Validate confirm password
        const confirmPassword = document.getElementById('password1').value;
        if (confirmPassword !== password) {
            alert('Passwords do not match.');
            return;
        }

        // Validate CAPTCHA
        const captchaInput = document.getElementById('captcha').value.trim();
        const captchaSpan = document.getElementById('captcha').textContent.trim();
        if (captchaInput !== captchaSpan) {
            alert('CAPTCHA verification failed. Please try again.');
            return;
        }

        // If all validation passes, submit the form
        this.submit();
    });

    function isValidEmail(email) {
        // Basic email validation using regex
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    function isValidPhoneNumber(phoneNumber) {
        // Basic phone number validation using regex
        const phoneRegex = /^[0-9+]+$/;
        return phoneRegex.test(phoneNumber);
    }
});

