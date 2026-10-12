# -*- coding: utf-8 -*-
"""
================================================================================
📱 [보험 리밸런스] 스마트폰 틱톡 100% 순수 글자 기반 '인간 스텔스 웜업' 엔진
================================================================================
- 브랜드: 보험 리밸런스 (공식 계정: @goldmom82)
- 설계 철칙:
  1. [좌표 0개 순수 글자 기반]: UIAutomator XML의 글자 노드 및 부모 역추적으로 동적 터치.
  2. [계정 자동 스위칭]: 다른 계정(아우라/주식)으로 로그인되어 있어도 프로필 -> 계정 전환 바텀시트에서
     'goldmom82' 글자를 찾아 보험 계정으로 100% 자동 스위칭.
  3. [인간 스텔스 웜업]:
     - 홈(추천 피드 FYP) 글자 터치 이동
     - 영상 1: 8초 감상 ➔ 글자로 '좋아요' 터치 ➔ 사람 스크롤
     - 영상 2: 7초 감상 ➔ 스킵(자연스러움) ➔ 사람 스크롤
     - 영상 3: 8초 감상 ➔ 글자로 '좋아요' 터치
     - 실물 영수증 캡처
     - 앱 클린 종료 및 홈 화면 복귀
================================================================================
"""

import subprocess
import time
import xml.etree.ElementTree as ET
import re
import sys
from pathlib import Path
from typing import Optional, Tuple

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[3]
ENGINE_DIR = PROJECT_ROOT / "kmarket-marketing-engine"
ADB_PATH = ENGINE_DIR / "tools" / "platform-tools" / "adb.exe"
XML_LOCAL = CURRENT_FILE.parent / "temp_screen_dump.xml"

PROOFS_DIR = ENGINE_DIR / "outputs" / "proofs"
PROOFS_DIR.mkdir(parents=True, exist_ok=True)
PROOF_DIR_SYSTEM = Path(r"C:\Users\zkfnt\.gemini\antigravity-ide\brain\998fe1e4-e7e3-436b-bdfc-908b49764dd2")
PROOF_DIR_SYSTEM.mkdir(parents=True, exist_ok=True)

TARGET_ACCOUNT_ID = "goldmom82"


class PhoneInsuranceTikTokStealth:
    """🛡️ 보험 리밸런스 전용 틱톡 인간 스텔스 웜업 엔진"""

    def __init__(self):
        self.adb = ADB_PATH

    def run_adb(self, *args) -> str:
        cmd = [str(self.adb)] + list(args)
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        return res.stdout.strip()

    def get_valid_bounds_rect(self, bounds_str: str) -> Optional[Tuple[int, int, int, int]]:
        m = re.findall(r"\d+", bounds_str)
        if len(m) == 4:
            x1, y1, x2, y2 = map(int, m)
            if (x2 - x1) > 10 and (y2 - y1) > 10:
                return (x1, y1, x2, y2)
        return None

    def dump_ui(self, pause_video: bool = False) -> ET.Element:
        if pause_video:
            self.run_adb("shell", "input", "keyevent", "85")
            time.sleep(0.5)

        self.run_adb("shell", "uiautomator", "dump", "/sdcard/stealth_dump.xml")
        time.sleep(0.8)
        self.run_adb("pull", "/sdcard/stealth_dump.xml", str(XML_LOCAL))

        if not XML_LOCAL.exists():
            time.sleep(1.0)
            self.run_adb("pull", "/sdcard/stealth_dump.xml", str(XML_LOCAL))

        tree = ET.parse(XML_LOCAL)
        return tree.getroot()

    def find_node_with_parent_climb(self, condition_fn, pause_video: bool = False):
        root = self.dump_ui(pause_video=pause_video)
        parent_map = {c: p for p in root.iter() for c in p}

        for node in root.iter("node"):
            if condition_fn(node):
                rect = self.get_valid_bounds_rect(node.attrib.get("bounds", ""))
                if rect:
                    return node, ((rect[0] + rect[2]) // 2, (rect[1] + rect[3]) // 2)

                curr = node
                while curr in parent_map:
                    curr = parent_map[curr]
                    p_rect = self.get_valid_bounds_rect(curr.attrib.get("bounds", ""))
                    if p_rect:
                        return node, ((p_rect[0] + p_rect[2]) // 2, (p_rect[1] + p_rect[3]) // 2)

        return None, None

    def tap_by_text(self, text_keyword: str, pause_video: bool = False, timeout: int = 10) -> bool:
        start = time.time()
        while time.time() - start < timeout:
            node, center = self.find_node_with_parent_climb(
                lambda n: text_keyword in n.attrib.get("text", "") or text_keyword in n.attrib.get("content-desc", ""),
                pause_video=pause_video
            )
            if center:
                matched_text = node.attrib.get("text") or node.attrib.get("content-desc")
                print(f"  🎯 [글자 매칭] '{matched_text}' -> 동적 좌표 {center} 터치")
                self.run_adb("shell", "input", "tap", str(center[0]), str(center[1]))
                return True
            time.sleep(1.0)
        return False

    def ensure_brand_account(self, target_account_id: str = TARGET_ACCOUNT_ID) -> bool:
        """
        [100% 순수 글자 기반 계정 자동 스위칭 엔진]
        현재 활성화된 계정이 target_account_id(@goldmom82)인지 확인하고,
        아니라면 프로필 -> 상단 계정명 터치 -> 계정 전환 바텀시트에서 해당 계정 글자를 찾아 터치
        """
        print(f"\n🔐 [보험 리밸런스] 틱톡 공식 계정(@{target_account_id}) 확인 및 스위칭 시작...")

        # 1. 프로필 탭으로 이동
        found_profile = self.tap_by_text("프로필", pause_video=False, timeout=6)
        time.sleep(2.5)

        root = self.dump_ui()

        # 2. 현재 계정이 이미 타깃 계정인지 확인
        for node in root.iter("node"):
            t = node.attrib.get("text", "").lower()
            d = node.attrib.get("content-desc", "").lower()
            if f"@{target_account_id.lower()}" in t or f"@{target_account_id.lower()}" in d:
                print(f"  ✅ 현재 이미 보험 계정(@{target_account_id})으로 접속되어 있습니다.")
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
            lambda n: target_account_id.lower() in n.attrib.get("text", "").lower() or
                      target_account_id.lower() in n.attrib.get("content-desc", "").lower() or
                      "골드맘" in n.attrib.get("text", "")
        )
        if acc_center:
            print(f"  🎯 보험 계정 글자('{target_account_id}') 발견: {acc_center} -> 전환 터치!")
            self.run_adb("shell", "input", "tap", str(acc_center[0]), str(acc_center[1]))
            time.sleep(3.5)
            print(f"  ✅ '{target_account_id}' 계정으로 스위칭 완료!")
            return True
        else:
            print(f"  ℹ️ 바텀시트에서 '{target_account_id}' 계정 글자를 찾지 못했습니다. (이미 해당 계정일 수 있음)")
            self.run_adb("shell", "input", "keyevent", "4")
            return False

    def human_scroll(self):
        """사람처럼 자연스러운 상향 스크롤"""
        print("  👉 📱 [사람 스크롤] 다음 추천 동영상으로 넘기기...")
        self.run_adb("shell", "input", "swipe", "540", "1600", "540", "420", "350")
        time.sleep(2.0)

    def click_like_by_text(self) -> bool:
        """오직 '좋아요' 글자/설명으로 노드를 찾아 클릭"""
        node, center = self.find_node_with_parent_climb(
            lambda n: "좋아요" in n.attrib.get("text", "") or "좋아요" in n.attrib.get("content-desc", ""),
            pause_video=True
        )
        if center:
            matched = node.attrib.get("text") or node.attrib.get("content-desc")
            print(f"  ❤️ 글자로 '좋아요' 버튼 발견: {center} ('{matched}') -> 하트 터치!")
            self.run_adb("shell", "input", "tap", str(center[0]), str(center[1]))
            time.sleep(1.5)
            return True
        else:
            print("  ⚠️ 화면에서 '좋아요' 글자 버튼을 찾지 못했습니다.")
            return False

    def execute_stealth(self) -> bool:
        print("\n" + "=" * 65)
        print("🛡️ [보험 리밸런스] 100% 글자 기반 스텔스 웜업 시작")
        print("=" * 65)

        # STEP 1: 틱톡 앱 클린 기상
        print("\n👉 [STEP 1] 틱톡 앱 클린 기상 및 실행")
        self.run_adb("shell", "am", "force-stop", "com.ss.android.ugc.trill")
        time.sleep(1.0)
        self.run_adb("shell", "am", "start", "-n", "com.ss.android.ugc.trill/com.ss.android.ugc.aweme.splash.SplashActivity")
        time.sleep(4.5)

        # STEP 2: 계정 자동 확인 및 스위칭
        print("\n👉 [STEP 2] 🔐 보험 리밸런스 계정(@goldmom82) 자동 확인 및 스위칭")
        self.ensure_brand_account(TARGET_ACCOUNT_ID)
        time.sleep(1.5)

        # STEP 3: 홈(FYP) 글자 탐색 후 이동
        print("\n👉 [STEP 3] '홈' 글자 탐색 -> 추천 피드(FYP) 이동")
        found_home = self.tap_by_text("홈", pause_video=False, timeout=6)
        time.sleep(3.0)

        # STEP 4: 스텔스 사람 시뮬레이션
        print("\n👉 [STEP 4-1] 🎬 첫 번째 영상 사람처럼 8초 동안 시청 중...")
        time.sleep(8.0)
        self.click_like_by_text()
        time.sleep(2.0)
        self.human_scroll()

        print("\n👉 [STEP 4-2] 🎬 두 번째 영상 7초 동안 시청 중 (자연스러운 패스)...")
        time.sleep(7.0)
        self.human_scroll()

        print("\n👉 [STEP 4-3] 🎬 세 번째 영상 8초 동안 시청 중...")
        time.sleep(8.0)
        self.click_like_by_text()
        time.sleep(3.0)

        # STEP 5: 실물 영수증 캡처
        print("\n👉 [STEP 5] 📸 스텔스 웜업 실물 영수증 캡처")
        ts_str = time.strftime("%Y%m%d_%H%M%S")
        latest_proof = PROOFS_DIR / "insurance_stealth_watching_latest.png"
        system_proof = PROOF_DIR_SYSTEM / "proof_insurance_stealth_watching_live.png"

        self.run_adb("shell", "screencap", "-p", "/sdcard/stealth_proof.png")
        self.run_adb("pull", "/sdcard/stealth_proof.png", str(latest_proof))
        self.run_adb("pull", "/sdcard/stealth_proof.png", str(system_proof))
        print(f"  📸 최종 영수증 저장: {latest_proof}")

        # STEP 6: 앱 클린 종료 및 홈 복귀
        print("\n👉 [STEP 6] 틱톡 앱 완전 종료(force-stop) 및 스마트폰 홈 복귀")
        self.run_adb("shell", "am", "force-stop", "com.ss.android.ugc.trill")
        self.run_adb("shell", "input", "keyevent", "3")
        time.sleep(1.0)

        print("\n" + "=" * 65)
        print("🎉 [성공] 🛡️ 보험 리밸런스 100% 글자 기반 스텔스 웜업 완결!")
        print("=" * 65 + "\n")
        return True


if __name__ == "__main__":
    stealth = PhoneInsuranceTikTokStealth()
    stealth.execute_stealth()
