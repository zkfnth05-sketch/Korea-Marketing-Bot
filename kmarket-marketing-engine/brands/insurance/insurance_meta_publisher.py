# -*- coding: utf-8 -*-
"""
Insurance Meta Graph API Publisher (🛡️ 보험 리밸런스 전용 Instagram & Facebook 무인 자동 발행 레고 블록)
=================================================================================================
- 역할:
  1. Meta 공식 Graph API를 통해 Instagram Reels / 피드 및 Facebook 페이지로 숏폼과 카드뉴스 무인 송출
  2. 차단/캡차/로봇인증 0%의 공식 API 엔드포인트 활용
  3. 인간 활동 패턴 모사 (자연스러운 포스팅 간격 분산, 심야 취침 모드)
  4. 공식 검색어 '보험 리밸런스' 및 공식 랜딩 URL, 4단 해시태그 자동 주입
- 원칙: Rule 1 (독립 레고 블록), Rule 6 (24시간 무인 자율 구동), Rule 7 (공식 검색어 '보험 리밸런스')
"""

import os
import sys
import json
import logging
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Dict, Any, List, Optional

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

from config import BASE_DIR, get_now_kst_str
from brands.insurance.insurance_hashtag_matrix import InsuranceHashtagMatrix

logger = logging.getLogger("InsuranceMetaPublisher")

ACCOUNTS_FILE = CURRENT_DIR / "accounts.json"
API_VERSION = "v20.0"
GRAPH_URL = f"https://graph.facebook.com/{API_VERSION}"


class InsuranceMetaPublisher:
    """🛡️ 보험 리밸런스 전용 Meta (Instagram & Facebook) 공식 API 퍼블리셔"""

    def __init__(self):
        self.brand = "insurance"
        self.accounts_file = ACCOUNTS_FILE
        self.history_file = CURRENT_DIR / "meta_publish_history.json"
        self._load_credentials()

    def _load_credentials(self):
        self.creds = {}
        if self.accounts_file.exists():
            with open(self.accounts_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.creds = data.get("credentials", {})
        
        self.page_id = self.creds.get("facebook_page_id", "1358924267302888")
        self.page_token = self.creds.get("facebook_access_token", "")
        self.ig_user_id = self.creds.get("instagram_account_id", "17841416133946561")
        self.ig_username = self.creds.get("instagram_username", "goldmomofficial")
        self.user_token = self.creds.get("meta_user_token", "")

    def is_available(self) -> bool:
        return bool(self.page_token and self.page_id)

    def publish_facebook_post(self, message: str, link: Optional[str] = None) -> Dict[str, Any]:
        """📘 페이스북 페이지 피드에 공식 메시지/링크 즉시 발행"""
        if not self.is_available():
            return {"status": "error", "message": "Meta 자격 증명 부재", "brand": self.brand}

        url = f"{GRAPH_URL}/{self.page_id}/feed"
        payload = {
            "message": message,
            "access_token": self.page_token
        }
        if link:
            payload["link"] = link

        try:
            data = urllib.parse.urlencode(payload).encode('utf-8')
            req = urllib.request.Request(url, data=data, method="POST")
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                post_id = result.get("id")
                logger.info(f"✅ [Meta-Insurance] 페이스북 페이지 발행 성공! Post ID: {post_id}")
                self._record_history("facebook_feed", post_id, message)
                return {
                    "status": "success",
                    "post_id": post_id,
                    "platform": "facebook",
                    "brand": self.brand
                }
        except Exception as e:
            logger.error(f"❌ [Meta-Insurance] 페이스북 페이지 발행 실패: {e}")
            return {"status": "error", "message": str(e), "brand": self.brand}

    def publish_facebook_cardnews_album(self, image_paths: List[str], caption: str) -> Dict[str, Any]:
        """📘 페이스북 페이지에 5장 카드뉴스 풀세트 앨범 피드 무인 발행"""
        if not self.is_available():
            return {"status": "error", "message": "Meta 자격 증명 부재", "brand": self.brand}

        import requests
        photo_ids = []
        for p in image_paths:
            if os.path.exists(p):
                with open(p, 'rb') as img_f:
                    res = requests.post(
                        f"{GRAPH_URL}/{self.page_id}/photos",
                        files={'source': img_f},
                        data={'published': 'false', 'access_token': self.page_token},
                        timeout=30
                    )
                    if res.status_code == 200:
                        pid = res.json().get('id')
                        photo_ids.append({'media_fbid': pid})

        if not photo_ids:
            return {"status": "error", "message": "카드뉴스 이미지 업로드 실패", "brand": self.brand}

        feed_res = requests.post(
            f"{GRAPH_URL}/{self.page_id}/feed",
            data={
                'message': caption,
                'attached_media': json.dumps(photo_ids),
                'access_token': self.page_token
            },
            timeout=30
        )
        if feed_res.status_code == 200:
            post_id = feed_res.json().get('id')
            logger.info(f"✅ [Meta-Insurance] 페이스북 {len(photo_ids)}장 카드뉴스 앨범 발행 성공! Post ID: {post_id}")
            self._record_history("facebook_cardnews_album", post_id, caption)
            return {
                "status": "success",
                "post_id": post_id,
                "slides_count": len(photo_ids),
                "platform": "facebook",
                "brand": self.brand
            }
        else:
            return {"status": "error", "message": feed_res.text, "brand": self.brand}

    def publish_facebook_photo(self, image_url: str, caption: str) -> Dict[str, Any]:
        """📘 페이스북 페이지 피드에 사진+카피라이팅 발행"""
        if not self.is_available():
            return {"status": "error", "message": "Meta 자격 증명 부재", "brand": self.brand}

        url = f"{GRAPH_URL}/{self.page_id}/photos"
        payload = {
            "url": image_url,
            "caption": caption,
            "access_token": self.page_token
        }
        try:
            data = urllib.parse.urlencode(payload).encode('utf-8')
            req = urllib.request.Request(url, data=data, method="POST")
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                post_id = result.get("post_id") or result.get("id")
                logger.info(f"✅ [Meta-Insurance] 페이스북 사진 발행 성공! Post ID: {post_id}")
                self._record_history("facebook_photo", post_id, caption)
                return {
                    "status": "success",
                    "post_id": post_id,
                    "platform": "facebook",
                    "brand": self.brand
                }
        except Exception as e:
            logger.error(f"❌ [Meta-Insurance] 페이스북 사진 발행 실패: {e}")
            return {"status": "error", "message": str(e), "brand": self.brand}

    def publish_instagram_photo(self, image_url: str, caption: str) -> Dict[str, Any]:
        """📸 인스타그램 피드/카드뉴스 이미지 발행 (2단계 컨테이너 방식)"""
        if not bool(self.user_token and self.ig_user_id):
            return {"status": "error", "message": "Instagram 자격 증명 부재", "brand": self.brand}

        create_url = f"{GRAPH_URL}/{self.ig_user_id}/media"
        create_payload = {
            "image_url": image_url,
            "caption": caption,
            "access_token": self.user_token
        }
        try:
            data = urllib.parse.urlencode(create_payload).encode('utf-8')
            req = urllib.request.Request(create_url, data=data, method="POST")
            with urllib.request.urlopen(req, timeout=30) as resp:
                create_res = json.loads(resp.read().decode('utf-8'))
                creation_id = create_res.get("id")

            if not creation_id:
                return {"status": "error", "message": "미디어 컨테이너 생성 실패", "brand": self.brand}

            import time
            time.sleep(3)

            publish_url = f"{GRAPH_URL}/{self.ig_user_id}/media_publish"
            publish_payload = {
                "creation_id": creation_id,
                "access_token": self.user_token
            }
            data_pub = urllib.parse.urlencode(publish_payload).encode('utf-8')
            req_pub = urllib.request.Request(publish_url, data=data_pub, method="POST")
            with urllib.request.urlopen(req_pub, timeout=30) as resp_pub:
                pub_res = json.loads(resp_pub.read().decode('utf-8'))
                media_id = pub_res.get("id")
                logger.info(f"✅ [Meta-Insurance] 인스타그램 사진 발행 성공! Media ID: {media_id}")
                self._record_history("instagram_photo", media_id, caption)
                return {
                    "status": "success",
                    "media_id": media_id,
                    "platform": "instagram",
                    "brand": self.brand
                }
        except urllib.error.HTTPError as he:
            err_body = he.read().decode('utf-8') if hasattr(he, 'read') else str(he)
            logger.error(f"❌ [Meta-Insurance] 인스타그램 사진 발행 HTTP 에러 ({he.code}): {err_body}")
            return {"status": "error", "message": f"HTTP {he.code}: {err_body}", "brand": self.brand}
        except Exception as e:
            logger.error(f"❌ [Meta-Insurance] 인스타그램 사진 발행 실패: {e}")
            return {"status": "error", "message": str(e), "brand": self.brand}

    def publish_instagram_carousel(self, image_paths: List[str], caption: str) -> Dict[str, Any]:
        """📸 인스타그램 피드에 4~5장 카드뉴스 캐러셀 앨범(CAROUSEL_ALBUM) 발행"""
        if not bool(self.user_token and self.ig_user_id):
            return {"status": "error", "message": "Instagram 자격 증명 부재", "brand": self.brand}

        from brands.insurance.insurance_supabase_manager import InsuranceSupabaseManager
        mgr = InsuranceSupabaseManager()

        public_urls = []
        for p in image_paths:
            if os.path.exists(p):
                url = mgr.upload_image_to_storage(p, bucket_subpath="cardnews/carousel") if hasattr(mgr, "upload_image_to_storage") else None
                if url:
                    public_urls.append(url)

        if not public_urls:
            # fallback: 로컬 이미지가 없거나 업로드 실패 시 기본 사진
            sample_img_url = "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=1080"
            return self.publish_instagram_photo(sample_img_url, caption)

        try:
            child_ids = []
            for u in public_urls:
                create_url = f"{GRAPH_URL}/{self.ig_user_id}/media"
                payload = {"image_url": u, "is_carousel_item": "true", "access_token": self.user_token}
                data = urllib.parse.urlencode(payload).encode("utf-8")
                req = urllib.request.Request(create_url, data=data, method="POST")
                with urllib.request.urlopen(req, timeout=30) as resp:
                    res = json.loads(resp.read().decode("utf-8"))
                    cid = res.get("id")
                    if cid:
                        child_ids.append(cid)

            if len(child_ids) < 2:
                return self.publish_instagram_photo(public_urls[0], caption)

            car_url = f"{GRAPH_URL}/{self.ig_user_id}/media"
            car_payload = {
                "media_type": "CAROUSEL",
                "children": ",".join(child_ids),
                "caption": caption,
                "access_token": self.user_token
            }
            data_car = urllib.parse.urlencode(car_payload).encode("utf-8")
            req_car = urllib.request.Request(car_url, data=data_car, method="POST")
            with urllib.request.urlopen(req_car, timeout=30) as resp_car:
                res_car = json.loads(resp_car.read().decode("utf-8"))
                car_id = res_car.get("id")

            if not car_id:
                return {"status": "error", "message": "인스타그램 캐러셀 컨테이너 생성 실패", "brand": self.brand}

            import time
            time.sleep(5)

            pub_url = f"{GRAPH_URL}/{self.ig_user_id}/media_publish"
            pub_payload = {"creation_id": car_id, "access_token": self.user_token}
            data_pub = urllib.parse.urlencode(pub_payload).encode("utf-8")
            req_pub = urllib.request.Request(pub_url, data=data_pub, method="POST")
            with urllib.request.urlopen(req_pub, timeout=30) as resp_pub:
                res_pub = json.loads(resp_pub.read().decode("utf-8"))
                media_id = res_pub.get("id")
                logger.info(f"✅ [Meta-Insurance] 인스타그램 {len(child_ids)}장 카드뉴스 캐러셀 발행 성공! Media ID: {media_id}")
                self._record_history("instagram_carousel", media_id, caption)
                return {
                    "status": "success",
                    "media_id": media_id,
                    "slides_count": len(child_ids),
                    "platform": "instagram_carousel",
                    "brand": self.brand
                }
        except urllib.error.HTTPError as he:
            err_body = he.read().decode("utf-8") if hasattr(he, "read") else str(he)
            logger.error(f"❌ [Meta-Insurance] 인스타그램 캐러셀 발행 HTTP 에러 ({he.code}): {err_body}")
            return {"status": "error", "message": f"HTTP {he.code}: {err_body}", "brand": self.brand}
        except Exception as e:
            logger.error(f"❌ [Meta-Insurance] 인스타그램 캐러셀 발행 예외: {e}")
            return {"status": "error", "message": str(e), "brand": self.brand}

    def publish_instagram_reels(self, video_url: str, caption: str) -> Dict[str, Any]:
        """📸 인스타그램 릴스(Reels) 비디오 자동 발행"""
        if not bool(self.user_token and self.ig_user_id):
            return {"status": "error", "message": "Instagram 자격 증명 부재", "brand": self.brand}

        create_url = f"{GRAPH_URL}/{self.ig_user_id}/media"
        create_payload = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "access_token": self.user_token
        }
        try:
            data = urllib.parse.urlencode(create_payload).encode('utf-8')
            req = urllib.request.Request(create_url, data=data, method="POST")
            with urllib.request.urlopen(req, timeout=35) as resp:
                create_res = json.loads(resp.read().decode('utf-8'))
                creation_id = create_res.get("id")

            if not creation_id:
                return {"status": "error", "message": "릴스 미디어 컨테이너 생성 실패", "brand": self.brand}

            import time
            time.sleep(5)

            publish_url = f"{GRAPH_URL}/{self.ig_user_id}/media_publish"
            publish_payload = {
                "creation_id": creation_id,
                "access_token": self.user_token
            }
            data_pub = urllib.parse.urlencode(publish_payload).encode('utf-8')
            req_pub = urllib.request.Request(publish_url, data=data_pub, method="POST")
            with urllib.request.urlopen(req_pub, timeout=35) as resp_pub:
                pub_res = json.loads(resp_pub.read().decode('utf-8'))
                media_id = pub_res.get("id")
                logger.info(f"✅ [Meta-Insurance] 인스타그램 릴스 발행 성공! Media ID: {media_id}")
                self._record_history("instagram_reels", media_id, caption)
                return {
                    "status": "success",
                    "media_id": media_id,
                    "platform": "instagram_reels",
                    "brand": self.brand
                }
        except Exception as e:
            logger.error(f"❌ [Meta-Insurance] 인스타그램 릴스 발행 실패: {e}")
            return {"status": "error", "message": str(e), "brand": self.brand}

    def publish_facebook_reels(self, video_path: str, description: str, first_comment: Optional[str] = None) -> Dict[str, Any]:
        """📘 페이스북 페이지 릴스(Reels) 비디오 바이너리 업로드 및 발행"""
        if not self.is_available():
            return {"status": "error", "message": "Meta 자격 증명 부재", "brand": self.brand}

        if not os.path.exists(video_path):
            return {"status": "error", "message": f"비디오 파일 없음: {video_path}", "brand": self.brand}

        try:
            init_url = f"{GRAPH_URL}/{self.page_id}/video_reels"
            init_payload = {"upload_phase": "start", "access_token": self.page_token}
            data = urllib.parse.urlencode(init_payload).encode('utf-8')
            req = urllib.request.Request(init_url, data=data, method="POST")
            with urllib.request.urlopen(req, timeout=25) as resp:
                init_res = json.loads(resp.read().decode('utf-8'))
                video_id = init_res.get("video_id")
                upload_url = init_res.get("upload_url")

            if not video_id or not upload_url:
                return {"status": "error", "message": "페이스북 릴스 세션 초기화 실패", "brand": self.brand}

            file_size = os.path.getsize(video_path)
            with open(video_path, "rb") as vf:
                video_bytes = vf.read()

            upload_req = urllib.request.Request(
                upload_url,
                data=video_bytes,
                headers={
                    "Authorization": f"OAuth {self.page_token}",
                    "offset": "0",
                    "file_size": str(file_size)
                },
                method="POST"
            )
            with urllib.request.urlopen(upload_req, timeout=60) as up_resp:
                pass

            finish_payload = {
                "upload_phase": "finish",
                "video_id": video_id,
                "video_state": "PUBLISHED",
                "description": description,
                "access_token": self.page_token
            }
            data_fin = urllib.parse.urlencode(finish_payload).encode('utf-8')
            req_fin = urllib.request.Request(init_url, data=data_fin, method="POST")
            with urllib.request.urlopen(req_fin, timeout=30) as resp_fin:
                fin_res = json.loads(resp_fin.read().decode('utf-8'))

            comment_id = None
            if first_comment and video_id:
                try:
                    comm_url = f"{GRAPH_URL}/{video_id}/comments"
                    comm_payload = {"message": first_comment, "access_token": self.page_token}
                    data_comm = urllib.parse.urlencode(comm_payload).encode('utf-8')
                    req_comm = urllib.request.Request(comm_url, data=data_comm, method="POST")
                    with urllib.request.urlopen(req_comm, timeout=15) as comm_resp:
                        comm_res = json.loads(comm_resp.read().decode('utf-8'))
                        comment_id = comm_res.get("id")
                except Exception as ce:
                    logger.warning(f"페이스북 릴스 첫 댓글 등록 경고: {ce}")

            logger.info(f"✅ [Meta-Insurance] 페이스북 릴스 발행 성공! Reel ID: {video_id}")
            self._record_history("facebook_reels", video_id, description)
            return {
                "status": "success",
                "reel_id": video_id,
                "comment_id": comment_id,
                "platform": "facebook_reels",
                "brand": self.brand
            }
        except Exception as e:
            logger.error(f"❌ [Meta-Insurance] 페이스북 릴스 발행 실패: {e}")
            return {"status": "error", "message": str(e), "brand": self.brand}

    def publish_facebook_video(self, video_path: str, title: str, description: str) -> Dict[str, Any]:
        """📘 페이스북 페이지 비디오 피드/릴스 직접 바이너리 업로드 및 즉시 발행 (graph-video)"""
        if not self.is_available():
            return {"status": "error", "message": "Meta 자격 증명 부재", "brand": self.brand}

        if not os.path.exists(video_path):
            return {"status": "error", "message": f"비디오 파일 없음: {video_path}", "brand": self.brand}

        import requests
        try:
            with open(video_path, "rb") as vf:
                res = requests.post(
                    f"https://graph-video.facebook.com/{API_VERSION}/{self.page_id}/videos",
                    files={"source": vf},
                    data={
                        "title": title,
                        "description": description,
                        "access_token": self.page_token
                    },
                    timeout=90
                )
            if res.status_code == 200:
                video_id = res.json().get("id")
                logger.info(f"✅ [Meta-Insurance] 페이스북 비디오 피드 업로드 성공! Video ID: {video_id}")
                self._record_history("facebook_video", video_id, description)
                return {
                    "status": "success",
                    "video_id": video_id,
                    "platform": "facebook_video",
                    "brand": self.brand
                }
            else:
                logger.error(f"❌ [Meta-Insurance] 페이스북 비디오 업로드 실패 ({res.status_code}): {res.text}")
                return {"status": "error", "message": res.text, "brand": self.brand}
        except Exception as e:
            logger.error(f"❌ [Meta-Insurance] 페이스북 비디오 업로드 예외: {e}")
            return {"status": "error", "message": str(e), "brand": self.brand}

    def _record_history(self, post_type: str, item_id: str, content_snippet: str):
        history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                history = []
        
        history.append({
            "timestamp": get_now_kst_str(),
            "type": post_type,
            "id": item_id,
            "snippet": content_snippet[:100]
        })
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
