<?php
include'../includes/connection.php';
include'../includes/sidebar.php';
?>

<div class="card shadow mb-4">
    <div class="card-header py-3">
        <h4 class="m-2 font-weight-bold text-primary">SCMS Assistant</h4>
    </div>
    <div class="card-body">
        <div id="chat-messages" class="mb-4" style="height: 400px; overflow-y: auto;">
            <!-- Messages will appear here -->
        </div>
        <div class="input-group">
            <input type="text" id="user-input" class="form-control" placeholder="Ask a question about inventory, sales, or customers...">
            <div class="input-group-append">
                <button class="btn btn-primary" type="button" id="send-button">
                    <i class="fas fa-paper-plane"></i> Send
                </button>
            </div>
        </div>
    </div>
</div>

<script>
document.getElementById('send-button').addEventListener('click', sendMessage);
document.getElementById('user-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

function appendMessage(message, isUser = false) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `p-3 mb-2 ${isUser ? 'bg-primary text-white text-right' : 'bg-light'}`;
    messageDiv.style.borderRadius = '10px';
    messageDiv.style.maxWidth = '80%';
    messageDiv.style.margin = isUser ? '10px 0 10px auto' : '10px auto 10px 0';
    messageDiv.textContent = message;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendMessage() {
    const input = document.getElementById('user-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Clear input
    input.value = '';
    
    // Show user message
    appendMessage(message, true);
    
    try {
        const response = await fetch('http://localhost:8000/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            mode: 'cors',
            body: JSON.stringify({
                question: message
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        appendMessage(data.answer);
        
    } catch (error) {
        console.error('Error:', error);
        appendMessage('Sorry, I encountered an error while processing your request. Error: ' + error.message);
    }
}
</script>

<?php
include'../includes/footer.php';
?> 