document.addEventListener('DOMContentLoaded', () => {
    const error = document.querySelector('.error');
    const form = document.querySelector('form');

    form.addEventListener('submit', function(event) {
        const formData = new FormData(form);

        fetch('/api/signup', {
            headers: { 'Content-Type': 'application/json' },
            method: "POST",
            body: JSON.stringify({
                username: formData.get('username'),
                password: formData.get('password')
            })
        }).then(async response => {
            if (response.status == 400) {
                error.innerText = "invalid request";
            } else if (response.status == 500) {
                error.innerText = "user already exists";
            } else {
                window.location = '/'; // send new user to home page
            }
        });

        event.preventDefault();
    });

});