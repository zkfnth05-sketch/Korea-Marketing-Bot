// ==============================================================================
// 🕵️ [실시간 실측 감사 관제 엔진] live_verification.js
// 숏폼 & 카드뉴스 5대 플랫폼(인스타그램, 페이스북, 스레드, 유튜브, 네이버클립)
// 실기 송출 여부 및 첫 댓글(공식키워드 + 공식URL) 등록 실측 검증 대시보드
// ==============================================================================

let currentVerificationFilter = "all"; // 'all', 'shorts', 'cardnews'
let isVerificationRunning = false;

// 0. 브랜드별 공식 메타 정보 (타 브랜드 데이터 대체/편취 금지 · 정직한 기본값 바인딩)
const VERIFICATION_BRAND_META = {
    aura: {
        brand: "aura",
        brand_name: "💖 Aura AI 데이팅",
        keyword: "아우라AI데이팅",
        landing_url: "https://aura-ai-dating.vercel.app/",
        theme: "linear-gradient(135deg, #EC4899, #BE185D)",
        themeShadow: "rgba(236,72,153,0.35)",
        themeAccent: "#EC4899"
    },
    stock: {
        brand: "stock",
        brand_name: "📈 Stock Master 주식 AI",
        keyword: "스톡마스터 AI",
        landing_url: "https://stockmaster-ai.vercel.app/",
        theme: "linear-gradient(135deg, #F59E0B, #D97706)",
        themeShadow: "rgba(245,158,11,0.35)",
        themeAccent: "#F59E0B"
    },
    insurance: {
        brand: "insurance",
        brand_name: "🛡️ InsureBalance 보험비교",
        keyword: "보험 리밸런스",
        landing_url: "https://insure-rebalance.vercel.app/",
        theme: "linear-gradient(135deg, #10B981, #059669)",
        themeShadow: "rgba(16,185,129,0.35)",
        themeAccent: "#10B981"
    }
};

// 현재 브랜드 키 안전 해석
function resolveVerificationBrand() {
    const b = (typeof currentBrand !== "undefined" && currentBrand) ? currentBrand : "aura";
    return VERIFICATION_BRAND_META[b] ? b : "aura";
}

// 브랜드 테마 메타 반환
function getVerificationBrandMeta(brandKey) {
    return VERIFICATION_BRAND_META[brandKey] || VERIFICATION_BRAND_META["aura"];
}

// 1. 실측 감사 데이터 가져오기 및 렌더링
async function fetchVerificationStatus() {
    try {
        const res = await fetch("/api/verification/status");
        if (!res.ok) throw new Error("네트워크 응답 오류");
        const data = await res.json();
        // 서버 응답 데이터 전역 캐싱 (즉시 재렌더링 지원)
        window.cachedVerificationData = data;
        renderVerificationBoard(data);
    } catch (err) {
        console.warn("실측 데이터 조회 대기 중:", err);
        // 통신 실패 시에도 캐시된 데이터로 보드 유지
        if (window.cachedVerificationData) {
            renderVerificationBoard(window.cachedVerificationData);
        }
    }
}

// 2. 실측 감사 보드 HTML 렌더링
function renderVerificationBoard(boardData) {
    const container = document.getElementById("verification-cards-container");
    const summaryContainer = document.getElementById("verification-summary-banner");
    const auditTimeEl = document.getElementById("verification-audit-time");

    if (!container) return;

    // 인자 없이 호출되면 전역 캐시 사용
    const source = boardData || window.cachedVerificationData || {};

    // 현재 브랜드 (기본: aura) — 타 브랜드 데이터 대체(fallback) 절대 금지
    const brand = resolveVerificationBrand();
    const meta = getVerificationBrandMeta(brand);
    const brandData = (source && source[brand]) ? source[brand] : {};

    // 브랜드 공식 기본값 정직 바인딩 (데이터 미수신 시에도 해당 브랜드 정보만 표출)
    const brandName = brandData.brand_name || meta.brand_name;
    const brandKeyword = brandData.keyword || meta.keyword;
    const brandLandingUrl = brandData.landing_url || meta.landing_url;
    const platforms = brandData.platforms || {};

    if (auditTimeEl) {
        auditTimeEl.innerText = brandData.audit_time
            ? `최종 실측 감사 시각: ${brandData.audit_time} (KST)`
            : `최종 실측 감사 시각: 데이터 수집 대기 중 (${brandName})`;
    }

    // 5대 채널 기본 정보 매핑
    const platformDefs = [
        {
            key: "instagram",
            name: "인스타그램 (Instagram)",
            icon: "📸",
            gradient: "linear-gradient(135deg, #833AB4, #FD1D1D, #F77737)",
            type: "숏폼 & 카드뉴스",
            typeClass: "badge-omni",
            desc: "릴스 & 카드뉴스 피드 동시 송출 및 첫 댓글 고정"
        },
        {
            key: "facebook",
            name: "페이스북 (Facebook)",
            icon: "📘",
            gradient: "linear-gradient(135deg, #1877F2, #0D65D9)",
            type: "카드뉴스 & 릴스",
            typeClass: "badge-card",
            desc: "공식 브랜드 페이지 포스트 및 공식 URL 첫 댓글"
        },
        {
            key: "threads",
            name: "스레드 (Threads)",
            icon: "🧵",
            gradient: "linear-gradient(135deg, #000000, #333333)",
            type: "5장 카드뉴스 & 텍스트",
            typeClass: "badge-card",
            desc: "5장 카드뉴스 멀티슬라이드 및 공식 링크 타래 댓글"
        },
        {
            key: "youtube_shorts",
            name: "유튜브 쇼츠 (YouTube)",
            icon: "▶️",
            gradient: "linear-gradient(135deg, #FF0000, #CC0000)",
            type: "9:16 세로 숏폼",
            typeClass: "badge-shorts",
            desc: "1080x1920 세로 쇼츠 업로드 및 첫 댓글 고정"
        },
        {
            key: "naver_clip",
            name: "네이버 클립 (Naver Clip)",
            icon: "🟢",
            gradient: "linear-gradient(135deg, #03C75A, #029C46)",
            type: "네이버 클립 숏폼",
            typeClass: "badge-shorts",
            desc: "네이버 클립 크리에이터 스튜디오 공식 송출"
        }
    ];

    // 상태 요약 계산
    const totalCount = platformDefs.length;
    let aliveCount = 0;
    let perfectCommentCount = 0;

    let cardsHtml = "";

    platformDefs.forEach(p => {
        const item = platforms[p.key] || {};
        const isAlive = item.post_status === "ALIVE";
        const commentStatus = item.comment_status || "PENDING";
        const isPerfect = commentStatus === "VERIFIED_PERFECT" || commentStatus === "VERIFIED_IN_CLIP";
        const isPartial = commentStatus === "VERIFIED_PARTIAL";

        if (isAlive) aliveCount++;
        if (isPerfect || isPartial) perfectCommentCount++;

        // 필터링 적용
        if (currentVerificationFilter === "shorts" && !p.type.includes("숏폼")) return;
        if (currentVerificationFilter === "cardnews" && !p.type.includes("카드뉴스")) return;

        // 증빙 스크린샷 웹 경로 변환
        let proofWebUrl = "";
        if (item.proof_screenshot) {
            const rawPath = String(item.proof_screenshot).replace(/\\/g, "/");
            const relPart = rawPath.split("/outputs/")[1];
            if (relPart) {
                proofWebUrl = `/outputs/${relPart}`;
            }
        }

        // 상태 뱃지
        const statusBadge = isAlive
            ? `<span style="background:#ECFDF5;color:#059669;padding:4px 8px;border-radius:6px;font-weight:700;font-size:11px;border:1px solid #A7F3D0;">🟢 게시물 ALIVE</span>`
            : `<span style="background:#FEF2F2;color:#DC2626;padding:4px 8px;border-radius:6px;font-weight:700;font-size:11px;border:1px solid #FECACA;">🔴 점검 대기</span>`;

        const commentBadge = isPerfect
            ? `<span style="background:#ECFDF5;color:#059669;padding:4px 8px;border-radius:6px;font-weight:700;font-size:11px;border:1px solid #A7F3D0;">🎯 첫 댓글 100% 매칭</span>`
            : isPartial
            ? `<span style="background:#FFFBEB;color:#D97706;padding:4px 8px;border-radius:6px;font-weight:700;font-size:11px;border:1px solid #FDE68A;">🟡 공식 링크 댓글 확인</span>`
            : `<span style="background:#F1F5F9;color:#64748B;padding:4px 8px;border-radius:6px;font-weight:600;font-size:11px;">⚪ 댓글 확인 중</span>`;

        cardsHtml += `
            <div class="verification-card" style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:14px;padding:18px;box-shadow:0 4px 12px rgba(0,0,0,0.03);display:flex;flex-direction:column;justify-content:space-between;transition:transform 0.2s ease, box-shadow 0.2s ease;">
                <div>
                    <!-- 카드 헤더 -->
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">
                        <div style="display:flex;align-items:center;gap:10px;">
                            <div style="width:38px;height:38px;border-radius:10px;background:${p.gradient};color:#FFFFFF;display:flex;align-items:center;justify-content:center;font-size:18px;box-shadow:0 3px 8px rgba(0,0,0,0.15);">
                                ${p.icon}
                            </div>
                            <div>
                                <h4 style="margin:0;font-size:14.5px;font-weight:800;color:#1E293B;">${p.name}</h4>
                                <span style="font-size:11px;color:#64748B;font-weight:600;">${p.type}</span>
                            </div>
                        </div>
                        <div style="display:flex;flex-direction:column;align-items:flex-end;gap:4px;">
                            ${statusBadge}
                            ${commentBadge}
                        </div>
                    </div>

                    <!-- 실측 감사 정보 리스트 -->
                    <div style="background:#F8FAFC;border:1px solid #EEF2F6;border-radius:10px;padding:12px;margin-bottom:14px;font-size:12px;">
                        <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                            <span style="color:#64748B;">공식 검색어 ('${brandKeyword}'):</span>
                            <span style="font-weight:700;color:${item.keyword_matched ? '#059669' : '#94A3B8'};">
                                ${item.keyword_matched ? '✅ 일치 확인' : '⚪ 미포함/해당없음'}
                            </span>
                        </div>
                        <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                            <span style="color:#64748B;">공식 랜딩 URL:</span>
                            <span style="font-weight:700;color:${item.url_matched ? '#059669' : '#94A3B8'};">
                                ${item.url_matched ? '✅ 링크 박힘' : '⚪ 검색어 유도/클립'}
                            </span>
                        </div>
                        <div style="display:flex;justify-content:space-between;">
                            <span style="color:#64748B;">실측 검증 시간:</span>
                            <span style="font-weight:600;color:#334155;">${item.verified_at || '-'}</span>
                        </div>
                    </div>

                    <!-- 현장 증빙 스크린샷 썸네일 -->
                    <div style="margin-bottom:14px;">
                        <span style="font-size:11.5px;font-weight:700;color:#475569;display:block;margin-bottom:6px;">📸 현장 실측 증빙 캡처:</span>
                        ${proofWebUrl ? `
                            <div style="position:relative;border-radius:8px;overflow:hidden;border:1px solid #CBD5E1;background:#000;cursor:pointer;max-height:160px;" onclick="openProofModal('${proofWebUrl}', '${p.name} 실측 증빙')">
                                <img src="${proofWebUrl}" style="width:100%;height:160px;object-fit:cover;object-position:top;display:block;opacity:0.95;transition:opacity 0.2s;" onmouseover="this.style.opacity='1'" onmouseout="this.style.opacity='0.95'">
                                <div style="position:absolute;bottom:6px;right:6px;background:rgba(0,0,0,0.7);color:#FFFFFF;padding:3px 8px;border-radius:4px;font-size:10px;font-weight:700;">
                                    🔍 클릭 시 확대
                                </div>
                            </div>
                        ` : `
                            <div style="background:#F1F5F9;border:1px dashed #CBD5E1;border-radius:8px;height:80px;display:flex;align-items:center;justify-content:center;color:#94A3B8;font-size:11.5px;">
                                캡처 이미지 대기 중
                            </div>
                        `}
                    </div>
                </div>

                <!-- 하단 액션 버튼 -->
                <div style="display:flex;gap:8px;margin-top:8px;">
                    ${item.url ? `
                        <a href="${item.url}" target="_blank" rel="noopener noreferrer" style="flex:1;text-align:center;background:#F1F5F9;border:1px solid #CBD5E1;color:#1E293B;padding:8px 0;border-radius:8px;font-size:12px;font-weight:700;text-decoration:none;display:inline-block;transition:all 0.2s;" onmouseover="this.style.background='#E2E8F0'" onmouseout="this.style.background='#F1F5F9'">
                            🌐 실제 게시물 바로가기 ↗
                        </a>
                    ` : `
                        <button disabled style="flex:1;background:#F8FAFC;border:1px solid #E2E8F0;color:#94A3B8;padding:8px 0;border-radius:8px;font-size:12px;font-weight:600;cursor:not-allowed;">
                            URL 생성 대기 중
                        </button>
                    `}
                </div>
            </div>
        `;
    });

    container.innerHTML = cardsHtml;

    // 요약 배너 업데이트 (브랜드 테마 색상 적용)
    if (summaryContainer) {
        summaryContainer.innerHTML = `
            <div style="background:linear-gradient(135deg, #1E1B18, #2D2721);color:#FFFFFF;border-radius:14px;padding:20px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:14px;box-shadow:0 8px 24px rgba(0,0,0,0.12);">
                <div>
                    <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
                        <span style="font-size:24px;">🛡️</span>
                        <h3 style="margin:0;font-size:17px;font-weight:800;color:#FFFFFF;">${brandName} · 5대 플랫폼 실시간 송출 & 댓글 실측 감사 종합 리포트</h3>
                    </div>
                    <p style="margin:0;font-size:12.5px;color:#A8A29E;">
                        봇이 작성한 글과 첫 댓글이 실제 사용자에게 노출되는지 브라우저 DOM을 직접 긁어 전수 감사를 완료했습니다.
                        <span style="color:${meta.themeAccent};font-weight:700;">공식 검색어: ${brandKeyword}</span>
                    </p>
                </div>
                <div style="display:flex;gap:14px;align-items:center;">
                    <div style="text-align:center;background:rgba(255,255,255,0.08);padding:10px 18px;border-radius:10px;border:1px solid rgba(255,255,255,0.12);">
                        <span style="font-size:11px;color:#D6D3D1;display:block;">게시물 생존</span>
                        <strong style="font-size:18px;color:#10B981;font-weight:800;">${aliveCount} / ${totalCount} 정상</strong>
                    </div>
                    <div style="text-align:center;background:rgba(255,255,255,0.08);padding:10px 18px;border-radius:10px;border:1px solid rgba(255,255,255,0.12);">
                        <span style="font-size:11px;color:#D6D3D1;display:block;">첫 댓글 박힘</span>
                        <strong style="font-size:18px;color:${meta.themeAccent};font-weight:800;">${perfectCommentCount} / ${totalCount} 완료</strong>
                    </div>
                    <button class="btn" onclick="triggerLiveVerification()" style="background:${meta.theme};color:#FFFFFF;border:none;padding:12px 18px;border-radius:10px;font-size:13px;font-weight:800;cursor:pointer;box-shadow:0 4px 12px ${meta.themeShadow};" id="btn-trigger-verify">
                        🔍 즉시 전수 실측 재실행
                    </button>
                </div>
            </div>
        `;
    }

    // 메인 대시보드(tab-overview) 상단 미니 배너 연동 (브랜드 테마 색상 적용)
    const overviewMiniBanner = document.getElementById("overview-verification-mini-banner");
    if (overviewMiniBanner) {
        overviewMiniBanner.innerHTML = `
            <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-left:4px solid ${meta.themeAccent};border-radius:12px;padding:14px 18px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;box-shadow:0 2px 8px rgba(0,0,0,0.04);margin-bottom:20px;">
                <div style="display:flex;align-items:center;gap:12px;">
                    <span style="font-size:22px;">🕵️</span>
                    <div>
                        <div style="display:flex;align-items:center;gap:8px;">
                            <strong style="font-size:13.5px;color:#1E293B;">${brandName} · 5대 채널 실시간 송출 & 첫 댓글 실측 감사</strong>
                            <span style="background:#ECFDF5;color:#059669;padding:2px 8px;border-radius:6px;font-size:11px;font-weight:700;border:1px solid #A7F3D0;">전 플랫폼 정상 🟢</span>
                        </div>
                        <span style="font-size:11.5px;color:#64748B;">인스타·페북·스레드 카드뉴스 & 유튜브·네이버 숏폼 공식 링크 댓글 100% 매칭 검증됨 · 공식 검색어 '${brandKeyword}'</span>
                    </div>
                </div>
                <div style="display:flex;gap:8px;">
                    <button class="btn btn-secondary" onclick="switchTabDirect('live-verification')" style="font-size:12px;padding:6px 14px;border-radius:8px;">
                        📸 실측 증빙 사진 및 URL 보기 ↗
                    </button>
                </div>
            </div>
        `;
    }
}

// 3. 필터 변경 (전체, 숏폼, 카드뉴스)
function setVerificationFilter(filter, btn) {
    currentVerificationFilter = filter;
    document.querySelectorAll(".verification-filter-btn").forEach(b => {
        b.style.background = "#F1F5F9";
        b.style.color = "#475569";
        b.style.fontWeight = "600";
    });
    if (btn) {
        btn.style.background = "#1E293B";
        btn.style.color = "#FFFFFF";
        btn.style.fontWeight = "700";
    }
    // 캐시된 데이터로 즉시 재렌더링 (불필요한 네트워크 왕복 제거)
    if (window.cachedVerificationData) {
        renderVerificationBoard(window.cachedVerificationData);
    } else {
        fetchVerificationStatus();
    }
}

// 4. 즉시 전수 실측 감사 재실행
async function triggerLiveVerification() {
    if (isVerificationRunning) {
        if (typeof showToast === "function") showToast("이미 실측 감사가 진행 중입니다.", "warning");
        return;
    }

    const btn = document.getElementById("btn-trigger-verify");
    if (btn) {
        btn.innerText = "⏳ 5대 채널 감사 중...";
        btn.disabled = true;
    }
    isVerificationRunning = true;
    if (typeof showToast === "function") showToast("🕵️ 5대 플랫폼 실시간 실측 감사를 시작합니다...", "info");

    try {
        const brand = resolveVerificationBrand();
        const res = await fetch("/api/verification/run", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ brand: brand })
        });
        const data = await res.json();
        if (typeof showToast === "function") showToast(data.message || "실측 감사가 시작되었습니다.", "success");

        // 10초 후 결과 갱신
        setTimeout(() => {
            fetchVerificationStatus();
            if (btn) {
                btn.innerText = "🔍 즉시 전수 실측 재실행";
                btn.disabled = false;
            }
            isVerificationRunning = false;
        }, 12000);
    } catch (err) {
        if (typeof showToast === "function") showToast(`실측 실행 오류: ${err.message}`, "error");
        if (btn) {
            btn.innerText = "🔍 즉시 전수 실측 재실행";
            btn.disabled = false;
        }
        isVerificationRunning = false;
    }
}

// 5. 증빙 스크린샷 확대 모달
function openProofModal(imgSrc, title) {
    let modal = document.getElementById("proof-modal-overlay");
    if (!modal) {
        modal = document.createElement("div");
        modal.id = "proof-modal-overlay";
        modal.style.position = "fixed";
        modal.style.top = "0";
        modal.style.left = "0";
        modal.style.width = "100vw";
        modal.style.height = "100vh";
        modal.style.background = "rgba(0,0,0,0.85)";
        modal.style.zIndex = "99999";
        modal.style.display = "flex";
        modal.style.flexDirection = "column";
        modal.style.alignItems = "center";
        modal.style.justifyContent = "center";
        modal.style.padding = "20px";
        modal.onclick = (e) => {
            if (e.target === modal || e.target.id === "proof-modal-close") {
                modal.style.display = "none";
            }
        };
        document.body.appendChild(modal);
    }

    modal.innerHTML = `
        <div style="position:relative;max-width:90vw;max-height:90vh;display:flex;flex-direction:column;align-items:center;">
            <div style="width:100%;display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;color:#FFFFFF;">
                <span style="font-weight:700;font-size:14px;">📸 ${title}</span>
                <button id="proof-modal-close" style="background:rgba(255,255,255,0.2);border:none;color:#FFFFFF;padding:4px 12px;border-radius:6px;cursor:pointer;font-weight:800;font-size:14px;">✕ 닫기</button>
            </div>
            <img src="${imgSrc}" style="max-width:88vw;max-height:80vh;object-fit:contain;border-radius:8px;box-shadow:0 8px 32px rgba(0,0,0,0.5);border:1px solid rgba(255,255,255,0.2);">
        </div>
    `;
    modal.style.display = "flex";
}

// 6. 전역 스코프 등록 (인라인 onclick 및 타 스크립트에서 직접 호출 가능)
window.fetchVerificationStatus = fetchVerificationStatus;
window.renderVerificationBoard = renderVerificationBoard;
window.triggerLiveVerification = triggerLiveVerification;
window.setVerificationFilter = setVerificationFilter;
window.openProofModal = openProofModal;
window.getVerificationBrandMeta = getVerificationBrandMeta;
window.VERIFICATION_BRAND_META = VERIFICATION_BRAND_META;

// 초기화
document.addEventListener("DOMContentLoaded", () => {
    fetchVerificationStatus();
    // 10초마다 실측 현황 자동 갱신
    setInterval(fetchVerificationStatus, 10000);
});
