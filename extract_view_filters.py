# -*- coding: utf-8 -*-
with open('tiktok_package_dump.txt', 'r', encoding='utf-16le', errors='ignore') as f:
    lines = f.readlines()

view_filters = []
capture = False
current = []

for line in lines:
    if 'android.intent.action.VIEW' in line:
        capture = True
        current = [line.strip()]
    elif capture:
        if line.strip().startswith('Activity') or line.strip().startswith('Receiver') or line.strip().startswith('Service'):
            capture = False
            view_filters.append('\n'.join(current))
            current = []
        else:
            current.append(line.strip())
            if len(current) > 30:
                capture = False
                view_filters.append('\n'.join(current))
                current = []

print(f'VIEW 필터 총 개수: {len(view_filters)}')
for idx, vf in enumerate(view_filters[:10]):
    print(f'--- 필터 #{idx+1} ---')
    print(vf)
