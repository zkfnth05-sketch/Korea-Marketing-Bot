# -*- coding: utf-8 -*-
import os
import wave
from pathlib import Path
from brands.insurance.insurance_voice_cloner import InsuranceVoiceCloner
from core.shorts_engine.insurance_shorts_scenario_director import InsuranceShortsScenarioDirector

s = InsuranceShortsScenarioDirector.SCRIPTS_22S[2]
full_txt = f"{s['hook_0_10s']} {s['app_10_20s']} {s['cta_18_22s']}"
print(f"📝 대본 글자수: {len(full_txt)}자")
print(f"📜 대본 내용: {full_txt}")

cloner = InsuranceVoiceCloner()
out_wav = r"c:\Users\zkfnt\Desktop\한국 마케팅봇\kmarket-marketing-engine\test_dur_2.wav"
res = cloner.synthesize(full_txt, output_wav_path=out_wav, gender="male")
w = wave.open(res, "rb")
dur = w.getnframes() / float(w.getframerate())
print(f"⏱️ 실측 오디오 길이: {dur:.2f}초")
