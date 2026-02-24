const chatContainer = document.getElementById('chatContainer');
const userInput = document.getElementById('userInput');


function autoResize(textarea) {
    textarea.style.height = 'auto'; 
    textarea.style.height = textarea.scrollHeight + 'px';
}

function appendMessage(text, sender) {
    // hämtar template
    const template = document.getElementById('message-template');
    const div = template.content.cloneNode(true).firstElementChild;

    div.classList.add(sender);

    // avatar
    const avatar = div.querySelector('.avatar');
    avatar.classList.add(sender);
    avatar.innerText = sender === 'user' ? 'U' : 'AI';

    // setting the message text
    const content = div.querySelector('.message-content');
    content.innerText = text;

    // appendar 
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

    // thinking template
    const thinkingTemplate = document.getElementById('thinking-template');
    const loadingDiv = thinkingTemplate.content.cloneNode(true).firstElementChild;

    chatContainer.appendChild(loadingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text, model: selectedModel })
        });
        
        const result = await response.json();
        
        // tar bort "Thinking..."
        if (loadingDiv.parentNode) {
            chatContainer.removeChild(loadingDiv);
        }

        if (result.type === 'json_recommendation') {
            appendRecommendationCards(result);
        } else {
            appendMessage("Något gick fel.", 'ai');
        }
    } catch (error) {
        if (loadingDiv.parentNode) {
            chatContainer.removeChild(loadingDiv);
        }
        appendMessage("Error: Kunde inte nå servern.", 'ai');
    }
}

function appendRecommendationCards(responsedata) {
    const shows = responsedata.data;
    const introText = responsedata.intro || "Här är resultaten:";

    // container template
    const containerTemplate = document.getElementById('recommendations-container-template');
    const msgDiv = containerTemplate.content.cloneNode(true).firstElementChild;
    
    // internal elements
    const contentDiv = msgDiv.querySelector('.message-content');
    const introP = msgDiv.querySelector('.intro-text');
    
    // intro text
    introP.innerText = introText;

    // card template
    const cardTemplate = document.getElementById('card-template');

    shows.forEach(show => {
        const clone = cardTemplate.content.cloneNode(true);
        
        let score = show.score || 0;
        let scoreClass = 'score-high';
        if (score < 40) scoreClass = 'score-low';
        else if (score < 70) scoreClass = 'score-mid';

        const badge = clone.querySelector('.score-badge');
        badge.innerText = `${score}% Match`;
        badge.classList.add(scoreClass);

        clone.querySelector('.title-text').innerText = show.title;
        clone.querySelector('.rating-text').innerText = `imdb rating: (${show.rating})`;
        clone.querySelector('.year-text').innerText = `(${show.year})`;
        clone.querySelector('.rec-reason').innerText = show.reason;

        contentDiv.appendChild(clone);
    });

    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Enter skickar meddelande, Shift+Enter ny rad
userInput.addEventListener("keydown", function(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
});