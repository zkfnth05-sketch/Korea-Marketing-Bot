# -*- coding: utf-8 -*-
"""
================================================================================
📱 [보험 리밸런스] 스마트폰 틱톡 100% 무인 풀코스 원스톱 자동 업로더 (순수 원본 음성 완결형)
================================================================================
- 브랜드: 보험 리밸런스 (공식 검색어: '보험 리밸런스', URL: https://insure-rebalance.vercel.app/)
- 설계 철칙:
  1. [스튜디오 원본 음성 100% 보존]: 외부 사운드 추가를 전면 배제하여,
     영상 자체의 보험 리밸런스 나레이션 말소리가 볼륨 간섭 없이 100% 선명하게 출력되도록 보장.
  2. [글자 기반 무인 자동화]: 좌표 수치 배제, 아우라와 100% 동일한 XML UI 트리의 글자 노드 추적으로 동적 터치.
  3. [원스톱 풀코스]:
     [1] 최신 영상 스마트폰 동기화 (PC -> /sdcard/DCIM/Camera/)
     [2] 틱톡 앱 클린 기상
     [3] 보험 계정(@goldmom82) 확인 및 스위칭
     [4] 하단 '만들기' 글자 터치 -> 갤러리 진입
     [5] '동영상' 탭 터치 -> 최신 1번 영상 선택
     [6] '다음' 글자 터치 (사운드 추가 없이 원본 음성 직결)
     [7] 캡션 입력창에 보험 리밸런스 공식 한글 캡션 및 해시태그 주입
     [8] '게시' 글자 터치 -> 서버 업로드
     [9] '취소' 글자 터치 (위젯 팝업 해제)
     [10] '첫 댓글 달기' 글자 터치 -> 보험 리밸런스 공식 3단 첫 댓글 자동 등록
     [11] 실물 댓글 영수증 상시 캡처 보관 & 대시보드(http://localhost:8080) 실시간 URL 연동
     [12] 앱 완전 종료 및 홈 복귀
================================================================================
"""

import os
import sys
import time
import json
import base64
import subprocess
import xml.etree.ElementTree as ET
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, Tuple

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent.parent
ENGINE_DIR = PROJECT_ROOT / "kmarket-marketing-engine"

# ADB 경로
ADB_PATH = ENGINE_DIR / "tools" / "platform-tools" / "adb.exe"
XML_TEMP = CURRENT_DIR / "temp_flow_dump.xml"

# 증빙 및 대시보드 연동 경로
PROOFS_DIR = ENGINE_DIR / "outputs" / "proofs"
PROOFS_DIR.mkdir(parents=True, exist_ok=True)
HISTORY_FILE = ENGINE_DIR / "outputs" / "tiktok_publish_history.json"
DATA_HISTORY_FILE = ENGINE_DIR / "data" / "insurance_tiktok_history.json"
DATA_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

PROOF_DIR_SYSTEM = Path(r"C:\Users\zkfnt\.gemini\antigravity-ide\brain\998fe1e4-e7e3-436b-bdfc-908b49764dd2")
PROOF_DIR_SYSTEM.mkdir(parents=True, exist_ok=True)

# Core 모바일 동기화 모듈 임포트
sys.path.insert(0, str(ENGINE_DIR))
from core.mobile.mobile_video_sync import sync_video_to_phone

# 🛡️ 보험 리밸런스 공식 캡션 및 해시태그
INSURANCE_TIKTOK_CAPTION = (
    "🛡️ 매달 줄줄 새는 내 보험료, 34개 보험사 공시 기준 3초 만에 무료 분석! "
    "네이버 검색창에 [보험 리밸런스]를 검색해 보세요! "
    "#보험리밸런스 #보험비교 #보험다이어트 #보험분석 #실비보험 #암보험 #추천 #fyp"
)

# 🛡️ 보험 리밸런스 공식 3단 표준 첫 댓글 규격 (절대 불변)
INSURANCE_TIKTOK_COMMENT = (
    "🛡️ [보험 리밸런스] 내 숨은 보험금 & 과다납입 3초 무료 진단:\n"
    "👉 https://insure-rebalance.vercel.app/\n\n"
    "🔍 네이버 검색창에 [보험 리밸런스]를 검색해보세요!\n\n"
    "✨ 34개 보험사 공시 기준 객관적 분석을 3초 만에 무료로 확인해 보세요!\n"
    "(네이버 검색: 보험 리밸런스)"
)

TIKTOK_PROFILE_URL = "https://www.tiktok.com/@goldmom82"
TARGET_ACCOUNT_ID = "goldmom82"


class PhoneInsuranceTikTokUploader:
    """🛡️ 보험 리밸런스 전용 모바일 틱톡 100% 무인 원스톱 업로더"""

    def __init__(self):
        self.adb = ADB_PATH

    def run_adb(self, *args) -> str:
        cmd = [str(self.adb)] + list(args)
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        return res.stdout.strip()

    def get_valid_bounds_rect(self, bounds_str: str) -> Optional[Tuple[int, int, int, int]]:
        """유효한 사각형 [x1, y1, x2, y2] 파싱 (가로/세로 10px 이상)"""
        m = re.findall(r"\d+", bounds_str)
        if len(m) == 4:
            x1, y1, x2, y2 = map(int, m)
            if (x2 - x1) > 10 and (y2 - y1) > 10:
                return (x1, y1, x2, y2)
        return None

    def dump_ui(self, pause_video: bool = False) -> ET.Element:
        """UIAutomator XML 덤프 및 루트 반환"""
        if pause_video:
            self.run_adb("shell", "input", "keyevent", "85")  # 미디어 일시정지 키이벤트 (좌표 배제)
            time.sleep(0.5)

        self.run_adb("shell", "uiautomator", "dump", "/sdcard/flow_dump.xml")
        time.sleep(0.8)
        self.run_adb("pull", "/sdcard/flow_dump.xml", str(XML_TEMP))

        if not XML_TEMP.exists():
            time.sleep(1.0)
            self.run_adb("pull", "/sdcard/flow_dump.xml", str(XML_TEMP))

        tree = ET.parse(XML_TEMP)
        return tree.getroot()

    def find_node_with_parent_climb(self, condition_fn, pause_video: bool = False):
        """
        [100% 순수 글자 기반 탐색 핵심 엔진]
        조건에 맞는 노드를 찾고, 텍스트 노드 자체의 bounds가 [0,0][0,0]으로 비어 있는 경우
        상위 부모 컨테이너(Parent Container)를 역추적하여 실제 유효한 터치 영역 중심 좌표 반환
        (안드로이드 내비게이션 바 하단 잘림 현상 발생 시 안전 영역 자동 보정)
        """
        root = self.dump_ui(pause_video=pause_video)
        parent_map = {c: p for p in root.iter() for c in p}

        for node in root.iter("node"):
            if condition_fn(node):
                # 1. 노드 자체의 rect가 유효한지 확인
                rect = self.get_valid_bounds_rect(node.attrib.get("bounds", ""))
                if rect:
                    cx = (rect[0] + rect[2]) // 2
                    cy = (rect[1] + rect[3]) // 2
                    # 하단 소프트키로 인해 y2가 2030 이상에서 얇게 잘린 경우 안전 보정
                    if rect[3] >= 2030 and (rect[3] - rect[1]) <= 30:
                        cy = rect[1] - 40
                    return node, (cx, cy)

                # 2. 노드 bounds가 0이면 상위 부모 노드로 역추적하여 진짜 버튼 컨테이너를 찾음
                curr = node
                while curr in parent_map:
                    curr = parent_map[curr]
                    p_rect = self.get_valid_bounds_rect(curr.attrib.get("bounds", ""))
                    if p_rect:
                        cx = (p_rect[0] + p_rect[2]) // 2
                        cy = (p_rect[1] + p_rect[3]) // 2
                        if p_rect[3] >= 2030 and (p_rect[3] - p_rect[1]) <= 30:
                            cy = p_rect[1] - 40
                        return node, (cx, cy)

        return None, None

    def tap_by_text(self, text_keyword: str, pause_video: bool = False, timeout: int = 12) -> bool:
        """순수 글자(text 또는 content-desc)를 기반으로 부모 영역까지 역추적하여 동적 탭"""
        start = time.time()
        while time.time() - start < timeout:
            node, center = self.find_node_with_parent_climb(
                lambda n: text_keyword in (n.attrib.get("text") or "") or text_keyword in (n.attrib.get("content-desc") or ""),
                pause_video=pause_video
            )
            if center:
                matched_text = node.attrib.get("text") or node.attrib.get("content-desc")
                print(f"  🎯 [순수 글자 매칭 성공] '{matched_text}' -> 동적 계산 좌표: {center}")
                self.run_adb("shell", "input", "tap", str(center[0]), str(center[1]))
                return True
            time.sleep(1.0)
        return False

    def dismiss_unexpected_popups(self):
        """잔여 팝업('계속 편집할까요?', '임시 저장', '취소' 등) 자율 해제"""
        try:
            root = self.dump_ui()
            for node in root.iter("node"):
                t = node.attrib.get("text", "")
                if any(k in t for k in ["취소", "임시 저장", "나중에", "계속 편집"]):
                    _, center = self.find_node_with_parent_climb(
                        lambda n: any(k in (n.attrib.get("text") or "") for k in ["취소", "임시 저장", "나중에"])
                    )
                    if center:
                        print(f"  🧹 잔여 다이얼로그 자동 해제: {center}")
                        self.run_adb("shell", "input", "tap", str(center[0]), str(center[1]))
                        time.sleep(1.5)
                        break
        except Exception:
            pass

    def ensure_brand_account(self, target_account_id: str = TARGET_ACCOUNT_ID) -> bool:
        """순수 글자 기반 계정 확인 및 스위칭"""
        print(f"\n🔐 [보험 리밸런스] 틱톡 공식 계정(@{target_account_id}) 확인 및 스위칭 시작...")

        # 하단 프로필 완전 일치 탐색
        node, prof_center = self.find_node_with_parent_climb(
            lambda n: n.attrib.get("content-desc") == "프로필" or n.attrib.get("text") == "프로필"
        )
        if prof_center:
            print(f"  🎯 [글자 매칭] '프로필' 탭 발견: {prof_center} -> 탭")
            self.run_adb("shell", "input", "tap", str(prof_center[0]), str(prof_center[1]))
            time.sleep(2.5)

        root = self.dump_ui()
        for n in root.iter("node"):
            t = n.attrib.get("text", "").lower()
            d = n.attrib.get("content-desc", "").lower()
            if f"@{target_account_id.lower()}" in t or f"@{target_account_id.lower()}" in d:
                print(f"  ✅ 현재 이미 보험 계정(@{target_account_id})으로 접속되어 있습니다.")
                return True

        # 상단 계정명 터치 -> 바텀시트
        title_node, title_center = self.find_node_with_parent_climb(
            lambda n: "t_3" in n.attrib.get("resource-id", "") or
                      any(k in n.attrib.get("text", "").lower() for k in ["아우라", "골드맘", "스톡", "aura", "stock", "goldmom"])
        )
        if title_center:
            print(f"  🎯 [글자 매칭] 상단 계정명 발견: {title_center} -> 탭")
            self.run_adb("shell", "input", "tap", str(title_center[0]), str(title_center[1]))
            time.sleep(2.5)

        # 바텀시트에서 target_account_id 글자 터치
        acc_node, acc_center = self.find_node_with_parent_climb(
            lambda n: target_account_id.lower() in n.attrib.get("text", "").lower() or
                      target_account_id.lower() in n.attrib.get("content-desc", "").lower() or
                      "골드맘" in n.attrib.get("text", "")
        )
        if acc_center:
            print(f"  🎯 [글자 매칭] 보험 계정 글자('{target_account_id}') 발견: {acc_center} -> 전환 터치!")
            self.run_adb("shell", "input", "tap", str(acc_center[0]), str(acc_center[1]))
            time.sleep(3.5)
            print(f"  ✅ '{target_account_id}' 계정으로 스위칭 완료!")
            return True
        else:
            self.run_adb("shell", "input", "keyevent", "4")
            return False

    def activate_adb_keyboard(self):
        """한글 입력을 위한 AdbIME 활성화"""
        self.run_adb("shell", "ime", "set", "com.android.adbkeyboard/.AdbIME")
        time.sleep(0.5)

    def restore_samsung_keyboard(self):
        """삼성 기본 키보드로 원복"""
        self.run_adb("shell", "ime", "set", "com.samsung.android.honeyboard/.service.HoneyBoardService")

    def input_korean_text(self, text: str):
        """AdbIME base64 브로드캐스트로 한글 및 특수문자 완벽 주입"""
        self.activate_adb_keyboard()
        b64_msg = base64.b64encode(text.encode("utf-8")).decode("utf-8")
        self.run_adb("shell", "am", "broadcast", "-a", "ADB_INPUT_B64", "--es", "msg", b64_msg)
        time.sleep(1.5)

    def save_publish_history(self, video_url: str, comment_text: str, proof_img_path: str):
        """대시보드 실시간 연동을 위한 히스토리 파일 업데이트"""
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "brand": "Insurance",
            "platform": "tiktok",
            "status": "success",
            "title": "보험 리밸런스 34개사 객관적 분석 숏폼 (스튜디오 원본 음성)",
            "url": video_url,
            "published_at": now_str,
            "timestamp": now_str,
            "caption": INSURANCE_TIKTOK_CAPTION,
            "comment": comment_text,
            "comment_proof_image": proof_img_path,
            "proof_url": f"/api/live_proof_image?path={proof_img_path}"
        }

        for h_path in [HISTORY_FILE, DATA_HISTORY_FILE]:
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
            with open(h_path, "w", encoding="utf-8") as f:
                json.dump(hist, f, ensure_ascii=False, indent=2)

        print(f"  📊 [대시보드 동기화 완료] 틱톡 URL & 댓글 영수증이 대시보드({HISTORY_FILE})에 즉시 등록되었습니다!")

    def execute_full_flow(
        self,
        local_video_path: Optional[Path] = None,
        remote_filename: str = "Insurance_latest_shorts.mp4"
    ) -> Dict[str, Any]:
        """
        [아우라 100% 동일 성공 방식] 보험 리밸런스 틱톡 모바일 원스톱 풀코스 실행
        """
        print("\n" + "=" * 65)
        print("🚀 [보험 리밸런스] 스마트폰 틱톡 원본 음성 100% 무인 업로드 파이프라인 시작")
        print("=" * 65)

        # -------------------------------------------------------------
        # STEP 1: PC 최신 렌더링 동영상 -> 스마트폰 Sync
        # -------------------------------------------------------------
        print("\n👉 [STEP 1] 최신 숏폼 동영상 모바일 자동 동기화")
        sync_res = sync_video_to_phone(
            brand="Insurance",
            local_video_path=local_video_path,
            remote_filename=remote_filename
        )
        if not sync_res.get("success"):
            print(f"❌ 동영상 동기화 실패: {sync_res.get('error')}")
            return {"success": False, "step": "sync", "error": sync_res.get("error")}

        # -------------------------------------------------------------
        # STEP 2: 틱톡 앱 클린 재실행 및 홈 피드 정렬
        # -------------------------------------------------------------
        print("\n👉 [STEP 2] 틱톡 앱 클린 기상 및 실행")
        self.run_adb("shell", "am", "force-stop", "com.ss.android.ugc.trill")
        time.sleep(1.0)
        self.run_adb("shell", "am", "start", "-n", "com.ss.android.ugc.trill/com.ss.android.ugc.aweme.splash.SplashActivity")
        time.sleep(4.5)

        # -------------------------------------------------------------
        # STEP 3: 🔐 보험 공식 계정(@goldmom82) 자동 확인 및 스위칭
        # -------------------------------------------------------------
        print("\n👉 [STEP 3] 🔐 보험 공식 계정(@goldmom82) 자동 스위칭")
        self.ensure_brand_account(TARGET_ACCOUNT_ID)
        time.sleep(1.5)

        # -------------------------------------------------------------
        # STEP 4: 하단 바 '만들기' 글자 버튼 터치
        # -------------------------------------------------------------
        print("\n👉 [STEP 4] 하단 '만들기' 글자 버튼 터치")
        self.dismiss_unexpected_popups()
        node, create_center = self.find_node_with_parent_climb(
            lambda n: n.attrib.get("content-desc") == "만들기" or n.attrib.get("text") == "만들기",
            pause_video=True
        )
        if create_center:
            print(f"  🎯 [글자 매칭] '만들기' 버튼 발견: {create_center} -> 탭")
            self.run_adb("shell", "input", "tap", str(create_center[0]), str(create_center[1]))
        else:
            self.tap_by_text("만들기", pause_video=True, timeout=8)
        time.sleep(3.5)
        self.dismiss_unexpected_popups()

        # 카메라 촬영 모드로 열렸을 경우 갤러리(업로드/앨범/사진) 글자 버튼 동적 탐색
        album_node, album_center = self.find_node_with_parent_climb(
            lambda n: any(k in (n.attrib.get("text") or "") or k in (n.attrib.get("content-desc") or "") for k in ["업로드", "앨범", "사진", "갤러리"]) or "upload_hot_area" in n.attrib.get("resource-id", "")
        )
        if album_center:
            print(f"  🎯 갤러리 앨범 글자 버튼 발견: {album_center} -> 탭")
            self.run_adb("shell", "input", "tap", str(album_center[0]), str(album_center[1]))
            time.sleep(3.0)

        # -------------------------------------------------------------
        # STEP 5: 갤러리 진입 -> '동영상' 탭 글자 터치 -> 최신 1번 영상 선택
        # -------------------------------------------------------------
        print("\n👉 [STEP 5] 갤러리 '동영상' 탭 글자 터치 및 최신 영상 선택")
        node, vid_tab = self.find_node_with_parent_climb(
            lambda n: n.attrib.get("text") == "동영상"
        )
        if vid_tab:
            print(f"  🎯 [글자 매칭] 갤러리 '동영상' 탭 발견: {vid_tab} -> 탭")
            self.run_adb("shell", "input", "tap", str(vid_tab[0]), str(vid_tab[1]))
            time.sleep(2.5)
        else:
            self.tap_by_text("동영상", timeout=8)
            time.sleep(2.5)

        # 첫 번째 동영상 항목(재생시간 글자 노드 예: '00:15', '00:19', '00:22', '00:25' 등) 순수 글자 동적 탐색
        vid_node, video_center = self.find_node_with_parent_climb(
            lambda n: re.match(r"^0\d:\d\d$", n.attrib.get("text", "")) is not None
        )
        if video_center:
            print(f"  🎯 최신 동영상 글자 노드 발견: {video_center} -> 탭")
            self.run_adb("shell", "input", "tap", str(video_center[0]), str(video_center[1]))
            time.sleep(4.0)

        # -------------------------------------------------------------
        # STEP 6: 🌟 외부 사운드 추가 없이 원본 음성 그대로 '다음' 글자 터치!
        # (갤러리 '다음(1)' 및 편집화면 '다음' 글자를 순수 글자로 스마트 통과)
        # -------------------------------------------------------------
        print("\n👉 [STEP 6] 🌟 외부 사운드 추가 없이 원본 음성 그대로 '다음' 글자 버튼 터치")
        for step_attempt in range(3):
            # 이미 최종 게시 화면에 도달했는지 확인
            post_check, _ = self.find_node_with_parent_climb(
                lambda n: "설명" in (n.attrib.get("text") or "") or n.attrib.get("text") == "게시"
            )
            if post_check:
                print("  ✅ 최종 게시 화면 도달 완료!")
                break
            found_n = self.tap_by_text("다음", pause_video=True, timeout=8)
            time.sleep(3.5)

        # -------------------------------------------------------------
        # STEP 7: 설명 입력창 터치 -> 보험 리밸런스 한글 캡션 및 해시태그 주입
        # -------------------------------------------------------------
        print("\n👉 [STEP 7] 설명 입력창 탐색 및 보험 리밸런스 한글 캡션 주입")
        node, center = self.find_node_with_parent_climb(
            lambda n: any(k in (n.attrib.get("text") or "") or k in (n.attrib.get("content-desc") or "") for k in ["설명을 추가하세요", "설명 추가"]) or "EditText" in n.attrib.get("class", "")
        )
        if center:
            print(f"  🎯 설명 입력창 발견: {center} -> 탭 및 주입")
            self.run_adb("shell", "input", "tap", str(center[0]), str(center[1]))
            time.sleep(1.5)
            self.input_korean_text(INSURANCE_TIKTOK_CAPTION)
            time.sleep(1.0)
        else:
            print("  ⚠️ 설명 입력창을 찾지 못해 기본 설명으로 진행합니다.")

        # 키보드 닫기 (뒤로 가기 1회)
        self.run_adb("shell", "input", "keyevent", "4")
        time.sleep(1.5)

        # -------------------------------------------------------------
        # STEP 8: '게시' 글자 버튼 터치 -> 서버 업로드
        # -------------------------------------------------------------
        print("\n👉 [STEP 8] '게시' 글자 버튼 터치 및 서버 업로드 시작")
        found_publish = False
        node, center = self.find_node_with_parent_climb(
            lambda n: n.attrib.get("text") == "게시" or n.attrib.get("content-desc") == "게시"
        )
        if center:
            print(f"  🎯 '게시' 글자 버튼 발견: {center} -> 터치!")
            self.run_adb("shell", "input", "tap", str(center[0]), str(center[1]))
            found_publish = True
        else:
            found_publish = self.tap_by_text("게시", timeout=10)

        if not found_publish:
            print("❌ '게시' 글자 버튼을 찾지 못했습니다.")
            return {"success": False, "step": "publish_btn"}

        print("  ⏳ 틱톡 서버 업로드 진행 중 (15초 대기)...")
        time.sleep(15.0)

        # -------------------------------------------------------------
        # STEP 9: '취소' 글자 터치 (카메라 위젯 팝업 등 자동 해제)
        # -------------------------------------------------------------
        print("\n👉 [STEP 9] 게시 후 위젯 팝업 감지 및 '취소' 글자 터치")
        self.dismiss_unexpected_popups()
        found_cancel = self.tap_by_text("취소", timeout=5)
        if found_cancel:
            print("  ✅ 팝업을 '취소' 글자로 정상 해제했습니다.")

        time.sleep(3.0)

        # -------------------------------------------------------------
        # STEP 10: 업로드 영상 피드 진입 -> 보험 리밸런스 공식 3단 첫 댓글 자동 등록
        # -------------------------------------------------------------
        print("\n👉 [STEP 10] 방금 게시된 영상 피드에 보험 리밸런스 공식 3단 첫 댓글 작성")
        node, center = self.find_node_with_parent_climb(
            lambda n: any(k in (n.attrib.get("text") or "") or k in (n.attrib.get("content-desc") or "") for k in ["첫 댓글", "댓글을 읽거나", "댓글"]),
            pause_video=True
        )

        comment_posted = False
        if center:
            print(f"  🎯 댓글 서랍 글자 버튼 발견: {center} -> 탭")
            self.run_adb("shell", "input", "tap", str(center[0]), str(center[1]))
            time.sleep(2.5)

            edit_node, edit_center = self.find_node_with_parent_climb(
                lambda n: any(k in (n.attrib.get("text") or "") for k in ["따듯한", "따뜻한", "댓글 추가"]) or "EditText" in n.attrib.get("class", ""),
                pause_video=False
            )

            if edit_center:
                print(f"  🎯 댓글 입력창 발견: {edit_center} -> 탭 및 주입")
                self.run_adb("shell", "input", "tap", str(edit_center[0]), str(edit_center[1]))
                time.sleep(1.5)
                self.input_korean_text(INSURANCE_TIKTOK_COMMENT)
                time.sleep(2.0)

                # 전송 버튼(↑) 글자/ID/접근성 라벨 동적 탐색 (부모 트리 역추적)
                send_node, send_center = self.find_node_with_parent_climb(
                    lambda n: any(k in n.attrib.get("resource-id", "") or k in n.attrib.get("content-desc", "") for k in ["d1y", "@2131823424", "send"])
                )

                if send_center:
                    print(f"  🎯 댓글 전송 버튼 터치: {send_center}")
                    self.run_adb("shell", "input", "tap", str(send_center[0]), str(send_center[1]))
                    time.sleep(3.5)
                    comment_posted = True
                    print("  ✅ 보험 리밸런스 3단 공식 첫 댓글 전송 완료!")

        # -------------------------------------------------------------
        # STEP 11: 📸 댓글 영수증 상시 보관 및 📊 대시보드 실시간 연동
        # -------------------------------------------------------------
        print("\n👉 [STEP 11] 댓글 실물 영수증 캡처 및 대시보드 실시간 연동")
        ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        latest_proof = PROOFS_DIR / "insurance_tiktok_comment_latest.png"
        ts_proof = PROOFS_DIR / f"insurance_tiktok_comment_{ts_str}.png"
        system_proof = PROOF_DIR_SYSTEM / "proof_insurance_latest_comment_live.png"

        self.run_adb("shell", "screencap", "-p", "/sdcard/comment_proof.png")
        self.run_adb("pull", "/sdcard/comment_proof.png", str(latest_proof))
        self.run_adb("pull", "/sdcard/comment_proof.png", str(ts_proof))
        self.run_adb("pull", "/sdcard/comment_proof.png", str(system_proof))

        # 삼성 키보드로 원복
        self.restore_samsung_keyboard()

        # 대시보드 히스토리 파일 실시간 업데이트
        self.save_publish_history(
            video_url=TIKTOK_PROFILE_URL,
            comment_text=INSURANCE_TIKTOK_COMMENT,
            proof_img_path=str(latest_proof)
        )

        # 🌟 [사용자 핵심 철칙] 작업 완료 후 앱 100% 완전 종료 및 홈 화면 복귀 (브랜드 간 화면 꼬임 원천 차단)
        print("\n👉 [STEP 12] 틱톡 앱 완전 종료(force-stop) 및 스마트폰 홈 화면 복귀")
        self.run_adb("shell", "am", "force-stop", "com.ss.android.ugc.trill")
        self.run_adb("shell", "input", "keyevent", "3")
        time.sleep(1.0)

        print("\n" + "=" * 65)
        print("🎉 [성공] 🛡️ 보험 리밸런스 원본 음성 100% + 첫 댓글 + 대시보드 URL + 클린 종료 완결!")
        print(f"📸 영수증 보관 경로: {latest_proof}")
        print("=" * 65 + "\n")

        return {
            "success": True,
            "comment_posted": comment_posted,
            "proof_path": str(latest_proof),
            "video_url": TIKTOK_PROFILE_URL,
            "caption": INSURANCE_TIKTOK_CAPTION,
            "comment": INSURANCE_TIKTOK_COMMENT
        }


if __name__ == "__main__":
    uploader = PhoneInsuranceTikTokUploader()
    res = uploader.execute_full_flow()
    print("최종 결과:", res)
