// ============== 通用工具函数 ==============

/**
 * 获取CSRF Token
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * 封装的 fetch 请求
 */
async function apiRequest(url, options = {}) {
    const defaultHeaders = {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
    };

    const config = {
        credentials: 'include',  // 携带cookie
        ...options,
        headers: {
            ...defaultHeaders,
            ...(options.headers || {}),
        },
    };

    try {
        const response = await fetch(url, config);
        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            throw { status: response.status, data };
        }
        return data;
    } catch (error) {
        console.error('API请求失败:', error);
        throw error;
    }
}

// ============== 登录状态管理 ==============

async function checkLoginStatus() {
    try {
        const user = await apiRequest('/api/user/me/');
        showLoggedInUI(user);
        return user;
    } catch (error) {
        showGuestUI();
        return null;
    }
}

function showLoggedInUI(user) {
    const guestButtons = document.getElementById('guest-buttons');
    const userInfo = document.getElementById('user-info');
    const usernameDisplay = document.getElementById('username-display');

    if (guestButtons) guestButtons.classList.add('hidden');
    if (userInfo) {
        userInfo.classList.remove('hidden');
        userInfo.classList.add('flex');
    }
    if (usernameDisplay) usernameDisplay.textContent = user.username;
}

function showGuestUI() {
    const guestButtons = document.getElementById('guest-buttons');
    const userInfo = document.getElementById('user-info');

    if (guestButtons) guestButtons.classList.remove('hidden');
    if (userInfo) {
        userInfo.classList.add('hidden');
        userInfo.classList.remove('flex');
    }
}

async function handleLogout() {
    try {
        await apiRequest('/api/user/logout/', { method: 'POST' });
        window.location.reload();
    } catch (error) {
        alert('登出失败');
    }
}

// ============== 通用工具 ==============

/**
 * 获取院校层次标签
 */
function getSchoolTags(school) {
    let tags = '';
    if (school.is_985) tags += '<span class="tag-985 px-2 py-0.5 text-xs rounded mr-1">985</span>';
    if (school.is_211) tags += '<span class="tag-211 px-2 py-0.5 text-xs rounded mr-1">211</span>';
    if (school.is_double_first) tags += '<span class="tag-double px-2 py-0.5 text-xs rounded mr-1">双一流</span>';
    return tags;
}

/**
 * URL 参数解析
 */
function getUrlParam(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
}

// ============== 页面初始化 ==============

document.addEventListener('DOMContentLoaded', function() {
    // 检查登录状态
    checkLoginStatus();

    // 绑定登出按钮
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) logoutBtn.addEventListener('click', handleLogout);
});