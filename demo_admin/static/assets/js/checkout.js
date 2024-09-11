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

    const planText = document.getElementById('planText')
    const planText2 = document.getElementById('planText2')
    const dailyMealText = document.getElementById('dailyMealText')
    const totalMealText = document.getElementById('totalMealText')
    const perMealText = document.getElementById('perMealText')
    const totalCostText = document.getElementById('totalCostText')


    window.onload = function() {
       if (localStorage.getItem('cookingStationData')) {
          var cookingStationData = JSON.parse(localStorage.getItem('cookingStationData'));
          planText.innerHTML = `${cookingStationData.days} days`;
          planText2.innerHTML = `${cookingStationData.days} days`;
          dailyMealText.innerHTML=cookingStationData.dailyMeal
          totalMealText.innerHTML=cookingStationData.totalMeals
          perMealText.innerHTML=`${cookingStationData.perMealCost} TK BDT`
          totalCostText.innerHTML=`${cookingStationData.totalCost} TK BDT`
          
       } else {
          console.log("No data found in localStorage.");
          window.location.href = 'dashboard.html'
       }
    }


    const form = document.getElementById('form-payment')

    form.addEventListener('submit', function(e) {
       e.preventDefault()
       window.location.href = 'payment-success.html'
    })