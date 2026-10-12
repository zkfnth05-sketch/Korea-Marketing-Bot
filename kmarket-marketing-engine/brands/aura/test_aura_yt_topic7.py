import asyncio
import sys
from pathlib import Path

CURRENT_DIR = Path(r"c:\Users\zkfnt\Desktop\한국 마케팅봇\kmarket-marketing-engine\brands\aura")
PROJECT_ROOT = CURRENT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from brands.aura.aura_youtube_bot_publisher import AuraYouTubeBotPublisher

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def main():
    target_video = Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Aura\Aura_07_aura_diagnosis_20260927_174016\Aura_22초숏폼_주제07_aura_diagnosis_20260927_174016.mp4")
    print(f"Target video: {target_video} (exists: {target_video.exists()})")
    
    publisher = AuraYouTubeBotPublisher(headless=True)
    res = publisher.publish_short(
        topic_id=7,
        video_path=target_video,
        title="[AI 아우라 매력 진단] 요즘 인스타에서 난리 난 내 얼굴 아우라 매력 테스트 #아우라AI데이팅 #Shorts",
        privacy_status="public"
    )
    print("Upload Result:", res)

if __name__ == "__main__":
    main()
