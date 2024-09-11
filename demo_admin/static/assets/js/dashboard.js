function previewFile() {
  const preview = document.getElementById("preview");
  const fileInput = document.querySelector("input[type=file]").files[0];
  const reader = new FileReader();

  reader.onloadend = function () {
    preview.src = reader.result;
  };

  if (fileInput) {
    reader.readAsDataURL(fileInput);
  } else {
    preview.src = "assets/img/dashboard/blank-profile.png";
  }
}

document.getElementById("subscribeBtn").addEventListener("click", function () {
  document.getElementById("paymentDiv").style.display = "block";
});
document.addEventListener("DOMContentLoaded", function () {
  var select = document.getElementById("duration");
  var costDiv = document.getElementById("cost");
  var days = parseInt(select.value);

  calculateCost(days);

  select.addEventListener("change", function () {
    document.getElementById("paymentDiv").style.display = "none";
    days = parseInt(this.value);
    calculateCost(days);
  });
});

function calculateCost(days) {
  var perMealCost = days < 15 ? 60 : 55;
  var totalCost = perMealCost * days * 2;

  var tableHTML = '<table class="table table-bordered">';
  tableHTML +=
    '<thead><tr><th scope="col">Plan</th><th scope="col">Total Meals</th><th scope="col">Per Meal</th><th scope="col">Total</th></tr></thead>';
  tableHTML += "<tbody>";
  tableHTML +=
    "<tr><td>" +
    days +
    " days</td><td>" +
    days * 2 +
    "</td><td>" +
    perMealCost +
    " BDT</td><td>" +
    totalCost +
    " BDT</td></tr>";
  tableHTML += "</tbody></table>";

  document.getElementById("cost").innerHTML = tableHTML;
}

NiceSelect.bind(document.getElementById("duration"), {
  searchable: false,
  placeholder: "select",
  searchtext: "zoek",
  selectedtext: "geselecteerd",
});

function paymentBtn() {
  var select = document.getElementById("duration");

  var days = parseInt(select.value);
  var totalMeals = days * 2;
  var perMealCost = days < 15 ? 60 : 55;
  var totalCost = perMealCost * days * 2;
  let cookingStationData = {
    days: days,
    dailyMeal: 2,
    perMealCost: perMealCost,
    totalMeals: totalMeals,
    totalCost: totalCost,
  };

  localStorage.setItem(
    "cookingStationData",
    JSON.stringify(cookingStationData)
  );
  window.location.href = "checkout.html";
}

// document.getElementById("userType").addEventListener("click", (e) => {
//   //   console.dir(e.target.firstElementChild);
//   const target = e.target;
//   if (target.nodeName === "LABEL") {
//     target.firstElementChild.checked = true;
//     document.querySelector('.activeUserType').classList.remove('activeUserType')
//     target.
//     console.dir(target.classList[1] === "activeUserType");
//   }
// });
