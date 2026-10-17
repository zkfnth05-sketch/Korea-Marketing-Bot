# -*- coding: utf-8 -*-
import re

with open('tiktok_package_dump.txt', 'r', encoding='utf-16le', errors='ignore') as f:
    text = f.read()

schemes = set(re.findall(r'scheme\s+"([^"]+)"', text, re.I))
print('발견된 URL Schemes:', list(schemes))

schemes_patterns = set(re.findall(r'([a-zA-Z0-9_\-]+://[^\s"\'<>]+)', text))
print('발견된 패턴들 (상위 20개):', list(schemes_patterns)[:20])

profile_activities = [line.strip() for line in text.splitlines() if any(k in line.lower() for k in ['profile', 'account', 'login', 'record', 'publish', 'upload', 'camera']) and 'com.ss.android.ugc' in line]
print(f'프로필/계정/업로드 관련 액티비티 수: {len(profile_activities)}')
for a in profile_activities[:25]:
    print('  -', a)
