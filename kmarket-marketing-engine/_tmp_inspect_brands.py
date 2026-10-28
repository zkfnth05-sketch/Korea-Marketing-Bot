# -*- coding: utf-8 -*-
import re

FILES = [
    'brands/aura/aura_youtube_bot_publisher.py',
    'brands/insurance/insurance_youtube_bot_publisher.py',
    'brands/stock/stock_youtube_bot_publisher.py',
]

for f in FILES:
    s = open(f, encoding='utf-8').read()
    print('=' * 70)
    print('FILE:', f)
    print('  class          :', re.findall(r'^class (\w+)', s, re.M))
    print('  post_comment   :', 'def post_comment_only(' in s,
          '| async:', 'def post_comment_only_async(' in s)
    print('  normalize      :', '_normalize_video_id' in s)
    print('  OFFICIAL_KEYWORD:', re.findall(r'OFFICIAL_KEYWORD\s*=\s*["\']([^"\']+)', s)[:2])
    print('  LANDING_URL    :', re.findall(r'LANDING_URL\s*=\s*["\']([^"\']+)', s)[:2])
    print('  BRAND          :', re.findall(r'^\s*BRAND\s*=\s*["\']([^"\']+)', s, re.M)[:2])
    print('  __init__ sig   :', re.findall(r'def __init__\(self[^)]*\)', s)[:2])
