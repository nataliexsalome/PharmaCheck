//test call to check data in the report table.
// axios.get("http://127.0.0.1:5000/api/report/data").then((response) => {
//   console.log("Data:", response.data);
// });


// Simulated function to handle form submission
function handleFormSubmission(event) {
  event.preventDefault(); // Stop the default form submission
  const form = document.getElementById("reportForm");
  const messageDiv = document.getElementById("submissionMessage");

  // Collect form data (for display purposes only, in a real app this would go to Firestore)
  const formData = new FormData(form);
  const reportData = Object.fromEntries(formData.entries());
  console.log(reportData);

  // Simple validation check (productName and description are required by HTML 'required' attributes, but check location too)
  if (
    !reportData.productName ||
    !reportData.location ||
    !reportData.description
  ) {
    messageDiv.className = "mt-6 p-4 text-red-700 bg-red-100 rounded-lg";
    messageDiv.innerHTML = "Please fill in all required fields (*).";
    messageDiv.classList.remove("hidden");
    return;
  }

  // Simulate API call delay
  messageDiv.className =
    "mt-6 p-4 text-green-700 bg-green-100 rounded-lg border border-green-700";
  messageDiv.innerHTML =
    '<p class="font-semibold flex items-center justify-center"><svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-green-700" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>Submitting confidential report securely... Please wait.</p>';
  messageDiv.classList.remove("hidden");

  axios
    .post("/api/report", { form_data: reportData })
    .then((response) => {
      const result = response.data;
      renderResult(input, result);
    })
    .catch((error) => {
      console.error("Error fetching data:", error);
    });

  setTimeout(() => {
    // Simulated Success Response
    form.reset(); // Clear the form
    messageDiv.className =
      "mt-6 p-4 text-green-700 bg-green-100 rounded-lg border border-green-700";
    messageDiv.innerHTML = `
                    <p class="font-bold">✅ Thank you for your confidential report!</p>
                    <p>Your submission regarding <span class="font-mono text-green-800">${reportData.productName.substring(
                      0,
                      30
                    )}...</span> has been successfully recorded. We will use this information to investigate potential counterfeit activity.</p>
                `;

    // Hide the message after 10 seconds
    setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 10000);
  }, 1500); // 1.5 second delay simulation
}

// Note: For a live deployment, full Firebase setup and logging would be integrated here.
