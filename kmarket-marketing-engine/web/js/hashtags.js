// ==========================================
// [모듈 8] hashtags.js: 17개국 바이럴 해시태그 전담 모듈
// ==========================================

async function loadHashtags(btn) {
    if (btn) animateRefreshBtn(btn, "17개국 바이럴 해시태그가 새로고침되었습니다! 📈");
    const grid = document.getElementById("hashtags-grid");
    if (!grid) return;

    try {
        const res = await fetch("/api/hashtags");
        const data = await res.json();
        const hashtags = data.hashtags || {};

        grid.innerHTML = Object.entries(hashtags).map(([countryCode, countryData]) => {
            const tags = countryData.tags || [];
            const isKM = currentBrand === "kmarket";
            const badgeColor = isKM ? "#10B981" : "#F59E0B";

            return `
                <div class="hashtag-card" style="background:#F6F1EA;border:1px solid #E5DDD1;border-top:3px solid ${badgeColor};border-radius:14px;padding:16px;box-shadow:var(--shadow-md);transition:transform 0.25s ease, box-shadow 0.25s ease;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                        <div style="display:flex;align-items:center;gap:8px;">
                            <span style="font-size:20px;">${countryData.flag || '🌐'}</span>
                            <h4 style="margin:0;font-size:14px;font-weight:700;color:#1E1B18;">${countryData.country_name} (${countryCode})</h4>
                        </div>
                        <span style="font-size:11px;color:#0284C7;font-weight:700;">실시간 트렌드</span>
                    </div>
                    <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:8px;">
                        ${tags.map(t => `
                            <span style="background:#FFFFFF;color:#334155;padding:4px 8px;border-radius:6px;font-size:11.5px;border:1px solid #E5DDD1;">
                                #${t}
                            </span>
                        `).join("")}
                    </div>
                </div>
            `;
        }).join("");
    } catch (e) {
        console.error("Hashtags load error:", e);
    }
}

async function refreshHashtags() {
    try {
        const res = await fetch("/api/hashtags/refresh", { method: "POST" });
        const data = await res.json();
        showToast(data.message || "해시태그 트렌드가 갱신되었습니다!", "success");
        loadHashtags();
    } catch (e) {
        showToast("해시태그 갱신 실패", "error");
    }
}

window.loadHashtags = loadHashtags;
window.refreshHashtags = refreshHashtags;
