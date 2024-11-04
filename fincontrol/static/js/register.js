const usernameField = document.querySelector('#usernameField');
const feedBackArea = document.querySelector('.invalid-feedback');
const emailField = document.querySelector('#emailField');
const emailFeedBackArea = document.querySelector('.emailFeedBackArea');
const passwordField = document.querySelector('#passwordField');
const usernameSuccessOutput = document.querySelector('.usernameSuccessOutput');
const showPasswordToggle = document.querySelector('.showPasswordToggle');
const submitBtn = document.querySelector('.submit-btn');

const handleToggleInput = (e) => {
    if (showPasswordToggle.textContent === 'Показати пароль') {
        showPasswordToggle.textContent = 'Приховати пароль';
        passwordField.setAttribute('type', 'text');
    } else {
        showPasswordToggle.textContent = 'Показати пароль';
        passwordField.setAttribute('type', 'password');
    }
}

showPasswordToggle.addEventListener('click', handleToggleInput);

emailField.addEventListener('keyup', (e) => {
    const emailVal = e.target.value;

    emailField.classList.remove('is-invalid');
    emailFeedBackArea.style.display = 'none';

    if (emailVal.length > 0) {
        fetch('/authentication/validate-email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email: emailVal }),
        }).then((res) => res.json()).then(data => {
            console.log('data', data);
            if (data.email_error) {
                submitBtn.disabled = true;
                emailField.classList.add('is-invalid');
                emailFeedBackArea.style.display = 'block';
                emailFeedBackArea.innerHTML = `<p>${data.email_error}</p>`;
            } else {
                submitBtn.removeAttribute('disabled');
            }
        });
    }
});


usernameField.addEventListener('keyup', (e) => {

    const usernameVal = e.target.value;

    usernameSuccessOutput.style.display = 'block';

    usernameSuccessOutput.textContent = `Перевірка ${usernameVal}`;

    usernameField.classList.remove('is-invalid');
    feedBackArea.style.display = 'none';

    if (usernameVal.length > 0) {
        fetch('/authentication/validate-username', {
            body: JSON.stringify({ username: usernameVal }),
            method: 'POST',
        }).then((res) => res.json()).then(data => {
            usernameSuccessOutput.style.display = 'none';
            if (data.username_error) {
                usernameField.classList.add('is-invalid');
                feedBackArea.style.display = 'block';
                feedBackArea.innerHTML = `<p>${data.username_error}</p>`;
                submitBtn.disabled = true;
            } else {
                submitBtn.removeAttribute('disabled');
            }
        });
    }
});
