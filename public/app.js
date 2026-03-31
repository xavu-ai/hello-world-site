// Hello World JavaScript
document.addEventListener('DOMContentLoaded', () => {
    const timestampEl = document.getElementById('timestamp');
    
    if (timestampEl) {
        const now = new Date();
        timestampEl.textContent = `Page loaded at: ${now.toLocaleString()}`;
    }
    
    // Add a simple interaction
    const greeting = document.getElementById('greeting');
    if (greeting) {
        greeting.addEventListener('click', () => {
            greeting.style.color = greeting.style.color === 'rgb(102, 126, 234)' ? '#764ba2' : '#667eea';
        });
    }
});
