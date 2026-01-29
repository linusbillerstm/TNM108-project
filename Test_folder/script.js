/* --- GLOBAL STATES --- */
const chatContainer = document.getElementById('chatContainer');
const userInput = document.getElementById('userInput');

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
        clone.querySelector('.rating-text').innerText = `imdb rating: (${show.rating})`;
        clone.querySelector('.year-text').innerText = `(${show.year})`;
        clone.querySelector('.rec-reason').innerText = show.reason;

        // Lägg till kortet i meddelandet
        contentDiv.appendChild(clone);
    });

    msgDiv.appendChild(avatarDiv);
    msgDiv.appendChild(contentDiv);
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Enter-tangent
userInput.addEventListener("keydown", function(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
});