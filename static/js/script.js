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