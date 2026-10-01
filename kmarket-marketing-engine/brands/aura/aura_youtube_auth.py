# -*- coding: utf-8 -*-
"""
Aura YouTube Auth Manager (🔑 Aura 전용 유튜브 채널 1회 원클릭 연동 인증기)
=============================================================================
- 역할:
  1. Google OAuth 2.0 승인 창을 브라우저에 띄워 Aura 유튜브 채널과 1회 연결
  2. refresh_token을 data/youtube_token_aura.json 에 영구 보관 (이후 100% 무인 갱신)
  3. 연동된 채널 명칭/핸들/구독자 정보 자동 확인
  4. 비공개(private) 1회 테스트 쇼츠 업로드 검증 지원
- 원칙: Rule 1 (독립 레고 블록), Rule 7 (Aura 공식 규격)
"""

import os
import sys
import json
import logging
from pathlib import Path

# Windows cp949 콘솔 인코딩 에러 방지
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import googleapiclient.discovery

logger = logging.getLogger("AuraYouTubeAuth")

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/youtube.readonly"
]

BASE_DIR = PROJECT_ROOT
CLIENT_SECRETS_FILE = BASE_DIR / "client_secrets_aura.json"
if not CLIENT_SECRETS_FILE.exists():
    CLIENT_SECRETS_FILE = BASE_DIR / "client_secrets.json"
AURA_TOKEN_PATH = BASE_DIR / "data" / "youtube_token_aura.json"


def authenticate_aura_youtube(force: bool = False) -> Credentials:
    """Aura 유튜브 OAuth 2.0 브라우저 로그인 플로우 실행"""
    creds = None

    if not force and AURA_TOKEN_PATH.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(AURA_TOKEN_PATH), SCOPES)
        except Exception as e:
            print(f"⚠️ 기존 [Aura] 토큰 로드 실패 (재인증 필요): {e}")
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                print("🔄 [Aura] 토큰 만료됨 -> refresh_token으로 자동 갱신 중...")
                creds.refresh(Request())
            except Exception as e:
                print(f"⚠️ [Aura] 토큰 자동 갱신 실패: {e} -> 브라우저 로그인 창 실행")
                creds = None

        if not creds:
            if not CLIENT_SECRETS_FILE.exists():
                raise FileNotFoundError(f"인증 파일이 없습니다: {CLIENT_SECRETS_FILE.name}")

            flow = InstalledAppFlow.from_client_secrets_file(
                str(CLIENT_SECRETS_FILE),
                SCOPES
            )
            
            # 승인 URL 생성 및 브라우저 실행
            import webbrowser
            print("\n" + "=" * 70, flush=True)
            print("👉 [Aura 유튜브 구글 승인 링크]:", flush=True)
            print("🌐 브라우저가 자동으로 열리지 않을 경우 아래 링크를 브라우저에 붙여넣어 주세요.", flush=True)
            print("=" * 70 + "\n", flush=True)

            try:
                creds = flow.run_local_server(
                    port=8080,
                    prompt="consent",
                    authorization_prompt_message="브라우저에서 계정을 승인해 주세요: {url}",
                    success_message="Aura 유튜브 채널 연동이 완료되었습니다! 이 창을 닫으셔도 좋습니다.",
                    open_browser=True
                )
            except Exception as e:
                print(f"⚠️ 포트 8080 대기 예외 ({e}), 임의 포트 자동 전환...", flush=True)
                creds = flow.run_local_server(
                    port=0,
                    prompt="consent",
                    authorization_prompt_message="브라우저에서 계정을 승인해 주세요: {url}",
                    success_message="Aura 유튜브 채널 연동이 완료되었습니다! 이 창을 닫으셔도 좋습니다.",
                    open_browser=True
                )

        AURA_TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(AURA_TOKEN_PATH, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
        print(f"✅ [인증 성공] Aura 전용 유튜브 토큰이 영구 저장되었습니다: {AURA_TOKEN_PATH.name}")

    return creds


def verify_channel_info(creds: Credentials):
    """연동된 유튜브 채널 정보 조회 및 검증"""
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=creds)
    req = youtube.channels().list(part="snippet,statistics", mine=True)
    res = req.execute()

    items = res.get("items", [])
    if not items:
        print("⚠️ 연결된 유튜브 채널을 찾을 수 없습니다.")
        return None

    ch = items[0]
    title = ch["snippet"]["title"]
    ch_id = ch["id"]
    custom_url = ch["snippet"].get("customUrl", "")
    print("\n" + "=" * 60)
    print(f"🎉 [연동 완료] 연결된 유튜브 채널: {title}")
    print(f"📌 채널 ID: {ch_id} | 핸들: {custom_url}")
    print("=" * 60 + "\n")
    return ch


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Aura YouTube Channel Auth Tool")
    parser.add_argument("--force", action="store_true", help="새 계정으로 강제 재인증")
    args = parser.parse_args()

    creds = authenticate_aura_youtube(force=args.force)
    verify_channel_info(creds)
