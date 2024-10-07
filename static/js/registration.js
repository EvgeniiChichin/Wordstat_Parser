document.addEventListener('DOMContentLoaded', function() {
    var passwordInput = document.getElementById('id_new_password1') || document.getElementById('id_password1');
    var passwordInfo = document.getElementById('password-info');

    if (passwordInput && passwordInfo) {
        passwordInput.addEventListener('focus', function() {
            passwordInfo.style.display = 'block';
        });

        passwordInput.addEventListener('blur', function() {
            passwordInfo.style.display = 'none';
        });
    }
});