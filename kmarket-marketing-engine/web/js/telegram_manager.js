// ==========================================
// [모듈] telegram_manager.js: 텔레그램 24시간 자율 성장 통합 사령부 (브랜드별 독립)
// 대형 통합 컨테이너 카드 내 3대 핵심 기능 (AI 매니저/브리핑 | 타 그룹 홍보 | 스텔스 초대) 100% 통합
// ==========================================

async function loadTelegramCommunityStats() {
    try {
        const brand = typeof currentBrand !== 'undefined' ? currentBrand : 'kmarket';
        const [statsResp, outreachResp] = await Promise.all([
            fetch(`/api/telegram/stats?brand=${brand}`),
            fetch('/api/telegram/outreach/status', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ brand })
            })
        ]);
        const stats    = await statsResp.json();
        const outreach = await outreachResp.json();
        renderTelegramCommunityPanel(stats, outreach);
    } catch (e) {
        console.error('텔레그램 통계 로드 실패:', e);
    }
}

function renderTelegramCommunityPanel(stats, outreach) {
    const container = document.getElementById('telegram-community-panel-container');
    if (!container) return;

    const brand      = stats.brand || (typeof currentBrand !== 'undefined' ? currentBrand : 'stock');
    let brandTitle = '📈 Stock Master';
    let brandColor = '#F59E0B';
    let groupName  = 'Stock Master VIP 시황 (t.me/stockmaster_vip)';
    let brandDesc  = '외인/기관 실시간 수급 분석 · 장전 08:30 브리핑 · 조건검색식 · 하루 2회 정기 증시 브리핑';

    if (brand === 'aura') {
        brandTitle = '💖 Aura 데이팅';
        brandColor = '#EC4899';
        groupName  = 'Aura Dating VIP (t.me/aura_dating_official)';
        brandDesc  = '2030 솔로 미팅 & 소개팅 코칭 · 실시간 Q&A · 주말 매칭 알림';
    } else if (brand === 'insurance') {
        brandTitle = '🛡️ InsureBalance';
        brandColor = '#10B981';
        groupName  = 'InsureBalance 케어 (t.me/insurebalance_official)';
        brandDesc  = '실손보험 비교 & �    container.innerHTML = `
        <!-- ━━━ 📱 [메인 사령부] 텔레그램 24시간 자율 성장 통합 센터 ━━━ -->
        <div class="card" style="background:#FFFFFF;border:1px solid #E2E8F0;border-top:4px solid ${brandColor};border-radius:16px;padding:22px;margin-bottom:24px;box-shadow:0 4px 16px rgba(0,0,0,0.06);">
            
            <!-- 상단 헤더: 브랜드 공식 그룹 & 전체 상태 요약 -->
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:18px;flex-wrap:wrap;gap:12px;border-bottom:1px solid #E2E8F0;padding-bottom:14px;">
                <div style="display:flex;align-items:center;gap:12px;">
                    <span style="font-size:28px;background:#F1F5F9;padding:8px 10px;border-radius:12px;">📱</span>
                    <div>
                        <div style="display:flex;align-items:center;gap:8px;">
                            <h2 style="margin:0;font-size:16px;font-weight:800;color:#0F172A;">${brandTitle} 텔레그램 24시간 자율 성장 통합 사령부</h2>
                            <span style="font-size:11px;color:${brandColor};background:#F8FAFC;border:1px solid #E2E8F0;padding:2px 8px;border-radius:6px;font-weight:700;">공식 본진: ${groupName}</span>
                        </div>
                        <p style="margin:3px 0 0;font-size:11px;color:#64748B;">${brandDesc}</p>
                    </div>
                </div>
                <div style="display:flex;align-items:center;gap:8px;">
                    <span class="badge" style="background:${isRunning ? '#10B981' : '#64748B'};color:#fff;padding:5px 12px;border-radius:20px;font-size:11px;font-weight:bold;">
                        ${isRunning ? '🟢 24h AI 사령부 가동 중' : '⏸️ 24h 사령부 대기 중'}
                    </span>
                    <span class="badge" style="background:${sessionReady ? 'rgba(56,189,248,0.15)' : 'rgba(239,68,68,0.15)'};color:${sessionReady ? '#0284C7' : '#DC2626'};border:1px solid ${sessionReady ? '#0284C7' : '#DC2626'};padding:5px 12px;border-radius:20px;font-size:11px;font-weight:bold;">
                        ${sessionReady ? '🟢 서브폰 세션 연동' : '🔴 서브폰 미연동'}
                    </span>
                </div>
            </div>

            <!-- ━━━ 3열 가로 일체형 서브 카드 그리드 ━━━ -->
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:14px;">
                
                <!-- ━━━ [1열] 24시간 AI 매니저 & 일일 브리핑 ━━━ -->
                <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-top:3px solid ${brandColor};border-radius:12px;padding:16px;display:flex;flex-direction:column;justify-content:space-between;box-shadow:0 2px 8px rgba(0,0,0,0.05);">
                    <div>
                        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">
                            <div style="display:flex;align-items:center;gap:8px;">
                                <span style="font-size:20px;">🤖</span>
                                <div>
                                    <h4 style="margin:0;font-size:13.5px;font-weight:700;color:#0F172A;">24시간 AI 지킴이 & 브리핑</h4>
                                    <div style="font-size:10px;color:#64748B;">17개국 환영 · Q&A · 08:40/20:00 푸시</div>
                                </div>
                            </div>
                            <span style="font-size:10px;padding:2px 7px;border-radius:10px;background:${isRunning?'rgba(16,185,129,0.15)':'#F1F5F9'};color:${isRunning?'#059669':'#64748B'};font-weight:700;">
                                ${isRunning ? '🟢 가동 중' : '⚪ 대기'}
                            </span>
                        </div>

                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:12px;">
                            <div style="background:#F8FAFC;border:1px solid #E2E8F0;padding:8px 10px;border-radius:6px;">
                                <div style="font-size:9.5px;color:#64748B;font-weight:600;">🤖 AI 질문 답변</div>
                                <div style="font-size:15px;color:#0284C7;font-weight:bold;margin-top:2px;">${ai.total_ai_replies||0} <span style="font-size:10px;color:#64748B;">건</span></div>
                            </div>
                            <div style="background:#F8FAFC;border:1px solid #E2E8F0;padding:8px 10px;border-radius:6px;">
                                <div style="font-size:9.5px;color:#64748B;font-weight:600;">👋 모국어 환영</div>
                                <div style="font-size:15px;color:#059669;font-weight:bold;margin-top:2px;">${ai.total_welcomed||0} <span style="font-size:10px;color:#64748B;">명</span></div>
                            </div>
                        </div>
                    </div>

                    <div>
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:6px;">
                            <button onclick="startTelegramAIManager()" style="background:#10B981;color:#fff;border:none;padding:7px 4px;border-radius:6px;font-size:11px;font-weight:bold;cursor:pointer;">
                                🚀 무인 가동
                            </button>
                            <button onclick="stopTelegramAIManager()" style="background:#EF4444;color:#fff;border:none;padding:7px 4px;border-radius:6px;font-size:11px;font-weight:bold;cursor:pointer;">
                                ⏹️ 정지
                            </button>
                        </div>
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;">
                            <button onclick="triggerTelegramBroadcast('morning_briefing')" style="background:#0284C7;color:#FFFFFF;border:none;padding:6px 4px;border-radius:6px;font-size:10.5px;font-weight:bold;cursor:pointer;">
                                ⚡ ${isKm ? '0원 나눔' : '세무 환급'} 브리핑
                            </button>
                            <button onclick="triggerTelegramBroadcast('poll')" style="background:#F5F3FF;border:1px solid #C4B5FD;color:#7C3AED;padding:6px 0;border-radius:6px;font-size:10.5px;font-weight:bold;cursor:pointer;">
                                📊 투표 1회 생성
                            </button>
                        </div>
                    </div>
                </div>

                <!-- ━━━ [2열] 타 그룹 홍보 게시 (Ban 위험 0%) ━━━ -->
                <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-top:3px solid #38BDF8;border-radius:12px;padding:16px;display:flex;flex-direction:column;justify-content:space-between;box-shadow:0 2px 8px rgba(0,0,0,0.05);">
                    <div>
                        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">
                            <div style="display:flex;align-items:center;gap:8px;">
                                <span style="font-size:20px;">📢</span>
                                <div>
                                    <h4 style="margin:0;font-size:13.5px;font-weight:700;color:#0F172A;">타 그룹 홍보 아웃리치</h4>
                                    <div style="font-size:10px;color:#64748B;">8개국어 현지화 · 5일 로테이션 (안전 100%)</div>
                                </div>
                            </div>
                            <span style="font-size:10px;padding:2px 7px;border-radius:10px;background:${sessionReady?'rgba(16,185,129,0.15)':'rgba(239,68,68,0.15)'};color:${sessionReady?'#059669':'#DC2626'};font-weight:700;">
                                ${sessionReady ? '🟢 서브폰' : '🔴 미연동'}
                            </span>
                        </div>

                        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:4px;margin-bottom:12px;">
                            <div style="background:#F8FAFC;border:1px solid #E2E8F0;padding:8px 4px;border-radius:6px;text-align:center;">
                                <div style="font-size:9px;color:#64748B;font-weight:600;">📢 총 게시</div>
                                <div style="font-size:14px;color:#0284C7;font-weight:bold;margin-top:2px;">${ot.total_posts||0} <span style="font-size:9px;color:#64748B;">회</span></div>
                            </div>
                            <div style="background:#F8FAFC;border:1px solid #E2E8F0;padding:8px 4px;border-radius:6px;text-align:center;">
                                <div style="font-size:9px;color:#64748B;font-weight:600;">🌐 게시 가능</div>
                                <div style="font-size:14px;color:#059669;font-weight:bold;margin-top:2px;">${ot.eligible_groups_now||0} <span style="font-size:9px;color:#64748B;">/ ${ot.target_groups_total||10}</span></div>
                            </div>
                            <div style="background:#F8FAFC;border:1px solid #E2E8F0;padding:8px 4px;border-radius:6px;text-align:center;">
                                <div style="font-size:9px;color:#64748B;font-weight:600;">⏰ 간격</div>
                                <div style="font-size:14px;color:#7C3AED;font-weight:bold;margin-top:2px;">${ot.min_interval_days||5} <span style="font-size:9px;color:#64748B;">일</span></div>
                            </div>
                        </div>
                    </div>

                    <div>
                        <div style="display:grid;grid-template-columns:2fr 1fr;gap:6px;">
                            <button onclick="runOutreach()" style="background:#0284C7;color:#FFFFFF;border:none;padding:7px 4px;border-radius:6px;font-size:11px;font-weight:bold;cursor:pointer;">
                                📢 홍보 게시 1회 실행
                            </button>
                            <button onclick="stopOutreach()" style="background:#E2E8F0;color:#475569;border:none;padding:7px 4px;border-radius:6px;font-size:11px;font-weight:bold;cursor:pointer;">
                                ⏹️ 정지
                            </button>
                        </div>
                    </div>
                </div>

                <!-- ━━━ [3열] 서브폰 스텔스 초대 부스터 ━━━ -->
                <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-top:3px solid #F59E0B;border-radius:12px;padding:16px;display:flex;flex-direction:column;justify-content:space-between;box-shadow:0 2px 8px rgba(0,0,0,0.05);">
                    <div>
                        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">
                            <div style="display:flex;align-items:center;gap:8px;">
                                <span style="font-size:20px;">🕵️</span>
                                <div>
                                    <h4 style="margin:0;font-size:13.5px;font-weight:700;color:#0F172A;">서브폰 스텔스 초대 부스터</h4>
                                    <div style="font-size:10px;color:#64748B;">1일 5명 캡 · 15~30분 슬립 · 메인 계정 완벽 보호</div>
                                </div>
                            </div>
                            <span style="font-size:10px;padding:2px 7px;border-radius:10px;background:#FEF3C7;color:#B45309;font-weight:700;">
                                🚀 부스터
                            </span>
                        </div>

                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:12px;">
                            <div style="background:#F8FAFC;border:1px solid #E2E8F0;padding:8px 10px;border-radius:6px;">
                                <div style="font-size:9.5px;color:#64748B;font-weight:600;">🕵️ 오늘 초대</div>
                                <div style="font-size:15px;color:#D97706;font-weight:bold;margin-top:2px;">${scraper.today_invited||0} <span style="font-size:10px;color:#64748B;">/ 5명</span></div>
                            </div>
                            <div style="background:#F8FAFC;border:1px solid #E2E8F0;padding:8px 10px;border-radius:6px;">
                                <div style="font-size:9.5px;color:#64748B;font-weight:600;">🌐 타깃 그룹 풀</div>
                                <div style="font-size:15px;color:#7C3AED;font-weight:bold;margin-top:2px;">${scraper.target_groups_count||10} <span style="font-size:10px;color:#64748B;">개</span></div>
                            </div>
                        </div>
                    </div>

                    <div>
                        <div style="display:grid;grid-template-columns:2fr 1fr;gap:6px;">
                            <button onclick="runStealthInvite()" style="background:#D97706;color:#FFFFFF;border:none;padding:7px 4px;border-radius:6px;font-size:11px;font-weight:bold;cursor:pointer;">
                                🕵️ 스텔스 초대 1회 실행
                            </button>
                            <button onclick="stopStealthInvite()" style="background:#E2E8F0;color:#475569;border:none;padding:7px 4px;border-radius:6px;font-size:11px;font-weight:bold;cursor:pointer;">
                                ⏹️ 정지
                            </button>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    `;roups_count||10} <span style="font-size:10px;color:#64748B;">개</span></div>
                            </div>
                        </div>
                    </div>

                    <div>
                        <div style="display:grid;grid-template-columns:2fr 1fr;gap:6px;">
                            <button onclick="runStealthInvite()" style="background:#F59E0B;color:#0B1120;border:none;padding:7px 4px;border-radius:6px;font-size:11px;font-weight:bold;cursor:pointer;">
                                🕵️ 스텔스 초대 1회 실행
                            </button>
                            <button onclick="stopStealthInvite()" style="background:#334155;color:#CBD5E1;border:none;padding:7px 4px;border-radius:6px;font-size:11px;font-weight:bold;cursor:pointer;">
                                ⏹️ 정지
                            </button>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    `;
}

// ━━━ API 호출 함수 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async function startTelegramAIManager() {
    const brand = typeof currentBrand !== 'undefined' ? currentBrand : 'kmarket';
    const resp = await fetch('/api/telegram/toggle-manager', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ brand, action: 'start' })
    });
    const res = await resp.json();
    alert(res.message || '가동되었습니다.');
    loadTelegramCommunityStats();
}

async function stopTelegramAIManager() {
    const brand = typeof currentBrand !== 'undefined' ? currentBrand : 'kmarket';
    const resp = await fetch('/api/telegram/toggle-manager', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ brand, action: 'stop' })
    });
    const res = await resp.json();
    alert(res.message || '정지되었습니다.');
    loadTelegramCommunityStats();
}

async function triggerTelegramBroadcast(type) {
    const brand = typeof currentBrand !== 'undefined' ? currentBrand : 'kmarket';
    const resp = await fetch('/api/telegram/broadcast', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type, brand })
    });
    const res = await resp.json();
    alert(res.message || '발송되었습니다.');
    loadTelegramCommunityStats();
}

async function runOutreach() {
    const brand = typeof currentBrand !== 'undefined' ? currentBrand : 'kmarket';
    const resp = await fetch('/api/telegram/outreach/run', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ brand })
    });
    const res = await resp.json();
    alert(res.message || '홍보 게시 완료.');
    loadTelegramCommunityStats();
}

function stopOutreach() {
    alert('📢 타 그룹 홍보 자동 배포가 일시 정지(대기) 상태입니다.');
    loadTelegramCommunityStats();
}

async function runStealthInvite() {
    const brand = typeof currentBrand !== 'undefined' ? currentBrand : 'kmarket';
    const resp = await fetch('/api/telegram/stealth-invite', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ brand })
    });
    const res = await resp.json();
    alert(res.message || '초대 작업 실행.');
    loadTelegramCommunityStats();
}

function stopStealthInvite() {
    alert('🕵️ 서브폰 스텔스 초대가 일시 정지(대기) 상태입니다.');
    loadTelegramCommunityStats();
}

// 10초마다 자동 갱신
setInterval(loadTelegramCommunityStats, 10000);
document.addEventListener('DOMContentLoaded', loadTelegramCommunityStats);
