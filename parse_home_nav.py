# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET

tree = ET.parse('home_nav.xml')
root = tree.getroot()

print("=== 하단 네비게이션 바 요소들 ===")
for node in root.iter('node'):
    txt = node.attrib.get('text', '')
    desc = node.attrib.get('content-desc', '')
    bounds = node.attrib.get('bounds', '')
    if any(k in txt or k in desc for k in ['홈', '친구', '만들기', '알림', '프로필', 'Profile']):
        print(f"텍스트: '{txt}' | desc: '{desc}' | bounds: {bounds} | id: {node.attrib.get('resource-id', '')}")
