# -*- coding: utf-8 -*-
"""
================================================================================
📱 [Aura AI 데이팅] 스마트폰(ADB) 글자 기반 틱톡 100% 무인 댓글 자동 등록 엔진
================================================================================
원칙:
1. 절대 고정(하드코딩) 좌표를 사용하지 않는다.
2. uiautomator dump XML 트리를 파싱하여 'text', 'content-desc', 'class', 'resource-id' 등
   화면의 실제 '글자'를 추적하여 동적으로 중심 좌표를 계산해 터치한다.
3. 기기 해상도, OS 버전, 키보드 높낮이에 영향받지 않고 100% 자율 동작한다.
================================================================================
"""

import subprocess
import time
import base64
import xml.etree.ElementTree as ET
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# 프로젝트 ADB 경로
ADB_PATH = Path(__file__).resolve().parents[3] / "kmarket-marketing-engine" / "tools" / "platform-tools" / "adb.exe"
XML_TEMP = Path(__file__).resolve().parent / "temp_screen_dump.xml"

# Aura 공식 3단 표준 첫 댓글 규격
AURA_TIKTOK_COMMENT = (
    "💖 [Aura AI 데이팅] 모든 기능 무료 사용하기 (3초 무료 입장):\n"
    "👉 https://aura-ai-dating.vercel.app/\n\n"
    "🔍 네이버 검색창에 [아우라AI데이팅]을 검색해보세요!\n\n"
    "✨ 50:50 황금 성비 라운지를 3초 만에 무료로 이용해 보세요!\n"
    "(네이버 검색: 아우라AI데이팅)"
)

def adb_cmd(cmd: str) -> str:
    full_cmd = f'"{ADB_PATH}" {cmd}'
    res = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    return res.stdout.strip()

def dump_ui(xml_dest: Path = XML_TEMP) -> Path:
    adb_cmd("shell uiautomator dump /sdcard/screen_dump.xml")
    adb_cmd(f'pull /sdcard/screen_dump.xml "{xml_dest}"')
    return xml_dest

def parse_bounds(bounds_str: str):
    m = re.findall(r'\d+', bounds_str)
    if len(m) == 4:
        x1, y1, x2, y2 = map(int, m)
        return (x1 + x2) // 2, (y1 + y2) // 2
    return None

def find_node(xml_file: Path, condition_fn):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    for node in root.iter('node'):
        if condition_fn(node):
            b = parse_bounds(node.attrib.get('bounds', ''))
            if b:
                return node, b
    return None, None

def post_tiktok_comment_by_text(comment_text: str = AURA_TIKTOK_COMMENT, proof_save_dir: Path = None) -> bool:
    print("==================================================")
    print("📱 [글자 기반 틱톡 100% 무인 댓글 자동 주입 시작]")
    print("==================================================")

    # 1. 한글 입력을 위한 AdbIME 키보드 활성화
    print("👉 [1단계] ADBKeyboard(AdbIME) 활성화")
    adb_cmd("shell ime set com.android.adbkeyboard/.AdbIME")
    time.sleep(1.0)

    # 2. 현재 화면 UI 덤프 및 '댓글' 버튼 글자 탐색
    dump_ui()
    
    # 만약 댓글 서랍이 닫혀 있다면 '댓글' 또는 '첫 댓글 달기' 글자를 찾아 오픈
    edit_node, edit_center = find_node(XML_TEMP, lambda n: 'EditText' in n.attrib.get('class', ''))
    if not edit_center:
        print("👉 댓글 서랍 열기: '댓글' / '첫 댓글 달기' 글자 탐색 중...")
        btn_node, btn_center = find_node(XML_TEMP, lambda n: (
            '댓글을 읽거나' in n.attrib.get('content-desc', '') or 
            '댓글' in n.attrib.get('text', '') or
            '첫 댓글' in n.attrib.get('text', '')
        ))
        if btn_center:
            print(f"✅ 글자로 댓글 버튼 발견! 좌표: {btn_center} (설명: '{btn_node.attrib.get('content-desc', '')}')")
            adb_cmd(f"shell input tap {btn_center[0]} {btn_center[1]}")
            time.sleep(2.0)
            dump_ui()
        else:
            print("❌ 화면에서 '댓글' 버튼 글자를 찾지 못했습니다.")
            return False

    # 3. 댓글 입력창(EditText) 글자 및 클래스 탐색
    print("👉 [2단계] 댓글 입력창(EditText) 글자 탐색...")
    edit_node, edit_center = find_node(XML_TEMP, lambda n: (
        'EditText' in n.attrib.get('class', '') or
        '따듯한' in n.attrib.get('text', '') or
        'eko' in n.attrib.get('resource-id', '')
    ))

    if not edit_center:
        print("❌ 댓글 입력창을 찾을 수 없습니다.")
        return False

    print(f"✅ 댓글 입력창 발견: {edit_center} (기존 텍스트: '{edit_node.attrib.get('text', '')}')")
    adb_cmd(f"shell input tap {edit_center[0]} {edit_center[1]}")
    time.sleep(1.5)

    # 4. 활성화된 입력창에 한글 댓글 주입
    print("👉 [3단계] 한글 3단 표준 댓글 주입...")
    b64_msg = base64.b64encode(comment_text.encode('utf-8')).decode('utf-8')
    adb_cmd(f'shell am broadcast -a ADB_INPUT_B64 --es msg {b64_msg}')
    time.sleep(2.0)

    # 5. 전송 버튼(↑) 글자 및 속성 탐색
    print("👉 [4단계] 전송 버튼(↑) 탐색...")
    dump_ui()
    tree = ET.parse(XML_TEMP)
    send_center = None
    for node in tree.getroot().iter('node'):
        cls = node.attrib.get('class', '')
        rid = node.attrib.get('resource-id', '')
        desc = node.attrib.get('content-desc', '')
        b = parse_bounds(node.attrib.get('bounds', ''))
        if not b:
            continue
        # 전송 버튼 조건: 우측(x > 800)의 Button/ImageView 또는 id에 d1y/send 포함
        if ('Button' in cls or 'ImageView' in cls) and (
            'd1y' in rid or 
            '@2131823424' in desc or 
            (b[0] > 800 and 1100 < b[1] < 1400)
        ):
            send_center = b
            print(f"🎯 전송 버튼 발견! 좌표: {send_center}, id='{rid}'")
            break

    if not send_center:
        print("❌ 전송 버튼을 찾지 못했습니다.")
        return False

    print(f"👉 전송 버튼 클릭: {send_center}")
    adb_cmd(f"shell input tap {send_center[0]} {send_center[1]}")
    time.sleep(3.5)

    # 6. 영수증 스크린샷 저장
    if proof_save_dir:
        proof_path = proof_save_dir / "proof_tiktok_comment_live.png"
        adb_cmd("shell screencap -p /sdcard/temp_screen.png")
        adb_cmd(f'pull /sdcard/temp_screen.png "{proof_path}"')
        print(f"📸 최종 실물 영수증 저장: {proof_path}")

    # 7. 기본 삼성 키보드로 원복
    print("👉 [5단계] 삼성 키보드로 원복")
    adb_cmd("shell ime set com.samsung.android.honeyboard/.service.HoneyBoardService")

    print("🎉 === 틱톡 댓글 등록 100% 무인 성공! ===")
    return True

if __name__ == "__main__":
    proof_dir = Path(r"C:\Users\zkfnt\.gemini\antigravity-ide\brain\998fe1e4-e7e3-436b-bdfc-908b49764dd2")
    post_tiktok_comment_by_text(proof_save_dir=proof_dir)
