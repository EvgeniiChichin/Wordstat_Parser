function hideMessages() {
    var messageContainer = document.getElementById('message-container');
    if (messageContainer) {
        messageContainer.style.opacity = '0';
        setTimeout(function() {
            messageContainer.style.display = 'none';
        }, 500);
    }
}

function showMessage(message, type) {
    var messageContainer = document.getElementById('message-container');
    if (!messageContainer) {
        messageContainer = document.createElement('div');
        messageContainer.id = 'message-container';
        document.body.insertBefore(messageContainer, document.body.firstChild);
    }

    var alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-' + type;
    alertDiv.textContent = message;

    messageContainer.appendChild(alertDiv);
    messageContainer.style.display = 'block';
    messageContainer.style.opacity = '1';

    setTimeout(hideMessages, 5000);
}

document.addEventListener('DOMContentLoaded', function() {
    setTimeout(hideMessages, 5000);
});