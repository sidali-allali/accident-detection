// --- File Upload Handling ---
const uploadBtn = document.getElementById('uploadBtn');
const videoUploadInput = document.getElementById('videoUploadInput');

uploadBtn.addEventListener('click', () => {
    videoUploadInput.click();
});

videoUploadInput.addEventListener('change', (event) => {
    const file = event.target.files[0];
    if (file) {
        const videoContainer = document.querySelector('.video-container');
        videoContainer.innerHTML = `<video controls autoplay style="width:100%; height:100%; border-radius:8px;">
            <source src="${URL.createObjectURL(file)}">
        </video>`;
    }
});

// --- Slide-out Menu Logic ---
const sideMenu = document.getElementById('sideMenu');
const menuOverlay = document.getElementById('menuOverlay');
const openMenuBtn = document.getElementById('openMenuBtn');
const closeMenuBtn = document.getElementById('closeMenuBtn');

function openMenu() {
    sideMenu.classList.add('open');
    menuOverlay.classList.add('show');
}

function closeMenu() {
    sideMenu.classList.remove('open');
    menuOverlay.classList.remove('show');
}

openMenuBtn.addEventListener('click', openMenu);
closeMenuBtn.addEventListener('click', closeMenu);
menuOverlay.addEventListener('click', closeMenu);

// --- Theme Toggling (Light/Dark Mode) ---
const themeLight = document.getElementById('themeLight');
const themeDark = document.getElementById('themeDark');

themeLight.addEventListener('click', () => {
    document.body.classList.add('light-mode');
    themeLight.classList.add('active');
    themeDark.classList.remove('active');
});

themeDark.addEventListener('click', () => {
    document.body.classList.remove('light-mode');
    themeDark.classList.add('active');
    themeLight.classList.remove('active');
});

// --- Tab Switching (Live Alerts vs Alert History) ---
const navLiveAlerts = document.getElementById('navLiveAlerts');
const navHistory = document.getElementById('navHistory');
const liveAlertsContainer = document.getElementById('liveAlertsContainer');
const historyAlertsContainer = document.getElementById('historyAlertsContainer');
const sidebarTitle = document.getElementById('sidebarTitle');
const actionPanel = document.getElementById('actionPanel');

navLiveAlerts.addEventListener('click', () => {
    // Update active button state
    navLiveAlerts.classList.add('active');
    navHistory.classList.remove('active');
    
    // Show Live Alerts, Hide History
    liveAlertsContainer.style.display = 'block';
    historyAlertsContainer.style.display = 'none';
    sidebarTitle.innerText = "Pending Alerts (2)";
    
    // Show Action Buttons
    actionPanel.style.display = 'flex';
    
    closeMenu();
});

navHistory.addEventListener('click', () => {
    // Update active button state
    navHistory.classList.add('active');
    navLiveAlerts.classList.remove('active');
    
    // Show History, Hide Live Alerts
    historyAlertsContainer.style.display = 'block';
    liveAlertsContainer.style.display = 'none';
    sidebarTitle.innerText = "Alert History (2)";
    
    // Hide Action Buttons (History items can't be re-verified)
    actionPanel.style.display = 'none';
    
    closeMenu();
});
// --- Alert Card Clicking Logic ---
const alertCards = document.querySelectorAll('.alert-card');
const metaTime = document.getElementById('metaTime');
const metaLocation = document.getElementById('metaLocation');
const metaLogic = document.getElementById('metaLogic'); // To update triggering logic text
const dangerLevelSelect = document.getElementById('dangerLevelSelect');

alertCards.forEach(card => {
    card.addEventListener('click', () => {
        // 1. Remove the 'active' highlight from all cards
        alertCards.forEach(c => c.classList.remove('active'));
        
        // 2. Add the 'active' highlight to the clicked card
        card.classList.add('active');

        // 3. Extract the text from the clicked card
        const locationText = card.querySelector('h3').innerText;
        const detailsText = card.querySelector('p').innerText; // e.g., "14:32:05 | Collision"
        
        // Split the details text to get just the time and type
        const timeText = detailsText.split(' | ')[0];
        const typeText = detailsText.split(' | ')[1];
        
        // 4. Determine severity from the card's badge
        const badge = card.querySelector('.badge');
        let severity = "Low";
        if (badge && badge.innerText.includes('High')) severity = "High";
        if (badge && badge.innerText.includes('Med')) severity = "Medium";

        // 5. Update the Metadata panel
        metaLocation.innerText = locationText;
        metaTime.innerText = timeText;
        metaLogic.innerText = typeText; // Set logic to the event type for now
        
        // 6. Update the dropdown value and trigger the color change
        dangerLevelSelect.value = severity;
        updateDropdownColor();
    });
});

// --- Dropdown Color Logic ---
function updateDropdownColor() {
    // Remove all color classes first
    dangerLevelSelect.classList.remove('text-red', 'text-yellow', 'text-orange');
    
    // Add the correct color class based on the newly selected value
    if (dangerLevelSelect.value === 'High') {
        dangerLevelSelect.classList.add('text-red');
    } else if (dangerLevelSelect.value === 'Medium') {
        dangerLevelSelect.classList.add('text-orange');
    } else {
        dangerLevelSelect.classList.add('text-yellow');
    }
}

// Listen for when the user manually changes the dropdown
dangerLevelSelect.addEventListener('change', updateDropdownColor);