# -*- coding: utf-8 -*-
"""
AuraSNSGuideGenerator - 📢 [Aura 데이팅 전용 숏폼 5대 SNS 포스팅 가이드 자동 생성 모듈]
- 유튜브 쇼츠(YouTube Shorts), 틱톡(TikTok), 인스타그램 릴스(Instagram Reels), 스레드(Threads), 페이스북 릴스(Facebook Reels)
- 숏폼 영상 1편이 생성될 때마다 해당 영상 폴더 내에 'SNS_포스팅_가이드.txt'를 100% 무인 자동 생성
- 관리자가 복사(Ctrl+C)해서 즉시 포스팅할 수 있는 완벽한 템플릿 제공
- 공식 검색어: '아우라AI데이팅' (붙여쓰기 철칙) / 공식 URL: https://aura-ai-dating.vercel.app/lounge
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("AuraSNSGuideGenerator")

# 8대 주제별 SNS 특화 카피 & 메타데이터 사전
AURA_TOPIC_SNS_DATA: Dict[int, Dict[str, Any]] = {
    1: {
        "theme_name": "소개팅 탈출 전화",
        "theme_code": "escape_call",
        "yt_title": "소개팅 나갔는데 분위기 싸할 때 1초 만에 합법 탈출하는 법 ㄷㄷ #Shorts",
        "yt_desc": (
            "소개팅 자리 나갔는데 사진이랑 너무 다르거나 분위기 싸해서 집 가고 싶었던 적 있으시죠?\n"
            "아우라 AI 소개팅 탈출 전화 버튼 하나면 10초 뒤에 '팀장님 긴급 업무 호출' 전화가 진짜로 옵니다!\n"
            "눈치 보지 말고 매너 있게 1초 만에 탈출하세요.\n\n"
            "👉 지금 바로 나만의 인연/동네 친구 찾기\n"
            "🔗 네이버 검색창에 [아우라AI데이팅] 검색!\n"
            "공식 라운지: https://aura-ai-dating.vercel.app/lounge\n"
        ),
        "pinned_comment": "분위기 싸한 소개팅, 억지로 버티지 마세요! 네이버에 '아우라AI데이팅' 검색하고 안심 탈출 기능 무료 체험해보세요 ✨",
        "tiktok_caption": (
            "소개팅 폭망했을 때 버튼 하나로 탈출하는 레전드 기능 ㅋㅋㅋ\n"
            "팀장님 긴급 호출 전화 울리자마자 칼퇴하듯 집으로 런!\n"
            "👇 프로필 링크(Bio)에서 무료 입장 가능!"
        ),
        "reels_caption": (
            "소개팅 자리에서 밥만 먹고 도망치고 싶었던 분들 필독 🚨\n\n"
            "아우라 앱에는 '긴급 탈출 전화' 기능이 있어서, 버튼 누르면 10초 뒤에 진짜 팀장님 목소리로 업무 전화가 옵니다 ㅋㅋㅋ\n"
            "상대방 기분 안 상하게 매너 탈출 완벽 성공!\n\n"
            "✨ Aura 데이팅만의 3가지 킬러 포인트:\n"
            "1️⃣ 어색한 자리 합법 탈출! AI 긴급 탈출 전화\n"
            "2️⃣ 유령회원 제로 & 남녀 50:50 완벽 성비 정원제\n"
            "3️⃣ 스토킹 걱정 없는 500m 안심 레이더\n\n"
            "👉 프로필 링크(@aura_official)나 네이버에서 [아우라AI데이팅]을 검색하세요!"
        ),
        "threads_text": (
            "소개팅 나갔는데 사진이랑 실물 너무 달라서 멘붕 온 적 있음?\n"
            "아우라는 버튼 누르면 10초 뒤에 진짜 팀장님 업무 전화 와서 합법 탈출 시켜줌 ㅋㅋㅋ\n\n"
            "다들 소개팅 최악의 빌런 썰 풀어보셈 👇"
        ),
        "fb_text": (
            "소개팅 최악의 순간 1위: 사진이랑 실물이 너무 다를 때...\n"
            "이제 억지로 앉아서 2차까지 끌려가지 마세요! 아우라 AI 긴급 탈출 전화로 매너 있게 1초 탈출 가능합니다.\n"
            "댓글 링크에서 무료로 확인해보세요!"
        ),
        "hashtags": "#소개팅썰 #소개팅탈출 #아우라AI데이팅 #소개팅앱 #연애팁 #데이트 #2030 #Shorts #Reels #TikTok"
    },
    2: {
        "theme_name": "실시간 자막 통화",
        "theme_code": "realtime_subtitles",
        "yt_title": "일본어 1도 몰라도 일본 여사친이랑 밤새 통화하는 법 (실시간 자막 ㄷㄷ) #Shorts",
        "yt_desc": (
            "외국인 친구나 일본인 친구 사귀고 싶은데 언어 장벽 때문에 포기하셨나요?\n"
            "아우라 실시간 AI 통역 통화로 내가 한국어로 말하면 상대방 화면엔 일본어 자막이, 상대방이 일본어로 말하면 나에겐 한국어 자막이 실시간으로 뜹니다!\n"
            "언어 장벽 제로 글로벌 데이팅의 시작!\n\n"
            "👉 글로벌 친구 & 인연 찾기\n"
            "🔗 네이버 검색창에 [아우라AI데이팅] 검색!\n"
            "공식 라운지: https://aura-ai-dating.vercel.app/lounge\n"
        ),
        "pinned_comment": "언어 장벽 없이 외국인/글로벌 친구 사귀기! 네이버에 '아우라AI데이팅' 검색해보세요 💖",
        "tiktok_caption": (
            "외국어 1도 몰라도 일본인 친구랑 1초 만에 밤샘 통화 가능한 AI 통역 통화 ㄷㄷ\n"
            "내가 한국어로 말하면 실시간 번역 자막이 바로 뜸!\n"
            "👇 프로필 링크에서 바로 만나보세요!"
        ),
        "reels_caption": (
            "일본 여행 가기 전에 일본인 친구 사귀고 싶은 사람 손! 🙋‍♀️\n\n"
            "아우라 앱에서는 실시간 음성 AI 통역으로 서로 다른 언어로 말해도 화면에 자막이 실시간으로 변환돼서 편하게 통화할 수 있어요.\n\n"
            "✨ Aura 글로벌 데이팅 핵심 기능:\n"
            "1️⃣ 한국어-일본어-영어 실시간 AI 자막 통화\n"
            "2️⃣ 해외 여행 가기 전 현지인 로컬 친구 매칭\n"
            "3️⃣ 100% 본인 인증 회원만 매칭\n\n"
            "👉 프로필 링크나 네이버에서 [아우라AI데이팅]을 검색해보세요!"
        ),
        "threads_text": (
            "일본어 아리가또밖에 모르는데 일본 친구랑 3시간 통화함 ㅋㅋㅋ\n"
            "실시간 AI 번역 자막 기능 진짜 신세계네요.\n"
            "외국인 친구 사귀고 싶은 분 계신가요?"
        ),
        "fb_text": (
            "외국어 못해도 글로벌 연애 가능? 아우라 실시간 AI 자막 통화로 언어 장벽 없이 대화해보세요!\n"
            "댓글 링크에서 바로 확인 가능합니다."
        ),
        "hashtags": "#일본인친구 #국제연애 #아우라AI데이팅 #글로벌데이팅 #언어교환 #소개팅앱 #Shorts #Reels #TikTok"
    },
    3: {
        "theme_name": "50:50 VIP 게이트",
        "theme_code": "vip_gate_5050",
        "yt_title": "소개팅 앱에 남자가 90%인 이유? 5:5 아니면 문 닫아버리는 앱 등장 #Shorts",
        "yt_desc": (
            "다른 소개팅 앱 가입하면 남초 90%에 유령회원만 가득해서 돈만 날리셨죠?\n"
            "아우라는 남녀 성비가 50:50 황금 비율이 유지될 때만 신규 입장을 허용하는 VIP 게이트를 운영합니다!\n"
            "유령회원 제로, 진짜 매칭되는 2030 프리미엄 라운지.\n\n"
            "👉 50:50 VIP 라운지 입장하기\n"
            "🔗 네이버 검색창에 [아우라AI데이팅] 검색!\n"
            "공식 라운지: https://aura-ai-dating.vercel.app/lounge\n"
        ),
        "pinned_comment": "남초 현상 없는 완벽한 5:5 성비 소개팅! 네이버에 '아우라AI데이팅' 검색하고 VIP 게이트를 확인해보세요 👑",
        "tiktok_caption": (
            "남초 90% 소개팅 앱들에 질린 분들 주목 🚨\n"
            "남녀 성비 50:50 안 맞으면 문 닫아버리는 정원제 데이팅 앱!\n"
            "👇 프로필 링크에서 지금 대기 순번 확인해보세요!"
        ),
        "reels_caption": (
            "기존 소개팅 앱에서 매칭 안 되고 과금만 유도당해서 지치셨나요? 😤\n\n"
            "아우라는 남녀 성비 50:50 정원제를 엄격하게 준수하여 유령회원 없이 진짜 활성 회원들만 실시간으로 연결됩니다.\n\n"
            "✨ Aura VIP 게이트 약속:\n"
            "1️⃣ 남녀 성비 50:50 칼같은 정원제 운영\n"
            "2️⃣ 유령회원 및 알바 계정 영구 제명\n"
            "3️⃣ 상위 0.1% 매력 지수 VIP 라운지\n\n"
            "👉 프로필 링크나 네이버에서 [아우라AI데이팅]을 검색하세요!"
        ),
        "threads_text": (
            "소개팅 앱 남초 90% 실화냐? 매칭 안 되는 이유가 있었음...\n"
            "성비 5:5 안 맞으면 가입도 막아버리는 앱 나왔다는데 어떻게 생각함?"
        ),
        "fb_text": (
            "돈만 쓰고 매칭은 1도 안 되는 남초 소개팅 앱은 이제 그만! 남녀 50:50 성비 정원제 아우라에서 진짜 인연을 만나보세요.\n"
            "댓글 링크에서 바로 입장 가능합니다."
        ),
        "hashtags": "#소개팅앱후기 #성비5대5 #아우라AI데이팅 #데이팅앱 #솔로탈출 #연애상담 #Shorts #Reels #TikTok"
    },
    4: {
        "theme_name": "청담동 화보 보정",
        "theme_code": "studio_profile",
        "yt_title": "방구석 셀카를 30만원짜리 청담동 스튜디오 화보로 바꿔주는 AI ㄷㄷ #Shorts",
        "yt_desc": (
            "소개팅 앱에 올릴 사진 없어서 화장실 거울 셀카 올리셨던 분들 필독!\n"
            "아우라 AI 청담동 스튜디오 기능으로 내 일상 사진 한 장만 넣으면 30만원짜리 프로필 화보로 완벽 변신합니다!\n"
            "과한 뽀샵 없이 내 이목구비 그대로 살린 인생 프로필을 만들어보세요.\n\n"
            "👉 내 사진 청담동 화보로 만들기\n"
            "🔗 네이버 검색창에 [아우라AI데이팅] 검색!\n"
            "공식 라운지: https://aura-ai-dating.vercel.app/lounge\n"
        ),
        "pinned_comment": "사진 한 장으로 인생 프로필 완성! 네이버에 '아우라AI데이팅' 검색하고 무료 AI 화보 받아보세요 📸",
        "tiktok_caption": (
            "소개팅 사진 없어서 고민인 사람? 방구석 셀카 1초 만에 청담동 화보로 바꿔줌 ㄷㄷ\n"
            "과한 포토샵 아니고 이목구비 찰떡 살린 실사 화보!\n"
            "👇 프로필 링크에서 지금 바로 생성해보세요!"
        ),
        "reels_caption": (
            "소개팅 매칭률 90%는 '첫인상 사진'에서 결정됩니다 📸\n\n"
            "비싼 스튜디오 갈 필요 없이, 아우라 AI 스튜디오에서 내 얼굴의 매력을 극대화한 청담동 스타일 화보를 무료로 제작해보세요!\n\n"
            "✨ Aura AI 스튜디오 특징:\n"
            "1️⃣ 어색한 뽀샵 NO! 자연스러운 고급 피부 텍스처\n"
            "2️⃣ 청담동 조명 & 황금비율 구도 자동 매칭\n"
            "3️⃣ 프로필 등록 시 매칭률 300% 상승\n\n"
            "👉 프로필 상단 링크나 네이버에서 [아우라AI데이팅]을 검색하세요!"
        ),
        "threads_text": (
            "소개팅 앱 프로필 사진에 셀카 올리면 매칭 안 되는 거 국룰...\n"
            "AI가 청담동 스튜디오에서 찍은 것처럼 바꿔주는데 싱크로율 미쳤음 ㄷㄷ\n"
            "다들 프로필 사진 어디서 찍으심?"
        ),
        "fb_text": (
            "소개팅 사진 고민 끝! 비싼 스튜디오 갈 필요 없이 AI로 인생 화보 프로필을 만들어보세요.\n"
            "댓글 링크에서 무료로 확인해보세요!"
        ),
        "hashtags": "#프로필사진 #인생샷 #청담동스튜디오 #아우라AI데이팅 #소개팅프로필 #AI프로필 #Shorts #Reels #TikTok"
    },
    5: {
        "theme_name": "가치관 밸런스 매칭",
        "theme_code": "balance_matching",
        "yt_title": "연락 빈도, 데이트 비용, 결혼관까지 100% 맞는 사람 찾는 밸런스 게임 #Shorts",
        "yt_desc": (
            "얼굴만 보고 만났다가 연락 스타일, 데이트 비용, 소비 습관 안 맞아서 싸우고 헤어지셨나요?\n"
            "아우라는 가치관 밸런스 게임으로 연애관, 생활 패턴, 금전 감각까지 나랑 찰떡궁합인 인연만 콕 집어 매칭해줍니다!\n"
            "시간 낭비 없는 진짜 가치관 매칭의 세계!\n\n"
            "👉 내 가치관 궁합 테스트하기\n"
            "🔗 네이버 검색창에 [아우라AI데이팅] 검색!\n"
            "공식 라운지: https://aura-ai-dating.vercel.app/lounge\n"
        ),
        "pinned_comment": "연락 스타일부터 가치관까지 딱 맞는 연애! 네이버에 '아우라AI데이팅' 검색해보세요 💖",
        "tiktok_caption": (
            "데이트 비용 더치페이 vs 번갈아 내기? 연락 하루종일 vs 용건만?\n"
            "나랑 가치관 100% 일치하는 사람만 골라주는 데이팅 밸런스 게임 ㅋㅋㅋ\n"
            "👇 프로필 링크에서 테스트해보세요!"
        ),
        "reels_caption": (
            "연애할 때 가치관 안 맞으면 결국 헤어지게 됩니다 💔\n\n"
            "아우라 가치관 밸런스 매칭으로 연락 스타일, 데이트 취향, 소비관까지 나와 찰떡인 인연을 미리 확인하고 만나보세요!\n\n"
            "✨ 밸런스 매칭 핵심 혜택:\n"
            "1️⃣ 연애 가치관 12가지 항목 100% 매칭률 분석\n"
            "2️⃣ 대화 전 서로의 라이프스타일 미리 확인\n"
            "3️⃣ 성향 불일치로 인한 감정 낭비 제로\n\n"
            "👉 프로필 링크나 네이버에서 [아우라AI데이팅]을 검색하세요!"
        ),
        "threads_text": (
            "데이트 비용 전액 부담 vs 5:5 더치페이, 뭐가 맞다고 생각함?\n"
            "이런 가치관 미리 맞춰보고 만나는 게 백배 낫더라.\n"
            "여러분의 연애 필수 가치관 1위는?"
        ),
        "fb_text": (
            "얼굴보다 가치관이 더 중요해진 2030 연애! 나랑 찰떡궁합인 인연을 아우라 밸런스 매칭으로 찾아보세요.\n"
            "댓글 링크에서 무료 테스트 가능합니다."
        ),
        "hashtags": "#가치관매칭 #연애밸런스게임 #아우라AI데이팅 #연애가치관 #데이트비용 #소개팅앱 #Shorts #Reels #TikTok"
    },
    6: {
        "theme_name": "AI 첫대화 비서",
        "theme_code": "ai_chat_assistant",
        "yt_title": "소개팅 매칭되고 첫마디 '안녕하세요' 보냈다가 읽씹당한 사람 필독 #Shorts",
        "yt_desc": (
            "어렵게 매칭됐는데 첫인사로 '안녕하세요 ㅎㅎ' 보냈다가 읽씹당해서 허탈하셨나요?\n"
            "아우라 AI 대화 비서가 상대방 프로필과 사진, 관심사를 정밀 분석해서 답장률 99% 심쿵 첫마디와 대화 주제를 추천해줍니다!\n"
            "대화 끊길 걱정 없이 자연스러운 티키타카를 시작하세요.\n\n"
            "👉 AI 첫대화 추천받기\n"
            "🔗 네이버 검색창에 [아우라AI데이팅] 검색!\n"
            "공식 라운지: https://aura-ai-dating.vercel.app/lounge\n"
        ),
        "pinned_comment": "첫마디 읽씹 방지! 답장률 99% AI 대화 비서, 네이버에 '아우라AI데이팅' 검색해보세요 💬",
        "tiktok_caption": (
            "소개팅 매칭되고 첫마디 뭐라고 보내야 할지 10분 고민하는 사람 ㅋㅋㅋ\n"
            "AI가 상대방 취향 분석해서 답장 100% 오는 멘트 써줌 ㄷㄷ\n"
            "👇 프로필 링크에서 확인해보세요!"
        ),
        "reels_caption": (
            "소개팅 앱에서 '안녕하세요'는 읽씹 1순위 멘트입니다 🚫\n\n"
            "아우라 AI 대화 비서로 상대방의 프로필 사진과 취미를 녹여낸 자연스럽고 매력적인 오프닝 멘트를 추천받아보세요!\n\n"
            "✨ AI 대화 비서 핵심 기능:\n"
            "1️⃣ 상대 프로필 기반 답장 유도형 첫인사 추천\n"
            "2️⃣ 어색한 침묵 깰 수 있는 맞춤형 스몰토크 제안\n"
            "3️⃣ 만남 약속으로 이어지는 자연스러운 멘트 가이드\n\n"
            "👉 프로필 링크나 네이버에서 [아우라AI데이팅]을 검색하세요!"
        ),
        "threads_text": (
            "소개팅 앱에서 매칭됐을 때 가장 받기 싫은 첫마디:\n"
            "1. 안녕하세요 ㅎㅎ\n"
            "2. 프사 예쁘시네요\n"
            "3. 주말에 뭐하세요\n"
            "진짜 센스 있는 첫마디는 AI가 상대 취향 맞춰서 짜주는 게 최고임 ㅋㅋㅋ"
        ),
        "fb_text": (
            "매칭은 됐는데 무슨 말을 해야 할지 막막할 때! AI 첫대화 비서가 티키타카를 완성해드립니다.\n"
            "댓글 링크에서 바로 확인하세요!"
        ),
        "hashtags": "#소개팅첫인사 #대화꿀팁 #아우라AI데이팅 #연애스킬 #카톡첫마디 #소개팅앱 #Shorts #Reels #TikTok"
    },
    7: {
        "theme_name": "AI 아우라 진단",
        "theme_code": "ai_aura_diagnosis",
        "yt_title": "내 얼굴 매력 지수는 상위 몇 %일까? AI가 1초 만에 분석해주는 아우라 진단 #Shorts",
        "yt_desc": (
            "내 얼굴은 청순상? 여우상? 분위기 상위 몇 %일까 궁금하지 않으셨나요?\n"
            "아우라 AI 외모 진단으로 내 사진 속 얼굴형, 이목구비 비율, 독보적인 매력 키워드를 정밀 분석받아보세요!\n"
            "나만의 매력을 알고 나면 소개팅 매칭 성공률이 수직 상승합니다.\n\n"
            "👉 내 AI 아우라 매력 진단받기\n"
            "🔗 네이버 검색창에 [아우라AI데이팅] 검색!\n"
            "공식 라운지: https://aura-ai-dating.vercel.app/lounge\n"
        ),
        "pinned_comment": "내 매력 지수 상위 몇 %? 네이버에 '아우라AI데이팅' 검색하고 무료 AI 진단 받아보세요 ✨",
        "tiktok_caption": (
            "친구들이랑 다 같이 해봤는데 소름 돋게 정확한 AI 외모/매력 분석 ㅋㅋㅋ\n"
            "내 매력 키워드랑 상위 % 바로 나옴!\n"
            "👇 프로필 링크에서 지금 무료로 진단해보세요!"
        ),
        "reels_caption": (
            "내 진짜 매력과 아우라를 객관적으로 분석해주는 AI 진단 등장! 🔍\n\n"
            "황금비율 이목구비 분석부터 나에게 가장 어울리는 연애 스타일과 매력 키워드까지 완벽 리포트를 제공합니다.\n\n"
            "✨ Aura AI 진단 리포트:\n"
            "1️⃣ 상위 % 매력 지수 및 외모 타입 분석\n"
            "2️⃣ 나에게 찰떡으로 꽂히는 이성 취향 매칭\n"
            "3️⃣ 프로필 매력도 극대화 꿀팁 제공\n\n"
            "👉 프로필 상단 링크나 네이버에서 [아우라AI데이팅]을 검색하세요!"
        ),
        "threads_text": (
            "AI 외모 진단 돌려봤는데 상위 0.1% 여우상 나옴 ㅋㅋㅋ\n"
            "친구들끼리 돌려보니까 은근 정확하고 꿀잼이네요.\n"
            "다들 무슨 상 나오셨나요?"
        ),
        "fb_text": (
            "내 매력 지수와 외모 스타일을 AI로 정밀 분석! 나만의 연애 아우라를 찾아보세요.\n"
            "댓글 링크에서 무료 진단 가능합니다."
        ),
        "hashtags": "#AI외모진단 #얼굴분석 #아우라AI데이팅 #외모테스트 #매력진단 #소개팅앱 #Shorts #Reels #TikTok"
    },
    8: {
        "theme_name": "500m 안심 레이더",
        "theme_code": "safe_radar",
        "yt_title": "소개팅 앱에서 집 주소 노출될까 봐 불안했던 분들 필독 (500m 안심 보안) #Shorts",
        "yt_desc": (
            "동네 친구 만나고 싶은데 집 주소나 정확한 위치 노출될까 봐 불안해서 망설이셨나요?\n"
            "아우라는 내 실제 집 위치를 500미터 랜덤 보안(지터링)으로 완벽하게 보호해줍니다!\n"
            "스토킹 걱정 제로! 성수동 카페 메이트, 한강 러닝 메이트를 안전하게 당일 번개로 만나보세요.\n\n"
            "👉 안전한 동네 친구 번개 퀘스트\n"
            "🔗 네이버 검색창에 [아우라AI데이팅] 검색!\n"
            "공식 라운지: https://aura-ai-dating.vercel.app/lounge\n"
        ),
        "pinned_comment": "스토킹 걱정 제로! 500m 안심 지터링 보안 동네 친구, 네이버에 '아우라AI데이팅' 검색해보세요 🛡️",
        "tiktok_caption": (
            "동네 친구 찾고 싶은데 집 주소 털릴까 봐 불안했던 사람 필독 🚨\n"
            "500m 랜덤 보안으로 내 위치 철통 방어하면서 당일 번개 메이트 찾기!\n"
            "👇 프로필 링크에서 동네 퀘스트 확인해보세요!"
        ),
        "reels_caption": (
            "동네 친구 만나고 싶은데 위치 노출될까 봐 무서우셨죠? 🛡️\n\n"
            "아우라의 '500m 안심 지터링 레이더'는 내 실제 주소를 절대 노출하지 않고 500m 반경 랜덤 보안으로 프라이버시를 완벽 보호합니다!\n\n"
            "✨ Aura 500m 안심 레이더 혜택:\n"
            "1️⃣ 실제 집 주소 노출 ZERO! 500m 지터링 보안\n"
            "2️⃣ 성수동 카페 번개, 러닝 메이트 당일 퀘스트\n"
            "3️⃣ 100% 실명/본인 인증 안전한 동네 친구\n\n"
            "👉 프로필 링크나 네이버에서 [아우라AI데이팅]을 검색하세요!"
        ),
        "threads_text": (
            "동네 산책 메이트나 러닝 친구 찾을 때 집 위치 노출 불안한 사람 나뿐임?\n"
            "아우라는 500미터 랜덤 보안 걸어줘서 집 주소 절대 안 털리더라.\n"
            "동네 친구 번개, 동성만 가능 vs 이성도 가능?"
        ),
        "fb_text": (
            "스토킹 불안 제로! 500m 안심 보안으로 내 위치는 안전하게 지키고, 동네 친구는 편하게 만나보세요.\n"
            "댓글 링크에서 바로 확인 가능합니다."
        ),
        "hashtags": "#동네친구 #번개모임 #500m안심레이더 #아우라AI데이팅 #러닝메이트 #산책메이트 #소개팅앱 #Shorts #Reels #TikTok"
    }
}


class AuraSNSGuideGenerator:
    """Aura 데이팅 전용 5대 SNS 포스팅 가이드 텍스트 자동 생성기"""

    OFFICIAL_SEARCH_KEYWORD = "아우라AI데이팅"
    OFFICIAL_LANDING_URL = "https://aura-ai-dating.vercel.app/lounge"

    @classmethod
    def generate_guide_content(
        cls,
        topic_id: int = 1,
        speech_hook: Optional[str] = None,
        custom_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        주제 ID(1~8)에 맞춰 5대 SNS(YouTube Shorts, TikTok, Instagram Reels, Threads, Facebook Reels)
        원클릭 복사용 포스팅 가이드 텍스트를 완성하여 반환합니다.
        """
        norm_id = ((topic_id - 1) % len(AURA_TOPIC_SNS_DATA)) + 1
        data = AURA_TOPIC_SNS_DATA.get(norm_id, AURA_TOPIC_SNS_DATA[1])

        theme_name = data["theme_name"]
        theme_code = data["theme_code"]
        yt_title = data["yt_title"]
        yt_desc = data["yt_desc"]
        pinned_comment = data["pinned_comment"]
        tiktok_caption = data.get("tiktok_caption", "")
        reels_caption = data.get("reels_caption", "")
        threads_text = data.get("threads_text", "")
        fb_text = data.get("fb_text", "")
        # 🌟 실시간 바이럴 해시태그 융합 (AuraKeywordMatrix 실시간 검색 트렌드 + 2030 네이버/구글 핫키워드)
        base_raw_tags = data.get("hashtags", "").split()
        try:
            from brands.aura.aura_keyword_matrix import AuraKeywordMatrix
            matrix = AuraKeywordMatrix()
            live_tag_list = matrix.get_live_hashtags(topic_id=norm_id, base_tags=base_raw_tags, count=10)
            hashtags = " ".join(live_tag_list)
        except Exception:
            hashtags = data["hashtags"]

        speech_summary = speech_hook or "2030 프리미엄 AI 데이팅 아우라 핵심 기능 소개"

        content = f"""================================================================================
🎬 [AURA AI 데이팅 - 숏폼 5대 SNS 원클릭 포스팅 가이드]
================================================================================
주제 번호: #{norm_id} [{theme_name}]
테마 코드: {theme_code}
영상 규격: 1080x1920 (9:16 세로 풀HD 숏폼, 22초)
공식 네이버 검색어: {cls.OFFICIAL_SEARCH_KEYWORD}  (← 붙여쓰기 고정)
공식 랜딩 URL: {cls.OFFICIAL_LANDING_URL}
발화 훅 요약: {speech_summary}
🏷️ 추천 통합 해시태그: {hashtags}
================================================================================

[1] 🔴 유튜브 쇼츠 (YouTube Shorts) 포스팅 가이드
--------------------------------------------------------------------------------
📌 [쇼츠 제목 (Title)]
{yt_title}

📌 [쇼츠 설명 (Description)]
{yt_desc}

📌 [고정 댓글 (Pinned Comment)]
{pinned_comment}


[2] 🎵 틱톡 (TikTok) 포스팅 가이드
--------------------------------------------------------------------------------
📌 [추천 캡션 (복사용 원문)]
{tiktok_caption}

{hashtags}

📌 [프로필 바이오 / 댓글 안내]
👉 Link in Bio: {cls.OFFICIAL_LANDING_URL}
👉 네이버 검색창에 [{cls.OFFICIAL_SEARCH_KEYWORD}] 검색!


[3] 📸 인스타그램 릴스 (Instagram Reels) 포스팅 가이드
--------------------------------------------------------------------------------
📌 [추천 캡션 (복사용 원문)]
{reels_caption}

{hashtags}

📌 [프로필 링크 안내]
🔗 Bio Link: @aura_official -> {cls.OFFICIAL_LANDING_URL}


[4] 🧵 스레드 (Threads) 포스팅 가이드
--------------------------------------------------------------------------------
📌 [본문 텍스트 (텍스트 바이럴 & 공감 질문형)]
{threads_text}

💬 [첫 번째 댓글 (전환 링크)]
👉 안전한 동네 친구 & 50:50 데이팅 바로가기: {cls.OFFICIAL_LANDING_URL}


[5] 📘 페이스북 릴스 (Facebook Reels) 포스팅 가이드
--------------------------------------------------------------------------------
📌 [피드 본문 (알고리즘 도달 극대화 - 본문 링크 배제)]
{fb_text}

{hashtags}

💬 [첫 번째 댓글 (전환 링크 자동 배치)]
👉 네이버에 [{cls.OFFICIAL_SEARCH_KEYWORD}] 검색 또는 바로가기: {cls.OFFICIAL_LANDING_URL}
================================================================================
"""
        return content

    @classmethod
    def save_guide_file(
        cls,
        output_folder: Path,
        topic_id: int = 1,
        speech_hook: Optional[str] = None
    ) -> Path:
        """지정된 폴더에 SNS_포스팅_가이드.txt 파일 저장"""
        output_folder.mkdir(parents=True, exist_ok=True)
        file_path = output_folder / "SNS_포스팅_가이드.txt"
        content = cls.generate_guide_content(topic_id=topic_id, speech_hook=speech_hook)
        file_path.write_text(content, encoding="utf-8")
        logger.info(f"📄 [Aura SNS 가이드 저장 완료] 파일: {file_path}")
        return file_path
