/**
 * Main JavaScript for static file hosting demo
 */

document.addEventListener('DOMContentLoaded', () => {
    const app = document.getElementById('app');
    
    // Update the app content
    app.innerHTML = `
        <p>This page is served statically via FastAPI!</p>
        <p>Current time: <span id="time">${new Date().toLocaleString()}</span></p>
        <button id="refresh-btn" style="margin-top: 1rem; padding: 0.5rem 1rem; cursor: pointer;">
            Refresh Time
        </button>
    `;
    
    // Add refresh functionality
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            const timeSpan = document.getElementById('time');
            if (timeSpan) {
                timeSpan.textContent = new Date().toLocaleString();
            }
        });
    }
    
    // Log startup message
    console.log('Static file hosting service initialized');
    
    // Check if health endpoint is accessible
    fetch('/health')
        .then(response => response.json())
        .then(data => {
            console.log('Health check:', data);
        })
        .catch(err => {
            console.error('Health check failed:', err);
        });
});
