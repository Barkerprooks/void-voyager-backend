
document.addEventListener('DOMContentLoaded', () => {

    const buyShip = document.querySelector('#buy-ship-form');
    const shipOptions = document.querySelectorAll('.user-ship-options');

    buyShip.onsubmit = (event) => {
        
        const formData = new FormData(buyShip);

        fetch('/api/user/buy/ship', {
            headers: {"Content-Type": "application/json"},
            method: "POST",
            body: JSON.stringify({
                ship: formData.get('ship')
            })
        }).then(response => {
            // refresh the page to get most recent data
            window.location.reload();
        })

        event.preventDefault();
    };

    shipOptions.forEach(shipOption => {
        shipOption.onsubmit = (event) => {
            event.preventDefault();

            const formData = new FormData(shipOption, event.submitter);
            const option = formData.get('option');

            if (option == "rename") {
                const name = shipOption.querySelector('.ship-name');
                const selected = shipOption.querySelector('.rename');
                const nameInput = document.createElement('input');
                
                selected.value = "save";
                nameInput.name = "name";
                nameInput.placeholder = `rename ${name.querySelector("h4").innerText}`;

                shipOption.removeChild(name);
                shipOption.prepend(nameInput);
            } else if (option == "save") { // save new name

                fetch(`/api/user/edit/ship/${formData.get("ship")}`, {
                    headers: {"Content-Type": "application/json"},
                    method: "POST",
                    body: JSON.stringify({ name: formData.get("name") })
                }).then(response => {
                    window.location.reload();
                });

            } else if (option == "sell") {

                fetch(`/api/user/sell/ship/${formData.get("ship")}`, {
                    headers: {"Content-Type": "application/json"},
                    method: "POST"
                }).then(response => {
                    window.location.reload();
                })
                
            }
        };
    });

});