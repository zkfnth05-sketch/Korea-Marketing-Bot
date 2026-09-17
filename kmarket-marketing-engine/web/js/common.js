// ==========================================
// [모듈 1] common.js: 공통 상태 관리 및 유틸리티
// ==========================================

let currentBrand = "aura";
let isStockRunning = false;
let isAuraRunning = false;
let isInsuranceRunning = false;
let isKMarketRunning = false;
let isEasyTaxRunning = false;
let logHistory = [];

// 토스트 메시지 표시
function showToast(message, type = "info") {
    const container = document.getElementById("toast-container");
    if (!container) return;
    
    const toast = document.createElement("div");
    toast.className = `toast-message ${type}`;
    toast.style.background = type === "error" ? "#EF4444" : type === "success" ? "#10B981" : "#1E293B";
    toast.style.color = "#FFFFFF";
    toast.style.padding = "10px 16px";
    toast.style.borderRadius = "8px";
    toast.style.marginBottom = "8px";
    toast.style.fontSize = "12.5px";
    toast.style.fontWeight = "700";
    toast.style.boxShadow = "0 4px 14px rgba(0,0,0,0.3)";
    toast.style.animation = "fadeIn 0.3s ease";
    toast.innerText = message;
    
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = "0";
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// 터미널 로그 추가
function appendLog(text, type = "info") {
    const logBox = document.getElementById("terminal-log");
    if (!logBox) return;
    
    const timeStr = new Date().toLocaleTimeString();
    const color = type === "error" ? "#EF4444" : type === "success" ? "#34D399" : type === "warning" ? "#F59E0B" : "#94A3B8";
    
    const line = document.createElement("div");
    line.className = `log-line ${type}`;
    line.style.fontSize = "12px";
    line.style.fontFamily = "monospace";
    line.style.margin = "3px 0";
    line.innerHTML = `<span style="color:#64748b;">[${timeStr}]</span> <span style="color:${color};">${text}</span>`;
    
    logBox.appendChild(line);

    // 최대 100줄 유지 (오래된 로그 자동 정리로 메모리 및 스크롤 최적화)
    while (logBox.children.length > 100) {
        logBox.removeChild(logBox.firstChild);
    }

    logBox.scrollTop = logBox.scrollHeight;
}

// 새로고침 버튼 회전 애니메이션 헬퍼
function animateRefreshBtn(btn, successMsg = "최신 데이터로 새로고침되었습니다! 🔄") {
    if (!btn) return;
    const origHtml = btn.innerHTML;
    btn.innerHTML = `<span class="spin-icon" style="display:inline-block;animation:rotateSpin 0.6s linear infinite;">🔄</span> 갱신 중...`;
    btn.classList.add("btn-spinning");
    setTimeout(() => {
        btn.innerHTML = origHtml;
        btn.classList.remove("btn-spinning");
        if (successMsg) showToast(successMsg);
    }, 600);
}

// 탭 초기화 및 전환
function initTabs() {
    const navItems = document.querySelectorAll(".nav-item");
    const tabContents = document.querySelectorAll(".tab-content");

    navItems.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetTab = btn.getAttribute("data-tab");

            navItems.forEach(i => i.classList.remove("active"));
            tabContents.forEach(c => c.classList.remove("active"));

            btn.classList.add("active");
            const targetContent = document.getElementById(`tab-${targetTab}`);
            if (targetContent) targetContent.classList.add("active");

            if (targetTab === "overview" && typeof renderHubGrid === "function") renderHubGrid();
            if (targetTab === "ir-analytics" && typeof loadIRAnalytics === "function") loadIRAnalytics();
            if (targetTab === "platforms" && typeof loadPlatforms === "function") loadPlatforms();
            if (targetTab === "hashtags" && typeof loadHashtags === "function") loadHashtags();
            if (targetTab === "gallery" && typeof loadGallery === "function") loadGallery();
            if (targetTab === "self-learning" && typeof loadGoldenCopies === "function") loadGoldenCopies();
            if (targetTab === "health" && typeof loadHealthStatus === "function") loadHealthStatus();
        });
    });
}

function switchTabDirect(tabName) {
    const btn = document.querySelector(`.nav-item[data-tab="${tabName}"]`);
    if (btn) btn.click();
}

// 브랜드 스위칭 (stock ↔ aura ↔ insurance)
function switchBrand(brand) {
    currentBrand = brand || "aura";
    const btnStock = document.getElementById("brand-tab-stock");
    const btnAura = document.getElementById("brand-tab-aura");
    const btnIns = document.getElementById("brand-tab-insurance");
    const pageTitle = document.getElementById("page-title");
    const pageDesc = document.getElementById("page-desc");
    const seasonName = document.getElementById("season-name");
    const gCount = document.getElementById("google-index-count");
    const seoCount = document.getElementById("stat-seo-count");

    // 기본 탭 스타일 리셋 (화이트 테마)
    [btnStock, btnAura, btnIns].forEach(btn => {
        if (btn) {
            btn.style.background = "#F1F5F9";
            btn.style.border = "1px solid #CBD5E1";
            btn.style.color = "#475569";
            btn.style.boxShadow = "none";
        }
    });

    if (currentBrand === "stock") {
        if (btnStock) {
            btnStock.style.background = "linear-gradient(135deg, #F59E0B, #D97706)";
            btnStock.style.border = "none";
            btnStock.style.color = "#FFFFFF";
            btnStock.style.boxShadow = "0 4px 14px rgba(245,158,11,0.45)";
        }
        if (pageTitle) pageTitle.innerHTML = "📈 Stock Master 주식 AI 마케팅 통합 제어 센터";
        if (pageDesc) pageDesc.innerText = "당일 외인/기관 수급 분석, 장전 08:30 시황, 조건검색식, 24개 증시 채널을 24시간 자율 가동합니다.";
        if (seasonName) {
            seasonName.innerText = "STOCK MASTER AI";
            seasonName.style.color = "#FACC15";
        }
        if (gCount) gCount.innerText = "24개 채널 연결됨";
        if (seoCount) seoCount.innerText = "24개 채널 (Stock AI)";
    } else if (currentBrand === "aura") {
        if (btnAura) {
            btnAura.style.background = "linear-gradient(135deg, #EC4899, #BE185D)";
            btnAura.style.border = "none";
            btnAura.style.color = "#FFFFFF";
            btnAura.style.boxShadow = "0 4px 14px rgba(236,72,153,0.45)";
        }
        if (pageTitle) pageTitle.innerHTML = "💖 Aura AI 데이팅 마케팅 통합 제어 센터";
        if (pageDesc) pageDesc.innerText = "2030 소개팅 팁, 연애 심리 칼럼, 릴스/숏폼, 24개 소셜 채널을 24시간 자율 가동합니다.";
        if (seasonName) {
            seasonName.innerText = "AURA DATING";
            seasonName.style.color = "#EC4899";
        }
        if (gCount) gCount.innerText = "24개 채널 연결됨";
        if (seoCount) seoCount.innerText = "24개 채널 (Aura)";
    } else if (currentBrand === "insurance") {
        if (btnIns) {
            btnIns.style.background = "linear-gradient(135deg, #10B981, #059669)";
            btnIns.style.border = "none";
            btnIns.style.color = "#FFFFFF";
            btnIns.style.boxShadow = "0 4px 14px rgba(16,185,129,0.45)";
        }
        if (pageTitle) pageTitle.innerHTML = "🛡️ InsureBalance 보험비교 마케팅 통합 제어 센터";
        if (pageDesc) pageDesc.innerText = "실손보험 비교, 3대 질병 절약 가이드, 호갱 탈출 팁, 24개 채널을 24시간 자율 가동합니다.";
        if (seasonName) {
            seasonName.innerText = "INSUREBALANCE";
            seasonName.style.color = "#10B981";
        }
        if (gCount) gCount.innerText = "24개 채널 연결됨";
        if (seoCount) seoCount.innerText = "24개 채널 (InsureBalance)";
    }

    if (typeof fetchStatus === "function") fetchStatus();
    if (typeof renderHubGrid === "function") renderHubGrid();
    if (typeof updateGoldenBatchPanel === "function") updateGoldenBatchPanel();
    if (typeof loadPlatforms === "function") loadPlatforms();
    if (typeof loadHashtags === "function") loadHashtags();
    if (typeof loadGallery === "function") loadGallery();
    if (typeof loadGoldenCopies === "function") loadGoldenCopies();
    if (typeof loadIRAnalytics === "function") loadIRAnalytics();
    if (typeof loadHealthStatus === "function") loadHealthStatus();
    if (typeof loadTelegramCommunityStats === "function") loadTelegramCommunityStats();
}

window.showToast = showToast;
window.appendLog = appendLog;
window.animateRefreshBtn = animateRefreshBtn;
window.initTabs = initTabs;
window.switchTabDirect = switchTabDirect;
window.switchBrand = switchBrand;
