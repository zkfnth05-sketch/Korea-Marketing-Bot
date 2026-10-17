# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET

tree = ET.parse('sheet_open.xml')
root = tree.getroot()

print("=== 바텀시트 계정 목록 요소 ===")
for node in root.iter('node'):
    txt = node.attrib.get('text', '')
    desc = node.attrib.get('content-desc', '')
    bounds = node.attrib.get('bounds', '')
    rid = node.attrib.get('resource-id', '')
    if any(k in txt.lower() or k in desc.lower() for k in ['goldmom', 'aura', 'stock', '계정 전환', '계정 추가']):
        print(f"텍스트: '{txt}' | desc: '{desc}' | bounds: {bounds} | id: {rid}")
