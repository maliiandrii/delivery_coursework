document.addEventListener('DOMContentLoaded', function() {
    const messages = document.querySelectorAll('.message');

    messages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            message.style.transition = 'opacity 0.5s';

            setTimeout(() => {
                message.remove();
            }, 500);
        }, 5000);
    });

    const addToCartForms = document.querySelectorAll('form[action*="add-to-cart"]');
    addToCartForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const button = form.querySelector('button');
            button.disabled = true;
            button.style.opacity = '0.6';

            setTimeout(() => {
                button.disabled = false;
                button.style.opacity = '1';
            }, 1000);
        });
    });
});
