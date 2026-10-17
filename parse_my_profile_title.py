# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET

tree = ET.parse('my_profile.xml')
root = tree.getroot()

print("=== 내 프로필 상단 계정명 요소 ===")
for node in root.iter('node'):
    txt = node.attrib.get('text', '')
    desc = node.attrib.get('content-desc', '')
    rid = node.attrib.get('resource-id', '')
    bounds = node.attrib.get('bounds', '')
    if any(k in txt.lower() or k in desc.lower() for k in ['골드맘', 'goldmom', 'aura', 'stock', '아우라', '스톡']):
        print(f"텍스트: '{txt}' | desc: '{desc}' | bounds: {bounds} | id: {rid}")
