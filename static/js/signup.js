document.addEventListener('DOMContentLoaded', () => {

    const form = document.querySelector('form');

    form.onsubmit = (event) => {
        event.preventDefault();

        fetch('/api/signup', {
            'method': "POST",
            'body': new FormData(form),
            "headers": {
                "Content-Type": "application/json"
            }
        }).then(response => {
            console.log(response.json());
        })
    };

});