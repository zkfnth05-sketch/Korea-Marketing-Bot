// ==========================================
// [모듈 2] overview.js: 대시보드 & 8대 AI 허브 24시간 무인 관제 전담 모듈
// ==========================================



async function fetchGoldenTargets() {
    try {
        const res = await fetch("/api/golden-targets");
        if (!res.ok) return;
        const data = await res.json();
        if (data.channels) {
            updateGoldenTargetIndicators(data.channels);
        }
    } catch (e) {}
}

function updateGoldenTargetIndicators(goldenTargets) {
    if (!goldenTargets) return;
    Object.keys(goldenTargets).forEach(chKey => {
        const info = goldenTargets[chKey];
        if (!info) return;
        const brand = chKey.startsWith("easytax_") ? "easytax" : "kmarket";
        const moduleName = chKey.replace("kmarket_", "").replace("easytax_", "");
        const indicator = document.getElementById(`golden-target-indicator-${brand}-${moduleName}`);
        if (indicator && info.detail) {
            indicator.innerText = `다음 순번: ${info.detail.flag || ''} ${info.detail.native || info.current_lang} (${info.current_lang})`;
        }
    });
}

// 0. 각 채널(24개 허브) 고유의 브랜드 다채색(Multicolor) 테마 정의
function getHubColorTheme(key, index) {
    const themes = {
        // 1. 미디어 / 영상 / 숏폼
        shorts: {
            primary: "#EF4444",
            startGradient: "linear-gradient(135deg, #EF4444 0%, #DC2626 100%)",
            actionBg: "#FEF2F2",
            actionBorder: "#FECACA",
            actionColor: "#B91C1C",
            batchGradient: "linear-gradient(135deg, #F43F5E 0%, #E11D48 100%)"
        },
        cardnews: {
            primary: "#EC4899",
            startGradient: "linear-gradient(135deg, #EC4899 0%, #DB2777 100%)",
            actionBg: "#FDF2F8",
            actionBorder: "#FBCFE8",
            actionColor: "#BE185D",
            batchGradient: "linear-gradient(135deg, #D946EF 0%, #C026D3 100%)"
        },
        // 2. 글로벌 SNS
        reddit: {
            primary: "#FF4500",
            startGradient: "linear-gradient(135deg, #FF4500 0%, #EA580C 100%)",
            actionBg: "#FFF7ED",
            actionBorder: "#FED7AA",
            actionColor: "#C2410C"
        },
        fb_groups: {
            primary: "#1877F2",
            startGradient: "linear-gradient(135deg, #1877F2 0%, #0284C7 100%)",
            actionBg: "#EFF6FF",
            actionBorder: "#BFDBFE",
            actionColor: "#1D4ED8"
        },
        blog: {
            primary: "#2563EB",
            startGradient: "linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)",
            actionBg: "#F0F9FF",
            actionBorder: "#BAE6FD",
            actionColor: "#0369A1"
        },
        seo: {
            primary: "#0EA5E9",
            startGradient: "linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%)",
            actionBg: "#F0FDFA",
            actionBorder: "#99F6E4",
            actionColor: "#0F766E"
        },
        threads: {
            primary: "#334155",
            startGradient: "linear-gradient(135deg, #475569 0%, #1E293B 100%)",
            actionBg: "#F8FAFC",
            actionBorder: "#CBD5E1",
            actionColor: "#334155"
        },
        // 3. 네이버 계열 (고유 그린 & 틸 계열 분화)
        naver_clip: {
            primary: "#059669",
            startGradient: "linear-gradient(135deg, #10B981 0%, #059669 100%)",
            actionBg: "#ECFDF5",
            actionBorder: "#A7F3D0",
            actionColor: "#047857"
        },
        naver_blog: {
            primary: "#03C75A",
            startGradient: "linear-gradient(135deg, #03C75A 0%, #029F48 100%)",
            actionBg: "#F0FDF4",
            actionBorder: "#BBF7D0",
            actionColor: "#15803D"
        },
        naver_post: {
            primary: "#0D9488",
            startGradient: "linear-gradient(135deg, #0D9488 0%, #0F766E 100%)",
            actionBg: "#CCFBF1",
            actionBorder: "#99F6E4",
            actionColor: "#115E59"
        },
        search_advisor: {
            primary: "#0284C7",
            startGradient: "linear-gradient(135deg, #0284C7 0%, #0369A1 100%)",
            actionBg: "#F0F9FF",
            actionBorder: "#BAE6FD",
            actionColor: "#075985"
        },
        naver_kin: {
            primary: "#16A34A",
            startGradient: "linear-gradient(135deg, #22C55E 0%, #16A34A 100%)",
            actionBg: "#DCFCE7",
            actionBorder: "#86EFAC",
            actionColor: "#166534"
        },
        naver_cafe: {
            primary: "#15803D",
            startGradient: "linear-gradient(135deg, #16A34A 0%, #15803D 100%)",
            actionBg: "#F0FDF4",
            actionBorder: "#BBF7D0",
            actionColor: "#14532D"
        },
        // 4. 카카오 계열 & 티스토리
        tistory: {
            primary: "#F97316",
            startGradient: "linear-gradient(135deg, #FB923C 0%, #EA580C 100%)",
            actionBg: "#FFF7ED",
            actionBorder: "#FED7AA",
            actionColor: "#C2410C"
        },
        brunch: {
            primary: "#78350F",
            startGradient: "linear-gradient(135deg, #92400E 0%, #78350F 100%)",
            actionBg: "#FEF3C7",
            actionBorder: "#FDE68A",
            actionColor: "#92400E"
        },
        daum_cafe: {
            primary: "#D97706",
            startGradient: "linear-gradient(135deg, #F59E0B 0%, #D97706 100%)",
            actionBg: "#FFFBEB",
            actionBorder: "#FDE68A",
            actionColor: "#B45309"
        },
        kakao_channel: {
            primary: "#EAB308",
            startGradient: "linear-gradient(135deg, #FACC15 0%, #EAB308 100%)",
            actionBg: "#FEFCE8",
            actionBorder: "#FEF08A",
            actionColor: "#854D0E"
        },
        // 5. 대형 커뮤니티 (차별화된 다채로운 색상)
        ppomppu: {
            primary: "#4F46E5",
            startGradient: "linear-gradient(135deg, #6366F1 0%, #4F46E5 100%)",
            actionBg: "#EEF2FF",
            actionBorder: "#C7D2FE",
            actionColor: "#4338CA"
        },
        dcinside: {
            primary: "#2563EB",
            startGradient: "linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)",
            actionBg: "#EFF6FF",
            actionBorder: "#BFDBFE",
            actionColor: "#1E40AF"
        },
        bobaedream: {
            primary: "#7C3AED",
            startGradient: "linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%)",
            actionBg: "#F5F3FF",
            actionBorder: "#DDD6FE",
            actionColor: "#6D28D9"
        },
        nate_pann: {
            primary: "#E11D48",
            startGradient: "linear-gradient(135deg, #F43F5E 0%, #E11D48 100%)",
            actionBg: "#FFF1F2",
            actionBorder: "#FECDD3",
            actionColor: "#BE123C"
        },
        fmkorea: {
            primary: "#0284C7",
            startGradient: "linear-gradient(135deg, #38BDF8 0%, #0284C7 100%)",
            actionBg: "#F0F9FF",
            actionBorder: "#BAE6FD",
            actionColor: "#0369A1"
        },
        twitter_x: {
            primary: "#0F172A",
            startGradient: "linear-gradient(135deg, #334155 0%, #0F172A 100%)",
            actionBg: "#F8FAFC",
            actionBorder: "#CBD5E1",
            actionColor: "#0F172A"
        }
    };

    if (themes[key]) return themes[key];

    // Fallback: 다채로운 프리미엄 순환 팔레트
    const palette = [
        { primary: "#2563EB", startGradient: "linear-gradient(135deg, #3B82F6, #1D4ED8)", actionBg: "#EFF6FF", actionBorder: "#BFDBFE", actionColor: "#1E40AF" },
        { primary: "#059669", startGradient: "linear-gradient(135deg, #10B981, #059669)", actionBg: "#ECFDF5", actionBorder: "#A7F3D0", actionColor: "#047857" },
        { primary: "#7C3AED", startGradient: "linear-gradient(135deg, #8B5CF6, #7C3AED)", actionBg: "#F5F3FF", actionBorder: "#DDD6FE", actionColor: "#6D28D9" },
        { primary: "#D97706", startGradient: "linear-gradient(135deg, #F59E0B, #D97706)", actionBg: "#FFFBEB", actionBorder: "#FDE68A", actionColor: "#B45309" },
        { primary: "#E11D48", startGradient: "linear-gradient(135deg, #F43F5E, #E11D48)", actionBg: "#FFF1F2", actionBorder: "#FECDD3", actionColor: "#BE123C" },
        { primary: "#0D9488", startGradient: "linear-gradient(135deg, #14B8A6, #0D9488)", actionBg: "#CCFBF1", actionBorder: "#99F6E4", actionColor: "#115E59" },
        { primary: "#4F46E5", startGradient: "linear-gradient(135deg, #6366F1, #4F46E5)", actionBg: "#EEF2FF", actionBorder: "#C7D2FE", actionColor: "#4338CA" },
        { primary: "#EA580C", startGradient: "linear-gradient(135deg, #FB923C, #EA580C)", actionBg: "#FFF7ED", actionBorder: "#FED7AA", actionColor: "#C2410C" }
    ];
    return palette[(index || 0) % palette.length];
}

// 1. 대시보드 22대 AI 마케팅 허브 그리드 동적 렌더링 (APP_PIPELINES 모듈 연동)
function renderHubGrid() {
    const container = document.getElementById("hub-grid-container");
    const panelTitle = document.getElementById("hub-panel-title");
    const panelDesc = document.getElementById("hub-panel-desc");
    if (!container) return;

    const brand = currentBrand || "aura";
    const app = (typeof APP_PIPELINES !== "undefined" && APP_PIPELINES[brand]) ? APP_PIPELINES[brand] : APP_PIPELINES["aura"];

    if (panelTitle) panelTitle.innerText = `🎯 24대 AI 마케팅 허브 & 24시간 무인 자율 공장`;
    if (panelDesc) panelDesc.innerText = `숏폼, 카드뉴스, 레딧, 페이스북, 블로그, 구글 색인 핑, 스레드 및 국내 16대 포털/커뮤니티 채널을 24시간 자율 가동합니다. (텔레그램은 상단 전용 사령부에서 통합 관제)`;

    container.innerHTML = app.hubs.map((h, idx) => {
        const theme = getHubColorTheme(h.key, idx);
        const isShorts = h.key === "shorts";
        const isCardnews = h.key === "cardnews";
        const isOmniBlog = h.key === "omni_blog";
        const isThreads = h.key === "threads";
        const isSeo = h.key === "seo";
        const isKin = h.key === "naver_kin" || h.isKin;
        const runActionText = isShorts 
            ? "🎬 완성 숏폼 원클릭 제작" 
            : isCardnews 
            ? "📸 카드뉴스 원클릭 제작" 
            : isOmniBlog 
            ? "🚀 옴니블로그 즉시 1회 발행" 
            : isThreads
            ? "📜 스토리 타래 1회 발행"
            : isSeo
            ? "🌐 구글·네이버 동시 색인 핑"
            : isKin
            ? "💡 지식iN 실시간 1회 낚아채기"
            : "⚡ 즉시 1회 시험 실행";
        const runActionOnClick = isOmniBlog 
            ? `publishOmniBlog('${brand}')`
            : isSeo
            ? `triggerSeoPing('${brand}', this)`
            : isKin
            ? `triggerKinCatch('${brand}', this)`
            : `runModule('${brand}_${h.key}')`;

        // 🌐 SEO 전용 서치콘솔 바로가기 링크 그룹
        const seoConsoleLinks = isSeo ? `
            <div style="display:flex;flex-wrap:wrap;gap:4px;margin-top:8px;padding-top:8px;border-top:1px dashed #E5DDD1;">
                <a href="${h.googleConsoleUrl || 'https://search.google.com/search-console'}" target="_blank" rel="noopener noreferrer" style="font-size:10.5px;font-weight:700;color:#2563EB;background:#EFF6FF;border:1px solid #BFDBFE;padding:3px 6px;border-radius:6px;text-decoration:none;display:inline-flex;align-items:center;gap:3px;" title="구글 서치콘솔 관리자 페이지 열기">
                    <span>🔍 구글 콘솔 ↗</span>
                </a>
                <a href="${h.naverAdvisorUrl || 'https://searchadvisor.naver.com/console/board'}" target="_blank" rel="noopener noreferrer" style="font-size:10.5px;font-weight:700;color:#059669;background:#ECFDF5;border:1px solid #A7F3D0;padding:3px 6px;border-radius:6px;text-decoration:none;display:inline-flex;align-items:center;gap:3px;" title="네이버 서치어드바이저 관리자 페이지 열기">
                    <span>🧭 네이버 콘솔 ↗</span>
                </a>
                <a href="${h.sitemapUrl || '#'}" target="_blank" rel="noopener noreferrer" style="font-size:10.5px;font-weight:700;color:#7C3AED;background:#F5F3FF;border:1px solid #DDD6FE;padding:3px 6px;border-radius:6px;text-decoration:none;display:inline-flex;align-items:center;gap:3px;" title="등록된 XML 사이트맵 보기">
                    <span>📄 사이트맵 ↗</span>
                </a>
            </div>
        ` : '';

        // 💡 지식iN 전용 실시간 쿼터 & 바로가기 위젯
        const kinWidget = isKin ? `
            <div style="margin-top:8px;padding-top:8px;border-top:1px dashed #E5DDD1;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                    <span style="font-size:11px;font-weight:700;color:#059669;">🎯 일일 선발 쿼터:</span>
                    <span id="kin-quota-${brand}" style="font-size:11px;font-weight:800;color:#1E1B18;background:#ECFDF5;border:1px solid #A7F3D0;padding:2px 8px;border-radius:10px;">
                        <span id="kin-count-${brand}">0</span> / 10개 (엄선 26:1)
                    </span>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                    <span style="font-size:11px;color:#6E665E;">현재 활성 슬롯:</span>
                    <span id="kin-slot-${brand}" style="font-size:10.5px;font-weight:700;color:#2563EB;">🌙 실시간 감지 중</span>
                </div>
                <div id="kin-recent-${brand}" style="font-size:11px;color:#4A443D;background:#FFFFFF;padding:6px 8px;border-radius:6px;border:1px solid #E5DDD1;margin-bottom:6px;max-height:45px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
                    최근 낚아챈 질문: 대기 중
                </div>
                <div style="display:flex;gap:4px;">
                    <a href="https://kin.naver.com" target="_blank" rel="noopener noreferrer" style="font-size:10.5px;font-weight:700;color:#059669;background:#ECFDF5;border:1px solid #A7F3D0;padding:3px 6px;border-radius:6px;text-decoration:none;display:inline-flex;align-items:center;gap:3px;" title="네이버 지식iN 바로가기">
                        <span>💡 네이버 지식iN ↗</span>
                    </a>
                </div>
            </div>
        ` : '';

        return `
        <div class="action-card" id="card-${brand}-${h.key}" style="background:#F6F1EA;border:1px solid #E5DDD1;border-top:3.5px solid ${theme.primary};border-radius:14px;padding:16px;display:flex;flex-direction:column;justify-content:space-between;gap:12px;box-shadow:var(--shadow-md);transition:transform 0.25s ease, box-shadow 0.25s ease;">
            <div>
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
                    <span style="font-size:24px;width:38px;height:38px;display:flex;align-items:center;justify-content:center;background:#FFFFFF;border:1px solid #E5DDD1;border-radius:8px;">${h.icon}</span>
                    <div>
                        <div style="font-size:11px;color:${theme.primary};font-weight:800;">#${idx+1} 마케팅 허브</div>
                        <h4 style="margin:0;font-size:14px;font-weight:700;color:#1E1B18;">${h.name}</h4>
                    </div>
                </div>
                <p style="font-size:11.5px;color:#6E665E;margin:0 0 10px 0;line-height:1.45;">${h.desc}</p>
                ${seoConsoleLinks}
                ${kinWidget}

                <!-- 실시간 24시간 가동 상태 바 -->
                <div style="display:flex;justify-content:space-between;align-items:center;background:#FFFFFF;padding:6px 10px;border-radius:8px;border:1px solid #E5DDD1;margin-top:8px;">
                    <span style="font-size:11px;color:#6E665E;">실시간 상태:</span>
                    <span id="badge-status-${brand}-${h.key}" class="badge-idle" style="font-size:11px;font-weight:700;padding:2px 8px;border-radius:10px;background:#F6F1EA;color:#6E665E;border:1px solid #E5DDD1;">
                        ⚪ 대기
                    </span>
                </div>
            </div>

            <div>
                <!-- 1:1 무인 가동 및 정지 버튼 그룹 -->
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:6px;">
                    <button class="btn" id="btn-start-${brand}-${h.key}" data-original-bg="${theme.startGradient}" onclick="startChannelDaemon('${brand}_${h.key}', this)" style="font-size:11.5px;padding:7px 4px;font-weight:800;background:${theme.startGradient};color:#FFFFFF;border:none;border-radius:8px;box-shadow:0 3px 8px rgba(0,0,0,0.12);cursor:pointer;" title="24시간 무인 자동 배포 데몬 시작">
                        🚀 무인 가동
                    </button>
                    <button class="btn btn-stop" id="btn-stop-${brand}-${h.key}" onclick="stopChannelDaemon('${brand}_${h.key}', this)" style="font-size:11.5px;padding:7px 4px;font-weight:700;border-radius:8px;cursor:pointer;" title="무인 데몬 정지">
                        ⏹️ 정지
                    </button>
                </div>
                <button class="btn btn-action" id="${isOmniBlog ? `btn-omni-${brand}` : isSeo ? `btn-seo-${brand}` : isKin ? `btn-kin-${brand}` : `btn-run-${brand}-${h.key}`}" onclick="${runActionOnClick}" style="width:100%;font-size:11.5px;padding:7px 0;background:${theme.actionBg};border:1px solid ${theme.actionBorder};color:${theme.actionColor};font-weight:700;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,0.04);cursor:pointer;">
                    ${runActionText}
                </button>
            </div>
        </div>
    `}).join("");

    setTimeout(() => {
        loadMediaEngineSettings();
        loadKinStats(brand);
    }, 50);
}

// 🌐 3대 슈퍼앱 전용 구글 & 네이버 실시간 색인 핑 전송 트리거
async function triggerSeoPing(brand, btn) {
    const nameMap = { "aura": "💖 Aura", "insurance": "🛡️ 보험비교", "stock": "📈 주식AI", "kmarket": "🛒 K-Market", "easytax": "💰 EasyTax" };
    const brandName = nameMap[brand] || brand.toUpperCase();
    
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<span class="spin-icon" style="display:inline-block;animation:rotateSpin 0.6s linear infinite;">🔄</span> 2대 포털 핑 전송 중...`;
    }
    appendLog(`[SEO Ping] 🌐 ${brandName} 구글 서치콘솔 + 네이버 서치어드바이저 동시 색인 핑 전송 시작...`, "info");
    showToast(`🌐 ${brandName} 구글·네이버 검색엔진 동시 색인 핑을 전송합니다!`, "info");

    try {
        const res = await fetch(`/api/seo/ping/${brand}`, { method: "POST" });
        const data = await res.json();
        showToast(data.message || `🌐 ${brandName} 2대 검색엔진 색인 핑 완료!`, "success");
        appendLog(`[SEO Ping Success] 🎉 ${data.message || '색인 핑 전송 완료'}`, "success");
        if (typeof fetchStatus === "function") fetchStatus();
    } catch (e) {
        showToast(`❌ 색인 핑 요청 실패: ${e}`, "error");
        appendLog(`[SEO Ping Error] ❌ ${e}`, "error");
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `🌐 구글·네이버 동시 색인 핑`;
        }
    }
}

// 💡 Aura 및 브랜드 전용 네이버 지식iN 100대 키워드 실시간 낚아채기 트리거
async function triggerKinCatch(brand, btn) {
    const nameMap = { "aura": "💖 Aura 데이팅", "insurance": "🛡️ 보험비교", "stock": "📈 주식AI" };
    const brandName = nameMap[brand] || brand.toUpperCase();

    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<span class="spin-icon" style="display:inline-block;animation:rotateSpin 0.6s linear infinite;">🔄</span> 100대 키워드 낚아채는 중...`;
    }
    appendLog(`[지식iN 레이더] 💡 ${brandName} 100대 황금 키워드 실시간 질문 스캔 & 85점 심사 시작...`, "info");
    showToast(`💡 ${brandName} 네이버 지식iN 실시간 낚아채기를 실행합니다!`, "info");

    try {
        const res = await fetch(`/api/kin/${brand}/run`, { method: "POST" });
        const data = await res.json();
        showToast(data.message || `💡 ${brandName} 지식iN 낚아채기 가동 완료!`, "success");
        appendLog(`[지식iN 가동] 🎉 ${data.message || '완료'}`, "success");
        setTimeout(() => loadKinStats(brand), 3000);
    } catch (e) {
        showToast(`❌ 지식iN 실행 실패: ${e}`, "error");
        appendLog(`[지식iN Error] ❌ ${e}`, "error");
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `💡 지식iN 실시간 1회 낚아채기`;
        }
    }
}

// 💡 네이버 지식iN 실시간 일일 쿼터 및 최근 등록 내역 조회
async function loadKinStats(brand = "aura") {
    try {
        const res = await fetch(`/api/kin/${brand}/history`);
        const data = await res.json();
        if (data.success) {
            const countEl = document.getElementById(`kin-count-${brand}`);
            if (countEl) countEl.innerText = data.daily_total || 0;
            const slotEl = document.getElementById(`kin-slot-${brand}`);
            if (slotEl && data.current_slot) slotEl.innerText = data.current_slot.name || "실시간 감지 중";
            const recentEl = document.getElementById(`kin-recent-${brand}`);
            if (recentEl && data.history && data.history.length > 0) {
                const latest = data.history[0];
                recentEl.innerHTML = `<a href="${latest.url}" target="_blank" style="color:#2563EB;text-decoration:underline;font-weight:600;" title="${latest.title}">[${latest.score}점] ${latest.title}</a>`;
            }
        }
    } catch (e) {
        console.debug("지식iN 통계 로드 예외:", e);
    }
}

// 2. 24시간 무인 자율 채널 데몬 시작
async function startChannelDaemon(moduleKey, btn) {
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<span class="spin-icon" style="display:inline-block;animation:rotateSpin 0.6s linear infinite;">🔄</span> 가동 중...`;
    }
    const cleanKey = moduleKey.replace("kmarket_", "").replace("easytax_", "").replace("stock_", "").replace("aura_", "").replace("insurance_", "");
    const brandPrefix = moduleKey.startsWith("aura_") ? "aura" : moduleKey.startsWith("insurance_") ? "insurance" : moduleKey.startsWith("stock_") ? "stock" : moduleKey.startsWith("easytax_") ? "easytax" : "kmarket";
    const badge = document.getElementById(`badge-status-${brandPrefix}-${cleanKey}`);
    if (badge) {
        badge.className = "badge-running";
        badge.style.background = "#DCFCE7";
        badge.style.color = "#15803D";
        badge.style.border = "1px solid #86EFAC";
        badge.innerHTML = "🟢 실행 중 (24h)";
    }

    try {
        const res = await fetch(`/api/channel/start/${moduleKey}`, { method: "POST" });
        const data = await res.json();
        showToast(data.message || `[${moduleKey}] 24시간 무인 가동이 시작되었습니다! 🚀`, "success");
        appendLog(`[Daemon Start] ${data.message || moduleKey}`, "success");
        if (btn) {
            btn.innerHTML = `🔄 무인 가동 중 🟢`;
            btn.style.background = "#059669";
            btn.disabled = false;
        }
        fetchStatus();
    } catch (e) {
        showToast("가동 요청 통신 오류", "error");
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `🚀 무인 가동`;
            btn.style.background = btn.getAttribute("data-original-bg") || "";
        }
    }
}

// 3. 24시간 무인 자율 채널 데몬 정지
async function stopChannelDaemon(moduleKey, btn) {
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `⏹️ 정지 중...`;
    }
    const cleanKey = moduleKey.replace("kmarket_", "").replace("easytax_", "").replace("stock_", "").replace("aura_", "").replace("insurance_", "");
    const brandPrefix = moduleKey.startsWith("aura_") ? "aura" : moduleKey.startsWith("insurance_") ? "insurance" : moduleKey.startsWith("stock_") ? "stock" : moduleKey.startsWith("easytax_") ? "easytax" : "kmarket";
    const badge = document.getElementById(`badge-status-${brandPrefix}-${cleanKey}`);
    if (badge) {
        badge.className = "badge-idle";
        badge.style.background = "#F6F1EA";
        badge.style.color = "#6E665E";
        badge.style.border = "1px solid #E5DDD1";
        badge.innerHTML = "⚪ 대기";
    }

    try {
        const res = await fetch(`/api/channel/stop/${moduleKey}`, { method: "POST" });
        const data = await res.json();
        showToast(data.message || `[${moduleKey}] 무인 가동이 정지되었습니다.`, "info");
        appendLog(`[Daemon Stop] ${data.message || moduleKey}`, "warning");
        const startBtn = document.getElementById(`btn-start-${brandPrefix}-${cleanKey}`);
        if (startBtn) {
            startBtn.innerHTML = "🚀 무인 가동";
            startBtn.style.background = startBtn.getAttribute("data-original-bg") || "";
        }
        fetchStatus();
    } catch (e) {
        showToast("정지 요청 통신 오류", "error");
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `⏹️ 정지`;
        }
    }
}

// 4. 채널 뱃지 동기화
function updateChannelBadges(runningChannels) {
    if (!runningChannels) return;
    const modules = [
        "shorts", "cardnews", "reddit", "fb_groups", "blog", "seo", "threads",
        "naver_clip", "naver_blog", "tistory", "naver_post", "brunch", "search_advisor",
        "naver_kin", "naver_cafe", "daum_cafe", "ppomppu", "dcinside", "bobaedream",
        "nate_pann", "fmkorea", "kakao_channel"
    ];
    const brands = ["stock", "aura", "insurance", "kmarket", "easytax"];

    brands.forEach(b => {
        modules.forEach(m => {
            const key = `${b}_${m}`;
            const isRunning = !!runningChannels[key];
            const badge = document.getElementById(`badge-status-${b}-${m}`);
            const startBtn = document.getElementById(`btn-start-${b}-${m}`);

            if (badge) {
                if (isRunning) {
                    badge.className = "badge-running";
                    badge.style.background = "#DCFCE7";
                    badge.style.color = "#15803D";
                    badge.style.border = "1px solid #86EFAC";
                    badge.innerHTML = "🟢 실행 중 (24h)";
                } else {
                    badge.className = "badge-idle";
                    badge.style.background = "#F6F1EA";
                    badge.style.color = "#6E665E";
                    badge.style.border = "1px solid #E5DDD1";
                    badge.innerHTML = "⚪ 대기";
                }
            }

            if (startBtn) {
                if (isRunning) {
                    startBtn.innerHTML = `🔄 무인 가동 중 🟢`;
                    startBtn.style.background = "#059669";
                } else {
                    startBtn.innerHTML = "🚀 무인 가동";
                    startBtn.style.background = startBtn.getAttribute("data-original-bg") || "";
                }
            }
        });
    });
}

// 5. 사이드바 데몬 시작/정지 & 3대 슈퍼앱 마스터 제어
async function startStockDaemon() {
    try {
        const res = await fetch("/api/stock/start", { method: "POST" });
        const data = await res.json();
        showToast(data.message || "📈 Stock Master 주식 AI 무인 봇 사이클이 가동되었습니다! 🚀", "success");
        fetchStatus();
    } catch (e) {
        showToast("주식 AI 가동 통신 오류", "error");
    }
}

async function stopStockDaemon() {
    try {
        const res = await fetch("/api/stock/stop", { method: "POST" });
        const data = await res.json();
        showToast(data.message || "📈 Stock Master 주식 AI 봇이 정지되었습니다.", "info");
        fetchStatus();
    } catch (e) {
        showToast("주식 AI 정지 통신 오류", "error");
    }
}

async function startAuraDaemon() {
    try {
        const res = await fetch("/api/aura/start", { method: "POST" });
        const data = await res.json();
        showToast(data.message || "💖 Aura 데이팅 무인 봇 사이클이 가동되었습니다! 🚀", "success");
        fetchStatus();
    } catch (e) {
        showToast("Aura 가동 통신 오류", "error");
    }
}

async function stopAuraDaemon() {
    try {
        const res = await fetch("/api/aura/stop", { method: "POST" });
        const data = await res.json();
        showToast(data.message || "💖 Aura 데이팅 봇이 정지되었습니다.", "info");
        fetchStatus();
    } catch (e) {
        showToast("Aura 정지 통신 오류", "error");
    }
}

async function startInsuranceDaemon() {
    try {
        const res = await fetch("/api/insurance/start", { method: "POST" });
        const data = await res.json();
        showToast(data.message || "🛡️ InsureBalance 보험비교 무인 봇 사이클이 가동되었습니다! 🚀", "success");
        fetchStatus();
    } catch (e) {
        showToast("보험비교 가동 통신 오류", "error");
    }
}

async function stopInsuranceDaemon() {
    try {
        const res = await fetch("/api/insurance/stop", { method: "POST" });
        const data = await res.json();
        showToast(data.message || "🛡️ InsureBalance 보험비교 봇이 정지되었습니다.", "info");
        fetchStatus();
    } catch (e) {
        showToast("보험비교 정지 통신 오류", "error");
    }
}

async function startKMarketDaemon() {
    try {
        const res = await fetch("/api/kmarket/start", { method: "POST" });
        const data = await res.json();
        showToast(data.message || "KTRS 마켓 무인 성장봇 사이클이 가동되었습니다! 🚀", "success");
        fetchStatus();
    } catch (e) {
        showToast("KTRS 마켓 가동 통신 오류", "error");
    }
}

async function stopKMarketDaemon() {
    try {
        const res = await fetch("/api/kmarket/stop", { method: "POST" });
        const data = await res.json();
        showToast(data.message || "KTRS 마켓 봇이 정지되었습니다.", "info");
        fetchStatus();
    } catch (e) {
        showToast("KTRS 마켓 정지 통신 오류", "error");
    }
}

async function startEasyTaxDaemon() {
    try {
        const res = await fetch("/api/easytax/start", { method: "POST" });
        const data = await res.json();
        showToast(data.message || "EasyTax 세금환급 봇 사이클이 가동되었습니다! 💰", "success");
        fetchStatus();
    } catch (e) {
        showToast("EasyTax 가동 통신 오류", "error");
    }
}

async function stopEasyTaxDaemon() {
    try {
        const res = await fetch("/api/easytax/stop", { method: "POST" });
        const data = await res.json();
        showToast(data.message || "EasyTax 봇이 정지되었습니다.", "info");
        fetchStatus();
    } catch (e) {
        showToast("EasyTax 정지 통신 오류", "error");
    }
}

async function startAllBots() {
    showToast("⚡ 3대 슈퍼앱 전체 봇을 동시 가동합니다! 🚀", "success");
    await startStockDaemon();
    await startAuraDaemon();
    await startInsuranceDaemon();
    if (typeof loadTelegramCommunityStats === "function") loadTelegramCommunityStats();
}

async function stopAllBots() {
    showToast("🛑 모든 무인 봇을 정지합니다.", "warning");
    await stopStockDaemon();
    await stopAuraDaemon();
    await stopInsuranceDaemon();
    if (typeof loadTelegramCommunityStats === "function") loadTelegramCommunityStats();
}

// 6. 실시간 서버 상태 폴링 (3초 주기)
let lastSeenLogKeys = new Set();

async function fetchStatus() {
    try {
        const res = await fetch("/api/status");
        if (!res.ok) return;
        const data = await res.json();

        isStockRunning = data.stock_running || false;
        isAuraRunning = data.aura_running || false;
        isInsuranceRunning = data.insurance_running || false;
        isKMarketRunning = data.kmarket_running || false;
        isEasyTaxRunning = data.easytax_running || false;

        // 📈 Stock Master 사이드바 상태
        const stockStatusText = document.getElementById("stock-daemon-status-text");
        const stockSub = document.getElementById("stock-daemon-sub");
        if (stockStatusText) {
            stockStatusText.innerText = isStockRunning ? "📈 주식 AI 가동 중 🟢" : "📈 주식 AI 대기 중 ⚪";
            stockStatusText.style.color = isStockRunning ? "#34D399" : "#FACC15";
        }
        if (stockSub) {
            stockSub.innerText = isStockRunning ? "24시간 자동 분석/발행 중" : "실시간수급/장전브리핑/조건검색";
        }

        // 💖 Aura 사이드바 상태
        const auraStatusText = document.getElementById("aura-daemon-status-text");
        const auraSub = document.getElementById("aura-daemon-sub");
        if (auraStatusText) {
            auraStatusText.innerText = isAuraRunning ? "💖 Aura 데이팅 가동 중 🟢" : "💖 Aura 데이팅 대기 중 ⚪";
            auraStatusText.style.color = isAuraRunning ? "#34D399" : "#EC4899";
        }
        if (auraSub) {
            auraSub.innerText = isAuraRunning ? "24시간 자동 매칭/바이럴 중" : "소개팅첫만남/2030연애/클립";
        }

        // 🛡️ InsureBalance 사이드바 상태
        const insStatusText = document.getElementById("insurance-daemon-status-text");
        const insSub = document.getElementById("insurance-daemon-sub");
        if (insStatusText) {
            insStatusText.innerText = isInsuranceRunning ? "🛡️ 보험비교 가동 중 🟢" : "🛡️ 보험비교 대기 중 ⚪";
            insStatusText.style.color = isInsuranceRunning ? "#34D399" : "#10B981";
        }
        if (insSub) {
            insSub.innerText = isInsuranceRunning ? "24시간 보장 분석/리모델링 중" : "실손/3대질병/호갱탈출";
        }

        // 22대 허브 실시간 뱃지 동기화
        updateChannelBadges(data.running_channels);
        if (data.golden_targets) {
            updateGoldenTargetIndicators(data.golden_targets);
        }
        if (data.golden_batch_summary) {
            updateGoldenBatchPanel(data.golden_batch_summary);
        }

        // 상단 지표 (현재 브랜드 전용 1:1 완벽 분리)
        const brand = currentBrand || "stock";
        const totalEl = document.getElementById("stat-total-count");
        const topScoreEl = document.getElementById("stat-top-score");
        const seoCountEl = document.getElementById("stat-seo-count");
        const googleCountEl = document.getElementById("google-index-count");

        if (totalEl) {
            if (brand === "stock") totalEl.innerText = `${data.stock_history_count || 0} 건`;
            else if (brand === "aura") totalEl.innerText = `${data.aura_history_count || 0} 건`;
            else if (brand === "insurance") totalEl.innerText = `${data.insurance_history_count || 0} 건`;
            else totalEl.innerText = `${data.total_history_count || 0} 건`;
        }
        if (topScoreEl) {
            topScoreEl.innerText = `${data.top_score || 0.0} 점`;
        }
        if (seoCountEl) {
            const bLabel = brand === "stock" ? "Stock AI" : brand === "aura" ? "Aura" : "InsureBalance";
            seoCountEl.innerText = `22개 채널 (${bLabel})`;
        }
        if (googleCountEl) {
            googleCountEl.innerText = `22개 채널 연결됨`;
        }

        // 최신 로그 콘솔 (중복 방지: 새 로그만 딱 1번 출력)
        if (data.recent_logs && data.recent_logs.length > 0) {
            data.recent_logs.forEach(msg => {
                const logKey = `${msg.id || msg.timestamp || msg.time || ''}_${msg.text}`;
                if (!lastSeenLogKeys.has(logKey)) {
                    lastSeenLogKeys.add(logKey);
                    appendLog(msg.text, msg.type);
                }
            });
            if (lastSeenLogKeys.size > 150) {
                lastSeenLogKeys = new Set(Array.from(lastSeenLogKeys).slice(-50));
            }
        }
    } catch (e) {
        console.error("Status fetch error:", e);
    }
}

// 7. 모듈 1회성 실행
async function runModule(moduleName) {
    appendLog(`[Action] ${moduleName} 모듈 즉시 실행 요청...`, "info");
    showToast(`${moduleName} 모듈이 백그라운드에서 실행됩니다.`);
    try {
        const res = await fetch(`/api/run-module/${moduleName}`, { method: "POST" });
        const data = await res.json();
        if (data.success) {
            appendLog(`[Success] ${data.message}`, "success");
            showToast(data.message);
            fetchStatus();
        } else {
            appendLog(`[Error] ${data.message}`, "error");
        }
    } catch (e) {
        appendLog(`[Error] 모듈 실행 통신 실패: ${e}`, "error");
    }
}

// 8. 구글 실시간 색인 핑
async function triggerGoogleIndex() {
    const endpoint = currentBrand === "easytax" ? "/api/easytax/google-index" : "/api/kmarket/google-index";
    const brandName = currentBrand === "easytax" ? "EasyTax" : "KTRS 마켓";
    appendLog(`[Google Indexing] Googlebot에게 ${brandName} 6,630개 URL 색인 핑 전송 중...`, "info");
    showToast(`구글 봇에게 [${brandName}] 실시간 색인 핑을 전송합니다...`);

    try {
        const res = await fetch(endpoint, { method: "POST" });
        const data = await res.json();
        if (data.success) {
            appendLog(`[Success] ${data.message}`, "success");
            showToast(data.message, "success");
        } else {
            appendLog(`[Error] ${data.message}`, "error");
        }
    } catch (e) {
        appendLog(`[Error] 구글 색인 요청 통신 실패: ${e}`, "error");
    }
}

// 9. 비주얼 미디어 엔진 관리
async function setMediaEngine(channelKey, engineMode = "wan") {
    appendLog(`[Engine] ${channelKey} 비주얼 엔진 준비 완료`, "info");
}

async function loadMediaEngineSettings() {
}

function updateMediaEngineUI(settings = {}, stats = {}) {
}

function refreshOverview(btn) {
    animateRefreshBtn(btn, "대시보드 활동 로그와 상태가 새로고침되었습니다! 📊");
    fetchStatus();
    renderHubGrid();
    loadMediaEngineSettings();
}

// 🌟 10. 8대 황금 타깃 국가 1일 2슬롯 풀가동 제어 모듈
let lastGoldenBatchSummary = null;

// 🚀 [원클릭 즉시 제작] 대시보드 버튼 하나로 즉시 카드뉴스/숏폼 생산 및 바탕화면 출력
async function triggerOneClickProduce(brand, mode, btnElement = null) {
    const brandNames = {
        stock: "Stock Master (주식 AI)",
        aura: "Aura (AI 데이팅)",
        insurance: "InsureBalance (보험비교)",
        easytax: "EasyTax (세금 환급)",
        kmarket: "K-Market (생활 커뮤니티)"
    };
    const brandName = brandNames[brand] || brand;
    const modeName = mode === "shorts" ? "완성 숏폼" : "4장 카드뉴스";
    const langSelect = document.getElementById(`select-lang-${brand}-${mode}`);
    const lang = langSelect ? langSelect.value : "ko";
    const amountSelect = document.getElementById(`select-amount-${brand}-${mode}`);
    const amount = amountSelect ? amountSelect.value : "random";
    
    appendLog(`[Action] 🚀 [${brandName}] ${modeName} 원클릭 즉시 제작 요청...`, "info");
    showToast(`🚀 [${brandName}] ${modeName} 제작을 시작합니다!`, "info");

    const originalText = btnElement ? btnElement.innerHTML : "";
    if (btnElement) {
        btnElement.disabled = true;
        btnElement.style.opacity = "0.7";
        btnElement.innerHTML = `<span>⏳</span> 제작 진행 중...`;
    }

    try {
        const res = await fetch("/api/factory/run", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                brand: brand,
                mode: mode,
                lang: lang,
                amount: amount
            })
        });
        const data = await res.json();
        if (data.success) {
            appendLog(`[Success] 🎉 ${data.message}`, "success");
            showToast(`🎉 제작이 시작되었습니다. 완성 후 바탕화면에 저장됩니다.`, "success");
        } else {
            appendLog(`[Error] ⚠️ ${data.message}`, "error");
            showToast(data.message, "error");
        }
    } catch (e) {
        appendLog(`[Error] ❌ 팩토리 통신 오류: ${e}`, "error");
        showToast("팩토리 통신 오류", "error");
    } finally {
        setTimeout(() => {
            if (btnElement) {
                btnElement.disabled = false;
                btnElement.style.opacity = "1";
                btnElement.innerHTML = originalText;
            }
            fetchStatus();
        }, 3000);
    }
}

async function triggerGoldenBatchRun(contentType = 'all', btnElement = null) {
    const brand = currentBrand || 'kmarket';
    const brandName = brand === 'easytax' ? 'EasyTax (세무)' : 'KTRS 마켓 (쇼핑)';
    const typeLabel = contentType === 'shorts' ? '숏폼 8편' : contentType === 'cardnews' ? '5장 카드뉴스 8세트' : '숏폼 8편 + 카드뉴스 8세트 (총 16건)';
    
    appendLog(`[Action] 🌟 [${brandName}] 8대 황금 타깃 국가 ${typeLabel} 일괄 즉시 생산 가동...`, "info");
    showToast(`🌟 [${brandName}] 8대 황금 타깃 ${typeLabel} 대량 생산을 시작합니다!`, "success");

    const btn = btnElement || document.getElementById(`btn-run-gb-${brand}-${contentType}`);
    const originalText = btn ? btn.innerHTML : "";
    if (btn) {
        btn.disabled = true;
        btn.style.opacity = "0.7";
        btn.innerHTML = `<span>⏳</span> 8대 국가 대량 생산 중... (바탕화면 실시간 저장)`;
    }

    try {
        const res = await fetch("/api/golden-batch/run", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ brand: brand, type: contentType, slot_name: "manual" })
        });
        const data = await res.json();
        if (data.success) {
            appendLog(`[Success] 🎉 ${data.message}`, "success");
            showToast(data.message, "success");
        } else {
            appendLog(`[Error] ⚠️ ${data.message}`, "error");
        }
    } catch (e) {
        appendLog(`[Error] ❌ 골든 배치 통신 오류: ${e}`, "error");
        showToast("골든 배치 통신 오류", "error");
    } finally {
        setTimeout(() => {
            if (btn) {
                btn.disabled = false;
                btn.style.opacity = "1";
                btn.innerHTML = originalText;
                updateGoldenBatchPanel();
            }
            fetchStatus();
        }, 3000);
    }
}

async function startGoldenBatchDaemon() {
    const brand = currentBrand || 'kmarket';
    const brandName = brand === 'easytax' ? 'EasyTax (세무)' : 'KTRS 마켓 (쇼핑)';
    appendLog(`[Daemon] ⏰ [${brandName}] 8대 황금 타깃 24시간 무인 데몬 시작 요청 (11:30 & 18:30)...`, "info");
    showToast(`⏰ [${brandName}] 24시간 무인 예약 데몬이 가동됩니다!`, "success");

    try {
        const res = await fetch("/api/golden-batch/daemon/start", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ brand: brand })
        });
        const data = await res.json();
        if (data.success) {
            appendLog(`[Success] 🟢 ${data.message}`, "success");
            showToast(data.message, "success");
            fetchStatus();
        }
    } catch (e) {
        appendLog(`[Error] ❌ 데몬 시작 통신 오류: ${e}`, "error");
    }
}

async function stopGoldenBatchDaemon() {
    const brand = currentBrand || 'kmarket';
    const brandName = brand === 'easytax' ? 'EasyTax (세무)' : 'KTRS 마켓 (쇼핑)';
    appendLog(`[Daemon] ⏹️ [${brandName}] 8대 황금 타깃 무인 데몬 정지 요청...`, "info");
    showToast(`⏹️ [${brandName}] 무인 데몬이 정지되었습니다.`, "info");

    try {
        const res = await fetch("/api/golden-batch/daemon/stop", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ brand: brand })
        });
        const data = await res.json();
        if (data.success) {
            appendLog(`[Info] ⚪ ${data.message}`, "info");
            showToast(data.message, "info");
            fetchStatus();
        }
    } catch (e) {
        appendLog(`[Error] ❌ 데몬 정지 통신 오류: ${e}`, "error");
    }
}

function updateGoldenBatchPanel(summary) {
    if (summary) lastGoldenBatchSummary = summary;
    const currentSummary = summary || lastGoldenBatchSummary;
    const brand = currentBrand || 'kmarket';

    if (currentSummary) {
        const totalS = currentSummary.total_shorts || 0;
        const totalC = currentSummary.total_cardnews || 0;
        
        const counterShorts = document.getElementById(`golden-counter-${brand}-shorts`);
        const counterCardnews = document.getElementById(`golden-counter-${brand}-cardnews`);
        if (counterShorts) counterShorts.innerText = `오늘 실적: ${totalS} / 16편`;
        if (counterCardnews) counterCardnews.innerText = `오늘 실적: ${totalC} / 16세트 (${totalC * 5}장)`;

        const daemonRunning = currentSummary.daemon_running ? (currentSummary.daemon_running[brand] || currentSummary.daemon_running['all']) : false;
        const badgeShorts = document.getElementById(`badge-status-${brand}-shorts`);
        const badgeCardnews = document.getElementById(`badge-status-${brand}-cardnews`);
        const btnDaemonShorts = document.getElementById(`btn-daemon-gb-${brand}-shorts`);
        const btnDaemonCardnews = document.getElementById(`btn-daemon-gb-${brand}-cardnews`);
        
        if (daemonRunning) {
            if (badgeShorts) {
                badgeShorts.innerHTML = "🟢 1일 2슬롯 무인 가동 중";
                badgeShorts.style.color = "#34D399";
                badgeShorts.style.background = "rgba(16,185,129,0.15)";
            }
            if (badgeCardnews) {
                badgeCardnews.innerHTML = "🟢 1일 2슬롯 무인 가동 중";
                badgeCardnews.style.color = "#34D399";
                badgeCardnews.style.background = "rgba(16,185,129,0.15)";
            }
            if (btnDaemonShorts) {
                btnDaemonShorts.innerHTML = "🔄 24h 가동 중 🟢";
                btnDaemonShorts.style.background = "#059669";
            }
            if (btnDaemonCardnews) {
                btnDaemonCardnews.innerHTML = "🔄 24h 가동 중 🟢";
                btnDaemonCardnews.style.background = "#059669";
            }
        } else {
            if (btnDaemonShorts) {
                btnDaemonShorts.innerHTML = "🚀 무인 가동";
                btnDaemonShorts.style.background = "linear-gradient(135deg, #10B981, #059669)";
            }
            if (btnDaemonCardnews) {
                btnDaemonCardnews.innerHTML = "🚀 무인 가동";
                btnDaemonCardnews.style.background = "linear-gradient(135deg, #10B981, #059669)";
            }
        }
    }
}

window.renderHubGrid = renderHubGrid;
// 🚀 4대 옴니블로그 원클릭 즉시 발행 함수 (BAT 파일 대체)
async function publishOmniBlog(brand) {
    const btnId = `btn-omni-${brand}`;
    const btn = document.getElementById(btnId);
    const originalHtml = btn ? btn.innerHTML : "";

    const nameMap = {
        aura: "💖 Aura 데이팅",
        insurance: "🛡️ InsureBalance 보험비교",
        stock: "📈 Stock Master 주식AI",
        all: "⚡ 3대 슈퍼앱 전체"
    };
    const brandName = nameMap[brand] || brand;

    if (btn) {
        btn.disabled = true;
        btn.style.opacity = "0.7";
        btn.innerHTML = `<span>⏳ ${brandName} 발행 중...</span>`;
    }

    appendLog(`[Action] ${brandName} 4대 옴니블로그 1회 즉시 발행 시작... (Gemini 2,000자 + 16:9 사진 생성)`, "info");
    showToast(`🚀 ${brandName} 옴니블로그 1회 즉시 발행이 시작되었습니다!`, "info");

    try {
        if (brand === "all") {
            // 3대 브랜드 순차 백그라운드 트리거
            const resA = await fetch("/api/omni-blog/publish/aura", { method: "POST" });
            const resI = await fetch("/api/omni-blog/publish/insurance", { method: "POST" });
            const resS = await fetch("/api/omni-blog/publish/stock", { method: "POST" });
            const data = await resA.json();
            appendLog(`[Success] 3대 슈퍼앱 전체 옴니블로그 1회 발행 작업이 가동되었습니다.`, "success");
            showToast("🎉 3대 앱 옴니블로그 발행이 백그라운드에서 진행 중입니다!", "success");
        } else {
            const res = await fetch(`/api/omni-blog/publish/${brand}`, { method: "POST" });
            const data = await res.json();
            if (data.success) {
                appendLog(`[Success] ${data.message}`, "success");
                showToast(data.message, "success");
            } else {
                appendLog(`[Error] 발행 실패: ${data.message}`, "error");
                showToast(`발행 실패: ${data.message}`, "error");
            }
        }
        if (typeof fetchStatus === "function") fetchStatus();
    } catch (e) {
        appendLog(`[Error] 옴니블로그 통신 실패: ${e}`, "error");
        showToast("서버 통신 실패", "error");
    } finally {
        setTimeout(() => {
            if (btn) {
                btn.disabled = false;
                btn.style.opacity = "1";
                btn.innerHTML = originalHtml;
            }
        }, 3000);
    }
}

window.publishOmniBlog = publishOmniBlog;
window.renderActionGrid = renderHubGrid;
window.startChannelDaemon = startChannelDaemon;
window.stopChannelDaemon = stopChannelDaemon;
window.startStockDaemon = startStockDaemon;
window.stopStockDaemon = stopStockDaemon;
window.startAuraDaemon = startAuraDaemon;
window.stopAuraDaemon = stopAuraDaemon;
window.startInsuranceDaemon = startInsuranceDaemon;
window.stopInsuranceDaemon = stopInsuranceDaemon;
window.startKMarketDaemon = startKMarketDaemon;
window.stopKMarketDaemon = stopKMarketDaemon;
window.startEasyTaxDaemon = startEasyTaxDaemon;
window.stopEasyTaxDaemon = stopEasyTaxDaemon;
window.startAllBots = startAllBots;
window.stopAllBots = stopAllBots;
window.fetchStatus = fetchStatus;
window.runModule = runModule;
window.triggerGoogleIndex = triggerGoogleIndex;
window.refreshOverview = refreshOverview;
window.setMediaEngine = setMediaEngine;
window.loadMediaEngineSettings = loadMediaEngineSettings;
window.triggerGoldenBatchRun = triggerGoldenBatchRun;
window.startGoldenBatchDaemon = startGoldenBatchDaemon;
window.stopGoldenBatchDaemon = stopGoldenBatchDaemon;
window.updateGoldenBatchPanel = updateGoldenBatchPanel;

// 초기화 시 엔진 상태 로드
document.addEventListener("DOMContentLoaded", () => {
    setTimeout(loadMediaEngineSettings, 200);
    setTimeout(() => {
        if (typeof updateGoldenBatchPanel === "function") updateGoldenBatchPanel();
    }, 250);
});


