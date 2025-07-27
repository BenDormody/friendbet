// Main JavaScript functionality for Fantasy Betting League

document.addEventListener("DOMContentLoaded", function () {
  // Initialize tooltips
  var tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]')
  );
  var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // Initialize popovers
  var popoverTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="popover"]')
  );
  var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
    return new bootstrap.Popover(popoverTriggerEl);
  });

  // Auto-hide alerts after 5 seconds
  setTimeout(function () {
    var alerts = document.querySelectorAll(".alert");
    alerts.forEach(function (alert) {
      var bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    });
  }, 5000);

  // Copy to clipboard functionality
  document.querySelectorAll(".copy-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var textToCopy = this.getAttribute("data-clipboard-text");
      navigator.clipboard.writeText(textToCopy).then(function () {
        // Show success message
        var originalText = btn.textContent;
        btn.textContent = "Copied!";
        btn.classList.add("btn-success");
        btn.classList.remove("btn-outline-secondary");

        setTimeout(function () {
          btn.textContent = originalText;
          btn.classList.remove("btn-success");
          btn.classList.add("btn-outline-secondary");
        }, 2000);
      });
    });
  });

  // Betting option selection
  document.querySelectorAll(".betting-option").forEach(function (option) {
    option.addEventListener("click", function () {
      // Remove selection from other options
      document.querySelectorAll(".betting-option").forEach(function (opt) {
        opt.classList.remove("selected");
      });

      // Select this option
      this.classList.add("selected");

      // Update hidden input
      var selectedOptionInput = document.getElementById("selected_option");
      if (selectedOptionInput) {
        selectedOptionInput.value = this.getAttribute("data-option");
      }

      // Update potential payout display
      updatePotentialPayout();
    });
  });

  // Bet amount input handling
  var betAmountInput = document.getElementById("bet_amount");
  if (betAmountInput) {
    betAmountInput.addEventListener("input", function () {
      updatePotentialPayout();
    });
  }

  // Form validation
  document.querySelectorAll("form").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      var requiredFields = form.querySelectorAll("[required]");
      var isValid = true;

      requiredFields.forEach(function (field) {
        if (!field.value.trim()) {
          isValid = false;
          field.classList.add("is-invalid");
        } else {
          field.classList.remove("is-invalid");
        }
      });

      if (!isValid) {
        e.preventDefault();
        showAlert("Please fill in all required fields.", "danger");
      }
    });
  });

  // Confirm delete actions
  document.querySelectorAll(".delete-confirm").forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      if (
        !confirm(
          "Are you sure you want to delete this item? This action cannot be undone."
        )
      ) {
        e.preventDefault();
      }
    });
  });
});

// Update potential payout based on selected option and bet amount
function updatePotentialPayout() {
  var selectedOption = document.querySelector(".betting-option.selected");
  var betAmountInput = document.getElementById("bet_amount");
  var payoutDisplay = document.getElementById("potential_payout");

  if (selectedOption && betAmountInput && payoutDisplay) {
    var odds = parseFloat(selectedOption.getAttribute("data-odds"));
    var amount = parseFloat(betAmountInput.value) || 0;

    if (odds && amount > 0) {
      var payout;
      if (odds > 0) {
        payout = amount + (amount * odds) / 100;
      } else {
        payout = amount + (amount * 100) / Math.abs(odds);
      }
      payoutDisplay.textContent = "$" + payout.toFixed(2);
      payoutDisplay.style.display = "block";
    } else {
      payoutDisplay.style.display = "none";
    }
  }
}

// Show alert message
function showAlert(message, type = "info") {
  var alertContainer = document.getElementById("alert-container");
  if (!alertContainer) {
    alertContainer = document.createElement("div");
    alertContainer.id = "alert-container";
    alertContainer.className = "position-fixed top-0 end-0 p-3";
    alertContainer.style.zIndex = "9999";
    document.body.appendChild(alertContainer);
  }

  var alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

  alertContainer.insertAdjacentHTML("beforeend", alertHtml);

  // Auto-remove after 5 seconds
  setTimeout(function () {
    var alerts = alertContainer.querySelectorAll(".alert");
    if (alerts.length > 0) {
      alerts[0].remove();
    }
  }, 5000);
}

// Format currency
function formatCurrency(amount) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(amount);
}

// Format date
function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

// API helper functions
const API = {
  async get(url) {
    try {
      const response = await fetch(url);
      if (!response.ok) throw new Error("Network response was not ok");
      return await response.json();
    } catch (error) {
      console.error("API GET Error:", error);
      throw error;
    }
  },

  async post(url, data) {
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error("Network response was not ok");
      return await response.json();
    } catch (error) {
      console.error("API POST Error:", error);
      throw error;
    }
  },
};

// Real-time updates (placeholder for future WebSocket implementation)
function initializeRealTimeUpdates() {
  // This will be implemented with WebSockets in Phase 3
  console.log("Real-time updates will be implemented in Phase 3");
}

// Export functions for use in other modules
window.FantasyBetting = {
  showAlert,
  formatCurrency,
  formatDate,
  API,
  updatePotentialPayout,
};
