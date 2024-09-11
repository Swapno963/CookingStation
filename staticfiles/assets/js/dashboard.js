function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Check if cookie name matches the CSRF token cookie name
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function saveImage() {
    var fileInput = document.getElementById('profile');
    var file = fileInput.files[0];

    if (file) {
        var formData = new FormData();
        formData.append('image', file);

        var csrftoken = getCookie('csrftoken');

        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/upload_image/', true);

        xhr.setRequestHeader('X-CSRFToken', csrftoken);

        xhr.onload = function() {
            if (xhr.status === 200) {
                setTimeout(function() {
                    location.reload();
                });
            }
        };
        xhr.send(formData);
    }
}


  NiceSelect.bind(document.getElementById("duration"), {
     searchable: false,
     placeholder: "select",
     searchtext: "zoek",
     selectedtext: "geselecteerd",
  });


document.addEventListener("DOMContentLoaded", function() {
    var select = document.getElementById("duration");
    var costDiv = document.getElementById("cost");
    var radioRegular = document.getElementById("regular");
    var radioPremium = document.getElementById("premium");

    function updateTable() {
        var selectedOption = select.options[select.selectedIndex];
        var planName = selectedOption.textContent;
        var planType = "";

        if (radioRegular.checked) {
            planType = "Regular";
        } else if (radioPremium.checked) {
            planType = "Premium";
        }

        var totalMeals = selectedOption.getAttribute("data-" + planType.toLowerCase() + "-total-meals");
        var perMeal = selectedOption.getAttribute("data-" + planType.toLowerCase() + "-per-meal");
        var totalAmount = selectedOption.getAttribute("data-" + planType.toLowerCase() + "-total-amount");

        var tableHTML = '<table class="table table-bordered">';
        tableHTML += '<thead><tr><th scope="col">Plan</th><th scope="col">Type</th><th scope="col">Total Meals</th><th scope="col">Per Meal</th><th scope="col">Total</th></tr></thead>';
        tableHTML += "<tbody>";
        tableHTML += "<tr><td>" + planName + "</td><td>" + planType + "</td><td>" + totalMeals + "</td><td>" + perMeal + " BDT</td><td>" + totalAmount + " BDT</td></tr>";
        tableHTML += "</tbody></table>";

        costDiv.innerHTML = tableHTML;
    }

    radioRegular.addEventListener("change", updateTable);
    radioPremium.addEventListener("change", updateTable);

    select.addEventListener("change", updateTable);

    select.dispatchEvent(new Event("change"));

    function subscribe() {
        var selectedOption = select.options[select.selectedIndex];
        var planName = selectedOption.textContent;
        var planType = "";

        if (radioRegular.checked) {
            planType = "Regular";
        } else if (radioPremium.checked) {
            planType = "Premium";
        }

        var totalMeals = selectedOption.getAttribute("data-" + planType.toLowerCase() + "-total-meals");
        var perMeal = selectedOption.getAttribute("data-" + planType.toLowerCase() + "-per-meal");
        var totalAmount = selectedOption.getAttribute("data-" + planType.toLowerCase() + "-total-amount");

        var checkoutUrl = "checkout/?plan=" + encodeURIComponent(planName) +
            "&type=" + encodeURIComponent(planType) +
            "&totalMeals=" + encodeURIComponent(totalMeals) +
            "&perMeal=" + encodeURIComponent(perMeal) +
            "&totalAmount=" + encodeURIComponent(totalAmount);
        window.location.href = checkoutUrl;
    }

    var subscribeButton = document.querySelector(".button-87");
    subscribeButton.addEventListener("click", subscribe);
});


document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('toggleForm').addEventListener('submit', function(event) {
        event.preventDefault();
        var form = event.target;
        var formData = new FormData(form);
        var xhr = new XMLHttpRequest();
        xhr.open(form.method, form.action, true);
        xhr.onload = function() {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);

                var mealStatusElements = document.querySelectorAll('.mealStatus');
                mealStatusElements.forEach(function(element) {
                    element.innerHTML = '<b>' + (response.reduce_balance ? 'ON' : 'OFF') + '</b>';
                });

                var button = document.getElementById('mealToggleButton');
                if (response.reduce_balance) {
                    button.innerText = 'Turn Off Meal';
                    button.style.backgroundColor = '#bf2f2f';
                } else {
                    button.innerText = 'Turn On Meal';
                    button.style.backgroundColor = '#0a6b37';
                }

                var currentDate = new Date();
                var currentHour = currentDate.getHours();
                var startHour1 = 9;
                var endHour1 = 12;
                var startHour2 = 15;
                var endHour2 = 24;

                if ((currentHour >= startHour1 && currentHour < endHour1) || (currentHour >= startHour2 && currentHour < endHour2)) {
                    button.disabled = true;
                } else {
                    if (response.reduce_balance && response.flexibility === 0) {
                        button.disabled = true;
                    } else {
                        button.disabled = false;
                    }
                }
                document.getElementById('remainingFlexibility').innerText = response.flexibility;
                document.getElementById('usedFlexibility').innerText = response.flexibility_used;
            } else {
                console.error('Error:', xhr.status);
            }
        };

        xhr.send(formData);
    });

    var button = document.getElementById('mealToggleButton');
    var currentDate = new Date();
    var currentHour = currentDate.getHours();
    var startHour1 = 9;
    var endHour1 = 12;
    var startHour2 = 15;
    var endHour2 = 24;
    if ((currentHour >= startHour1 && currentHour < endHour1) || (currentHour >= startHour2 && currentHour < endHour2)) {
        button.disabled = true;
    }
});
