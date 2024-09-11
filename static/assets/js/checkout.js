document.addEventListener("DOMContentLoaded", function() {
    function getParameterByName(name, url) {
        if (!url) url = window.location.href;
        name = name.replace(/[\[\]]/g, "\\$&");
        var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
            results = regex.exec(url);
        if (!results) return null;
        if (!results[2]) return '';
        return decodeURIComponent(results[2].replace(/\+/g, " "));
    }

    var planName = getParameterByName('plan');
    var type = getParameterByName('type');
    var totalMeals = getParameterByName('totalMeals');
    var perMeal = getParameterByName('perMeal');
    var totalAmount = getParameterByName('totalAmount');

    document.getElementById('planText2').textContent = planName;
    document.getElementById('type').textContent = type;
    document.getElementById('dailyMealText').textContent = 2;
    document.getElementById('totalMealText').textContent = totalMeals;
    document.getElementById('perMealText').textContent = perMeal + ' BDT';
    document.getElementById('totalCostText').textContent = totalAmount + ' BDT';
});


    document.addEventListener("DOMContentLoaded", function() {
       var bkashInstruction = document.getElementById("bkashInstruction");
       var nagadInstruction = document.getElementById("nagadInstruction");
       var bkashRadio = document.getElementById("bkash");
       var nagadRadio = document.getElementById("nagad");

       bkashRadio.addEventListener("change", function() {
          if (this.checked) {
             bkashInstruction.style.display = "block";
             nagadInstruction.style.display = "none";
          }
       });

       nagadRadio.addEventListener("change", function() {
          if (this.checked) {
             bkashInstruction.style.display = "none";
             nagadInstruction.style.display = "block";
          }
       });
    });


document.addEventListener("DOMContentLoaded", function() {
    var formPayment = document.getElementById("form-payment");
    var alertContainer = document.getElementById("alert-container");

    formPayment.addEventListener("submit", function(event) {
        event.preventDefault();

        var paymentProcessor = document.querySelector("input[name='payment_processor']:checked").value;
        var senderNumber = document.getElementById("senderPhone").value;
        var transactionId = document.getElementById("transactionId").value;
        var planName = document.getElementById("planText2").innerText;
        var type = document.getElementById("type").innerText;
        var totalAmount = document.getElementById("totalCostText").textContent;

        var xhr = new XMLHttpRequest();
        xhr.open("POST", "/save-payment-details/", true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.setRequestHeader("X-CSRFToken", document.querySelector("input[name='csrfmiddlewaretoken']").value);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    // console.log("Payment details saved successfully");
                    window.location.href = "payment_confirmed/";
                } else {
                    // console.error("Error saving payment details");
                    var response = JSON.parse(xhr.responseText);
                    var errorMessage = response.error || "Failed to proceed confirmation. Please try again.";
                    displayAlert(errorMessage, "alert-danger");
                    setTimeout(removeAlert, 10000)
                }
            }
        };
        var data = JSON.stringify({
            payment_processor: paymentProcessor,
            sender_number: senderNumber,
            transaction_id: transactionId,
            planName: planName,
            type: type,
            totalAmount : totalAmount,
        });
        xhr.send(data);
    });


    function displayAlert(message, alertType) {
        alertContainer.innerHTML = '';

        var alertDiv = document.createElement('div');
        alertDiv.classList.add('alert', alertType);
        alertDiv.setAttribute('role', 'alert');
        alertDiv.textContent = message;

        alertContainer.appendChild(alertDiv);
    }

    function removeAlert() {
        alertContainer.innerHTML = '';
    }
});
