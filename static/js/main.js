// ============== 通用弹窗组件 ==============

/**
 * Toast 轻提示（自动消失）
 * @param {string} message - 提示内容
 * @param {string} type - 'success' | 'error' | 'info' | 'warning'
 * @param {number} duration - 持续毫秒，默认2500
 */
function showToast(message, type = 'info', duration = 2500) {
    // 移除旧的toast
    const oldToast = document.getElementById('global-toast');
    if (oldToast) oldToast.remove();

    const colors = {
        success: 'bg-green-500',
        error: 'bg-red-500',
        info: 'bg-blue-500',
        warning: 'bg-yellow-500',
    };
    const icons = {
        success: '✓',
        error: '✕',
        info: 'ℹ',
        warning: '⚠',
    };

    const toast = document.createElement('div');
    toast.id = 'global-toast';
    toast.className = `fixed top-6 left-1/2 transform -translate-x-1/2 z-50 px-5 py-3 rounded-lg shadow-lg text-white ${colors[type]} flex items-center space-x-2 transition-all duration-300 opacity-0`;
    toast.innerHTML = `<span class="text-lg">${icons[type]}</span><span>${message}</span>`;
    document.body.appendChild(toast);

    // 触发动画
    requestAnimationFrame(() => {
        toast.classList.remove('opacity-0');
        toast.classList.add('opacity-100');
    });

    // 自动消失
    setTimeout(() => {
        toast.classList.remove('opacity-100');
        toast.classList.add('opacity-0');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

/**
 * Modal 模态对话框（替代confirm/alert）
 * @param {object} options
 *   - title: 标题
 *   - content: 内容（支持HTML）
 *   - confirmText: 确认按钮文字，默认"确定"
 *   - cancelText: 取消按钮文字，默认"取消"，传null则只有确定按钮
 *   - confirmClass: 确认按钮额外class（如 'bg-red-600'）
 *   - onConfirm: 确认回调
 *   - onCancel: 取消回调
 */
function showModal(options) {
    const {
        title = '提示',
        content = '',
        confirmText = '确定',
        cancelText = '取消',
        confirmClass = 'bg-blue-600 hover:bg-blue-700',
        onConfirm = null,
        onCancel = null,
    } = options;

    // 移除旧的modal
    const oldModal = document.getElementById('global-modal');
    if (oldModal) oldModal.remove();

    const modal = document.createElement('div');
    modal.id = 'global-modal';
    modal.className = 'fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 transition-opacity duration-200 opacity-0';

    modal.innerHTML = `
        <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 transform scale-95 transition-transform duration-200">
            <div class="px-6 py-4 border-b">
                <h3 class="text-lg font-bold text-gray-800">${title}</h3>
            </div>
            <div class="px-6 py-4 text-gray-700">${content}</div>
            <div class="px-6 py-3 border-t bg-gray-50 flex justify-end space-x-2 rounded-b-lg">
                ${cancelText ? `<button id="modal-cancel" class="px-4 py-2 text-gray-700 bg-white border rounded hover:bg-gray-100">${cancelText}</button>` : ''}
                <button id="modal-confirm" class="px-4 py-2 text-white rounded ${confirmClass}">${confirmText}</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);

    // 触发动画
    requestAnimationFrame(() => {
        modal.classList.remove('opacity-0');
        modal.classList.add('opacity-100');
        modal.querySelector('.transform').classList.remove('scale-95');
        modal.querySelector('.transform').classList.add('scale-100');
    });

    const close = () => {
        modal.classList.add('opacity-0');
        setTimeout(() => modal.remove(), 200);
    };

    document.getElementById('modal-confirm').addEventListener('click', () => {
        close();
        if (onConfirm) onConfirm();
    });

    const cancelBtn = document.getElementById('modal-cancel');
    if (cancelBtn) {
        cancelBtn.addEventListener('click', () => {
            close();
            if (onCancel) onCancel();
        });
    }

    // 点击遮罩关闭
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            close();
            if (onCancel) onCancel();
        }
    });
}

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