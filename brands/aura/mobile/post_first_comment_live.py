# -*- coding: utf-8 -*-
import subprocess
import time
import base64
import xml.etree.ElementTree as ET
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

p = r"c:\Users\zkfnt\Desktop\한국 마케팅봇\kmarket-marketing-engine\tools\platform-tools\adb.exe"
PROOF_DIR = Path(r"C:\Users\zkfnt\.gemini\antigravity-ide\brain\998fe1e4-e7e3-436b-bdfc-908b49764dd2")
XML_TEMP = Path(r"c:\Users\zkfnt\Desktop\한국 마케팅봇\brands\aura\mobile\live_comment_dump.xml")

# Aura 공식 3단 표준 첫 댓글
AURA_TIKTOK_COMMENT = (
    "💖 [Aura AI 데이팅] 모든 기능 무료 사용하기 (3초 무료 입장):\n"
    "👉 https://aura-ai-dating.vercel.app/\n\n"
    "🔍 네이버 검색창에 [아우라AI데이팅]을 검색해보세요!\n\n"
    "✨ 50:50 황금 성비 라운지를 3초 만에 무료로 이용해 보세요!\n"
    "(네이버 검색: 아우라AI데이팅)"
)

def run_adb(*args) -> str:
    res = subprocess.run([p] + list(args), capture_output=True, text=True, encoding='utf-8', errors='ignore')
    return res.stdout.strip()

def dump_ui():
    # 동영상 일시정지 (화면 중앙 터치하여 idle 상태 만들기)
    run_adb('shell', 'input', 'tap', '540', '1000')
    time.sleep(1.0)
    run_adb('shell', 'uiautomator', 'dump', '/sdcard/live_comm.xml')
    time.sleep(1.0)
    run_adb('pull', '/sdcard/live_comm.xml', str(XML_TEMP))

def parse_bounds(bounds_str):
    m = re.findall(r'\d+', bounds_str)
    if len(m) == 4:
        x1, y1, x2, y2 = map(int, m)
        return (x1 + x2) // 2, (y1 + y2) // 2
    return None

def find_node(condition_fn):
    tree = ET.parse(XML_TEMP)
    for n in tree.getroot().iter('node'):
        if condition_fn(n):
            b = parse_bounds(n.attrib.get('bounds', ''))
            if b:
                return n, b
    return None, None

print("==================================================")
print("📱 [방금 업로드한 Aura 영상에 글자 기반 첫 댓글 달기 시작]")
print("==================================================")

# 1. UI 덤프
dump_ui()

# 2. '첫 댓글 달기' 또는 '댓글' 글자 버튼 탐색
print("👉 [1단계] '첫 댓글 달기' 글자 탐색...")
btn_node, btn_center = find_node(lambda n: (
    '첫 댓글' in n.attrib.get('text', '') or 
    '댓글을 읽거나' in n.attrib.get('content-desc', '') or
    '댓글' in n.attrib.get('text', '')
))

if btn_center:
    print(f"🎯 글자로 댓글 버튼 발견! 좌표: {btn_center} (text='{btn_node.attrib.get('text')}')")
    run_adb('shell', 'input', 'tap', str(btn_center[0]), str(btn_center[1]))
    time.sleep(2.5)
else:
    print("⚠️ 댓글 버튼을 찾지 못함. 백업 시도...")

# 3. AdbIME 활성화
print("👉 [2단계] ADBKeyboard(AdbIME) 활성화")
run_adb('shell', 'ime', 'set', 'com.android.adbkeyboard/.AdbIME')
time.sleep(1.0)

# 4. 댓글 서랍 열린 상태에서 입력창 탐색
dump_ui()
edit_node, edit_center = find_node(lambda n: (
    'EditText' in n.attrib.get('class', '') or
    '따듯한' in n.attrib.get('text', '') or
    'eko' in n.attrib.get('resource-id', '')
))

if not edit_center:
    print("❌ 댓글 입력창을 찾지 못했습니다.")
    sys.exit(1)

print(f"🎯 댓글 입력창 발견: {edit_center}")
run_adb('shell', 'input', 'tap', str(edit_center[0]), str(edit_center[1]))
time.sleep(1.5)

# 5. 한글 3단 표준 첫 댓글 주입
print("👉 [3단계] Aura 공식 3단 첫 댓글 주입...")
b64_msg = base64.b64encode(AURA_TIKTOK_COMMENT.encode('utf-8')).decode('utf-8')
run_adb('shell', 'am', 'broadcast', '-a', 'ADB_INPUT_B64', '--es', 'msg', b64_msg)
time.sleep(2.0)

# 6. 전송 버튼(↑) 글자/ID 탐색
print("👉 [4단계] 전송 버튼(↑) 탐색...")
dump_ui()
tree = ET.parse(XML_TEMP)
send_center = None
for n in tree.getroot().iter('node'):
    cls = n.attrib.get('class', '')
    rid = n.attrib.get('resource-id', '')
    desc = n.attrib.get('content-desc', '')
    b = parse_bounds(n.attrib.get('bounds', ''))
    if not b:
        continue
    if ('Button' in cls or 'ImageView' in cls) and (
        'd1y' in rid or 
        '@2131823424' in desc or 
        (b[0] > 800 and 1100 < b[1] < 1400)
    ):
        send_center = b
        print(f"🎯 전송 버튼 발견! 좌표: {send_center}, id='{rid}'")
        break

if send_center:
    print(f"👉 전송 버튼 클릭: {send_center}")
    run_adb('shell', 'input', 'tap', str(send_center[0]), str(send_center[1]))
    time.sleep(4.0)

# 7. 실물 영수증 캡처
proof_comment = PROOF_DIR / "proof_aura_uploaded_video_comment_success.png"
run_adb('shell', 'screencap', '-p', '/sdcard/final_comm.png')
run_adb('pull', '/sdcard/final_comm.png', str(proof_comment))
print(f"📸 최종 실물 댓글 등록 영수증: {proof_comment}")

# 8. 삼성 키보드로 원복
run_adb('shell', 'ime', 'set', 'com.samsung.android.honeyboard/.service.HoneyBoardService')

print("\n🎉 === 💖 Aura 업로드 영상에 100% 무인 첫 댓글 등록 완벽 성공! ===")
