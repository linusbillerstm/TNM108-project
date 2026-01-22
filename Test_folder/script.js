/* --- VARIABLER --- */
let currentUser = null; // Håller koll på vem som är inloggad
const chatContainer = document.getElementById('chatContainer');
const userInput = document.getElementById('userInput');

/* --- 1. INLOGGNING & REGISTRERING --- */

// Körs direkt när sidan laddas för att se om vi redan är inloggade
window.onload = async function() {
    const response = await fetch('/check_session');
    const data = await response.json();
    if (data.logged_in) {
        setLoggedInState(data.username);
    }
};

// Hantera inloggnings-knappen i menyn
const openLoginBtn = document.getElementById('openLoginBtn');
const loginModal = document.getElementById('loginModal');
const registerModal = document.getElementById('registerModal');

// Öppna rutan
openLoginBtn.onclick = function() {
    if (currentUser) {
        // Om vi redan är inloggade, funkar knappen som "Logga ut"
        logout();
    } else {
        loginModal.style.display = "block";
    }
}

// Stäng rutor om man klickar utanför
window.onclick = function(event) {
    if (event.target == loginModal) loginModal.style.display = "none";
    if (event.target == registerModal) registerModal.style.display = "none";
}

// Hämta alla element med klassen "close" (dina kryss)
const closeSpans = document.querySelectorAll('.close');

// Ge båda kryssen funktionen att stänga sin modal
closeSpans.forEach(span => {
    span.onclick = function() {
        loginModal.style.display = "none";
        registerModal.style.display = "none";
    }
});

// Byt mellan Login och Register
document.getElementById('switchToRegister').onclick = (e) => {
    e.preventDefault();
    loginModal.style.display = "none";
    registerModal.style.display = "block";
};
document.getElementById('switchToLogin').onclick = (e) => {
    e.preventDefault();
    registerModal.style.display = "none";
    loginModal.style.display = "block";
};

// SKICKA LOGIN TILL PYTHON
document.getElementById('loginForm').onsubmit = async (e) => {
    e.preventDefault(); // Stoppa sidan från att ladda om
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

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

// SKICKA REGISTRERING TILL PYTHON
document.getElementById('registerForm').onsubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

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
    
    // Återställ knappen
    openLoginBtn.innerHTML = "Log In"; 
    
    // Återställ välkomstmeddelandet
    const welcomeMsg = document.getElementById('welcome-msg');
    if (welcomeMsg) {
        welcomeMsg.innerText = "Hej! Logga in för att spara serier, eller fråga direkt.";
    }
    
    alert("Utloggad.");
}

function setLoggedInState(username) {
    currentUser = username;
    
    // 1. Ändra knappen i menyn till BARA "Logga ut"
    openLoginBtn.innerHTML = "Logga ut";
    
    // 2. Ändra välkomstmeddelandet i chatten
    const welcomeMsg = document.getElementById('welcome-msg');
    if (welcomeMsg) {
        welcomeMsg.innerHTML = `Välkommen tillbaka, <b>${username}</b>! <br>Jag är redo att spara dina favoriter.`;
    }
}

/* --- 2. CHAT & GILLA FUNKTIONER --- */

async function sendMessage() {
    const text = userInput.value.trim();
    // Hämta vald modell
    const selectedModel = document.getElementById('modelSelect').value;

    if (text === "") return;

    appendMessage(text, 'user');
    userInput.value = "";
    userInput.style.height = 'auto'; // Återställ höjden

    // Skicka både meddelande OCH modell till Python
    const response = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            message: text, 
            model: selectedModel // Här skickar vi valet (gemini, tfidf, eller nomic)
        })
    });
    
    const result = await response.json();

    if (result.type === 'json_recommendation') {
        appendRecommendationCards(result);
    }
}

function appendMessage(text, sender) {
    const div = document.createElement('div');
    div.classList.add('message', sender);
    
    // Vi byter ut vanliga radbrytningar (\n) mot HTML-radbrytningar (<br>)
    // så att texten ser exakt ut som användaren skrev den.
    const formattedText = text.replace(/\n/g, '<br>');

    div.innerHTML = `
        <div class="avatar ${sender}">${sender === 'user' ? 'U' : 'AI'}</div>
        <div class="message-content">${formattedText}</div>
    `;
    
    chatContainer.appendChild(div);
    // Scrolla ner automatiskt
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// RITA UPP KORTEN MED TUMME UPP
function appendRecommendationCards(responsedata) {
    const shows = responsedata.data;
    const introText = responsedata.intro || "Här är några förslag:"; // Fallback om intro saknas

    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', 'ai');
    
    // Skapa Avatar
    const avatarDiv = document.createElement('div');
    avatarDiv.classList.add('avatar', 'ai');
    avatarDiv.innerText = 'AI';
    
    // Skapa innehållet
    const contentDiv = document.createElement('div');
    contentDiv.classList.add('message-content');
    
    // 1. Lägg till intro-texten först
    let htmlContent = `<p style="margin-bottom: 10px;">${introText}</p>`;
    
    // 2. Loopa igenom serierna och skapa kort
    shows.forEach(show => {
        htmlContent += `
        <div style="
            background: rgba(255,255,255,0.05); 
            padding: 15px; 
            margin-bottom: 10px; 
            border-radius: 8px; 
            border: 1px solid #565869;">
            
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div>
                    <h3 style="margin: 0; color: #10a37f; font-size: 1.1em;">
                        ${show.title} <span style="font-size:0.8em; color:#999;">(${show.year})</span>
                    </h3>
                    <p style="margin-top: 5px; font-size: 0.95em; color: #ddd; line-height: 1.4;">
                        ${show.reason}
                    </p>
                </div>
                
                <button onclick="likeShow('${show.title}', this)" style="
                    background: transparent; 
                    border: 1px solid #565869; 
                    color: white; 
                    cursor: pointer; 
                    padding: 6px 12px; 
                    border-radius: 4px; 
                    transition: all 0.2s;
                    margin-left: 10px;
                    white-space: nowrap;">
                    👍 Gilla
                </button>
            </div>
        </div>
        `;
    });

    contentDiv.innerHTML = htmlContent;
    
    msgDiv.appendChild(avatarDiv);
    msgDiv.appendChild(contentDiv);
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// NÄR MAN KLICKAR PÅ TUMMEN
async function likeShow(title, btnElement) {
    // 1. Kolla om man är inloggad först
    if (!currentUser) {
        alert("Du måste logga in för att spara serier!");
        return;
    }

    // 2. Skicka till backend
    const res = await fetch('/like', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ title: title })
    });
    const result = await res.json();

    // 3. Visa att det funkade
    if (result.status === 'success') {
        btnElement.innerText = "✅ Sparad";
        btnElement.disabled = true; // Stäng av knappen så man inte klickar igen
    } else {
        alert(result.message); // T.ex "Redan sparad"
    }
}

// Skicka meddelande med Enter (men Shift+Enter gör ny rad)
userInput.addEventListener("keydown", function(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault(); // Hindra att det blir en ny rad
        sendMessage();
    }
});

// Auto-resize funktion (så rutan växer när man skriver)
function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
}