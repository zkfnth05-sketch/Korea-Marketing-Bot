# -*- coding: utf-8 -*-
import re

with open('tiktok_activities.txt', 'r', encoding='utf-16le', errors='ignore') as f:
    text = f.read()

aweme_links = set(re.findall(r'aweme://[^\s"\'<>]+', text))
print('발견된 aweme 딥링크들:')
for l in sorted(aweme_links):
    print(' ', l)

snss_links = set(re.findall(r'snssdk[0-9]+://[^\s"\'<>]+', text))
print('발견된 snssdk 딥링크들:')
for l in sorted(snss_links):
    print(' ', l)
