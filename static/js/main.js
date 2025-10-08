// Fantasy Betting League - Main JavaScript

// Global configuration
const CONFIG = {
  API_BASE_URL: '/api',
  CURRENCY_SYMBOL: '$',
  ANIMATION_DURATION: 300,
  DEBOUNCE_DELAY: 500
};

// Utility functions
const Utils = {
  // Format currency
  formatCurrency: (amount) => {
    return `${CONFIG.CURRENCY_SYMBOL}${parseFloat(amount).toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })}`;
  },

  // Format number with commas
  formatNumber: (num) => {
    return parseInt(num).toLocaleString();
  },

  // Debounce function
  debounce: (func, wait) => {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },

  // Show toast notification
  showToast: (message, type = 'info', duration = 5000) => {
    const toastContainer = document.querySelector('.toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
      <div class="d-flex">
        <div class="toast-body">
          ${message}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
      </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast, {
      autohide: true,
      delay: duration
    });
    
    bsToast.show();
    
    // Remove toast element after it's hidden
    toast.addEventListener('hidden.bs.toast', () => {
      toast.remove();
    });
  },

  // Create toast container if it doesn't exist
  createToastContainer: () => {
    const container = document.createElement('div');
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '3000';
    document.body.appendChild(container);
    return container;
  },

  // Animate number counting
  animateCounter: (element, start, end, duration = 1000) => {
    const startTime = performance.now();
    const isIncreasing = end > start;
    
    function updateCounter(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Easing function (ease-out)
      const easeOut = 1 - Math.pow(1 - progress, 3);
      const current = start + (end - start) * easeOut;
      
      element.textContent = Utils.formatCurrency(current);
      
      if (progress < 1) {
        requestAnimationFrame(updateCounter);
      } else {
        element.textContent = Utils.formatCurrency(end);
      }
    }
    
    requestAnimationFrame(updateCounter);
  },

  // Copy text to clipboard
  copyToClipboard: async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      Utils.showToast('Copied to clipboard!', 'success', 2000);
    } catch (err) {
      console.error('Failed to copy: ', err);
      Utils.showToast('Failed to copy to clipboard', 'error', 3000);
    }
  },

  // Format relative time
  formatRelativeTime: (date) => {
    const now = new Date();
    const diff = now - new Date(date);
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    if (minutes > 0) return `${minutes}m ago`;
    return 'Just now';
  }
};

// Form validation helpers
const FormValidator = {
  // Validate email
  validateEmail: (email) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  },

  // Validate username
  validateUsername: (username) => {
    const re = /^[a-zA-Z0-9_]{3,20}$/;
    return re.test(username);
  },

  // Validate password strength
  validatePassword: (password) => {
    return password.length >= 6;
  },

  // Show field validation
  showFieldValidation: (field, isValid, message = '') => {
    field.classList.remove('is-valid', 'is-invalid');
    field.classList.add(isValid ? 'is-valid' : 'is-invalid');
    
    // Remove existing feedback
    const existingFeedback = field.parentNode.querySelector('.invalid-feedback, .valid-feedback');
    if (existingFeedback) {
      existingFeedback.remove();
    }
    
    // Add new feedback if message provided
    if (message) {
      const feedback = document.createElement('div');
      feedback.className = isValid ? 'valid-feedback' : 'invalid-feedback';
      feedback.textContent = message;
      field.parentNode.appendChild(feedback);
    }
  }
};

// API helpers
const API = {
  // Make API request
  request: async (endpoint, options = {}) => {
    const url = `${CONFIG.API_BASE_URL}${endpoint}`;
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
      }
    };
    
    const finalOptions = { ...defaultOptions, ...options };
    
    try {
      const response = await fetch(url, finalOptions);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'API request failed');
      }
      
      return data;
    } catch (error) {
      console.error('API request error:', error);
      throw error;
    }
  },

  // Get CSRF token
  getCSRFToken: () => {
    const token = document.querySelector('meta[name="csrf-token"]');
    return token ? token.getAttribute('content') : '';
  }
};

// Betting interface helpers
const BettingInterface = {
  // Calculate potential payout
  calculatePayout: (amount, odds) => {
    return parseFloat(amount) * parseFloat(odds);
  },

  // Format odds display
  formatOdds: (odds) => {
    return `+${(odds * 100).toFixed(0)}`;
  },

  // Update bet slip
  updateBetSlip: (ticketId, option, odds, amount) => {
    const betSlip = document.querySelector('.bet-slip');
    if (!betSlip) return;

    const selectedBet = betSlip.querySelector('.selected-bet');
    const amountInput = betSlip.querySelector('.bet-amount');
    const potentialWin = betSlip.querySelector('.potential-win .amount');

    if (selectedBet) {
      selectedBet.innerHTML = `
        <div class="bet-details">
          <div class="bet-option">${option}</div>
          <div class="bet-odds">${BettingInterface.formatOdds(odds)}</div>
        </div>
      `;
    }

    if (amountInput && amount) {
      amountInput.value = amount;
    }

    if (potentialWin && amount && odds) {
      const payout = BettingInterface.calculatePayout(amount, odds);
      potentialWin.textContent = Utils.formatCurrency(payout);
    }
  },

  // Validate bet amount
  validateBetAmount: (amount, userBalance) => {
    const numAmount = parseFloat(amount);
    const minBet = 1.0;
    const maxBet = parseFloat(userBalance);

    if (isNaN(numAmount) || numAmount < minBet) {
      return { valid: false, message: `Minimum bet is ${Utils.formatCurrency(minBet)}` };
    }

    if (numAmount > maxBet) {
      return { valid: false, message: `Insufficient balance. You have ${Utils.formatCurrency(maxBet)}` };
    }

    return { valid: true };
  }
};

// League management helpers
const LeagueManager = {
  // Join league with invite code
  joinLeague: async (inviteCode) => {
    try {
      const response = await API.request(`/leagues/join/${inviteCode}`, {
        method: 'POST'
      });
      
      Utils.showToast('Successfully joined league!', 'success');
      return response;
    } catch (error) {
      Utils.showToast(error.message || 'Failed to join league', 'error');
      throw error;
    }
  },

  // Create new league
  createLeague: async (leagueData) => {
    try {
      const response = await API.request('/leagues', {
        method: 'POST',
        body: JSON.stringify(leagueData)
      });
      
      Utils.showToast('League created successfully!', 'success');
      return response;
    } catch (error) {
      Utils.showToast(error.message || 'Failed to create league', 'error');
      throw error;
    }
  }
};

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  // Initialize tooltips
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

  // Initialize popovers
  const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
  popoverTriggerList.map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));

  // Add smooth scrolling to anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });

  // Initialize copy buttons
  document.querySelectorAll('.copy-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const text = btn.getAttribute('data-copy');
      if (text) {
        Utils.copyToClipboard(text);
      }
    });
  });

  // Initialize animated counters
  document.querySelectorAll('.animate-counter').forEach(element => {
    const start = parseFloat(element.dataset.start) || 0;
    const end = parseFloat(element.dataset.end) || 0;
    const duration = parseInt(element.dataset.duration) || 1000;
    
    Utils.animateCounter(element, start, end, duration);
  });

  // Add loading states to forms
  document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', (e) => {
      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
        
        // Re-enable button after 10 seconds as fallback
        setTimeout(() => {
          submitBtn.disabled = false;
          submitBtn.innerHTML = submitBtn.dataset.originalText || 'Submit';
        }, 10000);
      }
    });
  });

  // Initialize real-time updates (if on league pages)
  if (window.location.pathname.includes('/leagues/')) {
    initializeRealTimeUpdates();
  }
});

// Real-time updates for league pages
function initializeRealTimeUpdates() {
  // This would typically connect to WebSockets or use polling
  // For now, we'll set up a basic polling mechanism
  const leagueId = window.location.pathname.split('/').pop();
  
  if (leagueId && !isNaN(leagueId)) {
    setInterval(async () => {
      try {
        // Poll for updates every 30 seconds
        const response = await API.request(`/leagues/${leagueId}/updates`);
        updateLeagueData(response);
      } catch (error) {
        console.log('Failed to fetch updates:', error);
      }
    }, 30000);
  }
}

// Update league data with real-time information
function updateLeagueData(data) {
  // Update leaderboard
  if (data.leaderboard) {
    updateLeaderboard(data.leaderboard);
  }
  
  // Update ticket statuses
  if (data.tickets) {
    updateTicketStatuses(data.tickets);
  }
  
  // Update user balance
  if (data.userBalance) {
    updateUserBalance(data.userBalance);
  }
}

// Update leaderboard display
function updateLeaderboard(leaderboard) {
  const leaderboardContainer = document.querySelector('.leaderboard-list');
  if (!leaderboardContainer) return;

  leaderboardContainer.innerHTML = leaderboard.map((member, index) => `
    <div class="leaderboard-item">
      <div class="rank">${index + 1}</div>
      <div class="user">
        <div class="avatar" style="background-color: var(--accent-neon);">
          ${member.username[0].toUpperCase()}
        </div>
        <div class="name">${member.username}</div>
      </div>
      <div class="balance">${Utils.formatCurrency(member.balance)}</div>
    </div>
  `).join('');
}

// Update ticket statuses
function updateTicketStatuses(tickets) {
  tickets.forEach(ticket => {
    const ticketElement = document.querySelector(`[data-ticket-id="${ticket.id}"]`);
    if (ticketElement) {
      const statusBadge = ticketElement.querySelector('.status-badge');
      if (statusBadge) {
        statusBadge.className = `badge badge-status-${ticket.status.toLowerCase()}`;
        statusBadge.textContent = ticket.status.toUpperCase();
      }
    }
  });
}

// Update user balance
function updateUserBalance(balance) {
  const balanceElements = document.querySelectorAll('.user-balance');
  balanceElements.forEach(element => {
    Utils.animateCounter(element, parseFloat(element.textContent.replace(/[$,]/g, '')), balance);
  });
}

// Export utilities for use in other scripts
window.FantasyBetting = {
  Utils,
  FormValidator,
  API,
  BettingInterface,
  LeagueManager,
  CONFIG
};
