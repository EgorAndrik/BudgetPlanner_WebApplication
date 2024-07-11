document.getElementById('login-form').addEventListener('submit', async function(event) {
    event.preventDefault(); // Prevent the default form submission

    const form = event.target;
    const formData = new FormData(form);

    const response = await fetch('/LogInPage/LogIn', {
        method: 'POST',
        body: formData
    });

    const result = await response.json();

    if (result.success) {
        window.location.href = `/userPage/${result.userName}`;
    } else {
        document.getElementById('error-message').innerText = result.message;
    }
});
