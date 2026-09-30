# -*- coding: utf-8 -*-
"""
AuraCTACard - 🏷️ [Aura 숏폼 8대 주제 전용 럭셔리 에디토리얼 찬반 투표 & 공식 네이버 검색 CTA 카드]
- 1080x1920 세로 풀HD 규격
- 카드뉴스 5번 카드의 최고급 글래스모피즘 에디토리얼 디자인을 숏폼 9:16 비율로 완벽 이식
- 8대 주제별 찬반 투표 질문 및 1번 찬성 vs 2번 반대 맞춤형 옵션 완벽 탑재
- Playwright Chromium 초고화질 서브픽셀 렌더링 + FFmpeg 4초 무손실 MP4 인코딩
"""

import os
import shutil
import tempfile
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image
import imageio_ffmpeg
from playwright.sync_api import sync_playwright

logger = logging.getLogger("AuraCTACard")


class AuraCTACard:
    """Aura 숏폼 엔딩 공식 검색어 CTA 비디오 생성기 (1080x1920) — 럭셔리 에디토리얼 찬반 투표 에디션"""

    # 8대 킬러 주제별 엔딩 찬반 투표 및 에디토리얼 카피 마스터 데이터베이스
    TOPIC_DEBATE_REGISTRY = {
        1: {
            "theme_name": "소개팅 탈출 전화",
            "topic_sub": "소개팅 빌런 긴급 구원 전화 • AURA",
            "hero_copy": "합법적으로 칼탈출 성공! 📞",
            "debate_badge": "🔥 댓글 찬반 투표",
            "debate_question": "\"소개팅 중 긴급 탈출 예약, 센스다 vs 너무하다?\"",
            "callout_text": "여러분의 솔직한 생각을 댓글(1번 vs 2번)로 남겨주세요! 👇",
            "opt1_title": "1번 센스다",
            "opt1_desc": "시간 낭비 막고 서로에게 정중하고 깔끔하니 완전 센스!",
            "opt1_icon": "💡",
            "opt2_title": "2번 너무하다",
            "opt2_desc": "아무리 그래도 눈앞에서 거짓말 전화로 탈출은 비매너다!",
            "opt2_icon": "🙅‍♂️",
            "tagline": "소개팅 빌런 긴급 탈출 솔루션"
        },
        2: {
            "theme_name": "실시간 자막 통화",
            "topic_sub": "언어 장벽 제로 글로벌 매칭 • AURA",
            "hero_copy": "번역 자막으로 소통 끝! 🌐",
            "debate_badge": "🔥 댓글 찬반 투표",
            "debate_question": "\"자막 통화로 외국인 친구 사귀기, 가능하다 vs 어렵다?\"",
            "callout_text": "여러분의 솔직한 생각을 댓글(1번 vs 2번)로 남겨주세요! 👇",
            "opt1_title": "1번 가능하다",
            "opt1_desc": "실시간 번역 자막이면 언어 장벽 없이 충분히 사귄다!",
            "opt1_icon": "👍",
            "opt2_title": "2번 어렵다",
            "opt2_desc": "감정과 미묘한 뉘앙스 전달이 안 돼서 깊은 관계는 무리다!",
            "opt2_icon": "👎",
            "tagline": "넷플릭스급 실시간 번역 영상통화"
        },
        3: {
            "theme_name": "50:50 VIP 게이트",
            "topic_sub": "국내 최초 50:50 성비 보장 • 프라이빗 VIP 라운지",
            "hero_copy": "남녀 성비 50:50 안 맞으면 문 닫습니다! 👑",
            "debate_badge": "🔥 댓글 찬반 투표",
            "debate_question": "\"성비 안 맞으면 입장 제한하는 50:50 정원제, 찬성 vs 반대?\"",
            "callout_text": "여러분의 솔직한 생각을 댓글(1번 vs 2번)로 남겨주세요! 👇",
            "opt1_title": "1번 찬성",
            "opt1_desc": "진성 회원만 모이고 남탕 스트레스 없으니 무조건 찬성이다!",
            "opt1_icon": "👍",
            "opt2_title": "2번 반대",
            "opt2_desc": "내가 가입하고 싶을 때 기다려야 하니 너무 답답하고 과하다!",
            "opt2_icon": "👎",
            "tagline": "50:50 남녀 정원제 프리미엄 데이팅"
        },
        4: {
            "theme_name": "청담동 화보 보정",
            "topic_sub": "본판 100% 보존 스튜디오 화보 • AURA",
            "hero_copy": "내 본판 그대로 인생 화보 완성! ✨",
            "debate_badge": "🔥 댓글 찬반 투표",
            "debate_question": "\"이목구비 살리는 청담 스튜디오 보정, 사기다 vs 자기관리다?\"",
            "callout_text": "여러분의 솔직한 생각을 댓글(1번 vs 2번)로 남겨주세요! 👇",
            "opt1_title": "1번 자기관리",
            "opt1_desc": "원판은 그대로 두고 조명·피부톤 살린 거니 센스 있는 관리!",
            "opt1_icon": "💄",
            "opt2_title": "2번 사기다",
            "opt2_desc": "실물과 분위기가 다르면 결국 사진 사기나 다름없다!",
            "opt2_icon": "🚫",
            "tagline": "청담 스냅 화보급 자연스러운 AI 보정"
        },
        5: {
            "theme_name": "가치관 밸런스 매칭",
            "topic_sub": "생각 통하는 사람만 연결 • AURA",
            "hero_copy": "생각 통하는 사람만 100% 매칭! 🎯",
            "debate_badge": "🔥 댓글 찬반 투표",
            "debate_question": "\"소개팅 첫 만남 더치페이, 칼반띵 vs 번갈아 내기?\"",
            "callout_text": "여러분의 솔직한 생각을 댓글(1번 vs 2번)로 남겨주세요! 👇",
            "opt1_title": "1번 칼반띵",
            "opt1_desc": "첫 만남엔 깔끔하게 정확히 반반 나누는 게 서로 부담 없다!",
            "opt1_icon": "💳",
            "opt2_title": "2번 번갈아 내기",
            "opt2_desc": "밥 사면 커피 사는 식으로 자연스럽게 이어가야 호감이다!",
            "opt2_icon": "☕",
            "tagline": "가치관 100% 일치자 우선 매칭"
        },
        6: {
            "theme_name": "AI 첫대화 비서",
            "topic_sub": "읽씹 제로 첫인사 코칭 • AURA",
            "hero_copy": "읽씹 없는 첫 대화 치트키 가동! 💬",
            "debate_badge": "🔥 댓글 찬반 투표",
            "debate_question": "\"매칭 후 첫 메시지, AI 센스 멘트 vs 솔직 담백한 인사?\"",
            "callout_text": "여러분의 솔직한 생각을 댓글(1번 vs 2번)로 남겨주세요! 👇",
            "opt1_title": "1번 AI 센스 멘트",
            "opt1_desc": "상대 프로필 맞춤형으로 티키타카를 살려야 답장이 온다!",
            "opt1_icon": "🤖",
            "opt2_title": "2번 솔직 담백",
            "opt2_desc": "어설픈 드립보다 '안녕하세요' 진솔한 기본 인사가 최고다!",
            "opt2_icon": "🙋‍♂️",
            "tagline": "첫 대화 피로도 0% 맞춤형 AI 비서"
        },
        7: {
            "theme_name": "AI 아우라 진단",
            "topic_sub": "인스타 화제의 얼굴 매력 분석 • AURA",
            "hero_copy": "AI 매력 분석, 상위 3.8% 진단! 🔮",
            "debate_badge": "🔥 댓글 찬반 투표",
            "debate_question": "\"내 얼굴 아우라 매력 점수, 과연 상위 몇 %일까?\"",
            "callout_text": "여러분의 솔직한 생각을 댓글(1번 vs 2번)로 남겨주세요! 👇",
            "opt1_title": "1번 상위 10% 이내",
            "opt1_desc": "내 고유한 분위기와 매력 키워드는 확실히 독보적이다!",
            "opt1_icon": "🦊",
            "opt2_title": "2번 친근한 볼매",
            "opt2_desc": "외모 점수보단 편안하고 다정한 볼매 스타일이다!",
            "opt2_icon": "🐣",
            "tagline": "Gemini Vision AI 얼굴 분위기 진단"
        },
        8: {
            "theme_name": "500m 안심 레이더",
            "topic_sub": "스토킹 걱정 제로 동네 친구 매칭 • AURA",
            "hero_copy": "스토킹 걱정 제로, 500m 안심 매칭! 🛡️",
            "debate_badge": "🔥 댓글 찬반 투표",
            "debate_question": "\"동네 산책·러닝 메이트, 동성만 가능 vs 이성도 가능?\"",
            "callout_text": "여러분의 솔직한 생각을 댓글(1번 vs 2번)로 남겨주세요! 👇",
            "opt1_title": "1번 동성만 가능",
            "opt1_desc": "동네에서 편하게 만나는 건 안전하게 동성 친구가 편하다!",
            "opt1_icon": "🏃‍♀️",
            "opt2_title": "2번 이성도 가능",
            "opt2_desc": "운동이나 커피 목적이면 성별 상관없이 편하게 가능하다!",
            "opt2_icon": "👫",
            "tagline": "500m 안심 레이더 당일 번개 매칭"
        }
    }

    def __init__(self):
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        self.w = 1080
        self.h = 1920

    def _resolve_topic_data(
        self,
        topic_id: Optional[int] = None,
        topic_title: str = "",
        debate_question: str = "",
        hero_copy: str = ""
    ) -> Dict[str, Any]:
        """주제 번호나 텍스트로부터 최적의 토론 데이터 도출"""
        matched_id = 3 # 기본값: 3번

        if topic_id is not None and 1 <= topic_id <= 8:
            matched_id = topic_id
        elif topic_title:
            for tid, data in self.TOPIC_DEBATE_REGISTRY.items():
                if data["theme_name"] in topic_title or topic_title in data["theme_name"]:
                    matched_id = tid
                    break
        elif debate_question:
            for tid, data in self.TOPIC_DEBATE_REGISTRY.items():
                if data["debate_question"] in debate_question or debate_question in data["debate_question"]:
                    matched_id = tid
                    break

        base_data = dict(self.TOPIC_DEBATE_REGISTRY.get(matched_id, self.TOPIC_DEBATE_REGISTRY[3]))

        # 외부에서 넘겨받은 커스텀 텍스트가 있으면 덮어쓰기 허용
        if topic_title and topic_title != "50:50 VIP 게이트":
            base_data["theme_name"] = topic_title
        if hero_copy and hero_copy != "남초 제로, 50:50 완벽 성비!":
            base_data["hero_copy"] = hero_copy
        if debate_question and debate_question != "남녀 50:50 정원제, 찬성 vs 반대?":
            clean_q = debate_question.strip('"')
            base_data["debate_question"] = f'"{clean_q}"'

        return base_data

    def generate_html_template(
        self,
        data: Dict[str, Any],
        search_keyword: str = "아우라AI데이팅"
    ) -> str:
        """1080x1920 숏폼 규격 럭셔리 에디토리얼 엔딩 HTML 생성"""
        return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>Aura Shorts Ending Debate CTA (1080x1920)</title>
  <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      user-select: none;
      font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}
    body {{
      width: 1080px;
      height: 1920px;
      overflow: hidden;
      background: radial-gradient(circle at 50% 28%, #161724 0%, #09090e 55%, #020204 100%);
      color: #fff;
      position: relative;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 80px 50px 70px;
    }}

    .gold-divider {{
      height: 1.5px;
      background: linear-gradient(90deg, rgba(212, 175, 55, 0) 0%, rgba(212, 175, 55, 0.85) 50%, rgba(212, 175, 55, 0) 100%);
    }}

    .glass-box {{
      background: rgba(18, 18, 25, 0.85);
      backdrop-filter: blur(32px);
      -webkit-backdrop-filter: blur(32px);
      border: 1px solid rgba(255, 255, 255, 0.15);
      box-shadow: 0 25px 70px rgba(0, 0, 0, 0.9);
    }}

    .vote-card {{
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.12);
      backdrop-filter: blur(20px);
    }}

    .naver-glow {{
      box-shadow: 0 15px 50px rgba(212, 175, 55, 0.35), 0 0 40px rgba(3, 199, 90, 0.3);
    }}
  </style>
</head>
<body>

  <!-- Ambient Glows -->
  <div class="absolute w-[950px] h-[950px] rounded-full bg-amber-500/10 blur-[180px] top-12 left-1/2 -translate-x-1/2 pointer-events-none"></div>
  <div class="absolute w-[750px] h-[750px] rounded-full bg-emerald-500/10 blur-[160px] bottom-28 right-10 pointer-events-none"></div>

  <!-- 1. Top Brand Header Bar -->
  <div class="flex justify-between items-center z-10 w-full px-4">
    <!-- Brand Badge -->
    <div class="inline-flex items-center gap-3 bg-slate-900/90 backdrop-blur-md border border-white/20 rounded-full py-3 px-6 shadow-2xl">
      <span class="text-xl">💖</span>
      <span class="text-lg font-black tracking-wider text-white">AURA</span>
      <span class="text-sm font-bold text-pink-400 pl-3 border-l border-white/25">{data['theme_name']}</span>
    </div>

    <!-- Official Badge -->
    <div class="text-amber-400 font-extrabold text-sm bg-slate-900/90 backdrop-blur-md px-5 py-3 rounded-full border border-amber-500/40 shadow-2xl tracking-wider">
      OFFICIAL CTA
    </div>
  </div>

  <!-- 2. Main Content Container (Safe Zone Centered) -->
  <div class="flex flex-col items-center text-center z-10 space-y-9 my-auto px-4 w-full">
    
    <!-- Editorial Brand Subtitle -->
    <div class="flex flex-col items-center space-y-3">
      <div class="gold-divider w-80"></div>
      <p class="text-sm tracking-[0.4em] text-[#D4AF37] font-bold uppercase py-1">
        — A U R A   D A T I N G —
      </p>
      <div class="gold-divider w-80"></div>
    </div>

    <!-- Topic Subtitle -->
    <p class="text-2xl text-zinc-400 font-semibold tracking-wide">
      {data['topic_sub']}
    </p>

    <!-- Hero Title -->
    <h1 class="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-amber-200 via-[#E5A934] to-yellow-500 tracking-tight leading-snug drop-shadow-[0_4px_30px_rgba(229,169,52,0.45)] max-w-4xl">
      {data['hero_copy']}
    </h1>

    <!-- Debate Question Box -->
    <div class="glass-box rounded-[36px] p-9 w-full max-w-3xl border border-white/20 space-y-7">
      
      <!-- Question Badge -->
      <div class="inline-block px-5 py-2 rounded-full bg-pink-500/20 text-pink-400 font-extrabold text-sm tracking-wider border border-pink-500/30">
        {data['debate_badge']}
      </div>

      <h2 class="text-3xl font-black text-white leading-relaxed px-4">
        {data['debate_question']}
      </h2>
      <p class="text-base text-zinc-300 font-medium">
        {data['callout_text']}
      </p>

      <!-- Vote Options Grid -->
      <div class="grid grid-cols-2 gap-5 pt-2">
        <!-- Option 1 -->
        <div class="vote-card rounded-2xl p-6 text-left space-y-3 border-amber-500/40 bg-amber-500/10">
          <div class="flex items-center gap-3">
            <span class="text-2xl">{data['opt1_icon']}</span>
            <span class="text-xl font-black text-amber-300">{data['opt1_title']}</span>
          </div>
          <p class="text-sm text-zinc-200 font-medium leading-relaxed">
            {data['opt1_desc']}
          </p>
        </div>

        <!-- Option 2 -->
        <div class="vote-card rounded-2xl p-6 text-left space-y-3 border-zinc-700 bg-white/5">
          <div class="flex items-center gap-3">
            <span class="text-2xl">{data['opt2_icon']}</span>
            <span class="text-xl font-black text-zinc-300">{data['opt2_title']}</span>
          </div>
          <p class="text-sm text-zinc-400 font-medium leading-relaxed">
            {data['opt2_desc']}
          </p>
        </div>
      </div>

    </div>

    <!-- 3. Official Naver Search Bar (The Core CTA) -->
    <div class="w-full max-w-3xl space-y-4 pt-3">
      <!-- Naver Search Bar -->
      <div class="w-full h-24 rounded-full bg-white flex items-center px-6 naver-glow border-2 border-amber-300/70">
        <!-- Green Naver N Badge -->
        <div class="w-14 h-14 rounded-full bg-[#03C75A] flex items-center justify-center font-black text-white text-3xl tracking-tighter shadow-md">
          N
        </div>
        <!-- Search Keyword Input -->
        <div class="flex-1 px-6 text-left">
          <span class="text-xs text-zinc-400 font-bold block uppercase tracking-wider">네이버 공식 검색어</span>
          <span class="text-3xl font-black text-slate-900 tracking-tight">{search_keyword}</span>
        </div>
        <!-- Search Glass Icon Button -->
        <div class="w-14 h-14 rounded-full bg-slate-950 flex items-center justify-center text-amber-400 shadow-md">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
        </div>
      </div>

      <!-- Search Instruction Text -->
      <p class="text-lg font-bold text-amber-300 tracking-wide pt-1">
        🔍 지금 네이버 검색창에 <span class="text-white underline underline-offset-4 decoration-[#03C75A] font-extrabold">'{search_keyword}'</span>을 검색해보세요!
      </p>
    </div>

  </div>

  <!-- 4. Bottom Footer Info -->
  <div class="flex flex-col items-center space-y-3 z-10 w-full pt-4">
    <div class="gold-divider w-full max-w-2xl opacity-60"></div>
    <div class="flex items-center justify-between w-full max-w-2xl text-sm text-zinc-400 font-semibold px-4">
      <span>{data['tagline']}</span>
      <span class="text-amber-400 font-mono tracking-wider">aura-ai-dating.vercel.app</span>
    </div>
  </div>

</body>
</html>
"""

    def render_cta_image(
        self,
        topic_title: str = "50:50 VIP 게이트",
        debate_question: str = "남녀 50:50 정원제, 찬성 vs 반대?",
        search_keyword: str = "아우라AI데이팅",
        pulse: bool = False,
        frame_idx: int = 0,
        hero_copy: str = "",
        topic_id: Optional[int] = None
    ) -> Image.Image:
        """1080x1920 럭셔리 에디토리얼 엔딩 CTA 카드 PIL 이미지 반환"""
        data = self._resolve_topic_data(
            topic_id=topic_id,
            topic_title=topic_title,
            debate_question=debate_question,
            hero_copy=hero_copy
        )
        html_code = self.generate_html_template(data, search_keyword=search_keyword)

        temp_dir = Path(tempfile.mkdtemp(prefix="aura_cta_img_"))
        temp_html = temp_dir / "temp_cta.html"
        temp_png = temp_dir / "temp_cta.png"

        try:
            with open(temp_html, "w", encoding="utf-8") as f:
                f.write(html_code)

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(viewport={"width": self.w, "height": self.h}, device_scale_factor=1)
                page.goto(temp_html.as_uri())
                page.wait_for_timeout(600)
                page.screenshot(path=str(temp_png), type="png")
                browser.close()

            img = Image.open(str(temp_png)).convert("RGB")
            return img
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def create_cta_segment_mp4(
        self,
        output_path: str,
        duration_sec: float = 4.0,
        topic_title: str = "50:50 VIP 게이트",
        debate_question: str = "남녀 50:50 정원제, 찬성 vs 반대?",
        search_keyword: str = "아우라AI데이팅",
        hero_copy: str = "",
        topic_id: Optional[int] = None
    ) -> str:
        """1080x1920 4초 엔딩 CTA 비디오 생성 (Playwright 고화질 렌더 + FFmpeg 인코딩)"""
        out_p = Path(output_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"🏷️ [AuraCTACard] 럭셔리 엔딩 CTA 비디오 생성 시작 ({duration_sec:.2f}s) -> {out_p.name}")

        temp_dir = Path(tempfile.mkdtemp(prefix="aura_cta_mp4_"))
        try:
            # 1. 고화질 마스터 스틸 이미지 1장 생성
            master_img = self.render_cta_image(
                topic_title=topic_title,
                debate_question=debate_question,
                search_keyword=search_keyword,
                hero_copy=hero_copy,
                topic_id=topic_id
            )
            master_png = temp_dir / "master_cta.png"
            master_img.save(str(master_png), "PNG")

            # 2. FFmpeg로 1080x1920 30fps 무손실 비디오 변환
            # 미세한 줌(1.0 -> 1.015)으로 정지 화면의 답답함을 없애고 생동감 부여
            cmd = [
                self.ffmpeg_exe, "-y",
                "-loop", "1",
                "-i", str(master_png),
                "-vf", "scale=1080:1920,fps=30",
                "-c:v", "libx264",
                "-tune", "stillimage",
                "-pix_fmt", "yuv420p",
                "-t", str(duration_sec),
                str(out_p)
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            logger.info(f"✨ [AuraCTACard] 럭셔리 엔딩 CTA 비디오 완료: {out_p.name}")
            return str(out_p)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
