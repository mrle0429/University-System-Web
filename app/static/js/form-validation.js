document.addEventListener('DOMContentLoaded', function() {
    // 获取所有带有错误信息的输入框
    const inputsWithErrors = document.querySelectorAll('.form-control');
    
    inputsWithErrors.forEach(input => {
        // 检查是否存在错误信息
        const errorSpan = input.parentElement.querySelector('.error-message');
        if (errorSpan) {
            // 添加错误样式
            input.classList.add('error');
            // 清空输入值
            input.value = '';
            
            // 添加输入事件监听器
            input.addEventListener('input', function() {
                // 当用户开始输入时移除错误样式
                this.classList.remove('error');
                // 隐藏错误信息
                const errorMessages = this.parentElement.querySelectorAll('.error-message');
                errorMessages.forEach(msg => msg.style.display = 'none');
            });
        }
    });

    // 判断当前页面
    const isRegisterPage = window.location.pathname.includes('register');
    
    // 仅在注册页面添加密码验证
    if (isRegisterPage) {
        const passwordInputs = document.querySelectorAll('input[type="password"]');
        passwordInputs.forEach(input => {
            input.addEventListener('input', function() {
                validatePassword(this);
            });

            input.addEventListener('blur', function() {
                validatePassword(this, true);
            });
        });
    }
});

function validatePassword(input, showError = false) {
    const password = input.value;
    let isValid = true;
    let errorMessage = '';

    // 简化的密码验证规则
    if (password.length < 6) {
        isValid = false;
        errorMessage = 'Password must be at least 6 characters long';
    } else if (password.length > 20) {
        isValid = false;
        errorMessage = 'Password must not exceed 20 characters';
    } else if (!/[a-zA-Z]/.test(password)) {
        isValid = false;
        errorMessage = 'Password must contain at least one letter';
    } else if (!/[0-9]/.test(password)) {
        isValid = false;
        errorMessage = 'Password must contain at least one number';
    }

    // 获取或创建错误消息元素
    let errorSpan = input.parentElement.querySelector('.error-message');
    if (!errorSpan && !isValid) {
        errorSpan = document.createElement('span');
        errorSpan.className = 'error-message';
        input.parentElement.appendChild(errorSpan);
    }

    // 更新输入框样式和错误消息
    if (!isValid && showError) {
        input.classList.add('error');
        if (errorSpan) {
            errorSpan.textContent = errorMessage;
            errorSpan.style.display = 'block';
        }
    } else {
        input.classList.remove('error');
        if (errorSpan) {
            errorSpan.style.display = 'none';
        }
    }

    return isValid;
}

// 表单提交验证
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function(event) {
        // 仅在注册页面进行密码验证
        if (window.location.pathname.includes('register')) {
            const passwordInput = this.querySelector('input[type="password"]');
            if (passwordInput && !validatePassword(passwordInput, true)) {
                event.preventDefault();
            }
        }
    });
});