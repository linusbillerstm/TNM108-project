/* --- GLOBAL STATES --- */
let currentUser = null;
const chatContainer = document.getElementById('chatContainer');
const userInput = document.getElementById('userInput');

/* --- 1. SESSION & AUTH --- */
window.onload = async function() {
    const response = await fetch('/check_session');
    const data = await response.json();
    if (data.logged_in) {
        setLoggedInState(data.username);
    }
};

const loginModal = document.getElementById('loginModal');
const registerModal = document.getElementById('registerModal');
const openLoginBtn = document.getElementById('openLoginBtn');

openLoginBtn.onclick = function() {
    if (currentUser) logout();
    else loginModal.style.display = "block";
}

document.querySelectorAll('.close').forEach(span => {
    span.onclick = () => {
        loginModal.style.display = "none";
        registerModal.style.display = "none";
    }
});

document.getElementById('switchToRegister').onclick = (e) => {
    e.preventDefault(); loginModal.style.display = "none"; registerModal.style.display = "block";
};
document.getElementById('switchToLogin').onclick = (e) => {
    e.preventDefault(); registerModal.style.display = "none"; loginModal.style.display = "block";
};

// Login Submit
document.getElementById('loginForm').onsubmit = async (e) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.target).entries());
    const res = await fetch('/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });
    const result = await res.json();
    if (result.status === 'success') {
        setLoggedInState(result.username);
        loginModal.style.display = "none";
    } else {
        alert(result.message);
    }
};

// Register Submit
document.getElementById('registerForm').onsubmit = async (e) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.target).entries());
    const res = await fetch('/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });
    const result = await res.json();
    if (result.status === 'success') {
        alert("Konto skapat! Logga in.");
        registerModal.style.display = "none";
        loginModal.style.display = "block";
    } else {
        alert(result.message);
    }
};

async function logout() {
    await fetch('/logout', { method: 'POST' });
    currentUser = null;
    openLoginBtn.innerHTML = "Log In";
    document.getElementById('welcome-msg').innerText = "Hej! Logga in för att spara serier, eller fråga direkt.";
    alert("Utloggad.");
}

function setLoggedInState(username) {
    currentUser = username;
    openLoginBtn.innerHTML = "Logga ut";
    document.getElementById('welcome-msg').innerHTML = `Välkommen tillbaka, <b>${username}</b>! <br>Jag är redo att spara dina favoriter.`;
}

/* --- 2. CHAT & AI LOGIK --- */

function autoResize(textarea) {
    textarea.style.height = 'auto'; 
    textarea.style.height = textarea.scrollHeight + 'px';
}

function appendMessage(text, sender) {
    const div = document.createElement('div');
    div.classList.add('message', sender);
    const formattedText = text.replace(/\n/g, '<br>');
    div.innerHTML = `
        <div class="avatar ${sender}">${sender === 'user' ? 'U' : 'AI'}</div>
        <div class="message-content">${formattedText}</div>
    `;
    chatContainer.appendChild(div);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

async function sendMessage() {
    const text = userInput.value.trim();
    const selectedModel = document.getElementById('modelSelect').value;

    if (text === "") return;

    appendMessage(text, 'user');
    userInput.value = "";
    userInput.style.height = 'auto';

    const loadingDiv = document.createElement('div');
    loadingDiv.classList.add('message', 'ai');
    loadingDiv.innerHTML = `<div class="avatar ai">AI</div><div class="message-content">Thinking...</div>`;
    chatContainer.appendChild(loadingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text, model: selectedModel })
        });
        
        const result = await response.json();
        chatContainer.removeChild(loadingDiv);

        if (result.type === 'json_recommendation') {
            appendRecommendationCards(result);
        } else {
            appendMessage("Något gick fel.", 'ai');
        }
    } catch (error) {
        chatContainer.removeChild(loadingDiv);
        appendMessage("Error: Kunde inte nå servern.", 'ai');
    }
}

// --- DENNA FUNKTION ÄR NU HELT REN FRÅN HTML-STRÄNGAR ---
function appendRecommendationCards(responsedata) {
    const shows = responsedata.data;
    const introText = responsedata.intro || "Här är resultaten:";

    // 1. Skapa AI-meddelande container
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', 'ai');
    
    const avatarDiv = document.createElement('div');
    avatarDiv.classList.add('avatar', 'ai');
    avatarDiv.innerText = 'AI';

    const contentDiv = document.createElement('div');
    contentDiv.classList.add('message-content');
    
    // Intro text
    const p = document.createElement('p');
    p.innerText = introText;
    p.style.marginBottom = "15px";
    p.style.color = "#ccc";
    contentDiv.appendChild(p);
    
    // 2. Hämta mallen från index.html
    const template = document.getElementById('card-template');

    // 3. Loopa och klona mallen för varje serie
    shows.forEach(show => {
        // Klona innehållet i mallen
        const clone = template.content.cloneNode(true);
        
        // Räkna ut score-klass
        let score = show.score || 0;
        let scoreClass = 'score-high';
        if (score < 40) scoreClass = 'score-low';
        else if (score < 70) scoreClass = 'score-mid';

        // Hitta elementen i klonen och fyll i data (INGEN HTML KOD HÄR!)
        const badge = clone.querySelector('.score-badge');
        badge.innerText = `${score}% Match`;
        badge.classList.add(scoreClass);

        clone.querySelector('.title-text').innerText = show.title;
        clone.querySelector('.year-text').innerText = `(${show.year})`;
        clone.querySelector('.rec-reason').innerText = show.reason;

        // Lägg till klick-event på knappen
        const btn = clone.querySelector('.like-btn');
        btn.onclick = function() {
            likeShow(show.title, btn);
        };

        // Lägg till kortet i meddelandet
        contentDiv.appendChild(clone);
    });

    msgDiv.appendChild(avatarDiv);
    msgDiv.appendChild(contentDiv);
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

async function likeShow(title, btnElement) {
    if (!currentUser) {
        alert("Du måste logga in för att spara serier!");
        return;
    }
    const res = await fetch('/like', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ title: title })
    });
    const result = await res.json();
    if (result.status === 'success') {
        btnElement.innerText = "✅ Sparad";
        btnElement.classList.add('saved'); // Använder CSS-klass nu
        btnElement.disabled = true;
    } else {
        alert(result.message);
    }
}

// Enter-tangent
userInput.addEventListener("keydown", function(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
});