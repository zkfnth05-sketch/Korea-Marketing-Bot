# -*- coding: utf-8 -*-
import sys
import logging
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.shorts_engine.stock_app_recorder import StockAppRecorder

def test_record_board():
    out_dir = Path(r"C:\Users\zkfnt\Desktop\한국 숏폼_산출물\Stock\Test_Live_Record")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_mp4 = str(out_dir / "stock_live_samsung_4tabs_24s.mp4")
    
    recorder = StockAppRecorder()
    print("🚀 [StockAppRecorder] 삼성전자 4대 모달 탭 상하단 풀뷰 실시간 24초 녹화 시작...")
    res = recorder.record_simulation_clip(
        topic_id=1,
        duration_sec=24.0,
        output_mp4_path=out_mp4,
        force_fresh_record=True
    )
    print(f"🎉 [녹화 완료] 24초 실물 비디오: {res}")
    
if __name__ == "__main__":
    test_record_board()
