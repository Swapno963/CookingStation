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

document.addEventListener("DOMContentLoaded", function () {
  var select = document.getElementById("duration");
  var costDiv = document.getElementById("cost");
  var days = parseInt(select.value);

  calculateCost(days);

  select.addEventListener("change", function () {
    days = parseInt(this.value);
    calculateCost(days);
  });
});

function calculateCost(days) {
  var perMealCost = days < 15 ? 60 : 55;
  var totalCost = perMealCost * days * 2;
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
