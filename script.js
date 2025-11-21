// Configuration
const API_URL = 'http://127.0.0.1:8000/chat';
const SESSION_ID = 'user_' + Math.random().toString(36).substr(2, 9);

// DOM elements
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const loading = document.getElementById('loading');

// Add message to chat
function addMessage(content, isUser) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    messageDiv.textContent = content;
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Show/hide loading indicator
function setLoading(isLoading) {
    loading.style.display = isLoading ? 'block' : 'none';
    sendBtn.disabled = isLoading;
    userInput.disabled = isLoading;
}

// Send message to backend
async function sendMessage() {
    const message = userInput.value.trim();
    
    // Don't send empty messages
    if (!message) return;
    
    // Add user message to chat
    addMessage(message, true);
    
    // Clear input
    userInput.value = '';
    
    // Show loading
    setLoading(true);
    
    try {
        // Call API
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: SESSION_ID
            })
        });
        
        // Check if response is OK
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // Get bot reply
        const data = await response.json();
        addMessage(data.reply, false);
        
    } catch (error) {
        console.error('Error:', error);
        addMessage('❌ Sorry, I couldn\'t connect to the server. Please make sure the backend is running.', false);
    } finally {
        // Hide loading
        setLoading(false);
        
        // Focus input for next message
        userInput.focus();
    }
}

// Event listeners
sendBtn.addEventListener('click', sendMessage);

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Initial greeting when page loads
window.addEventListener('load', () => {
    setTimeout(() => {
        addMessage('Hi! I\'m your blog writing assistant. What topic would you like to write about? 📝', false);
    }, 500);
    
    // Focus input
    userInput.focus();
});
