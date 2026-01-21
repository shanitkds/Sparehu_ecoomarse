// toast.js

// Make toast function globally available
window.showToast = function(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  
  // Check if container exists
  if (!container) {
    console.error('Toast container not found!');
    return;
  }
  
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  
  const icons = {
    success: '✓',
    error: '✕',
    info: 'i',
    warning: '⚠'
  };
  
  toast.innerHTML = `
    <div class="toast-icon">${icons[type] || icons.info}</div>
    <div class="toast-content">${message}</div>
    <button class="toast-close" onclick="window.removeToast(this.parentElement)">
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M4 4l8 8M12 4l-8 8"/>
      </svg>
    </button>
    <div class="toast-progress"></div>
  `;
  
  container.appendChild(toast);
  
  // Auto remove after 3 seconds
  setTimeout(() => {
    window.removeToast(toast);
  }, 3000);
  
  // Pause on hover
  toast.addEventListener('mouseenter', () => {
    const progress = toast.querySelector('.toast-progress');
    if (progress) {
      progress.style.animationPlayState = 'paused';
    }
  });
  
  toast.addEventListener('mouseleave', () => {
    const progress = toast.querySelector('.toast-progress');
    if (progress) {
      progress.style.animationPlayState = 'running';
    }
  });
};

window.removeToast = function(toast) {
  if (!toast) return;
  toast.classList.add('removing');
  setTimeout(() => {
    if (toast.parentNode) {
      toast.remove();
    }
  }, 300);
};

// Helper functions for easier use
window.Toast = {
  success: (message) => window.showToast(message, 'success'),
  error: (message) => window.showToast(message, 'error'),
  info: (message) => window.showToast(message, 'info'),
  warning: (message) => window.showToast(message, 'warning')
};