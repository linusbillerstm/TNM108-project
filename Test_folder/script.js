/* --- MODAL LOGIC (New Stuff) --- */

const loginModal = document.getElementById('loginModal');
const registerModal = document.getElementById('registerModal');
const openLoginBtn = document.getElementById('openLoginBtn');
const closeBtns = document.querySelectorAll('.close-btn');
const switchToRegister = document.getElementById('switchToRegister');
const switchToLogin = document.getElementById('switchToLogin');

// 1. Open Login Modal
if (openLoginBtn) {
    openLoginBtn.addEventListener('click', () => {
        loginModal.style.display = 'block';
    });
}

// 2. Switch from Login to Register
switchToRegister.addEventListener('click', (e) => {
    e.preventDefault(); 
    loginModal.style.display = 'none';
    registerModal.style.display = 'block';
});

// 3. Switch from Register to Login
switchToLogin.addEventListener('click', (e) => {
    e.preventDefault();
    registerModal.style.display = 'none';
    loginModal.style.display = 'block';
});

// 4. Close Modals (Clicking 'X')
closeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        loginModal.style.display = 'none';
        registerModal.style.display = 'none';
    });
});

// 5. Close Modals (Clicking outside the box)
window.addEventListener('click', (e) => {
    if (e.target == loginModal) loginModal.style.display = 'none';
    if (e.target == registerModal) registerModal.style.display = 'none';
});


/* --- CHAT LOGIC (Old Stuff) --- */
const chatContainer = document.getElementById('chatContainer');
const userInput = document.getElementById('userInput');

function autoResize(textarea) {
    textarea.style.height = 'auto'; 
    textarea.style.height = textarea.scrollHeight + 'px';
}

function appendMessage(text, sender) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender);
    
    const avatarDiv = document.createElement('div');
    avatarDiv.classList.add('avatar', sender);
    avatarDiv.innerText = sender === 'user' ? 'U' : 'AI';

    const contentDiv = document.createElement('div');
    contentDiv.classList.add('message-content');
    contentDiv.innerText = text;

    msgDiv.appendChild(avatarDiv);
    msgDiv.appendChild(contentDiv);
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function sendMessage() {
    const text = userInput.value.trim();
    if (text === "") return;

    appendMessage(text, 'user');
    userInput.value = "";
    userInput.style.height = '24px';

    const loadingDiv = document.createElement('div');
    loadingDiv.classList.add('message', 'ai');
    loadingDiv.innerHTML = `<div class="avatar ai">AI</div><div class="message-content typing-indicator">Thinking</div>`;
    chatContainer.appendChild(loadingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    setTimeout(() => {
        chatContainer.removeChild(loadingDiv);
        appendMessage("I'm ready to connect to the backend!", 'ai');
    }, 1000);
}

userInput.addEventListener("keypress", function(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
});