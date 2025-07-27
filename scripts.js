const form = document.getElementById("forecastForm");
const modal = document.getElementById("predictionModal");
const closeModalBtn = document.getElementById("closeModal");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const formData = new FormData(form);
  const jsonData = {};
  formData.forEach((value, key) => {
    // Convert numeric strings to numbers; keep strings as-is
    jsonData[key] = isNaN(value) ? value : Number(value);
  });

  try {
    const response = await fetch("http://127.0.0.1:5000/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(jsonData),
    });

    const predictionResult = await response.json();

    document.getElementById("predictedDemand").textContent = predictionResult.PredictedDemand;
    document.getElementById("eoq").textContent = predictionResult.EOQ;
    document.getElementById("rol").textContent = predictionResult.ROL;
    document.getElementById("eoqInstruction").textContent = predictionResult.EOQ;
    document.getElementById("rolInstruction").textContent = predictionResult.ROL;

    modal.classList.add("show");
  } catch (err) {
    alert("❌ Error fetching prediction: " + err.message);
  }
});

closeModalBtn.addEventListener("click", () => {
  modal.classList.remove("show");
});
