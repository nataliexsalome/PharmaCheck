// --- CORE APPLICATION LOGIC ---

// Mock database structure (Data tier)
const MOCK_STOCK = {
  A1234567890: {
    status: "authentic",
    expiryDate: "2026-10-01",
    batch: "BTX-45",
    manufacturer: "PharmaCo Kenya",
  },
  C9876543210: {
    status: "counterfeit",
    expiryDate: "2025-01-01",
    batch: "XXX-01",
    manufacturer: "Unknown",
  },
  E1112223334: {
    status: "expired",
    expiryDate: "2024-01-01",
    batch: "BTX-30",
    manufacturer: "PharmaCo Kenya",
  },
  A0000000000: {
    status: "authentic",
    expiryDate: "2025-12-31",
    batch: "BTX-46",
    manufacturer: "PharmaCo Kenya",
  },
  C1111111111: {
    status: "counterfeit",
    expiryDate: "2026-03-01",
    batch: "BTX-45",
    manufacturer: "PharmaCo Kenya",
  }, // Cloned serial, but marked counterfeit for demo
  E4445556667: {
    status: "expired",
    expiryDate: "2023-05-15",
    batch: "OLD-22",
    manufacturer: "Global Meds",
  },
};

const getResult = (serial) => {
  // Check for exact match in mock data
  const mockResult = MOCK_STOCK[serial];

  if (mockResult) {
    // Check if expired logic
    const today = new Date();
    const expiry = new Date(mockResult.expiryDate);
    if (expiry < today && mockResult.status !== "counterfeit") {
      mockResult.status = "expired"; // Overwrite status if past date
    }
    return mockResult;
  }

  // Simulate partial match/not found logic for security
  if (serial.startsWith("C") || serial.startsWith("c")) {
    return {
      status: "counterfeit",
      expiryDate: "N/A",
      batch: "UNK-FF",
      manufacturer: "N/A",
    };
  }

  return {
    status: "not found",
    expiryDate: "N/A",
    batch: "N/A",
    manufacturer: "N/A",
  };
};

const renderResult = (serial, result) => {
  const resultsArea = document.getElementById("results-area");
  resultsArea.innerHTML = "";

  const now = new Date();
  const logEntry = {
    serial: serial,
    timestamp: now.toISOString(),
    status: result.status,
    userId: result.user,
  };

  let message, className;
  let detailsHtml = "";

  if (result.status === "AUTHENTIC") {
    message = `✅ VERIFIED: This Amoxicillin Serial ID is Authentic and Valid.`;
    className = "result-authentic";
    detailsHtml = `
                    <li><strong>Status:</strong> Authentic and Safe</li>
                    <li><strong>Expiry Date:</strong> ${result.expiryDate}</li>
                    <li><strong>Batch Number:</strong> ${result.batch}</li>
                    ${
                      result.serial
                        ? `<li><strong>Serial Number:</strong> ${result.serial}</li>`
                        : ""
                    }
                    <li><strong>Manufacturer:</strong> ${
                      result.manufacturer
                    }</li>
                `;
  } else if (result.status === "EXPIRED") {
    message = `⚠️ WARNING: This Amoxicillin Serial ID is Expired. Do Not Dispense.`;
    className = "result-expired";
    detailsHtml = `
                    <li><strong>Status:</strong> EXPIRED!</li>
                    <li><strong>Expiry Date:</strong> ${
                      result.expiryDate
                    } (Past Date)</li>
                    <li><strong>Batch Number:</strong> ${result.batch}</li>
                    ${
                      result.serial
                        ? `<li><strong>Serial Number:</strong> ${result.serial}</li>`
                        : ""
                    }
                    <li><strong>Manufacturer:</strong> ${
                      result.manufacturer
                    }</li>
                    <li><strong>ACTION:</strong> Quarantine stock immediately.</li>
                `;
  } else if (result.status === "COUNTERFEIT") {
    message = `❌ ALERT: Potential Counterfeit Detected`;
    className = "result-counterfeit";
    detailsHtml = `
                    <li><strong>Status:</strong> COUNTERFEIT</li>
                    <li><strong>Reason:</strong> Serial number flagged or matched a known fraudulent identifier.</li>
                    <li><strong>Batch/Serial Number:</strong> ${serial}</li>
                    <li><strong>ACTION:</strong> Immediately quarantine product and report to PPB.</li>
                `;
  } else {
    // not found
    // message = `❓ QUERY FAILED: Serial/Batch ID not found in system. Please re-enter or contact support.`;
    // className = 'result-expired'; // Use yellow for caution/not found
    // detailsHtml = `
    //     <li><strong>Status:</strong> Not Found</li>
    //     <li><strong>Action:</strong> Check input carefully, or contact your regulatory manager.</li>
    // `;
  }

  const messageDiv = document.createElement("div");
  messageDiv.className = `result-message ${className}`;
  messageDiv.textContent = message;

  const detailsUl = document.createElement("ul");
  detailsUl.className = "details-list";
  detailsUl.innerHTML = detailsHtml;

  resultsArea.appendChild(messageDiv);
  resultsArea.appendChild(detailsUl);

  // Trigger visibility animation
  setTimeout(() => {
    messageDiv.classList.add("visible");
  }, 50);

  // Log the transaction to Firestore (Objective iii: Audit Logging)
  logTransaction(logEntry);
};

const logTransaction = (logEntry) => {
  fetch("/api/log", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(logEntry)
  })
  .then(res => res.json())
  .then(data => {
    if (!data.success) console.warn("Log not saved:", data.error);
  })
  .catch(err => console.error("Error logging transaction:", err));
};


const handleVerification = () => {  
  const input = document
    .getElementById("serial-input")
    .value.trim()
    .toUpperCase();
  if (input.length < 5) {
    document.getElementById("results-area").innerHTML =
      '<div class="result-message result-expired visible">Please enter a valid serial or batch number (at least 5 characters).</div>';
    return;
  }

  // Simulate network delay for verification process
  document.getElementById("results-area").innerHTML =
    '<p style="text-align:center;"><i class="fas fa-spinner fa-spin"></i> Verifying against simulated database...</p>';

  /*  setTimeout(() => {
                const result = getResult(input);
                renderResult(input, result);
            }, 1500); // 1.5 second delay simulation */

  axios
    .post("/api/verify", { serial: input })
    .then((response) => {
      //console.log('Data:', response.data);
      const result = response.data;

      renderResult(input, result);
    })
    .catch((error) => {
      console.error("Error fetching data:", error);
    });
};

// Initialize Firebase on load
// document.addEventListener("DOMContentLoaded", initFirebase);

// Event Listeners for UI
document.addEventListener("DOMContentLoaded", function () {
  const verifyButton = document.getElementById("verify-button");
  const serialInput = document.getElementById("serial-input");
  const toggle = document.getElementById("mobile-menu-toggle");
  const nav = document.getElementById("main-navigation");
  // const connectionStatusText = document.getElementById("statusText");


  if (verifyButton) {
    verifyButton.addEventListener("click", () => {
      // if (connectionStatusText.textContent === "Server Online")
        handleVerification();
    });
  }
  if (serialInput) {
    serialInput.addEventListener("keydown", (e) => {
      if (
        e.key === "Enter" //&&
        // connectionStatusText.textContent === "Server Online"
      ) {
        handleVerification();
      }
    });
  }

  // Mobile Nav Toggle
  if (toggle && nav) {
    toggle.addEventListener("click", () => {
      if (!nav.classList.contains("mobile-nav-active")) {
        nav.classList.add("mobile-nav-active");
      } else {
        nav.classList.remove("mobile-nav-active");
      }
      if (!nav.classList.contains("active")) {
        nav.classList.add("active");
      } else {
        nav.classList.remove("active");
      }
      // Hide body overflow when mobile nav is open
      document.body.style.overflow = nav.classList.contains("mobile-nav-active")
        ? "hidden"
        : "auto";
    });
    nav.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        if (nav.classList.contains("mobile-nav-active")) {
          nav.classList.remove("mobile-nav-active");
          toggle.classList.remove("active");
          document.body.style.overflow = "auto";
        }
      });
    });
  }
});
