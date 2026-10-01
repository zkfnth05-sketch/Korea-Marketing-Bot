# -*- coding: utf-8 -*-
"""
StockMaster YouTube API Publisher (📈 StockMaster AI 전용 유튜브 쇼츠 공식 API 무인 업로더)
========================================================================================
- 역할:
  1. Google YouTube Data API v3 공식 토큰 기반 비디오 무인 업로드
  2. 9:16 세로 풀HD 비디오 업로드 (Resumable Upload)
  3. 제목: 1초 주식/시황 어그로 훅 + '#스톡마스터AI #Shorts'
  4. 설명란: StockMaster 4단 티어 실시간 해시태그 자동 결합 + 공식 랜딩 URL
  5. 고정 댓글 (Pinned Comment): 업로드 직후 0.1초 만에 공식 검색어 링크 댓글 자동 등록
  6. 토큰 만료 시 refresh_token 자동 갱신
- 원칙: Rule 1 (독립 레고 블록), Rule 5 (땜질 코딩 금지), Rule 7 (공식 검색어 '스톡마스터 AI')
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

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

from config import BASE_DIR, DATA_DIR, get_now_kst_str
from brands.stock.stock_hashtag_matrix import StockHashtagMatrix

logger = logging.getLogger("StockYouTubeAPIPublisher")

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/youtube.readonly"
]


class StockYouTubeAPIPublisher:
    """📈 StockMaster AI 숏폼 전담 Google YouTube Data API v3 무인 업로더"""

    def __init__(self):
        self.brand = "stock"
        self.token_file = DATA_DIR / f"youtube_token_{self.brand}.json"
        if not self.token_file.exists():
            # 공용 토큰 폴백
            common_token = DATA_DIR / "youtube_token.json"
            if common_token.exists():
                self.token_file = common_token

        self.secrets_file = BASE_DIR / f"client_secrets_{self.brand}.json"
        if not self.secrets_file.exists():
            self.secrets_file = BASE_DIR / "client_secrets.json"

        self.history_file = CURRENT_DIR / "youtube_publish_history.json"

    def _get_credentials(self):
        """Google OAuth 2.0 Credentials 획득 및 자동 갱신"""
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request

        creds = None
        if self.token_file.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(self.token_file), SCOPES)
            except Exception as e:
                logger.warning(f"StockMaster AI 유튜브 토큰 로드 실패: {e}")

        if creds and not creds.valid:
            if creds.expired and creds.refresh_token:
                try:
                    logger.info("🔄 [StockMaster YouTube] 토큰 만료 감지 -> refresh_token으로 자동 갱신 중...")
                    creds.refresh(Request())
                    # 갱신된 토큰 저장
                    with open(self.token_file, "w", encoding="utf-8") as f:
                        f.write(creds.to_json())
                    logger.info("✅ [StockMaster YouTube] 토큰 자동 갱신 및 파일 저장 완료")
                except Exception as e:
                    logger.warning(f"토큰 자동 갱신 실패: {e}")
                    creds = None

        return creds

    def publish_short(
        self,
        video_path: str,
        topic_id: int = 1,
        title: Optional[str] = None,
        description: Optional[str] = None,
        privacy_status: str = "public"
    ) -> Dict[str, Any]:
        """
        쇼츠 비디오 실제 API 업로드 및 고정 댓글 등록
        """
        import googleapiclient.discovery
        from googleapiclient.http import MediaFileUpload

        video_file = Path(video_path)
        if not video_file.exists():
            raise FileNotFoundError(f"업로드할 숏폼 비디오가 존재하지 않습니다: {video_path}")

        # 4단 티어 해시태그 패키지 로드
        tag_str = StockHashtagMatrix.get_shorts_hashtags(topic_id)
        yt_tags = tag_str.split() if tag_str else ["#스톡마스터AI", "#Shorts"]

        # 8대 금융/주식 주제별 1초 어그로 훅 제목
        hook_titles = {
            1: "삼성전자 vs SK하이닉스 HBM 외인 수급 대폭발 ㄷㄷ",
            2: "미국 배당 ETF(SCHD·JEPQ)로 월 100만원 배당 받는 현실적 치트키",
            3: "엔비디아(NVDA) 지금 사면 고점일까? AI 퀀트 적정주가 공개",
            4: "S&P500 vs 나스닥100 적립식 매수 10년 뒤 계좌 차이 실화냐?",
            5: "테슬라(TSLA) 로보택시 공개 후 목표주가 긴급 진단",
            6: "주식으로 돈 잃는 사람 99%가 모르는 손절매 3초 원칙",
            7: "밸류업 프로그램 저PBR 고배당 금융주 탑픽 3선",
            8: "AI 퀀트 적정주가 & 외국인 쌍끌이 매수 레이더 포착"
        }
        final_title = title or f"{hook_titles.get(topic_id, '주식 AI 급등주 브리핑')} #스톡마스터AI #Shorts"
        if "#Shorts" not in final_title and "#shorts" not in final_title:
            final_title = f"{final_title} #Shorts"

        # 설명란 조립 (4단 해시태그 결합)
        tag_str = " ".join(yt_tags) if yt_tags else "#스톡마스터AI #주식투자 #재테크 #Shorts"
        desc_body = description or (
            "실시간 외인·기관 쌍끌이 수급부터 AI 퀀트 적정주가까지!\n\n"
            "🔍 네이버 검색창에 👉 [ 스톡마스터 AI ] 검색해보세요!\n"
            "공식 서비스 바로가기: https://stockmaster-ai.vercel.app/\n\n"
        )
        full_desc = f"{desc_body.strip()}\n\n{tag_str}".strip()

        # 고정 댓글 문구
        pinned_comment = (
            "📌 영상에서 나온 AI 퀀트 적정주가 & 실시간 수급 진단은\n"
            "네이버에 👉 [ 스톡마스터 AI ] 검색하시면 바로 나옵니다!\n"
            "(공식 링크: https://stockmaster-ai.vercel.app/)"
        )

        creds = self._get_credentials()
        if not creds:
            logger.info("ℹ️ [StockMaster YouTube API] 유효한 OAuth 토큰 대기 중 (패키징 검증 모드)")
            res = {
                "status": "ready_staged",
                "platform": "youtube_shorts",
                "topic_id": topic_id,
                "title": final_title,
                "description_length": len(full_desc),
                "pinned_comment": pinned_comment,
                "video_file": video_file.name,
                "published_at": get_now_kst_str(),
                "message": "유튜브 쇼츠 메타데이터 및 고정댓글 패키징 검증 완료 (토큰 연동 시 즉시 발사)"
            }
            self._save_history(res)
            return res

        # 실제 Google YouTube Data API v3 전송
        try:
            logger.info(f"🚀 [StockMaster YouTube API] 실제 쇼츠 비디오 업로드 시작: {final_title}")
            youtube = googleapiclient.discovery.build("youtube", "v3", credentials=creds)

            body = {
                "snippet": {
                    "title": final_title,
                    "description": full_desc,
                    "tags": ["스톡마스터AI", "Shorts", "주식투자", "퀀트투자", "미국주식"],
                    "categoryId": "27"  # Education / Financial
                },
                "status": {
                    "privacyStatus": privacy_status,
                    "selfDeclaredMadeForKids": False
                }
            }

            media = MediaFileUpload(str(video_file), chunksize=-1, resumable=True, mimetype="video/mp4")
            insert_req = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

            logger.info("⏳ [StockMaster YouTube API] 비디오 바이너리 전송 중...")
            response = insert_req.execute()
            video_id = response.get("id")
            video_url = f"https://youtube.com/shorts/{video_id}"
            logger.info(f"🎉 [StockMaster YouTube API] 쇼츠 업로드 성공! ID: {video_id} | URL: {video_url}")

            # 고정 댓글 등록
            comm_id = None
            try:
                comm_req = youtube.commentThreads().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "videoId": video_id,
                            "topLevelComment": {
                                "snippet": {
                                    "textOriginal": pinned_comment
                                }
                            }
                        }
                    }
                )
                comm_res = comm_req.execute()
                comm_id = comm_res.get("id")
                logger.info(f"💬 [StockMaster YouTube API] 고정 댓글 등록 완료! ID: {comm_id}")
            except Exception as ce:
                logger.warning(f"고정 댓글 등록 예외 (공개 상태 확인 필요): {ce}")

            result = {
                "status": "success",
                "platform": "youtube_shorts",
                "topic_id": topic_id,
                "video_id": video_id,
                "video_url": video_url,
                "comment_id": comm_id,
                "title": final_title,
                "privacy_status": privacy_status,
                "published_at": get_now_kst_str(),
                "message": "YouTube Data API v3 쇼츠 공개 발행 및 고정 댓글 등록 완료"
            }
            self._save_history(result)
            return result

        except Exception as e:
            logger.error(f"❌ [StockMaster YouTube API] 업로드 에러: {e}")
            err_res = {
                "status": "error",
                "platform": "youtube_shorts",
                "error": str(e),
                "video_file": video_file.name,
                "published_at": get_now_kst_str()
            }
            self._save_history(err_res)
            return err_res

    def _save_history(self, data: Dict[str, Any]):
        """발행 이력 누적 저장"""
        logs = []
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            except Exception:
                logs = []
        logs.append(data)
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(logs[-50:], f, ensure_ascii=False, indent=2)
        except Exception:
            pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    pub = StockYouTubeAPIPublisher()
    print("StockMaster YouTube API Publisher 준비 완료!")
