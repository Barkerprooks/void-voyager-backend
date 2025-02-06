const validateField = (field, {min, max}) => {
    let errors = [];
    
    if (max != null && field.value.length > max)
        errors.push(`${field.name} must only be ${max} characters long`);

    if (min != null && field.value.length < min)
        errors.push(`${field.name} must be at least ${min} characters long`);

    return errors;
};

document.addEventListener('DOMContentLoaded', () => {

    let errors = [];
    
    const form = document.querySelector('form');
    const error = document.querySelector('.error');
    const inputs = document.querySelectorAll('input');
    const submit = document.querySelector('input[type=submit]');

    const username = document.querySelector('input[name=username]');
    const password = document.querySelector('input[name=password]');

    inputs.forEach(input => {
        input.onkeyup = () => {
            errors = []; 
        
            errors = errors.concat(validateField(username, {min: 3, max: 80}));
            errors = errors.concat(validateField(password, {min: 8, max: 80}));

            error.innerHTML = errors.join('<br/>');
            submit.disabled = errors.length > 0;
        };
    });

    form.addEventListener('submit', (event) => {
        const formData = new FormData(form);

        fetch('/api/signup', {
            method: "POST",
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: formData.get('username'),
                password: formData.get('password')
            })
        }).then(async response => {
            switch (response.status) {
                case 403:
                    error.innerText = "username exists already";
                    break;
                case 400:
                case 500:
                    error.innerText = "fatal error, try again later";
                    break;
                default: // 200-300
                    window.location = '/';
            }
        });

        event.preventDefault();
    });
});