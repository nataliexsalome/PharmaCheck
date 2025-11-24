document.addEventListener('DOMContentLoaded', function() {
    const loginTab = document.getElementById('login-tab');
    const signupTab = document.getElementById('signup-tab');
    const loginPanel = document.getElementById('login-panel');
    const signupPanel = document.getElementById('signup-panel');
    
    // 1. Set Footer Year
    const currentYearElement = document.getElementById("current-year");
    if (currentYearElement) {
        currentYearElement.textContent = new Date().getFullYear();
    }

    // 2. Function to switch panels (tabs)
    function switchTab(target) {
        if (target === 'login') {
            loginTab.classList.add('active-tab');
            signupTab.classList.remove('active-tab');
            loginPanel.classList.add('active-panel');
            signupPanel.classList.remove('active-panel');
        } else {
            signupTab.classList.add('active-tab');
            loginTab.classList.remove('active-tab');
            signupPanel.classList.add('active-panel');
            loginPanel.classList.remove('active-panel');
        }
    }

    // 3. Add event listeners for tab switching
    if (loginTab && signupTab) {
        loginTab.addEventListener('click', () => switchTab('login'));
        signupTab.addEventListener('click', () => switchTab('signup'));
    }

    // NOTE: In a real application, you would add form submission logic here.
});