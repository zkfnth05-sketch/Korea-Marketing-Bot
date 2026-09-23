# -*- coding: utf-8 -*-
import sys, json
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")
BASE = Path(__file__).resolve().parent

for brand in ["aura", "stock", "insurance"]:
    hfile = BASE / "data" / f"{brand}_kin_history.json"
    if not hfile.exists():
        print(f"[{brand}] 히스토리 없음")
        continue
    h = json.loads(hfile.read_text(encoding="utf-8"))
    today_recs = [r for r in h if r.get("created_at", "").startswith(today)]
    real_published = [r for r in today_recs if r.get("status") == "published" and "answerNo=" in r.get("published_url", "")]
    fake_published = [r for r in today_recs if r.get("status") == "published" and "answerNo=" not in r.get("published_url", "")]
    print(f"\n[{brand.upper()}] 오늘 전체={len(today_recs)} / 실제성공={len(real_published)} / 가짜published={len(fake_published)}")
    for r in today_recs:
        purl = r.get("published_url", "")
        real = "answerNo=" in purl
        tag = "✅실제" if real else ("❌가짜" if r.get("status") == "published" else "⚠️실패")
        print(f"  {tag} [{r.get('status')}] {r.get('title','')[:30]} | {purl[:70]}")
