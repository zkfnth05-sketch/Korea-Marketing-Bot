// ==========================================
// [모듈 8] hashtags.js: 실시간 바이럴 키워드 & 해시태그 전담 모듈
// ==========================================

async function loadHashtags(btn) {
    const brand = typeof currentBrand !== "undefined" ? currentBrand : "kmarket";
    if (btn) animateRefreshBtn(btn, brand === "aura" ? "Aura 2030 실시간 네이버/구글 키워드가 새로고침되었습니다! 💖" : "실시간 바이럴 해시태그가 새로고침되었습니다! 📈");
    const grid = document.getElementById("hashtags-grid");
    if (!grid) return;

    try {
        const res = await fetch(`/api/hashtags?brand=${encodeURIComponent(brand)}`);
        const data = await res.json();
        
        // Aura 2030 전용 렌더링
        if (brand === "aura" && data.brand === "aura" && data.hashtags && data.hashtags.categories) {
            const categories = data.hashtags.categories;
            grid.innerHTML = Object.entries(categories).map(([catKey, catData]) => {
                const naverKeys = catData.naver_top_keywords || [];
                const googleKeys = catData.google_top_keywords || [];
                const hashtags = catData.viral_hashtags || [];

                return `
                    <div class="hashtag-card" style="background:#FFFFFF;border:1px solid #E5DDD1;border-top:3px solid #EC4899;border-radius:14px;padding:18px;box-shadow:var(--shadow-md);transition:transform 0.25s ease;">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                            <div style="display:flex;align-items:center;gap:8px;">
                                <span style="font-size:22px;">${catData.icon || '💖'}</span>
                                <div>
                                    <h4 style="margin:0;font-size:14.5px;font-weight:700;color:#1E1B18;">${catData.name}</h4>
                                    <span style="font-size:11px;color:#64748B;">${catData.aura_feature || ''}</span>
                                </div>
                            </div>
                            <span style="font-size:11px;background:#FDF2F8;color:#DB2777;padding:3px 8px;border-radius:6px;font-weight:700;border:1px solid #FCE7F3;">
                                2030 실시간
                            </span>
                        </div>
                        <p style="font-size:11.5px;color:#475569;margin:6px 0 10px 0;line-height:1.4;">${catData.description}</p>
                        
                        <!-- 네이버 실시간 키워드 -->
                        <div style="margin-bottom:8px;">
                            <span style="font-size:10.5px;font-weight:700;color:#059669;display:block;margin-bottom:4px;">🔍 네이버 실시간 검색어</span>
                            <div style="display:flex;flex-wrap:wrap;gap:4px;">
                                ${naverKeys.length ? naverKeys.map(k => `
                                    <span style="background:#ECFDF5;color:#065F46;padding:3px 7px;border-radius:5px;font-size:11px;border:1px solid #A7F3D0;font-weight:600;">
                                        ${k}
                                    </span>
                                `).join("") : '<span style="font-size:11px;color:#94A3B8;">수집 대기 중</span>'}
                            </div>
                        </div>

                        <!-- 구글 실시간 질문형 키워드 -->
                        <div style="margin-bottom:8px;">
                            <span style="font-size:10.5px;font-weight:700;color:#2563EB;display:block;margin-bottom:4px;">🌐 구글 SEO 추천 검색어</span>
                            <div style="display:flex;flex-wrap:wrap;gap:4px;">
                                ${googleKeys.length ? googleKeys.map(k => `
                                    <span style="background:#EFF6FF;color:#1E40AF;padding:3px 7px;border-radius:5px;font-size:11px;border:1px solid #BFDBFE;font-weight:600;">
                                        ${k}
                                    </span>
                                `).join("") : '<span style="font-size:11px;color:#94A3B8;">수집 대기 중</span>'}
                            </div>
                        </div>

                        <!-- 바이럴 해시태그 -->
                        <div style="margin-top:10px;padding-top:8px;border-top:1px dashed #E2E8F0;">
                            <span style="font-size:10.5px;font-weight:700;color:#DB2777;display:block;margin-bottom:4px;">#️⃣ 4대 플랫폼 바이럴 태그</span>
                            <div style="display:flex;flex-wrap:wrap;gap:4px;">
                                ${hashtags.map(t => `
                                    <span style="background:#F6F1EA;color:#475569;padding:2px 6px;border-radius:4px;font-size:10.5px;border:1px solid #E5DDD1;">
                                        ${t}
                                    </span>
                                `).join("")}
                            </div>
                        </div>
                    </div>
                `;
            }).join("");
            return;
        }

        // 기존 17개국 매트릭스 렌더링 (K-Market / EasyTax 등)
        const hashtags = data.hashtags?.countries || data.hashtags || {};
        grid.innerHTML = Object.entries(hashtags).map(([countryCode, countryData]) => {
            const tags = countryData.tags || countryData.in_korea_common || [];
            const isKM = brand === "kmarket";
            const badgeColor = isKM ? "#10B981" : "#F59E0B";

            return `
                <div class="hashtag-card" style="background:#F6F1EA;border:1px solid #E5DDD1;border-top:3px solid ${badgeColor};border-radius:14px;padding:16px;box-shadow:var(--shadow-md);transition:transform 0.25s ease, box-shadow 0.25s ease;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                        <div style="display:flex;align-items:center;gap:8px;">
                            <span style="font-size:20px;">${countryData.flag || '🌐'}</span>
                            <h4 style="margin:0;font-size:14px;font-weight:700;color:#1E1B18;">${countryData.country_name || countryData.name || countryCode} (${countryCode})</h4>
                        </div>
                        <span style="font-size:11px;color:#0284C7;font-weight:700;">실시간 트렌드</span>
                    </div>
                    <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:8px;">
                        ${tags.map(t => `
                            <span style="background:#FFFFFF;color:#334155;padding:4px 8px;border-radius:6px;font-size:11.5px;border:1px solid #E5DDD1;">
                                ${t.startsWith('#') ? t : '#' + t}
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
    const brand = typeof currentBrand !== "undefined" ? currentBrand : "kmarket";
    try {
        const res = await fetch(`/api/hashtags/refresh?brand=${encodeURIComponent(brand)}`, { method: "POST" });
        const data = await res.json();
        showToast(data.message || "해시태그 트렌드가 갱신되었습니다!", "success");
        loadHashtags();
    } catch (e) {
        showToast("해시태그 갱신 실패", "error");
    }
}

window.loadHashtags = loadHashtags;
window.refreshHashtags = refreshHashtags;

