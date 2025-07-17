document.addEventListener('DOMContentLoaded', () => {
    // Ambil variabel yang dilewatkan dari HTML setelah DOM siap
    const CHAT_API_URL = JSON.parse(document.getElementById('chat-api-url').textContent);
    const BOT_AVATAR_URL = JSON.parse(document.getElementById('bot-avatar-url').textContent);

    const chatBox = document.getElementById("chatBox");
    const userInput = document.getElementById("userInput");
    const sendButton = document.getElementById("sendButton");
    const typingIndicator = document.getElementById("typingIndicator");
    let sessionId = localStorage.getItem("chat_session_id");

    function addMessage(message, sender) {
        const messageWrapper = document.createElement("div");
        messageWrapper.classList.add("chat-message", sender);

        if (sender === "bot") {
            const avatarDiv = document.createElement("div");
            avatarDiv.classList.add("avatar");
            const avatarImg = document.createElement("img");
            avatarImg.src = BOT_AVATAR_URL; // Gunakan variabel dari HTML
            avatarImg.alt = "Bot Avatar";
            avatarDiv.appendChild(avatarImg);
            messageWrapper.appendChild(avatarDiv);
        }

        const bubble = document.createElement("div");
        bubble.classList.add("message-bubble");
        bubble.textContent = message;

        messageWrapper.appendChild(bubble);
        chatBox.appendChild(messageWrapper);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    async function sendMessage() {
        const messageText = userInput.value.trim();
        if (messageText === "") return;

        addMessage(messageText, "user");
        userInput.value = "";
        typingIndicator.style.display = "block";

        try {
            const response = await fetch(CHAT_API_URL, { // Gunakan variabel dari HTML
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    message: messageText,
                    session_id: sessionId,
                }),
            });

            typingIndicator.style.display = "none";

            if (!response.ok) {
                // Mencoba membaca response sebagai HTML jika bukan JSON valid
                const errorText = await response.text();
                addMessage(`Error: Server merespon dengan status ${response.status}.`, "bot");
                console.error("Server response:", errorText);
                return;
            }

            const data = await response.json();
            addMessage(data.message, "bot");
            if (data.session_id && !sessionId) {
                sessionId = data.session_id;
                localStorage.setItem("chat_session_id", sessionId);
            }
        } catch (error) {
            typingIndicator.style.display = "none";
            console.error("Error mengirim pesan:", error);
            addMessage("Maaf, terjadi kesalahan. Periksa console untuk detail.", "bot");
        }
    }
    
    // Pastikan elemen ada sebelum menambahkan event listener
    if(sendButton) {
        sendButton.addEventListener("click", sendMessage);
    }
    
    if(userInput) {
        userInput.addEventListener("keypress", function (event) {
            if (event.key === "Enter") {
                sendMessage();
            }
        });
    }
});