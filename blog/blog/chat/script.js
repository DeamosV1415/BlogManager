
const API_URL = 'http://localhost:8000/chat';
const SESSION_ID = 'user_' + Math.random().toString(36).substr(2, 9);


const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const loading = document.getElementById('loading');


function addMessage(content, isUser) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    messageDiv.textContent = content;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}


function setLoading(isLoading) {
    loading.style.display = isLoading ? 'block' : 'none';
    sendBtn.disabled = isLoading;
    chatInput.disabled = isLoading;
}

let isProcessing = false;

async function sendMessage() {
    if (isProcessing) return;
    const message = chatInput.value.trim();
    if (!message) return;

    isProcessing = true;
    addMessage(message, true);
    chatInput.value = '';
    setLoading(true);

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                session_id: SESSION_ID
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        addMessage(data.reply, false);
    } catch (error) {
        console.error('Error:', error);
        addMessage('❌ Sorry, I could not connect to the server. Please try again later.', false);
    } finally {
        isProcessing = false;
        setLoading(false);
        chatInput.focus();
    }
}

// Event Listeners
sendBtn.addEventListener('click', sendMessage);

chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

window.addEventListener('load', () => {
    setTimeout(() => {
        addMessage("Hi! I'm Inko, your professional blog writing assistant. What topic would you like to write about, and what is the primary goal of your blog? 📝", false);
    }, 500);
    chatInput.focus();
});
