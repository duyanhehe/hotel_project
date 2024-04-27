const hamBurger = document.querySelector(".toggle-btn");

hamBurger.addEventListener("click", function () {
  document.querySelector("#sidebar").classList.toggle("expand");
});


async function validateForm() {
    var email = document.getElementById("email").value;
    var firstName = document.getElementById("firstName").value;
    var lastName = document.getElementById("lastName").value;
    var phoneNumber = document.getElementById("phoneNumber").value;
    var password = document.getElementById("password").value;
    var password1 = document.getElementById("password1").value;
    var captcha = document.getElementById("enter_captcha").value;
    var captchaValue = document.getElementById("captcha_value").value;
    var agreeTerms = document.getElementById("agree_terms").checked;

    // Simple email validation
    var emailRegex = /\S+@\S+\.\S+/;
    if (!emailRegex.test(email)) {
        document.getElementById('error_message').innerHTML="Please enter a valid email address.";
        document.getElementById('error_message').style.display='block';
        return false;
    }

    // Check if first name and last name are not empty
    if (firstName.trim() === "" || lastName.trim() === "") {
        document.getElementById('error_message').innerHTML="Please enter your first name and last name.";
        document.getElementById('error_message').style.display='block';
        return false;
    }

    // Phone number validation
    var phoneNumberRegex = /^\d{9,}$/;
    if (!phoneNumberRegex.test(phoneNumber)) {
        document.getElementById('error_message').innerHTML="Please enter a valid phone number (at least 9 digits).";
        document.getElementById('error_message').style.display='block';
        return false;
    }

    // Password length validation
    if (password.length < 8) {
        document.getElementById('error_message').innerHTML="Password must be at least 8 characters long.";
        document.getElementById('error_message').style.display='block';
        return false;
    }

    // Password match validation
    if (password !== password1) {
        document.getElementById('error_message').innerHTML="Passwords do not match.";
        document.getElementById('error_message').style.display='block';
        return false;
    }

    // CAPTCHA validation
    if (captcha !== captchaValue) {
        document.getElementById('error_message').innerHTML="Captcha is incorrect.";
        document.getElementById('error_message').style.display='block';
        console.log(captcha)
        console.log(captchaValue)
        return false;
    }

    // Terms agreement validation
    if (!agreeTerms) {
        document.getElementById('error_message').innerHTML="Please agree to the terms of service.";
        document.getElementById('error_message').style.display='block';
        return false;
    }

    // AJAX request to check if email exists
    try {
        const emailResponse = await fetch('/check-email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email: email })
        });

        if (!emailResponse.ok) {
            throw new Error('Network response was not ok');
        }

        const emailData = await emailResponse.json();

        if (emailData.exists) {
            document.getElementById('error_message').innerHTML = "Email already exists.";
            document.getElementById('error_message').style.display = 'block';
            return false;
        }

        // If email doesn't exist, proceed to check phone number
        const phoneResponse = await fetch('/check-phone-number', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ phoneNumber: phoneNumber })
        });

        if (!phoneResponse.ok) {
            throw new Error('Network response was not ok');
        }

        const phoneData = await phoneResponse.json();

        if (phoneData.exists) {
            document.getElementById('error_message').innerHTML = "Phone number already exists.";
            document.getElementById('error_message').style.display = 'block';
            return false;
        }

        // If both email and phone number are unique, continue with form submission
        document.getElementById('signupForm').submit();
        return true;
    } catch (error) {
        console.error('Error:', error);
        return false;
    }
}


//chart js
const chartData = {
    labels: ["Python", "Java", "Javascript", "C#", "Others"],
    data: [30, 17, 10, 7, 36]
};

const myChart = document.querySelector(".my-chart");
const ul = document.querySelector(".programming-stats .details ul ");

new Chart(myChart, {
    type:"doughnut",
    data: {
        labels: chartData.labels,
        datasets: [
            {
                label: "Language Popularity",
                data: chartData.data,
            },
        ],
    },
    options: {
        hoverBorderWidth: 10,
        plugins: {
            legend: {
                display: true
            },
        },
    },
}); 

const populateUL = () => {
    chartData.labels.forEach((l, i) => {
        let li = document.createElement("li");
        li.innerHTML = `${l}: <span class='percentage'>${chartData.data[i]}%</span>`;
        ul.appendChild(li);

    

    });
};

populateUL();