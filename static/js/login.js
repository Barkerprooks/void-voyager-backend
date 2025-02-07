document.addEventListener('DOMContentLoaded', () => {
    const error = document.querySelector('.error');
    const form = document.querySelector('form');

    form.addEventListener('submit', (event) => {
        const formData = new FormData(form);

        fetch('/api/login', {
            method: "POST",
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: formData.get('username'),
                password: formData.get('password')
            })
        }).then(async response => {
            switch (response.status) {
                case 401:
                    error.innerText = "invalid credentials";
                    break;
                case 400:
                case 500:
                    error.innerText = "fatal error, try again later";
                    break;
                default: // 200-300
                    window.location = '/dashboard';
            }
        });

        event.preventDefault();
    });

});