const chatContainer = document.getElementById('chatContainer');
const userInput = document.getElementById('userInput');

// Auto-resize the text area
function autoResize(textarea) {
    textarea.style.height = 'auto'; 
    textarea.style.height = textarea.scrollHeight + 'px';
}

// Add a message to the UI
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
    
    // Auto scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Function called when "Send" is clicked
function sendMessage() {
    const text = userInput.value.trim();
    if (text === "") return;

    // 1. Show User Message
    appendMessage(text, 'user');
    userInput.value = "";
    userInput.style.height = '24px'; // Reset height

    // 2. Simulate AI Thinking (Placeholder)
    const loadingDiv = document.createElement('div');
    loadingDiv.classList.add('message', 'ai');
    loadingDiv.innerHTML = `<div class="avatar ai">AI</div><div class="message-content typing-indicator">Thinking</div>`;
    chatContainer.appendChild(loadingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    // 3. Simulate AI Response (Delete this part when you connect Python!)
    setTimeout(() => {
        chatContainer.removeChild(loadingDiv);
        appendMessage("This is where your Python Qwen3 model response will go! It works!", 'ai');
    }, 1500);
}

// Allow pressing "Enter" to send
userInput.addEventListener("keypress", function(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
});