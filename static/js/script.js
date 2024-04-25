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
        alert("Please enter a valid phone number (at least 10 digits).");
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

    // Check if email already exists asynchronously
    try {
        const response = await fetch(`/check_email?email=${email}`);
        const data = await response.json();
        if (data.exists) {
            alert("This email address is already registered.");
            return false;
        }
    } catch (error) {
        console.error("Error checking email:", error);
        alert("An error occurred. Please try again later.");
        return false;
    }

    // Check if phone number is unique asynchronously
    try {
        const response = await fetch(`/check_phone?phoneNumber=${phoneNumber}`);
        const data = await response.json();
        if (data.exists) {
            alert("This phone number is already registered with another account.");
            return false;
        }
    } catch (error) {
        console.error("Error checking phone number:", error);
        alert("An error occurred. Please try again later.");
        return false;
    }

    return true;  // Form validation successful
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