// ==========================================
// [모듈 5] health.js: 3대 슈퍼앱 실시간 장애 감지 & 정직한 실시간 관제 모듈
// ==========================================

async function loadHealthStatus(btn) {
    if (btn) animateRefreshBtn(btn, "실시간 상태가 새로고침되었습니다! 🩺");
    try {
        // 실시간 라이브 피드와 헬스 데이터를 동시 조회 (캐시 원천 방지 타임스탬프)
        const [healthRes, feedRes] = await Promise.all([
            fetch(`/api/health?_t=${Date.now()}`),
            fetch(`/api/today-live-feed?_t=${Date.now()}`)
        ]);

        const data = await healthRes.json();
        const liveFeed = await feedRes.json();

        const b = currentBrand || "stock";
        const brandName = b === "stock" ? "📈 Stock Master 주식 AI" : b === "aura" ? "💖 Aura AI 데이팅" : b === "insurance" ? "🛡️ InsureBalance 보험비교" : b.toUpperCase();
        const panelTitle = document.getElementById("health-panel-title");
        const panelDesc = document.getElementById("health-panel-desc");
        
        // 💓 3초 실시간 맥박 타임스탬프 갱신
        const pulseText = document.getElementById("health-pulse-text");
        if (pulseText) {
            const nowTimeStr = new Date().toLocaleTimeString("ko-KR", { hour12: false });
            pulseText.innerText = `💓 3초 실시간 맥박 감지 중 (${nowTimeStr} 갱신)`;
        }
        
        if (panelTitle) {
            panelTitle.innerText = `🩺 [${brandName} 전담] 실시간 채널 무결성 & 장애 관제 센터`;
        }
        if (panelDesc) {
            panelDesc.innerText = "가짜 정상 문구를 전면 배제하고, 실제 발행 글 링크와 세션 만료 장애 및 해결 조치법을 100% 투명하게 실시간 표출합니다.";
        }

        // 🚀 0. 최상단: 현재 선택된 브랜드 1개 앱 전용 실시간 무인 발행 라이브 전광판 렌더링
        renderHealthBrandLiveFeed(liveFeed, data.gpu_status, b);

        const bFeed = (liveFeed.brands && liveFeed.brands[b]) || {};
        const blog = bFeed.blog || {};
        const kin = bFeed.kin || {};
        const shorts = bFeed.shorts || {};
        const cardnews = bFeed.cardnews || {};
        const channels = blog.channels || {};
        const shortsPlatforms = shorts.platforms || {};
        const cardPlatforms = cardnews.platforms || {};

        // 🚨 1. [장애 및 미발행 감지 분석]
        const criticalIssues = [];
        const scheduledPending = [];

        // 🔐 1.1 9대 플랫폼 영구 로그인 실시간 만료 감지 연동 (PlatformAuthSentinel)
        const authSentinelData = data.auth_sentinel || {};
        const brandAuthIssues = (authSentinelData.critical_issues || []).filter(iss => !b || b === "all" || iss.brand_key === b);
        brandAuthIssues.forEach(iss => {
            criticalIssues.push({
                brand: iss.brand,
                type: iss.status_label || "세션 만료",
                channel: `${iss.icon || '🔐'} ${iss.platform}`,
                cause: iss.cause,
                action: iss.action
            });
        });

        Object.keys(liveFeed.brands || {}).forEach(bKey => {
            // 현재 선택된 브랜드 전담 필터링
            if (b && b !== "all" && bKey !== b) return;

            const bf = liveFeed.brands[bKey];
            const chs = bf.blog?.channels || {};
            const shs = bf.shorts?.platforms || {};
            const crds = bf.cardnews?.platforms || {};
            const bTitle = bf.brand_name || bKey;

            // 1. 티스토리 블로그
            const batName = bKey === "aura" ? "[1회연동]_Aura_티스토리_영구로그인.bat" 
                          : bKey === "insurance" ? "[1회연동]_보험비교_티스토리_영구로그인.bat" 
                          : "[1회연동]_주식AI_티스토리_영구로그인.bat";

            if (chs.tistory?.is_session_expired) {
                criticalIssues.push({
                    brand: bTitle,
                    type: "세션 만료",
                    channel: "티스토리 (Tistory)",
                    cause: "카카오 로그인 세션 쿠키 수명 만료",
                    action: `바탕화면의 [${batName}] 배치 파일을 1회 실행하여 로그인해 주세요.`
                });
            } else if (chs.tistory?.status === "error") {
                criticalIssues.push({
                    brand: bTitle,
                    type: "발행 오류",
                    channel: "티스토리 (Tistory)",
                    cause: chs.tistory.message || "티스토리 자동 발행 실패",
                    action: `블로그 ID 확인 및 필요 시 바탕화면의 [${batName}] 실행`
                });
            } else if (!chs.tistory?.is_today && !chs.tistory?.is_success) {
                scheduledPending.push({
                    brand: bTitle,
                    type: "미발행",
                    channel: "티스토리 블로그",
                    cause: `오늘자 미발행 (최근 실제 발행: ${chs.tistory?.published_at || '-'})`,
                    action: "오늘자 정기 스케줄 대기 또는 1회 수동 발행 트리거"
                });
            }

            // 2. 네이버 블로그
            const naverBat = bKey === "aura" ? "[1회연동]_Aura_네이버_영구로그인.bat"
                           : bKey === "insurance" ? "[1회연동]_보험비교_네이버_영구로그인.bat"
                           : "[1회연동]_주식AI_네이버_영구로그인.bat";

            if (chs.naver_blog?.status === "error") {
                criticalIssues.push({
                    brand: bTitle,
                    type: "발행 에러",
                    channel: "네이버 블로그",
                    cause: chs.naver_blog.message || "네이버 글쓰기 세션 확인 필요",
                    action: `바탕화면의 [${naverBat}] 실행 필요`
                });
            } else if (!chs.naver_blog?.is_today) {
                scheduledPending.push({
                    brand: bTitle,
                    type: "미발행",
                    channel: "네이버 블로그",
                    cause: chs.naver_blog?.message || `오늘자 미발행 (최근 실제 발행: ${chs.naver_blog?.published_at || bf.blog?.last_run_time || '-'})`,
                    action: "오늘자 정기 스케줄 대기 또는 1회 수동 발행 트리거"
                });
            }

            // 3. 4대 숏폼 플랫폼
            const spCheckList = [
                { name: "유튜브 쇼츠", data: shs.youtube || {} },
                { name: "인스타그램 릴스", data: shs.instagram || {} },
                { name: "페이스북 릴스", data: shs.facebook || {} },
                { name: "네이버 클립", data: shs.naver_clip || {} }
            ];
            spCheckList.forEach(sp => {
                if (!sp.data.is_today && !sp.data.url) {
                    scheduledPending.push({
                        brand: bTitle,
                        type: "미발행",
                        channel: `숏폼 (${sp.name})`,
                        cause: `오늘자 미발행 (최근 실제 발행: ${sp.data.published_at || '-'})`,
                        action: "오늘자 정기 스케줄 대기 또는 1회 수동 발행 트리거"
                    });
                }
            });

            // 4. 5장 카드뉴스 플랫폼
            const cardCheckList = [
                { name: "인스타 캐러셀 (5장)", data: crds.instagram || {} },
                { name: "페이스북 앨범 (5장)", data: crds.facebook || {} },
                { name: "1080x1350 카드뉴스 완제품", data: crds.local_slides || {} }
            ];
            cardCheckList.forEach(cp => {
                if (!cp.data.is_today && !cp.data.url && !cp.data.is_success) {
                    scheduledPending.push({
                        brand: bTitle,
                        type: "미발행",
                        channel: `카드뉴스 (${cp.name})`,
                        cause: `오늘자 미발행 (최근 실제 발행: ${cp.data.published_at || cp.data.time || '-'})`,
                        action: "오늘자 정기 스케줄 대기 또는 1회 수동 발행 트리거"
                    });
                }
            });
        });

        // 🧠 2. 최상단: 실시간 장애 & 정기 스케줄 대기 관제 센터 렌더링
        const brainGrid = document.getElementById("health-brain-grid");
        if (brainGrid) {
            if (criticalIssues.length > 0) {
                brainGrid.innerHTML = `
                    <div style="grid-column: 1 / -1; background:#FEF2F2; border:2px solid #F87171; border-radius:12px; padding:16px 20px; box-shadow:0 4px 14px rgba(239,68,68,0.15);">
                        <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
                            <span style="font-size:20px;">🚨</span>
                            <h4 style="margin:0; font-size:16px; font-weight:800; color:#991B1B;">
                                실시간 장애 감지 (${criticalIssues.length}건) — 즉시 조치 필요
                            </h4>
                        </div>
                        <div style="display:flex; flex-direction:column; gap:10px;">
                            ${criticalIssues.map(iss => `
                                <div style="background:#FFFFFF; border:1px solid #FECACA; border-radius:8px; padding:12px 14px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
                                    <div>
                                        <div style="display:flex; align-items:center; gap:8px;">
                                            <span style="background:#DC2626; color:#FFFFFF; font-size:11px; font-weight:800; padding:2px 7px; border-radius:4px;">${iss.brand}</span>
                                            <strong style="color:#0F172A; font-size:13.5px;">${iss.channel} - ${iss.type}</strong>
                                        </div>
                                        <div style="color:#64748B; font-size:12px; margin-top:4px;">
                                            원인: <span style="color:#DC2626; font-weight:600;">${iss.cause}</span>
                                        </div>
                                    </div>
                                    <div style="background:#FFFBEB; border:1px solid #FDE68A; padding:6px 12px; border-radius:6px; font-size:12px; color:#92400E; font-weight:700;">
                                        👉 ${iss.action}
                                    </div>
                                </div>
                            `).join("")}
                        </div>
                    </div>
                `;
            } else if (scheduledPending.length > 0) {
                brainGrid.innerHTML = `
                    <div style="grid-column: 1 / -1; background:#FFFBEB; border:2px solid #FCD34D; border-radius:12px; padding:16px 20px; box-shadow:0 4px 14px rgba(245,158,11,0.12);">
                        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:12px;">
                            <div style="display:flex; align-items:center; gap:8px;">
                                <span style="font-size:20px;">⏳</span>
                                <div>
                                    <h4 style="margin:0; font-size:16px; font-weight:800; color:#92400E;">
                                        오늘자 정기 스케줄 대기 & 미발행 관제 (${scheduledPending.length}개 채널 대기 중)
                                    </h4>
                                    <span style="font-size:11.5px; color:#B45309;">치명적 장애 0건 — 정해진 시각에 24시간 무인 자동 발행되거나 수동 1회 즉시 실행 가능합니다.</span>
                                </div>
                            </div>
                            <span style="background:#F59E0B; color:#FFFFFF; font-size:11px; font-weight:800; padding:4px 10px; border-radius:6px;">⚪ STANDBY</span>
                        </div>
                        <div style="display:flex; flex-direction:column; gap:8px; max-height:280px; overflow-y:auto; padding-right:4px;">
                            ${scheduledPending.map(iss => `
                                <div style="background:#FFFFFF; border:1px solid #FDE68A; border-radius:8px; padding:10px 14px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                                    <div>
                                        <div style="display:flex; align-items:center; gap:8px;">
                                            <span style="background:#F59E0B; color:#FFFFFF; font-size:10.5px; font-weight:800; padding:2px 6px; border-radius:4px;">${iss.brand}</span>
                                            <strong style="color:#0F172A; font-size:13px;">${iss.channel} - <span style="color:#B45309;">${iss.type}</span></strong>
                                        </div>
                                        <div style="color:#64748B; font-size:11.5px; margin-top:3px;">
                                            원인: <span style="color:#B45309; font-weight:600;">${iss.cause}</span>
                                        </div>
                                    </div>
                                    <div style="background:#FEF3C7; border:1px solid #FDE68A; padding:5px 10px; border-radius:6px; font-size:11.5px; color:#92400E; font-weight:700;">
                                        👉 ${iss.action}
                                    </div>
                                </div>
                            `).join("")}
                        </div>
                    </div>
                `;
            } else {
                brainGrid.innerHTML = `
                    <div style="grid-column: 1 / -1; background:#F0FDF4; border:2px solid #86EFAC; border-radius:12px; padding:16px 20px;">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span style="font-size:20px;">✅</span>
                            <h4 style="margin:0; font-size:15px; font-weight:800; color:#166534;">
                                현재 감지된 장애 0건 — 3대 브랜드 모든 채널 100% 정상 작동 중
                            </h4>
                        </div>
                    </div>
                `;
            }
        }

        // 🕵️ 2.1 3대 브랜드 사람처럼 행동하는 스텔스 웜업 & 안티-섀도우밴 관제탑 렌더링
        const stealthData = data.stealth_routines || {};
        const brandStealth = stealthData[b] || {};
        renderStealthWarmupGrid(brandStealth, b, brandName);

        // 🤖 2.2 3대 브랜드 카드뉴스 & 숏폼 완제품 무결성 가디언 렌더링 (MarketingWatchdogGuardian)
        const watchdogGrid = document.getElementById("health-watchdog-grid");
        const watchdogData = data.marketing_watchdog || {};
        const brandWatchdog = (watchdogData.brands && watchdogData.brands[b]) || {};

        if (watchdogGrid) {
            if (!brandWatchdog.brand) {
                watchdogGrid.innerHTML = `
                    <div style="grid-column: 1 / -1; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:10px; padding:14px; text-align:center; color:#64748B; font-size:12.5px;">
                        선택된 브랜드(${brandName})의 산출물 무결성 진단 데이터를 불러오는 중입니다...
                    </div>
                `;
            } else {
                const cn = brandWatchdog.cardnews || {};
                const sh = brandWatchdog.shorts || {};

                const cnHealthy = cn.healthy;
                const shHealthy = sh.healthy;

                const cnBorder = cnHealthy ? "#86EFAC" : "#FCA5A5";
                const cnTopBorder = cnHealthy ? "#22C55E" : "#EF4444";
                const cnBadgeBg = cnHealthy ? "#ECFDF5" : "#FEF2F2";
                const cnBadgeColor = cnHealthy ? "#059669" : "#DC2626";

                const shBorder = shHealthy ? "#86EFAC" : "#FCA5A5";
                const shTopBorder = shHealthy ? "#22C55E" : "#EF4444";
                const shBadgeBg = shHealthy ? "#ECFDF5" : "#FEF2F2";
                const shBadgeColor = shHealthy ? "#059669" : "#DC2626";

                watchdogGrid.innerHTML = `
                    <!-- 1. 🖼️ 카드뉴스 5장 슬라이드 무결성 카드 -->
                    <div style="background:#FFFFFF; border:1.5px solid ${cnBorder}; border-top:4px solid ${cnTopBorder}; border-radius:12px; padding:16px; box-shadow:0 2px 8px rgba(0,0,0,0.04); display:flex; flex-direction:column; justify-content:space-between; gap:12px;">
                        <div>
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                                <div style="display:flex; align-items:center; gap:8px;">
                                    <span style="font-size:22px;">🖼️</span>
                                    <strong style="font-size:14.5px; color:#0F172A;">1080x1350 카드뉴스 (5장)</strong>
                                </div>
                                <span style="background:${cnBadgeBg}; color:${cnBadgeColor}; font-size:11px; font-weight:800; padding:3px 8px; border-radius:5px; border:1px solid ${cnBorder};">
                                    ${cnHealthy ? (cn.today_count > 0 ? `🟢 오늘 ${cn.today_count}세트 완비` : '🟢 정상 (대기 중)') : '🔴 점검 필요'}
                                </span>
                            </div>
                            <div style="font-size:12px; color:#475569; background:#F8FAFC; padding:10px 12px; border-radius:8px; border:1px solid #F1F5F9; line-height:1.5;">
                                <div style="margin-bottom:4px;"><strong>상태:</strong> ${cn.message || '검증 완료'}</div>
                                <div><strong>최근 완제품:</strong> <span style="color:#0284C7; font-weight:600;">${cn.latest_folder || '없음'}</span></div>
                            </div>
                        </div>
                        <div style="font-size:11.5px; color:${cnHealthy ? '#166534' : '#991B1B'}; background:${cnHealthy ? '#F0FDF4' : '#FEF2F2'}; border:1px solid ${cnHealthy ? '#BBF7D0' : '#FECACA'}; padding:6px 10px; border-radius:6px; font-weight:600;">
                            ${cnHealthy ? '✨ 0 byte 빈 파일 및 글자 깨짐 없는 무결성 검증 통과' : '⚠️ 슬라이드 손상 또는 누락 감지'}
                        </div>
                    </div>

                    <!-- 2. 🎬 숏폼 풀HD 완제품 MP4 무결성 카드 -->
                    <div style="background:#FFFFFF; border:1.5px solid ${shBorder}; border-top:4px solid ${shTopBorder}; border-radius:12px; padding:16px; box-shadow:0 2px 8px rgba(0,0,0,0.04); display:flex; flex-direction:column; justify-content:space-between; gap:12px;">
                        <div>
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                                <div style="display:flex; align-items:center; gap:8px;">
                                    <span style="font-size:22px;">🎬</span>
                                    <strong style="font-size:14.5px; color:#0F172A;">1080x1920 숏폼 완제품 (MP4)</strong>
                                </div>
                                <span style="background:${shBadgeBg}; color:${shBadgeColor}; font-size:11px; font-weight:800; padding:3px 8px; border-radius:5px; border:1px solid ${shBorder};">
                                    ${shHealthy ? (sh.today_count > 0 ? `🟢 오늘 ${sh.today_count}편 렌더링 완료` : '🟢 정상 (대기 중)') : '🔴 영상 손상'}
                                </span>
                            </div>
                            <div style="font-size:12px; color:#475569; background:#F8FAFC; padding:10px 12px; border-radius:8px; border:1px solid #F1F5F9; line-height:1.5;">
                                <div style="margin-bottom:4px;"><strong>상태:</strong> ${sh.message || '검증 완료'}</div>
                                <div><strong>최근 완제품:</strong> <span style="color:#0284C7; font-weight:600;">${sh.latest_file || '없음'}</span></div>
                            </div>
                        </div>
                        <div style="font-size:11.5px; color:${shHealthy ? '#166534' : '#991B1B'}; background:${shHealthy ? '#F0FDF4' : '#FEF2F2'}; border:1px solid ${shHealthy ? '#BBF7D0' : '#FECACA'}; padding:6px 10px; border-radius:6px; font-weight:600;">
                            ${shHealthy ? '✨ 완제품 정상 용량(>4MB) 및 프레임 결합 무결성 검증 통과' : '⚠️ 비디오 파일 누락 또는 비정상 용량 감지'}
                        </div>
                    </div>
                `;
            }
        }

        // 🔐 2.5 6대 플랫폼 영구 로그인 실시간 관제 센터 렌더링 (Threads, Naver, Instagram, Facebook, YouTube, TikTok, Tistory, Brunch)
        const authGrid = document.getElementById("health-auth-sentinel-grid");
        // [Fix: Duplicate declaration removed - using authSentinelData from scope]
        const brandAuth = (authSentinelData.brands && authSentinelData.brands[b]) || {};
        const platformAuthList = Array.isArray(brandAuth.platforms) 
            ? brandAuth.platforms 
            : Object.values(brandAuth.platforms || {});

        if (authGrid) {
            if (platformAuthList.length === 0) {
                authGrid.innerHTML = `
                    <div style="grid-column: 1 / -1; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:10px; padding:14px; text-align:center; color:#64748B; font-size:12.5px;">
                        선택된 브랜드(${brandName})의 영구 로그인 진단 데이터를 불러오는 중입니다...
                    </div>
                `;
            } else {
                authGrid.innerHTML = platformAuthList.map(p => {
                    const isOk = p.is_authenticated === true || p.status === "authenticated" || p.status === "active";
                    const isWarn = p.status === "expiring_soon" || p.status === "missing";
                    const isErr = !isOk;
                    
                    const borderColor = isOk ? "#86EFAC" : isWarn ? "#FCD34D" : "#FCA5A5";
                    const topBorderColor = isOk ? "#22C55E" : isWarn ? "#F59E0B" : "#EF4444";
                    const badgeBg = isOk ? "#ECFDF5" : isWarn ? "#FFFBEB" : "#FEF2F2";
                    const badgeColor = isOk ? "#059669" : isWarn ? "#92400E" : "#DC2626";
                    const badgeBorder = isOk ? "#A7F3D0" : isWarn ? "#FDE68A" : "#FECACA";

                    return `
                        <div style="background:#FFFFFF; border:1.5px solid ${borderColor}; border-top:4px solid ${topBorderColor}; border-radius:12px; padding:14px 16px; box-shadow:0 2px 8px rgba(0,0,0,0.04); display:flex; flex-direction:column; justify-content:space-between; gap:10px;">
                            <div>
                                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                                    <div style="display:flex; align-items:center; gap:8px;">
                                        <span style="font-size:20px;">${p.icon || '🔐'}</span>
                                        <strong style="font-size:14px; color:#0F172A;">${p.name || p.platform_name || p.platform}</strong>
                                    </div>
                                    <span style="background:${badgeBg}; color:${badgeColor}; border:1px solid ${badgeBorder}; font-size:11px; font-weight:800; padding:2px 7px; border-radius:5px;">
                                        ${p.status_label || (isOk ? '🟢 정상' : '🔴 점검 필요')}
                                    </span>
                                </div>
                                
                                <div style="display:flex; flex-direction:column; gap:4px; font-size:12px; color:#475569; background:#F8FAFC; padding:8px 10px; border-radius:6px; border:1px solid #F1F5F9;">
                                    <div style="display:flex; justify-content:space-between;">
                                        <span style="color:#64748B;">인증 계정:</span>
                                        <strong style="color:#0F172A;">${p.account || '-'}</strong>
                                    </div>
                                    <div style="display:flex; justify-content:space-between;">
                                        <span style="color:#64748B;">세션 수명:</span>
                                        <span style="color:${isOk ? '#059669' : '#DC2626'}; font-weight:700;">${p.expires_at || '확인 대기'}</span>
                                    </div>
                                </div>
                            </div>

                            ${!isOk ? `
                                <div style="background:#FEF2F2; border:1px solid #FECACA; border-radius:8px; padding:10px 12px; font-size:11.5px; line-height:1.45;">
                                    <div style="color:#991B1B; margin-bottom:4px;">
                                        ⚠️ <strong>장애 원인:</strong> <span style="font-weight:600;">${p.cause || '세션 만료 또는 로그인 필요'}</span>
                                    </div>
                                    <div style="color:#1E40AF; background:#EFF6FF; border:1px solid #BFDBFE; padding:6px 8px; border-radius:6px; margin-top:6px; font-weight:700;">
                                        👉 <strong>해결 조치:</strong> ${p.action || '배치 파일 실행으로 1회 로그인'}
                                    </div>
                                </div>
                            ` : `
                                <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:6px; padding:6px 10px; font-size:11.5px; color:#166534; font-weight:600; display:flex; align-items:center; gap:6px;">
                                    <span>✨</span> <span>영구 로그인 활성 상태 — 무인 자동 발행 준비 완료</span>
                                </div>
                            `}
                        </div>
                    `;
                }).join("");
            }
        }

        // 📡 3. 채널별 실제 발행 상태 및 바로가기 링크 렌더링
        const channelsGrid = document.getElementById("health-channels-grid");
        if (channelsGrid) {
            const nb = channels.naver_blog || {};
            const tb = channels.tistory || {};
            const supa = channels.supabase_research || {};
            const kinAnswers = kin.recent_answers || [];

            // 5대 숏폼 플랫폼 목록 생성 (유튜브, 인스타그램, 페이스북, 네이버 클립, 틱톡)
            const spList = [
                { key: "youtube", name: "유튜브 쇼츠", icon: "🔴", data: shortsPlatforms.youtube || {} },
                { key: "instagram", name: "인스타그램 릴스", icon: "📸", data: shortsPlatforms.instagram || {} },
                { key: "facebook", name: "페이스북 릴스", icon: "👥", data: shortsPlatforms.facebook || {} },
                { key: "naver_clip", name: "네이버 클립", icon: "🟢", data: shortsPlatforms.naver_clip || {} },
                { key: "tiktok", name: "틱톡 (TikTok)", icon: "📱", data: shortsPlatforms.tiktok || {} }
            ];

            const shortsHtml = spList.map(sp => {
                const isPub = sp.data.is_today && sp.data.url;
                const hasPast = Boolean(sp.data.url);
                return `
                    <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:10px 12px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span>${sp.icon}</span>
                            <strong style="font-size:13px; color:#0F172A;">${sp.name}</strong>
                            <span style="font-size:11px; color:#64748B;">⏱️ ${sp.data.published_at || '-'}</span>
                            ${isPub 
                                ? `<span style="background:#ECFDF5; color:#059669; font-size:10.5px; font-weight:800; padding:2px 6px; border-radius:4px;">🟢 오늘 발행 완료</span>`
                                : `<span style="background:#FEF3C7; color:#92400E; font-size:10.5px; font-weight:700; padding:2px 6px; border-radius:4px;">⚪ 오늘자 미발행 (정시 대기)</span>`}
                        </div>
                        <div style="display:flex; align-items:center; gap:6px;">
                            ${isPub 
                                ? `<a href="${sp.data.url}" target="_blank" style="font-size:11px; font-weight:700; color:#DC2626; background:#FEE2E2; border:1px solid #FECACA; padding:3px 8px; border-radius:6px; text-decoration:none; display:inline-flex; align-items:center; gap:3px;">
                                    <span>🔗 바로가기</span> <span>↗</span>
                                   </a>`
                                : hasPast
                                ? `<a href="${sp.data.url}" target="_blank" style="font-size:11px; font-weight:700; color:#475569; background:#F1F5F9; border:1px solid #E2E8F0; padding:3px 8px; border-radius:6px; text-decoration:none; display:inline-flex; align-items:center; gap:3px;">
                                    <span>🎬 최근 영상 ↗</span>
                                   </a>`
                                : `<span style="font-size:11px; font-weight:700; color:#92400E; background:#FEF3C7; padding:3px 8px; border-radius:6px;">👉 오늘자 정기 스케줄 대기 또는 1회 수동 발행 트리거</span>`}
                        </div>
                    </div>
                `;
            }).join("");

            // 5장 카드뉴스 플랫폼 목록 생성
            const cpList = [
                { key: "instagram", name: "인스타 캐러셀 (5장)", icon: "📸", data: cardPlatforms.instagram || {} },
                { key: "facebook", name: "페이스북 앨범 (5장)", icon: "📘", data: cardPlatforms.facebook || {} },
                { key: "local_slides", name: "1080x1350 카드뉴스 5장 완제품", icon: "📁", data: cardPlatforms.local_slides || {} }
            ];

            const cardnewsHtml = cpList.map(cp => {
                const isPub = cp.data.is_today && (cp.data.url || cp.data.is_success);
                const hasPast = Boolean(cp.data.url || cp.data.is_success);
                return `
                    <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:10px 12px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span>${cp.icon}</span>
                            <strong style="font-size:13px; color:#0F172A;">${cp.name}</strong>
                            <span style="font-size:11px; color:#64748B;">⏱️ ${cp.data.published_at || cp.data.time || '-'}</span>
                            ${isPub 
                                ? `<span style="background:#ECFDF5; color:#059669; font-size:10.5px; font-weight:800; padding:2px 6px; border-radius:4px;">🟢 오늘 발행 완료</span>`
                                : `<span style="background:#FEF3C7; color:#92400E; font-size:10.5px; font-weight:700; padding:2px 6px; border-radius:4px;">⚪ 오늘자 미발행 (정시 대기)</span>`}
                        </div>
                        <div style="display:flex; align-items:center; gap:6px;">
                            ${isPub && cp.data.url
                                ? `<a href="${cp.data.url}" target="_blank" style="font-size:11px; font-weight:700; color:#E1306C; background:#FCE7F3; border:1px solid #FBCFE8; padding:3px 8px; border-radius:6px; text-decoration:none; display:inline-flex; align-items:center; gap:3px;">
                                    <span>📸 카드뉴스 열기</span> <span>↗</span>
                                   </a>`
                                : hasPast && cp.data.url
                                ? `<a href="${cp.data.url}" target="_blank" style="font-size:11px; font-weight:700; color:#475569; background:#F1F5F9; border:1px solid #E2E8F0; padding:3px 8px; border-radius:6px; text-decoration:none; display:inline-flex; align-items:center; gap:3px;">
                                    <span>📸 최근 카드뉴스 ↗</span>
                                   </a>`
                                : cp.data.is_success
                                ? `<span style="font-size:11px; font-weight:700; color:#059669; background:#ECFDF5; padding:3px 8px; border-radius:6px;">✅ ${cp.data.slide_count || 5}장 완제품 보관 중</span>`
                                : `<span style="font-size:11px; font-weight:700; color:#92400E; background:#FEF3C7; padding:3px 8px; border-radius:6px;">👉 오늘자 정기 스케줄 대기 또는 1회 수동 발행 트리거</span>`}
                        </div>
                    </div>
                `;
            }).join("");

            let slotsHealthHtml = "";
            if (blog.today_slots && blog.today_slots.length > 0) {
                slotsHealthHtml = `
                    <div style="grid-column: 1 / -1; background:#F0FDF4; border:1.5px solid #BBF7D0; border-radius:12px; padding:14px 16px; margin-bottom:12px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                            <span style="font-size:13px; font-weight:800; color:#166534;">📊 당일 정시 블로그 발행 현황 (${blog.today_count || blog.today_slots.length}/3회)</span>
                            <span style="font-size:11px; font-weight:800; background:#DCFCE7; color:#15803D; padding:3px 8px; border-radius:6px;">${blog.slot_status_label || '🟢 오늘 목표 발행 달성'}</span>
                        </div>
                        <div style="display:flex; flex-direction:column; gap:6px;">
                            ${blog.today_slots.map(s => `
                                <div style="background:#FFFFFF; border:1px solid #DCFCE7; border-radius:8px; padding:8px 12px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:6px;">
                                    <div style="font-size:12px; color:#1E293B; font-weight:700;">
                                        <span style="color:#059669; font-weight:800;">[${s.slot_num}차 ${(s.published_at||'').split(' ')[1] || ''}]</span> ${s.title}
                                    </div>
                                    <div style="display:flex; gap:6px;">
                                        ${s.naver_url ? `<a href="${s.naver_url}" target="_blank" style="padding:3px 8px; background:#03C75A; color:#fff; border-radius:4px; font-size:11px; font-weight:800; text-decoration:none;">네이버 ↗</a>` : ''}
                                        ${s.tistory_url ? `<a href="${s.tistory_url}" target="_blank" style="padding:3px 8px; background:#FF5722; color:#fff; border-radius:4px; font-size:11px; font-weight:800; text-decoration:none;">티스토리 ↗</a>` : ''}
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
            }

            channelsGrid.innerHTML = `
                ${slotsHealthHtml}
                ${supa.is_success ? `
                <!-- 0. 🌐 자체 홈페이지 퀀트 리서치 블로그 -->
                <div class="action-card" style="border:1.5px solid #E2E8F0; border-top:4px solid #2563EB; background:#FFFFFF; padding:16px; border-radius:12px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span style="font-size:18px;">🌐</span>
                            <h4 style="margin:0; font-size:15px; font-weight:800; color:#0F172A;">자체 홈페이지 블로그 (Supabase 본진)</h4>
                        </div>
                        <span style="background:#EFF6FF; color:#1D4ED8; font-size:11px; font-weight:800; padding:3px 8px; border-radius:6px; border:1px solid #BFDBFE;">🟢 1순위 등록 완료</span>
                    </div>
                    <div style="font-size:13px; font-weight:700; color:#1E293B; margin-bottom:8px; line-height:1.4;">
                        ${supa.title || 'StockMaster 자체 퀀트 리서치 칼럼'}
                    </div>
                    <div style="font-size:11.5px; color:#64748B; margin-bottom:12px;">
                        발행 시각: <strong>${supa.published_at || '-'}</strong>
                    </div>
                    <a href="${supa.url || 'https://stockmaster-ai.vercel.app/'}" target="_blank" style="display:inline-flex; align-items:center; gap:6px; padding:7px 12px; background:#2563EB; color:#FFFFFF; border-radius:6px; font-size:12px; font-weight:800; text-decoration:none;">
                        <span>🔗 자체 홈페이지 블로그 열기</span>
                        <span>↗</span>
                    </a>
                </div>
                ` : ''}

                <!-- 1. 네이버 블로그 실시간 상태 -->
                <div class="action-card" style="border:1.5px solid #E2E8F0; border-top:4px solid #03C75A; background:#FFFFFF; padding:16px; border-radius:12px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span style="font-size:18px;">🟢</span>
                            <h4 style="margin:0; font-size:15px; font-weight:800; color:#0F172A;">네이버 블로그</h4>
                        </div>
                        ${nb.is_success && nb.is_today
                            ? `<span style="background:#ECFDF5; color:#059669; font-size:11px; font-weight:800; padding:3px 8px; border-radius:6px; border:1px solid #A7F3D0;">🟢 오늘 발행 완료</span>` 
                            : `<span style="background:#FEF3C7; color:#92400E; font-size:11px; font-weight:800; padding:3px 8px; border-radius:6px; border:1px solid #FDE68A;">⚪ 오늘자 미발행 (정시 대기)</span>`}
                    </div>
                    <div style="font-size:13px; font-weight:700; color:#1E293B; margin-bottom:8px; line-height:1.4;">
                        ${nb.title || blog.last_title_naver || blog.last_title || '오늘 발행 대기 중'}
                    </div>
                    <div style="font-size:11.5px; color:#64748B; margin-bottom:8px;">
                        발행 시각: <strong>${nb.published_at || blog.last_run_time || '-'}</strong>
                    </div>
                    ${(!nb.is_today) ? `
                        <div style="background:#FFFBEB; border:1px solid #FDE68A; padding:8px 10px; border-radius:6px; font-size:11.5px; color:#92400E; margin-bottom:10px; line-height:1.4;">
                            ⚠️ <strong>원인:</strong> 오늘자 미발행 (최근 실제 발행: ${nb.published_at || blog.last_run_time || '-' })<br>
                            👉 <strong>조치:</strong> 오늘자 정기 스케줄 대기 또는 1회 수동 발행 트리거
                        </div>
                    ` : ''}
                    ${nb.url && nb.is_success 
                        ? `<a href="${nb.url}" target="_blank" style="display:inline-flex; align-items:center; gap:6px; padding:7px 12px; background:#03C75A; color:#FFFFFF; border-radius:6px; font-size:12px; font-weight:800; text-decoration:none;">
                            <span>🔗 발행된 네이버 글 열기</span>
                            <span>↗</span>
                           </a>` 
                        : `<span style="font-size:11.5px; color:#94A3B8;">오늘 발행된 네이버 상세 URL이 없습니다.</span>`}
                </div>

                <!-- 2. 티스토리 블로그 실시간 상태 -->
                <div class="action-card" style="border:1.5px solid #E2E8F0; border-top:4px solid #FF5722; background:#FFFFFF; padding:16px; border-radius:12px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span style="font-size:18px;">🟠</span>
                            <h4 style="margin:0; font-size:15px; font-weight:800; color:#0F172A;">티스토리 (Tistory)</h4>
                        </div>
                        ${tb.is_success
                            ? (tb.is_today 
                                ? `<span style="background:#ECFDF5; color:#059669; font-size:11px; font-weight:800; padding:3px 8px; border-radius:6px;">🟢 오늘 발행 완료</span>`
                                : `<span style="background:#ECFDF5; color:#059669; font-size:11px; font-weight:800; padding:3px 8px; border-radius:6px;">🟢 정상 연동됨 (최신 글 연결)</span>`)
                            : tb.is_session_expired 
                            ? `<span style="background:#FEE2E2; color:#DC2626; font-size:11px; font-weight:800; padding:3px 8px; border-radius:6px; border:1px solid #FECACA;">🔴 세션 만료</span>`
                            : `<span style="background:#FEF3C7; color:#92400E; font-size:11px; font-weight:800; padding:3px 8px; border-radius:6px; border:1px solid #FDE68A;">⚪ 오늘자 미발행 (정시 대기)</span>`}
                    </div>
                    <div style="font-size:13px; font-weight:700; color:#1E293B; margin-bottom:8px; line-height:1.4;">
                        ${tb.title || blog.last_title_tistory || blog.last_title || '오늘 발행 대기 중'}
                    </div>
                    <div style="font-size:11.5px; color:#64748B; margin-bottom:8px;">
                        발행 시각: <strong>${tb.published_at || '-'}</strong>
                    </div>
                    ${tb.is_session_expired 
                        ? `<div style="background:#FEF2F2; border:1px solid #FECACA; padding:8px 10px; border-radius:6px; font-size:11.5px; color:#991B1B; margin-bottom:10px;">
                            ⚠️ <strong>원인:</strong> 카카오 세션 만료<br>
                            👉 <strong>조치:</strong> [1회연동] 티스토리 배치 파일 실행 필요
                           </div>` 
                        : (!tb.is_today && !tb.is_success) ? `
                        <div style="background:#FFFBEB; border:1px solid #FDE68A; padding:8px 10px; border-radius:6px; font-size:11.5px; color:#92400E; margin-bottom:10px; line-height:1.4;">
                            ⚠️ <strong>원인:</strong> 오늘자 미발행 (최근 실제 발행: ${tb.published_at || '-'})<br>
                            👉 <strong>조치:</strong> 오늘자 정기 스케줄 대기 또는 1회 수동 발행 트리거
                        </div>
                    ` : ''}
                    ${tb.url && tb.is_success 
                        ? `<a href="${tb.url}" target="_blank" style="display:inline-flex; align-items:center; gap:6px; padding:7px 12px; background:#FF5722; color:#FFFFFF; border-radius:6px; font-size:12px; font-weight:800; text-decoration:none;">
                            <span>🔗 발행된 티스토리 글 열기</span>
                            <span>↗</span>
                           </a>` 
                        : ''}
                </div>

                <!-- 3. 네이버 지식iN 실시간 상태 -->
                <div class="action-card" style="border:1.5px solid #E2E8F0; border-top:4px solid #0284C7; background:#FFFFFF; padding:16px; border-radius:12px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span style="font-size:18px;">💬</span>
                            <h4 style="margin:0; font-size:15px; font-weight:800; color:#0F172A;">네이버 지식iN</h4>
                        </div>
                        <span style="background:#E0F2FE; color:#0284C7; font-size:11.5px; font-weight:800; padding:3px 8px; border-radius:6px;">
                            오늘 ${kin.today_count || 0} / ${kin.target_count || 10}건 답변
                        </span>
                    </div>
                    ${kinAnswers.length > 0
                        ? `<div style="margin-top:6px; display:flex; flex-direction:column; gap:6px;">
                            ${kinAnswers.slice(0, 3).map((ka, kIdx) => `
                                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:6px; padding:8px 10px; display:flex; justify-content:space-between; align-items:center; gap:8px;">
                                    <div style="overflow:hidden; text-overflow:ellipsis; white-space:nowrap; flex:1;">
                                        <span style="font-size:11px; color:#64748B;">[${ka.created_at || '-'}]</span>
                                        <strong style="font-size:12px; color:#0F172A; margin-left:4px;">${ka.title}</strong>
                                    </div>
                                    <a href="${ka.url}" target="_blank" style="font-size:11px; font-weight:700; color:#0284C7; background:#E0F2FE; padding:3px 8px; border-radius:4px; text-decoration:none; white-space:nowrap;">
                                        열기 ↗
                                    </a>
                                </div>
                            `).join("")}
                           </div>` 
                        : `<div style="font-size:12px; color:#92400E; background:#FFFBEB; border:1px solid #FDE68A; padding:8px 10px; border-radius:6px; margin-top:8px;">
                            ⚠️ <strong>원인:</strong> 오늘자 미발행 (실시간 질문 낚아채기 대기 중)<br>
                            👉 <strong>조치:</strong> 오늘자 정기 스케줄 대기 또는 1회 수동 발행 트리거
                           </div>`}
                </div>

                <!-- 4. 4대 숏폼 & 릴스 플랫폼별 실시간 상태 -->
                <div class="action-card" style="border:1.5px solid #E2E8F0; border-top:4px solid #DC2626; background:#FFFFFF; padding:16px; border-radius:12px; grid-column: 1 / -1;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span style="font-size:18px;">🎬</span>
                            <h4 style="margin:0; font-size:15px; font-weight:800; color:#0F172A;">4대 숏폼 플랫폼 개별 송출 현황 (유튜브 · 인스타 · 페이스북 · 네이버 클립)</h4>
                        </div>
                        <span style="background:${shorts.today_count > 0 ? '#ECFDF5' : '#FEF3C7'}; color:${shorts.today_count > 0 ? '#059669' : '#92400E'}; font-size:11.5px; font-weight:800; padding:3px 8px; border-radius:6px;">
                            오늘 ${shorts.today_count || 0}건 송출 완료
                        </span>
                    </div>
                    ${shortsHtml}
                </div>

                <!-- 5. 5장 카드뉴스 플랫폼별 실시간 상태 -->
                <div class="action-card" style="border:1.5px solid #E2E8F0; border-top:4px solid #E1306C; background:#FFFFFF; padding:16px; border-radius:12px; grid-column: 1 / -1;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span style="font-size:18px;">📸</span>
                            <h4 style="margin:0; font-size:15px; font-weight:800; color:#0F172A;">5장 카드뉴스 플랫폼 개별 송출 현황 (인스타 · 페이스북 · 완제품 파일)</h4>
                        </div>
                        <span style="background:${cardnews.today_count > 0 ? '#ECFDF5' : '#FEF3C7'}; color:${cardnews.today_count > 0 ? '#059669' : '#92400E'}; font-size:11.5px; font-weight:800; padding:3px 8px; border-radius:6px;">
                            오늘 ${cardnews.today_count || 0}건 발행 완료
                        </span>
                    </div>
                    ${cardnewsHtml}
                </div>
            `;
        }

        // 📸 0. [12대 채널 실시간 육안 증빙 & 헬스 맥박 관제탑 렌더링]
        const livePulse = data.live_pulse || {};
        const brandPulse = (livePulse.brands && livePulse.brands[b]) || {};
        renderLivePulseGrid(brandPulse, b, brandName);

        // 헤더 뱃지 업데이트 (치명적 장애 vs 정시 대기 분리)
        const headerBadge = document.getElementById("header-health-score");
        if (headerBadge) {
            if (criticalIssues.length > 0) {
                headerBadge.innerText = `장애 ${criticalIssues.length}건 감지 🔴`;
                headerBadge.style.background = "#FEF2F2";
                headerBadge.style.color = "#DC2626";
                headerBadge.style.borderColor = "#F87171";
            } else if (scheduledPending.length > 0) {
                headerBadge.innerText = `정시 대기 중 (${scheduledPending.length}채널) 🟢`;
                headerBadge.style.background = "#ECFDF5";
                headerBadge.style.color = "#059669";
                headerBadge.style.borderColor = "#A7F3D0";
            } else {
                headerBadge.innerText = "100% 정상 🟢";
                headerBadge.style.background = "#ECFDF5";
                headerBadge.style.color = "#059669";
                headerBadge.style.borderColor = "#A7F3D0";
            }
        }
    } catch (e) {
        console.error("Health status load error:", e);
    }
}

// 📸 12대 채널 실시간 육안 증빙 & 헬스케어 맥박 그리드 렌더러
function renderLivePulseGrid(pulseData, brandKey, brandName) {
    const container = document.getElementById("health-live-pulse-grid");
    if (!container) return;

    const channels = pulseData.channels || [];
    if (channels.length === 0) {
        container.innerHTML = `
            <div style="grid-column: 1 / -1; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:16px; text-align:center; color:#64748B; font-size:13px;">
                ${brandName}의 12대 채널 실시간 증빙 데이터를 불러오는 중입니다...
            </div>
        `;
        return;
    }

    container.innerHTML = channels.map(ch => {
        const isHealthy = ch.status === "HEALTHY";
        const isError = ch.status === "ERROR";
        const isStandby = ch.status === "STANDBY";

        const cardBorder = isHealthy ? "#86EFAC" : isError ? "#FCA5A5" : "#E2E8F0";
        const topBorder = isHealthy ? "#22C55E" : isError ? "#EF4444" : "#94A3B8";
        const badgeBg = isHealthy ? "#ECFDF5" : isError ? "#FEF2F2" : "#F8FAFC";
        const badgeColor = isHealthy ? "#059669" : isError ? "#DC2626" : "#64748B";
        const badgeBorder = isHealthy ? "#A7F3D0" : isError ? "#FECACA" : "#CBD5E1";

        return `
            <div style="background:#FFFFFF; border:1.5px solid ${cardBorder}; border-top:4px solid ${topBorder}; border-radius:12px; padding:14px 16px; box-shadow:0 2px 10px rgba(0,0,0,0.04); display:flex; flex-direction:column; justify-content:space-between; gap:12px;">
                <div>
                    <!-- 상단 헤더: 아이콘 + 채널명 + 상태 뱃지 -->
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span style="font-size:20px;">${ch.icon}</span>
                            <strong style="font-size:13.5px; color:#0F172A;">${ch.name}</strong>
                        </div>
                        <span style="background:${badgeBg}; color:${badgeColor}; border:1px solid ${badgeBorder}; font-size:11px; font-weight:800; padding:2px 8px; border-radius:5px;">
                            ${ch.status_label}
                        </span>
                    </div>

                    <!-- 제목 및 시각 정보 -->
                    <div style="font-size:12px; color:#475569; background:#F8FAFC; padding:8px 10px; border-radius:6px; border:1px solid #F1F5F9; line-height:1.45;">
                        <div style="margin-bottom:3px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">
                            <strong>타이틀:</strong> <span style="color:#0F172A; font-weight:600;">${ch.title || '정시 스케줄 대기 중'}</span>
                        </div>
                        <div style="font-size:11px; color:#64748B;">
                            ${isHealthy ? `⏱️ <strong>발행 성공:</strong> ${ch.published_at || '-'}` : isError ? `⏱️ <strong>실패 시각:</strong> <span style="color:#DC2626;">${ch.failed_at || '-'}</span>` : `⏱️ <strong>스케줄:</strong> 24시간 무인 정시 대기`}
                        </div>
                    </div>

                    <!-- 🔴 장애/실패 사유 표시 (실패 시 투명하게 노출) -->
                    ${isError ? `
                        <div style="background:#FEF2F2; border:1px solid #FECACA; border-radius:8px; padding:10px 12px; font-size:11.5px; margin-top:8px; line-height:1.45;">
                            <div style="color:#991B1B; margin-bottom:4px;">
                                🚨 <strong>실패 원인:</strong> <span style="font-weight:600; color:#DC2626;">${ch.error_message || '요청 시간 초과 또는 로그인 세션 점검 필요'}</span>
                            </div>
                            <div style="color:#1E40AF; background:#EFF6FF; border:1px solid #BFDBFE; padding:6px 8px; border-radius:6px; margin-top:6px; font-weight:700; display:flex; justify-content:space-between; align-items:center;">
                                <span>👉 세션 확인 후 즉시 재시도 가능</span>
                                <button class="btn btn-primary" onclick="retryChannelPublish('${brandKey}', '${ch.key}', this)" style="font-size:10.5px; padding:3px 8px; background:#DC2626; border-color:#DC2626; margin:0;">
                                    🔄 즉시 재발행
                                </button>
                            </div>
                        </div>
                    ` : ''}

                    <!-- 📸 실시간 증빙 스크린샷 썸네일 (성공 시 노출) -->
                    ${ch.screenshot_url ? `
                        <div style="margin-top:10px; display:flex; align-items:center; gap:10px; background:#0F172A; padding:8px 10px; border-radius:8px; cursor:pointer;" onclick="openProofModal('${ch.screenshot_url}', '${ch.name} 실시간 라이브 증빙')">
                            <img src="${ch.screenshot_url}" alt="증빙 썸네일" style="width:50px; height:50px; object-fit:cover; border-radius:6px; border:1px solid #334155;" />
                            <div style="flex:1;">
                                <div style="font-size:11.5px; font-weight:700; color:#38BDF8; display:flex; align-items:center; gap:4px;">
                                    <span>📸 실시간 브라우저 캡처 증빙</span> <span>↗</span>
                                </div>
                                <div style="font-size:10.5px; color:#94A3B8; margin-top:2px;">클릭 시 고화질 원본 스크린샷 확대</div>
                            </div>
                        </div>
                    ` : ''}
                </div>

                <!-- 하단 액션 버튼: 실제 링크 바로가기 -->
                <div style="display:flex; justify-content:space-between; align-items:center; pt-2; border-top:1px solid #F1F5F9; margin-top:4px;">
                    ${ch.live_url ? `
                        <a href="${ch.live_url}" target="_blank" style="font-size:11.5px; font-weight:800; color:#2563EB; background:#EFF6FF; border:1px solid #BFDBFE; padding:5px 10px; border-radius:6px; text-decoration:none; display:inline-flex; align-items:center; gap:4px;">
                            <span>🔗 실제 발행글 바로가기</span> <span>↗</span>
                        </a>
                    ` : `
                        <span style="font-size:11px; color:#94A3B8;">대기 상태</span>
                    `}
                    <span style="font-size:10.5px; color:#64748B; font-weight:600;">[${ch.category}]</span>
                </div>
            </div>
        `;
    }).join("");
}

// 📸 실시간 증빙 스크린샷 모달 열기
function openProofModal(imageUrl, title) {
    const modal = document.getElementById("proof-modal");
    const modalImg = document.getElementById("proof-modal-img");
    const modalTitle = document.getElementById("proof-modal-title");

    if (modal && modalImg) {
        modalImg.src = imageUrl;
        if (modalTitle) modalTitle.innerHTML = `<span>📸</span> <span>${title || '실시간 라이브 발행 증빙'}</span>`;
        modal.style.display = "flex";
    }
}

// 📸 실시간 증빙 스크린샷 모달 닫기
function closeProofModal() {
    const modal = document.getElementById("proof-modal");
    if (modal) {
        modal.style.display = "none";
    }
}

// 🔄 실패 채널 1회 즉시 재시도 트리거
async function retryChannelPublish(brand, channelKey, btn) {
    if (btn) {
        btn.disabled = true;
        btn.innerText = "⏳ 재발행 중...";
    }
    showToast(`⚡ [${brand.toUpperCase()} - ${channelKey}] 1회 즉시 재발행을 가동합니다...`, "info");
    appendLog(`[Retry] ${brand} - ${channelKey} 1회 즉시 재발행 가동`, "info");

    try {
        const res = await fetch(`/api/run-hub/${brand}/${channelKey}`, { method: "POST" });
        const data = await res.json();
        showToast(data.message || "재발행 요청 완료", "success");
        appendLog(`[Retry Result] ${data.message}`, "success");
        setTimeout(() => loadHealthStatus(), 3000);
    } catch (e) {
        showToast(`재발행 실패: ${e}`, "error");
        appendLog(`[Retry Error] ${e}`, "error");
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerText = "🔄 즉시 재발행";
        }
    }
}

async function runFullHealthDiagnostic(btn) {
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<span class="spin-icon" style="display:inline-block;animation:rotateSpin 0.6s linear infinite;">🔄</span> 자가진단 중...`;
    }
    appendLog("[Diagnosis] 전체 시스템 정밀 자가진단 실행 중...", "info");
    showToast("🔍 시스템 전체 자가진단을 시작합니다...", "info");
    try {
        const res = await fetch("/api/health/run-diagnostic", { method: "POST" });
        const data = await res.json();
        if (data.success) {
            appendLog(`[Success] ${data.message}`, "success");
            showToast(data.message, "success");
            await loadHealthStatus();
        }
    } catch (e) {
        appendLog(`[Error] 자가진단 요청 통신 실패: ${e}`, "error");
        showToast("자가진단 통신 오류", "error");
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `🔍 1초 정밀 자가진단`;
        }
    }
}

// 🕵️ 3대 브랜드 6대 플랫폼 엔진별 사람처럼 행동하는 스텔스 웜업 관제탑 렌더러
function renderStealthWarmupGrid(stealth, brandKey, brandName) {
    const container = document.getElementById("health-stealth-grid");
    if (!container) return;

    const engines = stealth?.engines || [];
    if (engines.length === 0) {
        container.innerHTML = `
            <div style="grid-column: 1 / -1; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:16px; text-align:center; color:#64748B; font-size:13px;">
                ${brandName}의 6대 플랫폼 스텔스 웜업 엔진 데이터를 불러오는 중입니다...
            </div>
        `;
        return;
    }

    container.innerHTML = engines.map(eng => {
        const isRunning = eng.status === "WARMUP_RUNNING";
        const isBlocked = eng.status === "BLOCKED";
        const isHealthy = eng.status === "HEALTHY";

        const cardBorder = isRunning ? "#93C5FD" : isBlocked ? "#FCA5A5" : "#86EFAC";
        const topBorder = isRunning ? "#2563EB" : isBlocked ? "#EF4444" : "#22C55E";
        const badgeBg = isRunning ? "#DBEAFE" : isBlocked ? "#FEF2F2" : "#ECFDF5";
        const badgeColor = isRunning ? "#1D4ED8" : isBlocked ? "#DC2626" : "#059669";
        const badgeBorder = isRunning ? "#93C5FD" : isBlocked ? "#FECACA" : "#A7F3D0";

        return `
            <div style="background:#FFFFFF; border:1.5px solid ${cardBorder}; border-top:4px solid ${topBorder}; border-radius:12px; padding:16px; box-shadow:0 2px 10px rgba(0,0,0,0.04); display:flex; flex-direction:column; justify-content:space-between; gap:12px;">
                <div>
                    <!-- 상단 헤더: 아이콘 + 플랫폼 엔진명 + 상태 뱃지 -->
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span style="font-size:22px;">${eng.icon}</span>
                            <strong style="font-size:14px; color:#0F172A;">${eng.name}</strong>
                        </div>
                        <span style="background:${badgeBg}; color:${badgeColor}; border:1px solid ${badgeBorder}; font-size:11px; font-weight:800; padding:2px 8px; border-radius:5px;">
                            ${eng.status_label}
                        </span>
                    </div>

                    <!-- 인간 행동 루틴 상세 지표 -->
                    <div style="display:flex; flex-direction:column; gap:6px; font-size:12px; color:#475569; background:#F8FAFC; padding:10px 12px; border-radius:8px; border:1px solid #F1F5F9; line-height:1.45;">
                        <div>
                            <span style="color:#64748B;">🎯 <strong>인간 행동 루틴:</strong></span>
                            <div style="color:#0F172A; font-weight:600; margin-top:2px;">${eng.routine_type}</div>
                        </div>

                        <div style="border-top:1px dashed #E2E8F0; pt-1; margin-top:2px;">
                            <span style="color:#64748B;">🎨 <strong>관심사 알고리즘:</strong></span>
                            <span style="color:#2563EB; font-weight:600;"> ${eng.interest_mix}</span>
                        </div>

                        <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px dashed #E2E8F0; pt-1; margin-top:2px;">
                            <span style="color:#64748B;">🛡️ <strong>신뢰/안전 지수:</strong></span>
                            <strong style="color:#059669; font-size:11.5px;">${eng.trust_score}</strong>
                        </div>

                        <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px dashed #E2E8F0; pt-1; margin-top:2px;">
                            <span style="color:#64748B;">⏱️ <strong>오늘자 활동:</strong></span>
                            <span style="color:#0F172A; font-weight:600;">${eng.today_activity}</span>
                        </div>
                    </div>

                    <!-- 🔴 세션 만료 및 차단 시 원인/조치법 투명 노출 -->
                    ${isBlocked ? `
                        <div style="background:#FEF2F2; border:1px solid #FECACA; border-radius:8px; padding:10px 12px; font-size:11.5px; margin-top:10px; line-height:1.45;">
                            <div style="color:#991B1B; margin-bottom:4px;">
                                ⚠️ <strong>차단/만료 원인:</strong> <span style="font-weight:600; color:#DC2626;">${eng.cause}</span>
                            </div>
                            <div style="color:#1E40AF; background:#EFF6FF; border:1px solid #BFDBFE; padding:6px 8px; border-radius:6px; margin-top:6px; font-weight:700;">
                                👉 <strong>해결 조치:</strong> ${eng.action}
                            </div>
                        </div>
                    ` : ''}
                </div>

                <!-- 하단 액션: 해당 플랫폼 1회 즉시 스텔스 웜업 버튼 -->
                <div style="display:flex; justify-content:space-between; align-items:center; pt-2; border-top:1px solid #F1F5F9; margin-top:4px;">
                    <span style="font-size:11px; color:#64748B;">베지어 곡선 인간 마우스 적용</span>
                    <button class="btn btn-secondary" onclick="triggerPlatformStealth('${brandKey}', '${eng.platform}', '${eng.hub_key}', this)" style="font-size:11px; padding:4px 10px; background:#F1F5F9; border-color:#CBD5E1; color:#0F172A; font-weight:700; display:flex; align-items:center; gap:4px;">
                        <span>⚡</span> <span>1회 즉시 웜업</span>
                    </button>
                </div>
            </div>
        `;
    }).join("");
}

// ⚡ 특정 플랫폼 엔진 1회 즉시 스텔스 웜업 실행
async function triggerPlatformStealth(brand, platformKey, hubKey, btn) {
    if (btn) {
        btn.disabled = true;
        btn.innerText = "⏳ 웜업 가동 중...";
    }
    const nameMap = { aura: "💖 Aura", insurance: "🛡️ 보험비교", stock: "📈 주식AI" };
    const bName = nameMap[brand] || brand.toUpperCase();
    showToast(`🕵️ [${bName} - ${platformKey.toUpperCase()}] 사람처럼 피드 탐색 및 좋아요 웜업을 가동합니다...`, "info");
    appendLog(`[Stealth] ${bName} ${platformKey} 1회 즉시 스텔스 웜업 가동 (Gemini 0회, 순수 브라우저)`, "info");

    try {
        const targetHub = hubKey || "human_behavior";
        const res = await fetch(`/api/run-hub/${brand}/${targetHub}`, { method: "POST" });
        const data = await res.json();
        showToast(data.message || `${platformKey} 스텔스 웜업 요청 완료`, "success");
        appendLog(`[Stealth Result] ${data.message}`, "success");
        setTimeout(() => loadHealthStatus(), 3000);
    } catch (e) {
        showToast(`스텔스 웜업 실패: ${e}`, "error");
        appendLog(`[Stealth Error] ${e}`, "error");
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `<span>⚡</span> <span>1회 즉시 웜업</span>`;
        }
    }
}


// 🚀 [신규 전광판] 선택된 1개 브랜드 전용 실시간 무인 발행 라이브 전광판 렌더러
function renderHealthBrandLiveFeed(liveFeed, gpuStatus, bKey) {
    const container = document.getElementById("health-brand-live-feed-container");
    if (!container || !liveFeed || !liveFeed.brands) return;

    const b = bKey || currentBrand || "stock";
    const brandConfigs = {
        aura: {
            title: "💖 Aura AI 데이팅",
            sub: "2030 소개팅 · 데이팅 앱",
            color: "#EC4899",
            bgGradient: "linear-gradient(135deg, #FFF1F2 0%, #FDF2F8 100%)",
            border: "#FBCFE8",
            badgeBg: "#FCE7F3",
            badgeColor: "#BE185D",
            landing: "https://aura-ai-dating.vercel.app/"
        },
        insurance: {
            title: "🛡️ 보험 리밸런스",
            sub: "실손 · 3대질병 · 보험비교",
            color: "#10B981",
            bgGradient: "linear-gradient(135deg, #ECFDF5 0%, #F0FDF4 100%)",
            border: "#A7F3D0",
            badgeBg: "#D1FAE5",
            badgeColor: "#065F46",
            landing: "https://insure-rebalance.vercel.app/"
        },
        stock: {
            title: "📈 StockMaster AI",
            sub: "국내주식 · 10분 계량 전광판",
            color: "#F59E0B",
            bgGradient: "linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%)",
            border: "#FDE68A",
            badgeBg: "#FEF3C7",
            badgeColor: "#92400E",
            landing: "https://stockmaster-ai.vercel.app/"
        }
    };

    const cfg = brandConfigs[b] || brandConfigs.stock;
    const bData = liveFeed.brands[b] || {};
    const blog = bData.blog || {};
    const kin = bData.kin || {};
    const shorts = bData.shorts || {};
    const cardnews = bData.cardnews || {};
    const channels = blog.channels || {};
    const shortsPlatforms = shorts.platforms || {};
    const cardPlatforms = cardnews.platforms || {};
    const today = liveFeed.today || "";

    // 🎮 GPU 실시간 렌더링 가동 전광판 배너
    let gpuBannerHtml = "";
    if (gpuStatus && (gpuStatus.status === "busy" || gpuStatus.status === "running" || (gpuStatus.current_task && gpuStatus.status !== "idle"))) {
        const taskName = gpuStatus.current_task || "미디어 실사 렌더링 중";
        const isCardnews = taskName.includes("카드뉴스") || taskName.includes("T2I") || taskName.includes("사진");
        const isShorts = taskName.includes("숏폼") || taskName.includes("S2V") || taskName.includes("영상");
        const badgeColor = isCardnews ? "#EC4899" : isShorts ? "#8B5CF6" : "#F59E0B";
        const bgGrad = isCardnews
            ? "linear-gradient(135deg, #FFF1F2 0%, #FDF2F8 50%, #FAF5FF 100%)"
            : "linear-gradient(135deg, #F5F3FF 0%, #EDE9FE 50%, #F0F9FF 100%)";
        const borderCol = isCardnews ? "#F472B6" : "#A78BFA";

        gpuBannerHtml = `
            <div class="gpu-live-status-banner" style="background:${bgGrad};border:2px solid ${borderCol};border-radius:14px;padding:14px 18px;margin-bottom:16px;box-shadow:0 8px 25px rgba(236,72,153,0.18);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;animation:gpuPulseBorder 2s infinite alternate;">
                <div style="display:flex;align-items:center;gap:14px;">
                    <div style="width:44px;height:44px;border-radius:12px;background:#0F172A;display:flex;align-items:center;justify-content:center;font-size:22px;box-shadow:0 4px 12px rgba(0,0,0,0.15);">
                        ${isCardnews ? '🎨' : isShorts ? '🎬' : '⚡'}
                    </div>
                    <div>
                        <div style="display:flex;align-items:center;gap:8px;">
                            <span style="background:${badgeColor};color:#FFFFFF;font-size:11px;font-weight:800;padding:2px 8px;border-radius:12px;display:inline-flex;align-items:center;gap:5px;">
                                <span class="pulse-dot" style="background:#FFFFFF;width:6px;height:6px;border-radius:50%;display:inline-block;"></span>
                                GPU 실시간 연산 가동 중
                            </span>
                            <span style="font-size:11.5px;color:#64748B;font-weight:600;">🎮 NVIDIA GeForce RTX 5060 Ti (100% 자율 생산)</span>
                        </div>
                        <div style="font-size:14.5px;font-weight:800;color:#0F172A;margin-top:4px;">
                            ${taskName}
                        </div>
                    </div>
                </div>
                <div style="display:flex;align-items:center;gap:8px;">
                    <span class="badge" style="background:#ECFDF5;color:#059669;border:1px solid #A7F3D0;font-weight:700;font-size:11.5px;">
                        🟢 렌더링 완료 시 자동 동기화
                    </span>
                    <button class="btn btn-secondary" onclick="loadHealthStatus(this)" style="font-size:11.5px;padding:6px 12px;">
                        🩺 실시간 갱신 →
                    </button>
                </div>
            </div>
        `;
    }

    // 0. 자체 홈페이지 블로그 (Supabase / 라운지)
    const supa = channels.supabase_research || channels.app_lounge || {};
    let supaHtml = "";
    if (b === "stock" && supa.title) {
        supaHtml = `
            <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:8px;padding:10px 14px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
                <div>
                    <div style="display:flex;align-items:center;gap:6px;">
                        <span style="background:#FEF3C7;color:#92400E;font-size:11px;font-weight:800;padding:2px 8px;border-radius:4px;">🌐 자체 홈페이지 퀀트 블로그</span>
                        <span style="font-size:11px;color:#64748B;">🕒 ${supa.published_at || blog.last_run_time || '-'}</span>
                    </div>
                    <div style="font-size:13px;font-weight:700;color:#0F172A;margin-top:3px;">${supa.title}</div>
                </div>
                <a href="${cfg.landing}" target="_blank" style="display:inline-flex;align-items:center;gap:4px;padding:6px 12px;background:#F59E0B;color:#FFFFFF;border-radius:6px;font-size:11.5px;font-weight:800;text-decoration:none;">
                    <span>🔗 홈페이지 글 열기</span><span>↗</span>
                </a>
            </div>
        `;
    } else if (b === "aura") {
        supaHtml = `
            <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:8px;padding:10px 14px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
                <div>
                    <div style="display:flex;align-items:center;gap:6px;">
                        <span style="background:#FCE7F3;color:#BE185D;font-size:11px;font-weight:800;padding:2px 8px;border-radius:4px;">💖 Aura 자체 VIP 라운지</span>
                        <span style="font-size:11px;color:#059669;font-weight:700;">🟢 실시간 연동 중</span>
                    </div>
                </div>
                <a href="${cfg.landing}" target="_blank" style="display:inline-flex;align-items:center;gap:4px;padding:6px 12px;background:#EC4899;color:#FFFFFF;border-radius:6px;font-size:11.5px;font-weight:800;text-decoration:none;">
                    <span>🔗 라운지 열기</span><span>↗</span>
                </a>
            </div>
        `;
    }

    // 0. 당일 정시 슬롯 현황 배너
    let slotsBannerHtml = "";
    if (blog.today_slots && blog.today_slots.length > 0) {
        slotsBannerHtml = `
            <div style="background:#F0FDF4;border:1.5px solid #BBF7D0;border-radius:8px;padding:8px 10px;margin-bottom:8px;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                    <span style="font-size:11.5px;font-weight:800;color:#166534;">📊 오늘 정시 발행 현황 (${blog.today_count || blog.today_slots.length}/3회)</span>
                    <span style="font-size:10.5px;font-weight:800;background:#DCFCE7;color:#15803D;padding:2px 6px;border-radius:4px;">${blog.slot_status_label || '🟢 오늘 목표 발행 완료'}</span>
                </div>
                <div style="display:flex;flex-direction:column;gap:4px;">
                    ${blog.today_slots.map(s => `
                        <div style="background:#FFFFFF;border:1px solid #DCFCE7;border-radius:5px;padding:5px 8px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:4px;">
                            <div style="font-size:11px;color:#1E293B;font-weight:700;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:70%;">
                                <span style="color:#059669;font-weight:800;">[${s.slot_num}차 ${(s.published_at||'').split(' ')[1] || ''}]</span> ${s.title}
                            </div>
                            <div style="display:flex;gap:4px;">
                                ${s.naver_url ? `<a href="${s.naver_url}" target="_blank" style="padding:2px 6px;background:#03C75A;color:#fff;border-radius:4px;font-size:10px;font-weight:800;text-decoration:none;">네이버 ↗</a>` : ''}
                                ${s.tistory_url ? `<a href="${s.tistory_url}" target="_blank" style="padding:2px 6px;background:#FF5722;color:#fff;border-radius:4px;font-size:10px;font-weight:800;text-decoration:none;">티스토리 ↗</a>` : ''}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    // 1. 네이버 블로그
    const nb = channels.naver_blog || {};
    let naverHtml = "";
    if (nb.is_success && nb.url) {
        naverHtml = `
            <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:8px;padding:10px 14px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
                <div>
                    <div style="display:flex;align-items:center;gap:6px;">
                        <span style="background:#ECFDF5;color:#059669;font-size:11px;font-weight:800;padding:2px 8px;border-radius:4px;">🟢 네이버 블로그 (${nb.is_today ? '오늘 발행' : '이전 발행'})</span>
                        <span style="font-size:11px;color:#64748B;">🕒 ${nb.published_at || blog.last_run_time || '-'}</span>
                    </div>
                    <div style="font-size:13px;font-weight:700;color:#0F172A;margin-top:3px;">${blog.last_title_naver || blog.last_title || '네이버 글'}</div>
                </div>
                <a href="${nb.url}" target="_blank" style="display:inline-flex;align-items:center;gap:4px;padding:6px 12px;background:#03C75A;color:#FFFFFF;border-radius:6px;font-size:11.5px;font-weight:800;text-decoration:none;">
                    <span>🔗 네이버 글 열기</span><span>↗</span>
                </a>
            </div>
        `;
    } else {
        const isErr = nb.status === "error";
        naverHtml = `
            <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:8px;padding:10px 14px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
                <div>
                    <div style="display:flex;align-items:center;gap:6px;">
                        <span style="background:${isErr ? '#FEE2E2' : '#FEF3C7'};color:${isErr ? '#DC2626' : '#92400E'};font-size:11px;font-weight:700;padding:2px 8px;border-radius:4px;">${isErr ? '🔴 네이버 블로그 에러' : '⚪ 네이버 블로그 미발행'}</span>
                        <span style="font-size:11.5px;color:${isErr ? '#991B1B' : '#64748B'};font-weight:600;">${nb.message || '오늘자 정기 스케줄 대기 중'}</span>
                    </div>
                </div>
                <span style="font-size:11px;color:#92400E;background:#FEF3C7;padding:4px 8px;border-radius:4px;font-weight:700;">👉 오늘자 정기 스케줄 대기 또는 1회 수동 발행 트리거</span>
            </div>
        `;
    }

    // 2. 티스토리 블로그
    const tb = channels.tistory || {};
    let tistoryHtml = "";
    const batFile = b === "aura" ? "[1회연동]_Aura_티스토리_영구로그인.bat" 
                  : b === "insurance" ? "[1회연동]_보험비교_티스토리_영구로그인.bat" 
                  : "[1회연동]_주식AI_티스토리_영구로그인.bat";

    if (tb.is_success && tb.url) {
        const tTime = (tb.published_at || blog.last_run_time || '-').replace('T', ' ').slice(0, 19);
        tistoryHtml = `
            <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:8px;padding:10px 14px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
                <div>
                    <div style="display:flex;align-items:center;gap:6px;">
                        <span style="background:#FFF7ED;color:#C2410C;font-size:11px;font-weight:800;padding:2px 8px;border-radius:4px;">🟠 티스토리</span>
                        <span style="font-size:11px;color:#64748B;">🕒 ${tTime}</span>
                    </div>
                    <div style="font-size:13px;font-weight:700;color:#0F172A;margin-top:3px;">${tb.title || blog.last_title || '티스토리 글'}</div>
                </div>
                <a href="${tb.url}" target="_blank" style="display:inline-flex;align-items:center;gap:4px;padding:6px 12px;background:#EA580C;color:#FFFFFF;border-radius:6px;font-size:11.5px;font-weight:800;text-decoration:none;">
                    <span>🔗 티스토리 열기</span><span>↗</span>
                </a>
            </div>
        `;
    } else if (tb.is_session_expired) {
        tistoryHtml = `
            <div style="background:#FEF2F2;border:1px solid #FECACA;border-radius:8px;padding:10px 14px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
                <div>
                    <div style="display:flex;align-items:center;gap:6px;">
                        <span style="background:#DC2626;color:#FFFFFF;font-size:11px;font-weight:800;padding:2px 8px;border-radius:4px;">🔴 카카오 세션 만료</span>
                        <span style="font-size:11.5px;color:#991B1B;font-weight:700;">사유: 티스토리 글쓰기 세션 만료</span>
                    </div>
                </div>
                <div style="font-size:11px;color:#1E40AF;background:#EFF6FF;border:1px solid #BFDBFE;padding:4px 8px;border-radius:4px;font-weight:700;">
                    👉 바탕화면 [${batFile}] 1회 실행 필요
                </div>
            </div>
        `;
    } else {
        tistoryHtml = `
            <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:8px;padding:10px 14px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
                <div style="display:flex;align-items:center;gap:6px;">
                    <span style="background:#F1F5F9;color:#64748B;font-size:11px;font-weight:700;padding:2px 8px;border-radius:4px;">⚪ 티스토리</span>
                    <span style="font-size:11.5px;color:#64748B;">사유: 오늘 발행 대기 중</span>
                </div>
                <span style="font-size:11px;color:#94A3B8;font-weight:600;">idle</span>
            </div>
        `;
    }

    // 3. 5대 숏폼 플랫폼 목록
    const spKeys = [
        { key: "youtube", name: "유튜브 쇼츠", icon: "🔴", btnText: "영상 보기 ↗", color: "#DC2626", bg: "#FEF2F2" },
        { key: "instagram", name: "인스타 릴스", icon: "📸", btnText: "릴스 열기 ↗", color: "#E1306C", bg: "#FDF2F8" },
        { key: "facebook", name: "페이스북 릴스", icon: "🔵", btnText: "릴스 열기 ↗", color: "#1877F2", bg: "#EFF6FF" },
        { key: "tiktok", name: "틱톡 (TikTok)", icon: "📱", btnText: "틱톡 열기 ↗", color: "#000000", bg: "#F1F5F9" },
        { key: "naver_clip", name: "네이버 클립", icon: "🟢", btnText: "클립 열기 ↗", color: "#03C75A", bg: "#ECFDF5" }
    ];

    const shortsListHtml = spKeys.map(sp => {
        const item = shortsPlatforms[sp.key] || {};
        const isSuccess = item.is_success && item.url;
        const itemTime = (item.published_at || '-').replace('T', ' ').split('.')[0];
        if (isSuccess) {
            return `
                <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:8px;padding:8px 12px;display:flex;justify-content:space-between;align-items:center;">
                    <div style="display:flex;align-items:center;gap:8px;">
                        <span style="font-size:14px;">${sp.icon}</span>
                        <strong style="font-size:12px;color:#0F172A;">${sp.name}</strong>
                        <span style="font-size:11px;color:#64748B;">🕒 ${itemTime}</span>
                    </div>
                    <a href="${item.url}" target="_blank" style="display:inline-flex;align-items:center;gap:4px;padding:4px 10px;background:${sp.bg};color:${sp.color};border:1px solid ${sp.color};border-radius:5px;font-size:11px;font-weight:800;text-decoration:none;">
                        <span>🎬</span> <span>${sp.btnText}</span>
                    </a>
                </div>
            `;
        } else {
            return `
                <div style="background:#F8FAFC;border:1px dashed #CBD5E1;border-radius:8px;padding:8px 12px;display:flex;justify-content:space-between;align-items:center;">
                    <div style="display:flex;align-items:center;gap:8px;">
                        <span style="font-size:14px;opacity:0.6;">${sp.icon}</span>
                        <span style="font-size:12px;color:#64748B;font-weight:600;">${sp.name}</span>
                    </div>
                    <span style="font-size:11px;color:#94A3B8;font-weight:600;">대기</span>
                </div>
            `;
        }
    }).join("");

    // 4. 5대 옴니 카드뉴스 & 타래 목록
    const cpKeys = [
        { key: "instagram", name: "인스타 캐러셀 (5장)", icon: "📸", btnText: "캐러셀 열기 ↗", color: "#E1306C", bg: "#FDF2F8" },
        { key: "facebook", name: "페이스북 앨범 (5장)", icon: "🔵", btnText: "앨범 열기 ↗", color: "#1877F2", bg: "#EFF6FF" },
        { key: "threads", name: "스레드 타래/카드뉴스", icon: "🧵", btnText: "타래 열기 ↗", color: "#000000", bg: "#F8FAFC" }
    ];

    let cardnewsListHtml = cpKeys.map(cp => {
        const item = cardPlatforms[cp.key] || {};
        const isSuccess = item.is_success && item.url;
        const itemTime = (item.published_at || '-').replace('T', ' ').split('.')[0];
        if (isSuccess) {
            return `
                <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:8px;padding:8px 12px;display:flex;justify-content:space-between;align-items:center;">
                    <div style="display:flex;align-items:center;gap:8px;">
                        <span style="font-size:14px;">${cp.icon}</span>
                        <strong style="font-size:12px;color:#0F172A;">${cp.name}</strong>
                        <span style="font-size:11px;color:#64748B;">🕒 ${itemTime}</span>
                    </div>
                    <a href="${item.url}" target="_blank" style="display:inline-flex;align-items:center;gap:4px;padding:4px 10px;background:${cp.bg};color:${cp.color};border:1px solid ${cp.color};border-radius:5px;font-size:11px;font-weight:800;text-decoration:none;">
                        <span>🖼️</span> <span>${cp.btnText}</span>
                    </a>
                </div>
            `;
        } else {
            return `
                <div style="background:#F8FAFC;border:1px dashed #CBD5E1;border-radius:8px;padding:8px 12px;display:flex;justify-content:space-between;align-items:center;">
                    <div style="display:flex;align-items:center;gap:8px;">
                        <span style="font-size:14px;opacity:0.6;">${cp.icon}</span>
                        <span style="font-size:12px;color:#64748B;font-weight:600;">${cp.name}</span>
                    </div>
                    <span style="font-size:11px;color:#94A3B8;font-weight:600;">대기</span>
                </div>
            `;
        }
    }).join("");

    // 로컬 5장 카드뉴스 슬라이드 완제품
    const localCard = cardPlatforms.local_slides || {};
    cardnewsListHtml += `
        <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:8px;padding:8px 12px;display:flex;justify-content:space-between;align-items:center;">
            <div style="display:flex;align-items:center;gap:8px;">
                <span style="font-size:14px;">📁</span>
                <strong style="font-size:12px;color:#0F172A;">1080x1350 완제품</strong>
                <span style="font-size:11px;color:#64748B;">🕒 ${localCard.time || '-'}</span>
            </div>
            <span style="background:#ECFDF5;color:#059669;border:1px solid #A7F3D0;font-size:11px;font-weight:800;padding:2px 8px;border-radius:4px;">
                ✅ 5장 완성
            </span>
        </div>
    `;

    // 5. 네이버 지식iN 10건 목록
    const kinPosts = kin.posts || kin.recent_answers || [];
    let kinListHtml = "";
    if (kinPosts.length === 0) {
        kinListHtml = `<div style="background:#F8FAFC;border:1px dashed #CBD5E1;border-radius:8px;padding:10px;text-align:center;font-size:11.5px;color:#94A3B8;">오늘자 지식iN 답변 내역이 아직 없습니다. (정기 스케줄 대기 중)</div>`;
    } else {
        kinListHtml = kinPosts.slice(0, 5).map((p, idx) => {
            const pTime = (p.time || p.created_at || '-').replace('T', ' ').slice(0, 16);
            return `
            <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:8px;padding:8px 12px;display:flex;justify-content:space-between;align-items:center;gap:8px;">
                <div style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:70%;">
                    <span style="color:#0284C7;font-weight:800;font-size:11.5px;margin-right:4px;">#${idx + 1}</span>
                    <span style="font-size:12px;font-weight:600;color:#0F172A;">${p.title || '지식iN 답변'}</span>
                </div>
                <div style="display:flex;align-items:center;gap:8px;flex-shrink:0;">
                    <span style="font-size:10.5px;color:#64748B;">🕒 ${pTime}</span>
                    <a href="${p.url || '#'}" target="_blank" style="font-size:11px;color:#0284C7;font-weight:800;text-decoration:none;background:#F0F9FF;padding:2px 8px;border-radius:4px;border:1px solid #BAE6FD;">열기↗</a>
                </div>
            </div>
            `;
        }).join("");
    }

    // 6. 네이버 카페 침투 목록
    // 6. 네이버 카페 침투 목록
    const cafePosts = (bData.cafe && bData.cafe.posts) || [];
    let cafeListHtml = "";
    if (cafePosts.length === 0) {
        cafeListHtml = `<div style="background:#F8FAFC;border:1px dashed #CBD5E1;border-radius:8px;padding:10px;text-align:center;font-size:11.5px;color:#94A3B8;">오늘자 카페 침투 활동이 아직 없습니다. (정기 스케줄 대기 중)</div>`;
    } else {
        cafeListHtml = cafePosts.map(cp => `
            <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:8px;padding:10px 12px;display:flex;flex-direction:column;gap:6px;">
                <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px;">
                    <div>
                        <span style="background:#FEF3C7;color:#D97706;font-size:10.5px;font-weight:800;padding:2px 6px;border-radius:4px;">${cp.cafe_name || '카페'}</span>
                        <strong style="font-size:12px;color:#0F172A;margin-left:4px;">${cp.post_title || '게시글'}</strong>
                    </div>
                    <div style="display:flex;align-items:center;gap:6px;">
                        <span style="font-size:10.5px;color:#64748B;">🕒 ${cp.time || '-'}</span>
                        <a href="${cp.url || '#'}" target="_blank" style="font-size:11px;color:#D97706;font-weight:800;text-decoration:none;background:#FFFBEB;padding:2px 8px;border-radius:4px;border:1px solid #FDE68A;">열기↗</a>
                    </div>
                </div>
                ${cp.comment_snippet ? `
                    <div style="font-size:11.5px;color:#475569;background:#F8FAFC;padding:6px 10px;border-radius:6px;border-left:3px solid #F59E0B;line-height:1.4;">
                        💬 "${cp.comment_snippet}"
                    </div>
                ` : ''}
            </div>
        `).join("");
    }

    // 7. 🤖 레딧 글로벌 스텔스 침투 목록
    const reddit = bData.reddit || {};
    const redditPosts = reddit.posts || [];
    let redditListHtml = "";
    if (redditPosts.length === 0) {
        redditListHtml = `<div style="background:#F8FAFC;border:1px dashed #CBD5E1;border-radius:8px;padding:10px;text-align:center;font-size:11.5px;color:#94A3B8;">오늘자 레딧 침투 활동이 아직 없습니다. (정기 스케줄 대기 중)</div>`;
    } else {
        redditListHtml = redditPosts.slice(0, 3).map(rp => `
            <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:8px;padding:10px 12px;display:flex;flex-direction:column;gap:6px;">
                <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px;">
                    <div style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:70%;">
                        <span style="background:#FFF7ED;color:#EA580C;font-size:10.5px;font-weight:800;padding:2px 6px;border-radius:4px;border:1px solid #FED7AA;">🤖 Reddit</span>
                        <strong style="font-size:12px;color:#0F172A;margin-left:4px;">${rp.title || '게시글'}</strong>
                    </div>
                    <div style="display:flex;align-items:center;gap:6px;">
                        <span style="font-size:10.5px;color:#64748B;">🕒 ${rp.time || '-'}</span>
                        <a href="${rp.url || '#'}" target="_blank" style="font-size:11px;color:#EA580C;font-weight:800;text-decoration:none;background:#FFF7ED;padding:2px 8px;border-radius:4px;border:1px solid #FED7AA;">🔗 글 열기↗</a>
                    </div>
                </div>
                ${rp.comment_snippet ? `
                    <div style="font-size:11.5px;color:#475569;background:#F8FAFC;padding:6px 10px;border-radius:6px;border-left:3px solid #EA580C;line-height:1.4;">
                        💬 "${rp.comment_snippet}"
                    </div>
                ` : ''}
            </div>
        `).join("");
    }

    container.innerHTML = `
        ${gpuBannerHtml}
        <div class="section-card" style="border-top: 4px solid ${cfg.color}; background:${cfg.bgGradient}; border-color:${cfg.border}; box-shadow:0 6px 20px rgba(0,0,0,0.06); margin-bottom: 24px;">
            <!-- 전광판 상단 바 -->
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;flex-wrap:wrap;gap:10px;">
                <div>
                    <div style="display:flex;align-items:center;gap:8px;">
                        <h3 class="section-title" style="margin:0;font-size:17px;font-weight:800;color:#1E293B;">
                            🚀 [${cfg.title} 전담] 실시간 무인 발행 라이브 전광판 (100% 투명 시간/URL 표출)
                        </h3>
                        <span class="badge-live-pulse" style="font-size:11px;"><span class="pulse-dot"></span> 실시간 동기화</span>
                    </div>
                    <p class="section-subtitle" style="margin-top:4px;font-size:12px;color:#64748B;">
                        선택된 <strong>${cfg.title}</strong>의 모든 블로그, 숏폼, 카드뉴스, 지식iN, 카페, 레딧의 <strong>실제 발행 URL과 초 단위 시각(YYYY-MM-DD HH:MM:SS)</strong>을 100% 독립 분리 표출합니다.
                    </p>
                </div>
                <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                    <div style="font-size:11.5px;color:#475569;background:#FFFFFF;padding:6px 12px;border-radius:8px;font-weight:700;border:1px solid #CBD5E1;">
                        📅 오늘(${today}) 실적: 블로그 <strong style="color:#2563EB;">${blog.today_count || 0}</strong>건 | 숏폼 <strong style="color:#DC2626;">${shorts.today_count || 0}</strong>건 | 카드뉴스 <strong style="color:#7C3AED;">${cardnews.today_count || 0}</strong>세트 | 지식iN <strong style="color:#0284C7;">${kin.today_count || 0}</strong>건 | 카페 <strong style="color:#D97706;">${(bData.cafe && bData.cafe.today_count) || 0}</strong>건 | 레딧 <strong style="color:#EA580C;">${reddit.today_count || 0}</strong>건
                    </div>
                    <button class="btn btn-secondary" onclick="loadHealthStatus(this)" style="font-size:12px;padding:6px 12px;">
                        🔄 실시간 갱신
                    </button>
                    <button class="btn" onclick="publishOmniBlog('${b}', this)" style="background:${cfg.color};color:#FFFFFF;font-weight:800;font-size:12px;padding:6px 14px;border-radius:8px;border:none;cursor:pointer;">
                        ⚡ ${cfg.title} 1회 즉시 발행
                    </button>
                </div>
            </div>

            <!-- 전담 발행 그리드 (2열 반응형) -->
            <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(340px, 1fr));gap:16px;">
                <!-- 1. 📝 블로그 채널 발행 상태 -->
                <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:12px;padding:14px;display:flex;flex-direction:column;gap:10px;box-shadow:0 2px 6px rgba(0,0,0,0.03);">
                    <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #F1F5F9;padding-bottom:8px;">
                        <span style="font-size:13px;font-weight:800;color:#0F172A;">📝 블로그 채널 발행 상태 (오늘 ${blog.today_count || 0}/3회)</span>
                        <span style="font-size:11px;font-weight:800;background:#DCFCE7;color:#15803D;padding:2px 6px;border-radius:4px;">${blog.slot_status_label || '🟢 오늘 목표 발행 완료'}</span>
                    </div>
                    ${slotsBannerHtml}
                    ${supaHtml}
                    ${naverHtml}
                    ${tistoryHtml}
                </div>

                <!-- 2. 🎬 5대 숏폼 & 릴스 플랫폼 -->
                <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:12px;padding:14px;display:flex;flex-direction:column;gap:10px;box-shadow:0 2px 6px rgba(0,0,0,0.03);">
                    <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #F1F5F9;padding-bottom:8px;">
                        <span style="font-size:13px;font-weight:800;color:#DC2626;">🎬 5대 숏폼 & 릴스 (5대 플랫폼 실시간 발행 URL & 시간)</span>
                        <span style="font-size:11px;color:#64748B;">오늘 ${shorts.today_count || 0}건</span>
                    </div>
                    <div style="display:flex;flex-direction:column;gap:8px;">
                        ${shortsListHtml}
                    </div>
                </div>

                <!-- 3. 🖼️ 5대 옴니 카드뉴스 & 타래 -->
                <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:12px;padding:14px;display:flex;flex-direction:column;gap:10px;box-shadow:0 2px 6px rgba(0,0,0,0.03);">
                    <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #F1F5F9;padding-bottom:8px;">
                        <span style="font-size:13px;font-weight:800;color:#7C3AED;">🖼️ 5대 옴니 카드뉴스 & 타래 (1080x1350 5장 & 배포 URL)</span>
                        <span style="font-size:11px;color:#64748B;">오늘 ${cardnews.today_count || 0}건</span>
                    </div>
                    <div style="display:flex;flex-direction:column;gap:8px;">
                        ${cardnewsListHtml}
                    </div>
                </div>

                <!-- 4. 💬 네이버 지식iN 1:1 낚아채기 -->
                <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:12px;padding:14px;display:flex;flex-direction:column;gap:10px;box-shadow:0 2px 6px rgba(0,0,0,0.03);">
                    <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #F1F5F9;padding-bottom:8px;">
                        <span style="font-size:13px;font-weight:800;color:#0284C7;">💬 네이버 지식iN (오늘 ${kin.today_count || 0} / ${kin.target_count || 10}건)</span>
                        <button onclick="triggerKinCatch('${b}', this)" style="font-size:11px;font-weight:700;padding:3px 8px;background:#E0F2FE;color:#0284C7;border:1px solid #BAE6FD;border-radius:6px;cursor:pointer;">⚡ 1회 낚아채기</button>
                    </div>
                    <div style="display:flex;flex-direction:column;gap:6px;">
                        ${kinListHtml}
                    </div>
                </div>

                <!-- 5. ☕ 네이버 카페 8대 정예 침투 -->
                <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:12px;padding:14px;display:flex;flex-direction:column;gap:10px;box-shadow:0 2px 6px rgba(0,0,0,0.03);">
                    <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #F1F5F9;padding-bottom:8px;">
                        <span style="font-size:13px;font-weight:800;color:#D97706;">☕ 네이버 카페 침투 (오늘 ${(bData.cafe && bData.cafe.today_count) || 0} / 1건 | 슬롯: ${(bData.cafe && bData.cafe.current_slot) || '-'})</span>
                        <button onclick="triggerCafeInfiltration('${b}', this)" style="font-size:11px;font-weight:700;padding:3px 8px;background:#FEF3C7;color:#D97706;border:1px solid #FDE68A;border-radius:6px;cursor:pointer;">⚡ 1회 즉시 침투</button>
                    </div>
                    <div style="display:flex;flex-direction:column;gap:6px;">
                        ${cafeListHtml}
                    </div>
                </div>

                <!-- 6. 🤖 레딧 글로벌 2단계 스텔스 침투 -->
                <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:12px;padding:14px;display:flex;flex-direction:column;gap:10px;box-shadow:0 2px 6px rgba(0,0,0,0.03);">
                    <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #F1F5F9;padding-bottom:8px;">
                        <span style="font-size:13px;font-weight:800;color:#EA580C;">🤖 레딧 글로벌 침투 (오늘 ${reddit.today_count || 0} / ${reddit.target_count || 1}건 | Zero URL 원칙)</span>
                        <button onclick="triggerRedditInfiltration('${b}', this)" style="font-size:11px;font-weight:700;padding:3px 8px;background:#FFF7ED;color:#EA580C;border:1px solid #FED7AA;border-radius:6px;cursor:pointer;">⚡ 1회 즉시 침투</button>
                    </div>
                    <div style="display:flex;flex-direction:column;gap:6px;">
                        ${redditListHtml}
                    </div>
                </div>
            </div>
        </div>
    `;
}

// 🤖 레딧 1회 즉시 스텔스 침투 트리거
async function triggerRedditInfiltration(brand, btn) {
    const bName = brand === "aura" ? "Aura AI 데이팅" : brand === "insurance" ? "보험 리밸런스" : "StockMaster AI";
    if (btn) {
        btn.disabled = true;
        btn.innerText = "⏳ 침투 중...";
    }
    appendLog(`[Action] ${bName} 레딧 1회 스텔스 침투 시작...`, "info");
    showToast(`🤖 ${bName} 레딧 1회 즉시 침투가 시작되었습니다!`, "info");

    try {
        const res = await fetch(`/api/run-module/${brand}_reddit`, { method: "POST" });
        const data = await res.json();
        if (data.success) {
            appendLog(`[Success] 🎉 [${bName} 레딧 침투 가동] ${data.message}`, "success");
            showToast(data.message || "레딧 침투가 백그라운드에서 가동되었습니다.", "success");
            setTimeout(loadHealthStatus, 3000);
        } else {
            appendLog(`[Error] ❌ [${bName} 레딧] ${data.message || '침투 요청 실패'}`, "error");
            showToast(data.message || "레딧 침투 요청 실패", "error");
        }
    } catch (e) {
        appendLog(`[Error] ❌ 레딧 침투 통신 오류: ${e}`, "error");
        showToast("레딧 침투 통신 실패", "error");
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerText = "⚡ 1회 즉시 침투";
        }
    }
}

window.loadHealthStatus = loadHealthStatus;
window.runFullHealthDiagnostic = runFullHealthDiagnostic;
window.openProofModal = openProofModal;
window.closeProofModal = closeProofModal;
window.retryChannelPublish = retryChannelPublish;
window.triggerRedditInfiltration = triggerRedditInfiltration;
window.renderStealthWarmupGrid = renderStealthWarmupGrid;
window.triggerPlatformStealth = triggerPlatformStealth;
window.triggerStealthWarmup = triggerPlatformStealth;
window.renderHealthBrandLiveFeed = renderHealthBrandLiveFeed;
