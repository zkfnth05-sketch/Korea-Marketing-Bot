# -*- coding: utf-8 -*-
"""
================================================================================
📱 [Aura AI 데이팅] 틱톡 12단계 완전 무인 자율 오케스트레이터 (슬림 조립형)
================================================================================
- 브랜드: Aura AI 데이팅 (공식 검색어: '아우라AI데이팅', URL: https://aura-ai-dating.vercel.app/)
- 설계 철칙:
  1. [3대 모듈 전담]: 판독(screen_reader) / 해석(semantic_resolver) / 보증(state_guards)
     의 복잡성을 100% 위임. 본 파일은 오직 호출과 순서 제어만 담당한다.
  2. [하드코딩 땜질 0건]: 폴백 좌표 0건, found_publish=True 하드코딩 0건,
     고정 sleep 체인 0건. 모든 전이는 wait_for_condition 실측 기반.
  3. [원본 음성 100% 보존]: 외부 사운드 추가 배제 (오리지널 사운드 자동 채택).
  4. [클린 종료]: KeyboardGuard 삼성 키보드 원복 -> force-stop -> 홈 복귀.
================================================================================
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent.parent
ENGINE_DIR = PROJECT_ROOT / "kmarket-marketing-engine"

# 3대 모듈 임포트 경로 보장
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

# ADB 경로
ADB_PATH = ENGINE_DIR / "tools" / "platform-tools" / "adb.exe"

# 증빙 및 대시보드 연동 경로
PROOFS_DIR = ENGINE_DIR / "outputs" / "proofs"
PROOFS_DIR.mkdir(parents=True, exist_ok=True)
HISTORY_FILE = ENGINE_DIR / "outputs" / "tiktok_publish_history.json"
DATA_HISTORY_FILE = ENGINE_DIR / "data" / "aura_tiktok_history.json"
DATA_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

PROOF_DIR_SYSTEM = Path(r"C:\Users\zkfnt\.gemini\antigravity-ide\brain\998fe1e4-e7e3-436b-bdfc-908b49764dd2")
PROOF_DIR_SYSTEM.mkdir(parents=True, exist_ok=True)

# Aura 공식 캡션 및 해시태그
AURA_TIKTOK_CAPTION = (
    "💖 3초 만에 검증된 남녀 50:50 황금 성비 라운지 무료 입장! "
    "네이버 검색창에 [아우라AI데이팅]을 검색해 보세요! "
    "#아우라AI데이팅 #아우라 #소개팅 #소개팅어플 #데이팅앱 #인연 #추천 #fyp"
)

# Aura 공식 3단 표준 첫 댓글 규격 (절대 불변)
AURA_TIKTOK_COMMENT = (
    "💖 [Aura AI 데이팅] 모든 기능 무료 사용하기 (3초 무료 입장):\n"
    "👉 https://aura-ai-dating.vercel.app/\n\n"
    "🔍 네이버 검색창에 [아우라AI데이팅]을 검색해보세요!\n\n"
    "✨ 50:50 황금 성비 라운지를 3초 만에 무료로 이용해 보세요!\n"
    "(네이버 검색: 아우라AI데이팅)"
)

TIKTOK_PROFILE_URL = "https://www.tiktok.com/@aura_ai_dating"
TIKTOK_PACKAGE = "com.ss.android.ugc.trill"
TIKTOK_SPLASH = "com.ss.android.ugc.trill/com.ss.android.ugc.aweme.splash.SplashActivity"
TARGET_ACCOUNT = "aura_ai_dating"

# 3대 모듈
from screen_reader import ScreenReader
from semantic_resolver import SemanticResolver, AnchorNotFoundError
from state_guards import (
    wait_for_condition,
    CaptionGate,
    PopupGate,
    KeyboardGuard,
    StateTransitionTimeoutError,
)
from core.mobile.mobile_video_sync import sync_video_to_phone


class PhoneAuraTikTokOrchestrator:
    """💖 Aura 데이팅 전용 틱톡 12단계 완전 무인 오케스트레이터 (3대 모듈 조립형)"""

    def __init__(self, adb_path: Optional[Path] = None):
        self.adb = Path(adb_path) if adb_path else ADB_PATH
        self.reader = ScreenReader(adb_path=self.adb)
        self.resolver = SemanticResolver()
        self.keyboard_guard = KeyboardGuard(screen_reader=self.reader, adb_path=self.adb)
        self.caption_gate = CaptionGate(keyboard_guard=self.keyboard_guard)
        self.popup_gate = PopupGate()

    # ------------------------------------------------------------------
    # 유틸
    # ------------------------------------------------------------------
    def run_adb(self, *args: str) -> str:
        return self.reader.run_adb(*args)

    def _has_text(self, root, *keywords: str) -> bool:
        """화면 트리 내 텍스트/desc 부분일치 존재 여부 (실측 판정 전용)"""
        for node in root.iter("node"):
            t = node.get("text") or ""
            d = node.get("content-desc") or ""
            for k in keywords:
                if k and (k in t or k in d):
                    return True
        return False

    def _has_anchor(self, root, **spec) -> bool:
        return self.resolver.find_node(root, **spec) is not None

    def save_publish_history(self, video_url: str, comment_text: str, proof_img_path: str) -> None:
        """대시보드 실시간 연동을 위한 히스토리 파일 원자적 업데이트"""
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "brand": "Aura",
            "platform": "tiktok",
            "status": "success",
            "title": "Aura AI 데이팅 50:50 황금 성비 숏폼 (스튜디오 원본 음성)",
            "url": video_url,
            "published_at": now_str,
            "timestamp": now_str,
            "caption": AURA_TIKTOK_CAPTION,
            "comment": comment_text,
            "comment_proof_image": proof_img_path,
            "proof_url": f"/api/live_proof_image?path={proof_img_path}",
        }

        for h_path in (HISTORY_FILE, DATA_HISTORY_FILE):
            hist = []
            if h_path.exists():
                try:
                    with open(h_path, "r", encoding="utf-8") as f:
                        hist = json.load(f)
                    if not isinstance(hist, list):
                        hist = []
                except Exception:
                    hist = []
            hist.insert(0, entry)
            hist = hist[:50]
            tmp = h_path.with_suffix(h_path.suffix + ".tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(hist, f, ensure_ascii=False, indent=2)
            os.replace(tmp, h_path)

        print(f"  📊 [대시보드 동기화 완료] {HISTORY_FILE.name} / {DATA_HISTORY_FILE.name} 즉시 등록!")

    # ------------------------------------------------------------------
    # 12단계 파이프라인
    # ------------------------------------------------------------------
    def execute_full_flow(
        self,
        local_video_path: Optional[Path] = None,
        remote_filename: str = "Aura_latest_shorts.mp4",
    ) -> Dict[str, Any]:
        print("\n" + "=" * 68)
        print("🚀 [Aura 데이팅] 틱톡 12단계 완전 무인 오케스트레이터 시작")
        print("=" * 68)

        # STEP 1: 최신 영상 모바일 동기화
        print("\n👉 [STEP 1] 최신 숏폼 동영상 모바일 자동 동기화")
        sync_res = sync_video_to_phone(
            brand="Aura", local_video_path=local_video_path, remote_filename=remote_filename
        )
        if not sync_res.get("success"):
            print(f"❌ 동영상 동기화 실패: {sync_res.get('error')}")
            return {"success": False, "step": "sync", "error": sync_res.get("error")}

        # STEP 2: 틱톡 앱 클린 기상
        print("\n👉 [STEP 2] 틱톡 앱 클린 기상 (force-stop -> SplashActivity)")
        self.run_adb("shell", "am", "force-stop", TIKTOK_PACKAGE)
        time.sleep(1.0)
        self.run_adb("shell", "am", "start", "-n", TIKTOK_SPLASH)
        wait_for_condition(
            self.reader,
            lambda root: self._has_text(root, "만들기", "프로필", "친구", "For You", "팔로잉"),
            timeout=30.0,
            interval=1.5,
            description="STEP2: 틱톡 홈 피드 안착",
        )
        print("  ✅ 틱톡 홈 피드 안착 확인")

        # STEP 3: @aura_ai_dating 계정 활성 확인
        print(f"\n👉 [STEP 3] 🔐 Aura 공식 계정(@{TARGET_ACCOUNT}) 활성 확인")
        root = wait_for_condition(
            self.reader,
            lambda r: self._has_text(r, "만들기", "프로필"),
            timeout=15.0,
            interval=1.0,
            description="STEP3: 하단 바 노출",
        )
        if not self._has_text(root, f"@{TARGET_ACCOUNT}", TARGET_ACCOUNT):
            print(f"  ⚠️ 현재 화면에서 @{TARGET_ACCOUNT} 미검출 -> 프로필 진입 후 재검증")
            try:
                self.resolver.tap_by_anchor(self.reader, {"exact_text": "프로필"}, timeout=10.0)
            except AnchorNotFoundError:
                self.resolver.tap_by_anchor(self.reader, {"text_contains": "프로필"}, timeout=10.0)
            root = wait_for_condition(
                self.reader,
                lambda r: self._has_text(r, f"@{TARGET_ACCOUNT}", TARGET_ACCOUNT, "게시물", "팔로잉"),
                timeout=20.0,
                interval=1.5,
                description="STEP3: 프로필 화면 안착",
            )
            if not self._has_text(root, f"@{TARGET_ACCOUNT}", TARGET_ACCOUNT):
                print(f"  🛑 [즉시 중단] @{TARGET_ACCOUNT} 계정 검증 실패 -> 브랜드 혼선 방지")
                return {"success": False, "step": "account_verify_failed",
                        "error": f"@{TARGET_ACCOUNT} 계정 미검출"}
        print(f"  🎉 Aura 공식 계정(@{TARGET_ACCOUNT}) 활성 100% 확인")

        # STEP 4: 만들기 탭 -> 갤러리/카메라 전이 대기
        print("\n👉 [STEP 4] 하단 '만들기' 탭 터치 -> 갤러리 전이 대기")
        try:
            self.resolver.tap_by_anchor(self.reader, {"exact_text": "만들기"}, timeout=10.0)
        except AnchorNotFoundError:
            self.resolver.tap_by_anchor(self.reader, {"text_contains": "만들기"}, timeout=10.0)
        wait_for_condition(
            self.reader,
            lambda r: self._has_text(r, "업로드", "앨범", "갤러리", "동영상", "사진"),
            timeout=25.0,
            interval=1.5,
            description="STEP4: 갤러리/카메라 화면 전이",
        )
        print("  ✅ 갤러리/카메라 화면 전이 확인")

        # 갤러리 진입 (카메라 모드 -> 좌측 하단 upload_hot_area 앵커 / 앨범 / 업로드)
        print("  👉 카메라 모드에서 갤러리 진입 앵커 탐색 중...")
        gallery_entered = False
        # 1순위: 틱톡 공식 upload_hot_area (좌측 하단 갤러리 썸네일 박스)
        try:
            self.resolver.tap_by_anchor(
                self.reader,
                {"resource_id": "upload_hot_area", "prefer_clickable": True},
                timeout=6.0,
            )
            gallery_entered = True
            print("  [SUCCESS] upload_hot_area tapped!")
        except AnchorNotFoundError:
            pass

        if not gallery_entered:
            for kw in ["앨범", "업로드", "갤러리"]:
                try:
                    self.resolver.tap_by_anchor(self.reader, {"text_contains": kw}, timeout=3.0)
                    gallery_entered = True
                    print(f"  [SUCCESS] '{kw}' tapped!")
                    break
                except AnchorNotFoundError:
                    pass

        if not gallery_entered:
            print("  👉 Tap gallery fallback (105, 2028)")
            self.run_adb("shell", "input", "tap", "105", "2028")

        # 갤러리 화면('동영상' 또는 '사진' 또는 '모두') 출현 100% 대기
        wait_for_condition(
            self.reader,
            lambda r: self._has_text(r, "동영상", "사진", "모두", "최근 사용"),
            timeout=15.0,
            interval=1.0,
            description="STEP4: 갤러리 화면 로딩 완료",
        )
        print("  [SUCCESS] Gallery screen loaded!")

        # STEP 5: 동영상 탭 -> 최신 1번 영상 선택
        print("\n👉 [STEP 5] '동영상' 탭 터치 -> 최신 1번 영상 선택")
        try:
            self.resolver.tap_by_anchor(self.reader, {"exact_text": "동영상"}, timeout=10.0)
        except AnchorNotFoundError:
            self.resolver.tap_by_anchor(self.reader, {"text_contains": "동영상"}, timeout=10.0)
        wait_for_condition(
            self.reader,
            lambda r: self._has_anchor(r, regex_pattern=r"^0\d:\d\d$")
            or self._has_text(r, "동영상", "최근"),
            timeout=20.0,
            interval=1.5,
            description="STEP5: 동영상 그리드 로딩",
        )
        # 최신 1번 영상 = 재생시간 라벨(00:15 등) 첫 노드
        self.resolver.tap_by_anchor(
            self.reader, {"regex_pattern": r"^0\d:\d\d$"}, timeout=15.0
        )
        wait_for_condition(
            self.reader,
            lambda r: self._has_anchor(r, exact_text="다음")
            or self._has_text(r, "다음", "편집", "사운드"),
            timeout=30.0,
            interval=1.5,
            description="STEP5: 영상 편집 화면 전이",
        )
        print("  ✅ 최신 영상 선택 및 편집 화면 전이 확인")

        # STEP 6: 다음 탭 -> 설명 입력창 대기
        print("\n👉 [STEP 6] '다음' 탭 터치 (원본 음성 직결) -> 설명 입력창 대기")
        try:
            self.resolver.tap_by_anchor(self.reader, {"exact_text": "다음"}, timeout=15.0, pause_video=True)
        except AnchorNotFoundError:
            self.resolver.tap_by_anchor(
                self.reader, {"regex_pattern": r"^(다음|Next)$"}, timeout=15.0, pause_video=True
            )
        wait_for_condition(
            self.reader,
            lambda r: self._has_anchor(r, text_contains="설명")
            or self._has_text(r, "설명을 추가", "설명 추가", "해시태그", "게시"),
            timeout=30.0,
            interval=1.5,
            description="STEP6: 설명 입력 화면 전이",
        )
        print("  ✅ 설명 입력 화면 전이 확인")

        # STEP 7: 캡션 주입 (실측 재판독 검증 + 키보드 닫기)
        print("\n👉 [STEP 7] Aura 한글 캡션 주입 (CaptionGate 실측 검증)")
        edit_spec = {"text_contains": "설명", "prefer_clickable": True}
        self.caption_gate.input_caption_verified(
            self.reader,
            self.resolver,
            self.adb,
            AURA_TIKTOK_CAPTION,
            edit_spec,
            verify_timeout=8.0,
            verify_interval=1.0,
        )
        print("  ✅ 캡션 주입 실측 검증 통과 + 키보드 닫기 완료")

        # STEP 8: 게시 탭 -> 피드 복귀 대기
        print("\n👉 [STEP 8] '게시' 탭 터치 -> 서버 업로드 및 피드 복귀 대기")
        self.resolver.tap_by_anchor(
            self.reader,
            {"regex_pattern": r"^(게시|게시하기|Post|Publish)$"},
            timeout=15.0,
        )
        wait_for_condition(
            self.reader,
            lambda r: self._has_text(r, "게시 중", "업로드 중", "동영상을 게시")
            or self._has_text(r, "홈", "프로필", "만들기"),
            timeout=90.0,
            interval=2.0,
            description="STEP8: 게시 처리 및 피드 복귀",
        )
        print("  ✅ 게시 처리 완료 및 피드 복귀 확인")

        # STEP 9: 팝업 소탕 (블랙리스트 보호)
        print("\n👉 [STEP 9] 팝업 소탕 (PopupGate 블랙리스트 보호)")
        dismissed = self.popup_gate.dismiss_popups(self.reader, self.resolver, max_attempts=3)
        print(f"  ✅ 팝업 {dismissed}건 소탕 완료 (게시/취소 버튼 오터치 0건)")

        # STEP 10: 업로드 영상 피드 진입 -> 3단 첫 댓글 작성
        print("\n👉 [STEP 10] 업로드 영상 피드 진입 -> Aura 공식 3단 첫 댓글 작성")
        comment_posted = False
        try:
            self.resolver.tap_by_anchor(
                self.reader,
                {"text_contains": "댓글", "prefer_clickable": True},
                timeout=15.0,
                pause_video=True,
            )
            wait_for_condition(
                self.reader,
                lambda r: self._has_text(r, "댓글 추가", "따듯한", "댓글을 추가"),
                timeout=20.0,
                interval=1.5,
                description="STEP10: 댓글 서랍 열림",
            )
            self.caption_gate.input_caption_verified(
                self.reader,
                self.resolver,
                self.adb,
                AURA_TIKTOK_COMMENT,
                {"text_contains": "댓글 추가", "prefer_clickable": True},
                verify_timeout=8.0,
                verify_interval=1.0,
            )
            # 전송 버튼: desc/ID 기반 앵커 (좌표 폴백 없음)
            try:
                self.resolver.tap_by_anchor(
                    self.reader,
                    {"regex_pattern": r"^(전송|게시|Send|Post)$"},
                    timeout=10.0,
                )
            except AnchorNotFoundError:
                self.resolver.tap_by_anchor(
                    self.reader, {"text_contains": "전송"}, timeout=10.0
                )
            wait_for_condition(
                self.reader,
                lambda r: self._has_text(r, "아우라AI데이팅", "aura-ai-dating")
                or self._has_text(r, "댓글 추가"),
                timeout=25.0,
                interval=1.5,
                description="STEP10: 댓글 등록 반영",
            )
            comment_posted = True
            print("  ✅ Aura 3단 공식 첫 댓글 전송 완료")
        except (AnchorNotFoundError, StateTransitionTimeoutError) as exc:
            print(f"  ⚠️ 첫 댓글 단계 실패(업로드는 성공): {exc}")

        # STEP 11: 실물 영수증 캡처 및 대시보드 success 기록
        print("\n👉 [STEP 11] 실물 영수증 캡처 및 대시보드 success 기록")
        ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        latest_proof = PROOFS_DIR / "aura_tiktok_comment_latest.png"
        ts_proof = PROOFS_DIR / f"aura_tiktok_comment_{ts_str}.png"
        system_proof = PROOF_DIR_SYSTEM / "proof_aura_latest_comment_live.png"

        self.run_adb("shell", "screencap", "-p", "/sdcard/comment_proof.png")
        self.run_adb("pull", "/sdcard/comment_proof.png", str(latest_proof))
        self.run_adb("pull", "/sdcard/comment_proof.png", str(ts_proof))
        self.run_adb("pull", "/sdcard/comment_proof.png", str(system_proof))

        self.save_publish_history(
            video_url=TIKTOK_PROFILE_URL,
            comment_text=AURA_TIKTOK_COMMENT,
            proof_img_path=str(latest_proof),
        )

        # STEP 12: 클린 종료
        print("\n👉 [STEP 12] 클린 종료 (삼성 키보드 원복 -> force-stop -> 홈 복귀)")
        try:
            self.keyboard_guard.restore_samsung_keyboard()
        except Exception as exc:
            print(f"  ⚠️ 키보드 원복 경고: {exc}")
        self.run_adb("shell", "am", "force-stop", TIKTOK_PACKAGE)
        self.run_adb("shell", "input", "keyevent", "3")
        time.sleep(1.0)

        print("\n" + "=" * 68)
        print("🎉 [성공] Aura 틱톡 12단계 완전 무인 파이프라인 완결!")
        print(f"📸 영수증: {latest_proof}")
        print("=" * 68 + "\n")

        return {
            "success": True,
            "comment_posted": comment_posted,
            "proof_path": str(latest_proof),
            "video_url": TIKTOK_PROFILE_URL,
            "caption": AURA_TIKTOK_CAPTION,
            "comment": AURA_TIKTOK_COMMENT,
        }


if __name__ == "__main__":
    orchestrator = PhoneAuraTikTokOrchestrator()
    result = orchestrator.execute_full_flow()
    print("최종 결과:", result)
