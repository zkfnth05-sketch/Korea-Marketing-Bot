// ==============================================================================
// [독립 모듈] app_pipelines.js: 대한민국 3대 슈퍼앱 22대 옴니채널 파이프라인 데이터 정의 모듈
// 📈 Stock Master 주식 AI / 💖 Aura AI 데이팅 / 🛡️ InsureBalance 보험비교
// ==============================================================================

const APP_PIPELINES = {
    // --------------------------------------------------------------------------
    // 📈 1. Stock Master 주식 AI 22대 파이프라인
    // --------------------------------------------------------------------------
    stock: {
        brandKey: "stock",
        brandName: "Stock Master (주식 AI)",
        pageTitle: "📈 Stock Master 주식 AI 마케팅 통합 제어 센터",
        pageDesc: "당일 외인/기관 수급 분석, 장전 08:30 시황, 조건검색식, 22개 증시 채널을 24시간 자율 가동합니다.",
        seasonBadge: "STOCK MASTER AI",
        badgeColor: "#FACC15",
        accentColor: "#F59E0B",
        accentBorder: "rgba(245, 158, 11, 0.35)",
        btnGradient: "linear-gradient(135deg, #F59E0B 0%, #D97706 100%)",
        activeTabBg: "linear-gradient(135deg, #F59E0B, #D97706)",
        
        telegram: {
            title: "📈 Stock Master 텔레그램 24시간 자율 성장 통합 사령부",
            groupName: "Stock Master VIP 시황 (t.me/stockmaster_vip)",
            desc: "외인/기관 실시간 수급 분석 · 08:30 장전 브리핑 · 조건검색식 · 하루 2회(08:40/15:30) 정기 증시 브리핑",
            officialColor: "#F59E0B",
            morningBriefingTitle: "⚡ 장전 VIP 시황 브리핑",
            pollTitle: "📊 종목 토론 투표 1회 생성"
        },

        hubs: [
            // #1 숏폼
            {
                id: "shorts",
                key: "shorts",
                hubNumber: 1,
                name: "당일 급등주 & 외인 수급 숏폼 팩토리",
                icon: "🎬",
                desc: "유튜브 쇼츠 · 인스타 릴스 · 틱톡 · 네이버 클립 4대 플랫폼 동시 송출 (12:00 / 20:30 / 23:30 KST)"
            },
            // #2 카드뉴스
            {
                id: "cardnews",
                key: "cardnews",
                hubNumber: 2,
                name: "주도 섹터 심층 분석 4장 카드뉴스",
                icon: "📸",
                desc: "당일 테마주 수급 지도 & 차트 분석 4장 카드뉴스 (08:00 / 15:30 / 22:30 KST)"
            },
            // #3 Reddit
            {
                id: "reddit",
                key: "reddit",
                hubNumber: 3,
                name: "Reddit 1:1 리드 헌터",
                icon: "🤖",
                desc: "26개 서브레딧 실시간 감지 (1시간 간격 정기 자율 헌팅)"
            },
            // #4 페이스북
            {
                id: "fb_groups",
                key: "fb_groups",
                hubNumber: 4,
                name: "페이스북 50만 그룹 침투기",
                icon: "👥",
                desc: "4장 카드뉴스 + 첫댓글 (하루 3회 정시: 09:30 / 13:30 / 19:30 KST)"
            },
            // #5 SEO 블로그
            {
                id: "blog",
                key: "blog",
                hubNumber: 5,
                name: "17개국어 SEO 블로그 칼럼",
                icon: "🌐",
                desc: "17개국어 칼럼 (하루 3회 정시: 09:00 / 13:00 / 19:00 KST)"
            },
            // #6 구글 서치콘솔
            {
                id: "seo",
                key: "seo",
                hubNumber: 6,
                name: "구글 서치콘솔 & 실시간 색인 핑",
                icon: "🔍",
                desc: "Googlebot 색인 핑 & 사이트맵 갱신 (하루 1회 정시: 01:00 KST)",
                isSeo: true
            },
            // #7 Meta Threads
            {
                id: "threads",
                key: "threads",
                hubNumber: 7,
                name: "Meta Threads 바이럴 스레드",
                icon: "🧵",
                desc: "3~4단 타래 바이럴 (하루 3회 정시: 11:00 / 16:30 / 21:30 KST)"
            },
            // #8 네이버 클립
            {
                id: "naver_clip",
                key: "naver_clip",
                hubNumber: 8,
                name: "네이버 클립 (메인 노출 숏폼)",
                icon: "📎",
                desc: "당일 급등주 및 외인 매수 테마 숏폼 네이버 메인 노출"
            },
            // #9 네이버 블로그
            {
                id: "naver_blog",
                key: "naver_blog",
                hubNumber: 9,
                name: "네이버 블로그 (스마트블록 1위)",
                icon: "📗",
                desc: "스마트블록 상위 종목별 AI 기술적 지표 & 목표가 리포트"
            },
            // #10 티스토리
            {
                id: "tistory",
                key: "tistory",
                hubNumber: 10,
                name: "티스토리 (구글 SEO 1위)",
                icon: "🍊",
                desc: "구글 SEO 1위 '급등주 조건검색식' 및 퀀트 매매 전략 칼럼"
            },
            // #11 네이버 포스트
            {
                id: "naver_post",
                key: "naver_post",
                hubNumber: 11,
                name: "네이버 포스트 (카드 매거진)",
                icon: "📮",
                desc: "당일 주도 테마주/수급 지도 및 주도 섹터 정밀 분석 매거진"
            },
            // #12 카카오 브런치
            {
                id: "brunch",
                key: "brunch",
                hubNumber: 12,
                name: "카카오 브런치 (프리미엄 칼럼)",
                icon: "☕",
                desc: "거시경제 인사이트 · AI 퀀트 투자 심층 칼럼"
            },
            // #13 네이버 서치어드바이저
            {
                id: "search_advisor",
                key: "search_advisor",
                hubNumber: 13,
                name: "네이버 서치어드바이저",
                icon: "🧭",
                desc: "신규 칼럼 URL 네이버 웹마스터도구 5분 내 즉각 색인 핑"
            },
            // #14 네이버 지식iN
            {
                id: "naver_kin",
                key: "naver_kin",
                hubNumber: 14,
                name: "네이버 지식iN 실시간 낚아채기",
                icon: "💡",
                desc: "\"00전자 목표가\", \"00주식 전망\" 실시간 질문 감지 및 답변"
            },
            // #15 네이버 카페
            {
                id: "naver_cafe",
                key: "naver_cafe",
                hubNumber: 15,
                name: "네이버 카페 (5일 로테이션)",
                icon: "☕",
                desc: "30만 대형 주식 카페 5일 쿨다운 안티밴 준수 자연스러운 바이럴"
            },
            // #16 다음 카페
            {
                id: "daum_cafe",
                key: "daum_cafe",
                hubNumber: 16,
                name: "다음(Daum) 카페 (감성 썰)",
                icon: "🍵",
                desc: "대형 다음 카페 외인/기관 순매수 분석 정보글 투고"
            },
            // #17 뽐뿌 포럼
            {
                id: "ppomppu",
                key: "ppomppu",
                hubNumber: 17,
                name: "뽐뿌 포럼 (커뮤니티 팩트)",
                icon: "🛒",
                desc: "증권포럼 당일 실전 매매일지 및 수급 특징주 정보글"
            },
            // #18 디시인사이드
            {
                id: "dcinside",
                key: "dcinside",
                hubNumber: 18,
                name: "디시인사이드 (OCR 돌파)",
                icon: "갤",
                desc: "주식 갤러리/미주갤 한글 초성 캡차 자동 돌파 정보글 투고"
            },
            // #19 보배드림
            {
                id: "bobaedream",
                key: "bobaedream",
                hubNumber: 19,
                name: "보배드림 (베스트글 공략)",
                icon: "🚗",
                desc: "직장인 개미 매매일지 및 시장 분석 베스트글 공략"
            },
            // #20 네이트판
            {
                id: "nate_pann",
                key: "nate_pann",
                hubNumber: 20,
                name: "네이트판 (톡커들의 선택)",
                icon: "💬",
                desc: "주식 물린 개미 탈출 실전 팁 및 멘탈 관리 썰 투고"
            },
            // #21 에펨코리아
            {
                id: "fmkorea",
                key: "fmkorea",
                hubNumber: 21,
                name: "에펨코리아(펨코)",
                icon: "⚽",
                desc: "펨코 주식 갤러리 맞춤형 장중 시황 요약 및 수급 분석"
            },
            // #22 카카오 알림톡
            {
                id: "kakao_channel",
                key: "kakao_channel",
                hubNumber: 22,
                name: "카카오 알림톡 & 채널",
                icon: "💬",
                desc: "장전 08:30 시황 알림톡 · 당일 주도 테마주 속보 발송"
            }
        ]
    },

    // --------------------------------------------------------------------------
    // 💖 2. Aura (AI 데이팅) 22대 파이프라인
    // --------------------------------------------------------------------------
    aura: {
        brandKey: "aura",
        brandName: "Aura (AI 데이팅)",
        pageTitle: "💖 Aura AI 데이팅 마케팅 통합 제어 센터",
        pageDesc: "2030 소개팅 팁, 연애 심리 칼럼, 릴스/숏폼, 22개 소셜 채널을 24시간 자율 가동합니다.",
        seasonBadge: "AURA DATING",
        badgeColor: "#EC4899",
        accentColor: "#EC4899",
        accentBorder: "rgba(236, 72, 153, 0.35)",
        btnGradient: "linear-gradient(135deg, #EC4899 0%, #BE185D 100%)",
        activeTabBg: "linear-gradient(135deg, #EC4899, #BE185D)",

        telegram: {
            title: "💖 Aura 데이팅 텔레그램 24시간 자율 성장 통합 사령부",
            groupName: "Aura Dating VIP (t.me/aura_dating_official)",
            desc: "2030 솔로 미팅 & 소개팅 코칭 · 실시간 Q&A · 주말 매칭 알림 · 하루 2회(12:00/21:00) 정기 브리핑",
            officialColor: "#EC4899",
            morningBriefingTitle: "⚡ 연애 심리 모닝 브리핑",
            pollTitle: "📊 연애 취향 투표 1회 생성"
        },

        hubs: [
            // #1 숏폼
            {
                id: "shorts",
                key: "shorts",
                hubNumber: 1,
                name: "소개팅 첫만남 호감 숏폼 팩토리",
                icon: "🎬",
                desc: "유튜브 쇼츠 · 인스타 릴스 · 틱톡 · 네이버 클립 4대 플랫폼 동시 송출 (12:00 / 20:30 / 23:30 KST)"
            },
            // #2 카드뉴스
            {
                id: "cardnews",
                key: "cardnews",
                hubNumber: 2,
                name: "연애 센스 & 데이트 코스 4장 카드뉴스",
                icon: "📸",
                desc: "2030 감성 연애 에세이 & 주말 데이트 명소 4장 카드뉴스 (08:00 / 15:30 / 22:30 KST)"
            },
            // #3 Reddit
            {
                id: "reddit",
                key: "reddit",
                hubNumber: 3,
                name: "Reddit 1:1 리드 헌터",
                icon: "🤖",
                desc: "26개 서브레딧 실시간 감지 (1시간 간격 정기 자율 헌팅)"
            },
            // #4 페이스북
            {
                id: "fb_groups",
                key: "fb_groups",
                hubNumber: 4,
                name: "페이스북 50만 그룹 침투기",
                icon: "👥",
                desc: "4장 카드뉴스 + 첫댓글 (하루 3회 정시: 09:30 / 13:30 / 19:30 KST)"
            },
            // #5 SEO 블로그
            {
                id: "blog",
                key: "blog",
                hubNumber: 5,
                name: "17개국어 SEO 블로그 칼럼",
                icon: "🌐",
                desc: "17개국어 칼럼 (하루 3회 정시: 09:00 / 13:00 / 19:00 KST)"
            },
            // #6 구글 서치콘솔
            {
                id: "seo",
                key: "seo",
                hubNumber: 6,
                name: "구글 서치콘솔 & 실시간 색인 핑",
                icon: "🔍",
                desc: "Googlebot 색인 핑 & 사이트맵 갱신 (하루 1회 정시: 01:00 KST)",
                isSeo: true
            },
            // #7 Meta Threads
            {
                id: "threads",
                key: "threads",
                hubNumber: 7,
                name: "Meta Threads 바이럴 스레드",
                icon: "🧵",
                desc: "3~4단 타래 바이럴 (하루 3회 정시: 11:00 / 16:30 / 21:30 KST)"
            },
            // #8 네이버 클립
            {
                id: "naver_clip",
                key: "naver_clip",
                hubNumber: 8,
                name: "네이버 클립 (메인 노출 숏폼)",
                icon: "📎",
                desc: "Aura 데이팅 첫만남 호감 비결 & 대화법 숏폼 네이버 메인 노출"
            },
            // #9 네이버 블로그
            {
                id: "naver_blog",
                key: "naver_blog",
                hubNumber: 9,
                name: "네이버 블로그 (스마트블록 1위)",
                icon: "📗",
                desc: "스마트블록 상위 '소개팅 팁' · 데이트 코스 공략 리포트"
            },
            // #10 티스토리
            {
                id: "tistory",
                key: "tistory",
                hubNumber: 10,
                name: "티스토리 (구글 SEO 1위)",
                icon: "🍊",
                desc: "구글 SEO '소개팅 어플 순위/추천' · 2030 연애 심리 칼럼"
            },
            // #11 네이버 포스트
            {
                id: "naver_post",
                key: "naver_post",
                hubNumber: 11,
                name: "네이버 포스트 (카드 매거진)",
                icon: "📮",
                desc: "2030 감성 연애 카드뉴스 & 심리 테스트 매거진"
            },
            // #12 카카오 브런치
            {
                id: "brunch",
                key: "brunch",
                hubNumber: 12,
                name: "카카오 브런치 (프리미엄 칼럼)",
                icon: "☕",
                desc: "남녀 관계론 · 연애 심리 프리미엄 에세이 칼럼"
            },
            // #13 네이버 서치어드바이저
            {
                id: "search_advisor",
                key: "search_advisor",
                hubNumber: 13,
                name: "네이버 서치어드바이저",
                icon: "🧭",
                desc: "신규 칼럼 URL 네이버 웹마스터도구 5분 내 즉각 색인 핑"
            },
            // #14 네이버 지식iN
            {
                id: "naver_kin",
                key: "naver_kin",
                hubNumber: 14,
                name: "네이버 지식iN 실시간 낚아채기",
                icon: "💡",
                desc: "\"소개팅 첫 카톡\", \"호감 신호\" 실시간 질문 답변"
            },
            // #15 네이버 카페
            {
                id: "naver_cafe",
                key: "naver_cafe",
                hubNumber: 15,
                name: "네이버 카페 (5일 로테이션)",
                icon: "☕",
                desc: "30만 대형 2030 친목/직장인 카페 5일 쿨다운 안티밴 바이럴"
            },
            // #16 다음 카페
            {
                id: "daum_cafe",
                key: "daum_cafe",
                hubNumber: 16,
                name: "다음(Daum) 카페 (감성 썰)",
                icon: "🍵",
                desc: "대형 다음 카페 현실 공감 연애 썰 및 소개팅 팁 투고"
            },
            // #17 뽐뿌 포럼
            {
                id: "ppomppu",
                key: "ppomppu",
                hubNumber: 17,
                name: "뽐뿌 포럼 (커뮤니티 팩트)",
                icon: "🛒",
                desc: "자유게시판 솔로 탈출 공감 썰 · 소개팅 후기 정보글"
            },
            // #18 디시인사이드
            {
                id: "dcinside",
                key: "dcinside",
                hubNumber: 18,
                name: "디시인사이드 (OCR 돌파)",
                icon: "갤",
                desc: "연애 갤러리 한글 초성 캡차 자동 돌파 정보글 투고"
            },
            // #19 보배드림
            {
                id: "bobaedream",
                key: "bobaedream",
                hubNumber: 19,
                name: "보배드림 (베스트글 공략)",
                icon: "🚗",
                desc: "3040 현실 연애 팁 및 데이트 코스 정보글"
            },
            // #20 네이트판
            {
                id: "nate_pann",
                key: "nate_pann",
                hubNumber: 20,
                name: "네이트판 (톡커들의 선택)",
                icon: "💬",
                desc: "102030 공감 폭발 연애 썰 및 썸 탈출 실전 팁"
            },
            // #21 에펨코리아
            {
                id: "fmkorea",
                key: "fmkorea",
                hubNumber: 21,
                name: "에펨코리아(펨코)",
                icon: "⚽",
                desc: "2030 남성 맞춤형 유쾌한 소개팅 팁 및 대화법"
            },
            // #22 카카오 알림톡
            {
                id: "kakao_channel",
                key: "kakao_channel",
                hubNumber: 22,
                name: "카카오 알림톡 & 채널",
                icon: "💬",
                desc: "금요일 저녁 주말 맞춤 매칭 안내 및 코칭 알림톡"
            }
        ]
    },

    // --------------------------------------------------------------------------
    // 🛡️ 3. InsureBalance (보험 비교) 22대 파이프라인
    // --------------------------------------------------------------------------
    insurance: {
        brandKey: "insurance",
        brandName: "InsureBalance (보험비교)",
        pageTitle: "🛡️ InsureBalance 보험비교 마케팅 통합 제어 센터",
        pageDesc: "실손보험 비교, 3대 질병 절약 가이드, 호갱 탈출 팁, 22개 채널을 24시간 자율 가동합니다.",
        seasonBadge: "INSUREBALANCE",
        badgeColor: "#10B981",
        accentColor: "#10B981",
        accentBorder: "rgba(16, 185, 129, 0.35)",
        btnGradient: "linear-gradient(135deg, #10B981 0%, #059669 100%)",
        activeTabBg: "linear-gradient(135deg, #10B981, #059669)",

        telegram: {
            title: "🛡️ InsureBalance 텔레그램 24시간 자율 성장 통합 사령부",
            groupName: "InsureBalance 케어 (t.me/insurebalance_official)",
            desc: "실손보험 비교 & 호갱 탈출 가이드 · 3대 질병 절약 팁 · 실시간 보험 분석 · 하루 2회(09:00/18:00) 정기 브리핑",
            officialColor: "#10B981",
            morningBriefingTitle: "⚡ 보험 절약 모닝 브리핑",
            pollTitle: "📊 보험 만족도 투표 1회 생성"
        },

        hubs: [
            // #1 숏폼
            {
                id: "shorts",
                key: "shorts",
                hubNumber: 1,
                name: "보험료 15만원 다이어트 숏폼 팩토리",
                icon: "🎬",
                desc: "유튜브 쇼츠 · 인스타 릴스 · 틱톡 · 네이버 클립 4대 플랫폼 동시 송출 (12:00 / 20:30 / 23:30 KST)"
            },
            // #2 카드뉴스
            {
                id: "cardnews",
                key: "cardnews",
                hubNumber: 2,
                name: "호갱 탈출 & 필수 특약 4장 카드뉴스",
                icon: "📸",
                desc: "실손보험 비교 & 불필요 특약 삭제 4장 카드뉴스 (08:00 / 15:30 / 22:30 KST)"
            },
            // #3 Reddit
            {
                id: "reddit",
                key: "reddit",
                hubNumber: 3,
                name: "Reddit 1:1 리드 헌터",
                icon: "🤖",
                desc: "26개 서브레딧 실시간 감지 (1시간 간격 정기 자율 헌팅)"
            },
            // #4 페이스북
            {
                id: "fb_groups",
                key: "fb_groups",
                hubNumber: 4,
                name: "페이스북 50만 그룹 침투기",
                icon: "👥",
                desc: "4장 카드뉴스 + 첫댓글 (하루 3회 정시: 09:30 / 13:30 / 19:30 KST)"
            },
            // #5 SEO 블로그
            {
                id: "blog",
                key: "blog",
                hubNumber: 5,
                name: "17개국어 SEO 블로그 칼럼",
                icon: "🌐",
                desc: "17개국어 칼럼 (하루 3회 정시: 09:00 / 13:00 / 19:00 KST)"
            },
            // #6 구글 서치콘솔
            {
                id: "seo",
                key: "seo",
                hubNumber: 6,
                name: "구글 서치콘솔 & 실시간 색인 핑",
                icon: "🔍",
                desc: "Googlebot 색인 핑 & 사이트맵 갱신 (하루 1회 정시: 01:00 KST)",
                isSeo: true
            },
            // #7 Meta Threads
            {
                id: "threads",
                key: "threads",
                hubNumber: 7,
                name: "Meta Threads 바이럴 스레드",
                icon: "🧵",
                desc: "3~4단 타래 바이럴 (하루 3회 정시: 11:00 / 16:30 / 21:30 KST)"
            },
            // #8 네이버 클립
            {
                id: "naver_clip",
                key: "naver_clip",
                hubNumber: 8,
                name: "네이버 클립 (메인 노출 숏폼)",
                icon: "📎",
                desc: "보험 절약 꿀팁 · 숨은 보험금 찾기 숏폼 네이버 메인 노출"
            },
            // #9 네이버 블로그
            {
                id: "naver_blog",
                key: "naver_blog",
                hubNumber: 9,
                name: "네이버 블로그 (스마트블록 1위)",
                icon: "📗",
                desc: "VIEW 1위 '실손보험 비교' · 3대 질병 가성비 분석 리포트"
            },
            // #10 티스토리
            {
                id: "tistory",
                key: "tistory",
                hubNumber: 10,
                name: "티스토리 (구글 SEO 1위)",
                icon: "🍊",
                desc: "구글 SEO '보험료 계산기' · 운전자보험 비교 칼럼"
            },
            // #11 네이버 포스트
            {
                id: "naver_post",
                key: "naver_post",
                hubNumber: 11,
                name: "네이버 포스트 (카드 매거진)",
                icon: "📮",
                desc: "연령별 필수 보장 차트 및 보험 다이어트 매거진"
            },
            // #12 카카오 브런치
            {
                id: "brunch",
                key: "brunch",
                hubNumber: 12,
                name: "카카오 브런치 (프리미엄 칼럼)",
                icon: "☕",
                desc: "가계 금융 다이어트 · 합리적 보험 재테크 에세이"
            },
            // #13 네이버 서치어드바이저
            {
                id: "search_advisor",
                key: "search_advisor",
                hubNumber: 13,
                name: "네이버 서치어드바이저",
                icon: "🧭",
                desc: "신규 칼럼 URL 네이버 웹마스터도구 5분 내 즉각 색인 핑"
            },
            // #14 네이버 지식iN
            {
                id: "naver_kin",
                key: "naver_kin",
                hubNumber: 14,
                name: "네이버 지식iN 실시간 낚아채기",
                icon: "💡",
                desc: "\"이 보험 해지해야 하나요?\", \"실손 청구\" 맞춤 답변"
            },
            // #15 네이버 카페
            {
                id: "naver_cafe",
                key: "naver_cafe",
                hubNumber: 15,
                name: "네이버 카페 (5일 로테이션)",
                icon: "☕",
                desc: "30만 대형 재테크/맘카페 5일 쿨다운 안티밴 준수 정보 공유"
            },
            // #16 다음 카페
            {
                id: "daum_cafe",
                key: "daum_cafe",
                hubNumber: 16,
                name: "다음(Daum) 카페 (감성 썰)",
                icon: "🍵",
                desc: "대형 다음 카페 월 15만원 절약한 보험 리모델링 후기"
            },
            // #17 뽐뿌 포럼
            {
                id: "ppomppu",
                key: "ppomppu",
                hubNumber: 17,
                name: "뽐뿌 포럼 (커뮤니티 팩트)",
                icon: "🛒",
                desc: "보험포럼 불필요 특약 분석 및 가성비 플랜 정보글"
            },
            // #18 디시인사이드
            {
                id: "dcinside",
                key: "dcinside",
                hubNumber: 18,
                name: "디시인사이드 (OCR 돌파)",
                icon: "갤",
                desc: "보험 갤러리 한글 초성 캡차 자동 돌파 및 정보글 투고"
            },
            // #19 보배드림
            {
                id: "bobaedream",
                key: "bobaedream",
                hubNumber: 19,
                name: "보배드림 (베스트글 공략)",
                icon: "🚗",
                desc: "교통사고 처리 팁 & 변호사 선임비용 운전자보험 팁"
            },
            // #20 네이트판
            {
                id: "nate_pann",
                key: "nate_pann",
                hubNumber: 20,
                name: "네이트판 (톡커들의 선택)",
                icon: "💬",
                desc: "설계사 지인한테 당한 보험 리모델링 성공 썰 투고"
            },
            // #21 에펨코리아
            {
                id: "fmkorea",
                key: "fmkorea",
                hubNumber: 21,
                name: "에펨코리아(펨코)",
                icon: "⚽",
                desc: "사회초년생 첫 보험 필수 체크리스트 요약 정보글"
            },
            // #22 카카오 알림톡
            {
                id: "kakao_channel",
                key: "kakao_channel",
                hubNumber: 22,
                name: "카카오 알림톡 & 채널",
                icon: "💬",
                desc: "기존 증권 1:1 무료 분석 접수 및 맞춤 절약 플랜"
            }
        ]
    }
};

window.APP_PIPELINES = APP_PIPELINES;
