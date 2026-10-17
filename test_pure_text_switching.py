import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import subprocess
import time
import re
import xml.etree.ElementTree as ET
from pathlib import Path

adb = Path(r"c:\Users\zkfnt\Desktop\한국 마케팅봇\kmarket-marketing-engine\tools\platform-tools\adb.exe")

def run(*args):
    res = subprocess.run([str(adb)] + list(args), capture_output=True, text=True, encoding="utf-8", errors="ignore")
    return res.stdout.strip()

def dump_ui():
    run("shell", "uiautomator", "dump", "/sdcard/pure_text_dump.xml")
    run("pull", "/sdcard/pure_text_dump.xml", r"c:\Users\zkfnt\Desktop\한국 마케팅봇\pure_text_dump.xml")
    return ET.parse(r"c:\Users\zkfnt\Desktop\한국 마케팅봇\pure_text_dump.xml").getroot()

def get_rect(bounds_str):
    m = re.findall(r"\[(\d+),(\d+)\]", bounds_str)
    if len(m) == 2:
        return [int(m[0][0]), int(m[0][1]), int(m[1][0]), int(m[1][1])]
    return None

def tap_pure_text(keyword, max_wait=8):
    """오직 화면 속 글자(text / content-desc)만 찾아서 중심을 터치 (좌표 하드코딩 0%)"""
    start = time.time()
    while time.time() - start < max_wait:
        root = dump_ui()
        for n in root.iter("node"):
            t = n.attrib.get("text", "")
            d = n.attrib.get("content-desc", "")
            if keyword in t or keyword in d:
                rect = get_rect(n.attrib.get("bounds", ""))
                if rect and rect[2] > rect[0] and rect[3] > rect[1]:
                    cx = (rect[0] + rect[2]) // 2
                    cy = (rect[1] + rect[3]) // 2
                    print(f"  🎯 [글자 터치 성공] 키워드: '{keyword}' (화면 글자: '{t or d}') -> 위치 ({cx}, {cy}) 터치!")
                    run("shell", "input", "tap", str(cx), str(cy))
                    return True
        time.sleep(1.0)
    print(f"  ❌ [글자 미발견] '{keyword}'")
    return False

print("=" * 60)
print("🔤 [100% 순수 글자 기반 계정 스위칭 검증]")
print("=" * 60)

# 1. 혹시 팝업이 있으면 글자로 닫기
print("\n[1단계] 팝업 소탕 (순수 글자 '나중에', '닫기', '저장')...")
for pop_text in ["나중에", "닫기", "저장", "다음에"]:
    tap_pure_text(pop_text, max_wait=1)

# 2. 하단 '프로필' 글자 터치
print("\n[2단계] 하단 글자 '프로필' 터치...")
tap_pure_text("프로필", max_wait=5)
time.sleep(2.0)

# 3. 혹시 프로필 진입 후 팝업이 뜨면 닫기
for pop_text in ["저장", "닫기", "나중에"]:
    tap_pure_text(pop_text, max_wait=1)

# 4. 상단 계정명 글자('아우라' or '골드맘' or '스톡') 터치하여 바텀시트 열기
print("\n[3단계] 상단 계정명 글자 터치하여 '계정 전환' 바텀시트 열기...")
# 현재 어떤 계정이든 상단에 계정명 글자가 있음
opened = False
for brand_word in ["아우라", "골드맘", "스톡", "@aura", "@goldmom", "@stock"]:
    if tap_pure_text(brand_word, max_wait=2):
        opened = True
        break

time.sleep(2.5)

# 5. 바텀시트가 열렸는지 영수증 캡처
run("shell", "screencap", "-p", "/sdcard/pure_text_sheet.png")
run("pull", "/sdcard/pure_text_sheet.png", r"c:\Users\zkfnt\Desktop\한국 마케팅봇\kmarket-marketing-engine\outputs\proofs\pure_text_sheet.png")
print("📸 순수 글자 터치 결과 화면 저장 완료 -> pure_text_sheet.png")

# 6. 바텀시트에서 원하는 글자('goldmom82') 터치
print("\n[4단계] 바텀시트에서 순수 글자 'goldmom82' 터치...")
switched = tap_pure_text("goldmom82", max_wait=5)
time.sleep(3.0)

# 7. 전환 후 다시 '프로필' 글자 터치
print("\n[5단계] 다시 글자 '프로필' 터치하여 안착...")
tap_pure_text("프로필", max_wait=5)
time.sleep(2.0)

# 8. 최종 화면 캡처
run("shell", "screencap", "-p", "/sdcard/pure_text_final.png")
run("pull", "/sdcard/pure_text_final.png", r"c:\Users\zkfnt\Desktop\한국 마케팅봇\kmarket-marketing-engine\outputs\proofs\pure_text_final.png")
print("📸 최종 스위칭 결과 화면 저장 완료 -> pure_text_final.png")
print("=" * 60)
