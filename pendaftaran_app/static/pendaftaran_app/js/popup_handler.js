document.addEventListener('DOMContentLoaded', function() {
    const messagesContainer = document.getElementById('django-messages');
    if (messagesContainer) {
        const messages = messagesContainer.getElementsByTagName('span');
        for (let i = 0; i < messages.length; i++) {
            const tag = messages[i].getAttribute('data-tag');
            const messageText = messages[i].getAttribute('data-message');

            let iconType = 'info';
            if (tag.includes('success')) {
                iconType = 'success';
            } else if (tag.includes('error')) {
                iconType = 'error';
            } else if (tag.includes('warning')) {
                iconType = 'warning';
            }

            // Menggunakan tema gelap untuk SweetAlert2
            Swal.fire({
                title: tag.charAt(0).toUpperCase() + tag.slice(1),
                text: messageText,
                icon: iconType,
                confirmButtonText: 'Tutup',
                background: 'var(--container-bg)',
                color: 'var(--text-light)',
                confirmButtonColor: 'var(--accent-color)'
            });
        }
    }
});