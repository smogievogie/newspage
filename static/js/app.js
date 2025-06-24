// AI新闻收集器前端JavaScript

// 全局变量
let currentPage = 1;
let isLoading = false;
let hasMoreNews = true;

// DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// 初始化应用
function initializeApp() {
    loadNews();
    loadStats();
    loadKeywords();
    loadSources();
    setupEventListeners();
    setupAutoRefresh();
}

// 设置事件监听器
function setupEventListeners() {
    // 搜索功能
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(handleSearch, 500));
    }
    
    // 排序和过滤
    const sortSelect = document.getElementById('sortBy');
    if (sortSelect) {
        sortSelect.addEventListener('change', loadNews);
    }
    
    const sourceFilter = document.getElementById('sourceFilter');
    if (sourceFilter) {
        sourceFilter.addEventListener('change', loadNews);
    }
    
    const keywordFilter = document.getElementById('keywordFilter');
    if (keywordFilter) {
        keywordFilter.addEventListener('change', loadNews);
    }
    
    // 无限滚动
    window.addEventListener('scroll', handleScroll);
    
    // 手动收集新闻
    const collectBtn = document.getElementById('collectNewsBtn');
    if (collectBtn) {
        collectBtn.addEventListener('click', collectNews);
    }
    
    // 刷新按钮
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshData);
    }
}

// 加载新闻列表
async function loadNews(reset = true) {
    if (isLoading) return;
    
    if (reset) {
        currentPage = 1;
        hasMoreNews = true;
        const newsContainer = document.getElementById('newsContainer');
        if (newsContainer) {
            newsContainer.innerHTML = '';
        }
    }
    
    if (!hasMoreNews) return;
    
    isLoading = true;
    showLoading();
    
    try {
        const params = new URLSearchParams({
            page: currentPage,
            per_page: 10,
            sort_by: document.getElementById('sortBy')?.value || 'published_at',
            source: document.getElementById('sourceFilter')?.value || '',
            keyword: document.getElementById('keywordFilter')?.value || '',
            search: document.getElementById('searchInput')?.value || ''
        });
        
        const response = await fetch(`/api/news?${params}`);
        const data = await response.json();
        
        if (data.success) {
            displayNews(data.news, reset);
            hasMoreNews = data.news.length === 10;
            currentPage++;
        } else {
            showError('加载新闻失败: ' + data.error);
        }
    } catch (error) {
        console.error('Error loading news:', error);
        showError('网络错误，请稍后重试');
    } finally {
        isLoading = false;
        hideLoading();
    }
}

// 显示新闻列表
function displayNews(news, reset = false) {
    const newsContainer = document.getElementById('newsContainer');
    if (!newsContainer) return;
    
    if (reset) {
        newsContainer.innerHTML = '';
    }
    
    news.forEach(article => {
        const newsCard = createNewsCard(article);
        newsContainer.appendChild(newsCard);
    });
    
    // 添加淡入动画
    const newCards = newsContainer.querySelectorAll('.news-card:not(.fade-in)');
    newCards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('fade-in');
        }, index * 100);
    });
}

// 创建新闻卡片
function createNewsCard(article) {
    const card = document.createElement('div');
    card.className = 'news-card card';
    
    const publishedDate = new Date(article.published_at).toLocaleString('zh-CN');
    const relevanceColor = getRelevanceColor(article.relevance_score);
    
    card.innerHTML = `
        <div class="card-body">
            <h5 class="news-title">
                <a href="${article.url}" target="_blank" rel="noopener noreferrer">
                    ${escapeHtml(article.title)}
                </a>
            </h5>
            <p class="news-summary">${escapeHtml(article.summary || '暂无摘要')}</p>
            <div class="d-flex justify-content-between align-items-center news-meta">
                <div>
                    <span class="news-source">${escapeHtml(article.source)}</span>
                    <span class="relevance-score" style="background: ${relevanceColor}">
                        相关性: ${(article.relevance_score * 100).toFixed(0)}%
                    </span>
                    ${article.is_read ? '<span class="badge bg-secondary ms-2">已读</span>' : ''}
                </div>
                <div>
                    <small class="text-muted">${publishedDate}</small>
                    ${!article.is_read ? `<button class="btn btn-sm btn-outline-primary ms-2" onclick="markAsRead(${article.id})">标记已读</button>` : ''}
                </div>
            </div>
            ${article.keywords ? `
                <div class="mt-2">
                    ${article.keywords.split(',').map(keyword => 
                        `<span class="keyword-tag" onclick="filterByKeyword('${keyword.trim()}')">${escapeHtml(keyword.trim())}</span>`
                    ).join('')}
                </div>
            ` : ''}
        </div>
    `;
    
    return card;
}

// 获取相关性颜色
function getRelevanceColor(score) {
    if (score >= 0.8) return 'linear-gradient(45deg, #28a745, #20c997)';
    if (score >= 0.6) return 'linear-gradient(45deg, #ffc107, #fd7e14)';
    return 'linear-gradient(45deg, #6c757d, #495057)';
}

// 标记文章为已读
async function markAsRead(articleId) {
    try {
        const response = await fetch(`/api/news/${articleId}/read`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        if (data.success) {
            // 刷新新闻列表
            loadNews();
            loadStats();
            showSuccess('文章已标记为已读');
        } else {
            showError('标记失败: ' + data.error);
        }
    } catch (error) {
        console.error('Error marking as read:', error);
        showError('网络错误，请稍后重试');
    }
}

// 按关键词过滤
function filterByKeyword(keyword) {
    const keywordFilter = document.getElementById('keywordFilter');
    if (keywordFilter) {
        keywordFilter.value = keyword;
        loadNews();
    }
}

// 搜索处理
function handleSearch() {
    loadNews();
}

// 滚动处理（无限滚动）
function handleScroll() {
    if (isLoading || !hasMoreNews) return;
    
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;
    
    if (scrollTop + windowHeight >= documentHeight - 1000) {
        loadNews(false);
    }
}

// 收集新闻
async function collectNews() {
    const collectBtn = document.getElementById('collectNewsBtn');
    if (!collectBtn) return;
    
    const originalText = collectBtn.innerHTML;
    collectBtn.innerHTML = '<span class="loading-spinner"></span> 收集中...';
    collectBtn.disabled = true;
    
    try {
        const response = await fetch('/api/collect', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        if (data.success) {
            showSuccess(`成功收集 ${data.count} 篇新文章`);
            loadNews();
            loadStats();
            loadKeywords();
            loadSources();
        } else {
            showError('收集失败: ' + data.error);
        }
    } catch (error) {
        console.error('Error collecting news:', error);
        showError('网络错误，请稍后重试');
    } finally {
        collectBtn.innerHTML = originalText;
        collectBtn.disabled = false;
    }
}

// 加载统计信息
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        if (data.success) {
            updateStatsDisplay(data.stats);
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// 更新统计信息显示
function updateStatsDisplay(stats) {
    const elements = {
        'totalArticles': stats.total_articles,
        'unreadArticles': stats.unread_articles,
        'totalSources': stats.total_sources,
        'lastUpdate': stats.last_update ? new Date(stats.last_update).toLocaleString('zh-CN') : '从未更新'
    };
    
    Object.entries(elements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    });
}

// 加载热门关键词
async function loadKeywords() {
    try {
        const response = await fetch('/api/keywords');
        const data = await response.json();
        
        if (data.success) {
            updateKeywordsDisplay(data.keywords);
        }
    } catch (error) {
        console.error('Error loading keywords:', error);
    }
}

// 更新关键词显示
function updateKeywordsDisplay(keywords) {
    const keywordsList = document.getElementById('keywordsList');
    const keywordFilter = document.getElementById('keywordFilter');
    
    if (keywordsList) {
        keywordsList.innerHTML = keywords.map(keyword => 
            `<span class="keyword-tag" onclick="filterByKeyword('${keyword.keyword}')">
                ${escapeHtml(keyword.keyword)} (${keyword.count})
            </span>`
        ).join('');
    }
    
    if (keywordFilter) {
        const currentValue = keywordFilter.value;
        keywordFilter.innerHTML = '<option value="">所有关键词</option>' + 
            keywords.map(keyword => 
                `<option value="${escapeHtml(keyword.keyword)}">${escapeHtml(keyword.keyword)} (${keyword.count})</option>`
            ).join('');
        keywordFilter.value = currentValue;
    }
}

// 加载新闻源
async function loadSources() {
    try {
        const response = await fetch('/api/sources');
        const data = await response.json();
        
        if (data.success) {
            updateSourcesDisplay(data.sources);
        }
    } catch (error) {
        console.error('Error loading sources:', error);
    }
}

// 更新新闻源显示
function updateSourcesDisplay(sources) {
    const sourcesList = document.getElementById('sourcesList');
    const sourceFilter = document.getElementById('sourceFilter');
    
    if (sourcesList) {
        sourcesList.innerHTML = sources.map(source => 
            `<div class="d-flex justify-content-between align-items-center mb-2">
                <span>${escapeHtml(source.name)}</span>
                <span class="badge bg-primary">${source.count}</span>
            </div>`
        ).join('');
    }
    
    if (sourceFilter) {
        const currentValue = sourceFilter.value;
        sourceFilter.innerHTML = '<option value="">所有来源</option>' + 
            sources.map(source => 
                `<option value="${escapeHtml(source.name)}">${escapeHtml(source.name)} (${source.count})</option>`
            ).join('');
        sourceFilter.value = currentValue;
    }
}

// 刷新所有数据
function refreshData() {
    loadNews();
    loadStats();
    loadKeywords();
    loadSources();
    showSuccess('数据已刷新');
}

// 设置自动刷新
function setupAutoRefresh() {
    // 每5分钟自动刷新统计信息
    setInterval(() => {
        loadStats();
        loadKeywords();
        loadSources();
    }, 5 * 60 * 1000);
}

// 工具函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

function showLoading() {
    const loadingElement = document.getElementById('loadingIndicator');
    if (loadingElement) {
        loadingElement.style.display = 'block';
    }
}

function hideLoading() {
    const loadingElement = document.getElementById('loadingIndicator');
    if (loadingElement) {
        loadingElement.style.display = 'none';
    }
}

function showSuccess(message) {
    showToast(message, 'success');
}

function showError(message) {
    showToast(message, 'error');
}

function showToast(message, type = 'info') {
    // 创建toast元素
    const toast = document.createElement('div');
    toast.className = `alert alert-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info'} alert-dismissible fade show position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(toast);
    
    // 3秒后自动移除
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 3000);
}

// 导出函数供全局使用
window.loadNews = loadNews;
window.markAsRead = markAsRead;
window.filterByKeyword = filterByKeyword;
window.collectNews = collectNews;
window.refreshData = refreshData;