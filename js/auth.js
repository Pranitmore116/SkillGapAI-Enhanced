/**
 * auth.js
 * Client-side session management and validation.
 */

'use strict';

const $ = id => document.getElementById(id);

let isLogin = true;

/* ── DOM Elements ── */
const authForm = $('authForm');
const formTitle = $('formTitle');
const submitBtn = $('submitBtn');
const toggleBtn = $('toggleBtn');
const toggleText = $('toggleText');
const confirmGroup = $('confirmGroup');
const emailInput = $('email');
const passwordInput = $('password');
const confirmInput = $('confirmPassword');
const toast = $('toast');
const toastMsg = $('toastMsg');

/* ── Initialization ── */
document.addEventListener('DOMContentLoaded', () => {
    // Check if already logged in
    if (localStorage.getItem('user_session')) {
        window.location.href = 'index.html';
    }

    // Demo Login Bypass
    if ($('demo-login-btn')) {
        $('demo-login-btn').addEventListener('click', () => {
            emailInput.value = 'intern@skillgap.ai';
            passwordInput.value = 'presentation2026';
            processAuth();
        });
    }
});

/* ── View Toggle Logic ── */
toggleBtn.addEventListener('click', () => {
    isLogin = !isLogin;

    // Update Text
    formTitle.textContent = isLogin ? 'Login' : 'Create Account';
    submitBtn.textContent = isLogin ? 'Login' : 'Sign Up';
    toggleText.textContent = isLogin ? "Don't have an account?" : "Already have an account?";
    toggleBtn.textContent = isLogin ? 'Sign Up' : 'Login';

    // Toggle Visibility with Animation
    if (isLogin) {
        confirmGroup.style.display = 'none';
        confirmInput.removeAttribute('required');
    } else {
        confirmGroup.style.display = 'block';
        confirmInput.setAttribute('required', 'true');
    }

    // Clear validation
    clearValidation();
});

/* ── Form Logic ── */
authForm.addEventListener('submit', (e) => {
    e.preventDefault();
    if (validate()) {
        processAuth();
    }
});

function validate() {
    let isValid = true;
    clearValidation();

    // Email
    if (!emailInput.value.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
        emailInput.classList.add('invalid');
        isValid = false;
    }

    // Password
    if (passwordInput.value.length < 6) {
        passwordInput.classList.add('invalid');
        isValid = false;
    }

    // Confirm Password (Signup only)
    if (!isLogin && passwordInput.value !== confirmInput.value) {
        confirmInput.classList.add('invalid');
        isValid = false;
    }

    return isValid;
}

function clearValidation() {
    [emailInput, passwordInput, confirmInput].forEach(el => el.classList.remove('invalid'));
}

async function processAuth() {
    const email = emailInput.value;

    setLoading(true);

    // Simulate Network Delay
    await new Promise(r => setTimeout(r, 1200));

    // For a real app, this would be a fetch call to a backend.
    // Since we have no backend, we'll simulate a successful response.

    const session = {
        email,
        token: 'sk_' + Math.random().toString(36).substr(2, 16),
        loginAt: new Date().toISOString()
    };

    localStorage.setItem('user_session', JSON.stringify(session));

    showToast(isLogin ? "Welcome back!" : "Account created successfully.", "success");

    setTimeout(() => {
        window.location.href = 'dashboard.html';
    }, 1000);
}

/* ── UI Helpers ── */
function setLoading(loading) {
    submitBtn.disabled = loading;
    submitBtn.textContent = loading ? 'Processing...' : (isLogin ? 'Login' : 'Sign Up');
}

function showToast(msg, type) {
    toast.style.display = 'flex';
    toast.className = `toast ${type}`;
    toastMsg.textContent = msg;

    setTimeout(() => {
        toast.style.display = 'none';
    }, 3000);
}
