/**
 * AviRec 客户端 JS
 * 处理拍摄标记切换、照片上传、筛选等交互
 */

async function toggleSpotted(aircraftId, btn) {
    const card = btn.closest('.aircraft-card');
    const isCurrentlySpotted = card.dataset.spotted === 'true';

    try {
        const resp = await fetch(`/api/toggle-spotted/${aircraftId}`, { method: 'POST' });
        const data = await resp.json();

        if (data.spotted) {
            card.classList.remove('unspotted');
            card.classList.add('spotted');
            card.dataset.spotted = 'true';
            btn.classList.add('active');
            btn.textContent = '✓ 已拍摄';
            const badge = card.querySelector('.spotted-badge');
            if (badge) badge.textContent = '📷';
            if (data.photo_id) {
                showUploadPrompt(data.photo_id, card);
            }
        } else {
            card.classList.remove('spotted');
            card.classList.add('unspotted');
            card.dataset.spotted = 'false';
            btn.classList.remove('active');
            btn.textContent = '标记已拍';
            const badge = card.querySelector('.spotted-badge');
            if (badge) badge.textContent = '🛇';
        }
    } catch (err) {
        console.error('切换失败:', err);
    }
}

async function markSpotted(aircraftId) {
    try {
        const resp = await fetch(`/api/toggle-spotted/${aircraftId}`, { method: 'POST' });
        const data = await resp.json();
        if (data.spotted) location.reload();
    } catch (err) {
        console.error('标记失败:', err);
    }
}

function showUploadPrompt(photoId, card) {
    const existing = card.querySelector('.upload-area');
    if (existing) return;
    const div = document.createElement('div');
    div.className = 'upload-area';
    div.innerHTML = `
        <input type="file" accept="image/jpeg,image/png,image/webp"
               onchange="uploadPhoto(${photoId}, this)" style="display:none" id="upload-${photoId}">
        <label for="upload-${photoId}" class="upload-label">📸 上传拍摄照片</label>
    `;
    const toggleBtn = card.querySelector('.toggle-btn');
    if (toggleBtn) toggleBtn.after(div);
}

async function uploadPhoto(photoId, input) {
    const file = input.files[0];
    if (!file) return;
    if (file.size > 10 * 1024 * 1024) {
        alert('图片大小不能超过 10MB');
        return;
    }
    const formData = new FormData();
    formData.append('file', file);
    try {
        const resp = await fetch(`/api/upload-photo/${photoId}`, { method: 'POST', body: formData });
        const data = await resp.json();
        if (data.status === 'ok') {
            const card = input.closest('.aircraft-card');
            if (card) {
                const cardImg = card.querySelector('.card-image img');
                if (cardImg) {
                    cardImg.src = data.image_url;
                    cardImg.style.filter = 'none';
                    cardImg.style.opacity = '1';
                }
                const uploadArea = card.querySelector('.upload-area');
                if (uploadArea) uploadArea.remove();
            }
        }
    } catch (err) {
        console.error('上传失败:', err);
    }
}

async function editPhoto(photoId) {
    const card = document.getElementById('photo-edit-card');
    if (card) {
        card.style.display = 'block';
        document.getElementById('edit-photo-id').value = photoId;
        card.scrollIntoView({ behavior: 'smooth' });
    }
}

async function savePhotoEdit(event) {
    event.preventDefault();
    const photoId = document.getElementById('edit-photo-id').value;
    const formData = new FormData();
    formData.append('taken_date', document.getElementById('edit-taken-date').value);
    formData.append('taken_location', document.getElementById('edit-taken-location').value);
    formData.append('notes', document.getElementById('edit-notes').value);
    try {
        const resp = await fetch(`/api/update-photo/${photoId}`, { method: 'POST', body: formData });
        const data = await resp.json();
        if (data.status === 'ok') location.reload();
    } catch (err) {
        console.error('保存失败:', err);
    }
    return false;
}

// ── 筛选逻辑 ──

document.addEventListener('DOMContentLoaded', () => {
    // 航司列表搜索
    const searchInput = document.getElementById('search-airline');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const term = this.value.toLowerCase();
            document.querySelectorAll('.airline-row').forEach(row => {
                const name = row.querySelector('.airline-row-name').textContent.toLowerCase();
                const code = row.querySelector('.airline-row-code').textContent.toLowerCase();
                row.style.display = (name.includes(term) || code.includes(term)) ? '' : 'none';
            });
        });
    }

    // 机队页筛选：注册号实时过滤
    const fleetSearch = document.getElementById('fleet-search');
    if (fleetSearch) {
        fleetSearch.addEventListener('input', function() {
            const term = this.value.toLowerCase();
            document.querySelectorAll('.aircraft-card').forEach(card => {
                const reg = (card.dataset.registration || '').toLowerCase();
                card.style.display = reg.includes(term) ? '' : 'none';
            });
            updateSectionVisibility();
        });
    }

    // 机队页下拉筛选：提交表单
    const fleetFilters = document.querySelectorAll('.fleet-filter');
    fleetFilters.forEach(filter => {
        filter.addEventListener('change', () => {
            filter.closest('form').submit();
        });
    });

    // 折叠/展开 分组 section
    document.querySelectorAll('.category-header').forEach(header => {
        header.addEventListener('click', function() {
            const section = this.closest('.category-section');
            section.classList.toggle('collapsed');
        });
    });
});

function updateSectionVisibility() {
    document.querySelectorAll('.category-section').forEach(section => {
        const visibleCards = section.querySelectorAll('.aircraft-card[style*="display:"]');
        const allCards = section.querySelectorAll('.aircraft-card');
        const hiddenCount = section.querySelectorAll('.aircraft-card[style*="display: none"]').length;
        if (hiddenCount === allCards.length) {
            section.style.display = 'none';
        } else {
            section.style.display = '';
        }
    });
}
