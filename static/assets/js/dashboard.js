const modal = new bootstrap.Modal(
  document.getElementById("mealCustomizationModal")
);
const mealOffOptionUL = document.getElementById("mealOffOptionUL");

function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
      var cookie = cookies[i].trim();
      // Check if cookie name matches the CSRF token cookie name
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function saveImage() {
  var fileInput = document.getElementById("profile");
  var file = fileInput.files[0];

  if (file) {
    var formData = new FormData();
    formData.append("image", file);

    var csrftoken = getCookie("csrftoken");

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/upload_image/", true);

    xhr.setRequestHeader("X-CSRFToken", csrftoken);

    xhr.onload = function () {
      if (xhr.status === 200) {
        setTimeout(function () {
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
document.addEventListener("DOMContentLoaded", function () {
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

    var totalMeals = selectedOption.getAttribute(
      "data-" + planType.toLowerCase() + "-total-meals"
    );
    var perMeal = selectedOption.getAttribute(
      "data-" + planType.toLowerCase() + "-per-meal"
    );
    var totalAmount = selectedOption.getAttribute(
      "data-" + planType.toLowerCase() + "-total-amount"
    );

    var tableHTML = '<table class="table table-bordered">';
    tableHTML +=
      '<thead><tr><th scope="col">Plan</th><th scope="col">Type</th><th scope="col">Total Meals</th><th scope="col">Per Meal</th><th scope="col">Total</th></tr></thead>';
    tableHTML += "<tbody>";
    tableHTML +=
      "<tr><td>" +
      planName +
      "</td><td>" +
      planType +
      "</td><td>" +
      totalMeals +
      "</td><td>" +
      perMeal +
      " BDT</td><td>" +
      totalAmount +
      " BDT</td></tr>";
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

    var totalMeals = selectedOption.getAttribute(
      "data-" + planType.toLowerCase() + "-total-meals"
    );
    var perMeal = selectedOption.getAttribute(
      "data-" + planType.toLowerCase() + "-per-meal"
    );
    var totalAmount = selectedOption.getAttribute(
      "data-" + planType.toLowerCase() + "-total-amount"
    );

    var checkoutUrl =
      "checkout/?plan=" +
      encodeURIComponent(planName) +
      "&type=" +
      encodeURIComponent(planType) +
      "&totalMeals=" +
      encodeURIComponent(totalMeals) +
      "&perMeal=" +
      encodeURIComponent(perMeal) +
      "&totalAmount=" +
      encodeURIComponent(totalAmount);
    window.location.href = checkoutUrl;
  }

  var subscribeButton = document.querySelector(".button-87");
  subscribeButton.addEventListener("click", subscribe);
});

document.addEventListener("DOMContentLoaded", function () {
  document
    .getElementById("toggleForm")
    .addEventListener("submit", function (event) {
      event.preventDefault();

      var form = event.target;
      var formData = new FormData(form);
      var xhr = new XMLHttpRequest();
      xhr.open(form.method, form.action, true);
      xhr.onload = function () {
        if (xhr.status === 200) {
          var response = JSON.parse(xhr.responseText);
          if (response?.success) {
            const { used_flexibility, remaining_flexibility } = response;
            const remainingFlexibility = document.getElementById(
              "remainingFlexibility"
            );
            const usedFlexibility = document.getElementById("usedFlexibility");

            remainingFlexibility.innerHTML = `<b>${remaining_flexibility}</b>`;
            usedFlexibility.innerHTML = `<b>${used_flexibility}</b>`;
            modal.hide();
          } else {
            const error = document.querySelector(".mealOfError");
            if (!error) {
              const li = document.createElement("li");
              li.classList.add("list-group-item", "mealOfError");
              li.innerHTML = `<p class="text-danger fw-bold text-center">${response?.message}</p>`;

              mealOffOptionUL.insertBefore(li, mealOffOptionUL.firstChild);
            }
          }
        } else {
          console.error("Error:", xhr.status);
        }
      };

      xhr.send(formData);
    });

  const closeModalBtn = document.getElementById("closeModalBtn");
  closeModalBtn.addEventListener("click", () => {
    document.querySelector(".switch-input").checked = true;
  });
});

document.addEventListener("DOMContentLoaded", function () {
  const mealOnOffSwitch = document.querySelector(".switch-input");
  mealOnOffSwitch.addEventListener("change", function (e) {
    const isSwitchOn = e.target.checked;

    if (isSwitchOn) {
      var formData = new FormData();
      const userId = document.getElementById("user_id").value;
      formData.append("meal_off_choice", "None");
      formData.append("user_id", userId);
      const csrfmiddlewaretoken = document.getElementById("csrf_token").value;
      formData.append("csrfmiddlewaretoken", csrfmiddlewaretoken);

      var xhr = new XMLHttpRequest();
      xhr.open("POST", "toggle_meal_state/", true);
      xhr.onload = function () {
        if (xhr.status === 200) {
          var response = JSON.parse(xhr.responseText);
          if (response?.success) {
            document.querySelector(".switch-input").checked = true;
          } else {
            document.querySelector(".switch-input").checked = false;
          }
        } else {
          console.error("Error:", xhr.status);
          document.querySelector(".switch-input").checked = false;
        }
      };

      xhr.send(formData);
    } else {
      const error = document.querySelector(".mealOfError");
      if (error) {
        mealOffOptionUL.removeChild(mealOffOptionUL.firstChild);
      }
      modal.show();
    }
  });
});
