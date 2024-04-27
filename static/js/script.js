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
    var phoneNumberRegex = /^\d{10,}$/;
    if (!phoneNumberRegex.test(phoneNumber)) {
        document.getElementById('error_message').innerHTML="Please enter a valid phone number (at least 10 digits).";
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
        console.log("Entered CAPTCHA:", captcha);
        console.log("Actual CAPTCHA:", captchaValue);

        return false;
    }

    // Terms agreement validation
    if (!agreeTerms) {
        document.getElementById('error_message').innerHTML="Please agree to the terms of service.";
        document.getElementById('error_message').style.display='block';
        return false;
    }

    // Check if email already exists asynchronously
    // try {
    //     const response = await fetch(`/check_email?email=${email}`);
    //     const data = await response.json();
    //     if (data.exists) {
    //         alert("This email address is already registered.");
    //         return false;
    //     }
    // } catch (error) {
    //     console.error("Error checking email:", error);
    //     alert("An error occurred. Please try again later.");
    //     return false;
    // }

    // Check if phone number is unique asynchronously
    // try {
    //     const response = await fetch(`/check_phone?phoneNumber=${phoneNumber}`);
    //     const data = await response.json();
    //     if (data.exists) {
    //         alert("This phone number is already registered with another account.");
    //         return false;
    //     }
    // } catch (error) {
    //     console.error("Error checking phone number:", error);
    //     alert("An error occurred. Please try again later.");
    //     return false;
    // }
    document.getElementById('signupForm').submit()
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