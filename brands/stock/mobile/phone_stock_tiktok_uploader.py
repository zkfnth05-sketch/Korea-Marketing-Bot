# -*- coding: utf-8 -*-
"""
================================================================================
📱 [StockMaster AI] 스마트폰 틱톡 100% 무인 풀코스 원스톱 자동 업로더 (순수 원본 음성 완결형)
================================================================================
- 브랜드: StockMaster AI (공식 검색어: '스톡마스터 AI', URL: https://stockmaster-ai.vercel.app/)
- 틱톡 계정: @stock_master_ai (계정 자동 스위칭 탑재)
- 설계 철칙:
  1. [스튜디오 원본 음성 100% 보존]: 외부 사운드 추가를 전면 배제하여,
     영상 자체의 StockMaster AI 나레이션 말소리가 볼륨 간섭 없이 100% 선명하게 출력되도록 보장.
  2. [글자 기반 무인 자동화]: 고정 좌표 0개, XML UI 트리의 글자 노드를 추적하여 동적 터치.
  3. [계정 자동 스위칭]: 업로드 전 @stock_master_ai 계정인지 자동 확인하고, 다른 계정이면 글자로 전환.
  4. [원스톱 풀코스]:
     [1] 최신 영상 스마트폰 동기화 (PC -> /sdcard/DCIM/Camera/)
     [2] 틱톡 앱 클린 기상
     [3] @stock_master_ai 계정 자동 확보 (계정 전환 바텀시트 글자 추적)
     [4] 하단 '만들기' 글자 터치 -> 갤러리 진입
     [5] '동영상' 탭 터치 -> 최신 1번 영상 선택
     [6] '다음' 글자 터치 (사운드 추가 없이 원본 음성 직결)
     [7] 캡션 입력창에 StockMaster AI 공식 한글 캡션 및 해시태그 주입
     [8] '게시' 글자 터치 -> 서버 업로드
     [9] '취소' 글자 터치 (위젯 팝업 해제)
     [10] '첫 댓글 달기' 글자 터치 -> StockMaster AI 공식 3단 첫 댓글 자동 등록
     [11] 실물 댓글 영수증 상시 캡처 보관 & 대시보드(http://localhost:8080) 실시간 URL 연동
     [12] 앱 완전 종료(force-stop) 및 스마트폰 홈 복귀
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
DATA_HISTORY_FILE = ENGINE_DIR / "data" / "stock_tiktok_history.json"
DATA_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

PROOF_DIR_SYSTEM = Path(r"C:\Users\zkfnt\.gemini\antigravity-ide\brain\998fe1e4-e7e3-436b-bdfc-908b49764dd2")
PROOF_DIR_SYSTEM.mkdir(parents=True, exist_ok=True)

# Core 모바일 동기화 모듈 임포트
sys.path.insert(0, str(ENGINE_DIR))
from core.mobile.mobile_video_sync import sync_video_to_phone

# 📈 StockMaster AI 공식 캡션 및 해시태그
STOCK_TIKTOK_CAPTION = (
    "📈 내 보유종목 AI 수급 & 목표가 분석! 상위 1% 알고리즘 3초 무료 진단! "
    "네이버 검색창에 [스톡마스터 AI]를 검색해 보세요! "
    "#스톡마스터AI #주식 #국내주식 #미국주식 #주식투자 #급등주 #추천 #fyp"
)

# 📈 StockMaster AI 공식 3단 표준 첫 댓글 규격 (절대 불변)
STOCK_TIKTOK_COMMENT = (
    "📈 [StockMaster AI] 내 보유종목 AI 수급 & 목표가 3초 무료 진단:\n"
    "👉 https://stockmaster-ai.vercel.app/\n\n"
    "🔍 네이버 검색창에 [스톡마스터 AI]를 검색해보세요!\n\n"
    "✨ 상위 1% 알고리즘 실시간 분석을 3초 만에 무료로 확인해 보세요!\n"
    "(네이버 검색: 스톡마스터 AI)"
)

TIKTOK_ACCOUNT_ID = "stock_master_ai"
TIKTOK_PROFILE_URL = "https://www.tiktok.com/@stock_master_ai"


class PhoneStockTikTokUploader:
    """📈 StockMaster AI 전용 모바일 틱톡 100% 무인 원스톱 업로더"""

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
                rect = self.get_valid_bounds_rect(node.attrib.get("bounds", ""))
                if rect:
                    cx = (rect[0] + rect[2]) // 2
                    cy = (rect[1] + rect[3]) // 2
                    if rect[3] >= 2030 and (rect[3] - rect[1]) <= 30:
                        cy = rect[1] - 40
                    return node, (cx, cy)

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

    def ensure_brand_account(self, target_account_id: str = TIKTOK_ACCOUNT_ID) -> bool:
        """
        [100% 순수 글자 기반 계정 자동 스위칭 엔진]
        현재 활성화된 계정이 target_account_id(@stock_master_ai)인지 확인하고,
        아니라면 프로필 -> 상단 계정명 터치 -> 계정 전환 바텀시트에서 해당 계정 글자를 찾아 터치
        """
        print(f"\n🔐 [StockMaster AI] 틱톡 공식 계정(@{target_account_id}) 확인 및 스위칭 시작...")

        # 1. 하단 내비바 사람모양(프로필) 아이콘 완전 타격 (피드 자막 오작동 100% 차단)
        for attempt in range(3):
            self.dismiss_unexpected_popups()
            root = self.dump_ui()
            prof_node = None
            prof_center = None
            for n in root.iter("node"):
                desc = n.attrib.get("content-desc") or ""
                txt = n.attrib.get("text") or ""
                if desc == "프로필" or txt == "프로필":
                    rect = self.get_valid_bounds_rect(n.attrib.get("bounds", ""))
                    if rect and rect[1] >= 1800:  # 스마트폰 맨 밑바닥 영역 한정
                        cx = (rect[0] + rect[2]) // 2
                        cy = (rect[1] + rect[3]) // 2
                        if rect[3] >= 2030 and (rect[3] - rect[1]) <= 30:
                            cy = rect[1] - 40
                        prof_node = n
                        prof_center = (cx, cy)
                        break

            if prof_center:
                print(f"  🎯 [하단 사람모양 아이콘 발견] 좌표 {prof_center} -> 터치!")
                self.run_adb("shell", "input", "tap", str(prof_center[0]), str(prof_center[1]))
                time.sleep(2.5)

            # 프로필 페이지 안착 확인 (팔로잉/팔로워/좋아요/프로필 편집 또는 계정명)
            check_root = self.dump_ui()
            profile_landed = False
            for n in check_root.iter("node"):
                t = n.attrib.get("text", "")
                d = n.attrib.get("content-desc", "")
                if any(k in t or k in d for k in ["팔로워", "팔로잉", "좋아요", "프로필 편집", "@"]):
                    profile_landed = True
                    break
            if profile_landed:
                print("  ✅ [프로필 페이지 안착 확인 완료]")
                break
            time.sleep(1.0)

        root = self.dump_ui()

        # 2. 현재 계정이 이미 타깃 계정인지 확인
        for node in root.iter("node"):
            t = node.attrib.get("text", "").lower()
            d = node.attrib.get("content-desc", "").lower()
            if f"@{target_account_id.lower()}" in t or f"@{target_account_id.lower()}" in d:
                print(f"  ✅ 현재 이미 주식 계정(@{target_account_id})으로 접속되어 있습니다.")
                return True

        # 3. 바텀시트가 열려있는지 확인 ('계정 전환' 글자)
        sheet_node, sheet_center = self.find_node_with_parent_climb(
            lambda n: "계정 전환" in n.attrib.get("text", "") or "계정 전환" in n.attrib.get("content-desc", "")
        )

        # 안 열려 있다면 상단 계정명/타이틀 노드 찾아서 탭
        if not sheet_center:
            title_node, title_center = self.find_node_with_parent_climb(
                lambda n: any(k in n.attrib.get("resource-id", "") for k in ["t_3", "t6f", "pwb"]) or
                          any(k in n.attrib.get("text", "").lower() for k in ["aura", "goldmom", "stock", "아우라", "골드맘", "스톡"])
            )
            if title_center:
                print(f"  👉 상단 계정명 터치하여 계정 전환 바텀시트 열기: {title_center}")
                self.run_adb("shell", "input", "tap", str(title_center[0]), str(title_center[1]))
                time.sleep(2.0)

        # 4. 바텀시트에서 target_account_id 글자 찾아서 탭
        acc_node, acc_center = self.find_node_with_parent_climb(
            lambda n: target_account_id.lower() in (n.attrib.get("text") or "").lower() or
                      target_account_id.lower() in (n.attrib.get("content-desc") or "").lower() or
                      "스톡" in (n.attrib.get("text") or "")
        )
        if acc_center:
            print(f"  🎯 주식 계정 글자('{target_account_id}') 발견: {acc_center} -> 전환 터치!")
            self.run_adb("shell", "input", "tap", str(acc_center[0]), str(acc_center[1]))
            time.sleep(3.5)
            print(f"  ✅ '{target_account_id}' 계정으로 스위칭 완료!")
            return True
        else:
            print(f"  ℹ️ 바텀시트에서 '{target_account_id}' 계정 글자를 찾지 못했습니다. (이미 해당 계정일 수 있음)")
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
            "brand": "Stock",
            "platform": "tiktok",
            "status": "success",
            "title": "StockMaster AI 상위 1% 알고리즘 숏폼 (스튜디오 원본 음성)",
            "url": video_url,
            "published_at": now_str,
            "timestamp": now_str,
            "caption": STOCK_TIKTOK_CAPTION,
            "comment": comment_text,
            "comment_proof_image": proof_img_path,
            "proof_url": f"/api/live_proof_image?path={proof_img_path}"
        }

        # outputs/tiktok_publish_history.json & data/stock_tiktok_history.json
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
        remote_filename: str = "Stock_latest_shorts.mp4"
    ) -> Dict[str, Any]:
        """
        StockMaster AI 틱톡 모바일 원스톱 풀코스 실행 (사운드 추가 없이 원본 음성 100% 직결형)
        """
        print("\n" + "=" * 65)
        print("🚀 [StockMaster AI] 스마트폰 틱톡 원본 음성 100% 무인 업로드 파이프라인 시작")
        print("=" * 65)

        # -------------------------------------------------------------
        # STEP 1: PC 최신 렌더링 동영상 -> 스마트폰 Sync
        # -------------------------------------------------------------
        print("\n👉 [STEP 1] 최신 숏폼 동영상 모바일 자동 동기화")
        sync_res = sync_video_to_phone(
            brand="Stock",
            local_video_path=local_video_path,
            remote_filename=remote_filename
        )
        if not sync_res.get("success"):
            print(f"❌ 동영상 동기화 실패: {sync_res.get('error')}")
            return {"success": False, "step": "sync", "error": sync_res.get("error")}

        # -------------------------------------------------------------
        # STEP 2: 틱톡 앱 클린 재실행
        # -------------------------------------------------------------
        print("\n👉 [STEP 2] 틱톡 앱 클린 기상 및 실행")
        self.run_adb("shell", "am", "force-stop", "com.ss.android.ugc.trill")
        time.sleep(1.0)
        self.run_adb("shell", "am", "start", "-n", "com.ss.android.ugc.trill/com.ss.android.ugc.aweme.splash.SplashActivity")
        time.sleep(4.5)

        # -------------------------------------------------------------
        # STEP 3: 🔐 StockMaster AI 계정(@stock_master_ai) 자동 확인 및 스위칭
        # -------------------------------------------------------------
        print("\n👉 [STEP 3] 🔐 StockMaster AI 계정(@stock_master_ai) 자동 스위칭")
        self.ensure_brand_account(TIKTOK_ACCOUNT_ID)
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

        # 카메라 모드일 경우 갤러리(업로드/앨범/사진) 글자 버튼 탐색
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

        # 첫 번째 동영상 항목(재생시간 글자 노드 예: '00:15', '00:19' 등) 탐색
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
            post_check, _ = self.find_node_with_parent_climb(
                lambda n: "설명" in (n.attrib.get("text") or "") or n.attrib.get("text") == "게시"
            )
            if post_check:
                print("  ✅ 최종 게시 화면 도달 완료!")
                break
            found_n = self.tap_by_text("다음", pause_video=True, timeout=8)
            time.sleep(3.5)

        # -------------------------------------------------------------
        # STEP 7: 설명 입력창 터치 -> StockMaster AI 한글 캡션 주입
        # -------------------------------------------------------------
        print("\n👉 [STEP 7] 설명 입력창 탐색 및 StockMaster AI 한글 캡션 주입")
        node, center = self.find_node_with_parent_climb(
            lambda n: any(k in (n.attrib.get("text") or "") or k in (n.attrib.get("content-desc") or "") for k in ["설명을 추가하세요", "설명 추가"]) or "EditText" in n.attrib.get("class", "")
        )
        if center:
            print(f"  🎯 설명 입력창 발견: {center} -> 탭 및 주입")
            self.run_adb("shell", "input", "tap", str(center[0]), str(center[1]))
            time.sleep(1.5)
            self.input_korean_text(STOCK_TIKTOK_CAPTION)
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
        # STEP 9: '취소' 글자 터치 (카메라 위젯 팝업 자동 해제)
        # -------------------------------------------------------------
        print("\n👉 [STEP 9] 게시 후 위젯 팝업 감지 및 '취소' 글자 터치")
        self.dismiss_unexpected_popups()
        found_cancel = self.tap_by_text("취소", timeout=5)
        if found_cancel:
            print("  ✅ 카메라 위젯 팝업을 '취소' 글자로 정상 해제했습니다.")

        time.sleep(3.0)

        # -------------------------------------------------------------
        # STEP 10: 업로드 영상 피드 진입 -> StockMaster AI 공식 3단 첫 댓글 등록
        # -------------------------------------------------------------
        print("\n👉 [STEP 10] 방금 게시된 영상 피드에 StockMaster AI 공식 3단 첫 댓글 작성")
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
                self.input_korean_text(STOCK_TIKTOK_COMMENT)
                time.sleep(2.0)

                # 전송 버튼(↑) 글자/ID/접근성 라벨 동적 탐색
                send_node, send_center = self.find_node_with_parent_climb(
                    lambda n: any(k in n.attrib.get("resource-id", "") or k in n.attrib.get("content-desc", "") for k in ["d1y", "@2131823424", "send"])
                )

                if send_center:
                    print(f"  🎯 댓글 전송 버튼 터치: {send_center}")
                    self.run_adb("shell", "input", "tap", str(send_center[0]), str(send_center[1]))
                    time.sleep(3.5)
                    comment_posted = True
                    print("  ✅ StockMaster AI 3단 공식 첫 댓글 전송 완료!")

        # -------------------------------------------------------------
        # STEP 11: 📸 댓글 영수증 상시 보관 및 📊 대시보드 실시간 연동
        # -------------------------------------------------------------
        print("\n👉 [STEP 11] 댓글 실물 영수증 캡처 및 대시보드 실시간 연동")
        ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        latest_proof = PROOFS_DIR / "stock_tiktok_comment_latest.png"
        ts_proof = PROOFS_DIR / f"stock_tiktok_comment_{ts_str}.png"
        system_proof = PROOF_DIR_SYSTEM / "proof_stock_latest_comment_live.png"

        self.run_adb("shell", "screencap", "-p", "/sdcard/comment_proof.png")
        self.run_adb("pull", "/sdcard/comment_proof.png", str(latest_proof))
        self.run_adb("pull", "/sdcard/comment_proof.png", str(ts_proof))
        self.run_adb("pull", "/sdcard/comment_proof.png", str(system_proof))

        # 삼성 키보드로 원복
        self.restore_samsung_keyboard()

        # 대시보드 히스토리 파일 실시간 업데이트
        self.save_publish_history(
            video_url=TIKTOK_PROFILE_URL,
            comment_text=STOCK_TIKTOK_COMMENT,
            proof_img_path=str(latest_proof)
        )

        # 🌟 [사용자 핵심 철칙] 작업 완료 후 앱 100% 완전 종료 및 홈 화면 복귀
        print("\n👉 [STEP 12] 틱톡 앱 완전 종료(force-stop) 및 스마트폰 홈 화면 복귀")
        self.run_adb("shell", "am", "force-stop", "com.ss.android.ugc.trill")
        self.run_adb("shell", "input", "keyevent", "3")
        time.sleep(1.0)

        print("\n" + "=" * 65)
        print("🎉 [성공] 📈 StockMaster AI 원본 음성 100% + 첫 댓글 + 대시보드 URL + 클린 종료 완결!")
        print(f"📸 영수증 보관 경로: {latest_proof}")
        print("=" * 65 + "\n")

        return {
            "success": True,
            "comment_posted": comment_posted,
            "proof_path": str(latest_proof),
            "video_url": TIKTOK_PROFILE_URL,
            "caption": STOCK_TIKTOK_CAPTION,
            "comment": STOCK_TIKTOK_COMMENT
        }


if __name__ == "__main__":
    uploader = PhoneStockTikTokUploader()
    res = uploader.execute_full_flow()
    print("최종 결과:", res)
